from build import arrow, box, c, code, file_map, fig, flow, note, p, steps, table, text, tree, ui, warn


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
    "└── tools/                # manual consistency, fingerprint, screenshots",
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
    ("install.sh", "Installation, upgrade, removal."),
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
    ("tests/vm/run.sh", "Tests in the desktop VM on the test server: code, clean VM, scenarios, "
     "screenshots, results."),
    ("tests/vm/prepare.sh", "Builds the VM base disk once (Debian 13, GNOME, users)."),
    ("tests/vm/user-data.tpl", "The VM's cloud-init configuration: packages, users, automatic login, "
     "accessibility."),
    ("tests/vm/start.sh", "Starts the VM from a clean copy of the base disk."),
    ("tests/vm/stop.sh", "Shuts down the VM and deletes the working disk."),
    ("tests/vm/capture.py", "Captures the VM screen from the QEMU monitor."),
    ("tests/vm/desktop.py", "Reads and presses the buttons of the RootSpeak dialogs through GNOME accessibility."),
    ("tools/check-docs.py", "Consistency checks between code, help, manuals and tests."),
    ("tools/fingerprint.sh", "Code fingerprint (SHA-256 of src, Makefile, etc, install.sh) and commit, recorded "
     "with the test results."),
    ("tools/tui-screenshots.sh", "Real TUI screenshots for the manuals, captured in the test machine."),
    ("tools/setup-dev.sh", "Says what a freshly cloned copy is missing (packages, git identity); "
     + c("--install") + " installs the packages."),
    ("tools/backup.sh", "The whole repository, with its history, in a single git bundle."),
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
    + box(740, 40, 140, 56, "system", "/usr/local", "light")
    + box(740, 116, 140, 56, "results", "engine.json", "light")
    + arrow(192, 68, 248, 68) + arrow(442, 68, 498, 68) + arrow(682, 68, 738, 68)
    + arrow(442, 144, 498, 144, "#d97706") + arrow(682, 144, 738, 144, "#16a34a"),
    900, 268, "«FIG» — The Makefile targets and where they lead", "Building")

S2 = p("The build is a Makefile with no external tools besides gcc and pkg-config (for libsystemd). "
       "Everything ends up in " + c("build/") + " (or in a folder chosen with " + c("B=") + "); the installation "
       "folder of the helper is compiled into the program with " + c("-DLIBDIR") + ".",
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

S3 = flow([("Build", "make, if needed", "dark"), ("Programs", "rspeak 750 · rootspeak-user", "blue"),
           ("Hooks", "etc/", "blue"), ("/var/lib/rootspeak", "users 755 · sent 700", "blue"),
           ("Agents", "closed and restarted", "navy")], "«FIG» — The stages of install.sh") + steps([
    "It relaunches itself with " + c("sudo") + " if it is not root, and picks the administrators' group: the first "
    "one that exists among " + c("sudo") + ", " + c("wheel") + ", " + c("admin") + " (otherwise " + c("root") + "). It warns if "
    + c("zenity") + ", " + c("loginctl") + " or " + c("systemd-run") + " are missing.",
    "If the programs are missing from " + c("build/") + ", or were built for other folders (the "
    + c("LIBDIR") + " path does not appear inside " + c("build/rspeak") + "), it builds them with " + c("make PREFIX=…")
    + " (gcc, make, pkg-config and libsystemd-dev are needed).",
    "It installs " + c("$PREFIX/lib/rootspeak/rootspeak-user") + " (" + c("755") + ") and " + c("$PREFIX/bin/rspeak")
    + " with owner " + c("root:group") + " (the administrators' group) and permissions " + c("750") + ". " + c("PREFIX")
    + " is " + c("/usr/local") + ". It removes the language catalogs left by the first 0.2.0 builds: RootSpeak "
    "speaks English only.",
    "It installs the manuals in " + c("$PREFIX/share/doc/rootspeak/") + ", the configuration (only if missing), the shell "
    "hooks and the autostart entry, replacing " + c("@LIBDIR@") + " and " + c("@VARDIR@") + ".",
    "It adds to " + c("/etc/bash.bashrc") + " the line marked " + c("# RootSpeak hook") + " (on Debian, interactive "
    "non-login shells do not read " + c("/etc/profile.d") + "); if the system zshrc exists, it adds the line that sources "
    + c("rootspeak.zsh") + "; for fish it writes " + c("/etc/fish/conf.d/rootspeak.fish") + ".",
    "It creates " + c("/var/lib/rootspeak") + " and " + c("users/") + " (" + c("755") + ") and " + c("sent/") + " (" + c("700") + ").",
    "It closes the agents of the previous version: they restart, updated, at the first send or "
    "at login.",
]) + table(["Option", "Effect"], [
    ["none", "installs or upgrades"],
    [c("--uninstall"), "removes programs, manuals, hooks and the marked lines of " + c("bash.bashrc")
     + " and of the zshrc, stops the agents; keeps messages and configuration"],
    [c("--purge"), "like " + c("--uninstall") + ", and also removes " + c("/var/lib/rootspeak") + " and " + c("/etc/rootspeak")],
], "«TAB» — The modes of install.sh")

S4 = table(["Path", "Owner", "Permissions", "Contents"], [
    [c("/usr/local/bin/rspeak"), "root:sudo (or wheel, admin)", c("750"), "the administrators' command"],
    [c("/usr/local/lib/rootspeak/rootspeak-user"), "root", c("755"), "the helper, outside the PATH"],
    [c("/usr/local/lib/rootspeak/rootspeak.bash") + ", " + c("rootspeak.zsh"), "root", c("644"), "the bash and zsh hooks"],
    [c("/usr/local/share/doc/rootspeak/"), "root", c("644"), "the two HTML manuals"],
    [c("/etc/rootspeak/rootspeak.conf"), "root", c("644"), "the configuration (never overwritten)"],
    [c("/etc/profile.d/rootspeak.sh"), "root", c("644"), "the hook for the shells that read " + c("/etc/profile")],
    [c("/etc/fish/conf.d/rootspeak.fish"), "root", c("644"), "the fish hook"],
    [c("/etc/xdg/autostart/rootspeak-agent.desktop"), "root", c("644"), "the agent's autostart entry"],
    [c("/etc/bash.bashrc") + ", zshrc", "—", "—", "a line marked " + c("# RootSpeak hook")],
    [c("/var/lib/rootspeak/"), "root", c("755") + " (" + c("sent/") + " " + c("700") + ")", "the message store (" + cap(5) + ")"],
], "«TAB» — What install.sh installs, and where") + \
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
    "delivery, confirmations or permissions have changed; " + c("tests/vm/run.sh") + " if the desktop has changed.",
    "A test of the affected flow in test mode (" + cap(4, 4) + "); for the desktop, sudo and other users, a "
    "live test after " + c("./install.sh") + ", done by whoever has the root password.",
]) + warn("test results are committed together with the change: each suite writes its result with the "
          "commit and the code fingerprint, and " + cap(20) + " shows them next to the current fingerprint.")

CHAPTER = ("Repository, build and installation", [
    ("File map", S1),
    ("Building: the Makefile", S2),
    ("install.sh step by step", S3),
    ("What it installs, and where", S4),
    ("Before committing a change", S5),
])
