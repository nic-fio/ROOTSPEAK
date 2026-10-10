# Copyright (c) 2026 Nicola Fiorillo
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0

from build import arrow, box, c, code, file_map, fig, flow, note, p, steps, table, text, tree, ui, ul, warn


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">chapter {n}{"." + str(s) if s else ""}</a>'


TREE = tree([
    "RootSpeak/",
    "├── src/                  # the C code: two programs, common parts",
    "├── etc/                  # shell hooks, autostart, configuration",
    "├── install.sh            # installation, upgrade, removal",
    "├── Makefile              # build, tests, analysis, sanitizer",
    "├── docs/                 # the two generated manuals, decisions, reviews",
    "│   └── sources/          # generator, style, one file per chapter",
    "├── tests/                # engine, TUI, help, units, fuzzing, container, VM",
    "│   └── */results/        # results recorded with commit and fingerprint",
    "├── tools/                # manual consistency, fingerprint, screenshots, release",
    "│   └── packages/         # .deb, .rpm and Arch packages",
    "└── site/                 # the website: landing page, publication",
], "«FIG» — The folders of the repository")

S1 = p("The repository contains the C code, the files to install on the system, the manuals "
       "with their sources, the tests and the consistency checks. The following table is the <b>file map</b>: "
       "the lines are counted every time the manual is generated, and " + c("tools/check-docs.py") + " fails if a "
       "code file is missing or if one that does not exist is listed.", lead=True) + TREE + file_map([
    ("src/rspeak.c", "The administrators' command: relaunch through sudo, recipients, " + c("send") + ", " + c("list")
     + ", " + c("status") + ", " + c("revoke") + ", " + c("remind") + ", " + c("log") + ", " + c("purge")
     + ", message summaries, recovery."),
    ("src/rspeak.h", "The parts of rspeak also used by the TUI: recipient states, summary, commands."),
    ("src/tui.c", "The TUI for administrators: list, detail and history, writing and sending, actions with confirmation."),
    ("src/help.c", "The built-in help: tabbed guide, manual-style page, plain text."),
    ("src/help.h", "Interface of help.c."),
    ("src/store.c", "The operations on the mailboxes, always with the user's identity; writing to terminals; "
     "waking up the agent."),
    ("src/store.h", "Interface of store.c."),
    ("src/rootspeak-user.c", "The helper that runs as the user: " + c("prompt") + " (shell hook), " + c("agent")
     + " (desktop), recording of confirmations."),
    ("src/user.c", c("as_user") + ": a child process with a user's identity and a time limit."),
    ("src/user.h", "Interface of user.c."),
    ("src/sessions.c", "Human users, groups, sessions and terminals, from passwd, group and logind."),
    ("src/sessions.h", "Interface of sessions.c."),
    ("src/text.c", "Text cleaning, message format, configuration."),
    ("src/text.h", "Interface of text.c: " + c("msg_t") + ", " + c("conf_t") + "."),
    ("src/event.c", "Structured events in the journal and their text."),
    ("src/event.h", "Interface of event.c."),
    ("src/common.c", "Utilities: environment, errors, memory, growable strings, safe reading and writing of files."),
    ("src/common.h", "Interface of common.c, version (" + c("RSPEAK_VERSION") + ") and limits."),
    ("Makefile", "Build, internal tests, static analysis, sanitizer."),
    ("install.sh", "Installation, upgrade, removal from the archive; with " + c("DESTDIR") + " it only copies the "
     "files into a folder, for the packages."),
    ("etc/rootspeak-setup", "What an installation does besides copying files, the same for " + c("install.sh")
     + " and the packages: administrators' group, hook lines, store folders, agents; it takes the place of an "
     "installation from the archive."),
    ("etc/rootspeak.metainfo.xml", "The AppStream description that software centres show, with the logo as icon."),
    ("tools/packages/make-package.sh", "Makes a " + c(".deb") + ", " + c(".rpm") + " or Arch package from the "
     "programs built for " + c("/usr") + ", in a container of the family."),
    ("tools/packages/debian/control", "The " + c(".deb") + " description: dependencies, recommended zenity."),
    ("tools/packages/debian/preinst", "Before unpacking the " + c(".deb") + ": sets aside the "
     + c("rootspeak.conf") + " of an installation from the archive, so dpkg asks nothing."),
    ("tools/packages/debian/postinst", "After installing or upgrading the " + c(".deb") + ": puts those settings back, "
     "then " + c("rootspeak-setup configure") + "."),
    ("tools/packages/debian/prerm", "Before removing the " + c(".deb") + ": " + c("rootspeak-setup unconfigure") + "."),
    ("tools/packages/debian/postrm", c("apt purge") + ": also messages and configuration."),
    ("tools/packages/rpm/rootspeak.spec", "The " + c(".rpm") + ", one for the Fedora, RHEL and SUSE families."),
    ("tools/packages/arch/PKGBUILD", "The Arch package."),
    ("tools/packages/arch/rootspeak.install", "What pacman runs after installing and before removing."),
    ("tests/container/package.sh", "Installs, reinstalls and removes the package of the test machine with its "
     "package manager, without network."),
    ("etc/profile.d/rootspeak.sh", "The hook for the shells that read " + c("/etc/profile") + ", in plain sh: it hands "
     "bash over to " + c("rootspeak.bash") + " and asks the others (except zsh) at login."),
    ("etc/rootspeak.bash", "The bash hook: the question at login and at every prompt."),
    ("etc/rootspeak.zsh", "The zsh hook, sourced by the system zshrc."),
    ("etc/rootspeak.fish", "The fish hook, installed in " + c("/etc/fish/conf.d") + "."),
    ("etc/xdg/autostart/rootspeak-agent.desktop", "Autostart of the desktop agent."),
    ("etc/rootspeak/rootspeak.conf", "The default configuration."),
    ("tests/engine.sh", "Engine tests in test mode: confirmations, delivery, states, expiry, configuration, "
     "purge, agent, second review, reminder."),
    ("tests/unit-tests.c", "Tests of the internal parts: cleaning, messages, configuration, events."),
    ("tests/tui.py", "Test of the TUI on a virtual terminal: list, detail, sending, editor, reminder, revocation, "
     "search, sizes."),
    ("tests/help-tui.py", "Test of the built-in help on a virtual terminal."),
    ("tests/fuzz/fuzz.c", "Fuzzing with libFuzzer of what reads untrusted data (four targets)."),
    ("tests/fuzz/run.sh", "Builds and runs the fuzzing in a container with clang."),
    ("tests/container/Containerfile", "The test machine: Debian 13, or any distribution with systemd, with sshd, "
     "several users and shells."),
    ("tests/container/setup.sh", "Prepares the test machine on any distribution (apt, dnf, zypper, pacman): "
     "packages, sshd, shells, Italian locale, test users."),
    ("tests/container/run.sh", "Starts the test machine, builds and installs RootSpeak there, runs the scenarios, "
     "saves the results."),
    ("tests/distros/run.sh", "Compatibility tests on the test server: the scenarios on every distribution of "
     "the list, several at a time, with a summary."),
    ("tests/distros/list", "The distributions of the compatibility tests and their container images."),
    ("tests/container/scenarios.py", "The real-world scenarios, run as root in the test machine (also in the "
     "VM, together with the desktop ones)."),
    ("tests/vm/run.sh", "Tests in a VM with a desktop on the test server: code, clean VM, scenarios, "
     "screenshots, results; one desktop profile per run."),
    ("tests/vm/prepare.sh", "Builds once the base disk of a desktop profile, from the cloud image of its "
     "distribution."),
    ("tests/vm/users.sh", "Run in the VM while its base disk is prepared: users, ssh keys, Italian locale."),
    ("tests/vm/desktops/debian-gnome.yaml", "Desktop profile (cloud-init): Debian 13 with GNOME on Wayland."),
    ("tests/vm/desktops/ubuntu-gnome.yaml", "Desktop profile: Ubuntu 24.04 with GNOME on Wayland."),
    ("tests/vm/desktops/ubuntu-cinnamon.yaml", "Desktop profile: Cinnamon on X11 with LightDM on Ubuntu 24.04, "
     "the base of Linux Mint 22."),
    ("tests/vm/desktops/fedora-kde.yaml", "Desktop profile: Fedora 44 with KDE Plasma on Wayland."),
    ("tests/vm/desktops/rocky-gnome.yaml", "Desktop profile: Rocky Linux 9 with GNOME, SELinux enforcing."),
    ("tests/vm/start.sh", "Starts a VM from a clean copy of its base disk."),
    ("tests/vm/stop.sh", "Shuts down the VM and deletes the working disk."),
    ("tests/vm/capture.py", "Captures the VM screen from the QEMU monitor."),
    ("tests/vm/desktop.py", "Reads and presses the buttons of the RootSpeak dialogs through the desktop's "
     "accessibility (AT-SPI)."),
    ("tools/check-docs.py", "Consistency checks between code, help, manuals and tests."),
    ("tools/fingerprint.sh", "Code fingerprint (SHA-256 of src, Makefile, etc, install.sh, tools/packages) and commit, recorded "
     "with the test results."),
    ("tools/tui-screenshots.sh", "Real TUI screenshots for the manuals, captured in the test machine."),
    ("tools/setup-dev.sh", "Says what a freshly cloned copy is missing (packages, git identity); "
     + c("--install") + " installs the packages."),
    ("tools/backup.sh", "The whole repository, with its history, in a single git bundle."),
    ("tools/release.sh", "The downloads: the archive (the programs built on RHEL 9 on the test server, "
     + c("install.sh") + ", " + c("etc/") + ", the manuals and the licence) and the three packages, in "
     + c("build/release/") + "."),
    ("site/publish.sh", "Builds the website in " + c("site/public/") + " and copies it to the VPS."),
    ("site/seo-head.py", "Adds description, canonical address and link preview to a page of the website."),
    ("site/licence-page.py", "Turns " + c("LICENSE.md") + " into " + c("licence.html") + "."),
    ("docs/sources/build.py", "Generator of the two manuals and functions for figures and tables."),
    ("docs/sources/style.css", "The common style of the manuals of the seven projects, embedded unchanged in every "
     "manual; the rules that only RootSpeak needs are in " + c("build.py") + "."),
    ("docs/sources/manual.js", "The common script of the manuals: search in the sidebar, index, " + ui("Copy")
     + " button on the command boxes."),
], "«TAB» — File map") + \
    p("The chapters of the manuals are in " + c("docs/sources/user/") + " and " + c("docs/sources/technical/")
      + ", one file per chapter; " + c("docs/decisions-and-history.md") + " and " + c("CLAUDE.md") + " collect the "
      "decisions and the working agreements, " + c("docs/adversarial-review.md") + " the two external reviews. The "
      "bash prototype (version 0.1.0) is in the repository history.")

