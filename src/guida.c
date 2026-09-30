/* AMS - Advanced Messaging System
 * Guida integrata di ams --help, sul modello di MTERM: guida interattiva a
 * schede in un terminale; con un terminale più piccolo di 44x10, pagina in
 * stile manuale con un pager; se l'uscita non è un terminale, testo semplice.
 *
 * I testi sono voci «etichetta¦descrizione» con un contesto per gruppo; il
 * riferimento del manuale utente riporta comandi e opzioni con lo stesso
 * testo (dalla traduzione italiana, po/it.po): tools/check-docs.py lo controlla. */
#include "guida.h"

#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <termios.h>
#include <unistd.h>

#include "comune.h"
#include "lingua.h"

#define NC_(ctx, s) (s)

/* TRADUTTORI: ogni voce è «etichetta¦descrizione»; si traducono entrambe e il
 * carattere ¦ resta. */
static const char *const COMANDI[] = {
	NC_("guida-comandi", "(no command)¦In a terminal, opens the interactive interface: the messages with their recipients and history; write and send, revoke, remind, delete old messages. In a pipe, shows this guide."),
	NC_("guida-comandi", "send [options] [TEXT]¦Sends a message to the recipients given with --to. Without TEXT or --file, the text is read from stdin."),
	NC_("guida-comandi", "list¦Lists the messages sent, with how many recipients have confirmed each one."),
	NC_("guida-comandi", "status ID¦Shows the text of the message and the state of each recipient: sent, delivered (in their mailbox) or confirmed, with date, time and channel."),
	NC_("guida-comandi", "revoke ID¦Revokes a message: whoever has not seen it yet will not see it, and dialogs and questions still open close by themselves."),
	NC_("guida-comandi", "remind ID¦Reminds whoever has not confirmed yet: the question comes back at their next prompt and the dialog reappears on the desktop, even if they had postponed it."),
	NC_("guida-comandi", "log ID¦Shows the history of the message from the system log: sending, deliveries, postponements, confirmations and revocation, with date and time."),
	NC_("guida-comandi", "purge DURATION¦Deletes the messages sent more than DURATION ago (for example 90d), with the copies and confirmations in the users' mailboxes; the events stay in the system log."),
	NC_("guida-comandi", "version¦Shows the AMS version."),
	NC_("guida-comandi", "help, --help, -h¦Shows this guide."),
};

static const char *const OPZIONI[] = {
	NC_("guida-opzioni", "--to DEST¦Recipients, separated by commas without spaces: a user (mario), a Unix group (@developers), all (every human user) or online (only those logged in now)."),
	NC_("guida-opzioni", "--title TITLE¦Title shown in the message header and in the desktop dialog."),
	NC_("guida-opzioni", "--expires DURATION¦Expiry, after which the message is no longer shown: 30m, 2h, 3d or a date and time (\"2026-10-04 12:00\")."),
	NC_("guida-opzioni", "--file FILE¦Reads the message text from FILE."),
};

static const char *const ESEMPI[] = {
	NC_("guida-esempi", "ams send --to mario \"Your account expires on Friday.\"¦Message with read confirmation to a single user."),
	NC_("guida-esempi", "ams send --to @developers --title Maintenance --file notice.txt¦Text taken from a file, with a title, to every member of the developers group."),
	NC_("guida-esempi", "ams send --to online --expires 15m \"Reboot at 13:00.\"¦Urgent notice to whoever is logged in now; after 15 minutes it is no longer shown or asked about."),
	NC_("guida-esempi", "ams send --to all --expires 3d \"New password policy.\"¦To every user; after three days it stops being shown."),
	NC_("guida-esempi", "ams list¦Which messages were sent and how many confirmations they have."),
	NC_("guida-esempi", "ams status 12¦Who confirmed message 12, when and from where."),
	NC_("guida-esempi", "ams log 12¦The history of message 12: sending, deliveries, postponements, confirmations."),
	NC_("guida-esempi", "ams purge 90d¦Deletes the messages older than 90 days, with copies and confirmations."),
	NC_("guida-esempi", "ams revoke 12¦Revokes message 12."),
	NC_("guida-esempi", "ams remind 12¦Asks again, right now, whoever has not confirmed message 12."),
};

