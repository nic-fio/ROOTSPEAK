/* RootSpeak - Advanced Messaging System for Linux
 * The TUI for administrators: rspeak without arguments in a terminal.
 *
 * It reads the message store with the same functions as rspeak list and rspeak status, and every
 * action (send, revocation, reminder, purge) is the command itself, run in
 * a child process whose output is shown: the TUI has no way of its own to
 * do things, and no states of its own (only sent, delivered, confirmed;
 * revoked and expired as properties). */
#include "rspeak.h"

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


/* ---- terminal ---- */

static int tty = -1, TH, TW;
static struct termios saved;
static volatile sig_atomic_t stop_requested;
static bool colour;
static const char *R_ = "", *B_ = "", *D_ = "", *G_ = "", *Y_ = "", *C_ = "", *V_ = "", *VE = "", *GI = "", *RO = "",
		  *GR = "";

static void on_signal(int s)
{
	(void)s;
	stop_requested = 1;
}

static void colours(bool si)
{
	colour = si;
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

static bool size(int *r, int *c)
{
	struct winsize ws;

	if (ioctl(tty, TIOCGWINSZ, &ws) < 0 || !ws.ws_row || !ws.ws_col)
		return false;
	*r = ws.ws_row;
	*c = ws.ws_col;
	return true;
}

static void tui_mode(void)
{
	struct termios t = saved;
	static const char start[] = "\033[?1049h\033[?25l";

	/* no echo, no canonical mode; without IXON, Ctrl+S reaches the TUI */
	t.c_lflag &= ~(tcflag_t)(ECHO | ICANON);
	t.c_iflag &= ~(tcflag_t)(IXON | ICRNL);
	t.c_cc[VMIN] = 1;
	t.c_cc[VTIME] = 0;
	tcsetattr(tty, TCSAFLUSH, &t);
	write_all(1, start, sizeof start - 1);
}

static void normal_mode(void)
{
	static const char fine[] = "\033[?25h\033[?1049l";

	tcsetattr(tty, TCSAFLUSH, &saved);
	write_all(1, fine, sizeof fine - 1);
}

/* ---- text with colours: visible lengths ---- */

static int visible(const char *s)
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

/* Appends s cut or padded to w visible characters (the colours are kept). */
static void column(buf_t *out, const char *s, int w)
{
	int n = 0;
	bool cut = false;

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
				cut = true;
				break;
			}
			n++;
		}
		buf_addc(out, *s++);
	}
	if (cut || colour)
		buf_adds(out, R_);
	for (; n < w; n++)
		buf_addc(out, ' ');
}

/* ---- the frame ---- */

typedef struct {
	strv_t lines; /* content lines, with colours */
	char *title_text, *right, *keys;
	int cur_row, cur_col; /* cursor to show (0: hidden) */
} screen_t;

static void screen_line(screen_t *s, const char *fmt, ...) ATTR_PRINTF(2, 3);
static void screen_line(screen_t *s, const char *fmt, ...)
{
	buf_t b = {0};
	va_list ap;

	va_start(ap, fmt);
	buf_vprintf(&b, fmt, ap);
	va_end(ap);
	strv_add_own(&s->lines, b.s ? b.s : xstrdup(""));
}

static void repeat(buf_t *out, const char *c, int n)
{
	for (int i = 0; i < n; i++)
		buf_adds(out, c);
}

static void draw(screen_t *s)
{
	buf_t o = {0};
	int inner = TW - 4, area = TH - 4;
	char *t = xasprintf("─ %s ", s->title_text ? s->title_text : ""), *d = s->right ? xasprintf(" %s ─", s->right) : xstrdup("");
	int rest = TW - 2 - visible(t) - visible(d);

	buf_adds(&o, "\033[H");
	buf_printf(&o, "%s┌%s%s%s%s%s", D_, R_, C_, t, R_, D_);
	repeat(&o, "─", rest > 0 ? rest : 0);
	buf_printf(&o, "%s%s%s┐%s\n", R_, GR, d, D_);
	buf_adds(&o, R_);
	for (int i = 0; i < area; i++) {
		buf_printf(&o, "%s│%s ", D_, R_);
		column(&o, i < (int)s->lines.n ? s->lines.v[i] : "", inner);
		buf_printf(&o, " %s│%s\n", D_, R_);
	}
	buf_printf(&o, "%s├", D_);
	repeat(&o, "─", TW - 2);
	buf_printf(&o, "┤%s\n%s│%s ", R_, D_, R_);
	column(&o, s->keys ? s->keys : "", inner);
	buf_printf(&o, " %s│%s\n%s└", D_, R_, D_);
	repeat(&o, "─", TW - 2);
	buf_printf(&o, "┘%s\033[J", R_);
	if (s->cur_row > 0)
		buf_printf(&o, "\033[%d;%dH\033[?25h", s->cur_row + 1, s->cur_col + 3);
	else
		buf_adds(&o, "\033[?25l");
	write_all(1, o.s, o.n);
	buf_free(&o);
	free(t);
	free(d);
}

static void screen_free(screen_t *s)
{
	strv_free(&s->lines);
	free(s->title_text);
	free(s->right);
	free(s->keys);
	memset(s, 0, sizeof *s);
}

/* ---- keys ---- */

enum {
	K_NONE = 0, K_TIMEOUT, K_EOF, K_UP, K_DOWN, K_RIGHT, K_LEFT, K_PGUP, K_PGDN, K_HOME, K_END, K_ENTER, K_ESC,
	K_TAB, K_BACKTAB, K_BACKSPACE, K_DEL, K_CTRL_E, K_CTRL_S, K_TEXT
};

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

/* One key; for K_TEXT the character (UTF-8) in car. */
static int key_read(int ms, char car[8])
{
	int c = tty_bytes(ms), d, e;

	car[0] = '\0';
	if (c == -1)
		return K_TIMEOUT;
	if (c == -2)
		return K_EOF;
	if (c == 27) {
		d = tty_bytes(40);
		if (d < 0)
			return K_ESC;
		if (d != '[' && d != 'O')
			return K_NONE;
		e = tty_bytes(40);
		switch (e) {
		case 'A': return K_UP;
		case 'B': return K_DOWN;
		case 'C': return K_RIGHT;
		case 'D': return K_LEFT;
		case 'H': return K_HOME;
		case 'F': return K_END;
		case 'Z': return K_BACKTAB;
		default: break;
		}
		if (d == '[' && e >= '0' && e <= '9') {
			int x;

			while ((x = tty_bytes(40)) >= 0 && x != '~')
				;
			switch (e) {
			case '5': return K_PGUP;
			case '6': return K_PGDN;
			case '3': return K_DEL;
			case '1': case '7': return K_HOME;
			case '4': case '8': return K_END;
			default: return K_NONE;
			}
		}
		return K_NONE;
	}
	switch (c) {
	case '\r': case '\n': return K_ENTER;
	case '\t': return K_TAB;
	case 127: case 8: return K_BACKSPACE;
	case 5: return K_CTRL_E;
	case 19: return K_CTRL_S;
	default: break;
	}
	if (c < 32)
		return K_NONE;
	car[0] = (char)c;
	{
		int n = c >= 0xf0 ? 3 : c >= 0xe0 ? 2 : c >= 0xc0 ? 1 : 0;

		for (int i = 1; i <= n; i++) {
			int x = tty_bytes(40);

			if (x < 0)
				break;
			car[i] = (char)x;
			car[i + 1] = '\0';
		}
		car[n + 1] = '\0';
	}
	return K_TEXT;
}