MAKE = fig(
    box(20, 40, 170, 56, "make", "rspeak, rootspeak-user", "navy")
    + box(20, 116, 170, 56, "make unit", "build/unit-tests", "blue")
    + box(250, 40, 190, 56, "build/", "PIE, RELRO, warnings = errors", "dark")
    + box(250, 116, 190, 56, "make sanitizer", "build-san/ · ASan, UBSan", "amber")
    + box(250, 192, 190, 56, "make analyze", "build-analyze/ · -fanalyzer", "amber")
    + box(500, 40, 180, 56, "install.sh", "installs from build/", "navy")
    + box(500, 116, 180, 56, "tests/engine.sh", "RSPEAK_BUILD=build-san", "green")
    + box(740, 40, 140, 56, "system", "/usr/local, /usr", "light")
    + box(740, 116, 140, 56, "results", "engine.json", "light")
    + arrow(192, 68, 248, 68) + arrow(442, 68, 498, 68) + arrow(682, 68, 738, 68)
    + arrow(442, 144, 498, 144, "#d97706") + arrow(682, 144, 738, 144, "#16a34a"),
    900, 268, "«FIG» — The Makefile targets and where they lead", "Building")

S2 = p("The build is a Makefile with no external tools besides gcc and pkg-config (for libsystemd). "
       "Everything ends up in " + c("build/") + " (or in a folder chosen with " + c("B=") + "); the installation "
       "folders of the helper and of the manuals are compiled into the programs with " + c("-DLIBDIR") + " and "
       + c("-DDOCDIR") + ", from " + c("PREFIX") + " (" + c("/usr/local") + " by default, " + c("/usr") + " for the "
       "packages).",
       lead=True) + MAKE + table(["Target", "What it does"], [
    [c("make"), "builds " + c("build/rspeak") + " and " + c("build/rootspeak-user")],
    [c("make unit"), "builds and runs " + c("build/unit-tests") + " in test mode"],
    [c("make analyze"), "rebuilds everything in " + c("build-analyze/") + " with " + c("-fanalyzer")],
    [c("make sanitizer"), "rebuilds in " + c("build-san/") + " with AddressSanitizer and UBSan, plus "
     + c("unit-tests") + "; the engine is then run on them by hand with "
     + c("RSPEAK_BUILD=build-san tests/engine.sh")],
    [c("make docs"), "regenerates the two manuals (" + c("python3 docs/sources/build.py") + ")"],
    [c("make docs-check"), "runs " + c("tools/check-docs.py") + " (" + cap(20, 5) + ")"],
    [c("make test"), c("make") + ", " + c("make unit") + ", " + c("make docs-check") + ", then "
     + c("tests/engine.sh")],
    [c("make clean"), "removes " + c("build") + ", " + c("build-analyze") + " and " + c("build-san")],
], "«TAB» — The Makefile targets") + code("""WARNINGS   = -Wall -Wextra -Wpedantic -Wformat=2 -Wformat-security -Wshadow -Wpointer-arith \\
           -Wcast-qual -Wwrite-strings -Wstrict-prototypes -Wmissing-prototypes -Wvla \\
           -Wnull-dereference -Wimplicit-fallthrough -Wundef -Werror
HARDENING   = -D_FORTIFY_SOURCE=3 -fstack-protector-strong -fstack-clash-protection -fcf-protection -fPIE
LDFLAGS += -pie -Wl,-z,relro,-z,now -Wl,-z,noexecstack""", "text", "Makefile (excerpt)") + \
    p("Warnings are errors (" + c("-Werror") + "): the code does not build if gcc finds anything to object to. The "
      "meaning of each hardening flag is in " + cap(16, 3) + ".")