static const char *const FILES[] = {
	NC_("guida-file", "/etc/ams/ams.conf¦Configuration: minutes before a postponed message is asked about again, check interval of the desktop agent."),
	NC_("guida-file", "/var/lib/ams/¦The messages: sent/ (reference copies, root only) and users/USER/ (each user's mailbox, readable only by them and by root)."),
	NC_("guida-file", "sudo journalctl -t ams¦The system log: sending, deliveries, confirmations and revocations."),
	NC_("guida-file", "/usr/local/share/doc/ams/User Manual.html¦The complete user manual, to open in a browser."),
};

static const char *const SINTASSI[] = {
	NC_("guida-sintassi", "ams send --to DEST [options] [TEXT]"),
	NC_("guida-sintassi", "ams list"),
	NC_("guida-sintassi", "ams status ID"),
	NC_("guida-sintassi", "ams"),
	NC_("guida-sintassi", "ams revoke ID"),
	NC_("guida-sintassi", "ams remind ID"),
	NC_("guida-sintassi", "ams log ID"),
	NC_("guida-sintassi", "ams purge DURATION"),
	NC_("guida-sintassi", "ams version"),
};

#define N(a) (sizeof(a) / sizeof((a)[0]))

static const char *descrizione(void)
{
	return TC("guida", "AMS lets administrators send text messages to the users of the machine and know who has read them. "
			   "Messages appear in terminals (console, ssh, desktop terminals, tmux) and on the desktop, in a dialog "
			   "with the buttons «I have read it» and «Later»; whoever is not logged in finds them at the next login. "
			   "Every message asks for a read confirmation and AMS asks again until the user gives it, without ever "
			   "blocking their work. Each user sees AMS in their own language. The command is reserved to "
			   "administrators (sudo or wheel group) and re-runs itself with sudo.");
}

/* ---- testo ---- */

static const char *R_, *B_, *D_, *G_, *Y_, *C_, *V_;

static void colori(bool si)
{
	R_ = si ? "\033[0m" : "";
	B_ = si ? "\033[1m" : "";
	D_ = si ? "\033[2m" : "";
	G_ = si ? "\033[1;32m" : "";
	Y_ = si ? "\033[1;33m" : "";
	C_ = si ? "\033[1;36m" : "";
	V_ = si ? "\033[7;1m" : "";
}

/* Lunghezza in caratteri (UTF-8). */
static size_t lung(const char *s)
{
	size_t n = 0;

	for (; *s; s++)
		if (((unsigned char)*s & 0xc0) != 0x80)
			n++;
	return n;
}

/* I primi n caratteri di s. */
static size_t byte_di(const char *s, size_t n)
{
	size_t i = 0, c = 0;

	while (s[i]) {
		if (((unsigned char)s[i] & 0xc0) != 0x80) {
			if (c == n)
				break;
			c++;
		}
		i++;
	}
	return i;
}

/* Manda a capo testo a larghezza con rientro: righe in out. */
static void a_capo(const char *testo, int larghezza, int rientro, strv_t *out)
{
	int disp = larghezza - rientro;
	char *copia = xstrdup(testo), *salva = NULL;
	buf_t cur = {0};

	if (disp < 24)
		disp = 24;
	for (char *w = strtok_r(copia, " \t\n", &salva); w; w = strtok_r(NULL, " \t\n", &salva)) {
		if (!cur.n) {
			buf_printf(&cur, "%*s%s", rientro, "", w);
		} else if ((int)(lung(cur.s) - (size_t)rientro + 1 + lung(w)) <= disp) {
			buf_printf(&cur, " %s", w);
		} else {
			strv_add(out, cur.s);
			buf_clear(&cur);
			buf_printf(&cur, "%*s%s", rientro, "", w);
		}
	}
	if (cur.n)
		strv_add(out, cur.s);
	buf_free(&cur);
	free(copia);
}

