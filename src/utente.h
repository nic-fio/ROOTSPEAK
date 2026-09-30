/* AMS - Advanced Messaging System for linux
 * Utenti, e azioni di root con l'identità di un utente. */
#ifndef AMS_UTENTE_H
#define AMS_UTENTE_H

#include "comune.h"

typedef struct {
	char *nome;
	uid_t uid;
	gid_t gid;
} utente_t;

bool utente_cerca(const char *nome, utente_t *u);
bool utente_da_uid(uid_t uid, utente_t *u);
void utente_libera(utente_t *u);

/* Esegue fn(arg) in un processo figlio con l'identità di u: root non segue
 * così collegamenti simbolici preparati dall'utente e non legge ciò che
 * l'utente non potrebbe leggere. Il figlio riceve in (se c'è) su stdin; la
 * sua uscita, al più max byte, finisce in out (se c'è). Dopo secondi il
 * figlio viene fermato. Esito: il codice di uscita di fn, oppure -1 (figlio
 * non partito, identità non assunta, tempo scaduto, figlio ucciso).
 * In modalità di prova, senza root, il figlio resta con l'identità di chi
 * lancia il programma. */
typedef int (*come_utente_fn)(void *arg);
int come_utente(const utente_t *u, come_utente_fn fn, void *arg, const buf_t *in, buf_t *out, size_t max,
		int secondi);

#endif
