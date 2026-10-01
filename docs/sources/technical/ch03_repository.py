from build import arrow, box, c, code, file_map, fig, flow, note, p, steps, table, text, tree, ui, warn


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">chapter {n}{"." + str(s) if s else ""}</a>'


ALBERO = tree([
    "AMS/",
    "├── src/                  # the C code: two programs, common parts",
    "├── po/                   # texts to translate (ams.pot) and translations (it.po)",
    "├── etc/                  # shell hooks, autostart, configuration",
    "├── install.sh            # installation, upgrade, removal",
    "├── Makefile              # build, tests, analysis, sanitizer, texts",
    "├── docs/                 # the two generated manuals, decisions, reviews",
    "│   └── sources/          # generator, style, one file per chapter",
    "├── tests/                # engine, TUI, help, units, fuzzing, container, VM",
    "│   └── */results/        # results recorded with commit and fingerprint",
    "└── tools/                # manual consistency, fingerprint, screenshots",
], "«FIG» — The folders of the repository")

S1 = p("The repository contains the C code, the language catalogs, the files to install on the system, the manuals "
       "with their sources, the tests and the consistency checks. The following table is the <b>file map</b>: "
       "the lines are counted every time the manual is generated, and " + c("tools/check-docs.py") + " fails if a "
       "code file is missing or if one that does not exist is listed.", lead=True) + ALBERO + file_map([
    ("src/ams.c", "The administrators' command: relaunch through sudo, recipients, " + c("send") + ", " + c("list")
     + ", " + c("status") + ", " + c("revoke") + ", " + c("remind") + ", " + c("log") + ", " + c("purge")
     + ", message summaries, recovery."),
    ("src/ams.h", "The parts of ams also used by the TUI: recipient states, summary, commands."),
    ("src/tui.c", "The TUI for administrators: list, detail and history, writing and sending, actions with confirmation."),
    ("src/guida.c", "The built-in help: tabbed guide, manual-style page, plain text."),
    ("src/guida.h", "Interface of guida.c."),
    ("src/archivio.c", "The operations on the mailboxes, always with the user's identity; writing to terminals; "
     "terminal language; waking up the agent."),
    ("src/archivio.h", "Interface of archivio.c."),
    ("src/ams-user.c", "The helper that runs as the user: " + c("prompt") + " (shell hook), " + c("agent")
     + " (desktop), recording of confirmations."),
    ("src/utente.c", c("come_utente") + ": a child process with a user's identity and a time limit."),
    ("src/utente.h", "Interface of utente.c."),
    ("src/sessioni.c", "Human users, groups, sessions and terminals, from passwd, group and logind."),
    ("src/sessioni.h", "Interface of sessioni.c."),
    ("src/testo.c", "Text cleaning, message format, configuration."),
    ("src/testo.h", "Interface of testo.c: " + c("msg_t") + ", " + c("conf_t") + "."),
    ("src/lingua.c", "Language selection and reader of the .mo catalogs."),
    ("src/lingua.h", "Interface of lingua.c: " + c("T") + ", " + c("TC") + ", " + c("tl") + ", " + c("tlc") + "."),
    ("src/evento.c", "Structured events in the journal and their text in each language."),
    ("src/evento.h", "Interface of evento.c."),
    ("src/comune.c", "Utilities: environment, errors, memory, growable strings, safe reading and writing of files."),
    ("src/comune.h", "Interface of comune.c, version (" + c("AMS_VERSION") + ") and limits."),
    ("po/ams.pot", "The texts to translate, extracted from the sources (" + c("make pot") + "); also the source of the user manual's reference."),
    ("po/it.po", "The Italian translation."),
    ("Makefile", "Build, internal tests, static analysis, sanitizer, text extraction."),
    ("install.sh", "Installation, upgrade, removal."),
    ("etc/profile.d/ams.sh", "The hook for the shells that read " + c("/etc/profile") + ", in plain sh: it hands "
     "bash over to " + c("ams.bash") + " and asks the others (except zsh) at login."),
    ("etc/ams.bash", "The bash hook: the question at login and at every prompt."),
    ("etc/ams.zsh", "The zsh hook, sourced by the system zshrc."),
    ("etc/ams.fish", "The fish hook, installed in " + c("/etc/fish/conf.d") + "."),
    ("etc/xdg/autostart/ams-agent.desktop", "Autostart of the desktop agent."),
    ("etc/ams/ams.conf", "The default configuration."),
    ("tests/engine.sh", "Engine tests in test mode: confirmations, delivery, states, expiry, configuration, "
     "purge, agent, languages, second review, reminder."),
    ("tests/unit-tests.c", "Tests of the internal parts: cleaning, languages, messages, configuration, events."),
    ("tests/tui.py", "Test of the TUI on a virtual terminal: list, detail, sending, editor, reminder, revocation, "
     "search, sizes."),
    ("tests/help-tui.py", "Test of the built-in help on a virtual terminal."),
    ("tests/fuzz/fuzz.c", "Fuzzing with libFuzzer of what reads untrusted data (six targets)."),
    ("tests/fuzz/run.sh", "Builds and runs the fuzzing in a container with clang."),
    ("tests/container/Containerfile", "The test machine: Debian 13 with systemd, sshd, several users and shells."),
    ("tests/container/run.sh", "Starts the test machine, installs AMS, runs the scenarios, saves the results."),
    ("tests/container/scenarios.py", "The real-world scenarios, run as root in the test machine (also in the "
     "VM, together with the desktop ones)."),
    ("tests/vm/run.sh", "Tests in the desktop VM on the test server: code, clean VM, scenarios, "
     "screenshots, results."),
    ("tests/vm/prepare.sh", "Builds the VM base disk once (Debian 13, GNOME, users)."),
    ("tests/vm/user-data.tpl", "The VM's cloud-init configuration: packages, users, automatic login, "
     "accessibility."),
    ("tests/vm/start.sh", "Starts the VM from a clean copy of the base disk."),
    ("tests/vm/stop.sh", "Shuts down the VM and deletes the working disk."),
    ("tests/vm/capture.py", "Captures the VM screen from the QEMU monitor."),
    ("tests/vm/desktop.py", "Reads and presses the buttons of the AMS dialogs through GNOME accessibility."),
    ("tools/check-docs.py", "Consistency checks between code, help, translations, manuals and tests."),
    ("tools/fingerprint.sh", "Code fingerprint (SHA-256 of src, po, Makefile, etc, install.sh) and commit, recorded "
     "with the test results."),
    ("tools/tui-screenshots.sh", "Real TUI screenshots for the manuals, captured in the test machine."),
    ("tools/setup-dev.sh", "Says what a freshly cloned copy is missing (packages, git identity); "
     + c("--install") + " installs the packages."),
    ("tools/backup.sh", "The whole repository, with its history, in a single git bundle."),
    ("docs/sources/build.py", "Generator of the two manuals and functions for figures and tables."),
    ("docs/sources/style.css", "The common style of the manuals of the seven projects, embedded unchanged in every "
     "manual; the rules that only AMS needs are in " + c("build.py") + "."),
    ("docs/sources/manual.js", "The common script of the manuals: search in the sidebar, index, " + ui("Copy")
     + " button on the command boxes."),
], "«TAB» — File map") + \
    p("The chapters of the manuals are in " + c("docs/sources/user/") + " and " + c("docs/sources/technical/")
      + ", one file per chapter; " + c("docs/decisions-and-history.md") + " and " + c("CLAUDE.md") + " collect the "
      "decisions and the working agreements, " + c("docs/adversarial-review.md") + " the two external reviews. The "
      "bash prototype (version 0.1.0) is in the repository history.")

