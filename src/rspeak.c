/* Copyright (c) 2026 Nicola Fiorillo
 * SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0 */

/* RootSpeak - Advanced Messaging System for Linux
 * rspeak: sending and managing messages. Reserved to administrators: it always
 * runs as root, even for the help and the version, and re-runs itself with
 * sudo. RSPEAK_TEST=1 lets you try it without root on a test folder. */
#include "common.h"

#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <pwd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/file.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <systemd/sd-journal.h>
#include <unistd.h>

#include "rspeak.h"
#include "store.h"
#include "event.h"
#include "help.h"
#include "sessions.h"
#include "text.h"
#include "user.h"

static char empty_f[1];

static char *sent_dir(void)
{
	return xasprintf("%s/sent", rspeak_var);
}

static char *msg_dir(long long id)
{
	return xasprintf("%s/sent/%lld", rspeak_var, id);
}

static char *in_msg_dir(long long id, const char *name)
{
	return xasprintf("%s/sent/%lld/%s", rspeak_var, id, name);
}

/* Who is using rspeak: the administrator who came through sudo, or whoever runs it. */
static const char *author(void)
{
	static char name[64];
	const char *s = getenv("SUDO_USER");
	struct passwd *pw;

	if (s && *s && strlen(s) < sizeof name && getpwnam(s)) {
		snprintf(name, sizeof name, "%s", s);
		return name;
	}
	pw = getpwuid(getuid());
	snprintf(name, sizeof name, "%s", pw ? pw->pw_name : "?");
	return name;
}

/* Opens sent/ID/lock and takes the lock (exclusive); if nb and the lock is held,
 * returns -1. The descriptor is not passed to child processes. */
static int take_lock(long long id, bool nb)
{
	char *p = in_msg_dir(id, "lock");
	int fd = open(p, O_WRONLY | O_CREAT | O_CLOEXEC | O_NOFOLLOW, 0600);

	free(p);
	if (fd < 0)
		return -1;
	while (flock(fd, LOCK_EX | (nb ? LOCK_NB : 0)) < 0) {
		if (errno == EINTR)
			continue;
		close(fd);
		return -1;
	}
	return fd;
}

static bool mark(long long id, const char *name)
{
	char *p = in_msg_dir(id, name);
	bool r = exists(p);

	free(p);
	return r;
}

static void set_mark(long long id, const char *name)
{
	char *p = in_msg_dir(id, name);
	int fd = open(p, O_WRONLY | O_CREAT | O_CLOEXEC | O_NOFOLLOW, 0600);

	if (fd >= 0)
		close(fd);
	free(p);
}

static void clear_mark(long long id, const char *name)
{
	char *p = in_msg_dir(id, name);

	unlink(p);
	free(p);
}

static void read_recipients(long long id, strv_t *out)
{
	char *p = in_msg_dir(id, "recipients");
	buf_t b = {0};

	if (read_file(p, 1 << 22, true, &b) == 0)
		for (char *s = strtok(b.s ? b.s : empty_f, " \t\n"); s; s = strtok(NULL, " \t\n"))
			strv_add(out, s);
	buf_free(&b);
	free(p);
}

/* Deliveries recorded in sent/ID/delivery: user → terminals written to. */
typedef struct {
	strv_t user_list;
	strv_t terminals;
} deliveries_t;

static void read_deliveries(long long id, deliveries_t *c)
{
	char *p = in_msg_dir(id, "delivery");
	buf_t b = {0};

	memset(c, 0, sizeof *c);
	if (read_file(p, 1 << 24, true, &b) == 0)
		for (char *r = b.s; r && *r;) {
			size_t len = strcspn(r, "\n");
			char u[256] = "", t[32] = "0";
			char *line = xmalloc(len + 1);

			memcpy(line, r, len);
			line[len] = '\0';
			if (sscanf(line, "%255s %*s %31s", u, t) >= 1 && !strv_has(&c->user_list, u)) {
				strv_add(&c->user_list, u);
				strv_add(&c->terminals, t);
			}
			free(line);
			r += len;
			if (*r)
				r++;
		}
	buf_free(&b);
	free(p);
}

static const char *delivered_to(const deliveries_t *c, const char *u)
{
	for (size_t i = 0; i < c->user_list.n; i++)
		if (!strcmp(c->user_list.v[i], u))
			return c->terminals.v[i];
	return NULL;
}

static void deliveries_free(deliveries_t *c)
{
	strv_free(&c->user_list);
	strv_free(&c->terminals);
}

static void record_delivery(long long id, const char *u, int nterm)
{
	char *p = in_msg_dir(id, "delivery");
	int fd = open(p, O_WRONLY | O_CREAT | O_APPEND | O_CLOEXEC | O_NOFOLLOW, 0600);

	if (fd >= 0) {
		char line[400];
		int n = snprintf(line, sizeof line, "%s %lld %d\n", u, (long long)now(), nterm);

		if (n > 0 && (size_t)n < sizeof line)
			write_all(fd, line, (size_t)n);
		close(fd);
	}
	free(p);
}

static bool read_msg_text(long long id, buf_t *out)
{
	char *p = in_msg_dir(id, "msg");
	bool ok = read_file(p, RSPEAK_MAX_MSG, true, out) == 0 && out->n > 0;

	free(p);
	return ok;
}

/* ---- revocation and deletion (also used by recovery) ---- */

/* Removes the copies of message ID and the postponements from the mailboxes, as
 * each user. sent/ID/revoking stays as long as some copy could not be removed. */
static bool remove_copies_all(long long id)
{
	strv_t dest = {0};
	int missing = 0;

	read_recipients(id, &dest);
	for (size_t i = 0; i < dest.n; i++) {
		user_t u;

		if (!user_find(dest.v[i], &u))
			continue;
		if (!remove_copy(&u, id))
			missing++;
		user_free(&u);
	}
	strv_free(&dest);
	if (missing)
		return false;
	clear_mark(id, "revoking");
	return true;
}