static void etichetta_e_testo(const char *ctx, const char *voce, char **etichetta, const char **testo)
{
	const char *t = TC(ctx, voce), *sep = strstr(t, "¦");

	if (!sep) {
		*etichetta = xstrdup(t);
		*testo = "";
		return;
	}
	*etichetta = xmalloc((size_t)(sep - t) + 1);
	memcpy(*etichetta, t, (size_t)(sep - t));
	(*etichetta)[sep - t] = '\0';
	*testo = sep + strlen("¦");
}

/* ---- pagina in stile manuale (pager e testo semplice) ---- */

static void pagina(FILE *f, bool colore, int larghezza)
{
	const char *ti = "       ";
	const int di = 14;
	char *s;
	strv_t w = {0};

	if (larghezza < 60)
		larghezza = 60;
	if (larghezza > 100)
		larghezza = 100;
	colori(colore);
#define TRE(sx, mezzo, dx)                                                                                              \
	do {                                                                                                           \
		int gap = larghezza - (int)lung(sx) - (int)lung(mezzo) - (int)lung(dx), l;                            \
		if (gap < 2)                                                                                           \
			gap = 2;                                                                                       \
		l = gap / 2;                                                                                           \
		fprintf(f, "%s%s%*s%s%*s%s%s\n", B_, sx, l, "", mezzo, gap - l, "", dx, R_);                           \
	} while (0)
#define TITOLO(x) fprintf(f, "\n%s%s%s\n", B_, x, R_)
#define PARA(x, r)                                                                                                     \
	do {                                                                                                           \
		a_capo(x, larghezza, r, &w);                                                                           \
		for (size_t i_ = 0; i_ < w.n; i_++)                                                                    \
			fprintf(f, "%s\n", w.v[i_]);                                                                   \
		strv_free(&w);                                                                                         \
	} while (0)
#define VOCI(ctx, arr)                                                                                                 \
	do {                                                                                                           \
		for (size_t k_ = 0; k_ < N(arr); k_++) {                                                               \
			char *e_;                                                                                      \
			const char *d_;                                                                                \
			etichetta_e_testo(ctx, arr[k_], &e_, &d_);                                                     \
			fprintf(f, "%s%s%s%s\n", ti, G_, e_, R_);                                                      \
			PARA(d_, di);                                                                                  \
			free(e_);                                                                                      \
		}                                                                                                      \
	} while (0)

	TRE("AMS(1)", T("ams manual"), "AMS(1)");
	TITOLO(T("NAME"));
	PARA(T("ams — sends messages to the users of the machine and tracks their read confirmation"), 7);
	TITOLO(T("SYNOPSIS"));
	for (size_t k = 0; k < N(SINTASSI); k++) {
		const char *e = TC("guida-sintassi", SINTASSI[k]);
		size_t p = strcspn(e, " ");

		fprintf(f, "%s%s%.*s%s%s\n", ti, B_, (int)p, e, R_, e + p);
	}
	TITOLO(T("DESCRIPTION"));
	PARA(descrizione(), 7);
	TITOLO(T("COMMANDS"));
	VOCI("guida-comandi", COMANDI);
	TITOLO(T("SEND OPTIONS"));
	VOCI("guida-opzioni", OPZIONI);
	TITOLO(T("EXAMPLES"));
	VOCI("guida-esempi", ESEMPI);
	TITOLO(T("FILES"));
	VOCI("guida-file", FILES);
	TITOLO(T("ENVIRONMENT"));
	fprintf(f, "%s%sPAGER%s\n", ti, G_, R_);
	PARA(T("Pager used to page this guide when the terminal is too small for the interactive one (default: less). "
	       "Like NO_COLOR, it reaches ams only if sudo keeps it (env_keep in sudoers)."),
	     di);
	fprintf(f, "%s%sNO_COLOR%s\n", ti, G_, R_);
	PARA(T("If set, disables colours."), di);
	TITOLO(T("EXIT STATUS"));
	fprintf(f, "%s%s0%s\n", ti, G_, R_);
	PARA(T("Completed successfully."), di);
	fprintf(f, "%s%s1%s\n", ti, G_, R_);
	PARA(T("Error: the error message, starting with «ams:», says which."), di);
	TITOLO(T("SEE ALSO"));
	PARA(T("wall(1), write(1), and the user manual in /usr/local/share/doc/ams/User Manual.html"), 7);
	fputc('\n', f);
	s = xasprintf("ams %s", AMS_VERSION);
	TRE(s, "", "AMS(1)");
	free(s);
#undef TRE
#undef TITOLO
#undef PARA
#undef VOCI
}

