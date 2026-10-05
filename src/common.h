/* RootSpeak - Advanced Messaging System for Linux
 * Parts shared by rspeak (administrator, root) and rootspeak-user (user). */
#ifndef RSPEAK_COMMON_H
#define RSPEAK_COMMON_H

#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif
#include <stdarg.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <sys/types.h>
#include <time.h>

#define RSPEAK_VERSION "0.2.0"

/* Maximum length of a message's text, in bytes: the desktop dialog
 * receives it as a zenity argument, and Linux does not accept an
 * argument over 128 KiB. */
#define RSPEAK_MAX_BYTES 65536
/* A saved message (header plus text) never exceeds this
 * size: whoever reads a larger file rejects it. */
#define RSPEAK_MAX_MSG (RSPEAK_MAX_BYTES + 8192)

#define ATTR_PRINTF(a, b) __attribute__((format(printf, a, b)))
#define ATTR_NORETURN __attribute__((noreturn))

/* ---- environment ---- */

/* Where the manuals are installed: DOCDIR from the Makefile. */
#ifndef DOCDIR
#define DOCDIR "/usr/local/share/doc/rootspeak"
#endif

/* Set by rspeak_init: directories and test mode. */
extern const char *rspeak_var;       /* message store: RSPEAK_VAR or /var/lib/rootspeak */
extern const char *rspeak_libdir;    /* where rootspeak-user lives: RSPEAK_LIB or LIBDIR */
extern const char *rspeak_conf_path; /* configuration: RSPEAK_CONF or /etc/rootspeak/rootspeak.conf */
extern bool rspeak_test;             /* RSPEAK_TEST=1: test without root */
extern const char *rspeak_name;      /* error prefix: «rspeak» or «rootspeak-user» */

void rspeak_init(const char *name);

/* ---- errors and memory ---- */

void die(const char *fmt, ...) ATTR_PRINTF(1, 2) ATTR_NORETURN;
void notice(const char *fmt, ...) ATTR_PRINTF(1, 2);
void *xmalloc(size_t n);
void *xrealloc(void *p, size_t n);
char *xstrdup(const char *s);
char *xasprintf(const char *fmt, ...) ATTR_PRINTF(1, 2);

/* Growing text: s is always terminated by '\0'. */
typedef struct {
	char *s;
	size_t n, cap;
} buf_t;

void buf_add(buf_t *b, const void *p, size_t n);
void buf_adds(buf_t *b, const char *s);
void buf_addc(buf_t *b, char c);
void buf_printf(buf_t *b, const char *fmt, ...) ATTR_PRINTF(2, 3);
void buf_vprintf(buf_t *b, const char *fmt, va_list ap);
void buf_clear(buf_t *b);
void buf_free(buf_t *b);

/* List of strings. */
typedef struct {
	char **v;
	size_t n, cap;
} strv_t;

void strv_add(strv_t *l, const char *s);
void strv_add_own(strv_t *l, char *s);
bool strv_has(const strv_t *l, const char *s);
void strv_sort(strv_t *l);
void strv_free(strv_t *l);

/* ---- file ---- */

/* Reads a regular file (does not follow links if nofollow): at most max
 * bytes; returns -1 with errno if it is not a regular file, cannot be opened or is
 * larger than max. */
int read_file(const char *path, size_t max, bool nofollow, buf_t *out);
/* Reads from a descriptor to the end, at most max bytes (the rest is discarded). */
int read_fd(int fd, size_t max, buf_t *out);
/* Writes everything, retrying after partial writes. */
int write_all(int fd, const void *p, size_t n);
/* Writes path.tmp, flushes it to disk and renames it to path. */
int write_atomic(const char *path, const void *p, size_t n, mode_t mode);
/* fsync of a file or directory; syncfs of the file system of path. */
int sync_path(const char *path);
int syncfs_path(const char *path);
bool exists(const char *path);
bool is_folder(const char *path);
/* Names in the directory made only of digits, in numeric order. */
int list_numbers(const char *dir, strv_t *out);
bool only_digits(const char *s);
/* Non-negative integer from a string of digits only (at most 18). */
bool read_number(const char *s, long long *out);

/* ---- time ---- */

time_t now(void);
/* «29/09 22:15» */
void short_date(time_t t, char out[32]);

#endif