/* Removes the copies, confirmations and postponements of a message already moved
 * to sent/.deleting-ID, then its folder. Can be repeated. */
static void remove_folder(const char *dir, long long id)
{
	char *p = xasprintf("%s/recipients", dir);
	buf_t b = {0};
	DIR *d;

	if (read_file(p, 1 << 22, true, &b) == 0)
		for (char *s = strtok(b.s ? b.s : empty_f, " \t\n"); s; s = strtok(NULL, " \t\n")) {
			user_t u;

			if (user_find(s, &u)) {
				remove_copies(&u, id);
				user_free(&u);
			}
		}
	buf_free(&b);
	free(p);
	/* the folder contains only root's files */
	if ((d = opendir(dir))) {
		struct dirent *e;
		int dfd = dirfd(d);

		while ((e = readdir(d)))
			if (strcmp(e->d_name, ".") && strcmp(e->d_name, ".."))
				unlinkat(dfd, e->d_name, 0);
		closedir(d);
	}
	rmdir(dir);
}

/* ---- recovery: runs at the start of send, list, status, revoke, log ---- */

void recover(void)
{
	char *sd = sent_dir();
	strv_t ids = {0};
	DIR *d;

	if (list_numbers(sd, &ids) < 0) {
		free(sd);
		return;
	}
	for (size_t i = 0; i < ids.n; i++) {
		long long id;
		int lock;

		read_number(ids.v[i], &id);
		if (!mark(id, "incomplete") && !mark(id, "revoking"))
			continue;
		/* a send still in progress holds the lock: it was not interrupted, skip it */
		if ((lock = take_lock(id, true)) < 0)
			continue;
		if (mark(id, "incomplete")) {
			buf_t msg = {0};
			msg_t m;
			strv_t dest = {0};
			deliveries_t cons;
			int new_ones = 0, missing = 0;
			char *dir = msg_dir(id);

			read_recipients(id, &dest);
			if (!read_msg_text(id, &msg) || !dest.n || msg_from_text(msg.s, msg.n, &m) < 0) {
				char *f = in_msg_dir(id, "failed");
				char data[32];
				int n = snprintf(data, sizeof data, "%lld\n", (long long)now());

				write_atomic(f, data, (size_t)n, 0600);
				free(f);
				clear_mark(id, "incomplete");
				event("CANCELLED", id, "", "", "", "");
				notice("message %lld was interrupted before being saved and has been cancelled", id);
			} else if (mark(id, "revoked") || msg_expired(&m, now())) {
				clear_mark(id, "incomplete");
				msg_free(&m);
			} else {
				read_deliveries(id, &cons);
				for (size_t k = 0; k < dest.n; k++) {
					user_t u;
					bool recorded = delivered_to(&cons, dest.v[k]) != NULL;

					if (!user_find(dest.v[k], &u)) {
						missing++;
						continue;
					}
					/* A copy already recorded is checked again too: after
					 * a power failure it might not be on disk. */
					if (deliver_copy(&u, id, &msg)) {
						if (!recorded) {
							record_delivery(id, u.name, 0);
							event("DELIVERED", id, u.name, "", "", "");
							wake_agent(&u);
							new_ones++;
						}
					} else {
						missing++;
					}
					user_free(&u);
				}
				deliveries_free(&cons);
				msg_free(&m);
				if (!missing) {
					char *users = xasprintf("%s/users", rspeak_var);

					syncfs_path(users);
					sync_path(dir);
					free(users);
					clear_mark(id, "incomplete");
				}
				if (new_ones) {
					char det[24];

					snprintf(det, sizeof det, "%d", new_ones);
					event("RECOVERED", id, "", "", det, "");
					notice("completed delivery of message %lld to %d recipients", id, new_ones);
				}
				if (missing)
					notice("message %lld still not delivered to %d recipients (see rspeak status %lld)", id,
					       missing, id);
			}
			strv_free(&dest);
			buf_free(&msg);
			free(dir);
		}
		if (mark(id, "revoking"))
			remove_copies_all(id);
		close(lock);
	}
	strv_free(&ids);
	/* deletions left half done */
	if ((d = opendir(sd))) {
		struct dirent *e;
		strv_t del = {0};

		while ((e = readdir(d)))
			if (!strncmp(e->d_name, ".deleting-", 10) && only_digits(e->d_name + 10))
				strv_add(&del, e->d_name);
		closedir(d);
		for (size_t i = 0; i < del.n; i++) {
			char *dir = xasprintf("%s/%s", sd, del.v[i]);
			long long id;

			if (read_number(del.v[i] + 10, &id))
				remove_folder(dir, id);
			free(dir);
		}
		strv_free(&del);
	}
	free(sd);
}

/* ---- recipients ---- */

static void resolve_recipients(const char *to, strv_t *out)
{
	char *copy = xstrdup(to), *save = NULL;

	for (char *v = strtok_r(copy, ",", &save); v; v = strtok_r(NULL, ",", &save)) {
		strv_t l = {0};

		if (!strcmp(v, "all"))
			human_users(&l);
		else if (!strcmp(v, "online"))
			online_users(&l);
		else if (v[0] == '@') {
			if (!group_members(v + 1, &l))
				die("no such group: %s", v + 1);
		} else {
			if (!getpwnam(v))
				die("no such user: %s", v);
			strv_add(&l, v);
		}
		for (size_t i = 0; i < l.n; i++)
			if (*l.v[i] && !strv_has(out, l.v[i]))
				strv_add(out, l.v[i]);
		strv_free(&l);
	}
	free(copy);
	strv_sort(out);
}