/* ---- guida interattiva a schede ---- */

static int tty = -1, TH, TW, scheda;
static int scorri[5];
static struct termios salvato;
static volatile sig_atomic_t fermati;

static void su_segnale(int s)
{
	(void)s;
	fermati = 1;
}

static void ripristina(void)
{
	static const char fine[] = "\033[?25h\033[?1049l";

	tcsetattr(tty, TCSAFLUSH, &salvato);
	scrivi_tutto(1, fine, sizeof fine - 1);
}

static bool dimensioni(int *righe, int *colonne)
{
	struct winsize ws;

	if (ioctl(tty, TIOCGWINSZ, &ws) < 0 || !ws.ws_row || !ws.ws_col)
		return false;
	*righe = ws.ws_row;
	*colonne = ws.ws_col;
	return true;
}

typedef struct {
	char tipo; /* H titolo, F voce, T testo */
	char *testo;
} riga_t;

static void aggiungi(riga_t **r, size_t *n, char tipo, const char *testo)
{
	*r = xrealloc(*r, (*n + 1) * sizeof **r);
	(*r)[*n].tipo = tipo;
	(*r)[(*n)++].testo = xstrdup(testo);
}

static void voci_scheda(riga_t **r, size_t *n, const char *ctx, const char *const *arr, size_t na, int interno)
{
	for (size_t k = 0; k < na; k++) {
		char *e, *f;
		const char *d;
		strv_t w = {0};

		if (k)
			aggiungi(r, n, 'T', "");
		etichetta_e_testo(ctx, arr[k], &e, &d);
		f = xasprintf(" %s", e);
		aggiungi(r, n, 'F', f);
		a_capo(d, interno, 4, &w);
		for (size_t i = 0; i < w.n; i++)
			aggiungi(r, n, 'T', w.v[i]);
		strv_free(&w);
		free(e);
		free(f);
	}
}

