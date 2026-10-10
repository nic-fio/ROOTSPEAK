# RootSpeak (formerly AMS) — decisions and history

> Why RootSpeak is built the way it is: the context, the decisions and the
> history of the project. How it works in detail is in the
> [technical manual](Technical%20Manual.html), how to use it in the
> [user manual](User%20Manual.html) (HTML files: open them in a browser).
> Status: **version 0.2.1 in C**, renamed RootSpeak and in English only on
> 1 October 2026; tested live on the owner's PC (Debian 13, GNOME) on the same
> day. The bash prototype 0.1.0 was tested live on Debian 13 with GNOME 48 on Wayland.

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
| **Languages with gettext** | Superseded on 1 October by «English only». Decision of the user (30 September): standard format and tools. The `.mo` files are read by our own code, not libintl, because with libintl a language not installed on the system stays untranslated even when forcing `LANGUAGE` (tested), while root must be able to write to each terminal in its user's language. |
| **Built-in help like MTERM's, no man page** | «I don't want a man system, but a much more evolved system»: tabbed help in a terminal, manual-style page with a pager if the terminal is small, plain text in a pipe. A check (`tools/check-docs.py`) keeps help and manual aligned. |
| **Manuals on the IR_Service model** | A first version copied from NESH's manuals was rejected by the user on everything (diagrams, look, texts, opening): «Once again the HTML manuals suck». The reference given was IR_Service's Technical Manual: the manuals are generated from Python sources (one file per chapter) into two self-contained HTML files, with cover, side index, SVG diagrams and numbered tables. The command reference is generated from the texts of the built-in help. Superseded on 1 October by the common style of the 7 projects. |
| **Manuals in English** | Decision of the user (30 September): the two manuals and their sources are in English and are called `User Manual.html` and `Technical Manual.html`. The command reference of the user manual therefore comes from the English source texts of the help, and `tools/check-docs.py` compares them. At the time everything else stayed in Italian; superseded on 1 October by «Everything in English». |
| **Confirmation question in all shells** | Decision of the user (30 September): «yes, for all shells». In practice: a question at every prompt for bash, zsh and fish; at login for every shell that reads `/etc/profile`; text on delivery for any shell (some shells, such as `dash` and `tcsh`, have no hook before the prompt). Done on 30 September, tested in the test machine (scenarios K). |
| **Users don't reply** | Decision of the user (30 September): replies from users «are not planned for now». |
| **The user's language** | Superseded on 1 October by «English only». Decision of the user (30 September): question, window, buttons and notices in each recipient's language (`LANG`); the administrator's commands in their language; the text of the message stays as it is. Done on 30 September: Italian and English, English as fallback; the system log in the machine's language, rewritten by `log` in the reader's language. |
| **Name: RootSpeak** | Decision of the user (1 October). The product will be distributed and sold. A search in TMview (EUIPO) found 150 live marks identical to «AMS» in the software classes (9, 42, 38), among them ams-OSRAM (EU marks 2012 and 2013, classes 9 and 42) and Emerson/Fisher-Rosemount (EU mark 2006, class 9, for software); «Advanced Messaging System» is descriptive and is also the name of a US software company. «LMS» (Siemens, Audi…), «MessageX» (a messaging service), «TuxCast» (several Linux programs and podcasts), «Ambo» (a Romanian software company), «Edict» were taken; «Heedbell» and «Missivo» were disliked. «RootSpeak» was free on GitHub, among Debian packages and domains; the WIPO Global Brand Database (89 sources, EUIPO and UIBM included) has a single record, a US application of 2025 in class 41 (education/entertainment), not software and not in Europe. Subtitle «Advanced Messaging System for Linux». Command `rspeak` (the user proposed `rtspk`, which reads like RTSP); the rest uses the full name. No trademark registration for now: the user does not want to pay for it (Italy from €149, EU from €850). |
| **Everything in English, no trace of the old name** | Decision of the user (1 October): code, identifiers, file names, comments, configuration, tests, tools and documents in English, for customers who receive the source; Italian only in the conversation with Claude. No `AMS_…`, `ams` or `[AMS]` left anywhere except this history; `tools/check-docs.py` enforces it. |
| **English only** | Decision of the user (1 October), after a reply added to `remind` had been documented with the Italian output and an English gloss: «nothing Italian in the program, in the messages and in the documentation… this product is meant for administrators, not for normal users, so English only». The Italian translation, the gettext catalogues, our `.mo` reader and the choice of language per user and per terminal (root read the environment of the users' processes for it) were removed: less code, less attack surface, one text to keep aligned. Proposed and rejected by the user's reasoning: keeping the language machinery without catalogues. What normal users still see in English: the frame of the terminal text, the question «[y/N]» (only y confirms) and the dialog buttons; the message text is whatever the administrator writes. With it, everything visible went to English: TUI keys (y confirms, m reminds), journal fields and event names, files of the message store, file names of the sources. `tools/check-docs.py` fails if Italian reappears. The comments of the common style and script of the manuals were translated too: to be carried to the other 6 projects. |
| **systemd required in 1.0** | Decision of the user (1 October), at the start of the compatibility tests on other distributions: RootSpeak relies on logind and `systemd-run` (no daemon of its own), and the distributions with systemd cover about 90% of the market. Distributions without systemd (Alpine, Void, Gentoo with OpenRC, Devuan) would need elogind and a replacement for `systemd-run`: days of work before 1.0, postponed. |
| **Landing page: «Night sky»** | Decision of the user (1 October), among 20 mockups with the same content and twenty visual directions, made by four agents in parallel: mockup 19, deep navy with stars, the logo's orbit as a planetary path and its orange dot as the planet. Kept in `site/landing/` (the user had asked for `logos/`: proposed `site/` instead, the folder of the future site, since `logos/` holds only the logo in the common structure of the 7 projects). Still to do before it goes live: fonts licensed for commercial use, prices, licence, download links, domain. |
| **Freeware** | Decision of the user (5 October 2026): «I want to make it freeware, exactly like NESH and EFI Partition Manager». Until then the plan was to sell it (trial and full editions, a merchant-of-record platform, a commercial licence still to be chosen, a VAT number to check); now it is given away under the RootSpeak Freeware Licence, the same text as NESH and EFI Partition Manager adapted: free use also at work, redistribution unchanged, no sale, no inclusion in commercial products, no modification; commercial licences through `rootspeak@nicfio.it`. Before: «Licence: to be decided» (no licence, private repository, from 1 October). |
| **Source available** | Decision of the user (5 October 2026), the same day: before proposing RootSpeak for a review to a well-known Linux channel on YouTube, the source code becomes public, «readable at least». A closed program that runs as root and changes the shell startup files cannot be checked by whoever installs it, and a reviewer who promotes free software would object first. The RootSpeak Source-Available Licence replaces the Freeware Licence from 0.2.1: in addition, read, build and change for one's own use (the user chose this over «read and build only»), publish reviews and short excerpts; still no sale, no commercial products, no distribution of changed versions; the clause on decompiling is gone. Published as a source archive on the website, not as a public repository (the user chose this over a second, public repository): the private repository holds the VPS address, the test server and the working notes. Version 0.2.1: the programs do not change, but the licence inside the packages does, and files with the same name and a different content would confuse whoever checks `SHA256SUMS`. |
| **PolyForm Noncommercial** | Decision of the user (10 October 2026): one licence for the source code of the projects on his home page (NESH, EFI Partition Manager, Phonestra, RootSpeak), the PolyForm Noncommercial License 1.0.0, official text, unchanged, in `LICENSE.md`, from the version after 0.2.1. Free for any noncommercial use, changes included; commercial use, also at work inside a company, needs a licence from `rootspeak@nicfio.it`. Accepted by the user: use at work inside a company is no longer granted. `NOTICE.md` starts with `Required Notice: Copyright (c) 2026 Nicola Fiorillo (https://nicfio.it)`; every source file written for the project carries the copyright line and `SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0`. The earlier licences stay with their versions: `LICENSE-0.2.1` (Source-Available), `LICENSE-0.2.0` (Freeware). |
| **Public repository** | Decision of the user (10 October 2026), after the change of licence: the repository becomes public, history and working notes included (VPS address, test server), told of them beforehand. The source archive on the website stays. |
| **PolyForm also for 0.2.1** | Decision of the user (10 October 2026): the PolyForm Noncommercial License covers 0.2.1 too; copies of 0.2.1 and 0.2.0 may be used under the licence they were released with or under the PolyForm, at the user's choice. The 0.2.1 packages are rebuilt with the same version number, the same programs and the new licence files, `NOTICE.md` included (user's choice, knowing that their checksums change). |

