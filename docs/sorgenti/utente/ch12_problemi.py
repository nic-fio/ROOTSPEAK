import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import arrow, box, c, diamond, fig, flow, key, note, p, path, steps, table, term, text, tip, warn  # noqa: E402
from _aiuti import CONFERMATO, CONSEGNATO, INVIATO, rif  # noqa: E402

S1 = p("When a command fails, " + c("ams") + " prints a line in red that starts with " + c("ams:")
       + ", says what to correct and exits with status 1. In the TUI the same line appears in the result "
       "dialog. The messages below are shown as an Italian session prints them; an English session prints the "
       "English text given after each one.", lead=True) + term(
    'admin@server:~$ ams send --to mrio "Riunione alle 11."\n'
    "ams: utente inesistente: mrio", "A typical error") + \
    table(["Message", "What it means", "What to do"], [
        [c("manca --to") + " (“missing --to”)", "no recipient", "add " + c("--to") + " (" + rif(5, 1) + ")"],
        [c("manca il valore di --to") + " (“missing value for --to”)", "an option without its value (the same "
         "applies to " + c("--title") + ", " + c("--expires") + ", " + c("--file") + ")",
         "write the value after the option"],
        [c("utente inesistente: NOME") + " (“no such user”)", "the name is not a user of the machine",
         "check the name"],
        [c("gruppo inesistente: NOME") + " (“no such group”)", "the group after " + c("@") + " does not exist",
         "check the group name"],
        [c("nessun destinatario") + " (“no recipients”)", "the recipients given are empty, for example "
         + c("online") + " when nobody is logged in", "choose other recipients"],
        [c("messaggio vuoto") + " (“empty message”)", "the text is missing, or contains only spaces",
         "write the text"],
        [c("messaggio troppo lungo: N byte (al massimo 65536)") + " (“message too long”)", "the text exceeds 64 KB",
         "shorten it, or put the full text in a shared file and send the message with its path"],
        [c("scadenza non valida: X") + " (“invalid expiry”)", "the expiry was not understood", "use " + c("2h")
         + " or " + c('"2026-10-04 12:00"') + " (" + rif(5, 3) + ")"],
        [c("la scadenza è già passata") + " (“the expiry is already in the past”)", "the date given is in the past",
         "correct the date"],
        [c("opzione sconosciuta: X") + " (“unknown option”)", "misspelt option", c("ams --help")],
        [c("comando sconosciuto: X (ams --help per la guida)") + " (“unknown command”)", "misspelt command",
         c("ams --help")],
        [c("manca l'ID del messaggio") + " (“missing message ID”)", c("status") + ", " + c("revoke") + ", "
         + c("remind") + " or " + c("log") + " without a number", "add the number, taken from " + c("ams list")],
        [c("messaggio inesistente: ID") + " (“no such message”)", "no message with that number (or already "
         "deleted)", "check with " + c("ams list")],
        [c("manca la durata, per esempio 90d") + "<br>" + c("durata non valida: X (per esempio 90d, 12h, 30m)")
         + " (“missing duration”, “invalid duration”)",
         c("ams purge") + " without a duration or with a misspelt duration", "write a number followed by "
         + c("d") + ", " + c("h") + " or " + c("m")],
        [c("il messaggio N è stato ritirato: nessuno da sollecitare") + "<br>" + c("il messaggio N è scaduto: nessuno "
           "da sollecitare") + " (“has been revoked / has expired: nobody to remind”)", "reminder for a message "
         "that is no longer shown", "nothing; to ask again, send a new message"],
        [c("messaggio N non consegnato a: … (vedi il registro; il prossimo comando ams riproverà)")
         + " (“not delivered to”)", "the copy could not be written for those users; the others received it",
         "fix the cause, often a full disk (" + rif(12, 4) + ")"],
        [c("messaggio N ritirato, ma alcune copie non si sono potute togliere dalle caselle: il prossimo comando ams "
           "riproverà") + " (“revoked, but some copies could not be removed”)", "during the revocation a user's "
         "mailbox could not be reached", "nothing: AMS retries"],
        [c("FILE: …"), "with " + c("--file") + ": the file does not exist or cannot be read; the explanation is the "
         "system's own, in English (for example " + c("No such file or directory") + ")", "check the path"],
    ], "«TAB» — The error messages")

