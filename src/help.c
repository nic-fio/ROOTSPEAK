/* RootSpeak - Advanced Messaging System for Linux
 * Built-in help of rspeak --help, modelled on MTERM's: interactive help with
 * tabs in a terminal; with a terminal smaller than 44x10, a manual-style page
 * in a pager; if the output is not a terminal, plain text.
 *
 * The texts are items «label¦description»; the reference in the user manual
 * lists commands and options with the same text, read from this file:
 * tools/check-docs.py checks it. */
#include "help.h"

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

#include "common.h"

/* Each item is «label¦description». */
static const char *const COMMANDS[] = {
	"(no command)¦In a terminal, opens the interactive interface: the messages with their recipients and history; write and send, revoke, remind, delete old messages. In a pipe, shows this guide.",
	"send [options] [TEXT]¦Sends a message to the recipients given with --to. Without TEXT or --file, the text is read from stdin.",
	"list¦Lists the messages sent, with how many recipients have confirmed each one.",
	"status ID¦Shows the text of the message and the state of each recipient: sent, delivered (in their mailbox) or confirmed, with date, time and channel.",
	"revoke ID¦Revokes a message: whoever has not seen it yet will not see it, and dialogs and questions still open close by themselves.",
	"remind ID¦Reminds whoever has not confirmed yet: the question comes back at their next prompt and the dialog reappears on the desktop, even if they had postponed it.",
	"log ID¦Shows the history of the message from the system log: sending, deliveries, postponements, confirmations and revocation, with date and time.",
	"purge DURATION¦Deletes the messages sent more than DURATION ago (for example 90d), with the copies and confirmations in the users' mailboxes; the events stay in the system log.",
	"version¦Shows the RootSpeak version.",
	"help, --help, -h¦Shows this guide.",
};

static const char *const OPTIONS[] = {
	"--to DEST¦Recipients, separated by commas without spaces: a user (mario), a Unix group (@developers), all (every human user) or online (only those logged in now).",
	"--title TITLE¦Title shown in the message header and in the desktop dialog.",
	"--expires DURATION¦Expiry, after which the message is no longer shown: 30m, 2h, 3d or a date and time (\"2026-10-04 12:00\").",
	"--file FILE¦Reads the message text from FILE.",
};

static const char *const EXAMPLES[] = {
	"rspeak send --to mario \"Your account expires on Friday.\"¦Message with read confirmation to a single user.",
	"rspeak send --to @developers --title Maintenance --file notice.txt¦Text taken from a file, with a title, to every member of the developers group.",
	"rspeak send --to online --expires 15m \"Reboot at 13:00.\"¦Urgent notice to whoever is logged in now; after 15 minutes it is no longer shown or asked about.",
	"rspeak send --to all --expires 3d \"New password policy.\"¦To every user; after three days it stops being shown.",
	"rspeak list¦Which messages were sent and how many confirmations they have.",
	"rspeak status 12¦Who confirmed message 12, when and from where.",
	"rspeak log 12¦The history of message 12: sending, deliveries, postponements, confirmations.",
	"rspeak purge 90d¦Deletes the messages older than 90 days, with copies and confirmations.",
	"rspeak revoke 12¦Revokes message 12.",
	"rspeak remind 12¦Asks again, right now, whoever has not confirmed message 12.",
};

static const char *const FILES[] = {
	"/etc/rootspeak/rootspeak.conf¦Configuration: minutes before a postponed message is asked about again, check interval of the desktop agent.",
	"/var/lib/rootspeak/¦The messages: sent/ (reference copies, root only) and users/USER/ (each user's mailbox, readable only by them and by root).",
	"sudo journalctl -t rspeak¦The system log: sending, deliveries, confirmations and revocations.",
	DOCDIR "/User Manual.html¦The complete user manual, to open in a browser.",
};

static const char *const SYNOPSIS[] = {
	"rspeak send --to DEST [options] [TEXT]",
	"rspeak list",
	"rspeak status ID",
	"rspeak",
	"rspeak revoke ID",
	"rspeak remind ID",
	"rspeak log ID",
	"rspeak purge DURATION",
	"rspeak version",
};