| **Packages for the tested distributions** | Request of the user (5 October 2026), before advertising the product: «a classic deb/rpm hosted on our server», for all the tested distributions, with links on the home page and the logo as icon. `.deb` (Debian, Ubuntu), one `.rpm` (Fedora, RHEL and its rebuilds, openSUSE, SLES), `.pkg.tar.zst` (Arch), in `/usr`; the archive stays for the others, in `/usr/local`. Not in the distributions' official archives: they build from source and want a free licence. No repository with signed updates: the user does not want to weigh the VPS down (it would have been static files; the real cost was a signing key to keep). Files to download with `SHA256SUMS`, upgrades by installing the new file. The logo as icon goes where people see RootSpeak (software centres, notices); no menu entry (users have no command, administrators use the terminal); no logo in the users' dialog either: users don't know RootSpeak, the title «Message from the administrator» is what tells them (the user, 5 October). |

## 5. Technical choices born from tests

- **Command in `/usr/local/bin`, not `sbin`**: on Debian non-root users don't
  have `sbin` in their PATH, and the command was «command not found».
- **ssh tests with `ssh user@localhost`, not `su`**: with `su` the terminal
  still belongs to whoever opened it, and `send` doesn't find it.
- **Two identical windows** in a test were a message sent twice (two IDs in
  `list`), not a defect: no fix.