S2 = table(["Problem", "Likely cause", "Remedy"], [
    [c("ams: comando non trovato"), "AMS is not installed", "run " + c("./install.sh") + " (" + rif(2, 2) + ")"],
    [c("Permesso negato"), "whoever runs it is not an administrator", "this is intended (" + rif(11, 1) + ")"],
    [c("ams") + " on its own shows the help instead of the TUI", "the terminal is smaller than 80 columns or 20 "
     "rows, or the output is not a terminal", "enlarge the window, or use the commands"],
    ["the TUI closed by itself", "the window was shrunk below 80 × 20", "enlarge it and reopen " + c("ams")],
    ["the text reaches the terminal but the question does not", "the terminal window was open before the "
     "installation; or the shell is sh, dash or ksh (question only at login) or tcsh (no question); "
     "or zsh was installed after AMS", "open a new window or log in again; for zsh installed later, "
     "run " + c("./install.sh") + " again (" + rif(8, 3) + ")"],
    ["AMS appears in English to a user", "their session has no Italian locale (" + c("LANG") + " empty, "
     + c("C") + " or another language)", "set " + c("LANG=it_IT.UTF-8") + " for the user or for the system"],
    ["no dialog appears on the desktop", c("zenity") + " is missing, or the graphical session was "
     "started before the installation and the agent did not start", "install " + c("zenity") + "; the agent "
     "starts by itself with the first new message or at the next login"],
    ["two identical dialogs", "the same message was sent twice (two different numbers in the list)",
     "revoke the duplicate (" + rif(7, 1) + ")"],
    ["a user who logged in with " + c("su") + " does not see the text when it is sent", "with " + c("su")
     + " the terminal window still belongs to whoever opened it", "they still see the question at the next "
     "prompt; with " + c("ssh") + " everything works normally"],
    ["a user sees «Non è stato possibile registrare la conferma» (“The confirmation could not be recorded”)",
     "their mailbox is not writable, for example because the disk is full",
     "free some space: the message is asked again and the confirmation is not lost"],
    ["a recipient stays " + INVIATO, "their copy could not be written", "see " + rif(12, 4)],
    [key("Ctrl", "E") + " opens nano and not my editor", "sudo does not keep " + c("VISUAL") + " and "
     + c("EDITOR"), rif(10, 3)],
    ["a user says they saw nothing", "—", "follow the procedure in " + rif(12, 3)],
], "«TAB» — Frequent problems")

DIAGNOSI = fig(
    diamond(170, 110, 260, 90, "What state is it?", "navy")
    + box(360, 40, 240, 54, "sent", "the copy did not arrive: 12.4", "grey")
    + box(360, 118, 240, 54, "delivered", "has the copy, has not confirmed", "amber")
    + box(360, 196, 240, 54, "confirmed", "stated they have read it", "green")
    + box(650, 118, 230, 54, "Logged in? Postponing?", "message details and history", "blue")
    + box(650, 196, 230, 54, "From where, and when", "desktop or terminal, with the time", "blue")
    + path([(210, 80), (210, 67), (356, 67)], "#475569")
    + arrow(300, 110, 356, 140, "#475569")
    + path([(210, 140), (210, 223), (356, 223)], "#475569")
    + arrow(602, 145, 646, 145, "#0050C0") + arrow(602, 223, 646, 223, "#0050C0")
    + text(450, 290, "The starting point is always the message details (Enter in the TUI, or ams status)",
           11.5, "#334155", "600"),
    900, 310, "«FIG» — Where to start when a user says they did not see a message", "The diagnosis")

