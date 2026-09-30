/* AMS - Advanced Messaging System
 * Scelta della lingua e lettore dei cataloghi .mo di gettext. */
#include "lingua.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char ams_lingua[LINGUA_MAX] = "en";

/* ---- cataloghi .mo ----
 * Formato: numero magico 0x950412de, revisione, N, posizione della tabella
 * degli originali, posizione di quella delle traduzioni; ogni voce è
 * (lunghezza, posizione); gli originali sono in ordine, per la ricerca
 * binaria. Il contesto sta nell'originale come "contesto\004testo". I file
 * sono di root, ma si controlla comunque ogni posizione. */

struct catalogo {
	unsigned char *dati;
	size_t n;
	bool inverso; /* scritto con l'ordine dei byte opposto */
	uint32_t voci, orig, trad;
};

static uint32_t u32(const catalogo_t *c, size_t pos)
{
	const unsigned char *p = c->dati + pos;

	if (c->inverso)
		return (uint32_t)p[0] << 24 | (uint32_t)p[1] << 16 | (uint32_t)p[2] << 8 | p[3];
	return (uint32_t)p[3] << 24 | (uint32_t)p[2] << 16 | (uint32_t)p[1] << 8 | p[0];
}

/* La stringa numero i di una tabella, o NULL se esce dal file. */
static const char *voce(const catalogo_t *c, uint32_t tabella, uint32_t i, uint32_t *len)
{
	size_t pos = (size_t)tabella + (size_t)i * 8;
	uint32_t l, o;

	if (pos + 8 > c->n)
		return NULL;
	l = u32(c, pos);
	o = u32(c, pos + 4);
	if ((size_t)o + l + 1 > c->n || c->dati[(size_t)o + l] != '\0')
		return NULL;
	*len = l;
	return (const char *)c->dati + o;
}

catalogo_t *catalogo_da_memoria(const void *p, size_t n)
{
	catalogo_t *c;

	if (n < 20)
		return NULL;
	c = xmalloc(sizeof *c);
	c->dati = xmalloc(n);
	memcpy(c->dati, p, n);
	c->n = n;
	c->inverso = false;
	if (u32(c, 0) != 0x950412deu) {
		c->inverso = true;
		if (u32(c, 0) != 0x950412deu) {
			free(c->dati);
			free(c);
			return NULL;
		}
	}
	c->voci = u32(c, 8);
	c->orig = u32(c, 12);
	c->trad = u32(c, 16);
	if ((size_t)c->voci > n / 8 || (size_t)c->orig + (size_t)c->voci * 8 > n ||
	    (size_t)c->trad + (size_t)c->voci * 8 > n) {
		free(c->dati);
		free(c);
		return NULL;
	}
	return c;
}

const char *catalogo_cerca(const catalogo_t *c, const char *chiave)
{
	uint32_t lo = 0, hi, len;

	if (!c)
		return NULL;
	hi = c->voci;
	while (lo < hi) {
		uint32_t mid = lo + (hi - lo) / 2;
		const char *o = voce(c, c->orig, mid, &len);
		int r;

		if (!o)
			return NULL;
		r = strcmp(chiave, o);
		if (r == 0) {
			const char *t = voce(c, c->trad, mid, &len);

			/* una traduzione vuota vuol dire «non tradotto» */
			return t && *t ? t : NULL;
		}
		if (r < 0)
			hi = mid;
		else
			lo = mid + 1;
	}
	return NULL;
}

void catalogo_libera(catalogo_t *c)
{
	if (!c)
		return;
	free(c->dati);
	free(c);
}

/* Cataloghi già letti, per lingua (NULL se la lingua non ne ha uno). */
static struct {
	char lingua[LINGUA_MAX];
	catalogo_t *cat;
} cache[8];
static size_t ncache;

static bool codice_valido(const char *s)
{
	size_t n = strlen(s);

	if (n < 2 || n > 3)
		return false;
	for (; *s; s++)
		if (*s < 'a' || *s > 'z')
			return false;
	return true;
}

static char *percorso_mo(const char *lingua)
{
	return xasprintf("%s/%s/LC_MESSAGES/ams.mo", ams_localedir, lingua);
}

static catalogo_t *catalogo(const char *lingua)
{
	buf_t b = {0};
	catalogo_t *c = NULL;
	char *path;

	if (!codice_valido(lingua) || !strcmp(lingua, "en"))
		return NULL;
	for (size_t i = 0; i < ncache; i++)
		if (!strcmp(cache[i].lingua, lingua))
			return cache[i].cat;
	path = percorso_mo(lingua);
	if (leggi_file(path, 4 << 20, false, &b) == 0)
		c = catalogo_da_memoria(b.s, b.n);
	buf_free(&b);
	free(path);
	if (ncache < sizeof cache / sizeof cache[0]) {
		snprintf(cache[ncache].lingua, LINGUA_MAX, "%s", lingua);
		cache[ncache++].cat = c;
	}
	return c;
}

