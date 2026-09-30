/* AMS - Advanced Messaging System
 * ams: invio e gestione dei messaggi. Riservato agli amministratori: gira
 * sempre come root, anche per la guida e la versione, e si rilancia da solo
 * con sudo. AMS_TEST=1 permette di provarlo senza root su una cartella di prova. */
#include "comune.h"

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

#include "ams.h"
#include "archivio.h"
#include "evento.h"
#include "guida.h"
#include "lingua.h"
#include "sessioni.h"
#include "testo.h"
#include "utente.h"

static char vuota[1];

static char *sent_dir(void)
{
	return xasprintf("%s/sent", ams_var);
}

static char *msg_dir(long long id)
{
	return xasprintf("%s/sent/%lld", ams_var, id);
}

static char *in_msg(long long id, const char *nome)
{
	return xasprintf("%s/sent/%lld/%s", ams_var, id, nome);
}

/* Chi sta usando ams: l'amministratore che è passato da sudo, o chi lo lancia. */
static const char *autore(void)
{
	static char nome[64];
	const char *s = getenv("SUDO_USER");
	struct passwd *pw;

	if (s && *s && strlen(s) < sizeof nome && getpwnam(s)) {
		snprintf(nome, sizeof nome, "%s", s);
		return nome;
	}
	pw = getpwuid(getuid());
	snprintf(nome, sizeof nome, "%s", pw ? pw->pw_name : "?");
	return nome;
}

/* Apre sent/ID/lock e prende il lock (esclusivo); se nb e il lock è occupato,
 * esito -1. Il descrittore non passa ai processi figli. */