S3 = flow([("Build", "make, if needed", "dark"), ("Files", "copy_files · DESTDIR", "blue"),
           ("rootspeak-setup", "configure", "navy"), ("Group, hooks", "store folders", "blue"),
           ("Agents", "closed and restarted", "navy")], "«FIG» — The stages of install.sh") + steps([
    "It relaunches itself with " + c("sudo") + " if it is not root (with " + c("DESTDIR") + " it does not need to). "
    "It stops if RootSpeak is installed from a package (" + c("/usr/lib/rootspeak/rootspeak-user") + " exists): "
    "“RootSpeak is installed from a package: update or remove it with the package manager (apt, dnf, zypper, "
    "pacman).”. It warns if " + c("zenity") + ", " + c("loginctl") + " or " + c("systemd-run") + " are missing.",
    "If the programs are missing from " + c("build/") + ", or were built for other folders (the "
    + c("LIBDIR") + " path does not appear inside " + c("build/rspeak") + "), it builds them with " + c("make PREFIX=…")
    + " (gcc, make, pkg-config and libsystemd-dev are needed). From the downloadable archive, which has no "
    + c("Makefile") + ", it never builds: the programs are already in " + c("build/") + ", built for "
    + c("/usr/local") + "; with another " + c("PREFIX") + " it stops with “The programs of this archive install only "
    "in /usr/local (PREFIX=…)”.",
    "It copies the files (" + c("copy_files") + ", into " + c("$DESTDIR") + " if set): "
    + c("$PREFIX/lib/rootspeak/rootspeak-user") + " (" + c("755") + "), " + c("$PREFIX/bin/rspeak") + " (" + c("750")
    + ", the group comes later), " + c("rootspeak-setup") + ", the manuals and the licence in "
    + c("$PREFIX/share/doc/rootspeak/") + ", the logo in " + c("$PREFIX/share/icons/hicolor/") + ", the AppStream "
    "description, the configuration (only if missing), the shell hooks and the autostart entry, replacing "
    + c("@LIBDIR@") + ", " + c("@BINDIR@") + " and " + c("@VARDIR@") + ". " + c("PREFIX") + " is " + c("/usr/local")
    + ". With " + c("DESTDIR") + " it stops here: the packages run the rest when they are installed.",
    "It runs " + c("rootspeak-setup configure") + ": " + c("rspeak") + " goes to " + c("root:group") + ", the first "
    "administrators' group that exists among " + c("sudo") + ", " + c("wheel") + ", " + c("admin") + " (otherwise "
    + c("root") + "); " + c("/var/lib/rootspeak") + " and " + c("users/") + " (" + c("755") + ") and " + c("sent/")
    + " (" + c("700") + ") are created; the lines marked " + c("# RootSpeak hook") + " are removed and written again, "
    "in " + c("/etc/bash.bashrc") + " (on Debian, interactive non-login shells do not read " + c("/etc/profile.d")
    + ") and, if zsh is installed, in the system zshrc; the desktop agents of the previous version are closed: "
    "they restart, updated, at the first send or at login.",
]) + table(["Option", "Effect"], [
    ["none", "installs or upgrades"],
    [c("DESTDIR=folder"), "only copies the files into the folder, as " + c("root:root") + "; used by "
     + c("tools/packages/make-package.sh")],
    [c("--uninstall"), "removes programs, manuals, hooks and the marked lines of " + c("bash.bashrc")
     + " and of the zshrc, stops the agents; keeps messages and configuration"],
    [c("--purge"), "like " + c("--uninstall") + ", and also removes " + c("/var/lib/rootspeak") + " and " + c("/etc/rootspeak")],
], "«TAB» — The modes of install.sh")