#define N(a) (sizeof(a) / sizeof((a)[0]))

static const char *description(void)
{
	return "RootSpeak lets administrators send text messages to the users of the machine and know who has read them. "
			   "Messages appear in terminals (console, ssh, desktop terminals, tmux) and on the desktop, in a dialog "
			   "with the buttons «I have read it» and «Later»; whoever is not logged in finds them at the next login. "
			   "Every message asks for a read confirmation and RootSpeak asks again until the user gives it, without ever "
			   "blocking their work. The command is reserved to "
			   "administrators (sudo or wheel group) and re-runs itself with sudo.";
}

/* ---- text ---- */

static const char *R_, *B_, *D_, *G_, *Y_, *C_, *V_;

static void colours(bool si)
{
	R_ = si ? "\033[0m" : "";
	B_ = si ? "\033[1m" : "";
	D_ = si ? "\033[2m" : "";
	G_ = si ? "\033[1;32m" : "";
	Y_ = si ? "\033[1;33m" : "";
	C_ = si ? "\033[1;36m" : "";
	V_ = si ? "\033[7;1m" : "";
}

/* Length in characters (UTF-8). */
static size_t length(const char *s)
{
	size_t n = 0;

	for (; *s; s++)
		if (((unsigned char)*s & 0xc0) != 0x80)
			n++;
	return n;
}

/* Bytes taken by the first n characters of s. */
static size_t bytes_of(const char *s, size_t n)
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

/* Wraps txt to width with indent indent: lines in out. */
static void newline(const char *txt, int width, int indent, strv_t *out)
{
	int disp = width - indent;
	char *copy = xstrdup(txt), *save = NULL;
	buf_t cur = {0};

	if (disp < 24)
		disp = 24;
	for (char *w = strtok_r(copy, " \t\n", &save); w; w = strtok_r(NULL, " \t\n", &save)) {
		if (!cur.n) {
			buf_printf(&cur, "%*s%s", indent, "", w);
		} else if ((int)(length(cur.s) - (size_t)indent + 1 + length(w)) <= disp) {
			buf_printf(&cur, " %s", w);
		} else {
			strv_add(out, cur.s);
			buf_clear(&cur);
			buf_printf(&cur, "%*s%s", indent, "", w);
		}
	}
	if (cur.n)
		strv_add(out, cur.s);
	buf_free(&cur);
	free(copy);
}

static void label_and_text(const char *item, char **label, const char **txt)
{
	const char *t = item, *sep = strstr(t, "¦");

	if (!sep) {
		*label = xstrdup(t);
		*txt = "";
		return;
	}
	*label = xmalloc((size_t)(sep - t) + 1);
	memcpy(*label, t, (size_t)(sep - t));
	(*label)[sep - t] = '\0';
	*txt = sep + strlen("¦");
}

/* ---- manual-style page (pager and plain text) ---- */

