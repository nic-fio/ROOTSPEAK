/* AMS - Advanced Messaging System for linux
 * Caselle degli utenti (sempre con la loro identità), terminali, agente. */
#include "archivio.h"

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

#include "lingua.h"
#include "sessioni.h"
#include "testo.h"

/* ---- operazioni eseguite come l'utente (nel processo figlio) ---- */

typedef struct {
	const char *casella; /* users/U */
	long long id;
} op_t;

static char *in_casella(const op_t *o, const char *sotto, const char *suffisso)
{
	return xasprintf("%s/%s/%lld%s", o->casella, sotto, o->id, suffisso);
}

/* stdin: il messaggio. Esito 0 se la copia c'è, 1 altrimenti. */
static int op_consegna(void *arg)
{
	const op_t *o = arg;
	static const char *sotto[] = {"inbox", "read", "acks", "state"};
	char *letto, *confermato, *copia, *tmp;
	buf_t b = {0};
	struct stat st;
	int fd, r = 1;

	for (int i = 0; i < 4; i++) {
		char *d = xasprintf("%s/%s", o->casella, sotto[i]);

		if (mkdir(d, 0755) < 0 && errno != EEXIST)
			return 1;
		free(d);
	}
	letto = in_casella(o, "read", "");
	confermato = in_casella(o, "acks", "");
	if (esiste(letto) || esiste(confermato))
		return 0;
	if (leggi_fd(0, AMS_MAX_MSG, &b) < 0 || !b.n)
		return 1;
	copia = in_casella(o, "inbox", "");
	tmp = in_casella(o, "inbox", ".tmp");
	unlink(tmp);
	fd = open(tmp, O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC | O_NOFOLLOW, 0644);
	if (fd >= 0) {
		if (scrivi_tutto(fd, b.s, b.n) == 0 && close(fd) == 0 && rename(tmp, copia) == 0)
			r = 0;
		else
			unlink(tmp);
	}
	/* la copia c'è davvero, non vuota */
	if (r == 0 && (stat(copia, &st) < 0 || !S_ISREG(st.st_mode) || st.st_size == 0))
		r = 1;
	return r;
}

static int op_togli(void *arg)
{
	const op_t *o = arg;
	char *copia = in_casella(o, "inbox", ""), *t = in_casella(o, "state", ".term"),
	     *g = in_casella(o, "state", ".gui");

	unlink(copia);
	unlink(t);
	unlink(g);
	return esiste(copia) ? 1 : 0;
}

static int op_cancella(void *arg)
{
	const op_t *o = arg;
	static const char *f[][2] = {{"inbox", ""}, {"read", ""}, {"acks", ""}, {"state", ".term"}, {"state", ".gui"}};

	for (size_t i = 0; i < sizeof f / sizeof f[0]; i++) {
		char *p = in_casella(o, f[i][0], f[i][1]);

		unlink(p);
		free(p);
	}
	return 0;
}

/* Legge al più n byte dall'inizio di un file normale (non una pipe). */
static bool leggi_inizio(const char *path, size_t n, buf_t *out)
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

/* stdin: gli ID, uno per riga. stdout: «A ID prima-riga» e «S ID data». Si
 * cercano solo quegli ID: migliaia di file finti nella casella non contano. */
static int op_leggi(void *arg)
{
	const char *casella = arg;
	buf_t in = {0};

	if (chdir(casella) < 0)
		return 0;
	leggi_fd(0, (size_t)1 << 22, &in);
	for (char *p = in.s; p && *p;) {
		size_t len = strcspn(p, "\n");
		char id[24];

		if (len && len < sizeof id) {
			buf_t b = {0};
			char *f;
			struct stat st;
			long long piu = 0;

			memcpy(id, p, len);
			id[len] = '\0';
			if (!solo_cifre(id))
				goto avanti;
			f = xasprintf("acks/%s", id);
			if (leggi_inizio(f, 200, &b)) {
				size_t riga = b.s ? strcspn(b.s, "\n") : 0;

				printf("A %s %.*s\n", id, (int)riga, b.s ? b.s : "");
			}
			free(f);
			buf_free(&b);
			for (int k = 0; k < 2; k++) {
				f = xasprintf("state/%s.%s", id, k ? "gui" : "term");
				if (stat(f, &st) == 0 && S_ISREG(st.st_mode) && st.st_mtime > piu)
					piu = st.st_mtime;
				free(f);
			}
			if (piu)
				printf("S %s %lld\n", id, piu);
		}
avanti:
		p += len;
		if (*p)
			p++;
	}
	return 0;
}

static int op_environ(void *arg)
{
	buf_t b = {0};

	if (leggi_file(arg, 1 << 20, false, &b) < 0)
		return 1;
	scrivi_tutto(1, b.s, b.n);
	return 0;
}

typedef struct {
	uid_t uid;
} op_sveglia_t;

/* Manda SIGUSR1 all'agente pronto: il PID scritto in ams-agent.pronto, se è
 * davvero l'agente di AMS (riga di comando esatta). Esito 0 se svegliato. */