static riga_t *righe_scheda(int s, int interno, size_t *n)
{
	riga_t *r = NULL;
	strv_t w = {0};
	char *x;

	*n = 0;
	switch (s) {
	case 0:
		aggiungi(&r, n, 'H', T("NAME"));
		x = xasprintf("   %s", T("ams — messages to users with read confirmation"));
		aggiungi(&r, n, 'T', x);
		free(x);
		aggiungi(&r, n, 'T', "");
		aggiungi(&r, n, 'H', T("SYNOPSIS"));
		for (size_t k = 0; k < N(SINTASSI); k++) {
			x = xasprintf("   %s", TC("guida-sintassi", SINTASSI[k]));
			aggiungi(&r, n, 'T', x);
			free(x);
		}
		aggiungi(&r, n, 'T', "");
		aggiungi(&r, n, 'H', T("DESCRIPTION"));
		a_capo(descrizione(), interno, 3, &w);
		for (size_t i = 0; i < w.n; i++)
			aggiungi(&r, n, 'T', w.v[i]);
		strv_free(&w);
		aggiungi(&r, n, 'T', "");
		{
			char *m = xasprintf(T("AMS %s · complete manual: /usr/local/share/doc/ams/User Manual.html"),
					    AMS_VERSION);

			x = xasprintf("   %s", m);
			free(m);
		}
		aggiungi(&r, n, 'T', x);
		free(x);
		break;
	case 1:
		aggiungi(&r, n, 'H', T("Commands"));
		aggiungi(&r, n, 'T', "");
		voci_scheda(&r, n, "guida-comandi", COMANDI, N(COMANDI), interno);
		break;
	case 2:
		aggiungi(&r, n, 'H', T("Send options"));
		aggiungi(&r, n, 'T', "");
		voci_scheda(&r, n, "guida-opzioni", OPZIONI, N(OPZIONI), interno);
		break;
	case 3:
		aggiungi(&r, n, 'H', T("Examples"));
		aggiungi(&r, n, 'T', "");
		voci_scheda(&r, n, "guida-esempi", ESEMPI, N(ESEMPI), interno);
		break;
	default:
		aggiungi(&r, n, 'H', T("Files and log"));
		aggiungi(&r, n, 'T', "");
		voci_scheda(&r, n, "guida-file", FILES, N(FILES), interno);
		break;
	}
	return r;
}

static const char *nome_scheda(int s)
{
	switch (s) {
	case 0:
		return T("Info");
	case 1:
		return T("Commands");
	case 2:
		return T("Options");
	case 3:
		return T("Examples");
	default:
		return T("Files");
	}
}

/* Riga incorniciata di tipo t. */
static void riga(buf_t *out, char tipo, const char *testo)
{
	int interno = TW - 4;
	size_t b = byte_di(testo, (size_t)(interno > 0 ? interno : 0));
	int pad = interno - (int)lung(testo) > 0 ? interno - (int)lung(testo) : 0;
	const char *col = tipo == 'H' ? Y_ : tipo == 'F' ? G_ : "";

	if ((int)lung(testo) > interno)
		pad = 0;
	buf_printf(out, "%s│%s %s%.*s%s%*s %s│%s", D_, R_, col, (int)b, testo, *col ? R_ : "", pad, "", D_, R_);
}

static void ripeti(buf_t *out, const char *c, int volte)
{
	for (int i = 0; i < volte; i++)
		buf_adds(out, c);
}

static void bordo(buf_t *out, const char *sx, const char *dx, const char *titolo)
{
	int interno = TW - 2;

	if (titolo && *titolo) {
		char *t = xasprintf("─ %s ", titolo);

		buf_printf(out, "%s%s%s%s%s%s%s", D_, sx, R_, C_, t, R_, D_);
		ripeti(out, "─", interno - (int)lung(t));
		buf_printf(out, "%s%s", dx, R_);
		free(t);
	} else {
		buf_printf(out, "%s%s", D_, sx);
		ripeti(out, "─", interno);
		buf_printf(out, "%s%s", dx, R_);
	}
}