S4 = p("The packages install in " + c("/usr") + ", the archive in " + c("/usr/local") + "; " + c("PREFIX")
       + " below is one or the other. Everything in " + c("/etc") + " and " + c("/var") + " is the same.", lead=True) + \
    table(["Path", "Owner", "Permissions", "Contents"], [
    [c("PREFIX/bin/rspeak"), "root:sudo (or wheel, admin)", c("750"), "the administrators' command"],
    [c("PREFIX/lib/rootspeak/rootspeak-user"), "root", c("755"), "the helper, outside the PATH"],
    [c("PREFIX/lib/rootspeak/rootspeak-setup"), "root", c("755"), "group, hooks, folders, agents (" + cap(3, 3) + ")"],
    [c("PREFIX/lib/rootspeak/rootspeak.bash") + ", " + c("rootspeak.zsh"), "root", c("644"), "the bash and zsh hooks"],
    [c("PREFIX/share/doc/rootspeak/"), "root", c("644"), "the two HTML manuals and the licence"],
    [c("PREFIX/share/icons/hicolor/*/apps/rootspeak.*"), "root", c("644"), "the logo as icon: SVG and 48, 128, 256 px"],
    [c("PREFIX/share/metainfo/it.nicfio.rootspeak.metainfo.xml"), "root", c("644"), "the description for software centres"],
    [c("/etc/rootspeak/rootspeak.conf"), "root", c("644"), "the configuration (never overwritten)"],
    [c("/etc/profile.d/rootspeak.sh"), "root", c("644"), "the hook for the shells that read " + c("/etc/profile")],
    [c("/etc/fish/conf.d/rootspeak.fish"), "root", c("644"), "the fish hook"],
    [c("/etc/xdg/autostart/rootspeak-agent.desktop"), "root", c("644"), "the agent's autostart entry"],
    [c("/etc/bash.bashrc") + ", zshrc", "—", "—", "a line marked " + c("# RootSpeak hook")],
    [c("/var/lib/rootspeak/"), "root", c("755") + " (" + c("sent/") + " " + c("700") + ")", "the message store (" + cap(5) + ")"],
], "«TAB» — What gets installed, and where") + \
    note("users have no command: " + c("rootspeak-user") + " is not in the PATH and, when run by hand without "
         + c("prompt") + " or " + c("agent") + ", replies that it is an internal helper and exits with 1.")