MAKE = fig(
    box(20, 40, 170, 56, "make", "ams, ams-user, .mo", "navy")
    + box(20, 116, 170, 56, "make prove", "build/unit-tests", "blue")
    + box(20, 192, 170, 56, "make pot", "xgettext, msgmerge", "soft")
    + box(250, 40, 190, 56, "build/", "PIE, RELRO, warnings = errors", "dark")
    + box(250, 116, 190, 56, "make sanitizer", "build-san/ · ASan, UBSan", "amber")
    + box(250, 192, 190, 56, "make analizza", "build-analisi/ · -fanalyzer", "amber")
    + box(500, 40, 180, 56, "install.sh", "installs from build/", "navy")
    + box(500, 116, 180, 56, "tests/engine.sh", "AMS_BUILD=build-san", "green")
    + box(740, 40, 140, 56, "system", "/usr/local", "light")
    + box(740, 116, 140, 56, "results", "engine.json", "light")
    + arrow(192, 68, 248, 68) + arrow(442, 68, 498, 68) + arrow(682, 68, 738, 68)
    + arrow(442, 144, 498, 144, "#d97706") + arrow(682, 144, 738, 144, "#16a34a"),
    900, 268, "«FIG» — The Makefile targets and where they lead", "Building")

S2 = p("The build is a Makefile with no external tools besides gcc, pkg-config (for libsystemd) and gettext. "
       "Everything ends up in " + c("build/") + " (or in a folder chosen with " + c("B=") + "); the installation "
       "folders are compiled into the program with " + c("-DLIBDIR") + " and " + c("-DLOCALEDIR") + ".",
       lead=True) + MAKE + table(["Target", "What it does"], [
    [c("make"), "builds " + c("build/ams") + ", " + c("build/ams-user") + " and one " + c("ams.mo") + " for each "
     + c("po/*.po") + " (with " + c("msgfmt --check") + ")"],
    [c("make prove"), "builds and runs " + c("build/unit-tests") + " in test mode"],
    [c("make analizza"), "rebuilds everything in " + c("build-analisi/") + " with " + c("-fanalyzer")],
    [c("make sanitizer"), "rebuilds in " + c("build-san/") + " with AddressSanitizer and UBSan, plus "
     + c("unit-tests") + "; then " + c("AMS_BUILD=build-san tests/engine.sh")],
    [c("make pot"), "extracts the texts into " + c("po/ams.pot") + " and updates the " + c(".po") + " files with " + c("msgmerge")],
    [c("make clean"), "removes " + c("build") + ", " + c("build-analisi") + " and " + c("build-san")],
], "«TAB» — The Makefile targets") + code("""AVVISI = -Wall -Wextra -Wpedantic -Wformat=2 -Wformat-security -Wshadow -Wpointer-arith \\
         -Wcast-qual -Wwrite-strings -Wstrict-prototypes -Wmissing-prototypes -Wvla \\
         -Wnull-dereference -Wimplicit-fallthrough -Wundef -Werror
DIFESE = -D_FORTIFY_SOURCE=3 -fstack-protector-strong -fstack-clash-protection -fcf-protection -fPIE
LDFLAGS += -pie -Wl,-z,relro,-z,now -Wl,-z,noexecstack""", "text", "Makefile (excerpt)") + \
    p("Warnings are errors (" + c("-Werror") + "): the code does not build if gcc finds anything to object to. The "
      "meaning of each hardening flag is in " + cap(17, 3) + ".")

