import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import (arrow, box, c, dialog, fig, key, note, notification, p, seq, table, term, text, tip, ui,  # noqa: E402
                   ul, warn)
from _helpers import CONFERMATO, CONSEGNATO, rif  # noqa: E402

S1 = p("On the desktop the message appears by itself, on top of the other windows, a few moments after it is sent. "
       "The user does not have to do anything to receive it: at graphical login a small AMS program starts, the "
       "<b>desktop agent</b>, which waits for messages.", lead=True) + \
    dialog("AMS · Messaggio dall'amministratore", "Manutenzione · 30/09 16:55",
           "Sabato dalle 8 alle 12 il server sarà spento per la manutenzione dei dischi.",
           "«FIG» — The confirmation dialog (on GNOME; its look follows the desktop theme): «AMS · Messaggio "
           "dall'amministratore» (“AMS · Message from the administrator”), «Manutenzione» (“Maintenance”), «Sabato "
           "dalle 8 alle 12 il server sarà spento per la manutenzione dei dischi.» (“On Saturday from 8 to 12 the "
           "server will be switched off for disk maintenance.”), buttons «Più tardi» (“Later”) and «Ho letto» (“I have "
           "read it”)") + \
    table(["The user…", "What happens"], [
        ["presses " + ui("Ho letto") + " (\"I have read it\" on an English desktop)", "The message is " + CONFERMATO
         + " and never appears again, in any session."],
        ["presses " + ui("Più tardi") + " (\"Later\") or closes the dialog", "The message is postponed: the dialog "
         "comes back after 30 minutes, until the user confirms."],
        ["does nothing", "The dialog stays there without blocking anything: the user can keep working in the other "
         "windows."],
        ["logs out", "The dialog closes; the message appears again at the next login."],
    ], "«TAB» — What the user can do with the dialog") + \
    ul([
        "The top of the dialog shows the message title and the date it was sent; if the message has no title, "
        "only the date.",
        "If there are several messages, the dialogs appear one at a time, from the oldest to the most recent.",
        "The dialog closes by itself if the user confirms from a terminal, if the administrator revokes the message "
        "or if the message expires.",
    ]) + \
    notification("AMS · Conferma non registrata",
                 "Non è stato possibile registrare la conferma: il messaggio verrà riproposto.",
                 "«FIG» — The rare notice of a confirmation that could not be saved: «AMS · Conferma non registrata» "
                 "(“AMS · Confirmation not recorded”), «Non è stato possibile registrare la conferma: il messaggio verrà "
                 "riproposto.» (“The confirmation could not be recorded: the message will be shown again.”)") + \
    note("if the confirmation cannot be saved (for example because the disk is full), the desktop shows the notice "
         "above (\"AMS · Confirmation not recorded\" on an English desktop) and the message is asked again: the "
         "confirmation is never lost silently. The notice requires " + c("notify-send")
         + ".", "Confirmation not recorded.")

