/* RootSpeak - Advanced Messaging System for Linux
 * Pulizia del testo, formato dei messaggi, configurazione. */
#include "testo.h"

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* ---- pulizia ----
 * Tre passaggi, come nel prototipo (sed, tr, sed), riga per riga dove sed
 * lavora per righe:
 *   1. sequenze CSI «ESC [ cifre ; ? … finale» e OSC «ESC ] … BEL» (nella riga);
 *   2. caratteri C0 tranne tab e a capo, e DEL;
 *   3. caratteri C1 in UTF-8 (C2 80 … C2 9F). */

static void togli_sequenze_riga(const unsigned char *s, size_t n, buf_t *out)
{
	buf_t a = {0};
	size_t i;

	for (i = 0; i < n;) {
		if (s[i] == 0x1b && i + 1 < n && s[i + 1] == '[') {
			size_t j = i + 2;

			while (j < n && ((s[j] >= '0' && s[j] <= '9') || s[j] == ';' || s[j] == '?'))
				j++;
			if (j < n && s[j] >= 0x40 && s[j] <= 0x7e) {
				i = j + 1;
				continue;
			}
		}
		buf_addc(&a, (char)s[i++]);
	}
	for (i = 0; i < a.n;) {
		const unsigned char *t = (const unsigned char *)a.s;

		if (t[i] == 0x1b && i + 1 < a.n && t[i + 1] == ']') {
			size_t j = i + 2;

			while (j < a.n && t[j] != 0x07)
				j++;
			if (j < a.n) {
				i = j + 1;
				continue;
			}
		}
		buf_addc(out, (char)t[i++]);
	}
	buf_free(&a);
}

void pulisci(const char *in, size_t n, buf_t *out)
{
	const unsigned char *s = (const unsigned char *)in;
	buf_t a = {0}, b = {0};
	size_t i, inizio = 0;

	for (i = 0; i <= n; i++) {
		if (i == n || s[i] == '\n') {
			togli_sequenze_riga(s + inizio, i - inizio, &a);
			if (i < n)
				buf_addc(&a, '\n');
			inizio = i + 1;
		}
	}
	for (i = 0; i < a.n; i++) {
		unsigned char c = (unsigned char)a.s[i];

		if ((c <= 0x08) || (c >= 0x0b && c <= 0x1f) || c == 0x7f)
			continue;
		buf_addc(&b, (char)c);
	}
	for (i = 0; i < b.n;) {
		unsigned char c = (unsigned char)b.s[i];

		if (c == 0xc2 && i + 1 < b.n && (unsigned char)b.s[i + 1] >= 0x80 && (unsigned char)b.s[i + 1] <= 0x9f) {
			i += 2;
			continue;
		}
		buf_addc(out, (char)c);
		i++;
	}
	buf_free(&a);
	buf_free(&b);
}

/* ---- messaggi ---- */

void msg_libera(msg_t *m)
{
	free(m->from);
	free(m->title);
	free(m->body);
	memset(m, 0, sizeof *m);
}

int msg_da_testo(const char *s, size_t n, msg_t *m)
{
	const char *p = s, *fine = s + n;
	bool data = false;

	memset(m, 0, sizeof *m);
	while (p < fine) {
		const char *eol = memchr(p, '\n', (size_t)(fine - p));
		size_t len = eol ? (size_t)(eol - p) : (size_t)(fine - p);
		char *riga, *sep;

		if (len == 0) {
			p = eol ? eol + 1 : fine;
			break;
		}
		riga = xmalloc(len + 1);
		memcpy(riga, p, len);
		riga[len] = '\0';
		sep = strstr(riga, ": ");
		if (!sep && len > 0 && riga[len - 1] == ':')
			sep = riga + len - 1;
		if (sep) {
			const char *v = sep[1] ? sep + 2 : "";

			*sep = '\0';
			if (!strcmp(riga, "id"))
				leggi_numero(v, &m->id);
			else if (!strcmp(riga, "from")) {
				free(m->from);
				m->from = xstrdup(v);
			} else if (!strcmp(riga, "date"))
				data = leggi_numero(v, &m->date);
			else if (!strcmp(riga, "title")) {
				free(m->title);
				m->title = xstrdup(v);
			} else if (!strcmp(riga, "expires")) {
				if (!leggi_numero(v, &m->expires))
					m->expires = 0;
			}
			/* chiavi sconosciute (format e le future): ignorate */
		}
		free(riga);
		p = eol ? eol + 1 : fine;
	}
	m->body = xmalloc((size_t)(fine - p) + 1);
	memcpy(m->body, p, (size_t)(fine - p));
	m->body[fine - p] = '\0';
	if (!m->from)
		m->from = xstrdup("");
	if (!m->title)
		m->title = xstrdup("");
	if (!data) {
		msg_libera(m);
		errno = EINVAL;
		return -1;
	}
	return 0;
}

int msg_leggi(const char *path, msg_t *m)
{
	buf_t b = {0};
	int r;

	if (leggi_file(path, RSPEAK_MAX_MSG, true, &b) < 0) {
		buf_free(&b);
		memset(m, 0, sizeof *m);
		return -1;
	}
	r = msg_da_testo(b.s ? b.s : "", b.n, m);
	buf_free(&b);
	return r;
}

void msg_formatta(const msg_t *m, buf_t *out)
{
	buf_printf(out, "format: 1\nid: %lld\nfrom: %s\ndate: %lld\ntitle: %s\nexpires: ", m->id, m->from, m->date,
		   m->title);
	if (m->expires)
		buf_printf(out, "%lld", m->expires);
	buf_printf(out, "\n\n%s", m->body);
}

bool msg_scaduto(const msg_t *m, time_t ora)
{
	return m->expires && m->expires <= (long long)ora;
}

void msg_intestazione(const msg_t *m, buf_t *out)
{
	char d[32];

	data_breve((time_t)m->date, d);
	if (*m->title)
		buf_printf(out, "%s · %s", m->title, d);
	else
		buf_adds(out, d);
}

/* ---- configurazione ---- */

void conf_da_testo(const char *s, conf_t *c)
{
	c->remind_minutes = 30;
	c->agent_poll = 60;
	while (s && *s) {
		const char *eol = strchr(s, '\n');
		size_t len = eol ? (size_t)(eol - s) : strlen(s);
		char riga[256], *k, *v, *w;
		size_t j = 0;

		/* la riga senza commento e senza spazi; le righe lunghe non sono valide */
		for (size_t i = 0; i < len && s[i] != '#'; i++)
			if (s[i] != ' ' && s[i] != '\t' && s[i] != '\r' && s[i] != '\v' && s[i] != '\f') {
				if (j + 1 >= sizeof riga) {
					j = 0;
					break;
				}
				riga[j++] = s[i];
			}
		riga[j] = '\0';
		s = eol ? eol + 1 : s + len;
		if (!j || !(w = strchr(riga, '=')))
			continue;
		*w = '\0';
		k = riga;
		v = w + 1;
		if (!solo_cifre(v) || strlen(v) > 6 || atol(v) <= 0)
			continue;
		if (!strcmp(k, "RSPEAK_REMIND_MINUTES"))
			c->remind_minutes = atol(v);
		else if (!strcmp(k, "RSPEAK_AGENT_POLL"))
			c->agent_poll = atol(v);
	}
}

void conf_leggi(conf_t *c)
{
	buf_t b = {0};

	if (leggi_file(rspeak_conf_path, 65536, false, &b) < 0) {
		conf_da_testo(NULL, c);
	} else {
		conf_da_testo(b.s ? b.s : "", c);
	}
	buf_free(&b);
}