S5 = steps([
    c("make") + " (all warnings are errors) and " + c("make unit") + ".",
    c("python3 docs/sources/build.py") + ", then " + c("tools/check-docs.py") + ": generated manuals up to date, "
    "reference aligned with the help, file map complete, internal links valid, tests "
    "run on the current code (" + cap(20, 5) + ").",
    c("tests/engine.sh") + " always; " + c("tests/help-tui.py") + " if the help has changed; " + c("tests/tui.py")
    + " and " + c("tools/tui-screenshots.sh") + " if the TUI has changed; " + c("make sanitizer") + " with "
    + c("RSPEAK_BUILD=build-san tests/engine.sh") + ", " + c("make analyze") + " and " + c("tests/fuzz/run.sh")
    + " if the code that reads data has changed; " + c("tests/container/run.sh") + " if sending, "
    "delivery, confirmations or permissions have changed; " + c("tests/vm/run.sh") + " if the desktop has changed; "
    + c("tools/release.sh") + " and " + c("RSPEAK_RELEASE=build/release tests/distros/run.sh") + " if the build, "
    + c("install.sh") + ", " + c("rootspeak-setup") + " or the packages have changed.",
    "A test of the affected flow in test mode (" + cap(4, 4) + "); for the desktop, sudo and other users, a "
    "live test after " + c("./install.sh") + ", done by whoever has the root password.",
]) + warn("test results are committed together with the change: each suite writes its result with the "
          "commit and the code fingerprint, and " + cap(20) + " shows them next to the current fingerprint.")

