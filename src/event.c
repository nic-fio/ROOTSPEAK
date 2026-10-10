/* Copyright (c) 2026 Nicola Fiorillo
 * SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0 */

/* RootSpeak - Advanced Messaging System for Linux
 * Structured events in the journal, and their text. */
#include "event.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <syslog.h>
#include <systemd/sd-journal.h>

void channel_text(const char *channel, buf_t *out)
{
	/* The channel is stored as it is shown: «terminal pts/N» or «desktop»
	 * (message store format 1). */
	buf_adds(out, channel);
}

bool event_text(const char *ev, long long id, const char *user, const char *channel,
		  const char *details, const char *author, buf_t *out)
{
	buf_t ch = {0};
	bool ok = true;

	channel_text(channel, &ch);
	if (!strcmp(ev, "SENT"))
		buf_printf(out, "message %lld sent by %s to: %s", id, author, details);
	else if (!strcmp(ev, "DELIVERED") && *details)
		buf_printf(out, "message %lld delivered to %s (terminals written: %s)", id, user, details);
	else if (!strcmp(ev, "DELIVERED"))
		buf_printf(out, "message %lld delivered to %s (recovery)", id, user);
	else if (!strcmp(ev, "NOT_DELIVERED"))
		buf_printf(out, "message %lld: ERROR, copy for %s not written", id, user);
	else if (!strcmp(ev, "CANCELLED"))
		buf_printf(out, "message %lld: sending interrupted before it was saved, cancelled", id);
	else if (!strcmp(ev, "RECOVERED") && !strcmp(details, "1"))
		buf_printf(out, "message %lld: delivery completed for 1 recipient after an interruption", id);
	else if (!strcmp(ev, "RECOVERED"))
		buf_printf(out, "message %lld: delivery completed for %s recipients after an interruption", id,
			   details);
	else if (!strcmp(ev, "DELETED"))
		buf_printf(out, "message %lld deleted by %s (older than %s)", id, author, details);
	else if (!strcmp(ev, "REMINDED") && !strcmp(details, "1"))
		buf_printf(out, "message %lld: 1 recipient reminded by %s", id, author);
	else if (!strcmp(ev, "REMINDED"))
		buf_printf(out, "message %lld: %s recipients reminded by %s", id, details, author);
	else if (!strcmp(ev, "REVOKED"))
		buf_printf(out, "message %lld revoked by %s", id, author);
	else if (!strcmp(ev, "POSTPONED"))
		buf_printf(out, "user %s: postponed message %lld (%s)", user, id, ch.s ? ch.s : "");
	else if (!strcmp(ev, "CONFIRMED"))
		buf_printf(out, "user %s: confirmed reading message %lld (%s)", user, id, ch.s ? ch.s : "");
	else if (!strcmp(ev, "CONFIRMATION_FAILED"))
		buf_printf(out, "user %s: ERROR, confirmation of message %lld not recorded (%s): %s", user, id,
			   ch.s ? ch.s : "", *details ? details : "unknown error");
	else
		ok = false;
	buf_free(&ch);
	return ok;
}

void event(const char *ev, long long id, const char *user, const char *channel, const char *details,
	    const char *author)
{
	buf_t txt = {0}, det = {0};

	user = user ? user : "";
	channel = channel ? channel : "";
	author = author ? author : "";
	/* the details (for example an error message) on a single line */
	for (const char *p = details ? details : ""; *p; p++)
		buf_addc(&det, *p == '\n' ? ' ' : *p);
	if (!det.s)
		buf_adds(&det, "");
	event_text(ev, id, user, channel, det.s, author, &txt);
	if (sd_journal_send("MESSAGE=%s", txt.s ? txt.s : ev, "SYSLOG_IDENTIFIER=rspeak", "PRIORITY=%d", LOG_INFO,
			    "RSPEAK_EVENT=%s", ev, "RSPEAK_MESSAGE=%lld", id, "RSPEAK_USER=%s", user, "RSPEAK_CHANNEL=%s",
			    channel, "RSPEAK_DETAILS=%s", det.s, "RSPEAK_AUTHOR=%s", author, NULL) < 0) {
		/* without the journal, at least syslog */
		openlog("rspeak", 0, LOG_USER);
		syslog(LOG_INFO, "%s", txt.s ? txt.s : ev);
		closelog();
	}
	buf_free(&txt);
	buf_free(&det);
}