S3 = flow([("Build", "make, if needed", "dark"), ("Programs", "ams 750 · ams-user", "blue"),
           ("Languages, hooks", "locale/, etc/", "blue"), ("/var/lib/ams", "users 755 · sent 700", "blue"),
           ("Agents", "closed and restarted", "navy")], "«FIG» — The stages of install.sh") + steps([
    "It relaunches itself with " + c("sudo") + " if it is not root, and picks the administrators' group: the first "
    "one that exists among " + c("sudo") + ", " + c("wheel") + ", " + c("admin") + " (otherwise " + c("root") + "). It warns if "
    + c("zenity") + ", " + c("loginctl") + " or " + c("systemd-run") + " are missing.",
    "If the programs are missing from " + c("build/") + ", or were built for other folders (the "
    + c("LIBDIR") + " path does not appear inside " + c("build/ams") + "), it builds them with " + c("make PREFIX=…")
    + " (gcc, make, pkg-config, libsystemd-dev and gettext are needed).",
    "It installs " + c("$PREFIX/lib/ams/ams-user") + " (" + c("755") + "), the catalogs in "
    + c("$PREFIX/share/locale/LINGUA/LC_MESSAGES/ams.mo") + " (LINGUA: “LANGUAGE”) and " + c("$PREFIX/bin/ams")
    + " with owner " + c("root:gruppo") + " (gruppo: “group”, the administrators' group) and permissions " + c("750") + "; it removes the files of the bash prototype and an old "
    + c("sbin/ams") + ". " + c("PREFIX") + " is " + c("/usr/local") + ".",
    "It installs the manuals in " + c("$PREFIX/share/doc/ams/") + ", the configuration (only if missing), the shell "
    "hooks and the autostart entry, replacing " + c("@LIBDIR@") + " and " + c("@VARDIR@") + ".",
    "It adds to " + c("/etc/bash.bashrc") + " the line marked " + c("# AMS hook") + " (on Debian, interactive "
    "non-login shells do not read " + c("/etc/profile.d") + "); if the system zshrc exists, it adds the line that sources "
    + c("ams.zsh") + "; for fish it writes " + c("/etc/fish/conf.d/ams.fish") + ".",
    "It creates " + c("/var/lib/ams") + " and " + c("users/") + " (" + c("755") + ") and " + c("sent/") + " (" + c("700") + ").",
    "It closes the agents of the previous version (the bash ones too): they restart, updated, at the first send or "
    "at login.",
]) + table(["Option", "Effect"], [
    ["none", "installs or upgrades"],
    [c("--uninstall"), "removes programs, catalogs, manuals, hooks and the marked lines of " + c("bash.bashrc")
     + " and of the zshrc, stops the agents; keeps messages and configuration"],
    [c("--purge"), "like " + c("--uninstall") + ", and also removes " + c("/var/lib/ams") + " and " + c("/etc/ams")],
], "«TAB» — The modes of install.sh")