/* ---- commands in a child process ---- */

typedef struct {
	int argc;
	char **argv;
	const char *arg;
	void (*one)(const char *);
} launch_t;

/* Runs the command in a child, with stdin (if any) and with the output, error
 * output included, collected in out. Result: 0 on success, otherwise the exit code. */
static int execute(const launch_t *l, const buf_t *in, buf_t *out)
{
	int pin[2], pout[2], state;
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
		/* the pipe ends the parent uses: left open here, the command would
		 * never see the end of the text */
		close(pin[1]);
		close(pout[0]);
		dup2(pin[0], 0);
		dup2(pout[1], 1);
		dup2(pout[1], 2);
		if (l->one)
			l->one(l->arg);
		else
			cmd_send(l->argc, l->argv);
		fflush(stdout);
		fflush(stderr);
		_exit(0);
	}
	close(pin[0]);
	close(pout[1]);
	if (in && in->n)
		write_all(pin[1], in->s, in->n);
	close(pin[1]);
	read_fd(pout[0], 1 << 20, out);
	close(pout[0]);
	while (waitpid(pid, &state, 0) < 0)
		if (errno != EINTR)
			return -1;
	return WIFEXITED(state) ? WEXITSTATUS(state) : -1;
}

/* ---- data ---- */

typedef struct {
	summary_t *v;
	size_t n;
	char time_now[16];
} list_t;

static void list_free(list_t *e)
{
	for (size_t i = 0; i < e->n; i++)
		summary_free(&e->v[i]);
	free(e->v);
	e->v = NULL;
	e->n = 0;
}

static bool contains(const char *txt, const char *search)
{
	size_t n = strlen(search);

	if (!n)
		return true;
	for (const char *p = txt; *p; p++)
		if (!strncasecmp(p, search, n))
			return true;
	return false;
}

/* The messages, newest first; with a filter, only those that contain it. */
static void load_list(list_t *e, const char *filter)
{
	strv_t ids = {0};
	time_t time_now = now();
	struct tm tm;

	list_free(e);
	mailboxes_empty();
	message_list(&ids);
	e->v = xmalloc((ids.n ? ids.n : 1) * sizeof *e->v);
	for (size_t i = ids.n; i-- > 0;) {
		long long id;

		read_number(ids.v[i], &id);
		if (!summarise(id, &e->v[e->n]))
			continue;
		if (!contains(e->v[e->n].m.body, filter) && !contains(e->v[e->n].m.title, filter)) {
			summary_free(&e->v[e->n]);
			continue;
		}
		e->n++;
	}
	strv_free(&ids);
	localtime_r(&time_now, &tm);
	strftime(e->time_now, sizeof e->time_now, "%H:%M:%S", &tm);
}

/* Bar of w marks: confirmed █ green, delivered ▒ yellow, sent ░ red. */
static void bar(buf_t *o, const summary_t *r, int w)
{
	int tot = r->confirmed + r->delivered + r->sent, a, c, b;

	if (tot <= 0)
		tot = 1;
	a = r->confirmed * w / tot;
	c = r->sent * w / tot;
	if (r->sent && !c)
		c = 1;
	if (r->delivered && a + c == w && a > 0)
		a--;
	b = w - a - c;
	buf_adds(o, VE);
	repeat(o, "█", a);
	buf_adds(o, GI);
	repeat(o, "▒", b);
	buf_adds(o, RO);
	repeat(o, "░", c);
	buf_adds(o, R_);
}

static void coloured_summary(buf_t *o, const summary_t *r)
{
	const char *sep = "";

	if (!r->delivered && !r->sent) {
		buf_adds(o, VE);
		buf_printf(o, "all confirmed (%d)", r->confirmed);
		buf_adds(o, R_);
		return;
	}
	if (r->confirmed) {
		buf_adds(o, VE);
		buf_printf(o, "%d confirmed", r->confirmed);
		buf_adds(o, R_);
		sep = " · ";
	}
	if (r->delivered) {
		buf_printf(o, "%s%s", sep, GI);
		buf_printf(o, "%d delivered", r->delivered);
		buf_adds(o, R_);
		sep = " · ";
	}
	if (r->sent) {
		buf_printf(o, "%s%s", sep, RO);
		buf_printf(o, "%d sent", r->sent);
		buf_adds(o, R_);
	}
}

static void legend(buf_t *o)
{
	buf_printf(o, "%s█%s ", VE, R_);
	buf_adds(o, "confirmed");
	buf_printf(o, "   %s▒%s ", GI, R_);
	buf_adds(o, "delivered");
	buf_printf(o, "   %s░%s ", RO, R_);
	buf_adds(o, "sent");
}

/* ---- overlays: confirmation, message, question ---- */

/* Draws a window in the middle of the screen on top of what is there. */
static void dialog(screen_t *s, const char *title_text, const strv_t *txt, const char *buttons)
{
	int w = 60, h = (int)txt->n + 5, x, y;
	strv_t *r = &s->lines;
	buf_t line = {0};

	for (size_t i = 0; i < txt->n; i++)
		if (visible(txt->v[i]) + 6 > w)
			w = visible(txt->v[i]) + 6;
	if (w > TW - 8)
		w = TW - 8;
	x = (TW - 4 - w) / 2;
	y = (TH - 4 - h) / 2;
	if (y < 1)
		y = 1;
	while ((int)r->n < y + h)
		strv_add(r, "");
	for (int i = 0; i < h; i++) {
		buf_clear(&line);
		buf_printf(&line, "%*s", x, "");
		if (i == 0) {
			char *t = xasprintf("─ %s ", title_text);

			buf_printf(&line, "%s┌%s", B_, t);
			repeat(&line, "─", w - 2 - visible(t));
			buf_printf(&line, "┐%s", R_);
			free(t);
		} else if (i == h - 1) {
			buf_printf(&line, "%s└", B_);
			repeat(&line, "─", w - 2);
			buf_printf(&line, "┘%s", R_);
		} else {
			const char *c = i >= 2 && i - 2 < (int)txt->n ? txt->v[i - 2] : i == h - 2 ? buttons : "";

			buf_printf(&line, "%s│%s  ", B_, R_);
			column(&line, c, w - 6);
			buf_printf(&line, "  %s│%s", B_, R_);
		}
		free(r->v[y + i]);
		r->v[y + i] = xstrdup(line.s);
	}
	buf_free(&line);
}