static void page(FILE *f, bool colour, int width)
{
	const char *ti = "       ";
	const int di = 14;
	char *s;
	strv_t w = {0};

	if (width < 60)
		width = 60;
	if (width > 100)
		width = 100;
	colours(colour);
#define TRE(sx, middle, dx)                                                                                              \
	do {                                                                                                           \
		int gap = width - (int)length(sx) - (int)length(middle) - (int)length(dx), l;                            \
		if (gap < 2)                                                                                           \
			gap = 2;                                                                                       \
		l = gap / 2;                                                                                           \
		fprintf(f, "%s%s%*s%s%*s%s%s\n", B_, sx, l, "", middle, gap - l, "", dx, R_);                           \
	} while (0)
#define HEADING(x) fprintf(f, "\n%s%s%s\n", B_, x, R_)
#define PARA(x, r)                                                                                                     \
	do {                                                                                                           \
		newline(x, width, r, &w);                                                                           \
		for (size_t i_ = 0; i_ < w.n; i_++)                                                                    \
			fprintf(f, "%s\n", w.v[i_]);                                                                   \
		strv_free(&w);                                                                                         \
	} while (0)
#define ITEMS(arr)                                                                                                      \
	do {                                                                                                           \
		for (size_t k_ = 0; k_ < N(arr); k_++) {                                                               \
			char *e_;                                                                                      \
			const char *d_;                                                                                \
			label_and_text(arr[k_], &e_, &d_);                                                     \
			fprintf(f, "%s%s%s%s\n", ti, G_, e_, R_);                                                      \
			PARA(d_, di);                                                                                  \
			free(e_);                                                                                      \
		}                                                                                                      \
	} while (0)

	TRE("RSPEAK(1)", "rspeak manual", "RSPEAK(1)");
	HEADING("NAME");
	PARA("rspeak — sends messages to the users of the machine and tracks their read confirmation", 7);
	HEADING("SYNOPSIS");
	for (size_t k = 0; k < N(SYNOPSIS); k++) {
		const char *e = SYNOPSIS[k];
		size_t p = strcspn(e, " ");

		fprintf(f, "%s%s%.*s%s%s\n", ti, B_, (int)p, e, R_, e + p);
	}
	HEADING("DESCRIPTION");
	PARA(description(), 7);
	HEADING("COMMANDS");
	ITEMS(COMMANDS);
	HEADING("SEND OPTIONS");
	ITEMS(OPTIONS);
	HEADING("EXAMPLES");
	ITEMS(EXAMPLES);
	HEADING("FILES");
	ITEMS(FILES);
	HEADING("ENVIRONMENT");
	fprintf(f, "%s%sPAGER%s\n", ti, G_, R_);
	PARA("Pager used to page this guide when the terminal is too small for the interactive one (default: less). "
	       "Like NO_COLOR, it reaches rspeak only if sudo keeps it (env_keep in sudoers).",
	     di);
	fprintf(f, "%s%sNO_COLOR%s\n", ti, G_, R_);
	PARA("If set, disables colours.", di);
	HEADING("EXIT STATUS");
	fprintf(f, "%s%s0%s\n", ti, G_, R_);
	PARA("Completed successfully.", di);
	fprintf(f, "%s%s1%s\n", ti, G_, R_);
	PARA("Error: the error message, starting with «rspeak:», says which.", di);
	HEADING("SEE ALSO");
	PARA("wall(1), write(1), and the user manual in " DOCDIR "/User Manual.html", 7);
	fputc('\n', f);
	s = xasprintf("rspeak %s", RSPEAK_VERSION);
	TRE(s, "", "RSPEAK(1)");
	free(s);
#undef TRE
#undef HEADING
#undef PARA
#undef ITEMS
}

/* ---- interactive help with tabs ---- */

static int tty = -1, TH, TW, tab;
static int scroll[5];
static struct termios saved;
static volatile sig_atomic_t stop_requested;

static void on_signal(int s)
{
	(void)s;
	stop_requested = 1;
}

static void restore(void)
{
	static const char fine[] = "\033[?25h\033[?1049l";

	tcsetattr(tty, TCSAFLUSH, &saved);
	write_all(1, fine, sizeof fine - 1);
}

static bool size(int *lines, int *columns)
{
	struct winsize ws;

	if (ioctl(tty, TIOCGWINSZ, &ws) < 0 || !ws.ws_row || !ws.ws_col)
		return false;
	*lines = ws.ws_row;
	*columns = ws.ws_col;
	return true;
}

typedef struct {
	char kind; /* H heading, F item, T text */
	char *txt;
} line_t;

static void add(line_t **r, size_t *n, char kind, const char *txt)
{
	*r = xrealloc(*r, (*n + 1) * sizeof **r);
	(*r)[*n].kind = kind;
	(*r)[(*n)++].txt = xstrdup(txt);
}

static void tab_items(line_t **r, size_t *n, const char *const *arr, size_t na, int inner)
{
	for (size_t k = 0; k < na; k++) {
		char *e, *f;
		const char *d;
		strv_t w = {0};

		if (k)
			add(r, n, 'T', "");
		label_and_text(arr[k], &e, &d);
		f = xasprintf(" %s", e);
		add(r, n, 'F', f);
		newline(d, inner, 4, &w);
		for (size_t i = 0; i < w.n; i++)
			add(r, n, 'T', w.v[i]);
		strv_free(&w);
		free(e);
		free(f);
	}
}