- **`--expires` example corrected**: `date -d` doesn't understand
  `"saturday 12:00"`; the help uses the ISO format.
- **Packages: `rspeak` as `root:root 750` in the package**, the group set
  by `rootspeak-setup configure`: the administrators' group differs between
  families. The Arch package first came out with `rspeak` at `755` (makepkg
  runs as an unprivileged user): caught by scenario P1.
- **pacman refuses files it does not know**: moving from the archive to the
  package on Arch needs `./install.sh --uninstall` first; dpkg and rpm replace them.
- **The archive's `rootspeak.conf` under a `.deb`**: dpkg asked what to do with
  it (live test on the owner's PC, 5 October), and without a terminal it stops
  the installation. The `preinst` sets it aside, `postinst` puts it back; P6
  now fails if the question appears.
- **Ubuntu minimized and the Arch image skip `/usr/share/doc`**: the package
  installs there without the manuals, which are on the website.
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
| 1 October 2026 | Manuals and home page in the common style of the 7 projects. Licence analysis of the 7 projects: the product will be sold, so a name of its own is needed. Trademark search, new name **RootSpeak** with the command `rspeak`, everything in English with no trace of the old name; 20 logo proposals. `CLAUDE.md` and this document translated into English. Rename in code, paths, tests and documents; live test of the C version on the owner's PC (delivery, «Later», reminder, confirmation on the desktop). Then English only: translations and language machinery removed, everything in the repository in English. |
| 1 October 2026, afternoon | Compatibility: decision «systemd required in 1.0»; tests on 22 distributions in containers on the test server (`tests/distros/run.sh`, `tests/container/setup.sh` for apt, dnf, zypper and pacman), the investigation of the last failures split among four agents, one test machine each. RootSpeak defects fixed: build on Ubuntu 22.04, RHEL 9 and SLES 15 (the `Makefile` probes `_FORTIFY_SOURCE`, `-std=c17`, `-fcf-protection`), zsh hook on Arch (`install.sh` creates `/etc/zsh/zshrc`), the build error names the systemd development files of every family. All 22 passed; the user manual lists the packages per family. |
| 1 October 2026, evening | Desktops: `tests/vm` made of profiles (`tests/vm/desktops/*.yaml`, `users.sh`), one base disk each, prepared again when the profile changes. Ubuntu 24.04 with GNOME and with Cinnamon (for Mint), Fedora 44 with KDE Plasma, Rocky 9 with GNOME and SELinux enforcing, Debian 13 with GNOME: all passed, on Wayland and on X11. Three agents, one VM each, found and diagnosed a RootSpeak defect: a dialog left open at the end of the session was recorded as «Later» and came back only after the reminder time; fixed (a postponement only with the display still there) and covered by scenario I13; scenario I10 now logs out as soon as zenity has the answer (through accessibility it takes about 0.35 s, with a real key 40 ms). |
| 5 October 2026 | Alias `rootspeak@nicfio.it`. Decision «Freeware»: `LICENSE`, `NOTICE.md`, «Licence» in the README and in the user manual, licence in the footer of the manuals. The downloadable archive (`tools/release.sh`: built on RHEL 9, glibc 2.34, no source), tested on the 22 distributions as a customer installs it: all passed. The installation chapter of the user manual starts from the download. The website prepared for `rootspeak.nicfio.it` (`site/publish.sh`, landing page with Download and Free, licence page, search-engine tags). |
| 5 October 2026, afternoon | Packages: `.deb`, `.rpm` and Arch made by `tools/release.sh` with the tool of each family (`tools/packages/`), from the same programs built for `/usr`; `install.sh` split into copying files (also into `DESTDIR`) and `rootspeak-setup`, which the packages run too; the folder of the manuals compiled in (`DOCDIR`); the logo as icon (`logos/rootspeak-icon*`) and an AppStream description. Package scenarios P1–P7 (install, verify, reinstall, `install.sh` refusing, removal, from the archive to the package, purge) on the 22 distributions with `RSPEAK_RELEASE`. Landing page: a download for each family. |
| 5 October 2026, evening | Decision «Source available»: the RootSpeak Source-Available Licence, version 0.2.1, the source archive made by `tools/release.sh` (a fixed list of files, the script fails if the working notes or the website end up in it) and downloaded from the website next to the packages; `NOTICE.md`, README, the two manuals, the package metadata and the landing page (licence box, a question in the FAQ) updated. |
