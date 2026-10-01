# RootSpeak (formerly AMS) — decisions and history

> Why RootSpeak is built the way it is: the context, the decisions and the
> history of the project. How it works in detail is in the
> [technical manual](Technical%20Manual.html), how to use it in the
> [user manual](User%20Manual.html) (HTML files: open them in a browser).
> Status: **version 0.2.0 in C**, all suites passed (30 September 2026); the
> rename from AMS to RootSpeak started on 1 October 2026. The bash prototype
> 0.1.0 was tested live on Debian 13 with GNOME 48 on Wayland.

This is the only document that keeps the old name: until 1 October 2026 the
product was called **AMS - Advanced Messaging System** and its command `ams`.

---

## 1. What it is

**RootSpeak — Advanced Messaging System for Linux** is a tool with which the
administrators of a Linux machine send text messages to its users and know who
has confirmed reading them.

```
administrator ── sudo rspeak send ──> user's inbox ──> terminals (text + question at the prompt)
                                                  ├──> desktop («I have read it» window / notice)
                                                  └──> at login, if not logged in
```

## 2. Context and research

- The need: reach the users of a machine with notices from the
  administrators, if possible with **read confirmation**.
- Before designing, we checked that nothing suitable already existed. Only
  separate pieces exist:
  - `wall` and `write`: they write only to the terminals of logged-in users,
    without confirmation;
  - `notify-send` via `systemd-run --user`: desktop notifications, without state;
  - `systembus-notify`: notifications from the system bus, without buttons or
    confirmations;
  - `/etc/motd`, sshd's `Banner`, the GDM banner, STIG consent banners:
    fixed texts at login, without per-user state.
- None keeps a **state per message and per user** or answers the question
  «who has not read it yet?». RootSpeak puts the pieces together and adds
  exactly that.

## 3. A user's sessions

We started from the «text/graphical × local/remote» classification and refined
it: ssh pseudo-terminals with and without a pty, terminals inside the desktop,
detached tmux, X11 versus Wayland, remote desktop sharing the local session or
creating a new one, non-interactive sessions (cron, scp, services), `su`.
Conclusion: the useful question is not «how is the user logged in» but **«on
which channels can I reach them now»** (terminal, desktop, none), and the
reliable source is **logind**, not utmp.

## 4. Decisions