static line_t *tab_lines(int s, int inner, size_t *n)
{
	line_t *r = NULL;
	strv_t w = {0};
	char *x;

	*n = 0;
	switch (s) {
	case 0:
		add(&r, n, 'H', "NAME");
		x = xasprintf("   %s", "rspeak — messages to users with read confirmation");
		add(&r, n, 'T', x);
		free(x);
		add(&r, n, 'T', "");
		add(&r, n, 'H', "SYNOPSIS");
		for (size_t k = 0; k < N(SYNOPSIS); k++) {
			x = xasprintf("   %s", SYNOPSIS[k]);
			add(&r, n, 'T', x);
			free(x);
		}
		add(&r, n, 'T', "");
		add(&r, n, 'H', "DESCRIPTION");
		newline(description(), inner, 3, &w);
		for (size_t i = 0; i < w.n; i++)
			add(&r, n, 'T', w.v[i]);
		strv_free(&w);
		add(&r, n, 'T', "");
		{
			char *m = xasprintf("RootSpeak %s · complete manual: " DOCDIR "/User Manual.html",
					    RSPEAK_VERSION);

			x = xasprintf("   %s", m);
			free(m);
		}
		add(&r, n, 'T', x);
		free(x);
		break;
	case 1:
		add(&r, n, 'H', "Commands");
		add(&r, n, 'T', "");
		tab_items(&r, n, COMMANDS, N(COMMANDS), inner);
		break;
	case 2:
		add(&r, n, 'H', "Send options");
		add(&r, n, 'T', "");
		tab_items(&r, n, OPTIONS, N(OPTIONS), inner);
		break;
	case 3:
		add(&r, n, 'H', "Examples");
		add(&r, n, 'T', "");
		tab_items(&r, n, EXAMPLES, N(EXAMPLES), inner);
		break;
	default:
		add(&r, n, 'H', "Files and log");
		add(&r, n, 'T', "");
		tab_items(&r, n, FILES, N(FILES), inner);
		break;
	}
	return r;
}

static const char *tab_name(int s)
{
	switch (s) {
	case 0:
		return "Info";
	case 1:
		return "Commands";
	case 2:
		return "Options";
	case 3:
		return "Examples";
	default:
		return "Files";
	}
}

/* Framed line of type kind. */
static void line(buf_t *out, char kind, const char *txt)
{
	int inner = TW - 4;
	size_t b = bytes_of(txt, (size_t)(inner > 0 ? inner : 0));
	int pad = inner - (int)length(txt) > 0 ? inner - (int)length(txt) : 0;
	const char *col = kind == 'H' ? Y_ : kind == 'F' ? G_ : "";

	if ((int)length(txt) > inner)
		pad = 0;
	buf_printf(out, "%s│%s %s%.*s%s%*s %s│%s", D_, R_, col, (int)b, txt, *col ? R_ : "", pad, "", D_, R_);
}

static void repeat(buf_t *out, const char *c, int count)
{
	for (int i = 0; i < count; i++)
		buf_adds(out, c);
}

static void border(buf_t *out, const char *sx, const char *dx, const char *title_text)
{
	int inner = TW - 2;

	if (title_text && *title_text) {
		char *t = xasprintf("─ %s ", title_text);

		buf_printf(out, "%s%s%s%s%s%s%s", D_, sx, R_, C_, t, R_, D_);
		repeat(out, "─", inner - (int)length(t));
		buf_printf(out, "%s%s", dx, R_);
		free(t);
	} else {
		buf_printf(out, "%s%s", D_, sx);
		repeat(out, "─", inner);
		buf_printf(out, "%s%s", dx, R_);
	}
}

