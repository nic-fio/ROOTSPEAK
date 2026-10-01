/* RootSpeak - Advanced Messaging System for Linux
 * The parts of rspeak also used by the TUI: the TUI reads the message store with
 * the same functions as the commands, and the actions are the commands themselves. */
#ifndef RSPEAK_RSPEAK_H
#define RSPEAK_RSPEAK_H

#include "common.h"
#include "text.h"

/* The states of a recipient: the only three («Specification» chapter). */
typedef enum { SENT, DELIVERED, CONFIRMED } state_e;

/* A message summarised with its recipients. */
typedef struct {
	long long id;
	msg_t m;
	int confirmed, delivered, sent;
	bool revoked, expired;
} summary_t;

/* The numbers of the messages in sent/, in order. */
void message_list(strv_t *ids);
/* Summarises message id; false if it does not exist (or the sending was cancelled). */
bool summarise(long long id, summary_t *r);
void summary_free(summary_t *r);
/* «14 confirmed · 5 delivered · 2 sent» or «all confirmed (58)». */
void summary_text(const summary_t *r, buf_t *out);

/* The recipients of a message with the status line of rspeak status. */
typedef struct {
	char *user;
	state_e state;
	char *line;
} recipient_t;
typedef struct {
	recipient_t *v;
	size_t n;
} recipients_t;
void recipients(long long id, const msg_t *m, recipients_t *out);
void recipients_free(recipients_t *d);
/* Date of the revocation (0 if not revoked). */
long long revocation_date(long long id);

/* The mailboxes read stay in memory: the TUI forgets them at every refresh. */
void mailboxes_empty(void);
/* Completes interrupted sendings, revocations and deletions. */
void recover(void);

/* The commands: they print as from the command line and, on error, exit
 * with die. The TUI runs them in a child process and shows their output. */
void cmd_send(int argc, char **argv);
void cmd_revoke(const char *arg);
void cmd_remind(const char *arg);
void cmd_purge(const char *dur);
void cmd_log(const char *arg);
/* Resolves the recipients and prints how many there are (for the form's preview). */
void cmd_count_recipients(const char *to);

/* The TUI (src/tui.c): false if the terminal is too small. */
bool rspeak_tui(void);

#endif
