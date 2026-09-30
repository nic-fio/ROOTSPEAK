/* AMS - Advanced Messaging System
 * Destinatari e sessioni, da passwd, group e logind. */
#include "sessioni.h"

#include <dirent.h>
#include <grp.h>
#include <pwd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <systemd/sd-login.h>

static long login_defs(const char *chiave, long predefinito)
{
	buf_t b = {0};
	long v = predefinito;

	if (leggi_file("/etc/login.defs", 1 << 20, false, &b) == 0) {
		for (char *p = b.s; p && *p;) {
			size_t len = strcspn(p, "\n");
			char k[64];
			long x;

			if (sscanf(p, "%63s %ld", k, &x) == 2 && !strcmp(k, chiave))
				v = x;
			p += len;
			if (*p)
				p++;
		}
	}
	buf_free(&b);
	return v;
}

static bool shell_vera(const char *sh)
{
	size_t n = strlen(sh);

	return !((n >= 7 && !strcmp(sh + n - 7, "nologin")) || (n >= 5 && !strcmp(sh + n - 5, "false")));
}

void utenti_umani(strv_t *out)
{
	long min = login_defs("UID_MIN", 1000), max = login_defs("UID_MAX", 60000);
	struct passwd *pw;

	setpwent();
	while ((pw = getpwent()))
		if ((long)pw->pw_uid >= min && (long)pw->pw_uid <= max && shell_vera(pw->pw_shell ? pw->pw_shell : "") &&
		    !strv_has(out, pw->pw_name))
			strv_add(out, pw->pw_name);
	endpwent();
	strv_sort(out);
}

void utenti_online(strv_t *out)
{
	strv_t umani = {0};
	char **sessioni = NULL;
	int n = sd_get_sessions(&sessioni);

	utenti_umani(&umani);
	for (int i = 0; i < n; i++) {
		char *classe = NULL;
		uid_t uid;
		struct passwd *pw;

		if (sd_session_get_class(sessioni[i], &classe) >= 0 && !strcmp(classe, "user") &&
		    sd_session_get_uid(sessioni[i], &uid) >= 0 && (pw = getpwuid(uid)) && strv_has(&umani, pw->pw_name) &&
		    !strv_has(out, pw->pw_name))
			strv_add(out, pw->pw_name);
		free(classe);
		free(sessioni[i]);
	}
	free(sessioni);
	strv_free(&umani);
	strv_sort(out);
}

bool membri_gruppo(const char *gruppo, strv_t *out)
{
	struct group *gr = getgrnam(gruppo);
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

void terminali_utente(uid_t uid, strv_t *out)
{
	const char *prova = getenv("AMS_TEST_TTY");
	char **sessioni = NULL;
	DIR *d;
	int n;

	if (ams_test) {
		if (prova && *prova)
			strv_add(out, prova);
		return;
	}
	if ((d = opendir("/dev/pts"))) {
		struct dirent *e;

		while ((e = readdir(d))) {
			char *p;
			struct stat st;

			if (!solo_cifre(e->d_name))
				continue;
			p = xasprintf("/dev/pts/%s", e->d_name);
			if (lstat(p, &st) == 0 && S_ISCHR(st.st_mode) && st.st_uid == uid)
				strv_add_own(out, p);
			else
				free(p);
		}
		closedir(d);
	}
	n = sd_get_sessions(&sessioni);
	for (int i = 0; i < n; i++) {
		char *tipo = NULL, *tty = NULL;
		uid_t su;

		if (sd_session_get_uid(sessioni[i], &su) >= 0 && su == uid && sd_session_get_type(sessioni[i], &tipo) >= 0 &&
		    !strcmp(tipo, "tty") && sd_session_get_tty(sessioni[i], &tty) >= 0 && !strncmp(tty, "tty", 3) &&
		    solo_cifre(tty + 3)) {
			char *p = xasprintf("/dev/%s", tty);

			if (!strv_has(out, p))
				strv_add_own(out, p);
			else
				free(p);
		}
		free(tipo);
		free(tty);
		free(sessioni[i]);
	}
	free(sessioni);
	strv_sort(out);
}

bool sessione_grafica(uid_t uid)
{
	char **sessioni = NULL;
	int n = sd_get_sessions(&sessioni);
	bool trovata = false;

	for (int i = 0; i < n; i++) {
		char *tipo = NULL;
		uid_t su;

		if (!trovata && sd_session_get_uid(sessioni[i], &su) >= 0 && su == uid &&
		    sd_session_get_type(sessioni[i], &tipo) >= 0 && (!strcmp(tipo, "x11") || !strcmp(tipo, "wayland")))
			trovata = true;
		free(tipo);
		free(sessioni[i]);
	}
	free(sessioni);
	return trovata;
}