RELEASE = flow([("tools/release.sh", "on the test server", "dark"), ("rhel-9 image", "make, strip · glibc 2.34", "navy"),
                ("build/release/", "archive, .deb, .rpm, Arch", "blue"), ("tests/distros", "packages on 22 systems", "amber"),
                ("site/publish.sh", "rootspeak.nicfio.it", "green")],
               "«FIG» — From the code to the download on the website", "Release")

S6 = p("RootSpeak is distributed as built programs: a package for each family of distributions and an archive, "
       + c("rootspeak-VERSION-linux-x86_64.tar.gz") + ", for the others. They all carry the same programs, built "
       "once. Next to them, " + c("rootspeak-VERSION-source.tar.gz") + " carries the source code (PolyForm "
       "Noncommercial License 1.0.0, 0.2.1 included).", lead=True) + \
    RELEASE + steps([
    c("tools/release.sh") + " copies the files under version control to the test server and builds them in the "
    "image of RHEL 9 of the compatibility tests: RHEL 9 and its rebuilds have the oldest C library among the "
    "supported distributions (glibc 2.34; Ubuntu 22.04 has 2.35, SLES 15 2.38), and a program built against an "
    "older glibc runs on the newer ones. The programs are stripped of their symbols.",
    "It checks that no symbol needs a glibc newer than 2.34 and that the programs were built for "
    + c("/usr/local") + ", then makes the archive with " + c("install.sh") + ", " + c("etc/") + ", " + c("build/rspeak")
    + ", " + c("build/rootspeak-user") + ", the two manuals, " + c("LICENSE.md") + ", " + c("NOTICE.md") + " and a "
    + c("README.txt") + ".",
    "It builds the programs a second time with " + c("PREFIX=/usr") + ", in the same image, and makes the three "
    "packages with them (next section).",
    "It makes the source archive with a fixed list of files: " + c("Makefile") + ", " + c("src/") + ", " + c("etc/")
    + ", " + c("install.sh") + ", the icons, the two manuals, " + c("tests/unit-tests.c") + ", " + c("tests/engine.sh")
    + ", " + c("tools/fingerprint.sh") + ", " + c("tools/packages/") + ", " + c("LICENSE.md") + ", " + c("NOTICE.md") + " and a " + c("README.txt")
    + ". The working notes, the website and the test infrastructure stay out, and the script fails if "
    + c("CLAUDE.md") + " or " + c("site/") + " end up in it. " + c("SHA256SUMS") + " covers the two archives and "
    "the packages.",
    c("RSPEAK_RELEASE=build/release tests/distros/run.sh") + " runs all the scenarios on the 22 distributions "
    "with the package of each one installed by its package manager, plus the package scenarios (P); "
    + c("RSPEAK_ARCHIVE=build/release/….tar.gz") + " does the same with the archive. No build on the test "
    "machines; the summary records how RootSpeak was installed.",
    c("site/publish.sh") + " builds the website in " + c("site/public/") + " (landing page, manuals, "
    + c("licence.html") + ", " + c("download/") + ", " + c("og.jpg") + ", " + c("robots.txt") + ", "
    + c("sitemap.xml") + "; " + c("download/") + " with the two archives, the packages and " + c("SHA256SUMS")
    + ") and copies it to " + c("/srv/www/rootspeak.nicfio.it") + " on the VPS; "
    + c("--build") + " only builds.",
]) + note("the libsystemd the programs link to (" + c("libsystemd.so.0") + ") keeps its interface across "
          "versions: the one of RHEL 9 is enough everywhere.", "libsystemd.")

