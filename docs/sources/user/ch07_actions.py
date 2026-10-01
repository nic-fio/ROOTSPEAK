import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import c, key, note, p, schermata, seq, steps, table, term, tip, ui, ul, warn  # noqa: E402
from _helpers import CONFERMATO, CONSEGNATO, INVIATO, RITIRATO, SCADUTO, rif, schermata_u  # noqa: E402

RITIRO = seq([("Administrator", "r key or rspeak revoke", "dark"), ("RootSpeak", "message store", "navy"),
              ("Anna", "dialog open", "blue"), ("Luca", "not logged in yet", "light")], [
    (0, 1, "revokes message 4"),
    (1, 1, "marks the message as revoked"),
    (1, 3, "removes the copy from Luca's mailbox"),
    (1, 2, "removes the copy; the dialog closes by itself", True),
    (1, 0, "«Messaggio 4 ritirato.»", True),
    ("sep", "later".ljust(9)),
    (3, 1, "Luca logs in: sees nothing"),
], "«FIG» — What happens when a message is revoked; the reply «Messaggio 4 ritirato.» means “Message 4 revoked.”",
   "Revocation")

S1 = p("A message sent by mistake, or no longer valid, is <b>revoked</b>: in the TUI with " + key("r") + " on the "
       "selected message (in the list or in the open message), from the command line with " + c("rspeak revoke") + ". "
       "Before revoking, the TUI always asks for confirmation.", lead=True) + \
    schermata_u("revoke", "«FIG» — The revocation confirmation: title and recipients in the three states") + \
    term("admin@server:~$ rspeak revoke 4\nMessaggio 4 ritirato.", "With a command: “Message 4 revoked.”") + RITIRO + \
    table(["Who", "What happens"], [
        ["whoever has not seen it yet (not logged in)", "will never see it: the copy disappears from their mailbox"],
        ["whoever has a confirmation dialog open", "the dialog closes by itself within a second"],
        ["whoever has the question in the terminal", "the question is interrupted with «[RootSpeak] L'amministratore ha "
         "ritirato il messaggio.» (“[RootSpeak] The administrator has revoked the message.”)"],
        ["whoever had already confirmed", "stays " + CONFERMATO + ": confirmations already received count"],
        ["whoever confirms after the revocation", "the confirmation does not count: stays " + CONSEGNATO
         + ", «non confermato (ritirato)» (“not confirmed (revoked)”)"],
        ["the administrator", "in the list the message has " + c("[ritirato]") + " (“[revoked]”) in front; " + c("rspeak status")
         + " writes «RITIRATO il …» (“REVOKED on …”)"],
    ], "«TAB» — The effects of revocation") + \
    warn("the text that already appeared in the terminals when the message was sent cannot be erased: it is already "
         "on the user's screen. Revocation only stops the confirmation requests and the dialogs.",
         "Text already written stays.") + \
    note("if the message is still being sent to many recipients, the revocation waits a moment and stops the "
         "delivery at the next recipient; whoever already has the copy loses it. If some mailbox cannot be "
         "reached, RootSpeak says so («alcune copie non si sono potute togliere dalle caselle», “some copies could not be "
         "removed from the mailboxes”) and retries by itself.",
         "Revocation during sending.")

S2 = p("Whoever postponed sees the message again after 30 minutes. If it is needed sooner, send a <b>reminder</b>: in "
       "the TUI with " + key("s") + ", from the command line with " + c("rspeak remind") + ". The question comes back at the "
       "next prompt and the dialog reappears at once on the desktop, even if the user had just postponed it.",
       lead=True) + \
    schermata("reminder", "«FIG» — The reminder confirmation, with how many people it concerns") + \
    term("admin@server:~$ rspeak remind 2\nMessaggio 2: sollecitati 3 destinatari.",
         "With a command: “Message 2: 3 recipients reminded.”") + \
    table(["Recipient", "Reminded?"], [
        [CONSEGNATO + " (has the copy, has not confirmed)", "yes: question at the next prompt, dialog at once"],
        [CONFERMATO, "no: not disturbed"],
        [INVIATO, "no: does not have the copy yet; RootSpeak retries the delivery by itself"],
    ], "«TAB» — Who receives the reminder") + ul([
        "A " + RITIRATO + " or " + SCADUTO + " message cannot be reminded: the command replies «il messaggio 4 è "
        "stato ritirato: nessuno da sollecitare» (“message 4 has been revoked: nobody to remind”) or «… è scaduto: "
        "nessuno da sollecitare» (“… has expired: nobody to remind”).",
        "The reminder is recorded in the message's history and in the log, together with who asked for it.",
        "For users who are not logged in, a reminder changes nothing: they will see the message at their next login "
        "anyway.",
    ]) + tip("an occasional reminder works better than many: people who get the dialog in front of them every five "
             "minutes tend to confirm without reading.", "In moderation.")

