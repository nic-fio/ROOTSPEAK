/* Copyright (c) 2026 Nicola Fiorillo
 * SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0 */

/* RootSpeak - Advanced Messaging System for Linux
 * rootspeak-user: internal helper, not a command for the user. It runs with
 * the user's identity, launched by the shell hook (prompt) and by the desktop
 * autostart (agent): it shows the messages and records the read
 * confirmation. */
#include "common.h"

#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <pwd.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/file.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <unistd.h>

#include "event.h"
#include "sessions.h"
#include "text.h"

static char *U, *D; /* user name and their mailbox */
static conf_t conf;
static volatile sig_atomic_t wake, fine;

static void on_wake(int s)
{
	(void)s;
	wake = 1;
}

static void on_end(int s)
{
	(void)s;
	fine = 1;
}

/* zenity exiting interrupts the wait: the answer is recorded at once. */
static void on_child(int s)
{
	(void)s;
}

static char *file_path(const char *below, long long id, const char *suffix)
{
	return xasprintf("%s/%s/%lld%s", D, below, id, suffix);
}

static bool has_entry(const char *below, long long id, const char *suffix)
{
	char *p = file_path(below, id, suffix);
	bool r = exists(p);

	free(p);
	return r;
}

/* True if the copy in the mailbox has expired (an unreadable copy is not
 * treated as expired: it stops being shown only if it is missing). */
static bool expired(long long id)
{
	char *p = file_path("inbox", id, "");
	msg_t m;
	bool r = false;

	if (msg_read(p, &m) == 0) {
		r = msg_expired(&m, now());
		msg_free(&m);
	}
	free(p);
	return r;
}

static void mark_read(long long id)
{
	char *da = file_path("inbox", id, ""), *a = file_path("read", id, ""), *t = file_path("state", id, ".term"),
	     *g = file_path("state", id, ".gui");

	rename(da, a);
	unlink(t);
	unlink(g);
	free(da);
	free(a);
	free(t);
	free(g);
}

/* IDs of the messages to show, in order. Expired messages and those already
 * confirmed (an interruption between the confirmation and the move) go to read/. */
static void pending_n(strv_t *out)
{
	char *inbox = xasprintf("%s/inbox", D);
	strv_t ids = {0};

	list_numbers(inbox, &ids);
	for (size_t i = 0; i < ids.n; i++) {
		long long id;
		char *f;
		struct stat st;

		read_number(ids.v[i], &id);
		f = file_path("inbox", id, "");
		if (stat(f, &st) < 0 || !S_ISREG(st.st_mode)) {
			free(f);
			continue;
		}
		free(f);
		if (has_entry("acks", id, "")) {
			mark_read(id);
			continue;
		}
		if (expired(id)) {
			char *da = file_path("inbox", id, ""), *a = file_path("read", id, "");

			rename(da, a);
			free(da);
			free(a);
			continue;
		}
		strv_add(out, ids.v[i]);
	}
	strv_free(&ids);
	free(inbox);
}

/* True if the user postponed the message on that channel less than N minutes ago. */
static bool postponed(long long id, const char *channel)
{
	char *suff = xasprintf(".%s", channel), *p = file_path("state", id, suff);
	struct stat st;
	bool r = stat(p, &st) == 0 && (long long)(now() - st.st_mtime) < conf.remind_minutes * 60;

	free(suff);
	free(p);
	return r;
}

static void postpone(long long id, const char *channel)
{
	char *suff = xasprintf(".%s", channel), *p = file_path("state", id, suff);
	int fd = open(p, O_WRONLY | O_CREAT | O_CLOEXEC | O_NOFOLLOW, 0644);

	if (fd >= 0) {
		futimens(fd, NULL);
		close(fd);
	}
	event("POSTPONED", id, U, !strcmp(channel, "term") ? "terminal" : "desktop", "", "");
	free(suff);
	free(p);
}

/* Records the confirmation. The first one wins: the confirmation is written
 * to a temporary file and published with link, which fails if acks/ID already
 * exists; so «already confirmed» and «write failed» stay distinct, and a
 * half-written confirmation cannot exist.
 * Result: 0 recorded (or already present); 1 not recorded (the message stays
 * and will be asked about again); 2 message expired; 3 message revoked. */
