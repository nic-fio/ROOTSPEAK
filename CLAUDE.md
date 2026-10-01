# Working on RootSpeak (formerly AMS)

How this project is developed: the agreements, the decisions already taken and
what to check before recording a change. A clone plus this file is all the
working context: nothing needed to continue lives outside the repository.

The product is **RootSpeak — Advanced Messaging System for Linux**. The
administrators' command is `rspeak`. The rename is done in code, paths, tests
and documents (see «Rename in progress» below); parts of the code and of the
documents are still in Italian until the language pass.

## How we work

- **Talk to the user in Italian, always**, with no sentences in English. Only
  the conversation is in Italian.
- **Everything in the repository is in English** (decision of 1 October 2026):
  code, identifiers, file names, comments, program messages, configuration,
  tests, tools, `README.md`, the manuals, this file, the decision history and
  commit messages. The one exception is the Italian translation for users,
  `po/it.po`, which is a feature of the product. Older commits stay as they are.
  The old name does not appear anywhere in code, configuration, tests or
  manuals: no `AMS_…`, no `ams`, no `[AMS]` (only the decision history
  mentions it).
  Until the language pass is done, parts of the code and of the documents are
  still in Italian (see «Rename in progress»).
- **When the user proposes something**, first say whether it improves or
  worsens the result and why, then do it or make a counter-proposal.
- **Texts for users without programmer jargon**: the built-in help, the
  messages and the user manual are written for the people who use the product.
- **Verify, don't declare.** Every statement about behaviour comes from a run:
  test mode, `tests/`, or a live test after `./install.sh`. «It should work» is
  not a result.
- **Documentation counts as much as code.** A feature is not finished until the
  manuals describe it. The manuals are judged like graphic work: diagrams in
  every chapter, practical texts, and every page looked at with a screenshot
  before delivering it.
- **Claude does not have the sudo password**: installation and tests as root
  are run by the user (`! ./install.sh`, `! rspeak …`). Careful: if the user's
  sudo credentials are still cached, `build/rspeak` without `RSPEAK_TEST=1` starts as
  root without asking anything. In tests always set test mode (technical
  manual, «Testing without root»).

## Decisions taken: do not reopen them

The reasons for each are in [docs/decisions-and-history.md](docs/decisions-and-history.md).

