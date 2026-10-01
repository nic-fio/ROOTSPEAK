# RootSpeak - Advanced Messaging System for Linux

A tool with which the administrators of a Linux machine send text messages to
the users and know who has confirmed reading them.

Unlike `wall` and `write`, RootSpeak:

- reaches both the terminals (tty, ssh, tmux) and the graphical sessions (X11 and Wayland);
- keeps the messages for the users who are not logged in and shows them at their next login;
- records each user's read confirmation, with date and time;
- reminds whoever has not confirmed, **without ever blocking their work or logging anybody out**.

> Note: the confirmation records that the user *states* they have read the message,
> like the read ticks of a messaging app. It is no proof that they actually read it.

## Scope

- One machine only: no network, no sending between hosts.
- The `rspeak` command is reserved to the administrators, that is the members of the admin group that
  already exists (`sudo` on Debian/Ubuntu, `wheel` on Fedora/RHEL/Arch). RootSpeak creates no groups and has
  no permissions of its own.
- Users have no command at all: they only receive and confirm, automatically.
- Non-interactive sessions (cron, scp, rsync, ssh without a terminal, services) are never touched.
- RootSpeak speaks English, whatever the language of the session.

## Confirmation and states

Every message asks for a read confirmation and insists until the user confirms: a dialog on the
desktop, a question in the terminal and at login, reminders every 30 minutes. It never blocks. For each
recipient a message is **sent** (the copy is not yet in their mailbox), **delivered** (the copy is in
the mailbox) or **confirmed**. Expiry and revocation are properties of the message: for notices that
only matter for a short time use `--expires`.

## Interfaces

| Role | Interface |
|---|---|
| Administrator | `rspeak`: commands and, on its own in a terminal, the TUI (admin group only) |
| User in the terminal | No command: message and confirmation question appear automatically |
| User on the desktop | A minimal dialog with the "I have read it" button |

## Features

Legend: **[1]** first version · **[2]** second version · **[?]** to be decided

### Sending (administrator)
- [1] Recipients: a user, a list of users, a Unix group (`@group`), `all` (every human user), `online` (only those logged in)
- [1] Confirmation always requested; three states per recipient: sent, delivered, confirmed
- [1] Text from an argument, a file or stdin; optional title
- [1] Expiry (`--expires 2h`)
- [2] Scheduled sending (`--at "saturday 08:00"`)
- [2] Reusable message templates
- [?] Replies from the user to the administrator

### Management and control (administrator)
- [1] `rspeak list`: the messages sent, with the count of the confirmations
- [1] `rspeak status <id>`: state per user (delivered / confirmed, date and time, type of session)
- [1] `rspeak revoke <id>`: revokes a message
- [1] `rspeak remind <id>`: reminds whoever has not confirmed (the question and the dialog come back at once)
- [2] Export to CSV or JSON for audits
- [1] TUI for the administrator: `rspeak` on its own opens the list of the messages with the recipients in the
  three states, detail and history, writing and sending, revoke (`r`), remind (`m`) and purge (`p`) with
  a confirmation (`y`), automatic refresh

### Delivery
- [1] Terminal: writing to every active tty and pts, found through logind (not utmp)
- [1] Shell hook (bash, zsh, fish; sh, dash, ksh at login): pending messages at login and automatic
  confirmation question at the prompt
- [1] Desktop: dialog with the "I have read it" button (X11 and Wayland)
- [1] Queue for the users who are not logged in, with delivery at their next login
- [1] Dialog repeated every N minutes on the desktop until the user confirms

### Receiving (user)

Receiving is automatic: the user does not need to know or type any command.

- [1] **Desktop**: a dialog with the text and the **[Later]** and **[I have read it]** buttons appears on its own;
  with "Later" the dialog comes back after N minutes, until the user confirms.
- [1] **Terminal**: the full text appears in the terminal at the moment of sending; at the next prompt
  RootSpeak asks on its own “Do you confirm you have read the message? [y/N]”. If the user answers no,
  they see a reminder line at every prompt and the question comes back after N minutes.
- [1] **User not logged in**: message and question appear on their own at the next login.
- [1] Confirming once, in any session, is enough for the message to disappear everywhere.
- The user has no commands: once confirmed, the message cannot be read again
  (the full text is visible at the moment of the confirmation).

### Security (all [1])
- `rspeak` is installed as `root:<admin group>` with permissions `750`: other users cannot run it.
- If started by an administrator who is not root, `rspeak` re-runs itself with sudo (password as for any
  administrative operation). Whoever joins or leaves the admin group gains or loses access at once.
- Each user sees and confirms only their own messages, thanks to the permissions of their folder.
- The text is cleaned of control characters, to prevent the injection of escape sequences into terminals.
- Every operation is recorded in the system journal.

### Configuration and distribution
- [1] `/etc/rootspeak/rootspeak.conf`: interval of the reminders, check interval of the desktop agent
- [1] Installation script
- [1] User manual and technical manual in HTML (one file each), generated from `docs/sources/` with the
  common style of the 7 projects' manuals
- [1] Interactive built-in help (`rspeak --help`), modelled on MTERM's: tabs, a manual-style page
  if the terminal is small, plain text in a pipe. No man page.
- [1] `tools/check-docs.py`: fails if the built-in help and the manual diverge; `tests/help-tui.py` tests the help
- [2] deb and rpm packages

## Choices left out

