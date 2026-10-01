import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import c, flow, note, p, steps, table, term, tip, tree, warn  # noqa: E402
from _helpers import ref  # noqa: E402

S1 = p("RootSpeak runs on a Linux distribution with systemd; without systemd it does not work. It is tested "
       "automatically, as root and with real users and sessions, on the current versions of Debian, Ubuntu, Fedora, "
       "RHEL and its rebuilds (CentOS Stream, Rocky Linux, AlmaLinux, Oracle Linux), openSUSE, SLES and Arch Linux: "
       "the list, with the result on each one, is in the technical manual, chapter “Tests and checks”. The desktop "
       "dialog has been tested with GNOME (Debian 13, Ubuntu 24.04, Rocky Linux 9 with SELinux), KDE Plasma "
       "(Fedora 44) and Cinnamon (the desktop of Linux Mint), on Wayland and on X11.", lead=True) + \
    table(["Requirement", "What it is for"], [
        ["systemd", "knowing who is logged in and where, and opening the dialog on the desktop"],
        ["sudo and an administrators group", "deciding who may use " + c("rspeak") + ": the group " + c("sudo")
         + " on Debian and Ubuntu, " + c("wheel") + " on the others"],
        ["a shell: bash, zsh or fish", "the confirmation question in terminals at every prompt; with sh, dash and ksh "
         "only at login"],
        ["zenity", "the “I have read it” / “Later” dialog on the desktop"],
        ["notify-send (optional)", "the desktop notice when a confirmation could not be recorded"],
        ["the build tools, only for installing", "RootSpeak is written in C: " + c("install.sh") + " compiles it "
         "if needed, with the compiler and the systemd development files"],
    ], "«TAB» — Requirements") + \
    table(["Distribution", "Packages to install"], [
        ["Debian, Ubuntu", c("sudo apt install zenity libnotify-bin gcc make pkg-config libsystemd-dev")],
        ["Fedora, RHEL, CentOS Stream, Rocky, Alma, Oracle",
         c("sudo dnf install zenity libnotify gcc make pkgconf-pkg-config systemd-devel")],
        ["openSUSE, SLES", c("sudo zypper install zenity libnotify-tools gcc make pkg-config systemd-devel")],
        ["Arch Linux", c("sudo pacman -S zenity libnotify gcc make pkgconf")],
    ], "«TAB» — The packages on each family of distributions") + \
    term("admin@server:~$ sudo apt install zenity libnotify-bin gcc make pkg-config libsystemd-dev",
         "Installing the packages on Debian and Ubuntu") + \
    note("on machines without a desktop zenity and notify-send are not needed: RootSpeak uses only the terminals. "
         "The installation reports “Warning: zenity is missing” but carries on.", "Servers without a desktop.") + \
    note("on Fedora and RHEL the login shell dash stops on a file of the distribution (" + c("/etc/profile.d/lang.sh")
         + ") before reaching RootSpeak; on openSUSE the login shell must be " + c("/usr/bin/ksh93") + ", not "
         + c("/usr/bin/ksh") + ", which cannot start a login. Both are limits of the distributions, with or without "
         "RootSpeak.", "Two shells to know about.")

INSTALL_PATH = flow([("make", "compiles, as a user", "dark"), ("./install.sh", "installs, with sudo", "navy"),
                 ("rspeak version", "does it answer?", "blue"), ("rspeak", "the TUI, empty", "green")],
                "«FIG» — From the source tree to the first start", "Installation in four steps")

S2 = INSTALL_PATH + steps([
    "Open a terminal in the RootSpeak folder and compile, as a normal user:" + term(
        "admin@server:~/ROOTSPEAK$ make"),
    "Run the installation: the script restarts itself with sudo and asks for your password. At the end it confirms "
    "“RootSpeak installed”, gives the paths of the command (usable by the sudo group) and of the manuals, and reminds "
    "you that sessions already open get the messages in the terminal at once, and the confirmation question from the "
    "next shell or the next login." + term(
        "admin@server:~/ROOTSPEAK$ ./install.sh\n"
        "[sudo] password for admin:\n"
        "RootSpeak installed. Command: /usr/local/bin/rspeak (usable by the sudo group).\n"
        "Manuals: /usr/local/share/doc/rootspeak/User Manual.html and Technical Manual.html\n"
        "Sessions already open get messages in the terminal at once, and the\n"
        "confirmation question from the next shell or the next login."),
    "Check that the command answers:" + term("admin@server:~$ rspeak version\n"
                                             "RootSpeak - Advanced Messaging System for Linux 0.2.0"),
]) + tip("if " + c("make") + " has not been run, or if the programs were compiled for other folders, "
         + c("install.sh") + " compiles on its own. If compilation fails it writes “Build failed: gcc, make, pkg-config and "
         "the systemd development files are needed (libsystemd-dev or systemd-devel)”.", "Automatic compilation.") + \
    note("users who are already logged in receive messages straight away, on the desktop too. The confirmation "
         "question in the terminal, instead, arrives from the next terminal window they open: the ones already open "
         "have not loaded RootSpeak yet.", "Users already logged in.")