PKGFLOW = fig(
    box(20, 40, 200, 56, "build/ (PREFIX=/usr)", "rspeak, rootspeak-user", "navy")
    + box(280, 40, 200, 56, "install.sh", "DESTDIR=stage", "dark")
    + box(540, 10, 170, 50, "debian-12", "dpkg-deb → .deb", "blue")
    + box(540, 72, 170, 50, "rhel-9", "rpmbuild → .rpm", "blue")
    + box(540, 134, 170, 50, "arch", "makepkg → .pkg.tar.zst", "blue")
    + box(760, 72, 120, 50, "installed", "rootspeak-setup", "green")
    + arrow(222, 68, 278, 68) + arrow(482, 60, 538, 35) + arrow(482, 70, 538, 97) + arrow(482, 80, 538, 159)
    + arrow(712, 35, 758, 90) + arrow(712, 97, 758, 97) + arrow(712, 159, 758, 104),
    900, 200, "«FIG» — One set of files, three packages", "Packages")

S7 = p("The three packages contain the same files, copied by " + c("install.sh") + " with " + c("DESTDIR")
       + " and " + c("PREFIX=/usr") + "; each is made by the tool of its family, in the image of the compatibility "
       "tests, by " + c("tools/packages/make-package.sh") + ". Nothing is compiled while packaging.", lead=True) + \
    PKGFLOW + table(["Package", "Made on, with", "For", "Dependencies"], [
        [c("rootspeak_VERSION-1_amd64.deb"), "Debian 12, " + c("dpkg-deb") + " (xz)", "Debian 12–13, Ubuntu 22.04–26.04",
         c("libc6 (>= 2.34), libsystemd0, systemd, sudo, procps") + "; recommends " + c("zenity") + ", suggests "
         + c("libnotify-bin")],
        [c("rootspeak-VERSION-1.x86_64.rpm"), "RHEL 9, " + c("rpmbuild") + " (xz payload, which SLES 15's rpm 4.14 reads)",
         "Fedora, CentOS Stream, RHEL, Rocky, Alma, Oracle, openSUSE, SLES",
         c("systemd, sudo, /usr/bin/pkill") + ", the libraries found by rpm; recommends " + c("zenity")],
        [c("rootspeak-VERSION-1-x86_64.pkg.tar.zst"), "Arch, " + c("makepkg") + " as " + c("nobody"), "Arch Linux",
         c("glibc systemd systemd-libs sudo procps-ng") + "; optional " + c("zenity") + ", " + c("libnotify")],
    ], "«TAB» — The packages") + \
    table(["Moment", ".deb", ".rpm", "Arch"], [
        ["after installing or upgrading", c("postinst configure"), c("%post"), c("post_install") + ", " + c("post_upgrade")],
        ["before removing (not on upgrades)", c("prerm remove"), c("%preun") + " with " + c("$1 = 0"), c("pre_remove")],
        ["purge", c("postrm purge") + ": " + c("/var/lib/rootspeak") + ", " + c("/etc/rootspeak"), "—", "—"],
    ], "«TAB» — When the packages run rootspeak-setup") + \
    ul([
        "After installing, every package runs " + c("rootspeak-setup configure") + ", the same code as "
        + c("install.sh") + " (" + cap(3, 3) + "); before removing, " + c("rootspeak-setup unconfigure")
        + " takes the hook lines away and closes the agents. The hook lines are in files of other packages ("
        + c("bash.bashrc") + ", zshrc): this is why they are written by a script and not shipped as files.",
        "The package contains " + c("rspeak") + " as " + c("root:root 750") + ": the administrators' group differs "
        "between families and is set by " + c("configure") + ". " + c("rpm -V") + " and " + c("pacman -Qkk")
        + " therefore report the group of " + c("rspeak") + " as changed; nothing else.",
        "Only " + c("/etc/rootspeak/rootspeak.conf") + " is a configuration file of the package (a conffile, "
        + c("%config(noreplace)") + ", " + c("backup") + "): an upgrade keeps it. The hooks in " + c("/etc")
        + " are program parts, replaced on upgrades and removed with the package.",
        c("/var/lib/rootspeak") + " belongs to no package: it holds the messages, and survives removal.",
        "Over an installation from the archive, " + c("configure") + " removes " + c("/usr/local/bin/rspeak") + ", "
        + c("/usr/local/lib/rootspeak") + " and " + c("/usr/local/share/doc/rootspeak") + " and says so; the store "
        "is the same. dpkg and rpm replace the archive's files in " + c("/etc") + "; pacman refuses files it does "
        "not know, so on Arch " + c("./install.sh --uninstall") + " comes first. The archive's "
        + c("rootspeak.conf") + " is kept: dpkg would ask what to do with a configuration file it does not know "
        "(and, without a terminal, stop the installation), so the " + c("preinst") + " of the " + c(".deb")
        + " sets it aside and " + c("postinst") + " puts it back; rpm and pacman keep it by themselves, writing "
        "theirs as " + c(".rpmnew") + " or " + c(".pacnew") + ".",
        "The packages are not signed: the integrity check is " + c("SHA256SUMS") + " over HTTPS.",
    ])

CHAPTER = ("Repository, build and installation", [
    ("File map", S1),
    ("Building: the Makefile", S2),
    ("install.sh step by step", S3),
    ("What it installs, and where", S4),
    ("Before committing a change", S5),
    ("The downloads and the website", S6),
    ("The packages", S7),
])
