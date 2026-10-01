/* RootSpeak - Advanced Messaging System for Linux
 * Operazioni sulle caselle degli utenti, eseguite con la loro identità, e
 * scrittura nei terminali. Usate da rspeak (root). */
#ifndef RSPEAK_ARCHIVIO_H
#define RSPEAK_ARCHIVIO_H

#include "comune.h"
#include "utente.h"

/* Crea users/U (700, dell'utente) e, come U, inbox read acks state; poi, se U
 * non ha già letto o confermato il messaggio, scrive la copia (testo in msg)
 * e controlla che ci sia. Esito true se la copia c'è (o era già stata letta). */
bool consegna_copia(const utente_t *u, long long id, const buf_t *msg);
/* Toglie copia e rinvii di un messaggio (ritiro); true se la copia non c'è più. */
bool togli_copia(const utente_t *u, long long id);
/* Toglie i rinvii (sollecito); true se non ne restano. */
bool togli_rinvii(const utente_t *u, long long id);
/* Toglie copia, lettura, conferma e rinvii (cancellazione). */
void cancella_copie(const utente_t *u, long long id);

/* Conferme e rinvii di un utente per i messaggi dati (letti come l'utente,
 * al più 200 byte per conferma, ripuliti). */
typedef struct {
	long long id;
	char *conferma; /* prima riga di acks/ID, o NULL */
	long long rinvio;  /* data di modifica più recente di state/ID.*, o 0 */
} voce_casella_t;
typedef struct {
	voce_casella_t *v;
	size_t n;
} casella_t;
void leggi_casella(const utente_t *u, const strv_t *ids, casella_t *out);
/* L'uscita del figlio che legge la casella («A ID riga», «S ID data»): per le prove. */
void casella_da_testo(const char *raw, size_t n, casella_t *out);
const voce_casella_t *casella_voce(const casella_t *c, long long id);
void casella_libera(casella_t *c);

/* Scrive testo nel terminale t solo se, una volta aperto, è un terminale che
 * appartiene a uid (il nome /dev/pts/N non identifica una sessione); al più
 * 3 secondi. */
bool scrivi_terminale(const char *t, uid_t uid, const char *testo, size_t n);
/* Lingua di chi usa il terminale t (dell'utente u). */
void lingua_terminale(const char *t, const utente_t *u, char out[8]);
/* Sveglia l'agente del desktop dell'utente, o ne avvia uno. */
void sveglia_agente(const utente_t *u);

#endif