S4 = table(["Path", "Owner", "Permissions", "Contents"], [
    [c("/usr/local/bin/ams"), "root:sudo (or wheel, admin)", c("750"), "the administrators' command"],
    [c("/usr/local/lib/ams/ams-user"), "root", c("755"), "the helper, outside the PATH"],
    [c("/usr/local/lib/ams/ams.bash") + ", " + c("ams.zsh"), "root", c("644"), "the bash and zsh hooks"],
    [c("/usr/local/share/locale/*/LC_MESSAGES/ams.mo"), "root", c("644"), "the language catalogs"],
    [c("/usr/local/share/doc/ams/"), "root", c("644"), "the two HTML manuals"],
    [c("/etc/ams/ams.conf"), "root", c("644"), "the configuration (never overwritten)"],
    [c("/etc/profile.d/ams.sh"), "root", c("644"), "the hook for the shells that read " + c("/etc/profile")],
    [c("/etc/fish/conf.d/ams.fish"), "root", c("644"), "the fish hook"],
    [c("/etc/xdg/autostart/ams-agent.desktop"), "root", c("644"), "the agent's autostart entry"],
    [c("/etc/bash.bashrc") + ", zshrc", "—", "—", "a line marked " + c("# AMS hook")],
    [c("/var/lib/ams/"), "root", c("755") + " (" + c("sent/") + " " + c("700") + ")", "the message store (" + cap(5) + ")"],
], "«TAB» — What install.sh installs, and where") + \
    note("users have no command: " + c("ams-user") + " is not in the PATH and, when run by hand without "
         + c("prompt") + " or " + c("agent") + ", replies that it is an internal helper and exits with 1.")

S5 = steps([
    c("make") + " (all warnings are errors) and " + c("make prove") + ".",
    c("make pot") + " if texts to translate have changed, then the translation in " + c("po/it.po") + ".",
    c("python3 docs/sources/build.py") + ", then " + c("tools/check-docs.py") + ": generated manuals up to date, "
    "reference aligned with the help, catalogs complete, file map complete, internal links valid, tests "
    "run on the current code (" + cap(21, 5) + ").",
    c("tests/engine.sh") + " always; " + c("tests/help-tui.py") + " if the help has changed; " + c("tests/tui.py")
    + " and " + c("tools/tui-screenshots.sh") + " if the TUI has changed; " + c("make sanitizer") + " with "
    + c("AMS_BUILD=build-san tests/engine.sh") + ", " + c("make analizza") + " and " + c("tests/fuzz/run.sh")
    + " if the code that reads data has changed; " + c("tests/container/run.sh") + " if sending, "
    "delivery, confirmations or permissions have changed; " + c("tests/vm/run.sh") + " if the desktop has changed.",
    "A test of the affected flow in test mode (" + cap(4, 4) + "); for the desktop, sudo and other users, a "
    "live test after " + c("./install.sh") + ", done by whoever has the root password.",
]) + warn("test results are committed together with the change: each suite writes its result with the "
          "commit and the code fingerprint, and " + cap(21) + " shows them next to the current fingerprint.")

CHAPTER = ("Repository, build and installation", [
    ("File map", S1),
    ("Building: the Makefile", S2),
    ("install.sh step by step", S3),
    ("What it installs, and where", S4),
    ("Before committing a change", S5),
])
