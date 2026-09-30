/* AMS - Advanced Messaging System
 * La TUI per gli amministratori: ams senza argomenti in un terminale.
 *
 * Legge l'archivio con le stesse funzioni di ams list e ams status, e ogni
 * azione (invio, ritiro, sollecito, pulizia) è il comando stesso, eseguito in
 * un processo figlio di cui si mostra l'uscita: la TUI non ha un modo suo di
 * fare le cose, e non ha stati suoi (solo inviato, consegnato, confermato;
 * ritirato e scaduto come proprietà). */
#include "ams.h"

#include <errno.h>
#include <fcntl.h>
#include <grp.h>
#include <poll.h>
#include <pwd.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <termios.h>
#include <unistd.h>

#include "lingua.h"

/* ---- terminale ---- */

static int tty = -1, TH, TW;
static struct termios salvato;
static volatile sig_atomic_t fermati;
static bool colore;
static const char *R_ = "", *B_ = "", *D_ = "", *G_ = "", *Y_ = "", *C_ = "", *V_ = "", *VE = "", *GI = "", *RO = "",
		  *GR = "";

static void su_segnale(int s)
{
	(void)s;
	fermati = 1;
}

static void colori(bool si)
{
	colore = si;
	R_ = si ? "\033[0m" : "";
	B_ = si ? "\033[1m" : "";
	D_ = si ? "\033[2m" : "";
	G_ = si ? "\033[1;32m" : "";
	Y_ = si ? "\033[1;33m" : "";
	C_ = si ? "\033[1;36m" : "";
	V_ = si ? "\033[7;1m" : "";
	VE = si ? "\033[32m" : "";
	GI = si ? "\033[33m" : "";
	RO = si ? "\033[31m" : "";
	GR = si ? "\033[90m" : "";
}

static bool dimensioni(int *r, int *c)
{
	struct winsize ws;

	if (ioctl(tty, TIOCGWINSZ, &ws) < 0 || !ws.ws_row || !ws.ws_col)
		return false;
	*r = ws.ws_row;
	*c = ws.ws_col;
	return true;
}

static void modo_tui(void)
{
	struct termios t = salvato;
	static const char inizio[] = "\033[?1049h\033[?25l";

	/* senza eco né modo canonico; senza IXON Ctrl+S arriva alla TUI */
	t.c_lflag &= ~(tcflag_t)(ECHO | ICANON);
	t.c_iflag &= ~(tcflag_t)(IXON | ICRNL);
	t.c_cc[VMIN] = 1;
	t.c_cc[VTIME] = 0;
	tcsetattr(tty, TCSAFLUSH, &t);
	scrivi_tutto(1, inizio, sizeof inizio - 1);
}

static void modo_normale(void)
{
	static const char fine[] = "\033[?25h\033[?1049l";

	tcsetattr(tty, TCSAFLUSH, &salvato);
	scrivi_tutto(1, fine, sizeof fine - 1);
}

/* ---- testo con colori: lunghezze visibili ---- */

static int visibili(const char *s)
{
	int n = 0;

	while (*s) {
		if (*s == '\033' && s[1] == '[') {
			s += 2;
			while (*s && !((*s >= 'A' && *s <= 'Z') || (*s >= 'a' && *s <= 'z')))
				s++;
			if (*s)
				s++;
			continue;
		}
		if (((unsigned char)*s & 0xc0) != 0x80)
			n++;
		s++;
	}
	return n;
}

/* Aggiunge s tagliato o riempito a w caratteri visibili (i colori restano). */
static void colonna(buf_t *out, const char *s, int w)
{
	int n = 0;
	bool taglio = false;

	while (*s) {
		if (*s == '\033' && s[1] == '[') {
			const char *e = s + 2;

			while (*e && !((*e >= 'A' && *e <= 'Z') || (*e >= 'a' && *e <= 'z')))
				e++;
			if (*e)
				e++;
			buf_add(out, s, (size_t)(e - s));
			s = e;
			continue;
		}
		if (((unsigned char)*s & 0xc0) != 0x80) {
			if (n == w) {
				taglio = true;
				break;
			}
			n++;
		}
		buf_addc(out, *s++);
	}
	if (taglio || colore)
		buf_adds(out, R_);
	for (; n < w; n++)
		buf_addc(out, ' ');
}

/* ---- la cornice ---- */

typedef struct {
	strv_t righe; /* righe del contenuto, con colori */
	char *titolo, *destra, *tasti;
	int cur_r, cur_c; /* cursore da mostrare (0: nascosto) */
} schermo_t;

static void schermo_riga(schermo_t *s, const char *fmt, ...) ATTR_PRINTF(2, 3);
static void schermo_riga(schermo_t *s, const char *fmt, ...)
{
	buf_t b = {0};
	va_list ap;

	va_start(ap, fmt);
	buf_vprintf(&b, fmt, ap);
	va_end(ap);
	strv_add_own(&s->righe, b.s ? b.s : xstrdup(""));
}

static void ripeti(buf_t *out, const char *c, int n)
{
	for (int i = 0; i < n; i++)
		buf_adds(out, c);
}

static void disegna(schermo_t *s)
{
	buf_t o = {0};
	int interno = TW - 4, area = TH - 4;
	char *t = xasprintf("─ %s ", s->titolo ? s->titolo : ""), *d = s->destra ? xasprintf(" %s ─", s->destra) : xstrdup("");
	int resto = TW - 2 - visibili(t) - visibili(d);

	buf_adds(&o, "\033[H");
	buf_printf(&o, "%s┌%s%s%s%s%s", D_, R_, C_, t, R_, D_);
	ripeti(&o, "─", resto > 0 ? resto : 0);
	buf_printf(&o, "%s%s%s┐%s\n", R_, GR, d, D_);
	buf_adds(&o, R_);
	for (int i = 0; i < area; i++) {
		buf_printf(&o, "%s│%s ", D_, R_);
		colonna(&o, i < (int)s->righe.n ? s->righe.v[i] : "", interno);
		buf_printf(&o, " %s│%s\n", D_, R_);
	}
	buf_printf(&o, "%s├", D_);
	ripeti(&o, "─", TW - 2);
	buf_printf(&o, "┤%s\n%s│%s ", R_, D_, R_);
	colonna(&o, s->tasti ? s->tasti : "", interno);
	buf_printf(&o, " %s│%s\n%s└", D_, R_, D_);
	ripeti(&o, "─", TW - 2);
	buf_printf(&o, "┘%s\033[J", R_);
	if (s->cur_r > 0)
		buf_printf(&o, "\033[%d;%dH\033[?25h", s->cur_r + 1, s->cur_c + 3);
	else
		buf_adds(&o, "\033[?25l");
	scrivi_tutto(1, o.s, o.n);
	buf_free(&o);
	free(t);
	free(d);
}

static void schermo_libera(schermo_t *s)
{
	strv_free(&s->righe);
	free(s->titolo);
	free(s->destra);
	free(s->tasti);
	memset(s, 0, sizeof *s);
}

/* ---- tasti ---- */

enum {
	K_NULLA = 0, K_TEMPO, K_FINE, K_SU, K_GIU, K_DX, K_SX, K_PGSU, K_PGGIU, K_INIZIO, K_FINERIGA, K_INVIO, K_ESC,
	K_TAB, K_STAB, K_INDIETRO, K_CANC, K_CTRL_E, K_CTRL_S, K_TESTO
};