/* Draws a window over the base screen, leaving the base intact:
 * a later window does not overlap the previous one. */
static void overlay(const screen_t *base, const char *title_text, const strv_t *txt, const char *buttons,
		       char *keys)
{
	screen_t s = {0};

	for (size_t i = 0; i < base->lines.n; i++)
		strv_add(&s.lines, base->lines.v[i]);
	s.title_text = xstrdup(base->title_text ? base->title_text : "");
	s.right = base->right ? xstrdup(base->right) : NULL;
	s.keys = keys;
	dialog(&s, title_text, txt, buttons);
	draw(&s);
	screen_free(&s);
}

/* Asks for a confirmation over the screen; true if the administrator confirms. */
static bool confirm(screen_t *s, const char *title_text, const strv_t *txt)
{
	char car[8];
	char *p = xasprintf("%s y  %s %s     %s n  %s %s", V_, "Confirm", R_, D_, "Cancel", R_);

	overlay(s, title_text, txt, p,
		   xasprintf("%sy%s %s   %sn%s %s %sEsc%s %s", G_, R_, "confirm", G_, R_, "or", G_, R_, "cancel"));
	free(p);
	for (;;) {
		int k = key_read(500, car);

		if (stop_requested || k == K_EOF || k == K_ESC || (k == K_TEXT && (car[0] == 'n' || car[0] == 'N')))
			return false;
		if (k == K_TEXT && (car[0] == 'y' || car[0] == 'Y'))
			return true;
	}
}

/* Shows the result of a command until a key is pressed. */
static void outcome(screen_t *s, const char *title_text, const buf_t *exit_status)
{
	strv_t lines = {0};
	char car[8];
	buf_t clean = {0};

	clean_text(exit_status->s ? exit_status->s : "", exit_status->n, &clean);
	for (char *p = clean.s; p && *p;) {
		size_t len = strcspn(p, "\n");
		char *r = xmalloc(len + 1);

		memcpy(r, p, len);
		r[len] = '\0';
		strv_add_own(&lines, r);
		p += len;
		if (*p)
			p++;
	}
	if (!lines.n)
		strv_add(&lines, "Done.");
	overlay(s, title_text, &lines, "any key to continue", xstrdup("any key to continue"));
	while (key_read(500, car) == K_TIMEOUT && !stop_requested)
		;
	strv_free(&lines);
	buf_free(&clean);
}

/* A line of text asked for over the screen; NULL if cancelled. */
static char *question(screen_t *base, const char *title_text, const char *explanation, const char *initial)
{
	buf_t v = {0};
	char car[8];

	buf_adds(&v, initial);
	for (;;) {
		screen_t s = {0};
		strv_t t = {0};
		char *field;
		int k;

		for (size_t i = 0; i < base->lines.n; i++)
			strv_add(&s.lines, base->lines.v[i]);
		s.title_text = xstrdup(base->title_text);
		s.right = base->right ? xstrdup(base->right) : NULL;
		strv_add(&t, explanation);
		strv_add(&t, "");
		field = xasprintf("[ %s%s ]", v.s ? v.s : "", colour ? "\033[7m \033[0m" : "_");
		strv_add_own(&t, field);
		dialog(&s, title_text, &t, "");
		s.keys = xasprintf("%sEnter%s %s   %sEsc%s %s", G_, R_, "confirm", G_, R_, "cancel");
		draw(&s);
		screen_free(&s);
		strv_free(&t);
		k = key_read(500, car);
		if (stop_requested || k == K_EOF || k == K_ESC) {
			buf_free(&v);
			return NULL;
		}
		if (k == K_ENTER)
			return v.s ? v.s : xstrdup("");
		if (k == K_BACKSPACE && v.n) {
			do
				v.n--;
			while (v.n && ((unsigned char)v.s[v.n] & 0xc0) == 0x80);
			v.s[v.n] = '\0';
		} else if (k == K_TEXT && v.n < 200) {
			buf_adds(&v, car);
		}
	}
}

/* ---- actions ---- */

static void action(screen_t *s, const char *title_text, void (*fn)(const char *), const char *arg)
{
	launch_t l = {.one = fn, .arg = arg};
	buf_t out = {0};

	execute(&l, NULL, &out);
	outcome(s, title_text, &out);
	buf_free(&out);
}

static void revoke_message(screen_t *s, const summary_t *r)
{
	strv_t t = {0};
	char *id = xasprintf("%lld", r->id), *title_text = xasprintf("Revoke message %lld?", r->id);
	buf_t b = {0};

	buf_printf(&b, "«%s» · ", *r->m.title ? r->m.title : "no title");
	summary_text(r, &b);
	strv_add(&t, b.s);
	strv_add(&t, "");
	strv_add(&t, "Whoever has not seen it yet will not see it;");
	strv_add(&t, "open dialogs and questions close by themselves.");
	if (confirm(s, title_text, &t))
		action(s, title_text, cmd_revoke, id);
	strv_free(&t);
	buf_free(&b);
	free(id);
	free(title_text);
}

static void remind(screen_t *s, const summary_t *r)
{
	strv_t t = {0};
	char *id = xasprintf("%lld", r->id), *title_text = xasprintf("Remind message %lld?", r->id);
	char *line = r->delivered == 1 ? xstrdup("1 recipient has not confirmed yet.")
					: xasprintf("%d recipients have not confirmed yet.", r->delivered);

	strv_add(&t, line);
	strv_add(&t, "");
	strv_add(&t, "They are asked again now: at the next prompt");
	strv_add(&t, "and with the dialog on the desktop.");
	if (confirm(s, title_text, &t))
		action(s, title_text, cmd_remind, id);
	strv_free(&t);
	free(id);
	free(title_text);
	free(line);
}

static void purge(screen_t *s)
{
	char *dur = question(s, "Delete old messages", "Delete the messages sent more than (for example 90d, 12h):",
			    "90d");
	strv_t t = {0};
	char *line;

	if (!dur)
		return;
	line = xasprintf("Messages older than %s, with copies and confirmations.", dur);
	strv_add(&t, line);
	strv_add(&t, "The events stay in the system log.");
	if (confirm(s, "Delete old messages?", &t))
		action(s, "Delete old messages", cmd_purge, dur);
	strv_free(&t);
	free(line);
	free(dur);
}

