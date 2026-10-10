# Copyright (c) 2026 Nicola Fiorillo
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import c, dialog, flow, key, note, p, steps, table, term, tip, ui  # noqa: E402
from _helpers import CONFIRMED, DELIVERED, ref  # noqa: E402

S1 = p("This path leads from a freshly installed RootSpeak to the first confirmation, in four stages. The recipient of "
       "the first message can be the administrator themselves: that way you see with your own eyes what the users "
       "receive. Each stage refers to the chapter that explains it in detail.", lead=True) + \
    flow([("1. Install", "the package of the distribution", "dark"), ("2. Write and send", "rspeak, key n", "blue"),
          ("3. The user confirms", "dialog or terminal", "blue"), ("4. Check", "Enter on the message", "green")],
         "«FIG» — The four stages of the first steps", "From nothing to the first confirmation") + \
    table(["Stage", "What you do", "Chapter"], [
        ["1", "Install RootSpeak and check that it answers", ref(2)],
        ["2", "Write the message in the TUI (or with " + c("rspeak send") + ") and send it", ref(5)],
        ["3", "The recipient sees the dialog or the question and confirms", ref(8)],
        ["4", "Open the message and see who has confirmed", ref(6)],
    ], "«TAB» — The path")

TEXT = "On Saturday from 8 am to 12 noon the server will be off."

S2 = p("The simplest way is the TUI. Here the message goes to Mario; to try it on yourself, just type your own "
       "name.", lead=True) + steps([
        "Open a terminal and type " + c("rspeak") + ". When prompted, enter your password: " + c("rspeak")
        + " always asks for it, because it works as administrator." + term(
            "admin@server:~$ rspeak\n[sudo] password for admin:"),
        "In the list of messages press " + key("n") + ": the " + ui("New message") + " screen opens.",
        "In the " + ui("To") + " field type " + c("mario") + " and press " + key("Tab") + ": on the right "
        + ui("1 recipient") + " appears.",
        "In the " + ui("Title") + " field type " + c("Maintenance") + "; leave " + ui("Expires")
        + " empty and move to " + ui("Text") + " with " + key("Tab") + ".",
        "Type the text: " + c(TEXT) + " Start a new line with " + key("Enter") + ".",
        "Press " + key("Ctrl", "S") + ". The summary " + ui("Send the message?") + " appears: press " + key("y")
        + " to confirm.",
        "The " + ui("Message sent") + " window reports the answer of RootSpeak, for example “Message 1 sent to "
        "1 user.” Any key takes you back to the list, where the message is at the top.",
    ]) + p("The same message, with a single command (same text, same reply):") + term(
        'admin@server:~$ rspeak send --to mario --title Maintenance "' + TEXT + '"\n'
        "Message 1 sent to 1 user.") + \
    tip("the message number (here " + c("1") + ") is needed for the commands " + c("status") + ", " + c("log") + ", "
        + c("revoke") + " and " + c("remind") + ". In the TUI it is not needed: you pick the message from the list.",
        "The number.")

S3 = p("If Mario is logged in, the message reaches him at once, in all his sessions. On the desktop this "
       "dialog appears, above the other windows:", lead=True) + \
    dialog("RootSpeak · Message from the administrator", "Maintenance · 01/10 10:49", TEXT,
           "«FIG» — The confirmation dialog on Mario's desktop: the title and the text, and the buttons “Later” "
           "and “I have read it”") + \
    p("In terminal windows the text appears at once, under the heading “RootSpeak · Message from the "
      "administrator”; at the next prompt RootSpeak asks for the confirmation, and after the answer " + c("y")
      + " replies “[RootSpeak] Confirmed.”:") + term(
        "── RootSpeak · Message from the administrator · Maintenance · 01/10 10:49 ──\n"
        + TEXT + "\n"
        "────────────────────────────────────────\n"
        "[RootSpeak] Do you confirm you have read the message? [y/N] y\n"
        "[RootSpeak] Confirmed.\n"
        "mario@server:~$", "In Mario's terminal") + \
    note("confirming once, anywhere, is enough: the dialog closes by itself if Mario answers in the "
         "terminal, and vice versa. If Mario is not logged in, he will find the message at his next login. "
         + ref(8) + " describes everything the users see.", "One confirmation is enough.")

S4 = p("In the list the message shows its recipients in the three states: before Mario logs in "
       "“1 delivered”, after his confirmation “all confirmed (1)”. With "
       + key("Enter") + " you open the message and see the state of every recipient, with date, time and channel "
       "of the confirmation.", lead=True) + term(
    "admin@server:~$ rspeak status 1\n"
    "Message 1 · Maintenance · 01/10 10:49 · from admin\n"
    "  │ " + TEXT + "\n"
    "\n"
    "USER             STATE\n"
    "mario            confirmed on 01/10 10:50 (desktop)",
    "The same, with a command") + \
    table(["If the state is…", "It means", "What to do"], [
        [DELIVERED, "Mario has the copy but has not confirmed yet", "wait, or remind him (" + ref(7, 2) + ")"],
        [CONFIRMED + " (desktop)", "he pressed " + ui("I have read it") + " in the dialog", "nothing: it is done"],
        [CONFIRMED + " (terminal pts/1)", "he answered " + c("y") + " in a terminal window", "nothing: it is done"],
    ], "«TAB» — Reading the result") + \
    tip("the TUI updates itself every 3 seconds: keeping it open on the message, you see the confirmations "
        "arrive one after another.", "And then?")

CHAPTER = ("First steps", [
    ("The path", S1),
    ("Sending the first message", S2),
    ("What the user sees", S3),
    ("Seeing who has read it", S4),
])
