/* AMS - Advanced Messaging System for linux
 * Eventi strutturati nel journal, e il loro testo in ogni lingua. */
#include "evento.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <syslog.h>
#include <systemd/sd-journal.h>

#include "lingua.h"

void canale_testo(const char *lingua, const char *canale, buf_t *out)
{
	/* Il canale si salva senza lingua (formato 1 dell'archivio): «terminale
	 * pts/N» o «desktop»; si traduce solo quando si mostra. */
	if (!strncmp(canale, "terminale", 9))
		buf_printf(out, "%s%s", tl(lingua, "terminal"), canale + 9);
	else if (!strcmp(canale, "desktop"))
		buf_adds(out, tl(lingua, "desktop"));
	else
		buf_adds(out, canale);
}

bool evento_testo(const char *lingua, const char *ev, long long id, const char *utente, const char *canale,
		  const char *dettagli, const char *autore, buf_t *out)
{
	buf_t ch = {0};
	bool ok = true;

	canale_testo(lingua, canale, &ch);
	if (!strcmp(ev, "INVIATO"))
		buf_printf(out, tl(lingua, "message %lld sent by %s to: %s"), id, autore, dettagli);
	else if (!strcmp(ev, "CONSEGNATO") && *dettagli)
		buf_printf(out, tl(lingua, "message %lld delivered to %s (terminals written: %s)"), id, utente, dettagli);
	else if (!strcmp(ev, "CONSEGNATO"))
		buf_printf(out, tl(lingua, "message %lld delivered to %s (recovery)"), id, utente);
	else if (!strcmp(ev, "NON_CONSEGNATO"))
		buf_printf(out, tl(lingua, "message %lld: ERROR, copy for %s not written"), id, utente);
	else if (!strcmp(ev, "ANNULLATO"))
		buf_printf(out, tl(lingua, "message %lld: sending interrupted before it was saved, cancelled"), id);
	else if (!strcmp(ev, "RECUPERATO"))
		buf_printf(out, tl(lingua, "message %lld: delivery completed for %s recipients after an interruption"), id,
			   dettagli);
	else if (!strcmp(ev, "CANCELLATO"))
		buf_printf(out, tl(lingua, "message %lld deleted by %s (older than %s)"), id, autore, dettagli);
	else if (!strcmp(ev, "RITIRATO"))
		buf_printf(out, tl(lingua, "message %lld revoked by %s"), id, autore);
	else if (!strcmp(ev, "RINVIATO"))
		buf_printf(out, tl(lingua, "user %s: postponed message %lld (%s)"), utente, id, ch.s ? ch.s : "");
	else if (!strcmp(ev, "CONFERMATO"))
		buf_printf(out, tl(lingua, "user %s: confirmed reading message %lld (%s)"), utente, id, ch.s ? ch.s : "");
	else if (!strcmp(ev, "CONFERMA_FALLITA"))
		buf_printf(out, tl(lingua, "user %s: ERROR, confirmation of message %lld not recorded (%s): %s"), utente, id,
			   ch.s ? ch.s : "", *dettagli ? dettagli : tl(lingua, "unknown error"));
	else
		ok = false;
	buf_free(&ch);
	return ok;
}

void evento(const char *ev, long long id, const char *utente, const char *canale, const char *dettagli,
	    const char *autore)
{
	buf_t testo = {0}, det = {0};

	utente = utente ? utente : "";
	canale = canale ? canale : "";
	autore = autore ? autore : "";
	/* i dettagli (per esempio un messaggio d'errore) su una riga sola */
	for (const char *p = dettagli ? dettagli : ""; *p; p++)
		buf_addc(&det, *p == '\n' ? ' ' : *p);
	if (!det.s)
		buf_adds(&det, "");
	evento_testo(lingua_sistema(), ev, id, utente, canale, det.s, autore, &testo);
	if (sd_journal_send("MESSAGE=%s", testo.s ? testo.s : ev, "SYSLOG_IDENTIFIER=ams", "PRIORITY=%d", LOG_INFO,
			    "AMS_EVENTO=%s", ev, "AMS_MESSAGGIO=%lld", id, "AMS_UTENTE=%s", utente, "AMS_CANALE=%s",
			    canale, "AMS_DETTAGLI=%s", det.s, "AMS_AUTORE=%s", autore, NULL) < 0) {
		/* senza journal, almeno syslog */
		openlog("ams", 0, LOG_USER);
		syslog(LOG_INFO, "%s", testo.s ? testo.s : ev);
		closelog();
	}
	buf_free(&testo);
	buf_free(&det);
}
