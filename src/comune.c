/* RootSpeak - Advanced Messaging System for Linux
 * Utilità comuni: ambiente, errori, memoria, testi che crescono, file. */
#include "comune.h"

#include <ctype.h>
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#ifndef LIBDIR
#define LIBDIR "/usr/local/lib/rootspeak"
#endif
#ifndef LOCALEDIR
#define LOCALEDIR "/usr/local/share/locale"
#endif

const char *rspeak_var = "/var/lib/rootspeak";
const char *rspeak_libdir = LIBDIR;
const char *rspeak_localedir = LOCALEDIR;
const char *rspeak_conf_path = "/etc/rootspeak/rootspeak.conf";
bool rspeak_test = false;
const char *rspeak_nome = "rspeak";

void rspeak_init(const char *nome)
{
	const char *v;

	rspeak_nome = nome;
	/* Le variabili di prova valgono solo in modalità di prova: un programma
	 * di root non prende cartelle dall'ambiente di chi lo lancia. */
	v = getenv("RSPEAK_TEST");
	rspeak_test = v && *v;
	if (rspeak_test) {
		if ((v = getenv("RSPEAK_VAR")) && *v)
			rspeak_var = v;
		if ((v = getenv("RSPEAK_LIB")) && *v)
			rspeak_libdir = v;
		if ((v = getenv("RSPEAK_LOCALEDIR")) && *v)
			rspeak_localedir = v;
		if ((v = getenv("RSPEAK_CONF")) && *v)
			rspeak_conf_path = v;
	}
}

/* ---- errori e memoria ---- */

void die(const char *fmt, ...)
{
	va_list ap;

	fflush(stdout);
	fprintf(stderr, "%s: ", rspeak_nome);
	va_start(ap, fmt);
	vfprintf(stderr, fmt, ap);
	va_end(ap);
	fputc('\n', stderr);
	exit(1);
}

void avviso(const char *fmt, ...)
{
	va_list ap;

	fflush(stdout);
	fprintf(stderr, "%s: ", rspeak_nome);
	va_start(ap, fmt);
	vfprintf(stderr, fmt, ap);
	va_end(ap);
	fputc('\n', stderr);
}

void *xmalloc(size_t n)
{
	void *p = malloc(n ? n : 1);

	if (!p)
		die("memoria esaurita");
	return p;
}

void *xrealloc(void *p, size_t n)
{
	p = realloc(p, n ? n : 1);
	if (!p)
		die("memoria esaurita");
	return p;
}

char *xstrdup(const char *s)
{
	size_t n = strlen(s) + 1;
	char *p = xmalloc(n);

	memcpy(p, s, n);
	return p;
}

char *xasprintf(const char *fmt, ...)
{
	va_list ap;
	char *s;
	int r;

	va_start(ap, fmt);
	r = vasprintf(&s, fmt, ap);
	va_end(ap);
	if (r < 0)
		die("memoria esaurita");
	return s;
}

/* ---- testi che crescono ---- */

static void buf_spazio(buf_t *b, size_t extra)
{
	size_t serve;

	if (extra > SIZE_MAX - b->n - 1)
		die("memoria esaurita");
	serve = b->n + extra + 1;
	if (serve <= b->cap)
		return;
	if (b->cap < 64)
		b->cap = 64;
	while (b->cap < serve)
		b->cap = b->cap > SIZE_MAX / 2 ? serve : b->cap * 2;
	b->s = xrealloc(b->s, b->cap);
}

void buf_add(buf_t *b, const void *p, size_t n)
{
	buf_spazio(b, n);
	if (n)
		memcpy(b->s + b->n, p, n);
	b->n += n;
	b->s[b->n] = '\0';
}

void buf_adds(buf_t *b, const char *s)
{
	buf_add(b, s, strlen(s));
}

void buf_addc(buf_t *b, char c)
{
	buf_add(b, &c, 1);
}

void buf_vprintf(buf_t *b, const char *fmt, va_list ap)
{
	va_list ap2;
	int n;

	va_copy(ap2, ap);
	n = vsnprintf(NULL, 0, fmt, ap2);
	va_end(ap2);
	if (n < 0)
		die("formato non valido");
	buf_spazio(b, (size_t)n);
	vsnprintf(b->s + b->n, (size_t)n + 1, fmt, ap);
	b->n += (size_t)n;
}

void buf_printf(buf_t *b, const char *fmt, ...)
{
	va_list ap;

	va_start(ap, fmt);
	buf_vprintf(b, fmt, ap);
	va_end(ap);
}

void buf_clear(buf_t *b)
{
	b->n = 0;
	if (b->s)
		b->s[0] = '\0';
}

void buf_free(buf_t *b)
{
	free(b->s);
	b->s = NULL;
	b->n = b->cap = 0;
}

/* ---- elenchi ---- */

void strv_add_own(strv_t *l, char *s)
{
	if (l->n == l->cap) {
		l->cap = l->cap ? l->cap * 2 : 16;
		l->v = xrealloc(l->v, l->cap * sizeof *l->v);
	}
	l->v[l->n++] = s;
}

void strv_add(strv_t *l, const char *s)
{
	strv_add_own(l, xstrdup(s));
}

bool strv_has(const strv_t *l, const char *s)
{
	for (size_t i = 0; i < l->n; i++)
		if (!strcmp(l->v[i], s))
			return true;
	return false;
}