| Decision | |
|---|---|
| **One machine, only administrators send** | No network, no messages between users. |
| **Every message asks for confirmation; three states** | For each recipient: sent, delivered (copy in the inbox), confirmed. No levels (`info` was removed on 30 September: a choice to simplify the architecture); for short notices use `--expires`. Expiry and revocation are properties of the message. |
| **No blocking** | No `block` level, no logouts, no full-screen lock: the user can always postpone. |
| **Automatic delivery, no command for users** | Users don't have the administrators' command; the code that runs as the user is the helper `rootspeak-user`, outside the PATH. |
| **The command always runs as root, no exceptions** | It re-runs itself with sudo before anything else, including `--help` and `version`. |
| **No group of our own** | The existing admin group is used (`sudo`/`wheel`): the command is `root:<group>` `750`. |
| **No daemon** | logind, sudo, the shell hook, desktop autostart. |
| **Root does not touch inboxes as root** | Every access to `/var/lib/rootspeak/users/U` happens in a child process with the user's identity (`come_utente`), with a time limit. |
| **zenity** for the desktop | Window «I have read it» / «Later»; `notify-send`, if present, only to report a confirmation that was not recorded. |
| **Built-in help like MTERM's, no man page** | Tabs in a terminal, manual-style page with a pager below 44×10, plain text in a pipe; texts in `src/guida.c` (English) and in the `po/` catalogues. |
| **Manuals in the common style of the 7 projects (1 October 2026)** | Generated from `docs/sources/` (one file per chapter) into two self-contained HTML files in English (`User Manual.html`, `Technical Manual.html`), with the common style of the 7 projects' manuals, approved by the owner: embedded in every manual and identical in all of them. `docs/sources/style.css` is the canon (born from this project) and `docs/sources/manual.js` the common script (sidebar search, index, Copy button): they are copied verbatim, never changed in one project only; rules specific to this project live in `RSPEAK_CSS` in `build.py` (no script of its own: the common script does the Copy button). Cover: logo (`docs/sources/cover-logo.png`, transparent copy of the logo in `logos/`), «User Manual»/«Technical Manual», version and date. Footer: `<Product> · User Manual · Version X · Month YYYY · © 2026 Nicola Fiorillo` (no licence). Index only in the technical manual, from the glossary terms. The user rejected manuals in the NESH style ("they suck"). |
| **Rewrite in C (30 September)** | Everything: the command and the helper; the shell hooks stay scripts, the window stays zenity. Done: version 0.2.0; the bash prototype was removed when the C passed all tests (it remains in git history). Mandatory defences: all warnings, `-fanalyzer`, sanitizers in the tests, fuzzing of everything that reads users' files. |
| **Languages with gettext (30 September)** | gettext format and tools (`po/*.po`, `.mo`, `msgfmt --check`), source texts in English; the `.mo` files are read by our own reader, not libintl: with libintl a language not installed on the system does not work (tested: `C.UTF-8` ignores `LANGUAGE`), and root must write to each terminal in its user's language. |
| **TUI for administrators (30 September)** | The command without arguments in a terminal opens the TUI (`--help` stays the help; in a pipe it shows the help). Browse, act (revoke, purge, remind) with confirmation, write and send (Ctrl+E opens `$EDITOR`), automatic refresh. No ncurses. The TUI uses the same functions as the commands and **does not invent states**: only sent, delivered, confirmed; revoked and expired as properties. A message is summarised with its recipients: a three-colour bar and «14 confirmed · 5 delivered · 2 sent». |
| **Name: RootSpeak (1 October 2026)** | The product will be distributed and sold, and «AMS» is taken for software in the EU (ams-OSRAM, Emerson/Fisher-Rosemount and others). Product name **RootSpeak**, subtitle «Advanced Messaging System for Linux» (descriptive, not a name: it cannot be registered). Administrators' command **`rspeak`**; everything else uses the full name: helper `rootspeak-user`, paths `/etc/rootspeak`, `/var/lib/rootspeak`, catalogue `rootspeak.mo`. Rejected: LMS, MessageX, TuxCast (taken), Heedbell, Missivo (disliked), `rtspk` (reads like RTSP). No trademark registration for now: the user does not want to pay for it. |
| **Everything in English (1 October 2026)** | See «How we work». Replaces the exception of the common standard for the `.c`/`.h` file names in `src/`: in this project they become English too. |
| **Licence: to be decided** | Private repository, copyright Nicola Fiorillo. For sale a commercial licence is needed (proposal: per machine or organisation, internal use and modifications allowed, no redistribution, plus the clause on the rights of third-party components), to be reviewed by a lawyer. Until then: no licence. |

## Rename in progress (1 October 2026)

Order agreed with the user; each step is recorded in its own commit.

1. **Decision**: this file and `docs/decisions-and-history.md` in English with
   the new decisions. Done.
2. **Logo**: chosen by the user among 20 proposals (no. 07, «Orbit»: the old
   symbol redrawn — envelope, orbit, orange dot). Master
   `logos/rootspeak-logo.svg` (text in Outfit, SIL OFL 1.1),
   `logos/rootspeak-logo.png` 2172×724 rendered from it. Done; it replaced
   `logos/ams-logo.png` and the transparent copy `docs/sources/cover-logo.png`
   at step 4 instead of step 6 (the check on the old name also covers file
   names); the copy is made from the PNG because Outfit is not installed here.
3. **Trademark check** of «RootSpeak»: done on 1 October 2026 in the WIPO
   Global Brand Database (89 sources, EUIPO and UIBM included; TMview had
   blocked our automated searches). One record only: «ROOTSPEAK», US
   application 99350201, pending since 21 August 2025, class 41
   (education/entertainment), owner Dara Caldwell-Ross — not software, not in
   Europe. Not checked: the split form «root speak». A professional search is
   advisable before selling outside the EU.