/* ---- sending ---- */

static long long expiry_from(const char *s)
{
	size_t n = strlen(s);
	long long v;

	if (n >= 2 && strchr("mhd", s[n - 1])) {
		char *num = xstrdup(s);

		num[n - 1] = '\0';
		if (read_number(num, &v)) {
			free(num);
			return (long long)now() + v * (s[n - 1] == 'm' ? 60 : s[n - 1] == 'h' ? 3600 : 86400);
		}
		free(num);
	}
	/* date and time: parsed by date -d, as in the prototype */
	{
		int p[2];
		pid_t pid;
		buf_t b = {0};
		int state;

		if (pipe2(p, O_CLOEXEC) < 0)
			die("invalid expiry: %s", s);
		fflush(stdout);
		pid = fork();
		if (pid == 0) {
			int nul = open("/dev/null", O_WRONLY);

			dup2(p[1], 1);
			if (nul >= 0)
				dup2(nul, 2);
			execlp("date", "date", "-d", s, "+%s", (char *)NULL);
			_exit(127);
		}
		close(p[1]);
		read_fd(p[0], 64, &b);
		close(p[0]);
		waitpid(pid, &state, 0);
		if (pid < 0 || !WIFEXITED(state) || WEXITSTATUS(state) || !b.s)
			die("invalid expiry: %s", s);
		b.s[strcspn(b.s, "\n")] = '\0';
		if (!read_number(b.s, &v))
			die("invalid expiry: %s", s);
		buf_free(&b);
		return v;
	}
}

/* The next ID: a sequence under flock; if the folder already exists (the
 * sequence went back after a power failure), move on to the next one. */
static long long next_id(void)
{
	char *seq = xasprintf("%s/sent/.seq", rspeak_var), *lockp = xasprintf("%s/sent/.seq.lock", rspeak_var);
	int fd = open(lockp, O_WRONLY | O_CREAT | O_CLOEXEC | O_NOFOLLOW, 0600);
	buf_t b = {0};
	long long n = 0;
	char s[32];
	int len;

	if (fd < 0 || flock(fd, LOCK_EX) < 0)
		die("%s: %s", lockp, strerror(errno));
	if (read_file(seq, 64, true, &b) == 0 && b.s) {
		b.s[strcspn(b.s, "\n")] = '\0';
		if (!read_number(b.s, &n))
			n = 0;
	}
	for (;;) {
		char *d;

		n++;
		d = msg_dir(n);
		if (mkdir(d, 0700) == 0) {
			free(d);
			break;
		}
		if (errno != EEXIST)
			die("%s: %s", d, strerror(errno));
		free(d);
	}
	len = snprintf(s, sizeof s, "%lld\n", n);
	if (write_atomic(seq, s, (size_t)len, 0600) < 0)
		die("%s: %s", seq, strerror(errno));
	close(fd);
	buf_free(&b);
	free(seq);
	free(lockp);
	return n;
}

static void prepare_store(void)
{
	char *users = xasprintf("%s/users", rspeak_var), *sd = sent_dir();

	mkdir(rspeak_var, 0755);
	mkdir(users, 0755);
	mkdir(sd, 0700);
	if (!is_folder(users) || !is_folder(sd))
		die("%s: %s", rspeak_var, strerror(errno));
	free(users);
	free(sd);
}

/* The message formatted for a terminal, with «\r\n» (the terminal may be
 * in raw mode, for example inside an editor). */
static void terminal_text(const msg_t *m, buf_t *out)
{
	buf_t t = {0}, h = {0};

	msg_header(m, &h);
	buf_adds(&t, "\n");
	buf_printf(&t, "── RootSpeak · Message from the administrator · %s ──", h.s);
	buf_printf(&t, "\n%s", m->body);
	buf_adds(&t, "────────────────────────────────────────\n");
	for (size_t i = 0; i < t.n; i++) {
		if (t.s[i] == '\n')
			buf_addc(out, '\r');
		buf_addc(out, t.s[i]);
	}
	buf_free(&t);
	buf_free(&h);
}