static int cmp_str(const void *a, const void *b)
{
	return strcmp(*(char *const *)a, *(char *const *)b);
}

void strv_sort(strv_t *l)
{
	if (l->n > 1)
		qsort(l->v, l->n, sizeof *l->v, cmp_str);
}

void strv_free(strv_t *l)
{
	for (size_t i = 0; i < l->n; i++)
		free(l->v[i]);
	free(l->v);
	l->v = NULL;
	l->n = l->cap = 0;
}

/* ---- file ---- */

int leggi_fd(int fd, size_t max, buf_t *out)
{
	char tmp[8192];

	for (;;) {
		ssize_t r = read(fd, tmp, sizeof tmp);

		if (r < 0) {
			if (errno == EINTR)
				continue;
			return -1;
		}
		if (r == 0)
			return 0;
		if (out->n < max) {
			size_t n = (size_t)r;

			if (n > max - out->n)
				n = max - out->n;
			buf_add(out, tmp, n);
		}
	}
}

int leggi_file(const char *path, size_t max, bool nofollow, buf_t *out)
{
	struct stat st;
	int fd, r, e;

	/* O_NONBLOCK: una pipe al posto del file non blocca l'apertura; il
	 * controllo successivo la rifiuta. */
	fd = open(path, O_RDONLY | O_CLOEXEC | O_NOCTTY | O_NONBLOCK | (nofollow ? O_NOFOLLOW : 0));
	if (fd < 0)
		return -1;
	if (fstat(fd, &st) < 0 || !S_ISREG(st.st_mode)) {
		close(fd);
		errno = EINVAL;
		return -1;
	}
	if ((size_t)st.st_size > max) {
		close(fd);
		errno = EFBIG;
		return -1;
	}
	r = leggi_fd(fd, max, out);
	e = errno;
	close(fd);
	errno = e;
	return r;
}

int scrivi_tutto(int fd, const void *p, size_t n)
{
	const char *c = p;

	while (n) {
		ssize_t w = write(fd, c, n);

		if (w < 0) {
			if (errno == EINTR)
				continue;
			return -1;
		}
		c += w;
		n -= (size_t)w;
	}
	return 0;
}

int sync_path(const char *path)
{
	int fd = open(path, O_RDONLY | O_CLOEXEC | O_NOCTTY | O_NONBLOCK);
	int r;

	if (fd < 0)
		return -1;
	r = fsync(fd);
	close(fd);
	return r;
}

int syncfs_path(const char *path)
{
	int fd = open(path, O_RDONLY | O_CLOEXEC | O_NOCTTY | O_NONBLOCK);
	int r;

	if (fd < 0)
		return -1;
	r = syncfs(fd);
	close(fd);
	return r;
}

int scrivi_atomico(const char *path, const void *p, size_t n, mode_t mode)
{
	char *tmp = xasprintf("%s.tmp", path);
	int fd, e;

	unlink(tmp);
	fd = open(tmp, O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC | O_NOFOLLOW, mode);
	if (fd < 0)
		goto errore;
	if (scrivi_tutto(fd, p, n) < 0 || fsync(fd) < 0) {
		e = errno;
		close(fd);
		errno = e;
		goto errore;
	}
	if (close(fd) < 0 || rename(tmp, path) < 0)
		goto errore;
	free(tmp);
	return 0;
errore:
	e = errno;
	unlink(tmp);
	free(tmp);
	errno = e;
	return -1;
}

bool esiste(const char *path)
{
	struct stat st;

	return lstat(path, &st) == 0;
}

bool e_cartella(const char *path)
{
	struct stat st;

	return lstat(path, &st) == 0 && S_ISDIR(st.st_mode);
}

bool solo_cifre(const char *s)
{
	if (!*s)
		return false;
	for (; *s; s++)
		if (*s < '0' || *s > '9')
			return false;
	return true;
}

bool leggi_numero(const char *s, long long *out)
{
	long long v = 0;

	if (!solo_cifre(s) || strlen(s) > 18)
		return false;
	for (; *s; s++)
		v = v * 10 + (*s - '0');
	*out = v;
	return true;
}

static int cmp_num(const void *a, const void *b)
{
	const char *x = *(char *const *)a, *y = *(char *const *)b;
	size_t lx = strlen(x), ly = strlen(y);

	/* sole cifre: più corto = più piccolo (gli zeri iniziali non ci sono nei numeri di RootSpeak) */
	if (lx != ly)
		return lx < ly ? -1 : 1;
	return strcmp(x, y);
}

int elenca_numeri(const char *dir, strv_t *out)
{
	DIR *d = opendir(dir);
	struct dirent *e;

	if (!d)
		return -1;
	while ((e = readdir(d)))
		if (solo_cifre(e->d_name) && strlen(e->d_name) <= 18)
			strv_add(out, e->d_name);
	closedir(d);
	if (out->n > 1)
		qsort(out->v, out->n, sizeof *out->v, cmp_num);
	return 0;
}

/* ---- tempo ---- */

time_t adesso(void)
{
	return time(NULL);
}

void data_breve(time_t t, char out[32])
{
	struct tm tm;

	if (!localtime_r(&t, &tm) || !strftime(out, 32, "%d/%m %H:%M", &tm))
		snprintf(out, 32, "?");
}
