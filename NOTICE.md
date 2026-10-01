# Copyright and third-party components

RootSpeak - Advanced Messaging System for Linux
Copyright (c) 2026 nic-fio. All rights reserved.

The repository is private. No licence to use, copy, modify or distribute it
is granted: any use needs the author's explicit permission.

## Third-party components

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