static int byte_tty(int ms)
{
	unsigned char c;
	struct pollfd p = {.fd = tty, .events = POLLIN};
	int r = poll(&p, 1, ms);

	if (r == 0)
		return -1;
	if (r < 0)
		return errno == EINTR ? -1 : -2;
	if (read(tty, &c, 1) != 1)
		return -2;
	return c;
}

/* Un tasto; per K_TESTO il carattere (UTF-8) in car. */
static int tasto(int ms, char car[8])
{
	int c = byte_tty(ms), d, e;

	car[0] = '\0';
	if (c == -1)
		return K_TEMPO;
	if (c == -2)
		return K_FINE;
	if (c == 27) {
		d = byte_tty(40);
		if (d < 0)
			return K_ESC;
		if (d != '[' && d != 'O')
			return K_NULLA;
		e = byte_tty(40);
		switch (e) {
		case 'A': return K_SU;
		case 'B': return K_GIU;
		case 'C': return K_DX;
		case 'D': return K_SX;
		case 'H': return K_INIZIO;
		case 'F': return K_FINERIGA;
		case 'Z': return K_STAB;
		default: break;
		}
		if (d == '[' && e >= '0' && e <= '9') {
			int x;

			while ((x = byte_tty(40)) >= 0 && x != '~')
				;
			switch (e) {
			case '5': return K_PGSU;
			case '6': return K_PGGIU;
			case '3': return K_CANC;
			case '1': case '7': return K_INIZIO;
			case '4': case '8': return K_FINERIGA;
			default: return K_NULLA;
			}
		}
		return K_NULLA;
	}
	switch (c) {
	case '\r': case '\n': return K_INVIO;
	case '\t': return K_TAB;
	case 127: case 8: return K_INDIETRO;
	case 5: return K_CTRL_E;
	case 19: return K_CTRL_S;
	default: break;
	}
	if (c < 32)
		return K_NULLA;
	car[0] = (char)c;
	{
		int n = c >= 0xf0 ? 3 : c >= 0xe0 ? 2 : c >= 0xc0 ? 1 : 0;

		for (int i = 1; i <= n; i++) {
			int x = byte_tty(40);

			if (x < 0)
				break;
			car[i] = (char)x;
			car[i + 1] = '\0';
		}
		car[n + 1] = '\0';
	}
	return K_TESTO;
}

/* ---- comandi in un processo figlio ---- */

typedef struct {
	int argc;
	char **argv;
	const char *arg;
	void (*uno)(const char *);
} lancio_t;

/* Esegue il comando in un figlio, con stdin (se c'è) e con l'uscita, anche
 * d'errore, raccolta in out. Esito: 0 riuscito, altrimenti il codice. */
static int esegui(const lancio_t *l, const buf_t *in, buf_t *out)
{
	int pin[2], pout[2], stato;
	pid_t pid;

	if (pipe2(pin, O_CLOEXEC) < 0)
		return -1;
	if (pipe2(pout, O_CLOEXEC) < 0) {
		close(pin[0]);
		close(pin[1]);
		return -1;
	}
	fflush(stdout);
	pid = fork();
	if (pid < 0) {
		close(pin[0]);
		close(pin[1]);
		close(pout[0]);
		close(pout[1]);
		return -1;
	}
	if (pid == 0) {
		signal(SIGINT, SIG_DFL);
		signal(SIGPIPE, SIG_DFL);
		/* le parti delle pipe che usa il padre: aperte qui, il comando non
		 * vedrebbe mai la fine del testo */
		close(pin[1]);
		close(pout[0]);
		dup2(pin[0], 0);
		dup2(pout[1], 1);
		dup2(pout[1], 2);
		if (l->uno)
			l->uno(l->arg);
		else
			cmd_send(l->argc, l->argv);
		fflush(stdout);
		fflush(stderr);
		_exit(0);
	}
	close(pin[0]);
	close(pout[1]);
	if (in && in->n)
		scrivi_tutto(pin[1], in->s, in->n);
	close(pin[1]);
	leggi_fd(pout[0], 1 << 20, out);
	close(pout[0]);
	while (waitpid(pid, &stato, 0) < 0)
		if (errno != EINTR)
			return -1;
	return WIFEXITED(stato) ? WEXITSTATUS(stato) : -1;
}

/* ---- dati ---- */

typedef struct {
	riassunto_t *v;
	size_t n;
	char ora[16];
} elenco_t;

static void elenco_libera(elenco_t *e)
{
	for (size_t i = 0; i < e->n; i++)
		riassunto_libera(&e->v[i]);
	free(e->v);
	e->v = NULL;
	e->n = 0;
}

static bool contiene(const char *testo, const char *cerca)
{
	size_t n = strlen(cerca);

	if (!n)
		return true;
	for (const char *p = testo; *p; p++)
		if (!strncasecmp(p, cerca, n))
			return true;
	return false;
}

/* I messaggi, dal più recente; con un filtro, solo quelli che lo contengono. */
static void carica_elenco(elenco_t *e, const char *filtro)
{
	strv_t ids = {0};
	time_t ora = adesso();
	struct tm tm;

	elenco_libera(e);
	caselle_svuota();
	elenco_messaggi(&ids);
	e->v = xmalloc((ids.n ? ids.n : 1) * sizeof *e->v);
	for (size_t i = ids.n; i-- > 0;) {
		long long id;

		leggi_numero(ids.v[i], &id);
		if (!riassumi(id, &e->v[e->n]))
			continue;
		if (!contiene(e->v[e->n].m.body, filtro) && !contiene(e->v[e->n].m.title, filtro)) {
			riassunto_libera(&e->v[e->n]);
			continue;
		}
		e->n++;
	}
	strv_free(&ids);
	localtime_r(&ora, &tm);
	strftime(e->ora, sizeof e->ora, "%H:%M:%S", &tm);
}

/* Barra di w segni: confermato █ verde, consegnato ▒ giallo, inviato ░ rosso. */
static void barra(buf_t *o, const riassunto_t *r, int w)
{
	int tot = r->confermato + r->consegnato + r->inviato, a, c, b;

	if (tot <= 0)
		tot = 1;
	a = r->confermato * w / tot;
	c = r->inviato * w / tot;
	if (r->inviato && !c)
		c = 1;
	if (r->consegnato && a + c == w && a > 0)
		a--;
	b = w - a - c;
	buf_adds(o, VE);
	ripeti(o, "█", a);
	buf_adds(o, GI);
	ripeti(o, "▒", b);
	buf_adds(o, RO);
	ripeti(o, "░", c);
	buf_adds(o, R_);
}

static void frase_colorata(buf_t *o, const riassunto_t *r)
{
	const char *sep = "";

	if (!r->consegnato && !r->inviato) {
		buf_adds(o, VE);
		buf_printf(o, T("all confirmed (%d)"), r->confermato);
		buf_adds(o, R_);
		return;
	}
	if (r->confermato) {
		buf_adds(o, VE);
		buf_printf(o, T("%d confirmed"), r->confermato);
		buf_adds(o, R_);
		sep = " · ";
	}
	if (r->consegnato) {
		buf_printf(o, "%s%s", sep, GI);
		buf_printf(o, T("%d delivered"), r->consegnato);
		buf_adds(o, R_);
		sep = " · ";
	}
	if (r->inviato) {
		buf_printf(o, "%s%s", sep, RO);
		buf_printf(o, T("%d sent"), r->inviato);
		buf_adds(o, R_);
	}
}

