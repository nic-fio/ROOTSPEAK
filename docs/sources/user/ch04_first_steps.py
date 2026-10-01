import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import c, dialog, flow, key, note, p, steps, table, term, tip, ui  # noqa: E402
from _helpers import CONFERMATO, CONSEGNATO, rif  # noqa: E402

S1 = p("This path leads from a freshly installed RootSpeak to the first confirmation, in four stages. The recipient of "
       "the first message can be the administrator themselves: that way you see with your own eyes what the users "
       "receive. Each stage refers to the chapter that explains it in detail.", lead=True) + \
    flow([("1. Install", "make, ./install.sh", "dark"), ("2. Write and send", "rspeak, key n", "blue"),
          ("3. The user confirms", "dialog or terminal", "blue"), ("4. Check", "Enter on the message", "green")],
         "«FIG» — The four stages of the first steps", "From nothing to the first confirmation") + \
    table(["Stage", "What you do", "Chapter"], [
        ["1", "Install RootSpeak and check that it answers", rif(2)],
        ["2", "Write the message in the TUI (or with " + c("rspeak send") + ") and send it", rif(5)],
        ["3", "The recipient sees the dialog or the question and confirms", rif(8)],
        ["4", "Open the message and see who has confirmed", rif(6)],
    ], "«TAB» — The path")

S2 = p("The simplest way is the TUI. Here the message goes to Mario; to try it on yourself, just type your own "
       "name.", lead=True) + steps([
        "Open a terminal and type " + c("rspeak") + ". When prompted, enter your password: " + c("rspeak")
        + " always asks for it, because it works as administrator («password di admin»: “admin's password”)." + term(
            "admin@server:~$ rspeak\n[sudo] password di admin:"),
        "In the list of messages press " + key("n") + ": the " + ui("Nuovo messaggio") + " (“New message”) screen opens.",
        "In the " + ui("A") + " (“To”) field type " + c("mario") + " and press " + key("Tab") + ": on the right "
        + ui("1 destinatario") + " (“1 recipient”) appears.",
        "In the " + ui("Titolo") + " (“Title”) field type " + c("Manutenzione") + "; leave " + ui("Scadenza")
        + " (“Expires”) empty and move to " + ui("Testo") + " (“Text”) with " + key("Tab") + ".",
        "Type the text: " + c("Sabato dalle 8 alle 12 il server sarà spento.") + " (“On Saturday from 8 to 12 the "
        "server will be switched off.”) Start a new line with "
        + key("Enter") + ".",
        "Press " + key("Ctrl", "S") + ". The summary " + ui("Inviare il messaggio?") + " (“Send the message?”) "
        "appears: press " + key("s") + " to confirm.",
        "The " + ui("Messaggio inviato") + " (“Message sent”) window reports the answer of RootSpeak, for example «Messaggio "
        "1 inviato a 1 utente.» (“Message 1 sent to 1 user.”). Any key takes you back to the list, where the message "
        "is at the top.",
    ]) + p("The same message, with a single command (same text, same reply: “Message 1 sent to 1 user.”):") + term(
        'admin@server:~$ rspeak send --to mario --title Manutenzione "Sabato dalle 8 alle 12 il server sarà spento."\n'
        "Messaggio 1 inviato a 1 utente.") + \
    tip("the message number (here " + c("1") + ") is needed for the commands " + c("status") + ", " + c("log") + ", "
        + c("revoke") + " and " + c("remind") + ". In the TUI it is not needed: you pick the message from the list.",
        "The number.")

S3 = p("If Mario is logged in, the message reaches him at once, in all his sessions. On the desktop this "
       "dialog appears, above the other windows:", lead=True) + \
    dialog("RootSpeak · Messaggio dall'amministratore", "Manutenzione · 30/09 16:55",
           "Sabato dalle 8 alle 12 il server sarà spento.",
           "«FIG» — The confirmation dialog on Mario's desktop: «RootSpeak · Messaggio dall'amministratore» (“RootSpeak · Message "
           "from the administrator”), the title and the text, and the buttons «Più tardi» (“Later”) and «Ho letto» "
           "(“I have read it”)") + \
    p("In terminal windows the text appears at once, under the heading «RootSpeak · Messaggio dall'amministratore» (“RootSpeak · "
      "Message from the administrator”); at the next prompt RootSpeak asks for the confirmation, «[RootSpeak] Confermi di aver letto "
      "il messaggio? [s/N]» (“[RootSpeak] Do you confirm you have read the message? [y/N]”), and after the answer «s» "
      "(“y”) replies «[RootSpeak] Confermato.» (“[RootSpeak] Confirmed.”):") + term(
        "── RootSpeak · Messaggio dall'amministratore · Manutenzione · 30/09 16:55 ──\n"
        "Sabato dalle 8 alle 12 il server sarà spento.\n"
        "────────────────────────────────────────\n"
        "[RootSpeak] Confermi di aver letto il messaggio? [s/N] s\n"
        "[RootSpeak] Confermato.\n"
        "mario@server:~$", "In Mario's terminal") + \
    note("confirming once, anywhere, is enough: the dialog closes by itself if Mario answers in the "
         "terminal, and vice versa. If Mario is not logged in, he will find the message at his next login. "
         + rif(8) + " describes everything the users see.", "One confirmation is enough.")

S4 = p("In the list the message shows its recipients in the three states: before Mario logs in "
       "«1 consegnato» (“1 delivered”), after his confirmation «tutti confermato (1)» (“all confirmed (1)”). With "
       + key("Enter") + " you open the message and see the state of every recipient, with date, time and channel "
       "of the confirmation.", lead=True) + term(
    "admin@server:~$ rspeak status 1\n"
    "Messaggio 1 · Manutenzione · 30/09 16:55 · da admin\n"
    "  │ Sabato dalle 8 alle 12 il server sarà spento.\n"
    "\n"
    "UTENTE           STATO\n"
    "mario            confermato il 30/09 16:56 (desktop)",
    "The same, with a command: «da admin» (“from admin”), UTENTE (USER), STATO (STATE), «confermato il 30/09 16:56 "
    "(desktop)» (“confirmed on 30/09 16:56 (desktop)”)") + \
    table(["If the state is…", "It means", "What to do"], [
        [CONSEGNATO, "Mario has the copy but has not confirmed yet", "wait, or remind him (" + rif(7, 2) + ")"],
        [CONFERMATO + " (desktop)", "he pressed " + ui("Ho letto") + " (“I have read it”) in the dialog", "nothing: it is done"],
        [CONFERMATO + " (terminal pts/1)", "he answered " + c("s") + " in a terminal window", "nothing: it is done"],
    ], "«TAB» — Reading the result") + \
    tip("the TUI updates itself every 3 seconds: keeping it open on the message, you see the confirmations "
        "arrive one after another.", "And then?")

CHAPTER = ("First steps", [
    ("The path", S1),
    ("Sending the first message", S2),
    ("What the user sees", S3),
    ("Seeing who has read it", S4),
])
