/* RootSpeak - Advanced Messaging System for Linux
 * Users, and root actions performed with a user's identity (instead of runuser). */
#include "user.h"

#include <errno.h>
#include <fcntl.h>
#include <grp.h>
#include <poll.h>
#include <pwd.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <unistd.h>

static void from_passwd(const struct passwd *pw, user_t *u)
{
	u->name = xstrdup(pw->pw_name);
	u->uid = pw->pw_uid;
	u->gid = pw->pw_gid;
}

bool user_find(const char *name, user_t *u)
{
	struct passwd *pw;

	memset(u, 0, sizeof *u);
	errno = 0;
	pw = getpwnam(name);
	if (!pw)
		return false;
	from_passwd(pw, u);
	return true;
}

bool user_from_uid(uid_t uid, user_t *u)
{
	struct passwd *pw;

	memset(u, 0, sizeof *u);
	pw = getpwuid(uid);
	if (!pw)
		return false;
	from_passwd(pw, u);
	return true;
}

void user_free(user_t *u)
{
	free(u->name);
	memset(u, 0, sizeof *u);
}

static long long now_ms(void)
{
	struct timespec ts;

	clock_gettime(CLOCK_MONOTONIC, &ts);
	return (long long)ts.tv_sec * 1000 + ts.tv_nsec / 1000000;
}

static void child(const user_t *u, as_user_fn fn, void *arg, int in, int out)
{
	int nul = open("/dev/null", O_RDWR | O_CLOEXEC);

	if (nul < 0 || dup2(in >= 0 ? in : nul, 0) < 0 || dup2(out >= 0 ? out : nul, 1) < 0 || dup2(nul, 2) < 0)
		_exit(126);
	if (geteuid() == 0 && !rspeak_test) {
		/* the user's full identity: supplementary groups, then group, then user */
		if (initgroups(u->name, u->gid) < 0 || setresgid(u->gid, u->gid, u->gid) < 0 ||
		    setresuid(u->uid, u->uid, u->uid) < 0)
			_exit(126);
		if (getuid() != u->uid || geteuid() != u->uid || getegid() != u->gid || setuid(0) == 0)
			_exit(126);
	}
	if (chdir("/") < 0)
		_exit(126);
	umask(022);
	signal(SIGPIPE, SIG_DFL);
	{
		int r = fn(arg);

		fflush(stdout);
		_exit(r & 0xff);
	}
}

int as_user(const user_t *u, as_user_fn fn, void *arg, const buf_t *in, buf_t *out, size_t max,
		int seconds)
{
	int pin[2] = {-1, -1}, pout[2] = {-1, -1}, state;
	size_t written = 0;
	long long expiry = now_ms() + (long long)seconds * 1000;
	bool expired = false;
	pid_t pid;

	if (in && pipe2(pin, O_CLOEXEC) < 0)
		return -1;
	if (pipe2(pout, O_CLOEXEC) < 0) {
		if (in) {
			close(pin[0]);
			close(pin[1]);
		}
		return -1;
	}
	fflush(stdout);
	fflush(stderr);
	pid = fork();
	if (pid < 0) {
		if (in) {
			close(pin[0]);
			close(pin[1]);
		}
		close(pout[0]);
		close(pout[1]);
		return -1;
	}
	if (pid == 0) {
		if (in)
			close(pin[1]);
		close(pout[0]);
		child(u, fn, arg, in ? pin[0] : -1, pout[1]);
	}
	if (in) {
		close(pin[0]);
		fcntl(pin[1], F_SETFL, O_NONBLOCK);
	}
	close(pout[1]);
	if (in && (!in->n))
		close(pin[1]), pin[1] = -1;
	for (;;) {
		struct pollfd pf[2];
		int n = 0, r;
		long long rest = expiry - now_ms();

		if (rest <= 0) {
			expired = true;
			break;
		}
		pf[n++] = (struct pollfd){.fd = pout[0], .events = POLLIN};
		if (in && pin[1] >= 0)
			pf[n++] = (struct pollfd){.fd = pin[1], .events = POLLOUT};
		r = poll(pf, (nfds_t)n, (int)(rest > 1000 ? 1000 : rest));
		if (r < 0) {
			if (errno == EINTR)
				continue;
			break;
		}
		if (n == 2 && pf[1].revents) {
			ssize_t w = pf[1].revents & POLLOUT ? write(pin[1], in->s + written, in->n - written) : -1;

			if (w > 0)
				written += (size_t)w;
			if (w < 0 || written == in->n) {
				close(pin[1]);
				pin[1] = -1;
			}
		}
		if (pf[0].revents) {
			char tmp[8192];
			ssize_t l = read(pout[0], tmp, sizeof tmp);

			if (l < 0 && errno == EINTR)
				continue;
			if (l <= 0)
				break;
			if (out && out->n < max)
				buf_add(out, tmp, (size_t)l > max - out->n ? max - out->n : (size_t)l);
		}
	}
	if (pin[1] >= 0)
		close(pin[1]);
	close(pout[0]);
	/* Even after its output has ended the child has a time limit: the user
	 * could stop it (same UID), and rspeak must not hang. */
	for (;;) {
		pid_t w;

		if (expired)
			kill(pid, SIGKILL);
		w = waitpid(pid, &state, expired ? 0 : WNOHANG);
		if (w == pid)
			break;
		if (w < 0 && errno != EINTR)
			return -1;
		if (w == 0) {
			if (now_ms() >= expiry)
				expired = true;
			else
				poll(NULL, 0, 10);
		}
	}
	if (expired || !WIFEXITED(state))
		return -1;
	return WEXITSTATUS(state) == 126 ? -1 : WEXITSTATUS(state);
}