static void legenda(buf_t *o)
{
	buf_printf(o, "%s█%s ", VE, R_);
	buf_adds(o, T("confirmed"));
	buf_printf(o, "   %s▒%s ", GI, R_);
	buf_adds(o, T("delivered"));
	buf_printf(o, "   %s░%s ", RO, R_);
	buf_adds(o, T("sent"));
}

/* ---- sovrapposizioni: conferma, messaggio, domanda ---- */

/* Disegna una finestra al centro dello schermo sopra quello che c'è. */
static void finestra(schermo_t *s, const char *titolo, const strv_t *testo, const char *pulsanti)
{
	int w = 60, h = (int)testo->n + 5, x, y;
	strv_t *r = &s->righe;
	buf_t riga = {0};

	for (size_t i = 0; i < testo->n; i++)
		if (visibili(testo->v[i]) + 6 > w)
			w = visibili(testo->v[i]) + 6;
	if (w > TW - 8)
		w = TW - 8;
	x = (TW - 4 - w) / 2;
	y = (TH - 4 - h) / 2;
	if (y < 1)
		y = 1;
	while ((int)r->n < y + h)
		strv_add(r, "");
	for (int i = 0; i < h; i++) {
		buf_clear(&riga);
		buf_printf(&riga, "%*s", x, "");
		if (i == 0) {
			char *t = xasprintf("─ %s ", titolo);

			buf_printf(&riga, "%s┌%s", B_, t);
			ripeti(&riga, "─", w - 2 - visibili(t));
			buf_printf(&riga, "┐%s", R_);
			free(t);
		} else if (i == h - 1) {
			buf_printf(&riga, "%s└", B_);
			ripeti(&riga, "─", w - 2);
			buf_printf(&riga, "┘%s", R_);
		} else {
			const char *c = i >= 2 && i - 2 < (int)testo->n ? testo->v[i - 2] : i == h - 2 ? pulsanti : "";

			buf_printf(&riga, "%s│%s  ", B_, R_);
			colonna(&riga, c, w - 6);
			buf_printf(&riga, "  %s│%s", B_, R_);
		}
		free(r->v[y + i]);
		r->v[y + i] = xstrdup(riga.s);
	}
	buf_free(&riga);
}

/* Disegna una finestra sopra lo schermo di base, lasciando la base intatta:
 * una finestra successiva non si sovrappone a quella di prima. */
static void sovrapponi(const schermo_t *base, const char *titolo, const strv_t *testo, const char *pulsanti,
		       char *tasti)
{
	schermo_t s = {0};

	for (size_t i = 0; i < base->righe.n; i++)
		strv_add(&s.righe, base->righe.v[i]);
	s.titolo = xstrdup(base->titolo ? base->titolo : "");
	s.destra = base->destra ? xstrdup(base->destra) : NULL;
	s.tasti = tasti;
	finestra(&s, titolo, testo, pulsanti);
	disegna(&s);
	schermo_libera(&s);
}

/* Chiede una conferma sopra lo schermo; true se l'amministratore conferma. */
static bool conferma(schermo_t *s, const char *titolo, const strv_t *testo)
{
	char car[8];
	char *p = xasprintf("%s s  %s %s     %s n  %s %s", V_, T("Confirm"), R_, D_, T("Cancel"), R_);

	sovrapponi(s, titolo, testo, p,
		   xasprintf("%ss%s %s   %sn%s %s %sEsc%s %s", G_, R_, T("confirm"), G_, R_, T("or"), G_, R_, T("cancel")));
	free(p);
	for (;;) {
		int k = tasto(500, car);

		if (fermati || k == K_FINE || k == K_ESC || (k == K_TESTO && (car[0] == 'n' || car[0] == 'N')))
			return false;
		if (k == K_TESTO && (car[0] == 's' || car[0] == 'S' || car[0] == 'y' || car[0] == 'Y'))
			return true;
	}
}

/* Mostra l'esito di un comando finché non si preme un tasto. */
static void esito(schermo_t *s, const char *titolo, const buf_t *uscita)
{
	strv_t righe = {0};
	char car[8];
	buf_t pulito = {0};

	pulisci(uscita->s ? uscita->s : "", uscita->n, &pulito);
	for (char *p = pulito.s; p && *p;) {
		size_t len = strcspn(p, "\n");
		char *r = xmalloc(len + 1);

		memcpy(r, p, len);
		r[len] = '\0';
		strv_add_own(&righe, r);
		p += len;
		if (*p)
			p++;
	}
	if (!righe.n)
		strv_add(&righe, T("Done."));
	sovrapponi(s, titolo, &righe, T("any key to continue"), xstrdup(T("any key to continue")));
	while (tasto(500, car) == K_TEMPO && !fermati)
		;
	strv_free(&righe);
	buf_free(&pulito);
}

/* Una riga di testo chiesta sopra lo schermo; NULL se annullata. */
static char *domanda(schermo_t *base, const char *titolo, const char *spiegazione, const char *iniziale)
{
	buf_t v = {0};
	char car[8];

	buf_adds(&v, iniziale);
	for (;;) {
		schermo_t s = {0};
		strv_t t = {0};
		char *campo;
		int k;

		for (size_t i = 0; i < base->righe.n; i++)
			strv_add(&s.righe, base->righe.v[i]);
		s.titolo = xstrdup(base->titolo);
		s.destra = base->destra ? xstrdup(base->destra) : NULL;
		strv_add(&t, spiegazione);
		strv_add(&t, "");
		campo = xasprintf("[ %s%s ]", v.s ? v.s : "", colore ? "\033[7m \033[0m" : "_");
		strv_add_own(&t, campo);
		finestra(&s, titolo, &t, "");
		s.tasti = xasprintf("%sInvio%s %s   %sEsc%s %s", G_, R_, T("confirm"), G_, R_, T("cancel"));
		disegna(&s);
		schermo_libera(&s);
		strv_free(&t);
		k = tasto(500, car);
		if (fermati || k == K_FINE || k == K_ESC) {
			buf_free(&v);
			return NULL;
		}
		if (k == K_INVIO)
			return v.s ? v.s : xstrdup("");
		if (k == K_INDIETRO && v.n) {
			do
				v.n--;
			while (v.n && ((unsigned char)v.s[v.n] & 0xc0) == 0x80);
			v.s[v.n] = '\0';
		} else if (k == K_TESTO && v.n < 200) {
			buf_adds(&v, car);
		}
	}
}

/* ---- azioni ---- */

static void azione(schermo_t *s, const char *titolo, void (*fn)(const char *), const char *arg)
{
	lancio_t l = {.uno = fn, .arg = arg};
	buf_t out = {0};

	esegui(&l, NULL, &out);
	esito(s, titolo, &out);
	buf_free(&out);
}

static void ritira(schermo_t *s, const riassunto_t *r)
{
	strv_t t = {0};
	char *id = xasprintf("%lld", r->id), *titolo = xasprintf(T("Revoke message %lld?"), r->id);
	buf_t b = {0};

	buf_printf(&b, "«%s» · ", *r->m.title ? r->m.title : T("no title"));
	riassunto_frase(r, &b);
	strv_add(&t, b.s);
	strv_add(&t, "");
	strv_add(&t, T("Whoever has not seen it yet will not see it;"));
	strv_add(&t, T("open dialogs and questions close by themselves."));
	if (conferma(s, titolo, &t))
		azione(s, titolo, cmd_revoke, id);
	strv_free(&t);
	buf_free(&b);
	free(id);
	free(titolo);
}