S2 = p("In every terminal window of the user, whether local, inside the desktop, in tmux or connected through ssh, "
       "the text appears the moment the message is sent, even while the user is working:", lead=True) + term(
    "mario@server:~/progetti$ make\n"
    "gcc -O2 -c main.c\n"
    "\n"
    "── AMS · Messaggio dall'amministratore · Manutenzione · 30/09 16:55 ──\n"
    "Sabato dalle 8 alle 12 il server sarà spento.\n"
    "────────────────────────────────────────\n"
    "gcc -O2 -o prova main.o",
    "When the message is sent: «AMS · Messaggio dall'amministratore» (“AMS · Message from the administrator”), then "
    "title, date and text («Sabato dalle 8 alle 12 il server sarà spento.», “On Saturday from 8 to 12 the server will be "
    "switched off.”)") + \
    p("As soon as the user is back at the prompt (if already at the prompt, just press " + key("Enter") + "), AMS "
      "shows the message again and asks for confirmation:") + \
    term("── AMS · Messaggio dall'amministratore · Manutenzione · 30/09 16:55 ──\n"
         "Sabato dalle 8 alle 12 il server sarà spento.\n"
         "────────────────────────────────────────\n"
         "[AMS] Confermi di aver letto il messaggio? [s/N] s\n"
         "[AMS] Confermato.\n"
         "mario@server:~/progetti$",
         "At the next prompt: «[AMS] Confermi di aver letto il messaggio? [s/N]» (“[AMS] Do you confirm you have read "
         "the message? [y/N]”)") + \
    table(["The user answers", "What happens"], [
        [key("s") + " (or " + key("y") + ") and " + key("Enter"), "«[AMS] Confermato.» (in English: “[AMS] "
         "Confirmed.”): the message is confirmed everywhere."],
        ["anything else, even just " + key("Enter"), "«[AMS] La domanda verrà riproposta tra 30 minuti.» (in "
         "English: “[AMS] You will be asked again in 30 minutes.”)"],
        ["nothing, because they confirmed on the desktop", "«[AMS] Messaggio già confermato altrove (per esempio dal "
         "desktop).» (in English: “[AMS] Message already confirmed elsewhere (for example on the desktop).”): the "
         "question closes by itself"],
        ["nothing, and the message is revoked", "«[AMS] L'amministratore ha ritirato il messaggio.» (in English: "
         "“[AMS] The administrator has revoked the message.”)"],
        ["nothing, and the message expires", "«[AMS] Il messaggio è scaduto.» (in English: “[AMS] The message has "
         "expired.”)"],
    ], "«TAB» — The answers to the question") + \
    p("After a postponement, until the next question, only a one-line reminder appears at each prompt:") + \
    term("[AMS] Confermi di aver letto il messaggio? [s/N] n\n"
         "[AMS] La domanda verrà riproposta tra 30 minuti.\n"
         "mario@server:~/progetti$ ls\n"
         "main.c  main.o  prova\n"
         "[AMS] Hai 1 messaggio dell'amministratore da confermare.\n"
         "mario@server:~/progetti$",
         "If the user postpones: «[AMS] Hai 1 messaggio dell'amministratore da confermare.» (“[AMS] You have 1 message "
         "from the administrator to confirm.”)") + \
    note("if the user is running a full-screen program, such as an editor, the text sent to the terminal is drawn "
         "over the screen, as happens with " + c("wall") + ". Nothing is lost: the screen fixes itself, or with "
         + key("Ctrl", "L") + ", and the question only comes when the user leaves the program.",
         "Full-screen programs.")

S3 = p("The confirmation question in the terminal depends on the user's shell. The text shown when the message is "
       "sent, instead, always arrives, whatever the shell.", lead=True) + \
    table(["Shell", "Text when sent", "Confirmation question"], [
        ["bash", "yes", "at every prompt; at login also if it had been postponed"],
        ["zsh", "yes", "at every prompt; at login also if it had been postponed"],
        ["fish", "yes", "at every prompt; at login also if it had been postponed"],
        ["sh, dash, ksh and the others that read " + c("/etc/profile"), "yes", "only at login"],
        ["tcsh, csh and the shells that do not read " + c("/etc/profile"), "yes", "no (the dialog remains, if the "
         "user has a desktop)"],
    ], "«TAB» — Shells and the confirmation question") + \
    ul([
        "The question only appears in <b>interactive</b> shells: scripts, cron, " + c("scp") + ", " + c("rsync")
        + " and commands run with " + c("ssh server comando") + " (comando: “command”) never see it.",
        "Terminal windows already open when AMS is installed receive the text, but the question only from the next "
        "window or the next login.",
        "If zsh is installed after AMS, re-running " + c("./install.sh") + " is enough to get the question in zsh; "
        "fish, instead, gets it even if installed later.",
    ]) + warn("with " + c("su - mario") + " the terminal window still belongs to whoever opened it: the text sent "
              "with the message does not appear, the question at the prompt does. With " + c("ssh mario@server")
              + " everything works normally.",
              "Logins with su.")

FUORI = seq([("Administrator", "sends", "dark"), ("AMS", "Luca's mailbox", "navy"), ("Luca", "not logged in", "light")], [
    (0, 1, "message for luca"),
    (1, 1, "Luca is not logged in: the message waits"),
    ("sep", "the next day, Luca logs in".ljust(27)),
    (2, 1, "login (desktop, console or ssh)"),
    (1, 2, "dialog, or text and question"),
    (2, 1, "“Ho letto” or “s”"),
    (1, 0, "in the list: tutti confermato", True),
], "«FIG» — A message for someone who is not logged in; “Ho letto” is “I have read it”, “s” is “y”, and «tutti "
   "confermato» is “all confirmed”", "Delivery at the next login")

