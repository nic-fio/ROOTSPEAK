import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import VERSION, c, flow, note, p, steps, table, term, tip, tree, warn  # noqa: E402
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
        ["a 64-bit PC processor (x86-64)", "the programs of the packages are built for it"],
    ], "«TAB» — Requirements") + \
    table(["Distribution", "Desktop packages, if missing"], [
        ["Debian, Ubuntu", c("sudo apt install zenity libnotify-bin")],
        ["Fedora, RHEL, CentOS Stream, Rocky, Alma, Oracle", c("sudo dnf install zenity libnotify")],
        ["openSUSE, SLES", c("sudo zypper install zenity libnotify-tools")],
        ["Arch Linux", c("sudo pacman -S zenity libnotify")],
    ], "«TAB» — The desktop packages on each family of distributions") + \
    p("The RootSpeak package brings zenity with it, except on Arch Linux; notify-send is only suggested. Where they "
      "are missing, they are installed like this:") + \
    term("admin@server:~$ sudo apt install zenity libnotify-bin", "Installing the desktop packages on Debian and Ubuntu") + \
    note("on machines without a desktop zenity and notify-send are not needed: RootSpeak uses only the terminals. "
         "The packages only recommend zenity; " + c("install.sh") + " reports “Warning: zenity is missing” but carries on.", "Servers without a desktop.") + \
    note("on Fedora and RHEL the login shell dash stops on a file of the distribution (" + c("/etc/profile.d/lang.sh")
         + ") before reaching RootSpeak; on openSUSE the login shell must be " + c("/usr/bin/ksh93") + ", not "
         + c("/usr/bin/ksh") + ", which cannot start a login. Both are limits of the distributions, with or without "
         "RootSpeak.", "Two shells to know about.")

ARCHIVE = "rootspeak-" + VERSION + "-linux-x86_64"
DEB = "rootspeak_" + VERSION + "-1_amd64.deb"
RPM = "rootspeak-" + VERSION + "-1.x86_64.rpm"
PKG = "rootspeak-" + VERSION + "-1-x86_64.pkg.tar.zst"

INSTALL_PATH = flow([("Download", "the package of your distribution", "dark"),
                     ("apt, dnf, zypper, pacman", "installs it", "navy"),
                     ("rspeak version", "does it answer?", "blue"), ("rspeak", "the TUI, empty", "green")],
                    "«FIG» — From the download to the first start", "Installation in four steps")

PACKAGES = table(["Distribution", "File", "Install with"], [
    ["Debian, Ubuntu (and Linux Mint)", c(DEB), c("sudo apt install ./" + DEB)],
    ["Fedora, RHEL, CentOS Stream, Rocky, Alma, Oracle", c(RPM), c("sudo dnf install ./" + RPM)],
    ["openSUSE, SLES", c(RPM), c("sudo zypper install --allow-unsigned-rpm ./" + RPM)],
    ["Arch Linux", c(PKG), c("sudo pacman -U " + PKG)],
    ["any other with systemd", c(ARCHIVE + ".tar.gz"), c("./install.sh") + " from the extracted folder"],
], "«TAB» — The download for each family of distributions")

S2 = p("RootSpeak is free (" + ref(1) + ", “Licence”) and is downloaded from its website, "
       "<b>rootspeak.nicfio.it</b>, as a package for the package manager of your distribution: a " + c(".deb")
       + " for Debian and Ubuntu, an " + c(".rpm") + " for the Fedora, RHEL and SUSE families, a package for Arch "
       "Linux. The programs are already built, nothing needs to be compiled; the package manager knows every file "
       "RootSpeak installs and removes them cleanly.", lead=True) + INSTALL_PATH + PACKAGES + steps([
    "Download the file of your distribution and " + c("SHA256SUMS") + " from the website into the same folder, and "
    "check that the file arrived intact:" + term(
        "admin@server:~$ sha256sum -c --ignore-missing SHA256SUMS\n"
        + DEB + ": OK"),
    "Install it with the package manager, which asks for your password; on Debian and Ubuntu:" + term(
        "admin@server:~$ sudo apt install ./" + DEB) + "The package manager also installs what RootSpeak needs: "
    "zenity for the desktop dialog comes with it on Debian, Ubuntu, Fedora, RHEL and SUSE; on Arch Linux it is "
    "optional, " + c("sudo pacman -S zenity") + ".",
    "Check that the command answers:" + term("admin@server:~$ rspeak version\n"
                                             "RootSpeak - Advanced Messaging System for Linux " + VERSION),
]) + note("the packages are not signed with a key: the integrity check is " + c("SHA256SUMS") + ", downloaded from "
          "the website over HTTPS. For this reason zypper wants " + c("--allow-unsigned-rpm") + " and dnf on Fedora "
          "says that it skipped the OpenPGP checks for the package.", "Unsigned packages.") + \
    note("users who are already logged in receive messages straight away, on the desktop too. The confirmation "
         "question in the terminal, instead, arrives from the next terminal window they open: the ones already open "
         "have not loaded RootSpeak yet.", "Users already logged in.")