static void sollecita(schermo_t *s, const riassunto_t *r)
{
	strv_t t = {0};
	char *id = xasprintf("%lld", r->id), *titolo = xasprintf(T("Remind message %lld?"), r->id);
	char *riga = r->consegnato == 1 ? xstrdup(T("1 recipient has not confirmed yet."))
					: xasprintf(T("%d recipients have not confirmed yet."), r->consegnato);

	strv_add(&t, riga);
	strv_add(&t, "");
	strv_add(&t, T("They are asked again now: at the next prompt"));
	strv_add(&t, T("and with the dialog on the desktop."));
	if (conferma(s, titolo, &t))
		azione(s, titolo, cmd_remind, id);
	strv_free(&t);
	free(id);
	free(titolo);
	free(riga);
}

static void pulizia(schermo_t *s)
{
	char *dur = domanda(s, T("Delete old messages"), T("Delete the messages sent more than (for example 90d, 12h):"),
			    "90d");
	strv_t t = {0};
	char *riga;

	if (!dur)
		return;
	riga = xasprintf(T("Messages older than %s, with copies and confirmations."), dur);
	strv_add(&t, riga);
	strv_add(&t, T("The events stay in the system log."));
	if (conferma(s, T("Delete old messages?"), &t))
		azione(s, T("Delete old messages"), cmd_purge, dur);
	strv_free(&t);
	free(riga);
	free(dur);
}

/* ---- la lista ---- */

static void tasti_lista(schermo_t *s)
{
	s->tasti = xasprintf("%sInvio%s %s   %sn%s %s   %sr%s %s   %ss%s %s   %sp%s %s   %s/%s %s   %s?%s %s   %sq%s %s",
			     G_, R_, T("open"), G_, R_, T("new"), G_, R_, T("revoke"), G_, R_, T("remind"), G_, R_, T("purge"),
			     G_, R_, T("search"), G_, R_, T("keys"), G_, R_, T("quit"));
}

static void righe_lista(schermo_t *s, const elenco_t *e, size_t sel, size_t primo, const char *filtro)
{
	int interno = TW - 4, fw = interno >= 106 ? 42 : 0, bw = 12;
	int tw = interno - (1 + 3 + 2 + 11 + 2) - (bw + 2) - (fw ? fw + 2 : 7);
	int area = TH - 4 - 3;
	buf_t b = {0};

	if (tw < 10)
		tw = 10;
	schermo_riga(s, "%s", "");
	buf_printf(&b, " %s%3s  %-11s  ", Y_, T("ID"), T("DATE"));
	colonna(&b, T("MESSAGE"), tw);
	buf_printf(&b, "  %s%s", T("RECIPIENTS"), R_);
	strv_add(&s->righe, b.s);
	buf_clear(&b);
	if (!e->n)
		schermo_riga(s, "   %s%s%s", GR, *filtro ? T("No message contains the search text.") : T("No messages sent."), R_);
	for (size_t i = primo; i < e->n && (int)(i - primo) < area; i++) {
		const riassunto_t *r = &e->v[i];
		char data[32], id[24];
		buf_t t = {0}, f = {0};

		data_breve((time_t)r->m.date, data);
		snprintf(id, sizeof id, "%lld", r->id);
		if (r->ritirato)
			buf_printf(&t, "%s%s%s", GR, T("[revoked] "), R_);
		if (r->scaduto)
			buf_printf(&t, "%s%s%s", GR, T("[expired] "), R_);
		if (*r->m.title)
			buf_printf(&t, "%s%s%s · ", B_, r->m.title, R_);
		buf_add(&t, r->m.body, strcspn(r->m.body, "\n"));
		buf_printf(&b, "%s%3s  %-11s  ", i == sel ? ">" : " ", id, data);
		colonna(&b, t.s, tw);
		buf_adds(&b, "  ");
		barra(&b, r, bw);
		buf_adds(&b, "  ");
		if (fw)
			frase_colorata(&f, r);
		else
			buf_printf(&f, "%d/%d", r->confermato, r->confermato + r->consegnato + r->inviato);
		buf_adds(&b, f.s);
		if (i == sel && colore) {
			/* la riga scelta, in negativo e senza gli altri colori */
			buf_t pulita = {0}, c = {0};

			for (const char *p = b.s; *p;) {
				if (*p == '\033') {
					while (*p && *p != 'm')
						p++;
					if (*p)
						p++;
					continue;
				}
				buf_addc(&pulita, *p++);
			}
			buf_adds(&c, V_);
			colonna(&c, pulita.s, interno);
			strv_add(&s->righe, c.s);
			buf_free(&pulita);
			buf_free(&c);
		} else {
			strv_add(&s->righe, b.s);
		}
		buf_clear(&b);
		buf_free(&t);
		buf_free(&f);
	}
	while ((int)s->righe.n < TH - 5)
		strv_add(&s->righe, "");
	legenda(&b);
	if (*filtro) {
		buf_printf(&b, "      %s", GR);
		buf_printf(&b, T("search: «%s» (Esc to clear)"), filtro);
		buf_adds(&b, R_);
	}
	strv_add(&s->righe, b.s);
	buf_free(&b);
}

/* ---- il dettaglio ---- */

static void a_capo(const char *testo, int w, strv_t *out)
{
	for (const char *p = testo; *p;) {
		size_t len = strcspn(p, "\n");
		buf_t riga = {0};

		buf_add(&riga, p, len);
		/* righe lunghe: a capo sugli spazi */
		while (visibili(riga.s) > w) {
			size_t taglio = 0, c = 0;

			for (size_t k = 0; k < riga.n && (int)c <= w; k++) {
				if (((unsigned char)riga.s[k] & 0xc0) != 0x80)
					c++;
				if (riga.s[k] == ' ' && (int)c <= w)
					taglio = k;
			}
			if (!taglio)
				for (size_t k = 0, cc = 0; k < riga.n; k++)
					if (((unsigned char)riga.s[k] & 0xc0) != 0x80 && (int)++cc > w) {
						taglio = k;
						break;
					}
			{
				char *a = xmalloc(taglio + 1);

				memcpy(a, riga.s, taglio);
				a[taglio] = '\0';
				strv_add_own(out, a);
			}
			{
				buf_t resto = {0};

				buf_adds(&resto, riga.s + taglio + (riga.s[taglio] == ' '));
				buf_free(&riga);
				riga = resto;
			}
		}
		strv_add(out, riga.s ? riga.s : "");
		buf_free(&riga);
		p += len;
		if (*p)
			p++;
	}
}

static void storia(long long id, strv_t *out)
{
	char *arg = xasprintf("%lld", id);
	lancio_t l = {.uno = cmd_log, .arg = arg};
	buf_t o = {0}, p = {0};
	bool prima = true;

	esegui(&l, NULL, &o);
	pulisci(o.s ? o.s : "", o.n, &p);
	for (char *r = p.s; r && *r;) {
		size_t len = strcspn(r, "\n");

		if (!prima) {
			char *x = xmalloc(len + 1);

			memcpy(x, r, len);
			x[len] = '\0';
			strv_add_own(out, x);
		}
		prima = false;
		r += len;
		if (*r)
			r++;
	}
	free(arg);
	buf_free(&o);
	buf_free(&p);
}

/* Il dettaglio di un messaggio: destinatari e storia. Si rilegge ogni 3
 * secondi e dopo ogni azione; si esce con Esc. */