/* ---- the list ---- */

static void list_keys(screen_t *s)
{
	s->keys = xasprintf("%sEnter%s %s   %sn%s %s   %sr%s %s   %sm%s %s   %sp%s %s   %s/%s %s   %s?%s %s   %sq%s %s",
			     G_, R_, "open", G_, R_, "new", G_, R_, "revoke", G_, R_, "remind", G_, R_, "purge",
			     G_, R_, "search", G_, R_, "keys", G_, R_, "quit");
}

static void list_lines(screen_t *s, const list_t *e, size_t sel, size_t first, const char *filter)
{
	int inner = TW - 4, fw = inner >= 106 ? 42 : 0, bw = 12;
	int tw = inner - (1 + 3 + 2 + 11 + 2) - (bw + 2) - (fw ? fw + 2 : 7);
	int area = TH - 4 - 3;
	buf_t b = {0};

	if (tw < 10)
		tw = 10;
	screen_line(s, "%s", "");
	buf_printf(&b, " %s%3s  %-11s  ", Y_, "ID", "DATE");
	column(&b, "MESSAGE", tw);
	buf_printf(&b, "  %s%s", "RECIPIENTS", R_);
	strv_add(&s->lines, b.s);
	buf_clear(&b);
	if (!e->n)
		screen_line(s, "   %s%s%s", GR, *filter ? "No message contains the search text." : "No messages sent.", R_);
	for (size_t i = first; i < e->n && (int)(i - first) < area; i++) {
		const summary_t *r = &e->v[i];
		char data[32], id[24];
		buf_t t = {0}, f = {0};

		short_date((time_t)r->m.date, data);
		snprintf(id, sizeof id, "%lld", r->id);
		if (r->revoked)
			buf_printf(&t, "%s%s%s", GR, "[revoked] ", R_);
		if (r->expired)
			buf_printf(&t, "%s%s%s", GR, "[expired] ", R_);
		if (*r->m.title)
			buf_printf(&t, "%s%s%s · ", B_, r->m.title, R_);
		buf_add(&t, r->m.body, strcspn(r->m.body, "\n"));
		buf_printf(&b, "%s%3s  %-11s  ", i == sel ? ">" : " ", id, data);
		column(&b, t.s, tw);
		buf_adds(&b, "  ");
		bar(&b, r, bw);
		buf_adds(&b, "  ");
		if (fw)
			coloured_summary(&f, r);
		else
			buf_printf(&f, "%d/%d", r->confirmed, r->confirmed + r->delivered + r->sent);
		buf_adds(&b, f.s);
		if (i == sel && colour) {
			/* the selected row, in reverse video and without the other colours */
			buf_t cleaned = {0}, c = {0};

			for (const char *p = b.s; *p;) {
				if (*p == '\033') {
					while (*p && *p != 'm')
						p++;
					if (*p)
						p++;
					continue;
				}
				buf_addc(&cleaned, *p++);
			}
			buf_adds(&c, V_);
			column(&c, cleaned.s, inner);
			strv_add(&s->lines, c.s);
			buf_free(&cleaned);
			buf_free(&c);
		} else {
			strv_add(&s->lines, b.s);
		}
		buf_clear(&b);
		buf_free(&t);
		buf_free(&f);
	}
	while ((int)s->lines.n < TH - 5)
		strv_add(&s->lines, "");
	legend(&b);
	if (*filter) {
		buf_printf(&b, "      %s", GR);
		buf_printf(&b, "search: «%s» (Esc to clear)", filter);
		buf_adds(&b, R_);
	}
	strv_add(&s->lines, b.s);
	buf_free(&b);
}

/* ---- the detail ---- */

static void newline(const char *txt, int w, strv_t *out)
{
	for (const char *p = txt; *p;) {
		size_t len = strcspn(p, "\n");
		buf_t line = {0};

		buf_add(&line, p, len);
		/* long lines: wrap at spaces */
		while (visible(line.s) > w) {
			size_t cut = 0, c = 0;

			for (size_t k = 0; k < line.n && (int)c <= w; k++) {
				if (((unsigned char)line.s[k] & 0xc0) != 0x80)
					c++;
				if (line.s[k] == ' ' && (int)c <= w)
					cut = k;
			}
			if (!cut)
				for (size_t k = 0, cc = 0; k < line.n; k++)
					if (((unsigned char)line.s[k] & 0xc0) != 0x80 && (int)++cc > w) {
						cut = k;
						break;
					}
			{
				char *a = xmalloc(cut + 1);

				memcpy(a, line.s, cut);
				a[cut] = '\0';
				strv_add_own(out, a);
			}
			{
				buf_t rest = {0};

				buf_adds(&rest, line.s + cut + (line.s[cut] == ' '));
				buf_free(&line);
				line = rest;
			}
		}
		strv_add(out, line.s ? line.s : "");
		buf_free(&line);
		p += len;
		if (*p)
			p++;
	}
}

static void history(long long id, strv_t *out)
{
	char *arg = xasprintf("%lld", id);
	launch_t l = {.one = cmd_log, .arg = arg};
	buf_t o = {0}, p = {0};
	bool before = true;

	execute(&l, NULL, &o);
	clean_text(o.s ? o.s : "", o.n, &p);
	for (char *r = p.s; r && *r;) {
		size_t len = strcspn(r, "\n");

		if (!before) {
			char *x = xmalloc(len + 1);

			memcpy(x, r, len);
			x[len] = '\0';
			strv_add_own(out, x);
		}
		before = false;
		r += len;
		if (*r)
			r++;
	}
	free(arg);
	buf_free(&o);
	buf_free(&p);
}

/* The detail of a message: recipients and history. It is reread every 3
 * seconds and after every action; Esc leaves it. */
