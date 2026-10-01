/* RootSpeak - Advanced Messaging System for Linux
 * Utenti, e azioni di root con l'identità di un utente (al posto di runuser). */
#include "utente.h"

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

static void da_passwd(const struct passwd *pw, utente_t *u)
{
	u->nome = xstrdup(pw->pw_name);
	u->uid = pw->pw_uid;
	u->gid = pw->pw_gid;
}

bool utente_cerca(const char *nome, utente_t *u)
{
	struct passwd *pw;

	memset(u, 0, sizeof *u);
	errno = 0;
	pw = getpwnam(nome);
	if (!pw)
		return false;
	da_passwd(pw, u);
	return true;
}

bool utente_da_uid(uid_t uid, utente_t *u)
{
	struct passwd *pw;

	memset(u, 0, sizeof *u);
	pw = getpwuid(uid);
	if (!pw)
		return false;
	da_passwd(pw, u);
	return true;
}

void utente_libera(utente_t *u)
{
	free(u->nome);
	memset(u, 0, sizeof *u);
}

static long long ms_adesso(void)
{
	struct timespec ts;

	clock_gettime(CLOCK_MONOTONIC, &ts);
	return (long long)ts.tv_sec * 1000 + ts.tv_nsec / 1000000;
}

static void figlio(const utente_t *u, come_utente_fn fn, void *arg, int in, int out)
{
	int nul = open("/dev/null", O_RDWR | O_CLOEXEC);

	if (nul < 0 || dup2(in >= 0 ? in : nul, 0) < 0 || dup2(out >= 0 ? out : nul, 1) < 0 || dup2(nul, 2) < 0)
		_exit(126);
	if (geteuid() == 0 && !rspeak_test) {
		/* identità completa dell'utente: gruppi, poi gruppo, poi utente */
		if (initgroups(u->nome, u->gid) < 0 || setresgid(u->gid, u->gid, u->gid) < 0 ||
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

int come_utente(const utente_t *u, come_utente_fn fn, void *arg, const buf_t *in, buf_t *out, size_t max,
		int secondi)
{
	int pin[2] = {-1, -1}, pout[2] = {-1, -1}, stato;
	size_t scritti = 0;
	long long scadenza = ms_adesso() + (long long)secondi * 1000;
	bool scaduto = false;
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
		figlio(u, fn, arg, in ? pin[0] : -1, pout[1]);
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
		long long resto = scadenza - ms_adesso();

		if (resto <= 0) {
			scaduto = true;
			break;
		}
		pf[n++] = (struct pollfd){.fd = pout[0], .events = POLLIN};
		if (in && pin[1] >= 0)
			pf[n++] = (struct pollfd){.fd = pin[1], .events = POLLOUT};
		r = poll(pf, (nfds_t)n, (int)(resto > 1000 ? 1000 : resto));
		if (r < 0) {
			if (errno == EINTR)
				continue;
			break;
		}
		if (n == 2 && pf[1].revents) {
			ssize_t w = pf[1].revents & POLLOUT ? write(pin[1], in->s + scritti, in->n - scritti) : -1;

			if (w > 0)
				scritti += (size_t)w;
			if (w < 0 || scritti == in->n) {
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
	/* Anche dopo la fine dell'uscita il figlio ha un tempo massimo: l'utente
	 * potrebbe fermarlo (stesso UID), e rspeak non deve restare appeso. */
	for (;;) {
		pid_t w;

		if (scaduto)
			kill(pid, SIGKILL);
		w = waitpid(pid, &stato, scaduto ? 0 : WNOHANG);
		if (w == pid)
			break;
		if (w < 0 && errno != EINTR)
			return -1;
		if (w == 0) {
			if (ms_adesso() >= scadenza)
				scaduto = true;
			else
				poll(NULL, 0, 10);
		}
	}
	if (scaduto || !WIFEXITED(stato))
		return -1;
	return WEXITSTATUS(stato) == 126 ? -1 : WEXITSTATUS(stato);
}