static void dettaglio(long long id, const char *ora_elenco)
{
	int scheda = 0, scorri = 0, giri = 0;
	char car[8], ora[16];
	bool leggi = true, esci = false;
	riassunto_t r = {0};
	destinatari_t d = {0};
	strv_t corpo = {0}, sto = {0};

	snprintf(ora, sizeof ora, "%s", ora_elenco);
	while (!esci && !fermati) {
		schermo_t s = {0};
		char data[32], scad[32];
		buf_t b = {0};
		int area, k, righe;

		if (leggi) {
			riassunto_libera(&r);
			destinatari_libera(&d);
			strv_free(&corpo);
			strv_free(&sto);
			caselle_svuota();
			if (!riassumi(id, &r))
				break;
			destinatari(id, &r.m, &d);
			a_capo(r.m.body, TW - 8, &corpo);
			if (scheda == 1)
				storia(id, &sto);
			leggi = false;
		}
		s.titolo = *r.m.title ? xasprintf(T("Message %lld · %s"), id, r.m.title) : xasprintf(T("Message %lld"), id);
		s.destra = xasprintf(T("updated at %s"), ora);
		data_breve((time_t)r.m.date, data);
		buf_printf(&b, " %s%s%s · %s · ", B_, *r.m.title ? r.m.title : T("no title"), R_, data);
		buf_printf(&b, T("from %s"), r.m.from);
		if (r.m.expires) {
			data_breve((time_t)r.m.expires, scad);
			buf_adds(&b, " · ");
			buf_printf(&b, r.scaduto ? T("expired on %s") : T("expires on %s"), scad);
		}
		if (r.ritirato) {
			data_breve((time_t)data_ritiro(id), scad);
			buf_printf(&b, " · %s", RO);
			buf_printf(&b, T("revoked on %s"), scad);
			buf_adds(&b, R_);
		}
		strv_add(&s.righe, b.s);
		buf_clear(&b);
		for (size_t i = 0; i < corpo.n && i < 6; i++)
			schermo_riga(&s, " %s│%s %s", D_, R_, i == 5 && corpo.n > 6 ? "…" : corpo.v[i]);
		schermo_riga(&s, "%s", "");
		{
			char *td = xasprintf(" %s (%zu) ", T("Recipients"), d.n), *ts = xasprintf(" %s ", T("History"));

			buf_printf(&b, " %s%s%s %s%s%s    ", scheda == 0 ? V_ : D_, td, R_, scheda == 1 ? V_ : D_, ts, R_);
			barra(&b, &r, 12);
			buf_adds(&b, "  ");
			frase_colorata(&b, &r);
			strv_add(&s.righe, b.s);
			buf_clear(&b);
			free(td);
			free(ts);
		}
		schermo_riga(&s, "%s", "");
		area = TH - 4 - (int)s.righe.n;
		if (scheda == 0) {
			buf_t u = {0};

			righe = (int)d.n;
			buf_adds(&b, Y_);
			colonna(&b, T("USER"), 14);
			buf_printf(&b, "%s%s", T("STATE"), R_);
			schermo_riga(&s, " %s", b.s);
			buf_clear(&b);
			buf_free(&u);
			area--;
		} else {
			righe = (int)sto.n;
		}
		if (scorri > righe - area)
			scorri = righe - area;
		if (scorri < 0)
			scorri = 0;
		for (int i = scorri; i < righe && i - scorri < area; i++) {
			if (scheda == 0) {
				const char *col = d.v[i].stato == CONFERMATO ? VE : d.v[i].stato == CONSEGNATO ? GI : RO;
				buf_t u = {0};

				colonna(&u, d.v[i].utente, 13);
				schermo_riga(&s, " %s %s%s%s", u.s, col, d.v[i].riga, R_);
				buf_free(&u);
			} else {
				schermo_riga(&s, " %s", sto.v[i]);
			}
		}
		if (scheda == 1 && !sto.n)
			schermo_riga(&s, " %s%s%s", GR, T("No events in the system log."), R_);
		s.tasti = xasprintf("%sTab%s %s   %s↑/↓%s %s   %ss%s %s   %sr%s %s   %sEsc%s %s", G_, R_, T("recipients/history"),
				    G_, R_, T("scroll"), G_, R_, T("remind"), G_, R_, T("revoke"), G_, R_, T("back"));
		disegna(&s);
		k = tasto(500, car);
		if (k == K_TEMPO) {
			int r2, c2;

			if (dimensioni(&r2, &c2) && (r2 != TH || c2 != TW)) {
				TH = r2;
				TW = c2;
				leggi = true;
			}
			/* aggiornamento automatico ogni 3 secondi */
			if (++giri >= 6) {
				time_t t = adesso();
				struct tm tm;

				giri = 0;
				localtime_r(&t, &tm);
				strftime(ora, sizeof ora, "%H:%M:%S", &tm);
				leggi = true;
			}
		} else if (k == K_FINE || k == K_ESC || (k == K_TESTO && car[0] == 'q')) {
			esci = true;
		} else if (k == K_TAB || k == K_STAB) {
			scheda = 1 - scheda;
			scorri = 0;
			leggi = true;
		} else if (k == K_SU) {
			scorri--;
		} else if (k == K_GIU) {
			scorri++;
		} else if (k == K_PGSU) {
			scorri -= area;
		} else if (k == K_PGGIU) {
			scorri += area;
		} else if (k == K_TESTO && car[0] == 'r' && !r.ritirato) {
			ritira(&s, &r);
			leggi = true;
		} else if (k == K_TESTO && car[0] == 's' && !r.ritirato && !r.scaduto && r.consegnato) {
			sollecita(&s, &r);
			leggi = true;
		}
		schermo_libera(&s);
		buf_free(&b);
	}
	riassunto_libera(&r);
	destinatari_libera(&d);
	strv_free(&corpo);
	strv_free(&sto);
}

/* ---- nuovo messaggio ---- */

typedef struct {
	buf_t campo[3]; /* A, titolo, scadenza */
	strv_t testo;   /* righe del testo */
	int attivo;     /* 0-2 campi, 3 testo */
	size_t pos;     /* cursore nel campo (byte) */
	size_t riga, col; /* cursore nel testo (riga, byte) */
	char *anteprima_a, *anteprima_scad;
} modulo_t;

static void modulo_libera(modulo_t *m)
{
	for (int i = 0; i < 3; i++)
		buf_free(&m->campo[i]);
	strv_free(&m->testo);
	free(m->anteprima_a);
	free(m->anteprima_scad);
}

static void modulo_testo(const modulo_t *m, buf_t *out)
{
	for (size_t i = 0; i < m->testo.n; i++)
		buf_printf(out, "%s%s", i ? "\n" : "", m->testo.v[i]);
}

static void testo_da(modulo_t *m, const char *s)
{
	strv_free(&m->testo);
	for (const char *p = s;;) {
		size_t len = strcspn(p, "\n");
		char *r = xmalloc(len + 1);

		memcpy(r, p, len);
		r[len] = '\0';
		strv_add_own(&m->testo, r);
		p += len;
		if (!*p)
			break;
		p++;
	}
	/* niente righe vuote finali in più */
	while (m->testo.n > 1 && !*m->testo.v[m->testo.n - 1]) {
		free(m->testo.v[--m->testo.n]);
	}
	m->riga = m->testo.n - 1;
	m->col = strlen(m->testo.v[m->riga]);
}

