/* AMS - Advanced Messaging System
 * Le parti di ams usate anche dalla TUI: la TUI legge l'archivio con le
 * stesse funzioni dei comandi, e le azioni sono i comandi stessi. */
#ifndef AMS_AMS_H
#define AMS_AMS_H

#include "comune.h"
#include "testo.h"

/* Gli stati di un destinatario: gli unici tre (capitolo «Specifica»). */
typedef enum { INVIATO, CONSEGNATO, CONFERMATO } stato_e;

/* Un messaggio riassunto con i suoi destinatari. */
typedef struct {
	long long id;
	msg_t m;
	int confermato, consegnato, inviato;
	bool ritirato, scaduto;
} riassunto_t;

/* I numeri dei messaggi in sent/, in ordine. */
void elenco_messaggi(strv_t *ids);
/* Riassume il messaggio id; false se non c'è (o l'invio è stato annullato). */
bool riassumi(long long id, riassunto_t *r);
void riassunto_libera(riassunto_t *r);
/* «14 confermato · 5 consegnato · 2 inviato» oppure «tutti confermato (58)». */
void riassunto_frase(const riassunto_t *r, buf_t *out);

/* I destinatari di un messaggio con la riga di stato di ams status. */
typedef struct {
	char *utente;
	stato_e stato;
	char *riga;
} destinatario_t;
typedef struct {
	destinatario_t *v;
	size_t n;
} destinatari_t;
void destinatari(long long id, const msg_t *m, destinatari_t *out);
void destinatari_libera(destinatari_t *d);
/* Data del ritiro (0 se non ritirato). */
long long data_ritiro(long long id);

/* Le caselle lette restano in memoria: la TUI le dimentica a ogni aggiornamento. */
void caselle_svuota(void);
/* Completa invii, ritiri e cancellazioni interrotti. */
void recupera(void);

/* I comandi: stampano come da riga di comando e, in caso d'errore, escono
 * con die. La TUI li esegue in un processo figlio e ne mostra l'uscita. */
void cmd_send(int argc, char **argv);
void cmd_revoke(const char *arg);
void cmd_remind(const char *arg);
void cmd_purge(const char *dur);
void cmd_log(const char *arg);
/* Risolve i destinatari e stampa quanti sono (per l'anteprima del modulo). */
void cmd_conta_destinatari(const char *to);

/* La TUI (src/tui.c): false se il terminale è troppo piccolo. */
bool ams_tui(void);

#endif