static void detail(long long id, const char *list_time)
{
	int tab = 0, scroll = 0, rounds = 0;
	char car[8], time_now[16];
	bool read_item = true, quit = false;
	summary_t r = {0};
	recipients_t d = {0};
	strv_t body_text = {0}, sto = {0};

	snprintf(time_now, sizeof time_now, "%s", list_time);
	while (!quit && !stop_requested) {
		screen_t s = {0};
		char data[32], exp_str[32];
		buf_t b = {0};
		int area, k, lines;

		if (read_item) {
			summary_free(&r);
			recipients_free(&d);
			strv_free(&body_text);
			strv_free(&sto);
			mailboxes_empty();
			if (!summarise(id, &r))
				break;
			recipients(id, &r.m, &d);
			newline(r.m.body, TW - 8, &body_text);
			if (tab == 1)
				history(id, &sto);
			read_item = false;
		}
		s.title_text = *r.m.title ? xasprintf("Message %lld · %s", id, r.m.title) : xasprintf("Message %lld", id);
		s.right = xasprintf("updated at %s", time_now);
		short_date((time_t)r.m.date, data);
		buf_printf(&b, " %s%s%s · %s · ", B_, *r.m.title ? r.m.title : "no title", R_, data);
		buf_printf(&b, "from %s", r.m.from);
		if (r.m.expires) {
			short_date((time_t)r.m.expires, exp_str);
			buf_adds(&b, " · ");
			buf_printf(&b, r.expired ? "expired on %s" : "expires on %s", exp_str);
		}
		if (r.revoked) {
			short_date((time_t)revocation_date(id), exp_str);
			buf_printf(&b, " · %s", RO);
			buf_printf(&b, "revoked on %s", exp_str);
			buf_adds(&b, R_);
		}
		strv_add(&s.lines, b.s);
		buf_clear(&b);
		for (size_t i = 0; i < body_text.n && i < 6; i++)
			screen_line(&s, " %s│%s %s", D_, R_, i == 5 && body_text.n > 6 ? "…" : body_text.v[i]);
		screen_line(&s, "%s", "");
		{
			char *td = xasprintf(" %s (%zu) ", "Recipients", d.n), *ts = xasprintf(" %s ", "History");

			buf_printf(&b, " %s%s%s %s%s%s    ", tab == 0 ? V_ : D_, td, R_, tab == 1 ? V_ : D_, ts, R_);
			bar(&b, &r, 12);
			buf_adds(&b, "  ");
			coloured_summary(&b, &r);
			strv_add(&s.lines, b.s);
			buf_clear(&b);
			free(td);
			free(ts);
		}
		screen_line(&s, "%s", "");
		area = TH - 4 - (int)s.lines.n;
		if (tab == 0) {
			buf_t u = {0};

			lines = (int)d.n;
			buf_adds(&b, Y_);
			column(&b, "USER", 14);
			buf_printf(&b, "%s%s", "STATE", R_);
			screen_line(&s, " %s", b.s);
			buf_clear(&b);
			buf_free(&u);
			area--;
		} else {
			lines = (int)sto.n;
		}
		if (scroll > lines - area)
			scroll = lines - area;
		if (scroll < 0)
			scroll = 0;
		for (int i = scroll; i < lines && i - scroll < area; i++) {
			if (tab == 0) {
				const char *col = d.v[i].state == CONFIRMED ? VE : d.v[i].state == DELIVERED ? GI : RO;
				buf_t u = {0};

				column(&u, d.v[i].user, 13);
				screen_line(&s, " %s %s%s%s", u.s, col, d.v[i].line, R_);
				buf_free(&u);
			} else {
				screen_line(&s, " %s", sto.v[i]);
			}
		}
		if (tab == 1 && !sto.n)
			screen_line(&s, " %s%s%s", GR, "No events in the system log.", R_);
		s.keys = xasprintf("%sTab%s %s   %s↑/↓%s %s   %sm%s %s   %sr%s %s   %sEsc%s %s", G_, R_, "recipients/history",
				    G_, R_, "scroll", G_, R_, "remind", G_, R_, "revoke", G_, R_, "back");
		draw(&s);
		k = key_read(500, car);
		if (k == K_TIMEOUT) {
			int r2, c2;

			if (size(&r2, &c2) && (r2 != TH || c2 != TW)) {
				TH = r2;
				TW = c2;
				read_item = true;
			}
			/* automatic refresh every 3 seconds */
			if (++rounds >= 6) {
				time_t t = now();
				struct tm tm;

				rounds = 0;
				localtime_r(&t, &tm);
				strftime(time_now, sizeof time_now, "%H:%M:%S", &tm);
				read_item = true;
			}
		} else if (k == K_EOF || k == K_ESC || (k == K_TEXT && car[0] == 'q')) {
			quit = true;
		} else if (k == K_TAB || k == K_BACKTAB) {
			tab = 1 - tab;
			scroll = 0;
			read_item = true;
		} else if (k == K_UP) {
			scroll--;
		} else if (k == K_DOWN) {
			scroll++;
		} else if (k == K_PGUP) {
			scroll -= area;
		} else if (k == K_PGDN) {
			scroll += area;
		} else if (k == K_TEXT && car[0] == 'r' && !r.revoked) {
			revoke_message(&s, &r);
			read_item = true;
		} else if (k == K_TEXT && car[0] == 'm' && !r.revoked && !r.expired && r.delivered) {
			remind(&s, &r);
			read_item = true;
		}
		screen_free(&s);
		buf_free(&b);
	}
	summary_free(&r);
	recipients_free(&d);
	strv_free(&body_text);
	strv_free(&sto);
}

/* ---- new message ---- */

typedef struct {
	buf_t field[3]; /* To, title, expiry */
	strv_t txt;   /* lines of the text */
	int active;     /* 0-2 fields, 3 text */
	size_t pos;     /* cursor in the field (byte) */
	size_t line, col; /* cursor in the text (line, byte) */
	char *preview_to, *preview_expiry;
} form_t;

static void form_free(form_t *m)
{
	for (int i = 0; i < 3; i++)
		buf_free(&m->field[i]);
	strv_free(&m->txt);
	free(m->preview_to);
	free(m->preview_expiry);
}

static void form_text(const form_t *m, buf_t *out)
{
	for (size_t i = 0; i < m->txt.n; i++)
		buf_printf(out, "%s%s", i ? "\n" : "", m->txt.v[i]);
}

static void text_from(form_t *m, const char *s)
{
	strv_free(&m->txt);
	for (const char *p = s;;) {
		size_t len = strcspn(p, "\n");
		char *r = xmalloc(len + 1);

		memcpy(r, p, len);
		r[len] = '\0';
		strv_add_own(&m->txt, r);
		p += len;
		if (!*p)
			break;
		p++;
	}
	/* no extra trailing empty lines */
	while (m->txt.n > 1 && !*m->txt.v[m->txt.n - 1]) {
		free(m->txt.v[--m->txt.n]);
	}
	m->line = m->txt.n - 1;
	m->col = strlen(m->txt.v[m->line]);
}

/* One step back or forward by a UTF-8 character in s. */
static size_t char_before(const char *s, size_t i)
{
	if (!i)
		return 0;
	do
		i--;
	while (i && ((unsigned char)s[i] & 0xc0) == 0x80);
	return i;
}

static size_t char_after(const char *s, size_t i)
{
	if (!s[i])
		return i;
	do
		i++;
	while (s[i] && ((unsigned char)s[i] & 0xc0) == 0x80);
	return i;
}

