/* RootSpeak - Advanced Messaging System for Linux
 * Users, and root actions performed with a user's identity. */
#ifndef RSPEAK_USER_H
#define RSPEAK_USER_H

#include "common.h"

typedef struct {
	char *name;
	uid_t uid;
	gid_t gid;
} user_t;

bool user_find(const char *name, user_t *u);
bool user_from_uid(uid_t uid, user_t *u);
void user_free(user_t *u);

/* Runs fn(arg) in a child process with u's identity: this way root does not
 * follow symbolic links planted by the user and does not read what the user
 * could not read. The child receives in (if given) on stdin; its output, at
 * most max bytes, goes into out (if given). After seconds seconds the child
 * is stopped. Result: fn's exit code, or -1 (child not started, identity not
 * assumed, time limit reached, child killed).
 * In test mode, without root, the child keeps the identity of whoever
 * launches the program. */
typedef int (*as_user_fn)(void *arg);
int as_user(const user_t *u, as_user_fn fn, void *arg, const buf_t *in, buf_t *out, size_t max,
		int seconds);

#endif