static int confirm(long long id, const char *channel)
{
	char *ack = file_path("acks", id, ""), *tmp, *dir;
	char line[256];
	int fd, n, r = 0;

	if (exists(ack)) {
		mark_read(id);
		free(ack);
		return 0;
	}
	/* Without a copy in the mailbox the message was revoked: no confirmation.
	 * If the revocation arrives between this check and link, the date decides:
	 * rspeak status does not count a confirmation later than the revocation. */
	if (!has_entry("inbox", id, "")) {
		free(ack);
		return 3;
	}
	if (expired(id)) {
		mark_read(id);
		free(ack);
		return 2;
	}
	tmp = xasprintf("%s/acks/.%lld.%d", D, id, (int)getpid());
	n = snprintf(line, sizeof line, "%lld %s\n", (long long)now(), channel);
	unlink(tmp);
	fd = open(tmp, O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC | O_NOFOLLOW, 0644);
	if (fd < 0 || n <= 0 || write_all(fd, line, (size_t)n) < 0 || fsync(fd) < 0 || close(fd) < 0 ||
	    link(tmp, ack) < 0) {
		const char *err = strerror(errno);

		if (fd >= 0)
			close(fd);
		unlink(tmp);
		if (exists(ack)) {
			mark_read(id);
		} else {
			event("CONFIRMATION_FAILED", id, U, channel, err, "");
			r = 1;
		}
		free(tmp);
		free(ack);
		return r;
	}
	unlink(tmp);
	/* the confirmation reaches the disk before saying «Confirmed» */
	dir = xasprintf("%s/acks", D);
	sync_path(dir);
	free(dir);
	mark_read(id);
	event("CONFIRMED", id, U, channel, "", "");
	free(tmp);
	free(ack);
	return 0;
}

/* ---- terminal: called by the shell hook before every prompt ---- */

static void show_in_terminal(long long id)
{
	char *p = file_path("inbox", id, "");
	msg_t m;
	buf_t h = {0};

	if (msg_read(p, &m) == 0) {
		msg_header(&m, &h);
		putchar('\n');
		printf("── RootSpeak · Message from the administrator · %s ──", h.s);
		printf("\n%s────────────────────────────────────────\n", m.body);
		msg_free(&m);
	}
	buf_free(&h);
	free(p);
}

/* Asks for the confirmation. Result: 0 yes, 1 no, 2 already confirmed
 * elsewhere (for example on the desktop) while the question was waiting,
 * 3 message revoked, 4 message expired while the question was waiting. The
 * terminal stays in canonical mode: what the user is typing is not lost
 * between one check and the next. */
static int ask(long long id)
{
	int tty = open("/dev/tty", O_RDONLY | O_CLOEXEC | O_NOCTTY);
	char answer[256] = "";

	fputs("[RootSpeak] Do you confirm you have read the message? [y/N] ", stdout);
	fflush(stdout);
	if (tty < 0)
		return 1;
	for (;;) {
		struct pollfd p = {.fd = tty, .events = POLLIN};
		int r = poll(&p, 1, 1000);

		if (r > 0) {
			ssize_t l = read(tty, answer, sizeof answer - 1);

			answer[l > 0 ? l : 0] = '\0';
			break;
		}
		if (r < 0 && errno != EINTR)
			break;
		if (has_entry("acks", id, "")) {
			putchar('\n');
			close(tty);
			return 2;
		}
		if (!has_entry("inbox", id, "")) {
			putchar('\n');
			close(tty);
			return 3;
		}
		if (expired(id)) {
			putchar('\n');
			close(tty);
			return 4;
		}
	}
	close(tty);
	return strchr("yY", answer[0]) && answer[0] ? 0 : 1;
}