static void previews(form_t *m)
{
	launch_t l;
	buf_t o = {0};

	free(m->preview_to);
	m->preview_to = NULL;
	if (m->field[0].n) {
		l = (launch_t){.one = cmd_count_recipients, .arg = m->field[0].s};
		if (execute(&l, NULL, &o) == 0 && o.s) {
			long long n = 0;

			o.s[strcspn(o.s, "\n")] = '\0';
			read_number(o.s, &n);
			m->preview_to = n == 1 ? xstrdup("1 recipient") : xasprintf("%lld recipients", n);
		} else if (o.s) {
			buf_t p = {0};

			clean_text(o.s, o.n, &p);
			p.s[strcspn(p.s, "\n")] = '\0';
			m->preview_to = xasprintf("%s%s%s", RO, p.s, R_);
			buf_free(&p);
		}
	}
	buf_free(&o);
}

/* Opens the text in the editor of whoever runs rspeak (SUDO_USER), outside the TUI. */
static void editor(form_t *m)
{
	char path[] = "/tmp/rootspeak-testo-XXXXXX";
	int fd = mkstemp(path);
	buf_t t = {0};
	const char *who = getenv("SUDO_USER");
	struct passwd *pw = who && *who ? getpwnam(who) : NULL;
	pid_t pid;

	if (fd < 0)
		return;
	form_text(m, &t);
	buf_addc(&t, '\n');
	write_all(fd, t.s, t.n);
	/* the file belongs to the administrator, who opens it with their own editor */
	if (pw && geteuid() == 0 && fchown(fd, pw->pw_uid, pw->pw_gid) < 0)
		pw = NULL;
	close(fd);
	buf_free(&t);
	normal_mode();
	pid = fork();
	if (pid == 0) {
		const char *ed = getenv("VISUAL");

		if (!ed || !*ed)
			ed = getenv("EDITOR");
		signal(SIGINT, SIG_DFL);
		/* the editor runs with the administrator's identity, not as root */
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

		if (read_file(path, (size_t)RSPEAK_MAX_BYTES * 2, true, &b) == 0) {
			while (b.n && b.s[b.n - 1] == '\n')
				b.s[--b.n] = '\0';
			text_from(m, b.s ? b.s : "");
		}
		buf_free(&b);
	}
	unlink(path);
	tui_mode();
}

/* Sends: result true if sent (and the ID in *new_item). */
static bool send_message(screen_t *s, form_t *m, long long *new_item)
{
	strv_t t = {0};
	buf_t txt = {0}, out = {0};
	char *argv[10], *line;
	int argc = 0, r;
	launch_t l;
	bool ok = false;

	form_text(m, &txt);
	line = xasprintf("To: %s (%s)", m->field[0].s ? m->field[0].s : "",
			 m->preview_to ? m->preview_to : "?");
	strv_add_own(&t, line);
	if (m->field[1].n)
		strv_add_own(&t, xasprintf("Title: %s", m->field[1].s));
	if (m->field[2].n)
		strv_add_own(&t, xasprintf("Expires: %s", m->field[2].s));
	strv_add_own(&t, xasprintf("Text: %zu bytes", txt.n));
	if (!confirm(s, "Send the message?", &t)) {
		strv_free(&t);
		buf_free(&txt);
		return false;
	}
	{
		static char to[] = "--to", title[] = "--title", expires[] = "--expires", empty[] = "";

		argv[argc++] = to;
		argv[argc++] = m->field[0].s ? m->field[0].s : empty;
		if (m->field[1].n) {
			argv[argc++] = title;
			argv[argc++] = m->field[1].s;
		}
		if (m->field[2].n) {
			argv[argc++] = expires;
			argv[argc++] = m->field[2].s;
		}
	}
	argv[argc] = NULL;
	l = (launch_t){.argc = argc, .argv = argv};
	r = execute(&l, &txt, &out);
	outcome(s, r == 0 ? "Message sent" : "Sending result", &out);
	if (r == 0) {
		strv_t ids = {0};

		message_list(&ids);
		if (ids.n)
			read_number(ids.v[ids.n - 1], new_item);
		strv_free(&ids);
		ok = true;
	}
	strv_free(&t);
	buf_free(&txt);
	buf_free(&out);
	return ok;
}

