import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import c, flow, note, p, steps, table, term, tip, tree, warn  # noqa: E402
from _aiuti import rif  # noqa: E402

S1 = p("AMS runs on a Linux distribution with systemd. It has been tested on Debian 13 with GNOME on Wayland: live, "
       "and with automated tests in a test machine and in a virtual machine with a desktop. With X11, other desktops "
       "and other systemd distributions it should work the same way, but this has not been tested; without systemd "
       "it does not work.", lead=True) + \
    table(["Requirement", "What it is for", "Package on Debian and Ubuntu"], [
        ["systemd", "knowing who is logged in and where, and opening the dialog on the desktop", "already present"],
        ["sudo and an administrators group", "deciding who may use " + c("ams"),
         c("sudo") + " (group " + c("sudo") + "; on Fedora and similar " + c("wheel") + ")"],
        ["a shell: bash, zsh or fish", "the confirmation question in terminals at every prompt; with sh, dash and ksh "
         "only at login", "bash is already present"],
        ["zenity", "the «Ho letto» / «Più tardi» dialog on the desktop", c("zenity")],
        ["notify-send (optional)", "the desktop notice when a confirmation could not be recorded",
         c("libnotify-bin")],
        ["the build tools, only for installing", "AMS is written in C: " + c("install.sh") + " compiles it "
         "if needed", c("gcc make pkg-config libsystemd-dev gettext")],
    ], "«TAB» — Requirements") + \
    term("admin@server:~$ sudo apt install zenity libnotify-bin gcc make pkg-config libsystemd-dev gettext",
         "Installing the packages on Debian and Ubuntu") + \
    note("on machines without a desktop zenity is not needed: AMS uses only the terminals. The installation reports "
         "«Attenzione: manca zenity» (zenity is missing) but carries on.", "Servers without a desktop.")

PERCORSO = flow([("make", "compiles, as a user", "dark"), ("./install.sh", "installs, with sudo", "navy"),
                 ("ams version", "does it answer?", "blue"), ("ams", "the TUI, empty", "green")],
                "«FIG» — From the source tree to the first start", "Installation in four steps")

S2 = PERCORSO + steps([
    "Open a terminal in the AMS folder and compile, as a normal user:" + term(
        "admin@server:~/AMS$ make"),
    "Run the installation: the script restarts itself with sudo and asks for the password." + term(
        "admin@server:~/AMS$ ./install.sh\n"
        "[sudo] password di admin:\n"
        "AMS installato. Comando: /usr/local/bin/ams (utilizzabile dal gruppo sudo).\n"
        "Manuali: /usr/local/share/doc/ams/User Manual.html e Technical Manual.html\n"
        "Le sessioni già aperte ricevono i messaggi sul terminale subito e la domanda\n"
        "di conferma dalla prossima shell o dal prossimo login."),
    "Check that the command answers:" + term("admin@server:~$ ams version\n"
                                             "AMS - Advanced Messaging System 0.2.0"),
]) + tip("if " + c("make") + " has not been run, or if the programs were compiled for other folders, "
         + c("install.sh") + " compiles on its own. If compilation fails it writes «Compilazione non riuscita: "
         "servono gcc, make, pkg-config, libsystemd-dev e gettext» (compilation failed: gcc, make, pkg-config, "
         "libsystemd-dev and gettext are needed).", "Automatic compilation.") + \
    note("users who are already logged in receive messages straight away, on the desktop too. The confirmation "
         "question in the terminal, instead, arrives from the next terminal window they open: the ones already open "
         "have not loaded AMS yet.", "Users already logged in.")

ALBERO = tree([
    "/usr/local/bin/ams  # the administrators' command (root:sudo, 750)",
    "/usr/local/lib/ams/  # the internal parts",
    "├── ams-user  # shows the messages and records the confirmations, as the user",
    "├── ams.bash  # bash hook",
    "└── ams.zsh  # zsh hook",
    "/usr/local/share/locale/it/LC_MESSAGES/ams.mo  # the Italian translation",
    "/usr/local/share/doc/ams/  # this manual and the technical manual",
    "/etc/ams/ams.conf  # the settings (not overwritten by an upgrade)",
    "/etc/profile.d/ams.sh  # shell hook at login",
    "/etc/fish/conf.d/ams.fish  # fish hook",
    "/etc/xdg/autostart/ams-agent.desktop  # autostart on the desktop",
    "/var/lib/ams/  # messages and confirmations",
    "├── sent/  # the reference copies (root only)",
    "└── users/  # one mailbox per user",
], "«FIG» — The files installed by install.sh")

