/* RootSpeak - Advanced Messaging System for Linux
 * Clean text, messages, configuration. */
#ifndef RSPEAK_TEXT_H
#define RSPEAK_TEXT_H

#include "common.h"

/* Removes ANSI escape sequences and control characters (C0 except
 * tab and newline, DEL, C1 in UTF-8), so a message cannot inject
 * sequences into terminals. Same result as the bash prototype. */
void clean_text(const char *in, size_t n, buf_t *out);

/* ---- messages ---- */

/* Format 1: header "key: value", blank line, text. */
typedef struct {
	long long id;
	char *from;
	long long date;
	char *title;
	long long expires; /* 0: no expiry */
	char *body;
} msg_t;

/* Reads a message: returns -1 if the file is missing, is not a regular file, is
 * too large or has no valid date. */
int msg_read(const char *path, msg_t *m);
int msg_from_text(const char *s, size_t n, msg_t *m);
void msg_free(msg_t *m);
void msg_format(const msg_t *m, buf_t *out);
bool msg_expired(const msg_t *m, time_t time_now);
/* «Title · 29/09 22:15», or just the date. */
void msg_header(const msg_t *m, buf_t *out);

/* ---- configuration ---- */

/* The file is data, not a script: KEY=value lines, comments with #,
 * spaces ignored. Only the known keys with positive integers (at
 * most 6 digits) are accepted; the rest is ignored. */
typedef struct {
	long remind_minutes; /* RSPEAK_REMIND_MINUTES, 30 */
	long agent_poll;     /* RSPEAK_AGENT_POLL, 60 */
} conf_t;

void conf_read(conf_t *c);
void conf_from_text(const char *s, conf_t *c);

#endif