static bool new_message(long long *new_item)
{
	form_t m = {0};
	char car[8];
	bool sent = false;
	static const char *const names[] = {"To", "Title", "Expires"};
	static const char *const help_items_tui[] = {"user, @group, all or online, separated by commas",
					    "optional, one line", "optional: 30m, 2h, 3d or a date"};

	strv_add(&m.txt, "");
	for (;;) {
		screen_t s = {0};
		int w = TW - 4 - 14, height = TH - 4 - 1 - 3 - 3 - 3, k;
		strv_t vis = {0};
		size_t cur_visible = 0, cur_col = 0;
		buf_t b = {0};

		if (w < 20)
			w = 20;
		if (height < 3)
			height = 3;
		s.title_text = xstrdup("New message");
		screen_line(&s, "%s", "");
		for (int i = 0; i < 3; i++) {
			buf_t v = {0};
			const char *extra = i == 0 && m.preview_to ? m.preview_to : "";

			column(&v, m.field[i].s ? m.field[i].s : "", w - 26);
			buf_printf(&b, " %s", i == m.active ? B_ : "");
			column(&b, names[i], 10);
			buf_printf(&b, "%s [ %s ]  %s%s%s", R_, v.s, GR, *extra ? extra : help_items_tui[i], R_);
			if (i == 0 && *extra)
				buf_printf(&b, "%s", R_);
			strv_add(&s.lines, b.s);
			buf_clear(&b);
			buf_free(&v);
			if (i == m.active) {
				size_t c = 0;

				for (size_t k2 = 0; k2 < m.pos; k2++)
					if (((unsigned char)m.field[i].s[k2] & 0xc0) != 0x80)
						c++;
				s.cur_row = (int)s.lines.n;
				s.cur_col = 1 + 10 + 3 + (int)c;
			}
		}
		/* the text, wrapped at the width of the box */
		for (size_t i = 0; i < m.txt.n; i++) {
			strv_t parts = {0};
			const char *line = m.txt.v[i];
			size_t start = 0;

			newline(*line ? line : " ", w - 2, &parts);
			for (size_t p = 0; p < parts.n; p++) {
				size_t len = strlen(parts.v[p]);

				if (i == m.line && m.col >= start && (m.col <= start + len || p == parts.n - 1)) {
					size_t c = 0;

					for (size_t k2 = start; k2 < m.col && k2 < strlen(line); k2++)
						if (((unsigned char)line[k2] & 0xc0) != 0x80)
							c++;
					cur_visible = vis.n;
					cur_col = c;
				}
				strv_add(&vis, *line ? parts.v[p] : "");
				start += len + 1;
			}
			strv_free(&parts);
		}
		{
			size_t first = cur_visible >= (size_t)height ? cur_visible - (size_t)height + 1 : 0;

			buf_printf(&b, " %s", m.active == 3 ? B_ : "");
			column(&b, "Text", 10);
			buf_printf(&b, "%s %s┌", R_, D_);
			repeat(&b, "─", w);
			buf_printf(&b, "┐%s", R_);
			strv_add(&s.lines, b.s);
			buf_clear(&b);
			for (int i = 0; i < height; i++) {
				buf_printf(&b, "%*s%s│%s ", 12, "", D_, R_);
				column(&b, first + (size_t)i < vis.n ? vis.v[first + (size_t)i] : "", w - 2);
				buf_printf(&b, " %s│%s", D_, R_);
				strv_add(&s.lines, b.s);
				buf_clear(&b);
			}
			buf_printf(&b, "%*s%s└", 12, "", D_);
			repeat(&b, "─", w);
			buf_printf(&b, "┘%s", R_);
			strv_add(&s.lines, b.s);
			buf_clear(&b);
			{
				buf_t t = {0};

				form_text(&m, &t);
				buf_printf(&b, "%*s%s", 12, "", t.n > RSPEAK_MAX_BYTES ? RO : GR);
				buf_printf(&b, "%zu of %d bytes", t.n, RSPEAK_MAX_BYTES);
				buf_adds(&b, R_);
				strv_add(&s.lines, b.s);
				buf_clear(&b);
				buf_free(&t);
			}
			if (m.active == 3) {
				s.cur_row = 5 + (int)(cur_visible - first);
				s.cur_col = 14 + (int)cur_col;
			}
		}
		s.keys = xasprintf("%sTab%s %s   %sCtrl+E%s %s   %sCtrl+S%s %s   %sEsc%s %s", G_, R_, "next field", G_, R_,
				    "open in the editor", G_, R_, "send", G_, R_, "cancel");
		draw(&s);
		strv_free(&vis);
		buf_free(&b);
		k = key_read(500, car);
		if (stop_requested || k == K_EOF) {
			screen_free(&s);
			break;
		}
		if (k == K_ESC) {
			bool empty = !m.field[0].n && !m.field[1].n && !m.field[2].n && m.txt.n == 1 && !*m.txt.v[0];
			strv_t t = {0};

			strv_add(&t, "The message you are writing will be lost.");
			if (empty || confirm(&s, "Discard the message?", &t)) {
				strv_free(&t);
				screen_free(&s);
				break;
			}
			strv_free(&t);
		} else if (k == K_TAB || k == K_BACKTAB) {
			if (m.active == 0)
				previews(&m);
			m.active = (m.active + (k == K_TAB ? 1 : 3)) % 4;
			if (m.active < 3)
				m.pos = m.field[m.active].n;
		} else if (k == K_CTRL_E) {
			editor(&m);
			m.active = 3;
		} else if (k == K_CTRL_S) {
			previews(&m);
			if (send_message(&s, &m, new_item)) {
				sent = true;
				screen_free(&s);
				break;
			}
		} else if (m.active < 3) {
			buf_t *c = &m.field[m.active];

			if (k == K_TEXT && c->n < 1000) {
				buf_t n = {0};

				buf_add(&n, c->s ? c->s : "", m.pos);
				buf_adds(&n, car);
				buf_adds(&n, c->s ? c->s + m.pos : "");
				m.pos += strlen(car);
				buf_free(c);
				*c = n;
			} else if (k == K_BACKSPACE && m.pos) {
				size_t p = char_before(c->s, m.pos);

				memmove(c->s + p, c->s + m.pos, c->n - m.pos + 1);
				c->n -= m.pos - p;
				m.pos = p;
			} else if (k == K_DEL && m.pos < c->n) {
				size_t p = char_after(c->s, m.pos);

				memmove(c->s + m.pos, c->s + p, c->n - p + 1);
				c->n -= p - m.pos;
			} else if (k == K_LEFT) {
				m.pos = c->s ? char_before(c->s, m.pos) : 0;
			} else if (k == K_RIGHT) {
				m.pos = c->s ? char_after(c->s, m.pos) : 0;
			} else if (k == K_HOME) {
				m.pos = 0;
			} else if (k == K_END) {
				m.pos = c->n;
			} else if (k == K_ENTER || k == K_DOWN) {
				if (m.active == 0)
					previews(&m);
				m.active++;
				m.pos = m.active < 3 ? m.field[m.active].n : 0;
			} else if (k == K_UP && m.active > 0) {
				m.active--;
				m.pos = m.field[m.active].n;
			}
		} else {
			char *r = m.txt.v[m.line];
			size_t len = strlen(r);

			if (k == K_TEXT) {
				char *n = xasprintf("%.*s%s%s", (int)m.col, r, car, r + m.col);

				free(r);
				m.txt.v[m.line] = n;
				m.col += strlen(car);
			} else if (k == K_ENTER) {
				char *after = xstrdup(r + m.col);

				r[m.col] = '\0';
				strv_add(&m.txt, "");
				memmove(&m.txt.v[m.line + 2], &m.txt.v[m.line + 1],
					(m.txt.n - m.line - 2) * sizeof *m.txt.v);
				m.txt.v[m.line + 1] = after;
				m.line++;
				m.col = 0;
			} else if (k == K_BACKSPACE) {
				if (m.col) {
					size_t p = char_before(r, m.col);

					memmove(r + p, r + m.col, len - m.col + 1);
					m.col = p;
				} else if (m.line) {
					char *prec = m.txt.v[m.line - 1], *unit = xasprintf("%s%s", prec, r);

					m.col = strlen(prec);
					free(prec);
					free(r);
					m.txt.v[m.line - 1] = unit;
					memmove(&m.txt.v[m.line], &m.txt.v[m.line + 1], (m.txt.n - m.line - 1) * sizeof *m.txt.v);
					m.txt.n--;
					m.line--;
				}
			} else if (k == K_DEL) {
				if (m.col < len) {
					size_t p = char_after(r, m.col);

					memmove(r + m.col, r + p, len - p + 1);
				} else if (m.line + 1 < m.txt.n) {
					char *unit = xasprintf("%s%s", r, m.txt.v[m.line + 1]);

					free(r);
					free(m.txt.v[m.line + 1]);
					m.txt.v[m.line] = unit;
					memmove(&m.txt.v[m.line + 1], &m.txt.v[m.line + 2], (m.txt.n - m.line - 2) * sizeof *m.txt.v);
					m.txt.n--;
				}
			} else if (k == K_LEFT) {
				if (m.col)
					m.col = char_before(r, m.col);
				else if (m.line) {
					m.line--;
					m.col = strlen(m.txt.v[m.line]);
				}
			} else if (k == K_RIGHT) {
				if (m.col < len)
					m.col = char_after(r, m.col);
				else if (m.line + 1 < m.txt.n) {
					m.line++;
					m.col = 0;
				}
			} else if (k == K_UP) {
				if (m.line) {
					m.line--;
					if (m.col > strlen(m.txt.v[m.line]))
						m.col = strlen(m.txt.v[m.line]);
					while (m.col && ((unsigned char)m.txt.v[m.line][m.col] & 0xc0) == 0x80)
						m.col--;
				} else {
					m.active = 2;
					m.pos = m.field[2].n;
				}
			} else if (k == K_DOWN && m.line + 1 < m.txt.n) {
				m.line++;
				if (m.col > strlen(m.txt.v[m.line]))
					m.col = strlen(m.txt.v[m.line]);
				while (m.col && ((unsigned char)m.txt.v[m.line][m.col] & 0xc0) == 0x80)
					m.col--;
			} else if (k == K_HOME) {
				m.col = 0;
			} else if (k == K_END) {
				m.col = len;
			}
		}
		screen_free(&s);
	}
	form_free(&m);
	return sent;
}

