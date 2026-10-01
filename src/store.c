/* RootSpeak - Advanced Messaging System for Linux
 * Users' mailboxes (always with their identity), terminals, agent. */
#include "store.h"

#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <sys/wait.h>
#include <unistd.h>

#include "sessions.h"
#include "text.h"

/* ---- operations run as the user (in the child process) ---- */

typedef struct {
	const char *mailbox; /* users/U */
	long long id;
} op_t;

static char *in_mailbox(const op_t *o, const char *below, const char *suffix)
{
	return xasprintf("%s/%s/%lld%s", o->mailbox, below, o->id, suffix);
}

/* stdin: the message. Returns 0 if the copy is there, 1 otherwise. */
static int op_deliver(void *arg)
{
	const op_t *o = arg;
	static const char *below[] = {"inbox", "read", "acks", "state"};
	char *read_done, *confirmed, *copy, *tmp;
	buf_t b = {0};
	struct stat st;
	int fd, r = 1;

	for (int i = 0; i < 4; i++) {
		char *d = xasprintf("%s/%s", o->mailbox, below[i]);

		if (mkdir(d, 0755) < 0 && errno != EEXIST)
			return 1;
		free(d);
	}
	read_done = in_mailbox(o, "read", "");
	confirmed = in_mailbox(o, "acks", "");
	if (exists(read_done) || exists(confirmed))
		return 0;
	if (read_fd(0, RSPEAK_MAX_MSG, &b) < 0 || !b.n)
		return 1;
	copy = in_mailbox(o, "inbox", "");
	tmp = in_mailbox(o, "inbox", ".tmp");
	unlink(tmp);
	fd = open(tmp, O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC | O_NOFOLLOW, 0644);
	if (fd >= 0) {
		if (write_all(fd, b.s, b.n) == 0 && close(fd) == 0 && rename(tmp, copy) == 0)
			r = 0;
		else
			unlink(tmp);
	}
	/* the copy really is there, not empty */
	if (r == 0 && (stat(copy, &st) < 0 || !S_ISREG(st.st_mode) || st.st_size == 0))
		r = 1;
	return r;
}

static int op_take(void *arg)
{
	const op_t *o = arg;
	char *copy = in_mailbox(o, "inbox", ""), *t = in_mailbox(o, "state", ".term"),
	     *g = in_mailbox(o, "state", ".gui");

	unlink(copy);
	unlink(t);
	unlink(g);
	return exists(copy) ? 1 : 0;
}

static int op_clear_postponements(void *arg)
{
	const op_t *o = arg;
	char *t = in_mailbox(o, "state", ".term"), *g = in_mailbox(o, "state", ".gui");
	int r;

	unlink(t);
	unlink(g);
	r = exists(t) || exists(g) ? 1 : 0;
	free(t);
	free(g);
	return r;
}

static int op_remove(void *arg)
{
	const op_t *o = arg;
	static const char *f[][2] = {{"inbox", ""}, {"read", ""}, {"acks", ""}, {"state", ".term"}, {"state", ".gui"}};

	for (size_t i = 0; i < sizeof f / sizeof f[0]; i++) {
		char *p = in_mailbox(o, f[i][0], f[i][1]);

		unlink(p);
		free(p);
	}
	return 0;
}

/* Reads at most n bytes from the start of a regular file (not a pipe). */
static bool read_start(const char *path, size_t n, buf_t *out)
{
	int fd = open(path, O_RDONLY | O_CLOEXEC | O_NOCTTY | O_NONBLOCK);
	struct stat st;
	char tmp[256];
	ssize_t r;

	if (fd < 0)
		return false;
	if (fstat(fd, &st) < 0 || !S_ISREG(st.st_mode) || n > sizeof tmp) {
		close(fd);
		return false;
	}
	r = read(fd, tmp, n);
	close(fd);
	if (r < 0)
		return false;
	buf_add(out, tmp, (size_t)r);
	return true;
}

/* stdin: the IDs, one per line. stdout: «A ID first-line» and «S ID date». Only
 * those IDs are looked up: thousands of fake files in the mailbox do not matter. */