/* Un passo indietro o avanti di un carattere UTF-8 in s. */
static size_t car_prima(const char *s, size_t i)
{
	if (!i)
		return 0;
	do
		i--;
	while (i && ((unsigned char)s[i] & 0xc0) == 0x80);
	return i;
}

static size_t car_dopo(const char *s, size_t i)
{
	if (!s[i])
		return i;
	do
		i++;
	while (s[i] && ((unsigned char)s[i] & 0xc0) == 0x80);
	return i;
}

static void anteprime(modulo_t *m)
{
	lancio_t l;
	buf_t o = {0};

	free(m->anteprima_a);
	m->anteprima_a = NULL;
	if (m->campo[0].n) {
		l = (lancio_t){.uno = cmd_conta_destinatari, .arg = m->campo[0].s};
		if (esegui(&l, NULL, &o) == 0 && o.s) {
			long long n = 0;

			o.s[strcspn(o.s, "\n")] = '\0';
			leggi_numero(o.s, &n);
			m->anteprima_a = n == 1 ? xstrdup(T("1 recipient")) : xasprintf(T("%lld recipients"), n);
		} else if (o.s) {
			buf_t p = {0};

			pulisci(o.s, o.n, &p);
			p.s[strcspn(p.s, "\n")] = '\0';
			m->anteprima_a = xasprintf("%s%s%s", RO, p.s, R_);
			buf_free(&p);
		}
	}
	buf_free(&o);
}

/* Apre il testo nell'editor di chi usa ams (SUDO_USER), fuori dalla TUI. */
static void editor(modulo_t *m)
{
	char path[] = "/tmp/ams-testo-XXXXXX";
	int fd = mkstemp(path);
	buf_t t = {0};
	const char *chi = getenv("SUDO_USER");
	struct passwd *pw = chi && *chi ? getpwnam(chi) : NULL;
	pid_t pid;

	if (fd < 0)
		return;
	modulo_testo(m, &t);
	buf_addc(&t, '\n');
	scrivi_tutto(fd, t.s, t.n);
	/* il file è dell'amministratore, che lo apre con il suo editor */
	if (pw && geteuid() == 0 && fchown(fd, pw->pw_uid, pw->pw_gid) < 0)
		pw = NULL;
	close(fd);
	buf_free(&t);
	modo_normale();
	pid = fork();
	if (pid == 0) {
		const char *ed = getenv("VISUAL");

		if (!ed || !*ed)
			ed = getenv("EDITOR");
		signal(SIGINT, SIG_DFL);
		/* l'editor gira con l'identità dell'amministratore, non come root */
		if (pw && geteuid() == 0 &&
		    (initgroups(pw->pw_name, pw->pw_gid) < 0 || setresgid(pw->pw_gid, pw->pw_gid, pw->pw_gid) < 0 ||
		     setresuid(pw->pw_uid, pw->pw_uid, pw->pw_uid) < 0))
			_exit(126);
		if (ed && *ed)
			execl("/bin/sh", "sh", "-c", "exec $0 \"$1\"", ed, path, (char *)NULL);
		execlp("nano", "nano", path, (char *)NULL);
		execlp("vi", "vi", path, (char *)NULL);
		_exit(127);
	}
	if (pid > 0)
		while (waitpid(pid, NULL, 0) < 0 && errno == EINTR)
			;
	{
		buf_t b = {0};

		if (leggi_file(path, (size_t)AMS_MAX_BYTES * 2, true, &b) == 0) {
			while (b.n && b.s[b.n - 1] == '\n')
				b.s[--b.n] = '\0';
			testo_da(m, b.s ? b.s : "");
		}
		buf_free(&b);
	}
	unlink(path);
	modo_tui();
}

/* Invia: esito true se inviato (e l'ID in *nuovo). */
static bool invia(schermo_t *s, modulo_t *m, long long *nuovo)
{
	strv_t t = {0};
	buf_t testo = {0}, out = {0};
	char *argv[10], *riga;
	int argc = 0, r;
	lancio_t l;
	bool ok = false;

	modulo_testo(m, &testo);
	riga = xasprintf(T("To: %s (%s)"), m->campo[0].s ? m->campo[0].s : "",
			 m->anteprima_a ? m->anteprima_a : "?");
	strv_add_own(&t, riga);
	if (m->campo[1].n)
		strv_add_own(&t, xasprintf(T("Title: %s"), m->campo[1].s));
	if (m->campo[2].n)
		strv_add_own(&t, xasprintf(T("Expires: %s"), m->campo[2].s));
	strv_add_own(&t, xasprintf(T("Text: %zu bytes"), testo.n));
	if (!conferma(s, T("Send the message?"), &t)) {
		strv_free(&t);
		buf_free(&testo);
		return false;
	}
	{
		static char to[] = "--to", title[] = "--title", expires[] = "--expires", vuoto[] = "";

		argv[argc++] = to;
		argv[argc++] = m->campo[0].s ? m->campo[0].s : vuoto;
		if (m->campo[1].n) {
			argv[argc++] = title;
			argv[argc++] = m->campo[1].s;
		}
		if (m->campo[2].n) {
			argv[argc++] = expires;
			argv[argc++] = m->campo[2].s;
		}
	}
	argv[argc] = NULL;
	l = (lancio_t){.argc = argc, .argv = argv};
	r = esegui(&l, &testo, &out);
	esito(s, r == 0 ? T("Message sent") : T("Sending result"), &out);
	if (r == 0) {
		strv_t ids = {0};

		elenco_messaggi(&ids);
		if (ids.n)
			leggi_numero(ids.v[ids.n - 1], nuovo);
		strv_free(&ids);
		ok = true;
	}
	strv_free(&t);
	buf_free(&testo);
	buf_free(&out);
	return ok;
}

