/* RootSpeak - Advanced Messaging System for Linux
 * Ognuno legge RootSpeak nella sua lingua. I testi di partenza sono in inglese; le
 * traduzioni stanno nei file .mo di gettext (po/XX.po), che RootSpeak legge da sé:
 * così una lingua funziona anche se non è installata nel sistema, e root può
 * scrivere a ogni terminale nella lingua del suo utente. */
#ifndef RSPEAK_LINGUA_H
#define RSPEAK_LINGUA_H

#include "comune.h"

#define LINGUA_MAX 8

/* Lingua di chi usa questo processo (dall'ambiente), scelta da lingua_init. */
extern char rspeak_lingua[LINGUA_MAX];

void lingua_init(void);

/* Regole di gettext: conta il primo impostato fra LC_ALL, LC_MESSAGES e
 * LANG; se è C o POSIX vale l'inglese, altrimenti si prova prima l'elenco di
 * LANGUAGE. Vince la prima lingua che RootSpeak conosce, altrimenti l'inglese. Si
 * accettano solo codici di 2 o 3 lettere minuscole. */
void lingua_scegli(const char *language, const char *lc_all, const char *lc_messages, const char *lang,
		   char out[LINGUA_MAX]);
/* Dall'ambiente di un processo (formato /proc/PID/environ); false se vuoto. */
bool lingua_da_environ(const char *env, size_t n, char out[LINGUA_MAX]);
/* Lingua del sistema (/etc/default/locale o /etc/locale.conf): quella del registro. */
const char *lingua_sistema(void);
/* Vero se RootSpeak ha la lingua: l'inglese, o un .mo in rspeak_localedir. */
bool lingua_nota(const char *codice);

/* Traduzioni. tl: nella lingua data; T: in rspeak_lingua. Con contesto: tlc, TC. */
const char *tl(const char *lingua, const char *msgid) __attribute__((format_arg(2)));
const char *tlc(const char *lingua, const char *ctx, const char *msgid) __attribute__((format_arg(3)));
const char *T(const char *msgid) __attribute__((format_arg(1)));
const char *TC(const char *ctx, const char *msgid) __attribute__((format_arg(2)));
#define N_(s) (s)

/* Legge un catalogo .mo da memoria: per le prove. */
typedef struct catalogo catalogo_t;
catalogo_t *catalogo_da_memoria(const void *p, size_t n);
const char *catalogo_cerca(const catalogo_t *c, const char *chiave);
void catalogo_libera(catalogo_t *c);

#endif