static int cmd_prompt(bool login)
{
	const char *t = ttyname(0);
	char *where;
	strv_t ids = {0};
	int after = 0;

	if (!t)
		return 0;
	where = xasprintf("terminal %s", !strncmp(t, "/dev/", 5) ? t + 5 : t);
	pending_n(&ids);
	for (size_t i = 0; i < ids.n; i++) {
		long long id;

		read_number(ids.v[i], &id);
		if (!login && postponed(id, "term")) {
			after++;
			continue;
		}
		show_in_terminal(id);
		switch (ask(id)) {
		case 0:
			switch (confirm(id, where)) {
			case 0: fputs("[RootSpeak] Confirmed.", stdout); break;
			case 2: fputs("[RootSpeak] The message has expired: the confirmation was not recorded.", stdout); break;
			case 3: fputs("[RootSpeak] The administrator has revoked the message.", stdout); break;
			default: fputs("[RootSpeak] The confirmation could not be recorded: you will be asked again.", stdout); break;
			}
			break;
		case 2:
			mark_read(id);
			fputs("[RootSpeak] Message already confirmed elsewhere (for example on the desktop).", stdout);
			break;
		case 3:
			fputs("[RootSpeak] The administrator has revoked the message.", stdout);
			break;
		case 4:
			mark_read(id);
			fputs("[RootSpeak] The message has expired.", stdout);
			break;
		default:
			postpone(id, "term");
			printf("[RootSpeak] You will be asked again in %ld minutes.", conf.remind_minutes);
			break;
		}
		putchar('\n');
	}
	if (after == 1)
		puts("[RootSpeak] You have 1 message from the administrator to confirm.");
	else if (after > 1) {
		printf("[RootSpeak] You have %d messages from the administrator to confirm.", after);
		putchar('\n');
	}
	strv_free(&ids);
	free(where);
	return 0;
}

/* ---- desktop: started automatically in the graphical session ---- */

static sigset_t waiting; /* mask during waits: USR1 and end signals get through */

/* Waits at most ms milliseconds, or for a signal. */
static void wait_for(int ms)
{
	struct timespec ts = {ms / 1000, (long)(ms % 1000) * 1000000L};

	ppoll(NULL, 0, &ts, &waiting);
}

/* True if the socket at path (an abstract name if it starts with '@') accepts a connection. */
static bool socket_answers(const char *path)
{
	struct sockaddr_un a = {.sun_family = AF_UNIX};
	size_t n = strlen(path);
	int fd;
	bool r;

	if (n >= sizeof a.sun_path)
		return true;
	memcpy(a.sun_path, path, n);
	if (path[0] == '@')
		a.sun_path[0] = '\0';
	fd = socket(AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC, 0);
	if (fd < 0)
		return true;
	r = connect(fd, (struct sockaddr *)&a, (socklen_t)(offsetof(struct sockaddr_un, sun_path) + n)) == 0;
	close(fd);
	return r;
}

/* False if the display of the session is gone (session ended, display manager
 * restarted, compositor crashed). zenity also exits with 1 when it loses the
 * display, exactly as for «Later»: only a display still there tells them apart.
 * When in doubt, true. */
static bool display_alive(void)
{
	const char *w = getenv("WAYLAND_DISPLAY");
	const char *d = getenv("DISPLAY");
	const char *run = getenv("XDG_RUNTIME_DIR");
	bool r = true;

	if (!graphical_session(getuid()))
		return false;
	if (w && *w) {
		char *p = w[0] == '/' ? xstrdup(w) : xasprintf("%s/%s", run && *run ? run : "/tmp", w);

		r = socket_answers(p);
		free(p);
	} else if (d && d[0] == ':') {
		int num = atoi(d + 1);
		char *p = xasprintf("/tmp/.X11-unix/X%d", num);
		char *abs = xasprintf("@/tmp/.X11-unix/X%d", num);

		r = socket_answers(abs) || socket_answers(p);
		free(abs);
		free(p);
	}
	return r;
}

static void report_failed_confirmation(void)
{
	pid_t pid = fork();

	if (pid == 0) {
		int nul = open("/dev/null", O_RDWR);

		if (nul >= 0) {
			dup2(nul, 1);
			dup2(nul, 2);
		}
		execlp("notify-send", "notify-send", "-a", "RootSpeak", "-i", "rootspeak", "RootSpeak · Confirmation not recorded",
		       "The confirmation could not be recorded: the message will be shown again.", (char *)NULL);
		_exit(127);
	}
	if (pid > 0)
		while (waitpid(pid, NULL, 0) < 0 && errno == EINTR)
			;
}