static bool nuovo_messaggio(long long *nuovo)
{
	modulo_t m = {0};
	char car[8];
	bool inviato = false;
	static const char *const nomi[] = {N_("To"), N_("Title"), N_("Expires")};
	static const char *const aiuti[] = {N_("user, @group, all or online, separated by commas"),
					    N_("optional, one line"), N_("optional: 30m, 2h, 3d or a date")};

	strv_add(&m.testo, "");
	for (;;) {
		schermo_t s = {0};
		int w = TW - 4 - 14, altezza = TH - 4 - 1 - 3 - 3 - 3, k;
		strv_t vis = {0};
		size_t cur_vis = 0, cur_c = 0;
		buf_t b = {0};

		if (w < 20)
			w = 20;
		if (altezza < 3)
			altezza = 3;
		s.titolo = xstrdup(T("New message"));
		schermo_riga(&s, "%s", "");
		for (int i = 0; i < 3; i++) {
			buf_t v = {0};
			const char *extra = i == 0 && m.anteprima_a ? m.anteprima_a : "";

			colonna(&v, m.campo[i].s ? m.campo[i].s : "", w - 26);
			buf_printf(&b, " %s", i == m.attivo ? B_ : "");
			colonna(&b, T(nomi[i]), 10);
			buf_printf(&b, "%s [ %s ]  %s%s%s", R_, v.s, GR, *extra ? extra : T(aiuti[i]), R_);
			if (i == 0 && *extra)
				buf_printf(&b, "%s", R_);
			strv_add(&s.righe, b.s);
			buf_clear(&b);
			buf_free(&v);
			if (i == m.attivo) {
				size_t c = 0;

				for (size_t k2 = 0; k2 < m.pos; k2++)
					if (((unsigned char)m.campo[i].s[k2] & 0xc0) != 0x80)
						c++;
				s.cur_r = (int)s.righe.n;
				s.cur_c = 1 + 10 + 3 + (int)c;
			}
		}
		/* il testo, a capo alla larghezza del riquadro */
		for (size_t i = 0; i < m.testo.n; i++) {
			strv_t pezzi = {0};
			const char *riga = m.testo.v[i];
			size_t inizio = 0;

			a_capo(*riga ? riga : " ", w - 2, &pezzi);
			for (size_t p = 0; p < pezzi.n; p++) {
				size_t len = strlen(pezzi.v[p]);

				if (i == m.riga && m.col >= inizio && (m.col <= inizio + len || p == pezzi.n - 1)) {
					size_t c = 0;

					for (size_t k2 = inizio; k2 < m.col && k2 < strlen(riga); k2++)
						if (((unsigned char)riga[k2] & 0xc0) != 0x80)
							c++;
					cur_vis = vis.n;
					cur_c = c;
				}
				strv_add(&vis, *riga ? pezzi.v[p] : "");
				inizio += len + 1;
			}
			strv_free(&pezzi);
		}
		{
			size_t primo = cur_vis >= (size_t)altezza ? cur_vis - (size_t)altezza + 1 : 0;

			buf_printf(&b, " %s", m.attivo == 3 ? B_ : "");
			colonna(&b, T("Text"), 10);
			buf_printf(&b, "%s %s┌", R_, D_);
			ripeti(&b, "─", w);
			buf_printf(&b, "┐%s", R_);
			strv_add(&s.righe, b.s);
			buf_clear(&b);
			for (int i = 0; i < altezza; i++) {
				buf_printf(&b, "%*s%s│%s ", 12, "", D_, R_);
				colonna(&b, primo + (size_t)i < vis.n ? vis.v[primo + (size_t)i] : "", w - 2);
				buf_printf(&b, " %s│%s", D_, R_);
				strv_add(&s.righe, b.s);
				buf_clear(&b);
			}
			buf_printf(&b, "%*s%s└", 12, "", D_);
			ripeti(&b, "─", w);
			buf_printf(&b, "┘%s", R_);
			strv_add(&s.righe, b.s);
			buf_clear(&b);
			{
				buf_t t = {0};

				modulo_testo(&m, &t);
				buf_printf(&b, "%*s%s", 12, "", t.n > AMS_MAX_BYTES ? RO : GR);
				buf_printf(&b, T("%zu of %d bytes"), t.n, AMS_MAX_BYTES);
				buf_adds(&b, R_);
				strv_add(&s.righe, b.s);
				buf_clear(&b);
				buf_free(&t);
			}
			if (m.attivo == 3) {
				s.cur_r = 5 + (int)(cur_vis - primo);
				s.cur_c = 14 + (int)cur_c;
			}
		}
		s.tasti = xasprintf("%sTab%s %s   %sCtrl+E%s %s   %sCtrl+S%s %s   %sEsc%s %s", G_, R_, T("next field"), G_, R_,
				    T("open in the editor"), G_, R_, T("send"), G_, R_, T("cancel"));
		disegna(&s);
		strv_free(&vis);
		buf_free(&b);
		k = tasto(500, car);
		if (fermati || k == K_FINE) {
			schermo_libera(&s);
			break;
		}
		if (k == K_ESC) {
			bool vuoto = !m.campo[0].n && !m.campo[1].n && !m.campo[2].n && m.testo.n == 1 && !*m.testo.v[0];
			strv_t t = {0};

			strv_add(&t, T("The message you are writing will be lost."));
			if (vuoto || conferma(&s, T("Discard the message?"), &t)) {
				strv_free(&t);
				schermo_libera(&s);
				break;
			}
			strv_free(&t);
		} else if (k == K_TAB || k == K_STAB) {
			if (m.attivo == 0)
				anteprime(&m);
			m.attivo = (m.attivo + (k == K_TAB ? 1 : 3)) % 4;
			if (m.attivo < 3)
				m.pos = m.campo[m.attivo].n;
		} else if (k == K_CTRL_E) {
			editor(&m);
			m.attivo = 3;
		} else if (k == K_CTRL_S) {
			anteprime(&m);
			if (invia(&s, &m, nuovo)) {
				inviato = true;
				schermo_libera(&s);
				break;
			}
		} else if (m.attivo < 3) {
			buf_t *c = &m.campo[m.attivo];

			if (k == K_TESTO && c->n < 1000) {
				buf_t n = {0};

				buf_add(&n, c->s ? c->s : "", m.pos);
				buf_adds(&n, car);
				buf_adds(&n, c->s ? c->s + m.pos : "");
				m.pos += strlen(car);
				buf_free(c);
				*c = n;
			} else if (k == K_INDIETRO && m.pos) {
				size_t p = car_prima(c->s, m.pos);

				memmove(c->s + p, c->s + m.pos, c->n - m.pos + 1);
				c->n -= m.pos - p;
				m.pos = p;
			} else if (k == K_CANC && m.pos < c->n) {
				size_t p = car_dopo(c->s, m.pos);

				memmove(c->s + m.pos, c->s + p, c->n - p + 1);
				c->n -= p - m.pos;
			} else if (k == K_SX) {
				m.pos = c->s ? car_prima(c->s, m.pos) : 0;
			} else if (k == K_DX) {
				m.pos = c->s ? car_dopo(c->s, m.pos) : 0;
			} else if (k == K_INIZIO) {
				m.pos = 0;
			} else if (k == K_FINERIGA) {
				m.pos = c->n;
			} else if (k == K_INVIO || k == K_GIU) {
				if (m.attivo == 0)
					anteprime(&m);
				m.attivo++;
				m.pos = m.attivo < 3 ? m.campo[m.attivo].n : 0;
			} else if (k == K_SU && m.attivo > 0) {
				m.attivo--;
				m.pos = m.campo[m.attivo].n;
			}
		} else {
			char *r = m.testo.v[m.riga];
			size_t len = strlen(r);

			if (k == K_TESTO) {
				char *n = xasprintf("%.*s%s%s", (int)m.col, r, car, r + m.col);

				free(r);
				m.testo.v[m.riga] = n;
				m.col += strlen(car);
			} else if (k == K_INVIO) {
				char *dopo = xstrdup(r + m.col);

				r[m.col] = '\0';
				strv_add(&m.testo, "");
				memmove(&m.testo.v[m.riga + 2], &m.testo.v[m.riga + 1],
					(m.testo.n - m.riga - 2) * sizeof *m.testo.v);
				m.testo.v[m.riga + 1] = dopo;
				m.riga++;
				m.col = 0;
			} else if (k == K_INDIETRO) {
				if (m.col) {
					size_t p = car_prima(r, m.col);

					memmove(r + p, r + m.col, len - m.col + 1);
					m.col = p;
				} else if (m.riga) {
					char *prec = m.testo.v[m.riga - 1], *unita = xasprintf("%s%s", prec, r);

					m.col = strlen(prec);
					free(prec);
					free(r);
					m.testo.v[m.riga - 1] = unita;
					memmove(&m.testo.v[m.riga], &m.testo.v[m.riga + 1], (m.testo.n - m.riga - 1) * sizeof *m.testo.v);
					m.testo.n--;
					m.riga--;
				}
			} else if (k == K_CANC) {
				if (m.col < len) {
					size_t p = car_dopo(r, m.col);

					memmove(r + m.col, r + p, len - p + 1);
				} else if (m.riga + 1 < m.testo.n) {
					char *unita = xasprintf("%s%s", r, m.testo.v[m.riga + 1]);

					free(r);
					free(m.testo.v[m.riga + 1]);
					m.testo.v[m.riga] = unita;
					memmove(&m.testo.v[m.riga + 1], &m.testo.v[m.riga + 2], (m.testo.n - m.riga - 2) * sizeof *m.testo.v);
					m.testo.n--;
				}
			} else if (k == K_SX) {
				if (m.col)
					m.col = car_prima(r, m.col);
				else if (m.riga) {
					m.riga--;
					m.col = strlen(m.testo.v[m.riga]);
				}
			} else if (k == K_DX) {
				if (m.col < len)
					m.col = car_dopo(r, m.col);
				else if (m.riga + 1 < m.testo.n) {
					m.riga++;
					m.col = 0;
				}
			} else if (k == K_SU) {
				if (m.riga) {
					m.riga--;
					if (m.col > strlen(m.testo.v[m.riga]))
						m.col = strlen(m.testo.v[m.riga]);
					while (m.col && ((unsigned char)m.testo.v[m.riga][m.col] & 0xc0) == 0x80)
						m.col--;
				} else {
					m.attivo = 2;
					m.pos = m.campo[2].n;
				}
			} else if (k == K_GIU && m.riga + 1 < m.testo.n) {
				m.riga++;
				if (m.col > strlen(m.testo.v[m.riga]))
					m.col = strlen(m.testo.v[m.riga]);
				while (m.col && ((unsigned char)m.testo.v[m.riga][m.col] & 0xc0) == 0x80)
					m.col--;
			} else if (k == K_INIZIO) {
				m.col = 0;
			} else if (k == K_FINERIGA) {
				m.col = len;
			}
		}
		schermo_libera(&s);
	}
	modulo_libera(&m);
	return inviato;
}

