import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import VERSION, arrow, box, c, fig, key, note, p, path, table, text, tip, ui, ul, warn  # noqa: E402
from _helpers import CONFIRMED, DELIVERED, SENT, REVOKED, EXPIRED, ref  # noqa: E402

PANORAMA = fig(
    box(20, 128, 170, 64, "Administrator", "sudo rspeak · TUI or commands", "dark")
    + box(240, 128, 170, 64, "RootSpeak", "one mailbox per user", "navy")
    + box(462, 38, 220, 64, "In the terminal", "text at once, question at the prompt", "blue")
    + box(462, 128, 220, 64, "On the desktop", "“I have read it” / “Later” dialog", "blue")
    + box(462, 218, 220, 64, "At the next login", "for whoever is not logged in", "light")
    + box(730, 128, 150, 64, "Confirmation ✓", "who, when, from where", "green")
    + arrow(192, 160, 238, 160)
    + path([(412, 150), (436, 150), (436, 70), (460, 70)])
    + arrow(412, 160, 460, 160)
    + path([(412, 170), (436, 170), (436, 250), (460, 250)])
    + path([(684, 70), (706, 70), (706, 150), (728, 150)], "#16a34a", True)
    + arrow(684, 160, 728, 160, "#16a34a", True)
    + path([(684, 250), (706, 250), (706, 170), (728, 170)], "#16a34a", True)
    + path([(805, 194), (805, 318), (105, 318), (105, 194)], "#475569", True)
    + text(455, 309, "the message list and rspeak status: who has confirmed and who has not", 11.5, "#334155", "600"),
    900, 340, "«FIG» — A message reaches every session of the user; the first confirmation goes back to the administrator",
    "The path of a message")

S1 = p("<b>RootSpeak — Advanced Messaging System for Linux</b> lets whoever administers a Linux machine send a message to the "
       "users and know, for each of them, whether they have confirmed reading it. It is meant for the notices that "
       "matter: maintenance, a reboot, a new rule, an account about to expire.", lead=True) + \
    p("The administrator writes the message in the full-screen interface of " + c("rspeak") + " or with a command. "
      "RootSpeak delivers it wherever the user is: in terminal windows (including ssh connections), on the desktop, or at "
      "the next login if the user is not logged in at that moment. The user confirms with a click or a single "
      "letter, and the administrator sees who has confirmed, when and from where.") + PANORAMA + \
    p("For administrators, RootSpeak offers a single place in which to:") + ul([
        "write a message and send it to one user, to a group, to everyone or only to whoever is logged in;",
        "see how far each recipient has got: " + SENT + ", " + DELIVERED + " or " + CONFIRMED + ";",
        "remind whoever has not confirmed yet, revoke a mistaken message, give it an expiry;",
        "find the history of every message in the system log;",
        "delete old messages when they are no longer needed.",
    ]) + note("a confirmation is a <b>statement</b> by the user (“I have read it”), recorded with date, time and "
              "channel. RootSpeak cannot know whether the message was really read, and neither can any other messaging "
              "system.",
              "What a confirmation says.")

S2 = table(["", c("wall") + " / " + c("write"), c("/etc/motd") + " and banners", "RootSpeak"], [
    ["Writes to the terminals of logged-in users", "yes", "no", "yes"],
    ["Appears on the desktop (X11 and Wayland)", "no", "no", "yes, in a dialog"],
    ["Reaches users who are not logged in", "no", "yes, at every text login", "yes, at the next login"],
    ["Asks for a read confirmation", "no", "no", "yes, for every message"],
    ["Shows the message again to whoever has not confirmed", "no", "no", "yes, every 30 minutes"],
    ["Tells the administrator who has read it", "no", "no", "yes, with date, time and channel"],
], "«TAB» — RootSpeak and the classic Linux tools") + \
    p("RootSpeak, on the other hand, does <b>not</b> do these things, by design:") + ul([
        "<b>It never blocks anyone.</b> No locked screen, no denied login, no disconnection: the user can always "
        "postpone and carry on working. The message comes back later.",
        "<b>It is not a chat.</b> Users receive and confirm; they do not reply, do not write to others and have no "
        "commands to learn.",
        "<b>It does not use the network.</b> It reaches the users of this machine, including those connected "
        "remotely with ssh, but not other machines.",
        "<b>It does not disturb automated programs.</b> Backups, cron, copies with " + c("scp") + " or " + c("rsync")
        + " never see the RootSpeak question: it appears only in interactive shells.",
    ])

S3 = table(["Who", "What they do with RootSpeak", "Chapters"], [
    ["Administrator of the machine", "Installs RootSpeak, sends messages, follows the confirmations, revokes and reminds, "
     "changes the settings.", "2 - 7, 9 - 13"],
    ["Whoever has to explain RootSpeak to the users", "Knows what users see in the terminal and on the desktop, and how to "
     "answer their questions.", "8"],
    ["Whoever assesses security", "Knows who can use RootSpeak, who sees what and what a confirmation is worth.", "11"],
], "«TAB» — The readers of this manual") + \
    p("Anyone using RootSpeak for the first time can follow the guided path in " + ref(4) + ", which leads from "
      "installation to the first confirmation in a few steps. The users who receive the messages do not need to "
      "read anything: the dialog and the question explain themselves, and there is no command for them.") + \
    tip("the inner workings (message store, delivery, security) are described in the Technical Manual, "
        "installed next to this one in " + c("/usr/local/share/doc/rootspeak/") + ".", "Further reading.")

S4 = table(["Convention", "Meaning"], [
    [ui("I have read it"), "Text that appears on the screen: buttons, window titles, fields, RootSpeak messages. "
     "RootSpeak speaks English, whatever the language of the user's session."],
    [c("rspeak send --to mario"), "Commands, file names and values to type exactly as shown."],
    [key("Ctrl", "S") + " " + key("Enter"), "Keys to press; the + sign means “together”."],
    [SENT + " " + DELIVERED + " " + CONFIRMED, "The three states of a recipient, always in these colours, "
     "the same as in the TUI."],
    [REVOKED + " " + EXPIRED, "Properties of the message, not states of the recipients: from that moment on the "
     "message is no longer shown."],
    ["Blue <b>Note</b> box", "Information that helps understanding."],
    ["Green <b>Tip</b> box", "A better or safer way to do something."],
    ["Yellow <b>Warning</b> box", "A behaviour that may be surprising or cause data loss."],
], "«TAB» — The conventions of the manual") + \
    p("In the examples " + c("admin") + " is an administrator; " + c("mario") + ", " + c("anna") + " and " + c("luca")
      + " are users of the machine " + c("server") + ", and " + c("@developers") + " is a group. In the dark boxes, "
      "lines starting with the prompt (" + c("admin@server:~$") + ") are commands to type; orange lines are what "
      "RootSpeak shows to the users; red lines are errors. The TUI screenshots are real, taken from RootSpeak while "
      "running.") + \
    note("this manual describes RootSpeak " + VERSION + ". The command " + c("rspeak version") + " shows the installed "
         "version.", "Version.") + \
    warn(c("rspeak") + " always works as administrator (root) and asks for the sudo password, even just to show "
         "the help: this is a deliberate choice, not a bug.", "Always with sudo.")

CHAPTER = ("Welcome", [
    ("What RootSpeak is", S1),
    ("What it does, and what it does not", S2),
    ("Who this manual is for", S3),
    ("Conventions", S4),
])
