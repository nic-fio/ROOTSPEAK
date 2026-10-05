# Working on RootSpeak (formerly AMS)

How this project is developed: the agreements, the decisions already taken and
what to check before recording a change. A clone plus this file is all the
working context: nothing needed to continue lives outside the repository.

The product is **RootSpeak — Advanced Messaging System for Linux**. The
administrators' command is `rspeak`. It is meant for administrators and speaks
English only.

## How we work

- **Talk to the user in Italian, always**, with no sentences in English. Only
  the conversation is in Italian.
- **Everything in the repository is in English** (decision of 1 October 2026):
  code, identifiers, file names, comments, program messages, configuration,
  tests, tools, `README.md`, the manuals, this file, the decision history and
  commit messages, with no exception: the product has no translations (decision
  «English only» below). Older commits stay as they are. The old name does not
  appear anywhere in code, configuration, tests or manuals: no `AMS_…`, no
  `ams`, no `[AMS]` (only the decision history mentions it).
  `tools/check-docs.py` fails if the old name or Italian reappears.
- **The manuals quote the program exactly**: every output quoted in a manual is
  the English text in `src/`, copied, never paraphrased or glossed.
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
| **Root does not touch inboxes as root** | Every access to `/var/lib/rootspeak/users/U` happens in a child process with the user's identity (`as_user`), with a time limit. |
| **zenity** for the desktop | Window «I have read it» / «Later»; `notify-send`, if present, only to report a confirmation that was not recorded. |
| **Built-in help like MTERM's, no man page** | Tabs in a terminal, manual-style page with a pager below 44×10, plain text in a pipe; texts in `src/help.c`. |
| **Manuals in the common style of the 7 projects (1 October 2026)** | Generated from `docs/sources/` (one file per chapter) into two self-contained HTML files in English (`User Manual.html`, `Technical Manual.html`), with the common style of the 7 projects' manuals, approved by the owner: embedded in every manual and identical in all of them. `docs/sources/style.css` is the canon (born from this project) and `docs/sources/manual.js` the common script (sidebar search, index, Copy button): they are copied verbatim, never changed in one project only; rules specific to this project live in `RSPEAK_CSS` in `build.py` (no script of its own: the common script does the Copy button). Cover: logo (`docs/sources/cover-logo.png`, transparent copy of the logo in `logos/`), «User Manual»/«Technical Manual», version and date. Footer: `<Product> · User Manual · Version X · Month YYYY · © 2026 Nicola Fiorillo · Licence: freeware`. Index only in the technical manual, from the glossary terms. The user rejected manuals in the NESH style ("they suck"). |
| **Rewrite in C (30 September)** | Everything: the command and the helper; the shell hooks stay scripts, the window stays zenity. Done: version 0.2.0; the bash prototype was removed when the C passed all tests (it remains in git history). Mandatory defences: all warnings, `-fanalyzer`, sanitizers in the tests, fuzzing of everything that reads users' files. |
| **English only (1 October 2026)** | The product is meant for administrators: program, messages, TUI, help, manuals and code are in English only, whatever the language of the session. The translations and the language machinery of 30 September (gettext catalogues, our `.mo` reader, the language chosen per user and per terminal) were removed. Normal users see in English only the frame of the terminal text, the question «[y/N]» (only `y` confirms) and the dialog buttons; the message text is what the administrator writes. TUI keys: `y` confirms, `m` reminds. |
| **TUI for administrators (30 September)** | The command without arguments in a terminal opens the TUI (`--help` stays the help; in a pipe it shows the help). Browse, act (revoke, purge, remind) with confirmation, write and send (Ctrl+E opens `$EDITOR`), automatic refresh. No ncurses. The TUI uses the same functions as the commands and **does not invent states**: only sent, delivered, confirmed; revoked and expired as properties. A message is summarised with its recipients: a three-colour bar and «14 confirmed · 5 delivered · 2 sent». |
| **Name: RootSpeak (1 October 2026)** | The product will be distributed and sold, and «AMS» is taken for software in the EU (ams-OSRAM, Emerson/Fisher-Rosemount and others). Product name **RootSpeak**, subtitle «Advanced Messaging System for Linux» (descriptive, not a name: it cannot be registered). Administrators' command **`rspeak`**; everything else uses the full name: helper `rootspeak-user`, paths `/etc/rootspeak`, `/var/lib/rootspeak`; the journal identifier stays the command name (`journalctl -t rspeak`). Rejected: LMS, MessageX, TuxCast (taken), Heedbell, Missivo (disliked), `rtspk` (reads like RTSP). No trademark registration for now: the user does not want to pay for it. |
| **Everything in English (1 October 2026)** | See «How we work». Replaces the exception of the common standard for the `.c`/`.h` file names in `src/`: in this project they are English too. Visible names are English as well: journal fields `RSPEAK_EVENT`, `RSPEAK_MESSAGE`…, events `DELIVERED`, `CONFIRMED`…, store files `revoking`, `.deleting-ID`, `rootspeak-agent.ready`. |
| **systemd required in 1.0 (1 October 2026)** | Supported: distributions with systemd (logind, `systemd-run`), about 90% of the market. Not in 1.0: Alpine, Void, Gentoo with OpenRC, Devuan, other distributions without systemd. |
| **Packages (5 October 2026)** | `.deb`, `.rpm` and Arch packages of our own, downloaded from the website (not the distributions' archives: closed source); in `/usr`, while the archive installs in `/usr/local`. One configuration step for both: `rootspeak-setup` (`etc/`). Not signed and no repository for now: `SHA256SUMS`. The logo is the icon (software centres, notices), no menu entry. |
| **Freeware (5 October 2026)** | RootSpeak is given away, like NESH and EFI Partition Manager: the RootSpeak Freeware Licence (`LICENSE`, the same text as theirs, adapted): free use on any number of machines, also at work and in paid work; free redistribution unchanged; no sale, no inclusion in commercial products, no modification. Commercial licences: `rootspeak@nicfio.it` (alias on the nesh@ mailbox). Distributed as built programs, not as source; the repository stays private. Replaces «Licence: to be decided», the trial and full editions and the road to sale. Footer of the manuals: `… · © 2026 Nicola Fiorillo · Licence: freeware`. |

## Rename to RootSpeak (1 October 2026)

Order agreed with the user; each step recorded in its own commit.

1. **Decision**: this file and `docs/decisions-and-history.md` in English. Done.
2. **Logo**: no. 07 «Orbit» among 20 proposals. Master
   `logos/rootspeak-logo.svg` (text in Outfit, SIL OFL 1.1),
   `logos/rootspeak-logo.png` 2172×724 rendered from it; the transparent copy
   `docs/sources/cover-logo.png` is made from the PNG (Outfit is not installed
   here). Done.
3. **Trademark check** of «RootSpeak»: WIPO Global Brand Database (89 sources,
   EUIPO and UIBM included), 1 October 2026. One record only: «ROOTSPEAK», US
   application 99350201, pending since 21 August 2025, class 41
   (education/entertainment), owner Dara Caldwell-Ross — not software, not in
   Europe. Not checked: the split form «root speak». A professional search is
   advisable before selling outside the EU.
4. **Rename** in code, paths, tests and documents. Done; live test by the user.
5. **English only and language pass**: translations and language machinery
   removed; code, comments, identifiers, file names, `Makefile` targets,
   tests, tools and documents in English. Done on 1 October 2026.
6. **Manuals**: regenerated with the new name, logo and English TUI
   screenshots; every page checked. Done with step 5.
7. **Repository**: `nic-fio/ROOTSPEAK` (whole history), local folder
   `~/Documenti/ROOTSPEAK`; `nic-fio/AMS` and the old folder deleted; VM folder
   `/media/ROOTSPEAK`. **Still to do, in the other 6 projects** (on GitHub, not
   cloned on this PC): the mentions of AMS in their `CLAUDE.md` (8 lines), and
   the English comments of the common `docs/sources/style.css` and
   `docs/sources/manual.js` (translated here on 1 October: the files must be
   the same in all 7 projects). The user chose to do it in a dedicated session
   in each project (a session here cannot change the other repositories); the
   task text was given to the user on 1 October.
8. **Licence**: freeware (5 October 2026): `LICENSE`, `NOTICE.md`, a
   «Licence» section in the README and in the user manual. Done.

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
| `src/` | The C code: `rspeak.c` (administrators' command), `rootspeak-user.c` (helper running as the user), `store.c`, `user.c`, `sessions.c`, `text.c`, `event.c`, `help.c`, `common.c`, `tui.c`. |
| `Makefile` | `make`, `make unit`, `make test` (unit tests, manual checks, `tests/engine.sh`), `make docs`, `make docs-check`, `make sanitizer`, `make analyze`, `make clean`. |
| `etc/` | Shell hooks, desktop agent autostart, default configuration. |
| `install.sh` | Install, upgrade, `--uninstall`, `--purge`; `DESTDIR=` only copies the files (for the packages). |
| `docs/` | `User Manual.html` and `Technical Manual.html` (generated, never by hand), `index.html` (home page), `README.md` (what is there and how to regenerate it), `.nojekyll`, `decisions-and-history.md`, `adversarial-review.md`. |
| `docs/sources/` | `build.py` (generator and helpers for figures and tables), `style.css` and `manual.js` (style and script common to the 7 projects, not to be changed here), `cover-logo.png` (the cover logo), chapters in `user/` and `technical/`, real TUI screenshots in `screens/` and `user/screens/`. The command reference of the user manual is read from `src/help.c`. |
| `tests/` | `engine.sh`: the engine in test mode; `help-tui.py`: the interactive help on a virtual terminal; `tui.py`: the TUI; `container/`: the test machine and real scenarios (`setup.sh` prepares it on any distribution); `distros/`: the same scenarios on 22 distributions, on the test server; `vm/`: the desktop VM on the test server; `fuzz/`: fuzzing; `unit-tests.c`: the internals (`make unit`). Results in `results/` and `*/results/`. |
| `tools/packages/` | `make-package.sh` and the files of the `.deb` (`debian/`), `.rpm` (`rpm/rootspeak.spec`) and Arch (`arch/`) packages; `tools/release.sh` runs it in the debian-12, rhel-9 and arch images on the test server. |
| `tools/` | `check-docs.py`: consistency between code, help and manuals; `fingerprint.sh`: code fingerprint recorded with the results; `tui-screenshots.sh`: real TUI screenshots for the manuals; `setup-dev.sh`: what is missing to work on a fresh clone; `backup.sh`: the whole repository in a git bundle; `release.sh`: the downloads in `build/release/`: the archive and the three packages (programs built on RHEL 9 on the test server, glibc 2.34, so they run on all 22 distributions). |
| `logos/` | The project logo: `rootspeak-logo.svg` (master) and `rootspeak-logo.png` (2172×724); the covers of the manuals and of `docs/index.html` use its transparent copy `docs/sources/cover-logo.png`. `rootspeak-icon.svg` (the mark without the text) and its PNG at 48, 128, 256 px: the icon the packages install. |
| `site/` | The website, `https://rootspeak.nicfio.it`, on the owner's VPS. `landing/`: the landing page (mockup 19 «Night sky», chosen on 1 October 2026 among 20 mockups, which are lost: `site/mockups/` was outside git); since 5 October with Download and Free instead of trial and prices. `publish.sh` builds `site/public/` (landing, manuals, `licence.html` from `LICENSE` by `licence-page.py`, `download/` with the archive of `tools/release.sh`, its `SHA256SUMS` and the licence, `og.jpg`, `robots.txt`, `sitemap.xml`; `seo-head.py` adds description, canonical address and link preview) and copies it to the VPS as user `progetti`; `--build` only builds. |
| `LICENSE`, `NOTICE.md` | The RootSpeak Freeware Licence; copyright, the licence in short and third-party components (none embedded). |
| `.github/workflows/ci.yml` | On GitHub at every push: `make`, `make unit`, `tests/engine.sh`, `make docs-check` (no container or VM). |

**Test server** (192.168.0.2, ssh access with a key): the VMs live in
`/media/ROOTSPEAK` on the SSD (the server's `/` is in RAM). QEMU with KVM as a
normal user, without libvirt or sudo. One desktop profile per VM
(`tests/vm/desktops/*.yaml`: debian-gnome, ubuntu-gnome, ubuntu-cinnamon,
fedora-kde, rocky-gnome; `tests/vm/run.sh PROFILE`), each with its folder
(`vm` for Debian, `vm-PROFILE`), ssh port and base disk, prepared again
automatically when the profile or `tests/vm/users.sh` change (10–30 minutes);
every run starts from a clean copy and shuts the VM down at the end. RAM is
tight: at most 2–3 VMs at a time, with `RSPEAK_VM_MEMORY=4G`/`6G`. The server's system is ephemeral:
every reboot loses the installed packages (only `/media` survives). The test
scripts check first and print the command for the owner, who has sudo:
`ssh -t 192.168.0.2 'sudo apt install -y podman qemu-system-x86 qemu-utils
genisoimage curl python3'` (from a real terminal, not with `!`). After a
reboot the ssh key may be refused for a minute while the server starts.

## Before recording a change

1. `make` (warnings as errors) and `make unit`.
2. `make docs` (`python3 docs/sources/build.py`), then `make docs-check`
   (`tools/check-docs.py`): it fails if the manuals in `docs/` don't match the
   sources, if the built-in help and the user manual reference diverge, if a
   code file is missing from the file map, if the version doesn't match, if an
   internal link is broken, if `tests/engine.sh` was not run on the current
   code, or if the old name or Italian appears in the repository.
   **It fails if the manuals are not up to date.**
3. `tests/engine.sh` always; `tests/help-tui.py` if the help changed;
   `make sanitizer` with `RSPEAK_BUILD=build-san tests/engine.sh`, `make analyze`
   and `tests/fuzz/run.sh` if code that reads data changed;
   `tests/container/run.sh` (real tests as root in a container) if sending,
   delivery, confirmations or permissions changed; `tests/distros/run.sh`
   (the scenarios on 22 distributions, on the test server, about 15 minutes with
   `RSPEAK_PARALLEL=8`) if the build, `install.sh`, the shell hooks or anything
   that depends on the distribution changed; `tests/vm/run.sh` (VM with
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

Version: `RSPEAK_VERSION` in `src/common.h`, and the same in the two manuals
(checked by `tools/check-docs.py`).

## Where things stand

Version 0.2.0 in C (30 September 2026), renamed RootSpeak and English only on
1 October 2026. Suites (numbers in the technical manual, chapter «Tests and
checks», read from the results): `tests/engine.sh`, `tests/tui.py`,
`tests/help-tui.py`, `make unit`, container and VM, all passed on 1 October
2026, also with AddressSanitizer and UBSan; fuzzing with no defects. The
container and the VM desktop are in Italian on purpose: RootSpeak must speak
English anyway (scenarios L5, I12).

Live tests on the user's PC (Debian 13, GNOME), 1 October 2026, before the
English-only change: `./install.sh`, `rspeak send --to user` to the account
`user` logged in on the desktop, `status` «delivered», «I have read it» in the
dialog, `status` «confirmed … (desktop)»; a second message postponed with
«Later», brought back with `rspeak remind` and confirmed; `remind` on a
message confirmed by everyone. Not yet tested live with the C version:
expiry, the question in a terminal opened over ssh. The English-only build
was tested live the same day: `./install.sh` (English messages), `rspeak send`
to `user`, dialog in English, «Later» (`delivered, postponed on …`),
`rspeak remind`, «I have read it» (`confirmed on … (desktop)`). Then a send
from an administrator connected over ssh (from Android, `user` with sudo; the
store records `from: user`, as designed) to `nicfio`: dialog on GNOME,
confirmed there (message 4); a second one confirmed with `y` in a desktop
terminal, stored as `terminal pts/2` (message 5); `rspeak revoke 6` before any
answer («Message 6 revoked.», `list` «[revoked] … 1 delivered», the copy gone
from the mailbox); the TUI opened over ssh from the phone (Termius), list,
bars and keys as expected. The bash prototype was tested live on 29–30 September (window, terminal
also over ssh, single confirmation across channels).

**Compatibility (1 October 2026)**: `tests/distros/run.sh` runs the real
scenarios on 22 distributions with systemd (Debian 12–13, Ubuntu 22.04–26.04,
Fedora 44–45, CentOS Stream 9–10, RHEL 9–10 as UBI, Rocky, Alma and Oracle
9–10, openSUSE Leap 16 and Tumbleweed, SLES 15 and 16, Arch): all passed. Each
image is built from the official one by `tests/container/setup.sh`; RootSpeak
is compiled inside. Defects of RootSpeak found and fixed: the build failed on
Ubuntu 22.04 and RHEL 9 (`_FORTIFY_SOURCE=3`) and on SLES 15 (gcc 7: no
`-std=c17`, no `-fcf-protection`): the `Makefile` now probes the compiler;
`install.sh` did not hook zsh on Arch (no `/etc/zsh/zshrc`): it creates the
file. Limits of the distributions, documented: dash on Fedora/RHEL stops on
`/etc/profile.d/lang.sh`; on openSUSE `/usr/bin/ksh` cannot be a login shell
(use `/usr/bin/ksh93`). Test-machine quirks handled in `setup.sh` (masked
logind in Alma/UBI images, missing machine-id in Arch's, `systemd-pam` on
Fedora, EPEL on the rebuilds, `logger` on SUSE) and in `scenarios.py` (TERM,
answers to fish 4's terminal queries, OSC sequences of systemd 259, the user's
real primary group on SLES). On the test server podman must be run with
`--root /media/ROOTSPEAK/distros/storage`: a `storage.conf` is ignored by
rootless podman and the images (about 20 GB) would fill the server's RAM.
**Desktops (1 October 2026)**: five VM profiles, all passed (65 of 69, the four
shells are not in the VMs): Debian 13 GNOME/Wayland, Ubuntu 24.04 GNOME/X11,
Ubuntu 24.04 Cinnamon/X11 (stand-in for Mint 22, which has no cloud image),
Fedora 44 KDE Plasma/Wayland, Rocky 9 GNOME/Wayland with SELinux enforcing (no
denials). They found a RootSpeak defect, fixed: when the session ended with the
dialog open (logout, display manager restarted, compositor crash) zenity's
exit 1 was recorded as «Later», and the dialog came back only after
`RSPEAK_REMIND_MINUTES`; now a postponement is recorded only if the display is
still there (`display_alive()` in `rootspeak-user.c`, sessions «closing» not
counted in `graphical_session()`), scenario I13. The diagnosis was split among
three agents, one VM each: give each agent its own port (run.sh: 2222 Debian,
then 2223+ in the alphabetical order of the profiles) — wrong ports made two
agents work in each other's VM.

**Freeware and the website** (the user, 5 October 2026): RootSpeak is given
away like NESH and EFI Partition Manager (decision above), so the trial and
full editions, payments, the commercial licence and the road to sale are
dropped. The steps, in this order: (1) licence — done; (2) what is downloaded:
an archive with the built programs, `install.sh` and the manuals, no source,
built on the oldest supported distribution and tested on all 22 — done
(`tools/release.sh`, 22 of 22 passed on 5 October); (3) the site — online
since 5 October 2026 (Let's Encrypt certificate, every page and the download
checked; DNS record A `rootspeak` added in the OVH zone); sitemap submitted
to Search Console (domain property nicfio.it) on 5 October: first status
«Couldn't fetch», because Google had cached the name as nonexistent before
the DNS record; the server answers Googlebot with 200. Check it again. Earlier plan for (3)
on `rootspeak.nicfio.it`, like `nesh.nicfio.it` and `efipm.nicfio.it`: the
«Night sky» landing page with Download and Free instead of trial and prices,
the licence page, the manuals, `site/publish.sh` with the search-engine tags,
`robots.txt`, `sitemap.xml`; (4) the owner creates the site on the VPS
(`~/Documenti/VPS/add-site.sh`) and the DNS record; then publication and the
sitemap in Search Console (the domain property nicfio.it already covers the
subdomains). Version 1.0 comes later.

**Packages** (the user, 5 October 2026, before advertising the product):
`.deb`, `.rpm` and Arch, built by `tools/release.sh`, on the landing page
(a card per family) and in `download/`; scenarios P1–P7 with
`RSPEAK_RELEASE=build/release tests/distros/run.sh`. Next steps proposed to
the user: the logo as the zenity dialog's window icon (zenity 3 and 4 differ:
needs the VM tests), signed packages with an APT/DNF repository for automatic
upgrades (needs a GPG key kept by the owner).

Live test of the `.deb` on the owner's PC (Debian 13, GNOME), 5 October 2026,
over the installation from `install.sh`: «the installation from the archive in
/usr/local was replaced by this package»; `rspeak send --to user` (message 7),
dialog, «I have read it», `status` «confirmed … (desktop)». It found a defect:
dpkg asked what to do with the archive's `rootspeak.conf` (and stops without a
terminal); fixed with a `preinst`, verified by scenario P6 on the 22
distributions, not yet live (`apt install --reinstall` of the fixed package
asked nothing, but dpkg already knew the file).

The adversarial review of 30 September 2026
([docs/adversarial-review.md](docs/adversarial-review.md)) is closed. The [2]
items of the README were frozen until the review was closed; restart from
there only when the user says so.
