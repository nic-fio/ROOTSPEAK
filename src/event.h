/* RootSpeak - Advanced Messaging System for Linux
 * Structured events in the journal. */
#ifndef RSPEAK_EVENT_H
#define RSPEAK_EVENT_H

#include "common.h"

/* Event: EVENT MESSAGE USER CHANNEL DETAILS AUTHOR (empty when not needed).
 * The readable text is what journalctl -t rspeak shows; the RSPEAK_* fields
 * let rspeak log rebuild the history of a message. The journal adds
 * _UID. */
void event(const char *ev, long long id, const char *user, const char *channel, const char *details,
	    const char *author);

/* Text of an event; false if the event is not known. */
bool event_text(const char *ev, long long id, const char *user, const char *channel,
		  const char *details, const char *author, buf_t *out);

/* A recorded channel («terminale pts/3», «desktop») as it is shown. */
void channel_text(const char *channel, buf_t *out);

#endif
