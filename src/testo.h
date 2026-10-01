/* RootSpeak - Advanced Messaging System for Linux
 * Testo pulito, messaggi, configurazione. */
#ifndef RSPEAK_TESTO_H
#define RSPEAK_TESTO_H

#include "comune.h"

/* Toglie le sequenze di escape ANSI e i caratteri di controllo (C0 tranne
 * tab e a capo, DEL, C1 in UTF-8), così un messaggio non può iniettare
 * sequenze nei terminali. Stesso risultato del prototipo in bash. */
void pulisci(const char *in, size_t n, buf_t *out);

/* ---- messaggi ---- */

/* Formato 1: intestazione "chiave: valore", riga vuota, testo. */
typedef struct {
	long long id;
	char *from;
	long long date;
	char *title;
	long long expires; /* 0: nessuna scadenza */
	char *body;
} msg_t;

/* Legge un messaggio: esito -1 se il file manca, non è un file normale, è
 * troppo grande o non ha una data valida. */
int msg_leggi(const char *path, msg_t *m);
int msg_da_testo(const char *s, size_t n, msg_t *m);
void msg_libera(msg_t *m);
void msg_formatta(const msg_t *m, buf_t *out);
bool msg_scaduto(const msg_t *m, time_t ora);
/* «Titolo · 29/09 22:15», oppure solo la data. */
void msg_intestazione(const msg_t *m, buf_t *out);

/* ---- configurazione ---- */

/* Il file è di dati, non uno script: righe CHIAVE=valore, commenti con #,
 * spazi ignorati. Si accettano solo le chiavi note con interi positivi (al
 * più 6 cifre); il resto è ignorato. */
typedef struct {
	long remind_minutes; /* RSPEAK_REMIND_MINUTES, 30 */
	long agent_poll;     /* RSPEAK_AGENT_POLL, 60 */
} conf_t;

void conf_leggi(conf_t *c);
void conf_da_testo(const char *s, conf_t *c);

#endif