static int op_sveglia(void *arg)
{
	const op_sveglia_t *o = arg;
	char *pronto = xasprintf("/run/user/%u/ams-agent.pronto", (unsigned)o->uid), *cmd, *atteso;
	buf_t b = {0}, c = {0};
	long long pid;
	size_t la;
	bool ok;

	if (leggi_file(pronto, 64, true, &b) < 0 || !b.s)
		return 1;
	b.s[strcspn(b.s, "\n")] = '\0';
	if (!leggi_numero(b.s, &pid) || pid <= 1 || pid > 1 << 22)
		return 1;
	cmd = xasprintf("/proc/%lld/cmdline", pid);
	atteso = xasprintf("%s/ams-user", ams_libdir);
	la = strlen(atteso);
	ok = leggi_file(cmd, 4096, false, &c) == 0 && c.n == la + 1 + 6 && !memcmp(c.s, atteso, la + 1) &&
	     !memcmp(c.s + la + 1, "agent", 6);
	if (!ok)
		return 1;
	return kill((pid_t)pid, SIGUSR1) == 0 ? 0 : 1;
}

/* ---- dal lato di root ---- */

static char *casella_di(const utente_t *u)
{
	return xasprintf("%s/users/%s", ams_var, u->nome);
}

/* users/U: la crea root (700) e la dà all'utente. Se è rimasta di root (un
 * invio interrotto fra la creazione e il chown), la si sistema: in users/
 * scrive solo root, quindi è sua. */
static bool prepara_casella(const utente_t *u, const char *d)
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
	if (geteuid() == 0 && !ams_test && st.st_uid == 0 && lchown(d, u->uid, u->gid) < 0)
		return false;
	return true;
}

bool consegna_copia(const utente_t *u, long long id, const buf_t *msg)
{
	char *d = casella_di(u);
	op_t o = {d, id};
	bool ok = prepara_casella(u, d) && come_utente(u, op_consegna, &o, msg, NULL, 0, 20) == 0;

	free(d);
	return ok;
}

bool togli_copia(const utente_t *u, long long id)
{
	char *d = casella_di(u);
	op_t o = {d, id};
	bool ok = !e_cartella(d) || come_utente(u, op_togli, &o, NULL, NULL, 0, 20) == 0;

	free(d);
	return ok;
}

void cancella_copie(const utente_t *u, long long id)
{
	char *d = casella_di(u);
	op_t o = {d, id};

	if (e_cartella(d))
		come_utente(u, op_cancella, &o, NULL, NULL, 0, 20);
	free(d);
}

void leggi_casella(const utente_t *u, const strv_t *ids, casella_t *out)
{
	char *d = casella_di(u);
	buf_t in = {0}, raw = {0}, pulito = {0};

	memset(out, 0, sizeof *out);
	for (size_t i = 0; i < ids->n; i++)
		buf_printf(&in, "%s\n", ids->v[i]);
	if (!e_cartella(d) || !in.n || come_utente(u, op_leggi, d, &in, &raw, (size_t)1 << 22, 20) < 0)
		goto fine;
	casella_da_testo(raw.s ? raw.s : "", raw.n, out);
fine:
	buf_free(&in);
	buf_free(&raw);
	buf_free(&pulito);
	free(d);
}

void casella_da_testo(const char *raw, size_t n, casella_t *out)
{
	buf_t pulito = {0};

	memset(out, 0, sizeof *out);

	/* ciò che viene dalla casella è dato non fidato: ripulito */
	pulisci(raw, n, &pulito);
	for (char *p = pulito.s; p && *p;) {
		size_t len = strcspn(p, "\n");
		char tipo = p[0];
		char *riga = xmalloc(len + 1), *sp, *resto;
		long long id;

		memcpy(riga, p, len);
		riga[len] = '\0';
		p += len;
		if (*p)
			p++;
		if (len < 3 || riga[1] != ' ' || !(sp = strchr(riga + 2, ' '))) {
			free(riga);
			continue;
		}
		*sp = '\0';
		resto = sp + 1;
		if (!leggi_numero(riga + 2, &id)) {
			free(riga);
			continue;
		}
		{
			voce_casella_t *v = NULL;

			for (size_t k = 0; k < out->n && !v; k++)
				if (out->v[k].id == id)
					v = &out->v[k];

			if (!v) {
				out->v = xrealloc(out->v, (out->n + 1) * sizeof *out->v);
				v = &out->v[out->n++];
				memset(v, 0, sizeof *v);
				v->id = id;
			}
			if (tipo == 'A' && !v->conferma)
				v->conferma = xstrdup(resto);
			else if (tipo == 'S') {
				long long t;

				if (leggi_numero(resto, &t) && t > v->rinvio)
					v->rinvio = t;
			}
		}
		free(riga);
	}
	buf_free(&pulito);
}

const voce_casella_t *casella_voce(const casella_t *c, long long id)
{
	for (size_t i = 0; i < c->n; i++)
		if (c->v[i].id == id)
			return &c->v[i];
	return NULL;
}