void cmd_send(int argc, char **argv)
{
	const char *to = NULL, *title_text = "", *file = NULL;
	long long expiry = 0, id;
	buf_t txt = {0}, clean = {0}, tit = {0}, msgtxt = {0}, out = {0};
	strv_t dest = {0};
	msg_t m = {0};
	char *dir, *users;
	int lock, i, failed = 0;
	strv_t non = {0};

	for (i = 0; i < argc; i++) {
		const char *a = argv[i];

		if (!strcmp(a, "--to") || !strcmp(a, "--title") || !strcmp(a, "--expires") || !strcmp(a, "--file")) {
			if (i + 1 >= argc || !*argv[i + 1])
				die("missing value for %s", a);
			if (!strcmp(a, "--to"))
				to = argv[++i];
			else if (!strcmp(a, "--title"))
				title_text = argv[++i];
			else if (!strcmp(a, "--file"))
				file = argv[++i];
			else {
				expiry = expiry_from(argv[++i]);
				if (expiry <= (long long)now())
					die("%s", "the expiry is already in the past");
			}
		} else if (!strcmp(a, "--")) {
			i++;
			break;
		} else if (a[0] == '-' && a[1]) {
			die("unknown option: %s", a);
		} else {
			break;
		}
	}
	if (!to)
		die("%s", "missing --to");
	if (i < argc) {
		for (int k = i; k < argc; k++) {
			if (k > i)
				buf_addc(&txt, ' ');
			buf_adds(&txt, argv[k]);
		}
	} else if (file) {
		if (read_file(file, (size_t)1 << 26, false, &txt) < 0)
			die("%s: %s", file, strerror(errno));
	} else {
		read_fd(0, (size_t)1 << 26, &txt);
	}
	/* as in the prototype: no trailing newlines, then one */
	while (txt.n && txt.s[txt.n - 1] == '\n')
		txt.s[--txt.n] = '\0';
	clean_text(txt.s ? txt.s : "", txt.n, &clean);
	clean_text(title_text, strlen(title_text), &tit);
	for (size_t k = 0; k < tit.n; k++)
		if (tit.s[k] == '\n' || tit.s[k] == '\t')
			tit.s[k] = ' ';
	{
		bool empty = true;

		for (size_t k = 0; k < clean.n; k++)
			if (!strchr(" \t\n\v\f\r", clean.s[k]))
				empty = false;
		if (empty)
			die("%s", "empty message");
	}
	if (clean.n > RSPEAK_MAX_BYTES)
		die("message too long: %zu bytes (at most %d)", clean.n, RSPEAK_MAX_BYTES);

	resolve_recipients(to, &dest);
	if (!dest.n)
		die("%s", "no recipients");

	prepare_store();
	id = next_id();
	dir = msg_dir(id);
	/* The lock tells recovery, revocation and deletion «send in progress» for
	 * the whole delivery; if rspeak dies, even with SIGKILL, the kernel releases it. */
	if ((lock = take_lock(id, false)) < 0)
		die("%s: %s", dir, strerror(errno));
	/* The mark stays until all the copies are delivered and on disk. */
	set_mark(id, "incomplete");
	m.id = id;
	m.from = xstrdup(author());
	m.date = (long long)now();
	m.title = xstrdup(tit.s ? tit.s : "");
	m.expires = expiry;
	m.body = xasprintf("%s\n", clean.s ? clean.s : "");
	msg_format(&m, &msgtxt);
	terminal_text(&m, &out);
	{
		char *mp = in_msg_dir(id, "msg"), *rp = in_msg_dir(id, "recipients"), *ip = in_msg_dir(id, "incomplete");
		buf_t r = {0};

		for (size_t k = 0; k < dest.n; k++)
			buf_printf(&r, "%s\n", dest.v[k]);
		/* message, recipients and mark on disk before any delivery */
		if (write_atomic(mp, msgtxt.s, msgtxt.n, 0600) < 0 || write_atomic(rp, r.s, r.n, 0600) < 0)
			die("%s: %s", dir, strerror(errno));
		sync_path(ip);
		sync_path(dir);
		{
			char *sd = sent_dir();

			sync_path(sd);
			free(sd);
		}
		buf_free(&r);
		free(mp);
		free(rp);
		free(ip);
	}

	for (size_t k = 0; k < dest.n; k++) {
		user_t u;
		strv_t term = {0};
		int nterm = 0;
		char det[16];

		/* revoked during the send (rspeak revoke waits for the lock): deliver nothing more */
		if (mark(id, "revoked"))
			break;
		if (!user_find(dest.v[k], &u) || !deliver_copy(&u, id, &msgtxt)) {
			strv_add(&non, dest.v[k]);
			failed++;
			event("NOT_DELIVERED", id, dest.v[k], "", "", "");
			user_free(&u);
			continue;
		}
		user_terminals(u.uid, &term);
		for (size_t t = 0; t < term.n; t++)
			if (write_terminal(term.v[t], u.uid, out.s, out.n))
				nterm++;
		strv_free(&term);
		wake_agent(&u);
		record_delivery(id, u.name, nterm);
		snprintf(det, sizeof det, "%d", nterm);
		event("DELIVERED", id, u.name, "", det, "");
		user_free(&u);
	}
	{
		buf_t list = {0};

		for (size_t k = 0; k < dest.n; k++)
			buf_printf(&list, "%s%s", k ? " " : "", dest.v[k]);
		event("SENT", id, "", "", list.s, author());
		buf_free(&list);
	}
	if (failed) {
		buf_t l = {0};

		for (size_t k = 0; k < non.n; k++)
			buf_printf(&l, " %s", non.v[k]);
		printf("Message %lld delivered to %zu of %zu recipients.", id, dest.n - (size_t)failed, dest.n);
		putchar('\n');
		die("message %lld not delivered to:%s (see the log; the next rspeak command will retry)", id, l.s);
	}
	/* copies and deliveries on disk before removing the mark: while it is there,
	 * recovery checks every copy again */
	users = xasprintf("%s/users", rspeak_var);
	syncfs_path(users);
	sync_path(dir);
	clear_mark(id, "incomplete");
	sync_path(dir);
	if (mark(id, "revoked"))
		printf("Message %lld revoked while sending: delivery stopped.", id);
	else if (dest.n == 1)
		printf("Message %lld sent to 1 user.", id);
	else
		printf("Message %lld sent to %zu users.", id, dest.n);
	putchar('\n');
	close(lock);
	free(users);
	free(dir);
	msg_free(&m);
	buf_free(&txt);
	buf_free(&clean);
	buf_free(&tit);
	buf_free(&msgtxt);
	buf_free(&out);
	strv_free(&dest);
	strv_free(&non);
}

/* ---- state of the recipients (list, status) ---- */

/* The mailboxes are read once per user and stay in memory. */
static struct {
	char *name;
	mailbox_t c;
} *mailboxes;
static size_t n_mailboxes;
static strv_t all_ids;
static bool all_ids_read;