static int draw(void)
{
	int ch = TH - 6, inner = TW - 4, maximum, off, n = 0;
	size_t total;
	line_t *r = tab_lines(tab, inner, &total);
	buf_t out = {0}, bar = {0}, state = {0};
	char pos[64];
	const char *hint = "←/→ tabs · ↑/↓ scroll · PgUp/PgDn · g/G · q quit";

	maximum = (int)total - ch;
	if (maximum < 0)
		maximum = 0;
	if (scroll[tab] > maximum)
		scroll[tab] = maximum;
	if (scroll[tab] < 0)
		scroll[tab] = 0;
	off = scroll[tab];

	buf_adds(&out, "\033[H");
	border(&out, "┌", "┐", "rspeak — guide");
	buf_adds(&out, "\n");
	for (int i = 0; i < 5; i++) {
		const char *name = tab_name(i);

		if (i == tab) {
			if (*V_)
				buf_printf(&bar, "%s %s %s", V_, name, R_);
			else
				buf_printf(&bar, ">%s<", name);
		} else {
			buf_printf(&bar, "%s %s %s", D_, name, R_);
		}
		n += (int)length(name) + 2;
	}
	buf_printf(&out, "%s│%s %s%*s %s│%s\n", D_, R_, bar.s, inner - n > 0 ? inner - n : 0, "", D_, R_);
	border(&out, "├", "┤", NULL);
	buf_adds(&out, "\n");
	for (int i = 0; i < ch; i++) {
		if (off + i < (int)total)
			line(&out, r[off + i].kind, r[off + i].txt);
		else
			line(&out, 'T', "");
		buf_adds(&out, "\n");
	}
	border(&out, "├", "┤", NULL);
	buf_adds(&out, "\n");
	{
		int bottom = off + ch > (int)total ? (int)total : off + ch;

		snprintf(pos, sizeof pos, "lines %d-%d/%zu", off + 1, bottom, total);
	}
	buf_adds(&state, hint);
	if ((int)(length(hint) + length(pos) + 3) <= inner)
		buf_printf(&state, "%*s%s", inner - (int)length(hint) - (int)length(pos), "", pos);
	{
		size_t b = bytes_of(state.s, (size_t)inner);
		int pad = inner - (int)length(state.s) > 0 ? inner - (int)length(state.s) : 0;

		buf_printf(&out, "%s│ %.*s%*s │%s\n", D_, (int)b, state.s, pad, "", R_);
	}
	border(&out, "└", "┘", NULL);
	buf_adds(&out, "\033[J");
	write_all(1, out.s, out.n);
	for (size_t i = 0; i < total; i++)
		free(r[i].txt);
	free(r);
	buf_free(&out);
	buf_free(&bar);
	buf_free(&state);
	return maximum;
}

/* One byte from the terminal within ms milliseconds: -1 timeout, -2 end. */
static int tty_bytes(int ms)
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

enum { K_NONE, K_TIMEOUT, K_QUIT, K_UP, K_DOWN, K_RIGHT, K_LEFT, K_TAB, K_BACKTAB, K_PGUP, K_PGDN, K_HOME, K_EOF };

static int key_read(int *digit)
{
	int c = tty_bytes(300), d, e;

	*digit = 0;
	if (c == -1)
		return K_TIMEOUT;
	if (c == -2)
		return K_QUIT;
	switch (c) {
	case 27:
		d = tty_bytes(50);
		if (d < 0)
			return K_QUIT;
		e = tty_bytes(50);
		if (d == '[' || d == 'O') {
			switch (e) {
			case 'A': return K_UP;
			case 'B': return K_DOWN;
			case 'C': return K_RIGHT;
			case 'D': return K_LEFT;
			case 'H': return K_HOME;
			case 'F': return K_EOF;
			case 'Z': return K_BACKTAB;
			default: break;
			}
			if (d == '[' && e >= '0' && e <= '9') {
				int x;

				/* «ESC [ n ~»: 5 PgUp, 6 PgDn, 1/7 Home, 4/8 End */
				while ((x = tty_bytes(50)) >= 0 && x != '~')
					;
				switch (e) {
				case '5': return K_PGUP;
				case '6': return K_PGDN;
				case '1': case '7': return K_HOME;
				case '4': case '8': return K_EOF;
				default: return K_NONE;
				}
			}
		}
		return K_NONE;
	case 'q': case 'Q': return K_QUIT;
	case '\t': return K_TAB;
	case 'h': return K_LEFT;
	case 'l': case '\n': case '\r': return K_RIGHT;
	case 'j': return K_DOWN;
	case 'k': return K_UP;
	case ' ': return K_PGDN;
	case 'b': return K_PGUP;
	case 'g': return K_HOME;
	case 'G': return K_EOF;
	default:
		if (c >= '1' && c <= '9') {
			*digit = c - '0';
			return K_NONE;
		}
		return K_NONE;
	}
}

