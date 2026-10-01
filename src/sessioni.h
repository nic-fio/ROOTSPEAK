/* RootSpeak - Advanced Messaging System for Linux
 * Destinatari e sessioni (logind). */
#ifndef RSPEAK_SESSIONI_H
#define RSPEAK_SESSIONI_H

#include "comune.h"

/* Utenti umani: UID fra UID_MIN e UID_MAX (/etc/login.defs) e una shell che
 * non sia nologin o false. Root e gli account di sistema restano fuori. */
void utenti_umani(strv_t *out);
/* Gli utenti umani con almeno una sessione aperta. */
void utenti_online(strv_t *out);
/* Membri di un gruppo: elencati nel gruppo o con quello come gruppo principale.
 * false se il gruppo non esiste. */
bool membri_gruppo(const char *gruppo, strv_t *out);
/* Terminali dell'utente: gli pseudo-terminali di sua proprietà (ssh,
 * emulatori, tmux) più le console delle sue sessioni testuali. */
void terminali_utente(uid_t uid, strv_t *out);
/* Vero se l'utente ha una sessione grafica (x11 o wayland). */
bool sessione_grafica(uid_t uid);

#endif