static const mailbox_t *user_mailbox(const char *name)
{
	user_t u;

	for (size_t i = 0; i < n_mailboxes; i++)
		if (!strcmp(mailboxes[i].name, name))
			return &mailboxes[i].c;
	if (!all_ids_read) {
		char *sd = sent_dir();

		list_numbers(sd, &all_ids);
		all_ids_read = true;
		free(sd);
	}
	mailboxes = xrealloc(mailboxes, (n_mailboxes + 1) * sizeof *mailboxes);
	mailboxes[n_mailboxes].name = xstrdup(name);
	memset(&mailboxes[n_mailboxes].c, 0, sizeof mailboxes[n_mailboxes].c);
	if (user_find(name, &u)) {
		read_mailbox(&u, &all_ids, &mailboxes[n_mailboxes].c);
		user_free(&u);
	}
	return &mailboxes[n_mailboxes++].c;
}

void mailboxes_empty(void)
{
	for (size_t i = 0; i < n_mailboxes; i++) {
		free(mailboxes[i].name);
		mailbox_free(&mailboxes[i].c);
	}
	free(mailboxes);
	mailboxes = NULL;
	n_mailboxes = 0;
	strv_free(&all_ids);
	all_ids_read = false;
}

typedef struct {
	state_e state;
	bool late;     /* confirmation after expiry */
	long long when; /* date of the confirmation */
	char *channel;
} state_t;

/* State of a recipient. The expiry and the revocation that count are those of
 * the reference copy (sent/): a confirmation dated after them does not count. */
static void recipient_state(const char *u, long long id, const deliveries_t *cons, const msg_t *m, long long revocation,
			       state_t *s)
{
	const mailbox_item_t *v;
	long long when = 0;
	char *sp;

	memset(s, 0, sizeof *s);
	if (!delivered_to(cons, u)) {
		s->state = SENT;
		return;
	}
	s->state = DELIVERED;
	v = mailbox_item(user_mailbox(u), id);
	if (!v || !v->confirm)
		return;
	{
		char *copy = xstrdup(v->confirm);

		sp = strchr(copy, ' ');
		if (sp)
			*sp = '\0';
		if (!read_number(copy, &when))
			when = 0;
		free(copy);
	}
	if (m->expires && when > m->expires) {
		s->late = true;
		return;
	}
	if (revocation && when > revocation)
		return;
	s->state = CONFIRMED;
	s->when = when;
	sp = strchr(v->confirm, ' ');
	s->channel = xstrdup(sp && sp[1] ? sp + 1 : "?");
}

long long revocation_date(long long id)
{
	char *p = in_msg_dir(id, "revoked");
	buf_t b = {0};
	long long r = 0;

	if (read_file(p, 64, true, &b) == 0 && b.s) {
		b.s[strcspn(b.s, "\n")] = '\0';
		if (!read_number(b.s, &r))
			r = 0;
	}
	buf_free(&b);
	free(p);
	return r;
}

void message_list(strv_t *ids)
{
	char *sd = sent_dir();

	list_numbers(sd, ids);
	free(sd);
}

/* Everything needed is read first: a message deleted in the meantime by
 * rspeak purge disappears instead of being shown half. */
bool summarise(long long id, summary_t *r)
{
	char *p;
	strv_t dest = {0};
	deliveries_t cons;
	long long revocation;

	memset(r, 0, sizeof *r);
	r->id = id;
	if (mark(id, "failed"))
		return false;
	p = in_msg_dir(id, "msg");
	if (msg_read(p, &r->m) < 0) {
		free(p);
		return false;
	}
	free(p);
	read_recipients(id, &dest);
	if (!dest.n) {
		msg_free(&r->m);
		return false;
	}
	read_deliveries(id, &cons);
	revocation = revocation_date(id);
	for (size_t k = 0; k < dest.n; k++) {
		state_t st;

		recipient_state(dest.v[k], id, &cons, &r->m, revocation, &st);
		if (st.state == CONFIRMED)
			r->confirmed++;
		else if (st.state == DELIVERED)
			r->delivered++;
		else
			r->sent++;
		free(st.channel);
	}
	r->revoked = mark(id, "revoked");
	r->expired = msg_expired(&r->m, now());
	deliveries_free(&cons);
	strv_free(&dest);
	return true;
}

void summary_free(summary_t *r)
{
	msg_free(&r->m);
}

void summary_text(const summary_t *r, buf_t *out)
{
	const char *sep = "";

	if (!r->delivered && !r->sent) {
		buf_printf(out, "all confirmed (%d)", r->confirmed);
		return;
	}
	if (r->confirmed) {
		buf_printf(out, "%d confirmed", r->confirmed);
		sep = " · ";
	}
	if (r->delivered) {
		buf_adds(out, sep);
		buf_printf(out, "%d delivered", r->delivered);
		sep = " · ";
	}
	if (r->sent) {
		buf_adds(out, sep);
		buf_printf(out, "%d sent", r->sent);
	}
}

/* One message per line: the text (preceded by revoked and expired) and the
 * recipients in the three states (chapter «Specification»). */
/* Writes s in w characters (UTF-8), truncating or padding on the right. */
static void column(const char *s, size_t n, int w)
{
	size_t c = 0, k = 0;

	while (k < n && (int)c < w) {
		k++;
		while (k < n && ((unsigned char)s[k] & 0xc0) == 0x80)
			k++;
		c++;
	}
	printf("%.*s%*s", (int)k, s, (int)(w - (int)c), "");
}