/* ---- key guide ---- */

static void help_overlay(screen_t *s)
{
	strv_t t = {0};
	static const char *const items[][2] = {
		{"↑ ↓ PgUp PgDn", "move through the list"},
		{"Enter", "open the message: recipients and history"},
		{"n", "write and send a new message"},
		{"r", "revoke the selected message"},
		{"m", "remind whoever has not confirmed"},
		{"p", "delete old messages"},
		{"/", "search the messages by text or title"},
		{"q", "quit"},
	};

	for (size_t i = 0; i < sizeof items / sizeof items[0]; i++) {
		buf_t b = {0};

		buf_printf(&b, "%s", G_);
		column(&b, items[i][0], 16);
		buf_printf(&b, "%s%s", R_, items[i][1]);
		strv_add(&t, b.s);
		buf_free(&b);
	}
	strv_add(&t, "");
	strv_add(&t, "The list updates by itself every 3 seconds.");
	strv_add(&t, "The complete guide: rspeak --help.");
	{
		char car[8];

		overlay(s, "Keys", &t, "any key to continue", xstrdup("any key to continue"));
		while (key_read(500, car) == K_TIMEOUT && !stop_requested)
			;
	}
	strv_free(&t);
}

/* ---- main loop ---- */

bool rspeak_tui(void)
{
	list_t e = {0};
	size_t sel = 0, first = 0;
	char car[8], *filter = xstrdup("");
	int rounds = 0;
	struct sigaction sa = {0};

	tty = open("/dev/tty", O_RDWR | O_CLOEXEC | O_NOCTTY);
	if (tty < 0)
		return false;
	if (!size(&TH, &TW) || TW < 80 || TH < 20 || tcgetattr(tty, &saved) < 0) {
		close(tty);
		tty = -1;
		return false;
	}
	colours(!getenv("NO_COLOR"));
	sa.sa_handler = on_signal;
	sigaction(SIGINT, &sa, NULL);
	sigaction(SIGTERM, &sa, NULL);
	sigaction(SIGHUP, &sa, NULL);
	signal(SIGPIPE, SIG_IGN);
	tui_mode();
	load_list(&e, filter);
	for (bool reload = false; !stop_requested; reload = false) {
		screen_t s = {0};
		int area = TH - 4 - 3, k;

		if (sel >= e.n && e.n)
			sel = e.n - 1;
		if (sel < first)
			first = sel;
		if (area > 0 && sel >= first + (size_t)area)
			first = sel - (size_t)area + 1;
		s.title_text = xstrdup("RootSpeak · sent messages");
		s.right = xasprintf("updated at %s", e.time_now);
		list_lines(&s, &e, sel, first, filter);
		list_keys(&s);
		draw(&s);
		k = key_read(500, car);
		if (k == K_TIMEOUT) {
			int r, c;

			if (size(&r, &c) && (r != TH || c != TW)) {
				TH = r;
				TW = c;
				if (TW < 80 || TH < 20) {
					screen_free(&s);
					break;
				}
			}
			if (++rounds >= 6) {
				rounds = 0;
				reload = true;
			}
		} else if (k == K_EOF || (k == K_TEXT && (car[0] == 'q' || car[0] == 'Q'))) {
			screen_free(&s);
			break;
		} else if (k == K_ESC && *filter) {
			free(filter);
			filter = xstrdup("");
			reload = true;
		} else if (k == K_UP && sel) {
			sel--;
		} else if (k == K_DOWN && sel + 1 < e.n) {
			sel++;
		} else if (k == K_PGUP) {
			sel = sel > (size_t)area ? sel - (size_t)area : 0;
		} else if (k == K_PGDN) {
			sel = sel + (size_t)area < e.n ? sel + (size_t)area : e.n ? e.n - 1 : 0;
		} else if (k == K_HOME) {
			sel = 0;
		} else if (k == K_END) {
			sel = e.n ? e.n - 1 : 0;
		} else if (k == K_ENTER && e.n) {
			detail(e.v[sel].id, e.time_now);
			reload = true;
		} else if (k == K_TEXT && car[0] == 'n') {
			long long new_item = 0;

			if (new_message(&new_item)) {
				load_list(&e, filter);
				sel = 0;
			}
			reload = true;
		} else if (k == K_TEXT && car[0] == 'r' && e.n && !e.v[sel].revoked) {
			revoke_message(&s, &e.v[sel]);
			reload = true;
		} else if (k == K_TEXT && car[0] == 'm' && e.n && !e.v[sel].revoked && !e.v[sel].expired &&
			   e.v[sel].delivered) {
			remind(&s, &e.v[sel]);
			reload = true;
		} else if (k == K_TEXT && car[0] == 'p') {
			purge(&s);
			reload = true;
		} else if (k == K_TEXT && car[0] == '/') {
			char *f = question(&s, "Search", "Show only the messages containing:", filter);

			if (f) {
				free(filter);
				filter = f;
				sel = 0;
				reload = true;
			}
		} else if (k == K_TEXT && car[0] == '?') {
			help_overlay(&s);
		}
		screen_free(&s);
		if (reload)
			load_list(&e, filter);
	}
	list_free(&e);
	free(filter);
	normal_mode();
	close(tty);
	tty = -1;
	return true;
}
