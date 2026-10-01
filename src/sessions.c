/* RootSpeak - Advanced Messaging System for Linux
 * Recipients and sessions, from passwd, group and logind. */
#include "sessions.h"

#include <dirent.h>
#include <grp.h>
#include <pwd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <systemd/sd-login.h>

static long login_defs(const char *key, long default_value)
{
	buf_t b = {0};
	long v = default_value;

	if (read_file("/etc/login.defs", 1 << 20, false, &b) == 0) {
		for (char *p = b.s; p && *p;) {
			size_t len = strcspn(p, "\n");
			char k[64];
			long x;

			if (sscanf(p, "%63s %ld", k, &x) == 2 && !strcmp(k, key))
				v = x;
			p += len;
			if (*p)
				p++;
		}
	}
	buf_free(&b);
	return v;
}

static bool real_shell(const char *sh)
{
	size_t n = strlen(sh);

	return !((n >= 7 && !strcmp(sh + n - 7, "nologin")) || (n >= 5 && !strcmp(sh + n - 5, "false")));
}

void human_users(strv_t *out)
{
	long min = login_defs("UID_MIN", 1000), max = login_defs("UID_MAX", 60000);
	struct passwd *pw;

	setpwent();
	while ((pw = getpwent()))
		if ((long)pw->pw_uid >= min && (long)pw->pw_uid <= max && real_shell(pw->pw_shell ? pw->pw_shell : "") &&
		    !strv_has(out, pw->pw_name))
			strv_add(out, pw->pw_name);
	endpwent();
	strv_sort(out);
}

void online_users(strv_t *out)
{
	strv_t humans = {0};
	char **sessions = NULL;
	int n = sd_get_sessions(&sessions);

	human_users(&humans);
	for (int i = 0; i < n; i++) {
		char *classe = NULL;
		uid_t uid;
		struct passwd *pw;

		if (sd_session_get_class(sessions[i], &classe) >= 0 && !strcmp(classe, "user") &&
		    sd_session_get_uid(sessions[i], &uid) >= 0 && (pw = getpwuid(uid)) && strv_has(&humans, pw->pw_name) &&
		    !strv_has(out, pw->pw_name))
			strv_add(out, pw->pw_name);
		free(classe);
		free(sessions[i]);
	}
	free(sessions);
	strv_free(&humans);
	strv_sort(out);
}

bool group_members(const char *group_name, strv_t *out)
{
	struct group *gr = getgrnam(group_name);
	struct passwd *pw;
	gid_t gid;

	if (!gr)
		return false;
	gid = gr->gr_gid;
	for (char **m = gr->gr_mem; m && *m; m++)
		if (!strv_has(out, *m))
			strv_add(out, *m);
	setpwent();
	while ((pw = getpwent()))
		if (pw->pw_gid == gid && !strv_has(out, pw->pw_name))
			strv_add(out, pw->pw_name);
	endpwent();
	return true;
}

void user_terminals(uid_t uid, strv_t *out)
{
	const char *test_run = getenv("RSPEAK_TEST_TTY");
	char **sessions = NULL;
	DIR *d;
	int n;

	if (rspeak_test) {
		if (test_run && *test_run)
			strv_add(out, test_run);
		return;
	}
	if ((d = opendir("/dev/pts"))) {
		struct dirent *e;

		while ((e = readdir(d))) {
			char *p;
			struct stat st;

			if (!only_digits(e->d_name))
				continue;
			p = xasprintf("/dev/pts/%s", e->d_name);
			if (lstat(p, &st) == 0 && S_ISCHR(st.st_mode) && st.st_uid == uid)
				strv_add_own(out, p);
			else
				free(p);
		}
		closedir(d);
	}
	n = sd_get_sessions(&sessions);
	for (int i = 0; i < n; i++) {
		char *kind = NULL, *tty = NULL;
		uid_t su;

		if (sd_session_get_uid(sessions[i], &su) >= 0 && su == uid && sd_session_get_type(sessions[i], &kind) >= 0 &&
		    !strcmp(kind, "tty") && sd_session_get_tty(sessions[i], &tty) >= 0 && !strncmp(tty, "tty", 3) &&
		    only_digits(tty + 3)) {
			char *p = xasprintf("/dev/%s", tty);

			if (!strv_has(out, p))
				strv_add_own(out, p);
			else
				free(p);
		}
		free(kind);
		free(tty);
		free(sessions[i]);
	}
	free(sessions);
	strv_sort(out);
}

bool graphical_session(uid_t uid)
{
	char **sessions = NULL;
	int n = sd_get_sessions(&sessions);
	bool found_f = false;

	for (int i = 0; i < n; i++) {
		char *kind = NULL;
		uid_t su;

		if (!found_f && sd_session_get_uid(sessions[i], &su) >= 0 && su == uid &&
		    sd_session_get_type(sessions[i], &kind) >= 0 && (!strcmp(kind, "x11") || !strcmp(kind, "wayland")))
			found_f = true;
		free(kind);
		free(sessions[i]);
	}
	free(sessions);
	return found_f;
}