S4 = p("Users who are not logged in find the message at their next login, however they log in. Meanwhile it is "
       "already " + CONSEGNATO + ": the copy is in their mailbox, waiting for them.", lead=True) + FUORI + \
    table(["Login", "What the user sees"], [
        ["desktop", "the dialog, as soon as the session opens"],
        ["console or ssh", "text and question right after login, before the first prompt; at login the question "
         "is asked even if the user had postponed it"],
        ["a command over ssh, " + c("scp") + ", a service", "nothing: it is not an interactive login"],
    ], "«TAB» — The message at the next login")

UNA = seq([("Anna's desktop", "dialog", "blue"), ("AMS", "", "navy"), ("Anna's terminal", "ssh", "blue")], [
    (1, 0, "dialog “Ho letto” / “Più tardi”"),
    (1, 2, "text and question “Confermi?”"),
    (0, 1, "Anna presses “Ho letto”"),
    (1, 1, "records the first confirmation"),
    (1, 2, "“Messaggio già confermato altrove”", True),
], "«FIG» — The first confirmation closes all the other requests: the dialog “Ho letto” / “Più tardi” (“I have read it” "
   "/ “Later”), the question “Confermi?” (“Do you confirm?”) and, after the confirmation on the desktop, “Messaggio già "
   "confermato altrove” (“Message already confirmed elsewhere”) in the terminal",
   "One confirmation is valid for all sessions")

S5 = p("A user with several open sessions, for example the desktop and two ssh connections, receives the message in "
       "all of them. Confirming once is enough.", lead=True) + UNA + \
    p("The dialog closes by itself if the user confirms from a terminal, and the question in the terminal closes if "
      "the user confirms on the desktop. The message status keeps the first confirmation, with the channel it came "
      "from: " + c("desktop") + " or " + c("terminale pts/2") + " (“terminal pts/2”).") + \
    note("postponing, instead, applies to the channel where it is done: a user who presses “Più tardi” (“Later”) on "
         "the desktop still sees the question in the terminal, and vice versa.", "Separate postponements.")

TEMPI = fig(
    '<line x1="60" y1="150" x2="860" y2="150" stroke="#94a3b8" stroke-width="2"/>'
    + "".join(f'<line x1="{x}" y1="144" x2="{x}" y2="156" stroke="#94a3b8" stroke-width="2"/>'
              + text(x, 176, t, 11.5, "#475569", "600") for x, t in
              [(80, "16:55"), (260, "16:57"), (460, "17:27"), (640, "17:30"), (820, "17:31")])
    + box(20, 60, 120, 54, "Send", "ams send", "dark")
    + box(200, 60, 120, 54, "Più tardi", "postponed", "amber")
    + box(400, 60, 120, 54, "Back again", "postpones again", "amber")
    + box(580, 60, 120, 54, "Reminder", "ams remind", "blue")
    + box(760, 60, 120, 54, "Ho letto ✓", "confirmed", "green")
    + arrow(80, 116, 80, 144, "#475569") + arrow(260, 116, 260, 144, "#475569") + arrow(460, 116, 460, 144, "#475569")
    + arrow(640, 116, 640, 144, "#475569") + arrow(820, 116, 820, 144, "#475569")
    + text(360, 212, "30 minutes", 11.5, "#92400e", "700")
    + '<path d="M262 196 h196" stroke="#d97706" stroke-width="2" stroke-dasharray="4 3"/>'
    + text(550, 230, "a reminder does not wait: the dialog comes back at once", 11.5, "#1e40af", "600"),
    900, 250, "«FIG» — A message postponed, asked again, reminded and finally confirmed; «Più tardi» is the “Later” "
    "button and «Ho letto» the “I have read it” button", "Postponements and reminders")