TREE = tree([
    "/usr/local/bin/rspeak  # the administrators' command (root:sudo, 750)",
    "/usr/local/lib/rootspeak/  # the internal parts",
    "├── rootspeak-user  # shows the messages and records the confirmations, as the user",
    "├── rootspeak.bash  # bash hook",
    "└── rootspeak.zsh  # zsh hook",
    "/usr/local/share/doc/rootspeak/  # this manual and the technical manual",
    "/etc/rootspeak/rootspeak.conf  # the settings (not overwritten by an upgrade)",
    "/etc/profile.d/rootspeak.sh  # shell hook at login",
    "/etc/fish/conf.d/rootspeak.fish  # fish hook",
    "/etc/xdg/autostart/rootspeak-agent.desktop  # autostart on the desktop",
    "/var/lib/rootspeak/  # messages and confirmations",
    "├── sent/  # the reference copies (root only)",
    "└── users/  # one mailbox per user",
], "«FIG» — The files installed by install.sh")

S3 = p("The installation puts everything in the usual Linux places. Besides these files it adds a line, marked "
       + c("# RootSpeak hook") + ", at the end of " + c("/etc/bash.bashrc") + " and, if zsh is installed, to the system "
       "zshrc: this is what makes the question appear in the desktop's terminals.", lead=True) + TREE + \
    table(["Where", "What it is", "Who uses it"], [
        [c("/usr/local/bin/rspeak"), "The command. Only the administrators group can run it.", "administrators"],
        [c("/usr/local/lib/rootspeak/rootspeak-user"), "The helper that shows the messages and records the confirmations. It is "
         "not a command: users never launch it, it starts on its own.", "users' shells and desktops"],
        [c("/etc/rootspeak/rootspeak.conf"), "The settings (" + ref(10) + ").", "everyone, read-only"],
        [c("/var/lib/rootspeak/"), "The messages, the users' mailboxes, the confirmations.", "RootSpeak"],
        [c("/etc/xdg/autostart/rootspeak-agent.desktop"), "Starts the desktop agent at every graphical login.",
         "the users' desktops"],
    ], "«TAB» — What gets installed")

S4 = p("The " + c("rspeak") + " command belongs to root and to the administrators group the machine already has: "
       + c("sudo") + " on Debian and Ubuntu, " + c("wheel") + " on Fedora and similar (failing that, " + c("admin")
       + " or " + c("root") + "). RootSpeak has no list of administrators of its own.", lead=True) + \
    term("admin@server:~$ stat -c '%U:%G %a %n' /usr/local/bin/rspeak\n"
         "root:sudo 750 /usr/local/bin/rspeak", "The command and its permissions: root and the sudo group, nobody else") + \
    table(["To", "Command", "When it takes effect"], [
        ["give access to RootSpeak", c("sudo usermod -aG sudo anna"), "from anna's next login"],
        ["take it away", c("sudo gpasswd -d anna sudo"), "from anna's next login"],
        ["find out who can use it", c("getent group sudo"), "immediately"],
    ], "«TAB» — Managing the administrators") + \
    warn("joining the " + c("sudo") + " group means being able to become root on the whole machine, not only to "
         "use RootSpeak. This is intended: sending messages to all users is an administrator's task.", "A single group.")

S5 = p("Right after installation it is worth doing three checks, none of which disturbs anyone.", lead=True) + steps([
    "Open the built-in help: " + c("rspeak --help") + " (" + ref(9) + "). Leave it with " + c("q") + ".",
    "Check the list of messages: it is empty, because nothing has been sent yet." + term(
        "admin@server:~$ rspeak list\nNo messages sent."),
    "Open the TUI by typing " + c("rspeak") + " on its own: it shows “No messages sent.” and the keys at the "
    "bottom. Leave it with " + c("q") + ".",
    "For a complete test, send a message to yourself, as in " + ref(4) + ".",
]) + tip("a message sent to yourself shows in a few seconds everything the users will see: the text in the "
         "terminal, the question at the prompt, the dialog on the desktop.", "Try it on yourself.")

S6 = table(["To", "Command", "What happens"], [
    ["Upgrade", c("./install.sh") + " from the folder of the new version",
     "Installs the new version; messages and settings are kept. The desktop agents of the previous version are "
     "closed: a new one starts with the first message or at the next login."],
    ["Remove RootSpeak", c("./install.sh --uninstall"), "Removes the command, the hooks and the manuals; messages "
     "(" + c("/var/lib/rootspeak") + ") and settings (" + c("/etc/rootspeak") + ") are kept, for a possible reinstallation."],
    ["Remove everything", c("./install.sh --purge"), "As above, and in addition deletes the messages and the "
     "settings."],
], "«TAB» — Upgrading and removing") + \
    term("admin@server:~/ROOTSPEAK$ ./install.sh --uninstall\n"
         "RootSpeak removed. Messages (/var/lib/rootspeak) and configuration (/etc/rootspeak) kept.",
         "Removal: messages and settings stay") + \
    warn(c("--purge") + " also deletes the record of who confirmed what. If it needs to be kept, copy "
         + c("/var/lib/rootspeak") + " elsewhere first. The events remain in the system log in any case.",
         "Before --purge.")

CHAPTER = ("Installation and first start", [
    ("Requirements", S1),
    ("Compiling and installing", S2),
    ("What gets installed", S3),
    ("The administrators", S4),
    ("First start", S5),
    ("Upgrading and removing", S6),
])