static int disegna(void)
{
	int ch = TH - 6, interno = TW - 4, massimo, off, n = 0;
	size_t totale;
	riga_t *r = righe_scheda(scheda, interno, &totale);
	buf_t out = {0}, barra = {0}, stato = {0};
	char pos[64];
	const char *suggerimento = T("←/→ tabs · ↑/↓ scroll · PgUp/PgDn · g/G · q quit");

	massimo = (int)totale - ch;
	if (massimo < 0)
		massimo = 0;
	if (scorri[scheda] > massimo)
		scorri[scheda] = massimo;
	if (scorri[scheda] < 0)
		scorri[scheda] = 0;
	off = scorri[scheda];

	buf_adds(&out, "\033[H");
	bordo(&out, "┌", "┐", T("ams — guide"));
	buf_adds(&out, "\n");
	for (int i = 0; i < 5; i++) {
		const char *nome = nome_scheda(i);

		if (i == scheda) {
			if (*V_)
				buf_printf(&barra, "%s %s %s", V_, nome, R_);
			else
				buf_printf(&barra, ">%s<", nome);
		} else {
			buf_printf(&barra, "%s %s %s", D_, nome, R_);
		}
		n += (int)lung(nome) + 2;
	}
	buf_printf(&out, "%s│%s %s%*s %s│%s\n", D_, R_, barra.s, interno - n > 0 ? interno - n : 0, "", D_, R_);
	bordo(&out, "├", "┤", NULL);
	buf_adds(&out, "\n");
	for (int i = 0; i < ch; i++) {
		if (off + i < (int)totale)
			riga(&out, r[off + i].tipo, r[off + i].testo);
		else
			riga(&out, 'T', "");
		buf_adds(&out, "\n");
	}
	bordo(&out, "├", "┤", NULL);
	buf_adds(&out, "\n");
	{
		int fondo = off + ch > (int)totale ? (int)totale : off + ch;

		snprintf(pos, sizeof pos, T("lines %d-%d/%zu"), off + 1, fondo, totale);
	}
	buf_adds(&stato, suggerimento);
	if ((int)(lung(suggerimento) + lung(pos) + 3) <= interno)
		buf_printf(&stato, "%*s%s", interno - (int)lung(suggerimento) - (int)lung(pos), "", pos);
	{
		size_t b = byte_di(stato.s, (size_t)interno);
		int pad = interno - (int)lung(stato.s) > 0 ? interno - (int)lung(stato.s) : 0;

		buf_printf(&out, "%s│ %.*s%*s │%s\n", D_, (int)b, stato.s, pad, "", R_);
	}
	bordo(&out, "└", "┘", NULL);
	buf_adds(&out, "\033[J");
	scrivi_tutto(1, out.s, out.n);
	for (size_t i = 0; i < totale; i++)
		free(r[i].testo);
	free(r);
	buf_free(&out);
	buf_free(&barra);
	buf_free(&stato);
	return massimo;
}

/* Un byte dal terminale entro ms millisecondi: -1 tempo scaduto, -2 fine. */
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

enum { K_NULLA, K_TEMPO, K_ESCI, K_SU, K_GIU, K_DX, K_SX, K_TAB, K_STAB, K_PGSU, K_PGGIU, K_INIZIO, K_FINE };

static int tasto(int *cifra)
{
	int c = byte_tty(300), d, e;

	*cifra = 0;
	if (c == -1)
		return K_TEMPO;
	if (c == -2)
		return K_ESCI;
	switch (c) {
	case 27:
		d = byte_tty(50);
		if (d < 0)
			return K_ESCI;
		e = byte_tty(50);
		if (d == '[' || d == 'O') {
			switch (e) {
			case 'A': return K_SU;
			case 'B': return K_GIU;
			case 'C': return K_DX;
			case 'D': return K_SX;
			case 'H': return K_INIZIO;
			case 'F': return K_FINE;
			case 'Z': return K_STAB;
			default: break;
			}
			if (d == '[' && e >= '0' && e <= '9') {
				int x;

				/* «ESC [ n ~»: 5 PgUp, 6 PgDn, 1/7 Home, 4/8 End */
				while ((x = byte_tty(50)) >= 0 && x != '~')
					;
				switch (e) {
				case '5': return K_PGSU;
				case '6': return K_PGGIU;
				case '1': case '7': return K_INIZIO;
				case '4': case '8': return K_FINE;
				default: return K_NULLA;
				}
			}
		}
		return K_NULLA;
	case 'q': case 'Q': return K_ESCI;
	case '\t': return K_TAB;
	case 'h': return K_SX;
	case 'l': case '\n': case '\r': return K_DX;
	case 'j': return K_GIU;
	case 'k': return K_SU;
	case ' ': return K_PGGIU;
	case 'b': return K_PGSU;
	case 'g': return K_INIZIO;
	case 'G': return K_FINE;
	default:
		if (c >= '1' && c <= '9') {
			*cifra = c - '0';
			return K_NULLA;
		}
		return K_NULLA;
	}
}

