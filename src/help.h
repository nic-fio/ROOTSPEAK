/* Copyright (c) 2026 Nicola Fiorillo
 * SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0 */

/* RootSpeak - Advanced Messaging System for Linux
 * Built-in help of rspeak --help, modelled on MTERM's. */
#ifndef RSPEAK_HELP_H
#define RSPEAK_HELP_H

/* In a terminal: interactive help with tabs; with a terminal smaller than
 * 44x10: manual-style page in a pager; if the output is not a terminal:
 * plain text. */
void rspeak_help(void);

#endif