S2B = p("For a distribution with systemd that has none of these package managers, the website also offers "
        "an archive, " + c(ARCHIVE + ".tar.gz") + ", with the same programs, an installer script, the settings file "
        "and the two manuals. It installs in " + c("/usr/local") + " instead of " + c("/usr") + ".", lead=True) + steps([
    "Download the archive and " + c("SHA256SUMS") + ", check it as above, extract it and enter its folder:" + term(
        "admin@server:~$ tar -xzf " + ARCHIVE + ".tar.gz\n"
        "admin@server:~$ cd " + ARCHIVE),
    "Run the installation: the script restarts itself with sudo and asks for your password. At the end it confirms "
    "“RootSpeak installed”, gives the paths of the command (usable by the sudo group) and of the manuals, and reminds "
    "you that sessions already open get the messages in the terminal at once, and the confirmation question from the "
    "next shell or the next login." + term(
        "admin@server:~/" + ARCHIVE + "$ ./install.sh\n"
        "[sudo] password for admin:\n"
        "RootSpeak installed. Command: /usr/local/bin/rspeak (usable by the sudo group).\n"
        "Manuals: /usr/local/share/doc/rootspeak/User Manual.html and Technical Manual.html\n"
        "Sessions already open get messages in the terminal at once, and the\n"
        "confirmation question from the next shell or the next login."),
]) + tip("keep the extracted folder: " + c("./install.sh --uninstall") + " is run from there (“Upgrading and removing”, "
         "below). The archive also contains a short " + c("README.txt") + ".", "Keep the folder.") + \
    note("the archive and a package do not live together: with the package installed, " + c("./install.sh")
         + " stops and answers “RootSpeak is installed from a package: update or remove it with the package manager "
         "(apt, dnf, zypper, pacman).”. The other way round, see “Upgrading and removing”.", "One or the other.")

S2C = p("The website also offers the source code, " + c("rootspeak-" + VERSION + "-source.tar.gz") + ", so that you can "
        "check what RootSpeak does on your machines before installing it, or build it yourself (" + ref(1)
        + ", “Licence”). Building needs gcc, make, pkg-config and the systemd development files: "
        + c("libsystemd-dev") + " on Debian and Ubuntu, " + c("systemd-devel") + " on Fedora, RHEL and openSUSE.",
        lead=True) + steps([
    "Download the source archive and " + c("SHA256SUMS") + ", check it as above, extract it and enter its folder.",
    "Build and run the tests, as a normal user: they run in test mode, on a temporary message store, without root." + term(
        "admin@server:~/rootspeak-" + VERSION + "-source$ make\n"
        "admin@server:~/rootspeak-" + VERSION + "-source$ make unit\n"
        "OK: 15 tests\n"
        "admin@server:~/rootspeak-" + VERSION + "-source$ tests/engine.sh\n"
        "OK: 76 checks"),
    "Install with " + c("./install.sh") + ", as for the archive above: it installs in " + c("/usr/local")
    + " and builds the programs first if they are missing.",
]) + note("the folder also holds the files that make the packages (" + c("tools/packages/") + ") and a short "
          + c("README.txt") + ".", "What is inside.")

TREE = tree([
    "/usr/bin/rspeak  # the administrators' command (root:sudo, 750)",
    "/usr/lib/rootspeak/  # the internal parts",
    "├── rootspeak-user  # shows the messages and records the confirmations, as the user",
    "├── rootspeak-setup  # what installing and removing do besides copying files",
    "├── rootspeak.bash  # bash hook",
    "└── rootspeak.zsh  # zsh hook",
    "/usr/share/doc/rootspeak/  # this manual, the technical manual, the licence",
    "/usr/share/icons/hicolor/*/apps/rootspeak.*  # the logo, as the icon",
    "/etc/rootspeak/rootspeak.conf  # the settings (not overwritten by an upgrade)",
    "/etc/profile.d/rootspeak.sh  # shell hook at login",
    "/etc/fish/conf.d/rootspeak.fish  # fish hook",
    "/etc/xdg/autostart/rootspeak-agent.desktop  # autostart on the desktop",
    "/var/lib/rootspeak/  # messages and confirmations",
    "├── sent/  # the reference copies (root only)",
    "└── users/  # one mailbox per user",
], "«FIG» — The files installed by the package (the archive puts the first four in /usr/local)")

