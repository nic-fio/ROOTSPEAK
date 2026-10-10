# Copyright and third-party components

Required Notice: Copyright (c) 2026 Nicola Fiorillo (https://nicfio.it)

RootSpeak - Advanced Messaging System for Linux - is released under the
**PolyForm Noncommercial License 1.0.0**. See [LICENSE.md](LICENSE.md). It is
free for any noncommercial use; for commercial use write to
**rootspeak@nicfio.it**. The source code is published so that anyone can
check what RootSpeak does on their machines.

Version 0.2.1 was released under the RootSpeak Source-Available Licence
(`LICENSE-0.2.1`), version 0.2.0 under the RootSpeak Freeware Licence
(`LICENSE-0.2.0`); copies of those versions keep their licence.

## Third-party components

These components keep their own licences: the terms above apply to RootSpeak
itself, not to them.


RootSpeak neither embeds nor distributes third-party code: `rspeak`,
`rootspeak-user`, the shell hooks and the manuals are written for this
project. The style of the manuals comes from IR_Service, another project by
the same author.

It uses, without including them, programs and libraries already present on
the system, each with its own licence:

| Component | How RootSpeak uses it | Licence |
|---|---|---|
| libsystemd | dynamically linked to `rspeak` and `rootspeak-user` (journal, logind sessions) | LGPL-2.1 or later |
| zenity, notify-send | started as external programs, for the confirmation dialog on the desktop | LGPL-2.1 or later |
| Pygments | only to generate the manuals (code highlighting) | BSD 2-Clause |