static void cmd_list(void)
{
	char *sd = sent_dir();
	strv_t ids = {0};

	if (!is_folder(sd)) {
		puts("No messages sent.");
		free(sd);
		return;
	}
	free(sd);
	message_list(&ids);
	if (!ids.n) {
		puts("No messages sent.");
		strv_free(&ids);
		return;
	}
	printf("%-5s %-12s ", "ID", "DATE");
	column("TEXT", strlen("TEXT"), 40);
	printf("  %s\n", "RECIPIENTS");
	for (size_t i = 0; i < ids.n; i++) {
		long long id;
		summary_t r;
		char data[32];
		buf_t txt = {0}, summary_line = {0};

		read_number(ids.v[i], &id);
		if (mark(id, "failed")) {
			printf("%-5s %-12s %s\n", ids.v[i], "-", "[send cancelled: interrupted before it was saved]");
			continue;
		}
		if (!summarise(id, &r))
			continue;
		if (r.revoked)
			buf_adds(&txt, "[revoked] ");
		if (r.expired)
			buf_adds(&txt, "[expired] ");
		buf_add(&txt, r.m.body, strcspn(r.m.body, "\n"));
		summary_text(&r, &summary_line);
		short_date((time_t)r.m.date, data);
		printf("%-5s %-12s ", ids.v[i], data);
		column(txt.s, txt.n, 40);
		printf("  %s\n", summary_line.s);
		buf_free(&txt);
		buf_free(&summary_line);
		summary_free(&r);
	}
	strv_free(&ids);
}

static long long id_from(const char *s)
{
	long long id;

	if (!s || !*s)
		die("%s", "missing message ID");
	if (!read_number(s, &id))
		die("no such message: %s", s);
	return id;
}

static void load_msg(long long id, const char *arg, msg_t *m)
{
	char *p = in_msg_dir(id, "msg");

	if (msg_read(p, m) < 0)
		die("no such message: %s", arg);
	free(p);
}

/* The status line of each recipient, as in rspeak status. */
void recipients(long long id, const msg_t *m, recipients_t *out)
{
	strv_t dest = {0};
	deliveries_t cons;
	long long revocation = revocation_date(id);
	bool revoked = mark(id, "revoked"), incomplete = mark(id, "incomplete");
	char data[32];

	memset(out, 0, sizeof *out);
	read_recipients(id, &dest);
	read_deliveries(id, &cons);
	out->v = xmalloc((dest.n ? dest.n : 1) * sizeof *out->v);
	for (size_t k = 0; k < dest.n; k++) {
		state_t s;
		buf_t line = {0};

		recipient_state(dest.v[k], id, &cons, m, revocation, &s);
		if (s.state == CONFIRMED) {
			buf_t ch = {0};

			channel_text(s.channel, &ch);
			short_date((time_t)s.when, data);
			buf_printf(&line, "confirmed on %s (%s)", data, ch.s ? ch.s : "");
			buf_free(&ch);
		} else if (s.state == SENT) {
			buf_adds(&line, incomplete ? "sent, not delivered: the copy could not be written (see the log; the next rspeak command will retry)"
						   : "sent, not delivered");
		} else {
			buf_adds(&line, "delivered");
			if (revoked)
				buf_adds(&line, ", not confirmed (revoked)");
			else if (s.late)
				buf_adds(&line, ", not confirmed (expired; confirmation arrived after the expiry)");
			else if (msg_expired(m, now()))
				buf_adds(&line, ", not confirmed (expired)");
			else {
				const char *nt = delivered_to(&cons, dest.v[k]);
				const mailbox_item_t *v = mailbox_item(user_mailbox(dest.v[k]), id);
				long long n = 0;

				if (nt && read_number(nt, &n) && n == 1)
					buf_adds(&line, ", written to 1 terminal");
				else if (n > 1)
					buf_printf(&line, ", written to %lld terminals", n);
				if (v && v->postponement) {
					short_date((time_t)v->postponement, data);
					buf_printf(&line, ", postponed on %s", data);
				}
			}
		}
		out->v[out->n].user = xstrdup(dest.v[k]);
		out->v[out->n].state = s.state;
		out->v[out->n++].line = line.s ? line.s : xstrdup("");
		free(s.channel);
	}
	deliveries_free(&cons);
	strv_free(&dest);
}

void recipients_free(recipients_t *d)
{
	for (size_t i = 0; i < d->n; i++) {
		free(d->v[i].user);
		free(d->v[i].line);
	}
	free(d->v);
	memset(d, 0, sizeof *d);
}

static void cmd_status(const char *arg)
{
	long long id = id_from(arg), revocation;
	msg_t m;
	recipients_t d;
	buf_t h = {0};
	char data[32];

	load_msg(id, arg, &m);
	if (mark(id, "failed"))
		die("message %lld was cancelled: sending was interrupted before it was saved", id);
	msg_header(&m, &h);
	printf("Message %lld · %s · from %s", id, h.s, m.from);
	putchar('\n');
	revocation = revocation_date(id);
	if (mark(id, "revoked")) {
		short_date((time_t)revocation, data);
		printf("REVOKED on %s", data);
		putchar('\n');
	}
	if (msg_expired(&m, now()))
		puts("EXPIRED");
	for (char *p = m.body; *p;) {
		size_t len = strcspn(p, "\n");

		printf("  │ %.*s\n", (int)len, p);
		p += len;
		if (*p)
			p++;
	}
	putchar('\n');
	printf("%-16s %s\n", "USER", "STATE");
	recipients(id, &m, &d);
	for (size_t k = 0; k < d.n; k++)
		printf("%-16s %s\n", d.v[k].user, d.v[k].line);
	recipients_free(&d);
	msg_free(&m);
	buf_free(&h);
}

/* ---- revocation ---- */

/* The revocation happens when sent/ID/revoked appears (on disk): from then on
 * no new delivery and no later confirmation counts. Then any send in progress
 * is waited for (lock), which stops at the next recipient, and the copies are
 * removed; sent/ID/revoking stays until they are all removed. */
