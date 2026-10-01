/* RootSpeak - Advanced Messaging System for Linux
 * Parti comuni ad rspeak (amministratore, root) e rootspeak-user (utente). */
#ifndef RSPEAK_COMUNE_H
#define RSPEAK_COMUNE_H

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

/* Lunghezza massima del testo di un messaggio, in byte: la finestra del
 * desktop lo riceve come argomento di zenity, e Linux non accetta un
 * argomento oltre 128 KiB. */
#define RSPEAK_MAX_BYTES 65536
/* Un messaggio salvato (intestazione più testo) non supera mai questa
 * misura: chi legge un file più grande lo rifiuta. */
#define RSPEAK_MAX_MSG (RSPEAK_MAX_BYTES + 8192)

#define ATTR_PRINTF(a, b) __attribute__((format(printf, a, b)))
#define ATTR_NORETURN __attribute__((noreturn))

/* ---- ambiente ---- */

/* Impostati da rspeak_init: cartelle e modalità di prova. */
extern const char *rspeak_var;       /* archivio: RSPEAK_VAR o /var/lib/rootspeak */
extern const char *rspeak_libdir;    /* dove sta rootspeak-user: RSPEAK_LIB o LIBDIR */
extern const char *rspeak_localedir; /* dove stanno i .mo: RSPEAK_LOCALEDIR o LOCALEDIR */
extern const char *rspeak_conf_path; /* configurazione: RSPEAK_CONF o /etc/rootspeak/rootspeak.conf */
extern bool rspeak_test;             /* RSPEAK_TEST=1: prova senza root */
extern const char *rspeak_nome;      /* prefisso degli errori: «rspeak» o «rootspeak-user» */

void rspeak_init(const char *nome);

/* ---- errori e memoria ---- */

void die(const char *fmt, ...) ATTR_PRINTF(1, 2) ATTR_NORETURN;
void avviso(const char *fmt, ...) ATTR_PRINTF(1, 2);
void *xmalloc(size_t n);
void *xrealloc(void *p, size_t n);
char *xstrdup(const char *s);
char *xasprintf(const char *fmt, ...) ATTR_PRINTF(1, 2);

/* Testo che cresce: s è sempre terminato da '\0'. */
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

/* Elenco di stringhe. */
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

/* Legge un file normale (non segue collegamenti se nofollow): al più max
 * byte; esito -1 con errno se non è un file normale, se non si apre o se è
 * più grande di max. */
int leggi_file(const char *path, size_t max, bool nofollow, buf_t *out);
/* Legge da un descrittore fino alla fine, al più max byte (il resto si scarta). */
int leggi_fd(int fd, size_t max, buf_t *out);
/* Scrive tutto, ripetendo dopo le scritture parziali. */
int scrivi_tutto(int fd, const void *p, size_t n);
/* Scrive path.tmp, lo porta su disco e lo rinomina in path. */
int scrivi_atomico(const char *path, const void *p, size_t n, mode_t mode);
/* fsync di un file o di una cartella; syncfs del file system di path. */
int sync_path(const char *path);
int syncfs_path(const char *path);
bool esiste(const char *path);
bool e_cartella(const char *path);
/* Nomi della cartella fatti solo di cifre, in ordine numerico. */
int elenca_numeri(const char *dir, strv_t *out);
bool solo_cifre(const char *s);
/* Numero intero non negativo da una stringa di sole cifre (al più 18). */
bool leggi_numero(const char *s, long long *out);

/* ---- tempo ---- */

time_t adesso(void);
/* «29/09 22:15» */
void data_breve(time_t t, char out[32]);

#endif