| Decision | Why |
|---|---|
| **One machine, only administrators send** | The tool must stay «simple»: no network, no messages between users. |
| **Every message asks for confirmation; three states** | At first there were two levels, `ack` (with confirmation) and `info` (notice only). On 30 September, while working on the adversarial review, the user decided: «ALL messages have 3 states: sent, delivered, confirmed. The recipient must ALWAYS confirm reading», choosing to simplify the architecture. The «shown» state disappears: it confused delivery and reading (review, item 6). For short notices use `--expires`: after expiry the message is no longer shown or reminded. |
| **No blocking** | A `block` level was proposed and rejected (session closed if the user doesn't confirm within a grace period): «it kicks users out of the system, too extreme». Full-screen blocking was rejected too: invasive and not feasible on GNOME Wayland. Blocking would make the most common message worse («reboot in 10 minutes, save your work») and would break scripts. |
| **Automatic delivery** | Users must not know or type any command: desktop window, text and question in the terminal, all by itself. |
| **Users don't have the command** | They only receive and confirm. The code that runs as the user is the internal helper, outside the PATH. Accepted consequence: once confirmed, a message cannot be read again. |
| **No permission class of our own** | Proposed and rejected: an `ams-admin` group, then an `ams` group populated with the members of the root and admin groups. They would duplicate the administrators' group and go stale. The command is installed `root:sudo` (or `wheel`) with mode `750`. |
| **The command always runs as root, no exceptions** | It re-runs itself with sudo before any command, **including help and version**: a rule chosen by the user, at the cost of asking for the password even for help. |
| **No daemon** | Without the `block` level it is not needed: `send` delivers at once, the shell hook and the desktop agent do the rest. |
| **The first confirmation counts for all channels** | Found in a test: the user had to confirm twice (window and terminal). Now the terminal question notices the confirmation from the desktop, and the confirmation is written exclusively (`set -C`). |
| **Desktop agent woken by a signal** | Found in a test: the window arrived after 3-4 seconds (check every 10 s). `send` sends `SIGUSR1` to the agent: the window appears at once, and the periodic check goes to 60 s to save battery. |
| **`info` notices before confirmation windows** | Found in a test: at login a notice waited behind a window and looked like a second request. Superseded by the decision to always ask for confirmation. |
| **zenity for the window** | Standard, small package; a window that stays open until the user chooses. GNOME notifications can be ignored or disappear by themselves: unreliable for confirmation. |
| **Bash prototype** | To validate the flow with the system's tools. A rewrite in a compiled language would come only if concrete limits emerged. Superseded on 30 September: see the next row. |
| **Rewrite in C** | Decision of the user (30 September), after the second review: almost all the defects found came from bash (races between check and use, time limits, one process per operation). Rust was proposed to avoid memory corruption in a root program that reads users' files; the user chose C, with mandatory defences (warnings, static analysis, sanitizers, fuzzing). Everything is rewritten; the shell hooks stay scripts. |
| **TUI for administrators** | Decision of the user (30 September): for administrators, opened by the command without arguments, to browse, act, write and send, with automatic refresh. Discussing the previews, the user noticed invented states («pending», «complete», then «incomplete send» and «cancelled», technical markers of recovery that had ended up in the specification without going through the user): the states are only the three decided ones, revoked and expired are properties, and a message is summarised with the counts of its recipients in the three states, in words and with a bar. The specification was corrected accordingly. |
| **Languages with gettext** | Decision of the user (30 September): standard format and tools. The `.mo` files are read by our own code, not libintl, because with libintl a language not installed on the system stays untranslated even when forcing `LANGUAGE` (tested), while root must be able to write to each terminal in its user's language. |
| **Built-in help like MTERM's, no man page** | «I don't want a man system, but a much more evolved system»: tabbed help in a terminal, manual-style page with a pager if the terminal is small, plain text in a pipe. A check (`tools/check-docs.py`) keeps help and manual aligned. |
| **Manuals on the IR_Service model** | A first version copied from NESH's manuals was rejected by the user on everything (diagrams, look, texts, opening): «Once again the HTML manuals suck». The reference given was IR_Service's Technical Manual: the manuals are generated from Python sources (one file per chapter) into two self-contained HTML files, with cover, side index, SVG diagrams and numbered tables. The command reference is generated from the texts of the built-in help. Superseded on 1 October by the common style of the 7 projects. |
| **Manuals in English** | Decision of the user (30 September): the two manuals and their sources are in English and are called `User Manual.html` and `Technical Manual.html`. The command reference of the user manual therefore comes from the English source texts of the help, and `tools/check-docs.py` compares them. At the time everything else stayed in Italian; superseded on 1 October by «Everything in English». |
| **Confirmation question in all shells** | Decision of the user (30 September): «yes, for all shells». In practice: a question at every prompt for bash, zsh and fish; at login for every shell that reads `/etc/profile`; text on delivery for any shell (some shells, such as `dash` and `tcsh`, have no hook before the prompt). Done on 30 September, tested in the test machine (scenarios K). |
| **Users don't reply** | Decision of the user (30 September): replies from users «are not planned for now». |
| **The user's language** | Decision of the user (30 September): question, window, buttons and notices in each recipient's language (`LANG`); the administrator's commands in their language; the text of the message stays as it is. Done on 30 September: Italian and English, English as fallback; the system log in the machine's language, rewritten by `log` in the reader's language. |
| **Name: RootSpeak** | Decision of the user (1 October). The product will be distributed and sold. A search in TMview (EUIPO) found 150 live marks identical to «AMS» in the software classes (9, 42, 38), among them ams-OSRAM (EU marks 2012 and 2013, classes 9 and 42) and Emerson/Fisher-Rosemount (EU mark 2006, class 9, for software); «Advanced Messaging System» is descriptive and is also the name of a US software company. «LMS» (Siemens, Audi…), «MessageX» (a messaging service), «TuxCast» (several Linux programs and podcasts), «Ambo» (a Romanian software company), «Edict» were taken; «Heedbell» and «Missivo» were disliked. «RootSpeak» was free on GitHub, among Debian packages and domains; the WIPO Global Brand Database (89 sources, EUIPO and UIBM included) has a single record, a US application of 2025 in class 41 (education/entertainment), not software and not in Europe. Subtitle «Advanced Messaging System for Linux». Command `rspeak` (the user proposed `rtspk`, which reads like RTSP); the rest uses the full name. No trademark registration for now: the user does not want to pay for it (Italy from €149, EU from €850). |
| **Everything in English, no trace of the old name** | Decision of the user (1 October): code, identifiers, file names, comments, configuration, tests, tools and documents in English, for customers who receive the source; Italian only in the conversation with Claude and in the Italian translation for users. No `AMS_…`, `ams` or `[AMS]` left anywhere except this history; `tools/check-docs.py` enforces it. |
| **Licence: to be decided** | Until 1 October: «no licence», private repository. For sale a commercial licence is needed (proposal: per machine or organisation, internal use and modifications allowed, no redistribution, plus a clause on the rights of third-party components), to be reviewed by a lawyer. Apache 2.0 + Commons Clause (NESH, EFI_PARTITION_MANAGER) and «personal use only» (PHONESTRA) don't fit a product sold to organisations. |

## 5. Technical choices born from tests

- **Command in `/usr/local/bin`, not `sbin`**: on Debian non-root users don't
  have `sbin` in their PATH, and the command was «command not found».
- **ssh tests with `ssh user@localhost`, not `su`**: with `su` the terminal
  still belongs to whoever opened it, and `send` doesn't find it.
- **Two identical windows** in a test were a message sent twice (two IDs in
  `list`), not a defect: no fix.
- **`--expires` example corrected**: `date -d` doesn't understand
  `"saturday 12:00"`; the help uses the ISO format.
- **Revocation with an open window or question**: they close by themselves
  and don't record the confirmation of a revoked message.

## 6. History

| When | What |
|---|---|
| 29 September 2026, evening | Classification of sessions, purpose, search for existing tools, feature list, decisions on levels, blocking, user commands and permissions. Bash prototype and installation; first live tests (window, terminal, single confirmation, waking the agent). Private repository on GitHub. |
| 29 September 2026, night | Tests with a second user: delivery at graphical login, `info` notices, terminal over ssh. User manual in HTML in the NESH style; version 0.1.0. |
| 30 September 2026 | Interactive built-in help on the MTERM model, always as root; `tools/check-docs.py` and `tests/help-tui.py`. Technical manual, this document and `CLAUDE.md`. Manuals redone from scratch on the IR_Service model, with a generator in `docs/sorgenti/`. Adversarial review by two models and item-by-item work: confirmations never lost, delivery verified with recovery, three states for every message (no more levels), real suites in a container and in a desktop VM on the test server, structured events and `log`, `purge`, configuration as data, «Specification» chapter. Confirmation question in all shells (bash, zsh, fish; sh, dash, ksh at login) and the product in each user's language (Italian, English). |
| 30 September 2026, afternoon | Second review (two reviewers) and fixes: revocation serialised with sending, confirmations after revocation, terminal checked after opening, duration after a power cut, deletion in one go, anomalous inboxes. Rewrite in C (version 0.2.0) with gettext: same tests, all passed (engine, container, VM in Italian and English, help), plus sanitizers, static analysis and fuzzing; bash prototype removed. |
| 30 September 2026, evening | TUI for administrators (the command alone), after previews discussed with the user: correction of the invented states and of the specification; `remind`; `list` with the recipients in the three states. Tests: `tests/tui.py`, scenarios D5, T1-T3, I11; the VM found a reminder lost if it arrived within one second of «Later» (the agent now records the answer as soon as zenity closes). |
| 30 September 2026, night | Standard structure common to the 7 projects, decided by the owner: file and folder names in English (`docs/sources/`, `tests/results/`, `tests/unit-tests.c`, `tools/fingerprint.sh`, `run.sh` instead of `esegui.sh`; this document was called `decisioni-e-storia.md`), with the content unchanged; `NOTICE.md`, `docs/index.html`, `tools/setup-dev.sh`, `tools/backup.sh`, `make test`, `make docs`, `make docs-check`, CI on GitHub, the logo in `logos/`. |
| 1 October 2026 | Manuals and home page in the common style of the 7 projects. Licence analysis of the 7 projects: the product will be sold, so a name of its own is needed. Trademark search, new name **RootSpeak** with the command `rspeak`, everything in English with no trace of the old name; 20 logo proposals. `CLAUDE.md` and this document translated into English. |