void cmd_revoke(const char *arg)
{
	long long id = id_from(arg);
	msg_t m;
	char *dir = msg_dir(id), *rev = in_msg_dir(id, "revoked"), *revoking = in_msg_dir(id, "revoking");
	int lock;

	load_msg(id, arg, &m);
	set_mark(id, "revoking");
	if (!exists(rev)) {
		char data[32];
		int n = snprintf(data, sizeof data, "%lld\n", (long long)now());

		if (write_atomic(rev, data, (size_t)n, 0600) < 0)
			die("%s: %s", rev, strerror(errno));
		sync_path(revoking);
		sync_path(dir);
		event("REVOKED", id, "", "", "", author());
	}
	if ((lock = take_lock(id, false)) < 0)
		die("%s: %s", dir, strerror(errno));
	if (!remove_copies_all(id))
		die("message %lld revoked, but some copies could not be removed from the mailboxes: the next rspeak command will retry",
		    id);
	printf("Message %lld revoked.", id);
	putchar('\n');
	close(lock);
	msg_free(&m);
	free(dir);
	free(rev);
	free(revoking);
}

/* ---- reminder ---- */

/* Whoever has not confirmed is reminded at once: their postponements are removed
 * (the question comes back at the next prompt, the dialog at the next round) and
 * their desktop agent is woken up. */
void cmd_remind(const char *arg)
{
	long long id = id_from(arg);
	msg_t m;
	recipients_t d;
	int n = 0, confirmed_n = 0;
	size_t tot;
	char det[24];

	load_msg(id, arg, &m);
	if (mark(id, "revoked"))
		die("message %lld has been revoked: nobody to remind", id);
	if (msg_expired(&m, now()))
		die("message %lld has expired: nobody to remind", id);
	recipients(id, &m, &d);
	tot = d.n;
	for (size_t k = 0; k < d.n; k++) {
		user_t u;

		confirmed_n += d.v[k].state == CONFIRMED;
		if (d.v[k].state != DELIVERED || !user_find(d.v[k].user, &u))
			continue;
		if (clear_postponements(&u, id)) {
			wake_agent(&u);
			n++;
		}
		user_free(&u);
	}
	recipients_free(&d);
	snprintf(det, sizeof det, "%d", n);
	event("REMINDED", id, "", "", det, author());
	if (n == 0 && tot > 0 && (size_t)confirmed_n == tot)
		printf("Message %lld: everyone has already confirmed, nobody to remind.", id);
	else if (n == 1)
		printf("Message %lld: 1 recipient reminded.", id);
	else
		printf("Message %lld: %d recipients reminded.", id, n);
	putchar('\n');
	msg_free(&m);
}

void cmd_count_recipients(const char *to)
{
	strv_t dest = {0};

	resolve_recipients(to, &dest);
	printf("%zu\n", dest.n);
	strv_free(&dest);
}

/* ---- deletion ---- */

void cmd_purge(const char *dur)
{
	long long n, sec, limit;
	char *sd = sent_dir();
	strv_t ids = {0};
	int removed = 0;
	size_t l;

	if (!dur || !*dur)
		die("%s", "missing duration, for example 90d");
	l = strlen(dur);
	{
		char *num = xstrdup(dur);

		num[l - 1] = '\0';
		if (l < 2 || !strchr("mhd", dur[l - 1]) || !read_number(num, &n))
			die("invalid duration: %s (for example 90d, 12h, 30m)", dur);
		free(num);
	}
	sec = n * (dur[l - 1] == 'm' ? 60 : dur[l - 1] == 'h' ? 3600 : 86400);
	limit = (long long)now() - sec;
	list_numbers(sd, &ids);
	for (size_t i = 0; i < ids.n; i++) {
		long long id, when = 0;
		msg_t m;
		char *p, *new_item;
		int lock;

		read_number(ids.v[i], &id);
		if (mark(id, "incomplete"))
			continue;
		p = in_msg_dir(id, "msg");
		if (msg_read(p, &m) == 0) {
			when = m.date;
			msg_free(&m);
		} else {
			struct stat st;
			char *d = msg_dir(id);

			if (stat(d, &st) == 0)
				when = st.st_mtime;
			free(d);
		}
		free(p);
		if (when >= limit)
			continue;
		if ((lock = take_lock(id, true)) < 0)
			continue;
		/* The message disappears in one go (rename): the other commands
		 * see it whole or not at all. The purge of the mailboxes follows, and
		 * if it is interrupted the next rspeak command completes it. */
		p = msg_dir(id);
		new_item = xasprintf("%s/.deleting-%lld", sd, id);
		if (rename(p, new_item) == 0) {
			sync_path(sd);
			close(lock);
			event("DELETED", id, "", "", dur, author());
			remove_folder(new_item, id);
			removed++;
		} else {
			close(lock);
		}
		free(p);
		free(new_item);
	}
	if (removed == 0)
		printf("No messages older than %s.", dur);
	else if (removed == 1)
		printf("Deleted 1 message older than %s.", dur);
	else
		printf("Deleted %d messages older than %s.", removed, dur);
	putchar('\n');
	strv_free(&ids);
	free(sd);
}

/* ---- history from the journal ---- */

static char *field(sd_journal *j, const char *name)
{
	const void *d;
	size_t l, k = strlen(name);

	if (sd_journal_get_data(j, name, &d, &l) < 0 || l <= k)
		return xstrdup("");
	{
		char *s = xmalloc(l - k);

		memcpy(s, (const char *)d + k + 1, l - k - 1);
		s[l - k - 1] = '\0';
		return s;
	}
}

/* The events with RSPEAK_MESSAGE=ID from the date of the send (a reset message store
 * reuses the numbers, the journal does not), rewritten from the RSPEAK_* fields. Anyone can
 * write an event with those fields to the journal: the journal records _UID, who really
 * wrote it, and an event written by the wrong user is flagged. */