S6 = p("AMS never blocks work: the user can always postpone. But whoever postpones is asked again, at regular "
       "intervals, until they confirm.", lead=True) + TEMPI + \
    table(["When", "In the terminal", "On the desktop"], [
        ["after a postponement", "a one-line reminder at each prompt", "no dialog"],
        ["after 30 minutes", "text and question at the next prompt", "the dialog comes back (within a minute)"],
        ["at login", "text and question at once, even if the user had postponed", "the dialog when the session opens"],
        ["after a reminder", "text and question at the next prompt", "the dialog at once"],
        ["on expiry or revocation", "nothing more", "nothing more"],
    ], "«TAB» — When the message comes back") + \
    p("The 30-minute interval is the same for the dialog and for the terminal and can be changed in the settings ("
      + rif(10) + "). Meanwhile the administrator sees in the message details who postponed and when.")

S7 = p("Everyone sees AMS in their own language: dialog, buttons, header, question and notices follow the language "
       "of the user's session. The <b>message text</b> arrives as it was written: it is not translated.", lead=True) + \
    term("── AMS · Message from the administrator · Manutenzione · 30/09 16:55 ──\n"
         "Sabato dalle 8 alle 12 il server sarà spento.\n"
         "────────────────────────────────────────\n"
         "[AMS] Do you confirm you have read the message? [y/N] y\n"
         "[AMS] Confirmed.", "The same message for a user who works in English: the title «Manutenzione» "
         "(“Maintenance”) and the text «Sabato dalle 8 alle 12 il server sarà spento.» (“On Saturday from 8 to 12 the "
         "server will be switched off.”) stay as they were written") + \
    table(["Session language (" + c("LANG") + ", " + c("LC_MESSAGES") + ", " + c("LC_ALL") + ", "
           + c("LANGUAGE") + ")", "AMS appears in"], [
        ["Italian, for example " + c("LANG=it_IT.UTF-8"), "Italian"],
        ["English, or a language AMS does not have yet", "English"],
        [c("C") + " or " + c("POSIX") + ", or no language", "English"],
    ], "«TAB» — The languages of AMS") + ul([
        "The question accepts " + key("s") + " and " + key("y") + " in every language.",
        "The text written to terminals when the message is sent uses the language of that terminal's shell; if it "
        "cannot be determined, the machine's language.",
        c("ams") + " and the TUI speak the language of the administrator using them.",
        "The system log is in the machine's language; " + c("ams log") + " and the TUI rewrite it in the language "
        "of the reader.",
    ]) + dialog("AMS · Message from the administrator", "Manutenzione · 30/09 16:55",
                "Sabato dalle 8 alle 12 il server sarà spento.",
                "«FIG» — The dialog for a user working in English: buttons “I have read it” and “Later”; title and text "
                "stay in Italian, as written («Manutenzione», “Maintenance”)").replace(
        "<span>Più tardi</span><span>Ho letto</span>", "<span>Later</span><span>I have read it</span>")

S8 = p("Users have no AMS commands and do not need to learn anything. It can still help to answer a few "
       "questions: the table collects the most common ones, with short, accurate answers to pass on as they are.",
       lead=True) + \
    table(["The user's question", "Answer"], [
        ["“What is this window?”", "A message from the administrators of the machine. “I have read it” (“Ho "
         "letto”) confirms you have read it; “Later” (“Più tardi”) postpones it by half an hour."],
        ["“Does anything happen if I press Later?”", "No, you can keep working. The message comes back after 30 "
         "minutes until you confirm."],
        ["“Do I have to confirm in the terminal too?”", "No: one confirmation is valid everywhere. The question in "
         "the terminal closes by itself."],
        ["“Can I read a message again after confirming it?”", "No: after the confirmation it does not appear again. "
         "If needed, ask the administrator."],
        ["“Can I reply?”", "No: AMS is only for notices from the administrators. To reply, use the usual "
         "channels."],
        ["“Can other people see my messages?”", "No: everyone sees only the messages sent to them."],
        ["“Why is it in English?”", "The session does not have the Italian language set (" + rif(12, 2) + ")."],
    ], "«TAB» — Users' questions") + \
    tip("for an important notice it is worth telling users, with the first message, what the dialog and the "
        "question are: the first message can explain AMS itself.", "The first message.")

CHAPTER = ("What users see", [
    ("On the desktop", S1),
    ("In the terminal", S2),
    ("Shells", S3),
    ("Users who are not logged in", S4),
    ("Several sessions, one confirmation", S5),
    ("Postponing and reminders", S6),
    ("In which language", S7),
    ("Explaining AMS to users", S8),
])