S3 = p("The installation puts everything in the usual Linux places. Besides these files it adds a line, marked "
       + c("# AMS hook") + ", at the end of " + c("/etc/bash.bashrc") + " and, if zsh is installed, to the system "
       "zshrc: this is what makes the question appear in the desktop's terminals.", lead=True) + ALBERO + \
    table(["Where", "What it is", "Who uses it"], [
        [c("/usr/local/bin/ams"), "The command. Only the administrators group can run it.", "administrators"],
        [c("/usr/local/lib/ams/ams-user"), "The helper that shows the messages and records the confirmations. It is "
         "not a command: users never launch it, it starts on its own.", "users' shells and desktops"],
        [c("/etc/ams/ams.conf"), "The settings (" + rif(10) + ").", "everyone, read-only"],
        [c("/var/lib/ams/"), "The messages, the users' mailboxes, the confirmations.", "AMS"],
        [c("/etc/xdg/autostart/ams-agent.desktop"), "Starts the desktop agent at every graphical login.",
         "the users' desktops"],
    ], "«TAB» — What gets installed")

S4 = p("The " + c("ams") + " command belongs to root and to the administrators group the machine already has: "
       + c("sudo") + " on Debian and Ubuntu, " + c("wheel") + " on Fedora and similar (failing that, " + c("admin")
       + " or " + c("root") + "). AMS has no list of administrators of its own.", lead=True) + \
    term("admin@server:~$ stat -c '%U:%G %a %n' /usr/local/bin/ams\n"
         "root:sudo 750 /usr/local/bin/ams", "The command and its permissions: root and the sudo group, nobody else") + \
    table(["To", "Command", "When it takes effect"], [
        ["give access to AMS", c("sudo usermod -aG sudo anna"), "from anna's next login"],
        ["take it away", c("sudo gpasswd -d anna sudo"), "from anna's next login"],
        ["find out who can use it", c("getent group sudo"), "immediately"],
    ], "«TAB» — Managing the administrators") + \
    warn("joining the " + c("sudo") + " group means being able to become root on the whole machine, not only to "
         "use AMS. This is intended: sending messages to all users is an administrator's task.", "A single group.")

S5 = p("Right after installation it is worth doing three checks, none of which disturbs anyone.", lead=True) + steps([
    "Open the built-in help: " + c("ams --help") + " (" + rif(9) + "). Leave it with " + c("q") + ".",
    "Check the list of messages: it is empty, because nothing has been sent yet." + term(
        "admin@server:~$ ams list\nNessun messaggio inviato."),
    "Open the TUI by typing " + c("ams") + " on its own: it shows «Nessun messaggio inviato.» (No messages sent.) "
    "and the keys at the bottom. Leave it with " + c("q") + ".",
    "For a complete test, send a message to yourself, as in " + rif(4) + ".",
]) + tip("a message sent to yourself shows in a few seconds everything the users will see: the text in the "
         "terminal, the question at the prompt, the dialog on the desktop.", "Try it on yourself.")

S6 = table(["To", "Command", "What happens"], [
    ["Upgrade", c("./install.sh") + " from the folder of the new version",
     "Installs the new version; messages and settings are kept. The desktop agents of the previous version are "
     "closed: a new one starts with the first message or at the next login."],
    ["Remove AMS", c("./install.sh --uninstall"), "Removes the command, hooks, manuals and translations; messages "
     "(" + c("/var/lib/ams") + ") and settings (" + c("/etc/ams") + ") are kept, for a possible reinstallation."],
    ["Remove everything", c("./install.sh --purge"), "As above, and in addition deletes the messages and the "
     "settings."],
], "«TAB» — Upgrading and removing") + \
    term("admin@server:~/AMS$ ./install.sh --uninstall\n"
         "AMS rimosso. Messaggi (/var/lib/ams) e configurazione (/etc/ams) conservati.", "Removal") + \
    warn(c("--purge") + " also deletes the record of who confirmed what. If it needs to be kept, copy "
         + c("/var/lib/ams") + " elsewhere first. The events remain in the system log in any case.",
         "Before --purge.")

CHAPTER = ("Installation and first start", [
    ("Requirements", S1),
    ("Compiling and installing", S2),
    ("What gets installed", S3),
    ("The administrators", S4),
    ("First start", S5),
    ("Upgrading and removing", S6),
])