void casella_libera(casella_t *c)
{
	for (size_t i = 0; i < c->n; i++)
		free(c->v[i].conferma);
	free(c->v);
	memset(c, 0, sizeof *c);
}

/* ---- terminali ---- */

bool scrivi_terminale(const char *t, uid_t uid, const char *testo, size_t n)
{
	int fd = open(t, O_WRONLY | O_NOCTTY | O_NONBLOCK | O_CLOEXEC);
	struct timespec inizio, ora;
	struct stat st;
	size_t fatti = 0;

	if (fd < 0)
		return false;
	/* il proprietario del terminale aperto, non del nome */
	if (fstat(fd, &st) < 0 || st.st_uid != uid || (!S_ISCHR(st.st_mode) && !ams_test)) {
		close(fd);
		return false;
	}
	clock_gettime(CLOCK_MONOTONIC, &inizio);
	while (fatti < n) {
		ssize_t w = write(fd, testo + fatti, n - fatti);

		if (w > 0) {
			fatti += (size_t)w;
			continue;
		}
		if (w < 0 && errno != EAGAIN && errno != EINTR)
			break;
		clock_gettime(CLOCK_MONOTONIC, &ora);
		if (ora.tv_sec - inizio.tv_sec >= 3)
			break;
		poll(&(struct pollfd){.fd = fd, .events = POLLOUT}, 1, 100);
	}
	close(fd);
	return fatti == n;
}

/* Il numero di terminale di un processo (campo tty_nr di /proc/PID/stat). */
static bool tty_di(const char *pid, unsigned long long *tty)
{
	char *p = xasprintf("/proc/%s/stat", pid);
	buf_t b = {0};
	char *q;
	bool ok = false;

	if (leggi_file(p, 4096, false, &b) == 0 && b.s && (q = strrchr(b.s, ')'))) {
		char stato;
		int ppid, pgrp, sess, tty_nr;

		if (sscanf(q + 1, " %c %d %d %d %d", &stato, &ppid, &pgrp, &sess, &tty_nr) == 5) {
			*tty = (unsigned int)tty_nr;
			ok = true;
		}
	}
	buf_free(&b);
	free(p);
	return ok;
}

void lingua_terminale(const char *t, const utente_t *u, char out[8])
{
	struct stat st;
	unsigned long long cercato;
	strv_t pids = {0};

	snprintf(out, 8, "%s", ams_test ? ams_lingua : lingua_sistema());
	if (ams_test || stat(t, &st) < 0 || !S_ISCHR(st.st_mode))
		return;
	cercato = (minor(st.st_rdev) & 0xff) | (major(st.st_rdev) << 8) | ((minor(st.st_rdev) & ~0xffu) << 12);
	elenca_numeri("/proc", &pids);
	/* il primo processo del terminale, di solito la shell */
	for (size_t i = 0; i < pids.n; i++) {
		unsigned long long tty;
		char *env;
		buf_t b = {0};
		bool ok;

		if (!tty_di(pids.v[i], &tty) || tty != cercato)
			continue;
		env = xasprintf("/proc/%s/environ", pids.v[i]);
		/* root senza CAP_SYS_PTRACE (un container) non può leggerlo: lo legge l'utente */
		ok = leggi_file(env, 1 << 20, false, &b) == 0 ||
		     (buf_clear(&b), come_utente(u, op_environ, env, NULL, &b, 1 << 20, 5) == 0);
		if (ok && lingua_da_environ(b.s ? b.s : "", b.n, out)) {
			buf_free(&b);
			free(env);
			break;
		}
		snprintf(out, 8, "%s", lingua_sistema());
		buf_free(&b);
		free(env);
		break;
	}
	strv_free(&pids);
}

/* ---- agente del desktop ---- */

void sveglia_agente(const utente_t *u)
{
	op_sveglia_t o = {u->uid};
	char *agente, *macchina;
	pid_t pid;

	if (ams_test || !sessione_grafica(u->uid))
		return;
	if (come_utente(u, op_sveglia, &o, NULL, NULL, 0, 5) == 0)
		return;
	/* Nessun agente pronto: se ne avvia uno nel gestore utente di systemd, che
	 * conosce già l'ambiente grafico. Se uno stava partendo, il nuovo trova il
	 * lock ed esce; quello che partiva legge la casella al primo giro. */
	agente = xasprintf("%s/ams-user", ams_libdir);
	macchina = xasprintf("--machine=%s@.host", u->nome);
	fflush(stdout);
	pid = fork();
	if (pid == 0) {
		int nul = open("/dev/null", O_RDWR);

		if (nul >= 0) {
			dup2(nul, 0);
			dup2(nul, 1);
		}
		if (geteuid() == 0)
			execlp("systemd-run", "systemd-run", "--user", macchina, "--collect", "--quiet", agente, "agent",
			       (char *)NULL);
		else
			execlp("systemd-run", "systemd-run", "--user", "--collect", "--quiet", agente, "agent", (char *)NULL);
		_exit(127);
	}
	if (pid > 0)
		while (waitpid(pid, NULL, 0) < 0 && errno == EINTR)
			;
	free(agente);
	free(macchina);
}