S3 = p("The installation puts everything in the usual Linux places. Besides these files it adds a line, marked "
       + c("# RootSpeak hook") + ", at the end of " + c("/etc/bash.bashrc") + " and, if zsh is installed, to the system "
       "zshrc: this is what makes the question appear in the desktop's terminals. The logo of RootSpeak is its icon: "
       "in the software centres and in the desktop notices.", lead=True) + TREE + \
    table(["Where", "What it is", "Who uses it"], [
        [c("/usr/bin/rspeak"), "The command. Only the administrators group can run it.", "administrators"],
        [c("/usr/lib/rootspeak/rootspeak-user"), "The helper that shows the messages and records the confirmations. It is "
         "not a command: users never launch it, it starts on its own.", "users' shells and desktops"],
        [c("/etc/rootspeak/rootspeak.conf"), "The settings (" + ref(10) + ").", "everyone, read-only"],
        [c("/var/lib/rootspeak/"), "The messages, the users' mailboxes, the confirmations.", "RootSpeak"],
        [c("/etc/xdg/autostart/rootspeak-agent.desktop"), "Starts the desktop agent at every graphical login.",
         "the users' desktops"],
    ], "«TAB» — What gets installed") + \
    note("the minimal installations of Ubuntu, and the container images of Ubuntu and Arch Linux, are set up not "
         "to extract " + c("/usr/share/doc") + ": there the package installs everything except the two manuals, "
         "which are on the website, rootspeak.nicfio.it.", "Minimal systems.")

S4 = p("The " + c("rspeak") + " command belongs to root and to the administrators group the machine already has: "
       + c("sudo") + " on Debian and Ubuntu, " + c("wheel") + " on Fedora and similar (failing that, " + c("admin")
       + " or " + c("root") + "). RootSpeak has no list of administrators of its own.", lead=True) + \
    term("admin@server:~$ stat -c '%U:%G %a %n' /usr/bin/rspeak\n"
         "root:sudo 750 /usr/bin/rspeak", "The command and its permissions: root and the sudo group, nobody else") + \
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

S6 = p("A package is upgraded by installing the file of the new version in the same way, and removed with the "
       "package manager. Messages and settings survive upgrades and removal; only " + c("apt purge") + " also deletes "
       "them.", lead=True) + table(["To", "Debian, Ubuntu", "Fedora, RHEL…", "openSUSE, SLES", "Arch Linux"], [
    ["Upgrade", c("sudo apt install ./NEW.deb"), c("sudo dnf install ./NEW.rpm"),
     c("sudo zypper install --allow-unsigned-rpm ./NEW.rpm"), c("sudo pacman -U NEW.pkg.tar.zst")],
    ["Remove RootSpeak", c("sudo apt remove rootspeak"), c("sudo dnf remove rootspeak"), c("sudo zypper remove rootspeak"),
     c("sudo pacman -R rootspeak")],
    ["Remove everything", c("sudo apt purge rootspeak"), "remove, then " + c("sudo rm -rf /var/lib/rootspeak /etc/rootspeak"),
     "the same", "the same"],
], "«TAB» — Upgrading and removing a package") + \
    p("Upgrading closes the desktop agents of the previous version: a new one starts with the first message or at "
      "the next login. Removing takes away the command, the hooks and the manuals; the messages ("
      + c("/var/lib/rootspeak") + ") and the settings (" + c("/etc/rootspeak") + ") are kept, for a possible "
      "reinstallation.") + \
    p("From the archive to a package: on Debian, Ubuntu, Fedora, RHEL and SUSE install the package over it, and it "
      "takes the archive's place, messages included:" + term(
          "RootSpeak: the installation from the archive in /usr/local was replaced by this package.") +
      "pacman, on Arch Linux, does not install over files it does not know: run " + c("./install.sh --uninstall")
      + " from the archive's folder first (the messages stay), then " + c("sudo pacman -U") + ".") + \
    table(["To", "Command", "What happens"], [
        ["Upgrade", "download and extract the new archive, then " + c("./install.sh") + " from its folder",
         "Installs the new version; messages and settings are kept."],
        ["Remove RootSpeak", c("./install.sh --uninstall"), "Removes the command, the hooks and the manuals; messages "
         "and settings are kept."],
        ["Remove everything", c("./install.sh --purge"), "As above, and in addition deletes the messages and the "
         "settings."],
    ], "«TAB» — Upgrading and removing, with the archive") + \
    term("admin@server:~/" + ARCHIVE + "$ ./install.sh --uninstall\n"
         "RootSpeak removed. Messages (/var/lib/rootspeak) and configuration (/etc/rootspeak) kept.",
         "Removal of the archive: messages and settings stay") + \
    warn(c("apt purge") + " and " + c("--purge") + " also delete the record of who confirmed what. If it needs to be "
         "kept, copy " + c("/var/lib/rootspeak") + " elsewhere first. The events remain in the system log in any case.",
         "Before a purge.")

CHAPTER = ("Installation and first start", [
    ("Requirements", S1),
    ("Downloading and installing", S2),
    ("Without a package: the archive", S2B),
    ("From the source code", S2C),
    ("What gets installed", S3),
    ("The administrators", S4),
    ("First start", S5),
    ("Upgrading and removing", S6),
])