static bool tabbed_help(void)
{
	struct termios t;
	struct sigaction sa = {0};
	static const char start[] = "\033[?1049h\033[?25l";

	tty = open("/dev/tty", O_RDWR | O_CLOEXEC | O_NOCTTY);
	if (tty < 0)
		return false;
	if (!size(&TH, &TW) || TW < 44 || TH < 10 || tcgetattr(tty, &saved) < 0) {
		close(tty);
		tty = -1;
		return false;
	}
	colours(!getenv("NO_COLOR"));
	tab = 0;
	memset(scroll, 0, sizeof scroll);
	sa.sa_handler = on_signal;
	sigaction(SIGINT, &sa, NULL);
	sigaction(SIGTERM, &sa, NULL);
	sigaction(SIGHUP, &sa, NULL);
	t = saved;
	t.c_lflag &= ~(tcflag_t)(ECHO | ICANON);
	t.c_cc[VMIN] = 1;
	t.c_cc[VTIME] = 0;
	tcsetattr(tty, TCSAFLUSH, &t);
	write_all(1, start, sizeof start - 1);
	draw();
	while (!stop_requested) {
		int digit, k = key_read(&digit), ch = TH - 7;

		if (stop_requested || k == K_QUIT)
			break;
		if (k == K_TIMEOUT) {
			int r, c;

			/* redraw if the window has changed size */
			if (size(&r, &c) && (r != TH || c != TW)) {
				TH = r;
				TW = c;
				if (TW < 44 || TH < 10)
					break;
				draw();
			}
			continue;
		}
		switch (k) {
		case K_LEFT: case K_BACKTAB: tab = (tab + 4) % 5; break;
		case K_RIGHT: case K_TAB: tab = (tab + 1) % 5; break;
		case K_UP: scroll[tab]--; break;
		case K_DOWN: scroll[tab]++; break;
		case K_PGUP: scroll[tab] -= ch; break;
		case K_PGDN: scroll[tab] += ch; break;
		case K_HOME: scroll[tab] = 0; break;
		case K_EOF: scroll[tab] = 999999; break;
		default:
			if (digit >= 1 && digit <= 5)
				tab = digit - 1;
			else
				continue;
		}
		draw();
	}
	restore();
	close(tty);
	tty = -1;
	return true;
}

static bool in_path(const char *prog)
{
	const char *path = getenv("PATH");
	char *copy, *save = NULL;
	bool found = false;

	if (!path)
		path = "/usr/bin:/bin";
	copy = xstrdup(path);
	for (char *d = strtok_r(copy, ":", &save); d && !found; d = strtok_r(NULL, ":", &save)) {
		char *p = xasprintf("%s/%s", d, prog);

		found = access(p, X_OK) == 0;
		free(p);
	}
	free(copy);
	return found;
}

void rspeak_help(void)
{
	bool colour = !getenv("NO_COLOR");
	int lines = 0, columns = 80;
	const char *pager = getenv("PAGER");
	FILE *f;

	if (!isatty(0) || !isatty(1)) {
		page(stdout, false, 80);
		return;
	}
	if (tabbed_help())
		return;
	tty = open("/dev/tty", O_RDWR | O_CLOEXEC | O_NOCTTY);
	if (tty >= 0) {
		size(&lines, &columns);
		close(tty);
		tty = -1;
	}
	fflush(stdout);
	if (pager && *pager)
		f = popen(pager, "w");
	else if (in_path("less"))
		f = popen("less -R -F -X", "w");
	else
		f = NULL;
	if (!f) {
		page(stdout, colour, columns);
		return;
	}
	signal(SIGPIPE, SIG_IGN);
	page(f, colour, columns);
	pclose(f);
}