bool lingua_nota(const char *codice)
{
	char *path;
	bool ok;

	if (!codice_valido(codice))
		return false;
	if (!strcmp(codice, "en"))
		return true;
	path = percorso_mo(codice);
	ok = esiste(path);
	free(path);
	return ok;
}

/* ---- traduzioni ---- */

const char *tl(const char *lingua, const char *msgid)
{
	const char *t = catalogo_cerca(catalogo(lingua), msgid);

	return t ? t : msgid;
}

const char *tlc(const char *lingua, const char *ctx, const char *msgid)
{
	char *chiave = xasprintf("%s\004%s", ctx, msgid);
	const char *t = catalogo_cerca(catalogo(lingua), chiave);

	free(chiave);
	return t ? t : msgid;
}

const char *T(const char *msgid)
{
	return tl(ams_lingua, msgid);
}

const char *TC(const char *ctx, const char *msgid)
{
	return tlc(ams_lingua, ctx, msgid);
}

/* ---- scelta della lingua ---- */

/* La lingua di un valore di locale: «it_IT.UTF-8» → «it». */
static bool lingua_di(const char *valore, size_t n, char out[LINGUA_MAX])
{
	size_t k = 0;

	while (k < n && valore[k] != '_' && valore[k] != '.' && valore[k] != '@' && valore[k] != ':')
		k++;
	if (k < 2 || k > 3)
		return false;
	memcpy(out, valore, k);
	out[k] = '\0';
	return codice_valido(out) && lingua_nota(out);
}

void lingua_scegli(const char *language, const char *lc_all, const char *lc_messages, const char *lang,
		   char out[LINGUA_MAX])
{
	const char *loc = lc_all && *lc_all ? lc_all : lc_messages && *lc_messages ? lc_messages : lang ? lang : "";
	size_t base = strcspn(loc, ".@");

	snprintf(out, LINGUA_MAX, "en");
	if (base == 0 || (base == 1 && loc[0] == 'C') || (base == 5 && !strncmp(loc, "POSIX", 5)))
		return;
	for (const char *p = language ? language : ""; *p;) {
		size_t n = strcspn(p, ":");

		if (n && lingua_di(p, n, out))
			return;
		p += n;
		if (*p == ':')
			p++;
	}
	if (!lingua_di(loc, strlen(loc), out))
		snprintf(out, LINGUA_MAX, "en");
}

static void campi_locale(const char *riga, size_t n, char **language, char **lc_all, char **lc_messages,
			 char **lang)
{
	static const char *nomi[] = {"LANGUAGE=", "LC_ALL=", "LC_MESSAGES=", "LANG="};
	char **dove[] = {language, lc_all, lc_messages, lang};

	for (int i = 0; i < 4; i++) {
		size_t k = strlen(nomi[i]);

		if (n >= k && !strncmp(riga, nomi[i], k)) {
			char *v = xmalloc(n - k + 1);
			size_t j = 0;

			/* /etc/locale.conf può mettere il valore tra virgolette */
			for (size_t x = k; x < n; x++)
				if (riga[x] != '"' && riga[x] != '\'')
					v[j++] = riga[x];
			v[j] = '\0';
			free(*dove[i]);
			*dove[i] = v;
		}
	}
}

bool lingua_da_environ(const char *env, size_t n, char out[LINGUA_MAX])
{
	char *language = NULL, *lc_all = NULL, *lc_messages = NULL, *lang = NULL;
	size_t i = 0, voci = 0;

	while (i < n) {
		size_t len = strnlen(env + i, n - i);

		campi_locale(env + i, len, &language, &lc_all, &lc_messages, &lang);
		voci++;
		i += len + 1;
	}
	lingua_scegli(language, lc_all, lc_messages, lang, out);
	free(language);
	free(lc_all);
	free(lc_messages);
	free(lang);
	return voci > 0;
}

const char *lingua_sistema(void)
{
	static char sistema[LINGUA_MAX];
	static const char *file[] = {"/etc/default/locale", "/etc/locale.conf"};

	if (*sistema)
		return sistema;
	snprintf(sistema, LINGUA_MAX, "en");
	for (int f = 0; f < 2; f++) {
		char *language = NULL, *lc_all = NULL, *lc_messages = NULL, *lang = NULL;
		buf_t b = {0};

		if (leggi_file(file[f], 65536, false, &b) < 0) {
			buf_free(&b);
			continue;
		}
		for (char *p = b.s; p && *p;) {
			size_t len = strcspn(p, "\n");

			campi_locale(p, len, &language, &lc_all, &lc_messages, &lang);
			p += len;
			if (*p)
				p++;
		}
		lingua_scegli(language, lc_all, lc_messages, lang, sistema);
		free(language);
		free(lc_all);
		free(lc_messages);
		free(lang);
		buf_free(&b);
		break;
	}
	return sistema;
}

void lingua_init(void)
{
	lingua_scegli(getenv("LANGUAGE"), getenv("LC_ALL"), getenv("LC_MESSAGES"), getenv("LANG"), ams_lingua);
}