4. **Rename** in code, paths, tests, documents (`ams` → `rspeak`,
   `ams-user` → `rootspeak-user`, every `AMS_…` constant, variable, header
   guard and the `[AMS]` prefix of terminal messages → `RSPEAK_…` /
   `[RootSpeak]`), then all the suites, container and VM included, and a live
   test by the user. **No trace of the old name may remain** in code,
   configuration, tests, tools or manuals: the old name survives only as
   history (`docs/decisions-and-history.md`, «formerly AMS»).
   `tools/check-docs.py` fails if `AMS`/`ams` reappears in a tracked file
   or file name outside those places (allowed also: the origin comment of the
   common `style.css`, the quoted titles of the two reviews in
   `docs/adversarial-review.md`). Done on 1 October 2026: engine 82, help,
   TUI, sanitizers, container 72 of 72 (+1 desktop not testable there),
   fuzzing, VM, manuals regenerated with the new logo and screenshots. The
   journal identifier stays the command name (`journalctl -t rspeak`). The
   legacy clean-up of the bash prototype was removed from `install.sh`
   (nobody has an AMS installation to upgrade). Live test by the user on
   1 October 2026 (see «Where things stand»).
5. **Language pass**: code, comments, identifiers, file names, `Makefile`
   targets, tests, tools and documents into English, file by file, in a
   separate commit from the rename. **No Italian may remain** outside
   `po/it.po` and the history of decisions.
6. **Manuals**: regenerated with the new name, logo and TUI screenshots;
   every page checked.
7. **Repository**: done on 1 October 2026 by the user's choice: a new private
   repository `nic-fio/ROOTSPEAK` with the whole git history (42 commits,
   identical hashes), local folder `~/Documenti/ROOTSPEAK`, CI passed;
   `nic-fio/AMS` and the old local folder deleted; links and the VM folder
   (`/media/ROOTSPEAK`) renamed at step 4. Still to do: the mentions of AMS in
   the `CLAUDE.md` of the other 6 projects (8 lines, on GitHub: they are not
   cloned on this PC).
8. **Licence**: commercial licence, `NOTICE.md`, a «Licence» section in the
   README and in the manuals.

## The repository

The structure follows the standard common to the 7 projects (ROOTSPEAK,
EFI_PARTITION_MANAGER, HOSTER, MTERM, NESH, PHONESTRA, SCRAPER), decided by the
owner on 30 September 2026: file and folder names in English, `README.md`,
`CLAUDE.md`, `NOTICE.md`, `Makefile` with `make`, `make test`,
`make docs-check`, `make clean`, `.github/workflows/ci.yml`, `logos/`, `src/`,
`tests/`, `tools/` and `docs/` with `index.html`, the two manuals,
`README.md`, `decisions-and-history.md`, `.nojekyll`, `sources/`.

