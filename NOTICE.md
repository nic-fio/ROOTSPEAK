# Copyright and third-party components

RootSpeak - Advanced Messaging System for Linux
Copyright (c) 2026 Nicola Fiorillo. All rights reserved.

RootSpeak is **freeware**, released under the **RootSpeak Freeware Licence**.
See [LICENSE](LICENSE).

## In short

| You may, free of charge | You may not, without a written licence |
|---|---|
| Use it for anything, at home or at work, also as a tool in paid work (administering the machines of a company, a school or a customer) | **Sell** it, or charge a fee for it |
| Copy it and give it to anyone, unchanged, with the licence | **Include** it in a product or service that is sold or offered as part of a business |
| Install it on any number of machines, also with your own deployment tools, and change its configuration file | **Modify** it, or decompile it beyond what the law allows |
| Put it in a collection of software given away free of charge, unchanged and with the licence | Remove the copyright and licence notices, or use the name to suggest an endorsement |

**Want to include it in a product, or buy the project?** Write to
**rootspeak@nicfio.it**.

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