- **Full-screen lock** of the graphical sessions: too invasive and not feasible on GNOME Wayland.
- **Lock at login** with forced logout of whoever does not confirm: too extreme.
- **GUI for the administrator**: administrators work from the terminal.
- **Dedicated `rspeak` group**: it would duplicate the admin group and would have to be kept aligned with it.
  To be reconsidered only if non-administrators ever need to send messages.
- **Commands for the user** (`rspeak read`, `rspeak ack`, `rspeak history`): receiving is automatic and the
  command stays reserved to root.
- **Translations**: RootSpeak is for administrators and speaks English only (decision of 1 October 2026).

## Architecture

No daemon: every piece uses tools already present on the system. The details are in the
[technical manual](docs/Technical%20Manual.html).

- `rspeak` always runs as root (it re-runs itself with sudo): it saves the message and delivers it at once to
  the active sessions, writing to the terminals and waking the desktop agent with a signal
  (if the agent is missing, it starts one with `systemd-run --user`).
- `/usr/local/lib/rootspeak/rootspeak-user`: internal helper, outside the PATH and not documented as a command.
  It runs as the user and only the hook and the agent use it, to show the messages and record the confirmation.
- The hook in `/etc/profile.d` shows the pending messages and the reminders in the terminal.
- A small agent started automatically in the graphical session (`/etc/xdg/autostart`)
  shows the confirmation dialog and shows it again as long as needed.
- Message store:
  - `/var/lib/rootspeak/sent/` — reference copy of the messages and of the recipients, accessible to root only;
  - `/var/lib/rootspeak/users/<user>/` — the user's messages and confirmations, accessible only to them and to root.
  `rspeak status` works out the state by comparing the two parts. If a user deletes a message
  from their own folder, the message simply shows as not confirmed.

The first prototype (0.1.0) was a shell script, to validate the flow; from version 0.2.0 RootSpeak
is written in C, with the same tests and the same store format.

## Installation

RootSpeak needs a distribution with systemd. Building needs gcc, make, pkg-config and the systemd
development files (`libsystemd-dev` on Debian and Ubuntu, `systemd-devel` on Fedora, RHEL and SUSE),
and the desktop needs `zenity`; the user manual lists the packages of each family. It is tested on 22
distributions (`tests/distros`) and on GNOME, KDE Plasma and Cinnamon, on Wayland and X11 (`tests/vm`).
`tools/setup-dev.sh` says which ones are missing (with `--install` it installs them). `tools/backup.sh` saves
the whole repository, with its history, in a single file.

```
make                      # builds in build/
./install.sh              # installs (asks for the sudo password)
./install.sh --uninstall  # removes, keeping messages and configuration
./install.sh --purge      # removes everything
```

| File | Role |
|---|---|
| `/usr/local/bin/rspeak` | The administrators' command (`root:sudo`, permissions 750) |
| `/usr/local/lib/rootspeak/` | Internal helper `rootspeak-user` and the bash and zsh hooks |
| `/etc/rootspeak/rootspeak.conf` | Configuration |
| `/etc/profile.d/rootspeak.sh` | Hook of the shells that read `/etc/profile` (also called from `/etc/bash.bashrc`); hands bash over to `lib/rootspeak/rootspeak.bash` |
| `/usr/local/lib/rootspeak/rootspeak.zsh` | zsh hook (called from the system zshrc) |
| `/etc/fish/conf.d/rootspeak.fish` | fish hook |
| `/etc/xdg/autostart/rootspeak-agent.desktop` | Automatic start of the desktop agent |
| `/var/lib/rootspeak/` | Messages sent (`sent/`) and the users' folders (`users/`) |
| `/usr/local/share/doc/rootspeak/` | User manual and technical manual (`User Manual.html`, `Technical Manual.html`) |

## Documentation

| Document | For whom |
|---|---|
| [`docs/User Manual.html`](docs/User%20Manual.html) | The administrators who use RootSpeak |
| [`docs/Technical Manual.html`](docs/Technical%20Manual.html) | Whoever develops RootSpeak: architecture, message store, security, tests |
| [`docs/decisions-and-history.md`](docs/decisions-and-history.md) | Why RootSpeak is the way it is |
| [`NOTICE.md`](NOTICE.md) | Copyright and third-party components |
| [`logos/rootspeak-logo.png`](logos/rootspeak-logo.png) | The RootSpeak logo (the logo files are in `logos/`) |
| [`CLAUDE.md`](CLAUDE.md) | Working agreements and decisions not to reopen |
| `rspeak --help` | The built-in help, in tabs |

The two manuals are self-contained HTML files: they open with a double click or with
`xdg-open "docs/User Manual.html"`, can be attached to an email and printed. GitHub does not show
them laid out (it shows the source code): download them or open them from the local copy.
After the installation they are also in `/usr/local/share/doc/rootspeak/`.

They are generated: edit the chapters in `docs/sources/user/` and `docs/sources/technical/`
and regenerate them with `make docs` (needs `python3-pygments`); `make docs-check` checks that they are aligned.
`docs/` also holds `index.html`, the home page of the documentation ([`docs/README.md`](docs/README.md)).

Examples:

```
rspeak send --to mario "On Saturday from 8 am to 12 noon the server will be off."
rspeak send --to @developers --title "Policy" --expires 3d --file policy.txt
rspeak send --to online --expires 15m "The web service restarts at 13:00."
rspeak list
rspeak status 12
rspeak revoke 12
```