| Where | What |
|---|---|
| `src/` | The C code: `rspeak.c` (administrators' command), `rootspeak-user.c` (helper running as the user), `archivio.c`, `utente.c`, `sessioni.c`, `testo.c`, `lingua.c`, `evento.c`, `guida.c`, `comune.c`, `tui.c`. |
| `po/` | gettext catalogues: `rootspeak.pot` and the translations (`it.po`). |
| `Makefile` | `make`, `make prove`, `make test` (unit tests, manual checks, `tests/engine.sh`), `make docs`, `make docs-check`, `make sanitizer`, `make analizza`, `make pot`, `make clean`. |
| `etc/` | Shell hooks, desktop agent autostart, default configuration. |
| `install.sh` | Install, upgrade, `--uninstall`, `--purge`. |
| `docs/` | `User Manual.html` and `Technical Manual.html` (generated, never by hand), `index.html` (home page), `README.md` (what is there and how to regenerate it), `.nojekyll`, `decisions-and-history.md`, `adversarial-review.md`. |
| `docs/sources/` | `build.py` (generator and helpers for figures and tables), `style.css` and `manual.js` (style and script common to the 7 projects, not to be changed here), `cover-logo.png` (the cover logo), chapters in `user/` and `technical/`, real TUI screenshots in `screens/` and `user/screens/`. The command reference of the user manual comes from the English source texts in `po/rootspeak.pot`. |
| `tests/` | `engine.sh`: the engine in test mode; `help-tui.py`: the interactive help on a virtual terminal; `tui.py`: the TUI; `container/`: the test machine and real scenarios; `vm/`: the desktop VM on the test server; `fuzz/`: fuzzing; `unit-tests.c`: the internals (`make prove`). Results in `results/` and `*/results/`. |
| `tools/` | `check-docs.py`: consistency between code, help and manuals; `fingerprint.sh`: code fingerprint recorded with the results; `tui-screenshots.sh`: real TUI screenshots for the manuals; `setup-dev.sh`: what is missing to work on a fresh clone; `backup.sh`: the whole repository in a git bundle. |
| `logos/` | The project logo: `rootspeak-logo.svg` (master) and `rootspeak-logo.png` (2172×724); the covers of the manuals and of `docs/index.html` use its transparent copy `docs/sources/cover-logo.png`. |
| `NOTICE.md` | Copyright and third-party components (none embedded). |
| `.github/workflows/ci.yml` | On GitHub at every push: `make`, `make prove`, `tests/engine.sh`, `make docs-check` (no container or VM). |

**Test server** (192.168.0.2, ssh access with a key): the VM lives in
`/media/ROOTSPEAK` on the SSD (the server's `/` is in RAM). QEMU with KVM as a
normal user, without libvirt or sudo. The base disk is prepared once
(`tests/vm/run.sh --prepara`, about 10 minutes); every run starts from a clean
copy and shuts the VM down at the end.

## Before recording a change

1. `make` (warnings as errors) and `make prove`; `make pot` if translatable
   texts changed, then the translation in `po/it.po`.
2. `make docs` (`python3 docs/sources/build.py`), then `make docs-check`
   (`tools/check-docs.py`): it fails if the manuals in `docs/` don't match the
   sources, if the built-in help and the user manual reference diverge, if a
   code file is missing from the file map, if the version doesn't match, if an
   internal link is broken, if a catalogue is incomplete or if
   `tests/engine.sh` was not run on the current code.
   **It fails if the manuals are not up to date.**
3. `tests/engine.sh` always; `tests/help-tui.py` if the help changed;
   `make sanitizer` with `RSPEAK_BUILD=build-san tests/engine.sh`, `make analizza`
   and `tests/fuzz/run.sh` if code that reads data changed;
   `tests/container/run.sh` (real tests as root in a container) if sending,
   delivery, confirmations or permissions changed; `tests/vm/run.sh` (VM with
   GNOME on the test server, 192.168.0.2) if the desktop changed.
   The results are recorded together with the change.
4. A test of the affected flow in test mode; for desktop, sudo and other
   users, a live test after `./install.sh`, done by the user.
5. Commits use the repository's local identity (name `nic-fio`, GitHub noreply
   address), which keeps the personal address out. Messages in English (from
   1 October 2026). Never `git add -A` without looking at `git status`.

The **«Specification»** chapter of the technical manual is the contract of the
product (authoritative sources, states, invariants, interruptions, time,
archive format): every change respects it or updates it explicitly.

Version: `RSPEAK_VERSION` in `src/comune.h`, and the same in the two manuals
(checked by `tools/check-docs.py`).

## Where things stand

Version 0.2.0 in C (30 September 2026), which replaces the bash prototype
0.1.0. Suites (numbers kept up to date in the technical manual, chapter 11,
read from the results): `tests/engine.sh` 82 checks, `tests/tui.py`, container
72 scenarios (plus the desktop, which cannot be tested there), VM with an
Italian desktop 66 scenarios, all passed (shells are tested only in the
container; `RSPEAK_PROVA_LINGUA=en` for the English desktop, 11 of 11)
(30 September 2026), also with AddressSanitizer and UBSan; fuzzing for 30
minutes with no defects. The bash prototype was also tested live on Debian 13
with GNOME 48 on Wayland, with two accounts (`nicfio`, `user`): window at once
and at login, text and question in the terminal also over ssh, a single
confirmation across channels, `list` and `status`. `revoke`, expiry, errors
and text cleaning tested in test mode. The adversarial review of 30 September
2026 ([docs/adversarial-review.md](docs/adversarial-review.md)) is closed: the
two remaining decisions were taken on 30 September: the confirmation question
in all shells (bash, zsh, fish at every prompt; at login for the shells that
read `/etc/profile`), no replies from users, interface in each user's
language. Shells and languages are done (scenarios K and L; gettext
catalogues in `po/`, English as fallback). The C version (as RootSpeak) was
tested live on the user's PC on 1 October 2026: `./install.sh` on Debian 13
with GNOME, `rspeak send --to user` from the administrator's session to the
account `user` logged in on the desktop, `status` «delivered», then «I have
read it» in the window and `status` «confirmed … (desktop)» a minute after
sending. Not yet tested live with the C version: the question in the
terminal and over ssh, `revoke`, expiry. The [2] items of
the README were frozen until the review was closed; restart from there only
when the user says so.

On 1 October 2026 the rename to RootSpeak was done (step 4, see above).