/* The confirmation dialog. The agent waits for it and records the answer as
 * soon as it arrives; meanwhile, every second, it closes the dialog if the
 * user confirmed from a terminal, if the administrator revoked the message or
 * if it expired. The wake-up signal (a new message) does not close it. */
static void show_dialog(long long id)
{
	char *f = file_path("inbox", id, "");
	msg_t m;
	buf_t txt = {0};
	pid_t pid;
	int state = 0;
	bool closed_by_us = false;
	long long wait_end = 0;

	if (msg_read(f, &m) < 0) {
		free(f);
		return;
	}
	msg_header(&m, &txt);
	buf_printf(&txt, "\n\n%s", m.body);
	msg_free(&m);
	fflush(stdout);
	pid = fork();
	if (pid == 0) {
		char *title_text = xasprintf("--title=%s", "RootSpeak · Message from the administrator");
		char *text = xasprintf("--text=%s", txt.s);
		char *ok = xasprintf("--ok-label=%s", "I have read it");
		char *no = xasprintf("--cancel-label=%s", "Later");
		int nul = open("/dev/null", O_RDWR);
		sigset_t empty;

		sigemptyset(&empty);
		sigprocmask(SIG_SETMASK, &empty, NULL);
		signal(SIGCHLD, SIG_DFL);
		signal(SIGUSR1, SIG_DFL);
		signal(SIGTERM, SIG_DFL);
		signal(SIGHUP, SIG_DFL);
		signal(SIGINT, SIG_DFL);
		if (nul >= 0)
			dup2(nul, 2);
		execlp("zenity", "zenity", "--question", "--no-markup", "--width=460", title_text, text, ok, no, (char *)NULL);
		_exit(127);
	}
	buf_free(&txt);
	if (pid < 0) {
		free(f);
		return;
	}
	for (;;) {
		pid_t w = waitpid(pid, &state, WNOHANG);

		if (w == pid)
			break;
		if (w < 0 && errno != EINTR)
			break;
		if (!closed_by_us && (has_entry("acks", id, "") || !has_entry("inbox", id, "") || expired(id))) {
			kill(pid, SIGTERM);
			closed_by_us = true;
		}
		/* on logout: wait a little longer for the dialog (it receives the
		 * signal too), then close it */
		if (fine && !wait_end)
			wait_end = (long long)now() + 2;
		if (wait_end && (long long)now() >= wait_end && !closed_by_us) {
			kill(pid, SIGTERM);
			closed_by_us = true;
		}
		wait_for(1000);
	}
	if (has_entry("acks", id, "") || !has_entry("inbox", id, "")) {
		free(f);
		return;
	}
	if (expired(id)) {
		mark_read(id);
		free(f);
		return;
	}
	/* zenity exits with 0 for «I have read it», with 1 for «Later» or the dialog
	 * closed by the user. Other results (dialog killed) are not the user's
	 * choice: no postponement, the dialog comes back at the next round. */
	if (WIFEXITED(state) && WEXITSTATUS(state) == 0) {
		if (confirm(id, "desktop") == 1 && has_entry("inbox", id, ""))
			report_failed_confirmation();
	} else if (WIFEXITED(state) && WEXITSTATUS(state) == 1) {
		/* «Later», or zenity lost the display (session ended, display
		 * manager restarted): only a display still there tells them apart.
		 * Checked at once: a reminder arriving right after «Later» must find
		 * the postponement already written (scenario I11). */
		if (!fine && display_alive())
			postpone(id, "gui");
	}
	free(f);
}

static char *ready;

static void remove_ready(void)
{
	if (ready)
		unlink(ready);
}