S3 = p("Messages and confirmations stay in the message store until they are deleted. <b>Purging</b> removes the "
       "messages sent more than a certain time ago, together with the copies and confirmations in the users' "
       "mailboxes.", lead=True) + \
    steps([
        "In the list press " + key("p") + ": " + ui("Cancellare i messaggi vecchi") + " (“Delete old messages”) opens, "
        "with " + c("90d") + " already filled in.",
        "Change the duration if needed (" + c("90d") + " days, " + c("12h") + " hours, " + c("30m") + " minutes) and "
        "press " + key("Enter") + ".",
        "Read the summary " + ui("Cancellare i messaggi vecchi?") + " (“Delete old messages?”) and confirm with "
        + key("s") + " (or y).",
        "The next dialog shows the reply from RootSpeak, for example «Cancellati 12 messaggi più vecchi di 90d.» (“Deleted "
        "12 messages older than 90d.”).",
    ]) + schermata_u("purge", "«FIG» — The duration prompt") + \
    term("admin@server:~$ rspeak purge 90d\nCancellati 12 messaggi più vecchi di 90d.",
         "With a command: “Deleted 12 messages older than 90d.”") + ul([
        "A deleted message disappears from the list and from " + c("rspeak status") + "; if someone had not confirmed "
        "it yet, they will no longer be asked.",
        "A sending still in progress is not touched.",
        "The system log keeps the events of the message and that of the deletion "
        "(«messaggio 1 cancellato da admin (più vecchio di 90d)», “message 1 deleted by admin (older than 90d)”).",
        "Message numbers are not reused: the next message takes the number after the last one.",
    ]) + warn("deletion cannot be undone. If you need to keep the list of confirmations, first save the output of "
              + c("rspeak status") + " for the messages you care about.", "Final.")

S4 = p("Not every action makes sense on every message. When a key has no effect, the TUI simply does "
       "nothing; the commands, instead, reply with an error.", lead=True) + \
    table(["Action", "Not possible when…", "Command reply"], [
        [key("r") + " / " + c("rspeak revoke"), "the message is already revoked", "no error: «Messaggio 4 ritirato.» "
         "(“Message 4 revoked.”)"],
        [key("s") + " / " + c("rspeak remind"), "the message is revoked", c("rspeak: il messaggio 4 è stato ritirato: nessuno da sollecitare")
         + " (“rspeak: message 4 has been revoked: nobody to remind”)"],
        [key("s") + " / " + c("rspeak remind"), "the message has expired", c("rspeak: il messaggio 4 è scaduto: nessuno da sollecitare")
         + " (“rspeak: message 4 has expired: nobody to remind”)"],
        [key("s") + " / " + c("rspeak remind"), "nobody is " + CONSEGNATO, "nothing in the TUI; the command replies "
         "«sollecitati 0 destinatari» (“0 recipients reminded”)"],
        [key("Enter") + " / " + c("rspeak status"), "the number does not exist", c("rspeak: messaggio inesistente: 99")
         + " (“rspeak: no such message: 99”)"],
        [key("p") + " / " + c("rspeak purge"), "the duration is badly written", c("rspeak: durata non valida: 3 (per esempio 90d, 12h, 30m)")
         + " (“rspeak: invalid duration: 3 (for example 90d, 12h, 30m)”)"],
    ], "«TAB» — When an action cannot be carried out") + \
    note("no TUI action starts without a confirmation: the message to revoke, the people to remind and the messages "
         "to delete are always shown first. " + key("n") + " or " + key("Esc") + " cancel.",
         "Always a confirmation.") + \
    p("All these actions are reserved to administrators and are recorded in the log under their name: for " + c("rspeak")
      + " the author is whoever used sudo, not root (" + rif(11, 1) + ").")

CHAPTER = ("Revoking, reminding, cleaning up", [
    ("Revoking a message", S1),
    ("Reminding those who have not confirmed", S2),
    ("Deleting old messages", S3),
    ("When an action cannot be carried out", S4),
])