void cmd_log(const char *arg)
{
	long long id = id_from(arg);
	msg_t m;
	sd_journal *j;
	buf_t h = {0};
	char match[64];
	uid_t root_admin = rspeak_test ? getuid() : 0;

	load_msg(id, arg, &m);
	msg_header(&m, &h);
	printf("Message %lld · %s", id, h.s);
	putchar('\n');
	fflush(stdout);
	if (sd_journal_open(&j, 0) < 0)
		return;
	snprintf(match, sizeof match, "RSPEAK_MESSAGE=%lld", id);
	sd_journal_add_match(j, "SYSLOG_IDENTIFIER=rspeak", 0);
	sd_journal_add_match(j, match, 0);
	sd_journal_seek_realtime_usec(j, (uint64_t)(m.date > 0 ? m.date - 1 : 0) * 1000000u);
	while (sd_journal_next(j) > 0) {
		uint64_t usec;
		char *ev = field(j, "RSPEAK_EVENT"), *u = field(j, "RSPEAK_USER"), *ch = field(j, "RSPEAK_CHANNEL"),
		     *det = field(j, "RSPEAK_DETAILS"), *author_s = field(j, "RSPEAK_AUTHOR"), *msg = field(j, "MESSAGE"),
		     *uid = field(j, "_UID");
		buf_t line = {0}, cleaned = {0};
		long long expected = root_admin, written_one = -1;
		char data[32];
		time_t t;
		struct tm tm;

		if (sd_journal_get_realtime_usec(j, &usec) < 0)
			usec = 0;
		t = (time_t)(usec / 1000000u);
		if (!localtime_r(&t, &tm) || !strftime(data, sizeof data, "%Y-%m-%d %H:%M:%S", &tm))
			snprintf(data, sizeof data, "?");
		if (!strcmp(ev, "POSTPONED") || !strcmp(ev, "CONFIRMED") || !strcmp(ev, "CONFIRMATION_FAILED")) {
			struct passwd *pw = getpwnam(u);

			expected = pw ? (long long)pw->pw_uid : -2;
		}
		buf_printf(&line, "%s  ", data);
		if (!read_number(uid, &written_one) || written_one != expected)
			buf_printf(&line, "[not trustworthy: written by UID %s] ", *uid ? uid : "?");
		if (!event_text(ev, id, u, ch, det, author_s, &line))
			buf_adds(&line, msg);
		clean_text(line.s, line.n, &cleaned);
		printf("%s\n", cleaned.s ? cleaned.s : "");
		buf_free(&line);
		buf_free(&cleaned);
		free(ev);
		free(u);
		free(ch);
		free(det);
		free(author_s);
		free(msg);
		free(uid);
	}
	sd_journal_close(j);
	msg_free(&m);
	buf_free(&h);
}

/* ---- startup ---- */

static void rerun_with_sudo(char **argv)
{
	char self[PATH_MAX];
	ssize_t n = readlink("/proc/self/exe", self, sizeof self - 1);
	int argc = 0;
	char **new_items;

	if (n <= 0)
		die("/proc/self/exe: %s", strerror(errno));
	self[n] = '\0';
	while (argv[argc])
		argc++;
	new_items = xmalloc(((size_t)argc + 3) * sizeof *new_items);
	static char sudo[] = "sudo", end_of_options[] = "--";

	new_items[0] = sudo;
	new_items[1] = end_of_options;
	new_items[2] = self;
	for (int i = 1; i <= argc; i++)
		new_items[i + 2] = argv[i];
	execvp("sudo", new_items);
	die("sudo: %s", strerror(errno));
}

int main(int argc, char **argv)
{
	const char *cmd = argc > 1 ? argv[1] : "";

	rspeak_init("rspeak");
	/* As a non-root administrator, rspeak re-runs itself with sudo, even for
	 * the help and the version. */
	if (geteuid() != 0 && !rspeak_test)
		rerun_with_sudo(argv);
	umask(022);

	/* rspeak alone in a terminal opens the TUI; in a pipe, or with a
	 * terminal too small, the help */
	if (!*cmd && isatty(0) && isatty(1)) {
		recover();
		if (rspeak_tui())
			return 0;
	}
	if (!*cmd || !strcmp(cmd, "help") || !strcmp(cmd, "-h") || !strcmp(cmd, "--help")) {
		rspeak_help();
		return 0;
	}
	if (!strcmp(cmd, "version") || !strcmp(cmd, "--version")) {
		printf("RootSpeak - Advanced Messaging System for Linux %s\n", RSPEAK_VERSION);
		return 0;
	}
	if (strcmp(cmd, "send") && strcmp(cmd, "list") && strcmp(cmd, "status") && strcmp(cmd, "revoke") &&
	    strcmp(cmd, "remind") && strcmp(cmd, "log") && strcmp(cmd, "purge"))
		die("unknown command: %s (rspeak --help for the guide)", cmd);
	/* an extra argument is a typing error to report, not something to ignore
	 * (rspeak remind 3 4 does not remind message 4) */
	if (strcmp(cmd, "send")) {
		int want = !strcmp(cmd, "list") ? 0 : 1;

		if (argc - 2 > want)
			die("too many arguments for %s: %s (rspeak --help for the guide)", cmd, argv[2 + want]);
	}
	if (strcmp(cmd, "purge"))
		recover();
	if (!strcmp(cmd, "send"))
		cmd_send(argc - 2, argv + 2);
	else if (!strcmp(cmd, "list"))
		cmd_list();
	else if (!strcmp(cmd, "status"))
		cmd_status(argv[2]);
	else if (!strcmp(cmd, "revoke"))
		cmd_revoke(argv[2]);
	else if (!strcmp(cmd, "remind"))
		cmd_remind(argv[2]);
	else if (!strcmp(cmd, "log"))
		cmd_log(argv[2]);
	else
		cmd_purge(argv[2]);
	return 0;
}