static int op_read(void *arg)
{
	const char *mailbox = arg;
	buf_t in = {0};

	if (chdir(mailbox) < 0)
		return 0;
	read_fd(0, (size_t)1 << 22, &in);
	for (char *p = in.s; p && *p;) {
		size_t len = strcspn(p, "\n");
		char id[24];

		if (len && len < sizeof id) {
			buf_t b = {0};
			char *f;
			struct stat st;
			long long more = 0;

			memcpy(id, p, len);
			id[len] = '\0';
			if (!only_digits(id))
				goto next_item;
			f = xasprintf("acks/%s", id);
			if (read_start(f, 200, &b)) {
				size_t line = b.s ? strcspn(b.s, "\n") : 0;

				printf("A %s %.*s\n", id, (int)line, b.s ? b.s : "");
			}
			free(f);
			buf_free(&b);
			for (int k = 0; k < 2; k++) {
				f = xasprintf("state/%s.%s", id, k ? "gui" : "term");
				if (stat(f, &st) == 0 && S_ISREG(st.st_mode) && st.st_mtime > more)
					more = st.st_mtime;
				free(f);
			}
			if (more)
				printf("S %s %lld\n", id, more);
		}
next_item:
		p += len;
		if (*p)
			p++;
	}
	return 0;
}

typedef struct {
	uid_t uid;
} op_wake_t;

/* Sends SIGUSR1 to the ready agent: the PID written in rootspeak-agent.ready, if it
 * really is the RootSpeak agent (exact command line). Returns 0 if woken up. */
static int op_wake(void *arg)
{
	const op_wake_t *o = arg;
	char *ready = xasprintf("/run/user/%u/rootspeak-agent.ready", (unsigned)o->uid), *cmd, *expected;
	buf_t b = {0}, c = {0};
	long long pid;
	size_t la;
	bool ok;

	if (read_file(ready, 64, true, &b) < 0 || !b.s)
		return 1;
	b.s[strcspn(b.s, "\n")] = '\0';
	if (!read_number(b.s, &pid) || pid <= 1 || pid > 1 << 22)
		return 1;
	cmd = xasprintf("/proc/%lld/cmdline", pid);
	expected = xasprintf("%s/rootspeak-user", rspeak_libdir);
	la = strlen(expected);
	ok = read_file(cmd, 4096, false, &c) == 0 && c.n == la + 1 + 6 && !memcmp(c.s, expected, la + 1) &&
	     !memcmp(c.s + la + 1, "agent", 6);
	if (!ok)
		return 1;
	return kill((pid_t)pid, SIGUSR1) == 0 ? 0 : 1;
}

/* ---- on root's side ---- */

static char *mailbox_of(const user_t *u)
{
	return xasprintf("%s/users/%s", rspeak_var, u->name);
}

/* users/U: root creates it (700) and gives it to the user. If it is still owned by root (a
 * sending interrupted between the creation and the chown), it is fixed: only root
 * writes in users/, so it is root's own. */
static bool prepare_mailbox(const user_t *u, const char *d)
{
	struct stat st;

	if (lstat(d, &st) < 0) {
		if (mkdir(d, 0700) < 0 && errno != EEXIST)
			return false;
		if (lstat(d, &st) < 0)
			return false;
	}
	if (!S_ISDIR(st.st_mode))
		return false;
	if (geteuid() == 0 && !rspeak_test && st.st_uid == 0 && lchown(d, u->uid, u->gid) < 0)
		return false;
	return true;
}

bool deliver_copy(const user_t *u, long long id, const buf_t *msg)
{
	char *d = mailbox_of(u);
	op_t o = {d, id};
	bool ok = prepare_mailbox(u, d) && as_user(u, op_deliver, &o, msg, NULL, 0, 20) == 0;

	free(d);
	return ok;
}

bool remove_copy(const user_t *u, long long id)
{
	char *d = mailbox_of(u);
	op_t o = {d, id};
	bool ok = !is_folder(d) || as_user(u, op_take, &o, NULL, NULL, 0, 20) == 0;

	free(d);
	return ok;
}

bool clear_postponements(const user_t *u, long long id)
{
	char *d = mailbox_of(u);
	op_t o = {d, id};
	bool ok = is_folder(d) && as_user(u, op_clear_postponements, &o, NULL, NULL, 0, 20) == 0;

	free(d);
	return ok;
}

void remove_copies(const user_t *u, long long id)
{
	char *d = mailbox_of(u);
	op_t o = {d, id};

	if (is_folder(d))
		as_user(u, op_remove, &o, NULL, NULL, 0, 20);
	free(d);
}

void read_mailbox(const user_t *u, const strv_t *ids, mailbox_t *out)
{
	char *d = mailbox_of(u);
	buf_t in = {0}, raw = {0}, clean = {0};

	memset(out, 0, sizeof *out);
	for (size_t i = 0; i < ids->n; i++)
		buf_printf(&in, "%s\n", ids->v[i]);
	if (!is_folder(d) || !in.n || as_user(u, op_read, d, &in, &raw, (size_t)1 << 22, 20) < 0)
		goto fine;
	mailbox_from_text(raw.s ? raw.s : "", raw.n, out);
fine:
	buf_free(&in);
	buf_free(&raw);
	buf_free(&clean);
	free(d);
}

