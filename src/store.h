/* Copyright (c) 2026 Nicola Fiorillo
 * SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0 */

/* RootSpeak - Advanced Messaging System for Linux
 * Operations on the users' mailboxes, run with their identity, and writing
 * to terminals. Used by rspeak (root). */
#ifndef RSPEAK_STORE_H
#define RSPEAK_STORE_H

#include "common.h"
#include "user.h"

/* Creates users/U (700, owned by the user) and, as U, inbox read acks state; then, if U
 * has not already read or confirmed the message, writes the copy (text in msg)
 * and checks that it is there. Returns true if the copy is there (or was already read). */
bool deliver_copy(const user_t *u, long long id, const buf_t *msg);
/* Removes the copy and postponements of a message (revocation); true if the copy is gone. */
bool remove_copy(const user_t *u, long long id);
/* Removes the postponements (reminder); true if none remain. */
bool clear_postponements(const user_t *u, long long id);
/* Removes copy, read mark, confirmation and postponements (deletion). */
void remove_copies(const user_t *u, long long id);

/* A user's confirmations and postponements for the given messages (read as the user,
 * at most 200 bytes per confirmation, cleaned). */
typedef struct {
	long long id;
	char *confirm; /* first line of acks/ID, or NULL */
	long long postponement;  /* most recent modification time of state/ID.*, or 0 */
} mailbox_item_t;
typedef struct {
	mailbox_item_t *v;
	size_t n;
} mailbox_t;
void read_mailbox(const user_t *u, const strv_t *ids, mailbox_t *out);
/* The output of the child that reads the mailbox («A ID line», «S ID date»): for tests. */
void mailbox_from_text(const char *raw, size_t n, mailbox_t *out);
const mailbox_item_t *mailbox_item(const mailbox_t *c, long long id);
void mailbox_free(mailbox_t *c);

/* Writes txt to terminal t only if, once opened, it is a terminal that
 * belongs to uid (the name /dev/pts/N does not identify a session); at most
 * 3 seconds. */
bool write_terminal(const char *t, uid_t uid, const char *txt, size_t n);
/* Wakes up the user's desktop agent, or starts one. */
void wake_agent(const user_t *u);

#endif
