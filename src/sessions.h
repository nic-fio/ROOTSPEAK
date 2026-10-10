/* Copyright (c) 2026 Nicola Fiorillo
 * SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0 */

/* RootSpeak - Advanced Messaging System for Linux
 * Recipients and sessions (logind). */
#ifndef RSPEAK_SESSIONS_H
#define RSPEAK_SESSIONS_H

#include "common.h"

/* Human users: UID between UID_MIN and UID_MAX (/etc/login.defs) and a shell
 * that is not nologin or false. Root and system accounts are left out. */
void human_users(strv_t *out);
/* The human users with at least one open session. */
void online_users(strv_t *out);
/* Members of a group: listed in the group or having it as their primary group.
 * false if the group does not exist. */
bool group_members(const char *group_name, strv_t *out);
/* The user's terminals: the pseudo-terminals they own (ssh, terminal
 * emulators, tmux) plus the consoles of their text sessions. */
void user_terminals(uid_t uid, strv_t *out);
/* True if the user has a graphical session (x11 or wayland). */
bool graphical_session(uid_t uid);

#endif