void mailbox_from_text(const char *raw, size_t n, mailbox_t *out)
{
	buf_t clean = {0};

	memset(out, 0, sizeof *out);

	/* what comes from the mailbox is untrusted data: cleaned */
	clean_text(raw, n, &clean);
	for (char *p = clean.s; p && *p;) {
		size_t len = strcspn(p, "\n");
		char kind = p[0];
		char *line = xmalloc(len + 1), *sp, *rest;
		long long id;

		memcpy(line, p, len);
		line[len] = '\0';
		p += len;
		if (*p)
			p++;
		if (len < 3 || line[1] != ' ' || !(sp = strchr(line + 2, ' '))) {
			free(line);
			continue;
		}
		*sp = '\0';
		rest = sp + 1;
		if (!read_number(line + 2, &id)) {
			free(line);
			continue;
		}
		{
			mailbox_item_t *v = NULL;

			for (size_t k = 0; k < out->n && !v; k++)
				if (out->v[k].id == id)
					v = &out->v[k];

			if (!v) {
				out->v = xrealloc(out->v, (out->n + 1) * sizeof *out->v);
				v = &out->v[out->n++];
				memset(v, 0, sizeof *v);
				v->id = id;
			}
			if (kind == 'A' && !v->confirm)
				v->confirm = xstrdup(rest);
			else if (kind == 'S') {
				long long t;

				if (read_number(rest, &t) && t > v->postponement)
					v->postponement = t;
			}
		}
		free(line);
	}
	buf_free(&clean);
}

const mailbox_item_t *mailbox_item(const mailbox_t *c, long long id)
{
	for (size_t i = 0; i < c->n; i++)
		if (c->v[i].id == id)
			return &c->v[i];
	return NULL;
}

void mailbox_free(mailbox_t *c)
{
	for (size_t i = 0; i < c->n; i++)
		free(c->v[i].confirm);
	free(c->v);
	memset(c, 0, sizeof *c);
}

/* ---- terminals ---- */

bool write_terminal(const char *t, uid_t uid, const char *txt, size_t n)
{
	int fd = open(t, O_WRONLY | O_NOCTTY | O_NONBLOCK | O_CLOEXEC);
	struct timespec start, time_now;
	struct stat st;
	size_t done = 0;

	if (fd < 0)
		return false;
	/* the owner of the opened terminal, not of the name */
	if (fstat(fd, &st) < 0 || st.st_uid != uid || (!S_ISCHR(st.st_mode) && !rspeak_test)) {
		close(fd);
		return false;
	}
	clock_gettime(CLOCK_MONOTONIC, &start);
	while (done < n) {
		ssize_t w = write(fd, txt + done, n - done);

		if (w > 0) {
			done += (size_t)w;
			continue;
		}
		if (w < 0 && errno != EAGAIN && errno != EINTR)
			break;
		clock_gettime(CLOCK_MONOTONIC, &time_now);
		if (time_now.tv_sec - start.tv_sec >= 3)
			break;
		poll(&(struct pollfd){.fd = fd, .events = POLLOUT}, 1, 100);
	}
	close(fd);
	return done == n;
}

/* ---- desktop agent ---- */

void wake_agent(const user_t *u)
{
	op_wake_t o = {u->uid};
	char *agent, *machine;
	pid_t pid;

	if (rspeak_test || !graphical_session(u->uid))
		return;
	if (as_user(u, op_wake, &o, NULL, NULL, 0, 5) == 0)
		return;
	/* No ready agent: one is started in the systemd user manager, which
	 * already knows the graphical environment. If one was starting, the new one finds the
	 * lock and exits; the one that was starting reads the mailbox on its first round. */
	agent = xasprintf("%s/rootspeak-user", rspeak_libdir);
	machine = xasprintf("--machine=%s@.host", u->name);
	fflush(stdout);
	pid = fork();
	if (pid == 0) {
		int nul = open("/dev/null", O_RDWR);

		if (nul >= 0) {
			dup2(nul, 0);
			dup2(nul, 1);
		}
		if (geteuid() == 0)
			execlp("systemd-run", "systemd-run", "--user", machine, "--collect", "--quiet", agent, "agent",
			       (char *)NULL);
		else
			execlp("systemd-run", "systemd-run", "--user", "--collect", "--quiet", agent, "agent", (char *)NULL);
		_exit(127);
	}
	if (pid > 0)
		while (waitpid(pid, NULL, 0) < 0 && errno == EINTR)
			;
	free(agent);
	free(machine);
}