S3 = p("It is the most common question. The answer is almost always in the message details and in its history.",
       lead=True) + DIAGNOSI + steps([
        "Open the message in the TUI (" + key("Enter") + ") or run " + c("ams status ID") + ", and find "
        "the user's line.",
        "If it is " + CONFERMATO + ", the line says when and from where: for example «confermato il 30/09 16:56 "
        "(desktop)» (“confirmed on …” in English). The user has confirmed, perhaps without reading carefully ("
        + rif(11, 3) + ").",
        "If it is " + CONSEGNATO + ", look at the details: «scritto su 2 terminali» (“written to 2 terminals”) "
        "means that the text appeared on their screens; «rimandato il …» (“postponed on …”) that they saw the "
        "question or the dialog and postponed it. If neither is there, they have probably not logged in yet.",
        "If it is " + INVIATO + ", the copy did not reach their mailbox: see " + rif(12, 4) + ".",
        "In the " + key("Tab") + " " + "«Storia» tab (“History” in English), or with " + c("ams log ID")
        + ", you find all the events, postponements included, to the second.",
        "If needed, remind them (" + rif(7, 2) + "): the dialog comes back on their desktop at once.",
    ]) + tip("a user who works only through ssh and with a shell such as tcsh does not get the question in the "
             "terminal: they see the text when it is sent, but can confirm only from the desktop. With bash, zsh "
             "or fish the problem does not arise.",
             "Unusual shells.")

RECUPERO = flow([("Sending interrupted", "full disk, power cut…", "grey"), ("Next ams", "list, status, TUI…", "navy"),
                 ("Recovery", "rewrites the missing copies", "blue"), ("All delivered", "or a notice of who is missing", "green")],
                "«FIG» — AMS completes the deliveries left behind by itself", "Recovery")

S4 = p("If a sending is interrupted halfway (the disk fills up, " + c("ams") + " is stopped, the power goes) "
       "AMS does not lose the message: the next time it is used, it resumes from where it stopped.", lead=True) + \
    RECUPERO + \
    table(["Notice", "What it means", "What to do"], [
        [c("ams: completata la consegna del messaggio N a K destinatari") + " (“completed delivery of message N to "
         "K recipients”)", "the missing copies have been written: those recipients are now " + CONSEGNATO,
         "nothing"],
        [c("ams: messaggio N ancora non consegnato a K destinatari (vedi ams status N)") + " (“still not "
         "delivered”)", "for someone the copy still cannot be written", "fix the cause, usually disk space; then "
         "use " + c("ams") + " again"],
        [c("ams: il messaggio N era stato interrotto prima di essere salvato ed è stato annullato") + " (“was "
         "interrupted before being saved and has been cancelled”)", "the sending stopped before the message was "
         "even saved: nobody received it", "send it again"],
        [c("[invio annullato: interrotto prima del salvataggio]") + " in " + c("ams list"), "the same case, "
         "in the list (“[send cancelled: interrupted before it was saved]”)", "send it again"],
    ], "«TAB» — The recovery notices") + \
    note("recovery starts at the beginning of " + c("ams send") + ", " + c("list") + ", " + c("status") + ", "
         + c("revoke") + ", " + c("remind") + ", " + c("log") + " and when the TUI opens. Nothing is needed "
         "other than using AMS.", "When it starts.") + \
    warn("with a full disk the users' confirmations cannot be saved either: users see «Non è stato "
         "possibile registrare la conferma» (“The confirmation could not be recorded”) and the message is asked "
         "again. Freeing space in " + c("/var/lib") + " solves both.", "Full disk.")

S5 = table(["What", "Where"], [
    ["the command", c("/usr/local/bin/ams")],
    ["the settings", c("/etc/ams/ams.conf")],
    ["messages and confirmations", c("/var/lib/ams/")],
    ["the log", c("sudo journalctl -t ams")],
    ["the help", c("ams --help")],
    ["the manuals", c("/usr/local/share/doc/ams/User Manual.html") + " and " + c("Technical Manual.html")],
    ["the shell hooks", c("/etc/profile.d/ams.sh") + ", " + c("/usr/local/lib/ams/ams.bash") + ", "
     + c("ams.zsh") + ", " + c("/etc/fish/conf.d/ams.fish")],
    ["the desktop autostart", c("/etc/xdg/autostart/ams-agent.desktop")],
    ["the code", c("https://github.com/nic-fio/AMS") + " (private)"],
], "«TAB» — Where to find things") + \
    tip("when something does not add up, the places to look are, in order: the message details, its history, "
        "the log with " + c("sudo journalctl -t ams") + ", and the built-in help.", "Where to look.")

CHAPTER = ("Troubleshooting", [
    ("Error messages", S1),
    ("Frequent problems", S2),
    ("“I didn't see any message”", S3),
    ("Interrupted sendings", S4),
    ("Useful files and folders", S5),
])
