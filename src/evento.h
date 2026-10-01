/* RootSpeak - Advanced Messaging System for Linux
 * Eventi strutturati nel journal. */
#ifndef RSPEAK_EVENTO_H
#define RSPEAK_EVENTO_H

#include "comune.h"

/* Evento: EVENTO MESSAGGIO UTENTE CANALE DETTAGLI AUTORE (vuoti se non servono).
 * Il testo leggibile (journalctl -t rspeak) è nella lingua del sistema; i campi
 * RSPEAK_* permettono di ricostruire la storia di un messaggio e ad rspeak log di
 * riscriverla nella lingua di chi legge. Il journal aggiunge _UID. */
void evento(const char *ev, long long id, const char *utente, const char *canale, const char *dettagli,
	    const char *autore);

/* Testo di un evento nella lingua data; false se l'evento non è noto. */
bool evento_testo(const char *lingua, const char *ev, long long id, const char *utente, const char *canale,
		  const char *dettagli, const char *autore, buf_t *out);

/* Canale registrato («terminale pts/3», «desktop») nella lingua data. */
void canale_testo(const char *lingua, const char *canale, buf_t *out);

#endif