static int prendi_lock(long long id, bool nb)
{
	char *p = in_msg(id, "lock");
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

static bool segno(long long id, const char *nome)
{
	char *p = in_msg(id, nome);
	bool r = esiste(p);

	free(p);
	return r;
}

static void metti_segno(long long id, const char *nome)
{
	char *p = in_msg(id, nome);
	int fd = open(p, O_WRONLY | O_CREAT | O_CLOEXEC | O_NOFOLLOW, 0600);

	if (fd >= 0)
		close(fd);
	free(p);
}

static void togli_segno(long long id, const char *nome)
{
	char *p = in_msg(id, nome);

	unlink(p);
	free(p);
}

static void leggi_destinatari(long long id, strv_t *out)
{
	char *p = in_msg(id, "recipients");
	buf_t b = {0};

	if (leggi_file(p, 1 << 22, true, &b) == 0)
		for (char *s = strtok(b.s ? b.s : vuota, " \t\n"); s; s = strtok(NULL, " \t\n"))
			strv_add(out, s);
	buf_free(&b);
	free(p);
}

/* Consegne annotate in sent/ID/delivery: utente → terminali scritti. */
typedef struct {
	strv_t utenti;
	strv_t terminali;
} consegne_t;

static void leggi_consegne(long long id, consegne_t *c)
{
	char *p = in_msg(id, "delivery");
	buf_t b = {0};

	memset(c, 0, sizeof *c);
	if (leggi_file(p, 1 << 24, true, &b) == 0)
		for (char *r = b.s; r && *r;) {
			size_t len = strcspn(r, "\n");
			char u[256] = "", t[32] = "0";
			char *riga = xmalloc(len + 1);

			memcpy(riga, r, len);
			riga[len] = '\0';
			if (sscanf(riga, "%255s %*s %31s", u, t) >= 1 && !strv_has(&c->utenti, u)) {
				strv_add(&c->utenti, u);
				strv_add(&c->terminali, t);
			}
			free(riga);
			r += len;
			if (*r)
				r++;
		}
	buf_free(&b);
	free(p);
}

static const char *consegnato_a(const consegne_t *c, const char *u)
{
	for (size_t i = 0; i < c->utenti.n; i++)
		if (!strcmp(c->utenti.v[i], u))
			return c->terminali.v[i];
	return NULL;
}

static void consegne_libera(consegne_t *c)
{
	strv_free(&c->utenti);
	strv_free(&c->terminali);
}

static void annota_consegna(long long id, const char *u, int nterm)
{
	char *p = in_msg(id, "delivery");
	int fd = open(p, O_WRONLY | O_CREAT | O_APPEND | O_CLOEXEC | O_NOFOLLOW, 0600);

	if (fd >= 0) {
		char riga[400];
		int n = snprintf(riga, sizeof riga, "%s %lld %d\n", u, (long long)adesso(), nterm);

		if (n > 0 && (size_t)n < sizeof riga)
			scrivi_tutto(fd, riga, (size_t)n);
		close(fd);
	}
	free(p);
}

static bool leggi_testo_msg(long long id, buf_t *out)
{
	char *p = in_msg(id, "msg");
	bool ok = leggi_file(p, AMS_MAX_MSG, true, out) == 0 && out->n > 0;

	free(p);
	return ok;
}

/* ---- ritiro e cancellazione (usati anche dal recupero) ---- */

/* Toglie dalle caselle le copie del messaggio ID e i rinvii, come ciascun
 * utente. sent/ID/ritiro resta finché qualche copia non si è potuta togliere. */
static bool togli_copie(long long id)
{
	strv_t dest = {0};
	int mancano = 0;

	leggi_destinatari(id, &dest);
	for (size_t i = 0; i < dest.n; i++) {
		utente_t u;

		if (!utente_cerca(dest.v[i], &u))
			continue;
		if (!togli_copia(&u, id))
			mancano++;
		utente_libera(&u);
	}
	strv_free(&dest);
	if (mancano)
		return false;
	togli_segno(id, "ritiro");
	return true;
}

/* Toglie copie, conferme e rinvii di un messaggio già spostato in
 * sent/.cancella-ID, poi la sua cartella. Si può ripetere. */
static void cancella_cartella(const char *dir, long long id)
{
	char *p = xasprintf("%s/recipients", dir);
	buf_t b = {0};
	DIR *d;

	if (leggi_file(p, 1 << 22, true, &b) == 0)
		for (char *s = strtok(b.s ? b.s : vuota, " \t\n"); s; s = strtok(NULL, " \t\n")) {
			utente_t u;

			if (utente_cerca(s, &u)) {
				cancella_copie(&u, id);
				utente_libera(&u);
			}
		}
	buf_free(&b);
	free(p);
	/* la cartella contiene solo file di root */
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

/* ---- recupero: gira all'inizio di send, list, status, revoke, log ---- */

void recupera(void)
{
	char *sd = sent_dir();
	strv_t ids = {0};
	DIR *d;

	if (elenca_numeri(sd, &ids) < 0) {
		free(sd);
		return;
	}
	for (size_t i = 0; i < ids.n; i++) {
		long long id;
		int lock;

		leggi_numero(ids.v[i], &id);
		if (!segno(id, "incomplete") && !segno(id, "ritiro"))
			continue;
		/* un invio ancora in corso tiene il lock: non è interrotto, si salta */
		if ((lock = prendi_lock(id, true)) < 0)
			continue;
		if (segno(id, "incomplete")) {
			buf_t msg = {0};
			msg_t m;
			strv_t dest = {0};
			consegne_t cons;
			int nuove = 0, mancano = 0;
			char *dir = msg_dir(id);

			leggi_destinatari(id, &dest);
			if (!leggi_testo_msg(id, &msg) || !dest.n || msg_da_testo(msg.s, msg.n, &m) < 0) {
				char *f = in_msg(id, "failed");
				char data[32];
				int n = snprintf(data, sizeof data, "%lld\n", (long long)adesso());

				scrivi_atomico(f, data, (size_t)n, 0600);
				free(f);
				togli_segno(id, "incomplete");
				evento("ANNULLATO", id, "", "", "", "");
				avviso(T("message %lld was interrupted before being saved and has been cancelled"), id);
			} else if (segno(id, "revoked") || msg_scaduto(&m, adesso())) {
				togli_segno(id, "incomplete");
				msg_libera(&m);
			} else {
				leggi_consegne(id, &cons);
				for (size_t k = 0; k < dest.n; k++) {
					utente_t u;
					bool annotata = consegnato_a(&cons, dest.v[k]) != NULL;

					if (!utente_cerca(dest.v[k], &u)) {
						mancano++;
						continue;
					}
					/* Anche una copia già annotata si ricontrolla: dopo
					 * un'interruzione di corrente potrebbe non essere su disco. */
					if (consegna_copia(&u, id, &msg)) {
						if (!annotata) {
							annota_consegna(id, u.nome, 0);
							evento("CONSEGNATO", id, u.nome, "", "", "");
							sveglia_agente(&u);
							nuove++;
						}
					} else {
						mancano++;
					}
					utente_libera(&u);
				}
				consegne_libera(&cons);
				msg_libera(&m);
				if (!mancano) {
					char *users = xasprintf("%s/users", ams_var);

					syncfs_path(users);
					sync_path(dir);
					free(users);
					togli_segno(id, "incomplete");
				}
				if (nuove) {
					char det[24];

					snprintf(det, sizeof det, "%d", nuove);
					evento("RECUPERATO", id, "", "", det, "");
					avviso(T("completed delivery of message %lld to %d recipients"), id, nuove);
				}
				if (mancano)
					avviso(T("message %lld still not delivered to %d recipients (see ams status %lld)"), id,
					       mancano, id);
			}
			strv_free(&dest);
			buf_free(&msg);
			free(dir);
		}
		if (segno(id, "ritiro"))
			togli_copie(id);
		close(lock);
	}
	strv_free(&ids);
	/* cancellazioni rimaste a metà */
	if ((d = opendir(sd))) {
		struct dirent *e;
		strv_t canc = {0};

		while ((e = readdir(d)))
			if (!strncmp(e->d_name, ".cancella-", 10) && solo_cifre(e->d_name + 10))
				strv_add(&canc, e->d_name);
		closedir(d);
		for (size_t i = 0; i < canc.n; i++) {
			char *dir = xasprintf("%s/%s", sd, canc.v[i]);
			long long id;

			if (leggi_numero(canc.v[i] + 10, &id))
				cancella_cartella(dir, id);
			free(dir);
		}
		strv_free(&canc);
	}
	free(sd);
}

/* ---- destinatari ---- */

static void risolvi_destinatari(const char *to, strv_t *out)
{
	char *copia = xstrdup(to), *salva = NULL;

	for (char *v = strtok_r(copia, ",", &salva); v; v = strtok_r(NULL, ",", &salva)) {
		strv_t l = {0};

		if (!strcmp(v, "all"))
			utenti_umani(&l);
		else if (!strcmp(v, "online"))
			utenti_online(&l);
		else if (v[0] == '@') {
			if (!membri_gruppo(v + 1, &l))
				die(T("no such group: %s"), v + 1);
		} else {
			if (!getpwnam(v))
				die(T("no such user: %s"), v);
			strv_add(&l, v);
		}
		for (size_t i = 0; i < l.n; i++)
			if (*l.v[i] && !strv_has(out, l.v[i]))
				strv_add(out, l.v[i]);
		strv_free(&l);
	}
	free(copia);
	strv_sort(out);
}

/* ---- invio ---- */

static long long scadenza_da(const char *s)
{
	size_t n = strlen(s);
	long long v;

	if (n >= 2 && strchr("mhd", s[n - 1])) {
		char *num = xstrdup(s);

		num[n - 1] = '\0';
		if (leggi_numero(num, &v)) {
			free(num);
			return (long long)adesso() + v * (s[n - 1] == 'm' ? 60 : s[n - 1] == 'h' ? 3600 : 86400);
		}
		free(num);
	}
	/* data e ora: le interpreta date -d, come nel prototipo */
	{
		int p[2];
		pid_t pid;
		buf_t b = {0};
		int stato;

		if (pipe2(p, O_CLOEXEC) < 0)
			die(T("invalid expiry: %s"), s);
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
		leggi_fd(p[0], 64, &b);
		close(p[0]);
		waitpid(pid, &stato, 0);
		if (pid < 0 || !WIFEXITED(stato) || WEXITSTATUS(stato) || !b.s)
			die(T("invalid expiry: %s"), s);
		b.s[strcspn(b.s, "\n")] = '\0';
		if (!leggi_numero(b.s, &v))
			die(T("invalid expiry: %s"), s);
		buf_free(&b);
		return v;
	}
}

/* Il prossimo ID: sequenza con flock; se la cartella esiste già (la
 * sequenza tornata indietro dopo un'interruzione di corrente), si va avanti. */
static long long prossimo_id(void)
{
	char *seq = xasprintf("%s/sent/.seq", ams_var), *lockp = xasprintf("%s/sent/.seq.lock", ams_var);
	int fd = open(lockp, O_WRONLY | O_CREAT | O_CLOEXEC | O_NOFOLLOW, 0600);
	buf_t b = {0};
	long long n = 0;
	char s[32];
	int len;

	if (fd < 0 || flock(fd, LOCK_EX) < 0)
		die("%s: %s", lockp, strerror(errno));
	if (leggi_file(seq, 64, true, &b) == 0 && b.s) {
		b.s[strcspn(b.s, "\n")] = '\0';
		if (!leggi_numero(b.s, &n))
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
	if (scrivi_atomico(seq, s, (size_t)len, 0600) < 0)
		die("%s: %s", seq, strerror(errno));
	close(fd);
	buf_free(&b);
	free(seq);
	free(lockp);
	return n;
}

static void prepara_archivio(void)
{
	char *users = xasprintf("%s/users", ams_var), *sd = sent_dir();

	mkdir(ams_var, 0755);
	mkdir(users, 0755);
	mkdir(sd, 0700);
	if (!e_cartella(users) || !e_cartella(sd))
		die("%s: %s", ams_var, strerror(errno));
	free(users);
	free(sd);
}

/* Il messaggio formattato per un terminale, nella lingua data, con «\r\n»
 * (il terminale può essere in modo grezzo, per esempio dentro un editor). */
static void testo_terminale(const msg_t *m, const char *lingua, buf_t *out)
{
	buf_t t = {0}, h = {0};

	msg_intestazione(m, &h);
	buf_adds(&t, "\n");
	buf_printf(&t, tl(lingua, "── AMS · Message from the administrator · %s ──"), h.s);
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
	const char *to = NULL, *titolo = "", *file = NULL;
	long long scadenza = 0, id;
	buf_t testo = {0}, pulito = {0}, tit = {0}, msgtxt = {0};
	strv_t dest = {0};
	msg_t m = {0};
	char *dir, *users;
	int lock, i, falliti = 0;
	strv_t non = {0};

	for (i = 0; i < argc; i++) {
		const char *a = argv[i];

		if (!strcmp(a, "--to") || !strcmp(a, "--title") || !strcmp(a, "--expires") || !strcmp(a, "--file")) {
			if (i + 1 >= argc || !*argv[i + 1])
				die(T("missing value for %s"), a);
			if (!strcmp(a, "--to"))
				to = argv[++i];
			else if (!strcmp(a, "--title"))
				titolo = argv[++i];
			else if (!strcmp(a, "--file"))
				file = argv[++i];
			else {
				scadenza = scadenza_da(argv[++i]);
				if (scadenza <= (long long)adesso())
					die("%s", T("the expiry is already in the past"));
			}
		} else if (!strcmp(a, "--")) {
			i++;
			break;
		} else if (a[0] == '-' && a[1]) {
			die(T("unknown option: %s"), a);
		} else {
			break;
		}
	}
	if (!to)
		die("%s", T("missing --to"));
	if (i < argc) {
		for (int k = i; k < argc; k++) {
			if (k > i)
				buf_addc(&testo, ' ');
			buf_adds(&testo, argv[k]);
		}
	} else if (file) {
		if (leggi_file(file, (size_t)1 << 26, false, &testo) < 0)
			die("%s: %s", file, strerror(errno));
	} else {
		leggi_fd(0, (size_t)1 << 26, &testo);
	}
	/* come nel prototipo: niente a capo finali, poi uno */
	while (testo.n && testo.s[testo.n - 1] == '\n')
		testo.s[--testo.n] = '\0';
	pulisci(testo.s ? testo.s : "", testo.n, &pulito);
	pulisci(titolo, strlen(titolo), &tit);
	for (size_t k = 0; k < tit.n; k++)
		if (tit.s[k] == '\n' || tit.s[k] == '\t')
			tit.s[k] = ' ';
	{
		bool vuoto = true;

		for (size_t k = 0; k < pulito.n; k++)
			if (!strchr(" \t\n\v\f\r", pulito.s[k]))
				vuoto = false;
		if (vuoto)
			die("%s", T("empty message"));
	}
	if (pulito.n > AMS_MAX_BYTES)
		die(T("message too long: %zu bytes (at most %d)"), pulito.n, AMS_MAX_BYTES);

	risolvi_destinatari(to, &dest);
	if (!dest.n)
		die("%s", T("no recipients"));

	prepara_archivio();
	id = prossimo_id();
	dir = msg_dir(id);
	/* Il lock dice «invio in corso» a recupero, ritiro e cancellazione per
	 * tutta la consegna; se ams muore, anche con SIGKILL, il kernel lo rilascia. */
	if ((lock = prendi_lock(id, false)) < 0)
		die("%s: %s", dir, strerror(errno));
	/* Il segno resta finché tutte le copie non sono consegnate e su disco. */
	metti_segno(id, "incomplete");
	m.id = id;
	m.from = xstrdup(autore());
	m.date = (long long)adesso();
	m.title = xstrdup(tit.s ? tit.s : "");
	m.expires = scadenza;
	m.body = xasprintf("%s\n", pulito.s ? pulito.s : "");
	msg_formatta(&m, &msgtxt);
	{
		char *mp = in_msg(id, "msg"), *rp = in_msg(id, "recipients"), *ip = in_msg(id, "incomplete");
		buf_t r = {0};

		for (size_t k = 0; k < dest.n; k++)
			buf_printf(&r, "%s\n", dest.v[k]);
		/* messaggio, destinatari e segno su disco prima di ogni consegna */
		if (scrivi_atomico(mp, msgtxt.s, msgtxt.n, 0600) < 0 || scrivi_atomico(rp, r.s, r.n, 0600) < 0)
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
		utente_t u;
		strv_t term = {0};
		int nterm = 0;
		char det[16];

		/* ritirato durante l'invio (ams revoke aspetta il lock): non si consegna altro */
		if (segno(id, "revoked"))
			break;
		if (!utente_cerca(dest.v[k], &u) || !consegna_copia(&u, id, &msgtxt)) {
			strv_add(&non, dest.v[k]);
			falliti++;
			evento("NON_CONSEGNATO", id, dest.v[k], "", "", "");
			utente_libera(&u);
			continue;
		}
		terminali_utente(u.uid, &term);
		for (size_t t = 0; t < term.n; t++) {
			char lingua[8];
			buf_t out = {0};

			/* nella lingua di chi usa quel terminale */
			lingua_terminale(term.v[t], &u, lingua);
			testo_terminale(&m, lingua, &out);
			if (scrivi_terminale(term.v[t], u.uid, out.s, out.n))
				nterm++;
			buf_free(&out);
		}
		strv_free(&term);
		sveglia_agente(&u);
		annota_consegna(id, u.nome, nterm);
		snprintf(det, sizeof det, "%d", nterm);
		evento("CONSEGNATO", id, u.nome, "", det, "");
		utente_libera(&u);
	}
	{
		buf_t elenco = {0};

		for (size_t k = 0; k < dest.n; k++)
			buf_printf(&elenco, "%s%s", k ? " " : "", dest.v[k]);
		evento("INVIATO", id, "", "", elenco.s, autore());
		buf_free(&elenco);
	}
	if (falliti) {
		buf_t l = {0};

		for (size_t k = 0; k < non.n; k++)
			buf_printf(&l, " %s", non.v[k]);
		printf(T("Message %lld delivered to %zu of %zu recipients."), id, dest.n - (size_t)falliti, dest.n);
		putchar('\n');
		die(T("message %lld not delivered to:%s (see the log; the next ams command will retry)"), id, l.s);
	}
	/* copie e consegne su disco prima di togliere il segno: finché c'è, il
	 * recupero ricontrolla ogni copia */
	users = xasprintf("%s/users", ams_var);
	syncfs_path(users);
	sync_path(dir);
	togli_segno(id, "incomplete");
	sync_path(dir);
	if (segno(id, "revoked"))
		printf(T("Message %lld revoked while sending: delivery stopped."), id);
	else if (dest.n == 1)
		printf(T("Message %lld sent to 1 user."), id);
	else
		printf(T("Message %lld sent to %zu users."), id, dest.n);
	putchar('\n');
	close(lock);
	free(users);
	free(dir);
	msg_libera(&m);
	buf_free(&testo);
	buf_free(&pulito);
	buf_free(&tit);
	buf_free(&msgtxt);
	strv_free(&dest);
	strv_free(&non);
}

/* ---- stato dei destinatari (list, status) ---- */

/* Le caselle si leggono una volta per utente e restano in memoria. */
static struct {
	char *nome;
	casella_t c;
} *caselle;
static size_t ncaselle;
static strv_t tutti_id;
static bool tutti_id_letti;

static const casella_t *casella_utente(const char *nome)
{
	utente_t u;

	for (size_t i = 0; i < ncaselle; i++)
		if (!strcmp(caselle[i].nome, nome))
			return &caselle[i].c;
	if (!tutti_id_letti) {
		char *sd = sent_dir();

		elenca_numeri(sd, &tutti_id);
		tutti_id_letti = true;
		free(sd);
	}
	caselle = xrealloc(caselle, (ncaselle + 1) * sizeof *caselle);
	caselle[ncaselle].nome = xstrdup(nome);
	memset(&caselle[ncaselle].c, 0, sizeof caselle[ncaselle].c);
	if (utente_cerca(nome, &u)) {
		leggi_casella(&u, &tutti_id, &caselle[ncaselle].c);
		utente_libera(&u);
	}
	return &caselle[ncaselle++].c;
}

void caselle_svuota(void)
{
	for (size_t i = 0; i < ncaselle; i++) {
		free(caselle[i].nome);
		casella_libera(&caselle[i].c);
	}
	free(caselle);
	caselle = NULL;
	ncaselle = 0;
	strv_free(&tutti_id);
	tutti_id_letti = false;
}

typedef struct {
	stato_e stato;
	bool tardiva;     /* conferma dopo la scadenza */
	long long quando; /* data della conferma */
	char *canale;
} stato_t;

/* Stato di un destinatario. La scadenza e il ritiro che contano sono quelli
 * della copia di riferimento (sent/): una conferma con data successiva non vale. */
static void stato_destinatario(const char *u, long long id, const consegne_t *cons, const msg_t *m, long long ritiro,
			       stato_t *s)
{
	const voce_casella_t *v;
	long long quando = 0;
	char *sp;

	memset(s, 0, sizeof *s);
	if (!consegnato_a(cons, u)) {
		s->stato = INVIATO;
		return;
	}
	s->stato = CONSEGNATO;
	v = casella_voce(casella_utente(u), id);
	if (!v || !v->conferma)
		return;
	{
		char *copia = xstrdup(v->conferma);

		sp = strchr(copia, ' ');
		if (sp)
			*sp = '\0';
		if (!leggi_numero(copia, &quando))
			quando = 0;
		free(copia);
	}
	if (m->expires && quando > m->expires) {
		s->tardiva = true;
		return;
	}
	if (ritiro && quando > ritiro)
		return;
	s->stato = CONFERMATO;
	s->quando = quando;
	sp = strchr(v->conferma, ' ');
	s->canale = xstrdup(sp && sp[1] ? sp + 1 : "?");
}

long long data_ritiro(long long id)
{
	char *p = in_msg(id, "revoked");
	buf_t b = {0};
	long long r = 0;

	if (leggi_file(p, 64, true, &b) == 0 && b.s) {
		b.s[strcspn(b.s, "\n")] = '\0';
		if (!leggi_numero(b.s, &r))
			r = 0;
	}
	buf_free(&b);
	free(p);
	return r;
}

void elenco_messaggi(strv_t *ids)
{
	char *sd = sent_dir();

	elenca_numeri(sd, ids);
	free(sd);
}

/* Tutto ciò che serve si legge prima: un messaggio cancellato nel frattempo
 * da ams purge sparisce invece di uscire a metà. */
bool riassumi(long long id, riassunto_t *r)
{
	char *p;
	strv_t dest = {0};
	consegne_t cons;
	long long ritiro;

	memset(r, 0, sizeof *r);
	r->id = id;
	if (segno(id, "failed"))
		return false;
	p = in_msg(id, "msg");
	if (msg_leggi(p, &r->m) < 0) {
		free(p);
		return false;
	}
	free(p);
	leggi_destinatari(id, &dest);
	if (!dest.n) {
		msg_libera(&r->m);
		return false;
	}
	leggi_consegne(id, &cons);
	ritiro = data_ritiro(id);
	for (size_t k = 0; k < dest.n; k++) {
		stato_t st;

		stato_destinatario(dest.v[k], id, &cons, &r->m, ritiro, &st);
		if (st.stato == CONFERMATO)
			r->confermato++;
		else if (st.stato == CONSEGNATO)
			r->consegnato++;
		else
			r->inviato++;
		free(st.canale);
	}
	r->ritirato = segno(id, "revoked");
	r->scaduto = msg_scaduto(&r->m, adesso());
	consegne_libera(&cons);
	strv_free(&dest);
	return true;
}

void riassunto_libera(riassunto_t *r)
{
	msg_libera(&r->m);
}

void riassunto_frase(const riassunto_t *r, buf_t *out)
{
	const char *sep = "";

	if (!r->consegnato && !r->inviato) {
		buf_printf(out, T("all confirmed (%d)"), r->confermato);
		return;
	}
	if (r->confermato) {
		buf_printf(out, T("%d confirmed"), r->confermato);
		sep = " · ";
	}
	if (r->consegnato) {
		buf_adds(out, sep);
		buf_printf(out, T("%d delivered"), r->consegnato);
		sep = " · ";
	}
	if (r->inviato) {
		buf_adds(out, sep);
		buf_printf(out, T("%d sent"), r->inviato);
	}
}

/* Un messaggio per riga: il testo (con ritirato e scaduto davanti) e i
 * destinatari nei tre stati (capitolo «Specifica»). */
/* Scrive s in w caratteri (UTF-8), tagliando o riempiendo a destra. */
static void colonna(const char *s, size_t n, int w)
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

	if (!e_cartella(sd)) {
		puts(T("No messages sent."));
		free(sd);
		return;
	}
	free(sd);
	elenco_messaggi(&ids);
	if (!ids.n) {
		puts(T("No messages sent."));
		strv_free(&ids);
		return;
	}
	printf("%-5s %-12s ", T("ID"), T("DATE"));
	colonna(T("TEXT"), strlen(T("TEXT")), 40);
	printf("  %s\n", T("RECIPIENTS"));
	for (size_t i = 0; i < ids.n; i++) {
		long long id;
		riassunto_t r;
		char data[32];
		buf_t testo = {0}, frase = {0};

		leggi_numero(ids.v[i], &id);
		if (segno(id, "failed")) {
			printf("%-5s %-12s %s\n", ids.v[i], "-", T("[send cancelled: interrupted before it was saved]"));
			continue;
		}
		if (!riassumi(id, &r))
			continue;
		if (r.ritirato)
			buf_adds(&testo, T("[revoked] "));
		if (r.scaduto)
			buf_adds(&testo, T("[expired] "));
		buf_add(&testo, r.m.body, strcspn(r.m.body, "\n"));
		riassunto_frase(&r, &frase);
		data_breve((time_t)r.m.date, data);
		printf("%-5s %-12s ", ids.v[i], data);
		colonna(testo.s, testo.n, 40);
		printf("  %s\n", frase.s);
		buf_free(&testo);
		buf_free(&frase);
		riassunto_libera(&r);
	}
	strv_free(&ids);
}

static long long id_da(const char *s)
{
	long long id;

	if (!s || !*s)
		die("%s", T("missing message ID"));
	if (!leggi_numero(s, &id))
		die(T("no such message: %s"), s);
	return id;
}

static void carica_msg(long long id, const char *arg, msg_t *m)
{
	char *p = in_msg(id, "msg");

	if (msg_leggi(p, m) < 0)
		die(T("no such message: %s"), arg);
	free(p);
}

/* La riga di stato di ogni destinatario, come in ams status. */
void destinatari(long long id, const msg_t *m, destinatari_t *out)
{
	strv_t dest = {0};
	consegne_t cons;
	long long ritiro = data_ritiro(id);
	bool ritirato = segno(id, "revoked"), incompleto = segno(id, "incomplete");
	char data[32];

	memset(out, 0, sizeof *out);
	leggi_destinatari(id, &dest);
	leggi_consegne(id, &cons);
	out->v = xmalloc((dest.n ? dest.n : 1) * sizeof *out->v);
	for (size_t k = 0; k < dest.n; k++) {
		stato_t s;
		buf_t riga = {0};

		stato_destinatario(dest.v[k], id, &cons, m, ritiro, &s);
		if (s.stato == CONFERMATO) {
			buf_t ch = {0};

			canale_testo(ams_lingua, s.canale, &ch);
			data_breve((time_t)s.quando, data);
			buf_printf(&riga, T("confirmed on %s (%s)"), data, ch.s ? ch.s : "");
			buf_free(&ch);
		} else if (s.stato == INVIATO) {
			buf_adds(&riga, incompleto ? T("sent, not delivered: the copy could not be written (see the log; the next ams command will retry)")
						   : T("sent, not delivered"));
		} else {
			buf_adds(&riga, T("delivered"));
			if (ritirato)
				buf_adds(&riga, T(", not confirmed (revoked)"));
			else if (s.tardiva)
				buf_adds(&riga, T(", not confirmed (expired; confirmation arrived after the expiry)"));
			else if (msg_scaduto(m, adesso()))
				buf_adds(&riga, T(", not confirmed (expired)"));
			else {
				const char *nt = consegnato_a(&cons, dest.v[k]);
				const voce_casella_t *v = casella_voce(casella_utente(dest.v[k]), id);
				long long n = 0;

				if (nt && leggi_numero(nt, &n) && n == 1)
					buf_adds(&riga, T(", written to 1 terminal"));
				else if (n > 1)
					buf_printf(&riga, T(", written to %lld terminals"), n);
				if (v && v->rinvio) {
					data_breve((time_t)v->rinvio, data);
					buf_printf(&riga, T(", postponed on %s"), data);
				}
			}
		}
		out->v[out->n].utente = xstrdup(dest.v[k]);
		out->v[out->n].stato = s.stato;
		out->v[out->n++].riga = riga.s ? riga.s : xstrdup("");
		free(s.canale);
	}
	consegne_libera(&cons);
	strv_free(&dest);
}

void destinatari_libera(destinatari_t *d)
{
	for (size_t i = 0; i < d->n; i++) {
		free(d->v[i].utente);
		free(d->v[i].riga);
	}
	free(d->v);
	memset(d, 0, sizeof *d);
}

static void cmd_status(const char *arg)
{
	long long id = id_da(arg), ritiro;
	msg_t m;
	destinatari_t d;
	buf_t h = {0};
	char data[32];

	carica_msg(id, arg, &m);
	if (segno(id, "failed"))
		die(T("message %lld was cancelled: sending was interrupted before it was saved"), id);
	msg_intestazione(&m, &h);
	printf(T("Message %lld · %s · from %s"), id, h.s, m.from);
	putchar('\n');
	ritiro = data_ritiro(id);
	if (segno(id, "revoked")) {
		data_breve((time_t)ritiro, data);
		printf(T("REVOKED on %s"), data);
		putchar('\n');
	}
	if (msg_scaduto(&m, adesso()))
		puts(T("EXPIRED"));
	for (char *p = m.body; *p;) {
		size_t len = strcspn(p, "\n");

		printf("  │ %.*s\n", (int)len, p);
		p += len;
		if (*p)
			p++;
	}
	putchar('\n');
	printf("%-16s %s\n", T("USER"), T("STATE"));
	destinatari(id, &m, &d);
	for (size_t k = 0; k < d.n; k++)
		printf("%-16s %s\n", d.v[k].utente, d.v[k].riga);
	destinatari_libera(&d);
	msg_libera(&m);
	buf_free(&h);
}

/* ---- ritiro ---- */

/* Il ritiro avviene quando compare sent/ID/revoked (su disco): da lì nessuna
 * nuova consegna e nessuna conferma successiva vale. Poi si aspetta l'invio
 * eventualmente in corso (lock), che si ferma al destinatario successivo, e
 * si tolgono le copie; sent/ID/ritiro resta finché non sono tolte tutte. */
void cmd_revoke(const char *arg)
{
	long long id = id_da(arg);
	msg_t m;
	char *dir = msg_dir(id), *rev = in_msg(id, "revoked"), *rit = in_msg(id, "ritiro");
	int lock;

	carica_msg(id, arg, &m);
	metti_segno(id, "ritiro");
	if (!esiste(rev)) {
		char data[32];
		int n = snprintf(data, sizeof data, "%lld\n", (long long)adesso());

		if (scrivi_atomico(rev, data, (size_t)n, 0600) < 0)
			die("%s: %s", rev, strerror(errno));
		sync_path(rit);
		sync_path(dir);
		evento("RITIRATO", id, "", "", "", autore());
	}
	if ((lock = prendi_lock(id, false)) < 0)
		die("%s: %s", dir, strerror(errno));
	if (!togli_copie(id))
		die(T("message %lld revoked, but some copies could not be removed from the mailboxes: the next ams command will retry"),
		    id);
	printf(T("Message %lld revoked."), id);
	putchar('\n');
	close(lock);
	msg_libera(&m);
	free(dir);
	free(rev);
	free(rit);
}

/* ---- sollecito ---- */

/* Chi non ha confermato viene sollecitato subito: si tolgono i suoi rinvii
 * (la domanda torna al prompt successivo, la finestra al giro successivo) e
 * si sveglia il suo agente del desktop. */
void cmd_remind(const char *arg)
{
	long long id = id_da(arg);
	msg_t m;
	destinatari_t d;
	int n = 0;
	char det[24];

	carica_msg(id, arg, &m);
	if (segno(id, "revoked"))
		die(T("message %lld has been revoked: nobody to remind"), id);
	if (msg_scaduto(&m, adesso()))
		die(T("message %lld has expired: nobody to remind"), id);
	destinatari(id, &m, &d);
	for (size_t k = 0; k < d.n; k++) {
		utente_t u;

		if (d.v[k].stato != CONSEGNATO || !utente_cerca(d.v[k].utente, &u))
			continue;
		if (togli_rinvii(&u, id)) {
			sveglia_agente(&u);
			n++;
		}
		utente_libera(&u);
	}
	destinatari_libera(&d);
	snprintf(det, sizeof det, "%d", n);
	evento("SOLLECITATO", id, "", "", det, autore());
	if (n == 1)
		printf(T("Message %lld: 1 recipient reminded."), id);
	else
		printf(T("Message %lld: %d recipients reminded."), id, n);
	putchar('\n');
	msg_libera(&m);
}

void cmd_conta_destinatari(const char *to)
{
	strv_t dest = {0};

	risolvi_destinatari(to, &dest);
	printf("%zu\n", dest.n);
	strv_free(&dest);
}

/* ---- cancellazione ---- */

void cmd_purge(const char *dur)
{
	long long n, sec, limite;
	char *sd = sent_dir();
	strv_t ids = {0};
	int tolti = 0;
	size_t l;

	if (!dur || !*dur)
		die("%s", T("missing duration, for example 90d"));
	l = strlen(dur);
	{
		char *num = xstrdup(dur);

		num[l - 1] = '\0';
		if (l < 2 || !strchr("mhd", dur[l - 1]) || !leggi_numero(num, &n))
			die(T("invalid duration: %s (for example 90d, 12h, 30m)"), dur);
		free(num);
	}
	sec = n * (dur[l - 1] == 'm' ? 60 : dur[l - 1] == 'h' ? 3600 : 86400);
	limite = (long long)adesso() - sec;
	elenca_numeri(sd, &ids);
	for (size_t i = 0; i < ids.n; i++) {
		long long id, quando = 0;
		msg_t m;
		char *p, *nuovo;
		int lock;

		leggi_numero(ids.v[i], &id);
		if (segno(id, "incomplete"))
			continue;
		p = in_msg(id, "msg");
		if (msg_leggi(p, &m) == 0) {
			quando = m.date;
			msg_libera(&m);
		} else {
			struct stat st;
			char *d = msg_dir(id);

			if (stat(d, &st) == 0)
				quando = st.st_mtime;
			free(d);
		}
		free(p);
		if (quando >= limite)
			continue;
		if ((lock = prendi_lock(id, true)) < 0)
			continue;
		/* Il messaggio sparisce in un colpo solo (rinomina): gli altri comandi
		 * lo vedono intero o non lo vedono. La pulizia delle caselle segue, e
		 * se si interrompe la completa il comando ams successivo. */
		p = msg_dir(id);
		nuovo = xasprintf("%s/.cancella-%lld", sd, id);
		if (rename(p, nuovo) == 0) {
			sync_path(sd);
			close(lock);
			evento("CANCELLATO", id, "", "", dur, autore());
			cancella_cartella(nuovo, id);
			tolti++;
		} else {
			close(lock);
		}
		free(p);
		free(nuovo);
	}
	if (tolti == 0)
		printf(T("No messages older than %s."), dur);
	else if (tolti == 1)
		printf(T("Deleted 1 message older than %s."), dur);
	else
		printf(T("Deleted %d messages older than %s."), tolti, dur);
	putchar('\n');
	strv_free(&ids);
	free(sd);
}

/* ---- storia dal journal ---- */

static char *campo(sd_journal *j, const char *nome)
{
	const void *d;
	size_t l, k = strlen(nome);

	if (sd_journal_get_data(j, nome, &d, &l) < 0 || l <= k)
		return xstrdup("");
	{
		char *s = xmalloc(l - k);

		memcpy(s, (const char *)d + k + 1, l - k - 1);
		s[l - k - 1] = '\0';
		return s;
	}
}

/* Gli eventi con AMS_MESSAGGIO=ID dalla data dell'invio (un archivio azzerato
 * riusa i numeri, il journal no), riscritti dai campi AMS_* nella lingua di
 * chi legge. Chiunque può scrivere nel journal un evento con quei campi: il
 * journal registra _UID, chi l'ha scritto davvero, e un evento scritto
 * dall'utente sbagliato viene segnalato. */
void cmd_log(const char *arg)
{
	long long id = id_da(arg);
	msg_t m;
	sd_journal *j;
	buf_t h = {0};
	char match[64];
	uid_t radm = ams_test ? getuid() : 0;

	carica_msg(id, arg, &m);
	msg_intestazione(&m, &h);
	printf(T("Message %lld · %s"), id, h.s);
	putchar('\n');
	fflush(stdout);
	if (sd_journal_open(&j, 0) < 0)
		return;
	snprintf(match, sizeof match, "AMS_MESSAGGIO=%lld", id);
	sd_journal_add_match(j, "SYSLOG_IDENTIFIER=ams", 0);
	sd_journal_add_match(j, match, 0);
	sd_journal_seek_realtime_usec(j, (uint64_t)(m.date > 0 ? m.date - 1 : 0) * 1000000u);
	while (sd_journal_next(j) > 0) {
		uint64_t usec;
		char *ev = campo(j, "AMS_EVENTO"), *u = campo(j, "AMS_UTENTE"), *ch = campo(j, "AMS_CANALE"),
		     *det = campo(j, "AMS_DETTAGLI"), *aut = campo(j, "AMS_AUTORE"), *msg = campo(j, "MESSAGE"),
		     *uid = campo(j, "_UID");
		buf_t riga = {0}, pulita = {0};
		long long atteso = radm, scritto = -1;
		char data[32];
		time_t t;
		struct tm tm;

		if (sd_journal_get_realtime_usec(j, &usec) < 0)
			usec = 0;
		t = (time_t)(usec / 1000000u);
		if (!localtime_r(&t, &tm) || !strftime(data, sizeof data, "%Y-%m-%d %H:%M:%S", &tm))
			snprintf(data, sizeof data, "?");
		if (!strcmp(ev, "RINVIATO") || !strcmp(ev, "CONFERMATO") || !strcmp(ev, "CONFERMA_FALLITA")) {
			struct passwd *pw = getpwnam(u);

			atteso = pw ? (long long)pw->pw_uid : -2;
		}
		buf_printf(&riga, "%s  ", data);
		if (!leggi_numero(uid, &scritto) || scritto != atteso)
			buf_printf(&riga, T("[not trustworthy: written by UID %s] "), *uid ? uid : "?");
		if (!evento_testo(ams_lingua, ev, id, u, ch, det, aut, &riga))
			buf_adds(&riga, msg);
		pulisci(riga.s, riga.n, &pulita);
		printf("%s\n", pulita.s ? pulita.s : "");
		buf_free(&riga);
		buf_free(&pulita);
		free(ev);
		free(u);
		free(ch);
		free(det);
		free(aut);
		free(msg);
		free(uid);
	}
	sd_journal_close(j);
	msg_libera(&m);
	buf_free(&h);
}

/* ---- avvio ---- */

static void rilancia_con_sudo(char **argv)
{
	char self[PATH_MAX];
	ssize_t n = readlink("/proc/self/exe", self, sizeof self - 1);
	int argc = 0;
	char **nuovi;

	if (n <= 0)
		die("/proc/self/exe: %s", strerror(errno));
	self[n] = '\0';
	while (argv[argc])
		argc++;
	nuovi = xmalloc(((size_t)argc + 3) * sizeof *nuovi);
	static char sudo[] = "sudo", fine_opzioni[] = "--";

	nuovi[0] = sudo;
	nuovi[1] = fine_opzioni;
	nuovi[2] = self;
	for (int i = 1; i <= argc; i++)
		nuovi[i + 2] = argv[i];
	execvp("sudo", nuovi);
	die("sudo: %s", strerror(errno));
}

int main(int argc, char **argv)
{
	const char *cmd = argc > 1 ? argv[1] : "";

	ams_init("ams");
	lingua_init();
	/* Da amministratore non root, ams si rilancia con sudo, anche per la
	 * guida e la versione. */
	if (geteuid() != 0 && !ams_test)
		rilancia_con_sudo(argv);
	umask(022);

	/* ams da solo in un terminale apre la TUI; in una pipe, o con un
	 * terminale troppo piccolo, la guida */
	if (!*cmd && isatty(0) && isatty(1)) {
		recupera();
		if (ams_tui())
			return 0;
	}
	if (!*cmd || !strcmp(cmd, "help") || !strcmp(cmd, "-h") || !strcmp(cmd, "--help")) {
		ams_guida();
		return 0;
	}
	if (!strcmp(cmd, "version") || !strcmp(cmd, "--version")) {
		printf("AMS - Advanced Messaging System %s\n", AMS_VERSION);
		return 0;
	}
	if (strcmp(cmd, "send") && strcmp(cmd, "list") && strcmp(cmd, "status") && strcmp(cmd, "revoke") &&
	    strcmp(cmd, "remind") && strcmp(cmd, "log") && strcmp(cmd, "purge"))
		die(T("unknown command: %s (ams --help for the guide)"), cmd);
	if (strcmp(cmd, "purge"))
		recupera();
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