static int cmd_agent(void)
{
	const char *run = getenv("XDG_RUNTIME_DIR");
	char *lock = xasprintf("%s/rootspeak-agent.lock", run && *run ? run : "/tmp");
	int fd = open(lock, O_WRONLY | O_CREAT | O_CLOEXEC | O_NOFOLLOW, 0600);
	char s[32];
	int n;
	sigset_t block_signals;
	struct sigaction sa = {0};

	/* Only one agent per user. The lock is not inherited by child processes
	 * (O_CLOEXEC): an orphaned dialog does not block a new agent. */
	if (fd < 0 || flock(fd, LOCK_EX | LOCK_NB) < 0)
		return 0;
	/* On logout SIGTERM arrives: the agent finishes recording the answer
	 * already given and exits at the first safe point. Signals stay blocked
	 * except during waits: none is lost. */
	sa.sa_handler = on_end;
	sigaction(SIGTERM, &sa, NULL);
	sigaction(SIGHUP, &sa, NULL);
	sigaction(SIGINT, &sa, NULL);
	sa.sa_handler = on_child;
	sigaction(SIGCHLD, &sa, NULL);
	sigemptyset(&block_signals);
	sigaddset(&block_signals, SIGCHLD);
	sigaddset(&block_signals, SIGUSR1);
	sigaddset(&block_signals, SIGTERM);
	sigaddset(&block_signals, SIGHUP);
	sigaddset(&block_signals, SIGINT);
	sigprocmask(SIG_BLOCK, &block_signals, &waiting);
	sigdelset(&waiting, SIGCHLD);
	sigdelset(&waiting, SIGUSR1);
	sigdelset(&waiting, SIGTERM);
	sigdelset(&waiting, SIGHUP);
	sigdelset(&waiting, SIGINT);
	/* `rspeak send` sends SIGUSR1 to wake the agent up, but only to the PID
	 * written here, that is to an agent already able to receive it. */
	ready = xasprintf("%s/rootspeak-agent.ready", run && *run ? run : "/tmp");
	atexit(remove_ready);
	n = snprintf(s, sizeof s, "%d\n", (int)getpid());
	if (write_atomic(ready, s, (size_t)n, 0644) < 0)
		return 1;
	while (!fine && graphical_session(getuid())) {
		strv_t ids = {0};

		/* a wake-up arriving from here on (even with a dialog open) starts
		 * the round again at once */
		wake = 0;
		/* the configuration is reread at every round: a change applies at once */
		conf_read(&conf);
		pending_n(&ids);
		for (size_t i = 0; i < ids.n && !fine; i++) {
			long long id;

			read_number(ids.v[i], &id);
			/* display gone: no dialog until the next round */
			if (!display_alive())
				break;
			if (!postponed(id, "gui"))
				show_dialog(id);
		}
		strv_free(&ids);
		if (fine)
			break;
		/* interruptible wait: the signal from `rspeak send` ends it at once */
		for (long ms = conf.agent_poll * 1000; ms > 0 && !wake && !fine; ms -= 1000)
			wait_for(ms > 1000 ? 1000 : (int)ms);
	}
	return 0;
}

int main(int argc, char **argv)
{
	struct sigaction sa = {0};
	struct passwd *pw;

	/* First of all: the wake-up signal must not kill the agent while it
	 * starts. */
	sa.sa_handler = on_wake;
	sigaction(SIGUSR1, &sa, NULL);
	rspeak_init("rootspeak-user");
	conf_read(&conf);
	pw = getpwuid(getuid());
	if (!pw)
		return 1;
	U = xstrdup(pw->pw_name);
	D = xasprintf("%s/users/%s", rspeak_var, U);
	if (argc >= 2 && !strcmp(argv[1], "prompt"))
		return cmd_prompt(argc >= 3 && !strcmp(argv[2], "--login"));
	if (argc >= 2 && !strcmp(argv[1], "agent"))
		return cmd_agent();
	/* tests only: recording the confirmation, on its own */
	if (rspeak_test && argc == 4 && !strcmp(argv[1], "confirm")) {
		long long id;

		return read_number(argv[2], &id) ? confirm(id, argv[3]) : 1;
	}
	fputs("rootspeak-user: internal RootSpeak helper, not meant to be run directly", stderr);
	fputc('\n', stderr);
	return 1;
}