static bool guida_a_schede(void)
{
	struct termios t;
	struct sigaction sa = {0};
	static const char inizio[] = "\033[?1049h\033[?25l";

	tty = open("/dev/tty", O_RDWR | O_CLOEXEC | O_NOCTTY);
	if (tty < 0)
		return false;
	if (!dimensioni(&TH, &TW) || TW < 44 || TH < 10 || tcgetattr(tty, &salvato) < 0) {
		close(tty);
		tty = -1;
		return false;
	}
	colori(!getenv("NO_COLOR"));
	scheda = 0;
	memset(scorri, 0, sizeof scorri);
	sa.sa_handler = su_segnale;
	sigaction(SIGINT, &sa, NULL);
	sigaction(SIGTERM, &sa, NULL);
	sigaction(SIGHUP, &sa, NULL);
	t = salvato;
	t.c_lflag &= ~(tcflag_t)(ECHO | ICANON);
	t.c_cc[VMIN] = 1;
	t.c_cc[VTIME] = 0;
	tcsetattr(tty, TCSAFLUSH, &t);
	scrivi_tutto(1, inizio, sizeof inizio - 1);
	disegna();
	while (!fermati) {
		int cifra, k = tasto(&cifra), ch = TH - 7;

		if (fermati || k == K_ESCI)
			break;
		if (k == K_TEMPO) {
			int r, c;

			/* ridisegna se la finestra ha cambiato dimensione */
			if (dimensioni(&r, &c) && (r != TH || c != TW)) {
				TH = r;
				TW = c;
				if (TW < 44 || TH < 10)
					break;
				disegna();
			}
			continue;
		}
		switch (k) {
		case K_SX: case K_STAB: scheda = (scheda + 4) % 5; break;
		case K_DX: case K_TAB: scheda = (scheda + 1) % 5; break;
		case K_SU: scorri[scheda]--; break;
		case K_GIU: scorri[scheda]++; break;
		case K_PGSU: scorri[scheda] -= ch; break;
		case K_PGGIU: scorri[scheda] += ch; break;
		case K_INIZIO: scorri[scheda] = 0; break;
		case K_FINE: scorri[scheda] = 999999; break;
		default:
			if (cifra >= 1 && cifra <= 5)
				scheda = cifra - 1;
			else
				continue;
		}
		disegna();
	}
	ripristina();
	close(tty);
	tty = -1;
	return true;
}

static bool nel_path(const char *prog)
{
	const char *path = getenv("PATH");
	char *copia, *salva = NULL;
	bool trovato = false;

	if (!path)
		path = "/usr/bin:/bin";
	copia = xstrdup(path);
	for (char *d = strtok_r(copia, ":", &salva); d && !trovato; d = strtok_r(NULL, ":", &salva)) {
		char *p = xasprintf("%s/%s", d, prog);

		trovato = access(p, X_OK) == 0;
		free(p);
	}
	free(copia);
	return trovato;
}

void ams_guida(void)
{
	bool colore = !getenv("NO_COLOR");
	int righe = 0, colonne = 80;
	const char *pager = getenv("PAGER");
	FILE *f;

	if (!isatty(0) || !isatty(1)) {
		pagina(stdout, false, 80);
		return;
	}
	if (guida_a_schede())
		return;
	tty = open("/dev/tty", O_RDWR | O_CLOEXEC | O_NOCTTY);
	if (tty >= 0) {
		dimensioni(&righe, &colonne);
		close(tty);
		tty = -1;
	}
	fflush(stdout);
	if (pager && *pager)
		f = popen(pager, "w");
	else if (nel_path("less"))
		f = popen("less -R -F -X", "w");
	else
		f = NULL;
	if (!f) {
		pagina(stdout, colore, colonne);
		return;
	}
	signal(SIGPIPE, SIG_IGN);
	pagina(f, colore, colonne);
	pclose(f);
}