/* ---- guida dei tasti ---- */

static void aiuto(schermo_t *s)
{
	strv_t t = {0};
	static const char *const voci[][2] = {
		{"↑ ↓ PgUp PgDn", N_("move through the list")},
		{"Invio", N_("open the message: recipients and history")},
		{"n", N_("write and send a new message")},
		{"r", N_("revoke the selected message")},
		{"s", N_("remind whoever has not confirmed")},
		{"p", N_("delete old messages")},
		{"/", N_("search the messages by text or title")},
		{"q", N_("quit")},
	};

	for (size_t i = 0; i < sizeof voci / sizeof voci[0]; i++) {
		buf_t b = {0};

		buf_printf(&b, "%s", G_);
		colonna(&b, voci[i][0], 16);
		buf_printf(&b, "%s%s", R_, T(voci[i][1]));
		strv_add(&t, b.s);
		buf_free(&b);
	}
	strv_add(&t, "");
	strv_add(&t, T("The list updates by itself every 3 seconds."));
	strv_add(&t, T("The complete guide: ams --help."));
	{
		char car[8];

		sovrapponi(s, T("Keys"), &t, T("any key to continue"), xstrdup(T("any key to continue")));
		while (tasto(500, car) == K_TEMPO && !fermati)
			;
	}
	strv_free(&t);
}

/* ---- ciclo principale ---- */

bool ams_tui(void)
{
	elenco_t e = {0};
	size_t sel = 0, primo = 0;
	char car[8], *filtro = xstrdup("");
	int giri = 0;
	struct sigaction sa = {0};

	tty = open("/dev/tty", O_RDWR | O_CLOEXEC | O_NOCTTY);
	if (tty < 0)
		return false;
	if (!dimensioni(&TH, &TW) || TW < 80 || TH < 20 || tcgetattr(tty, &salvato) < 0) {
		close(tty);
		tty = -1;
		return false;
	}
	colori(!getenv("NO_COLOR"));
	sa.sa_handler = su_segnale;
	sigaction(SIGINT, &sa, NULL);
	sigaction(SIGTERM, &sa, NULL);
	sigaction(SIGHUP, &sa, NULL);
	signal(SIGPIPE, SIG_IGN);
	modo_tui();
	carica_elenco(&e, filtro);
	for (bool ricarica = false; !fermati; ricarica = false) {
		schermo_t s = {0};
		int area = TH - 4 - 3, k;

		if (sel >= e.n && e.n)
			sel = e.n - 1;
		if (sel < primo)
			primo = sel;
		if (area > 0 && sel >= primo + (size_t)area)
			primo = sel - (size_t)area + 1;
		s.titolo = xstrdup(T("AMS · sent messages"));
		s.destra = xasprintf(T("updated at %s"), e.ora);
		righe_lista(&s, &e, sel, primo, filtro);
		tasti_lista(&s);
		disegna(&s);
		k = tasto(500, car);
		if (k == K_TEMPO) {
			int r, c;

			if (dimensioni(&r, &c) && (r != TH || c != TW)) {
				TH = r;
				TW = c;
				if (TW < 80 || TH < 20) {
					schermo_libera(&s);
					break;
				}
			}
			if (++giri >= 6) {
				giri = 0;
				ricarica = true;
			}
		} else if (k == K_FINE || (k == K_TESTO && (car[0] == 'q' || car[0] == 'Q'))) {
			schermo_libera(&s);
			break;
		} else if (k == K_ESC && *filtro) {
			free(filtro);
			filtro = xstrdup("");
			ricarica = true;
		} else if (k == K_SU && sel) {
			sel--;
		} else if (k == K_GIU && sel + 1 < e.n) {
			sel++;
		} else if (k == K_PGSU) {
			sel = sel > (size_t)area ? sel - (size_t)area : 0;
		} else if (k == K_PGGIU) {
			sel = sel + (size_t)area < e.n ? sel + (size_t)area : e.n ? e.n - 1 : 0;
		} else if (k == K_INIZIO) {
			sel = 0;
		} else if (k == K_FINERIGA) {
			sel = e.n ? e.n - 1 : 0;
		} else if (k == K_INVIO && e.n) {
			dettaglio(e.v[sel].id, e.ora);
			ricarica = true;
		} else if (k == K_TESTO && car[0] == 'n') {
			long long nuovo = 0;

			if (nuovo_messaggio(&nuovo)) {
				carica_elenco(&e, filtro);
				sel = 0;
			}
			ricarica = true;
		} else if (k == K_TESTO && car[0] == 'r' && e.n && !e.v[sel].ritirato) {
			ritira(&s, &e.v[sel]);
			ricarica = true;
		} else if (k == K_TESTO && car[0] == 's' && e.n && !e.v[sel].ritirato && !e.v[sel].scaduto &&
			   e.v[sel].consegnato) {
			sollecita(&s, &e.v[sel]);
			ricarica = true;
		} else if (k == K_TESTO && car[0] == 'p') {
			pulizia(&s);
			ricarica = true;
		} else if (k == K_TESTO && car[0] == '/') {
			char *f = domanda(&s, T("Search"), T("Show only the messages containing:"), filtro);

			if (f) {
				free(filtro);
				filtro = f;
				sel = 0;
				ricarica = true;
			}
		} else if (k == K_TESTO && car[0] == '?') {
			aiuto(&s);
		}
		schermo_libera(&s);
		if (ricarica)
			carica_elenco(&e, filtro);
	}
	elenco_libera(&e);
	free(filtro);
	modo_normale();
	close(tty);
	tty = -1;
	return true;
}
