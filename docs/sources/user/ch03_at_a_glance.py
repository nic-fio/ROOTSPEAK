import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import arrow, box, c, fig, key, note, p, path, schermata, table, text, tip, ul, zone  # noqa: E402
from _helpers import CONFERMATO, CONSEGNATO, INVIATO, RITIRATO, SCADUTO, barra, mono, numero, rif, riquadro, schermata_u  # noqa: E402

DUE_MODI = fig(
    zone(20, 44, 400, 250, "In the TUI: ams, on its own")
    + zone(480, 44, 400, 250, "With commands: ams COMMAND")
    + box(44, 80, 170, 42, "n", "write and send", "blue")
    + box(226, 80, 170, 42, "Enter", "recipients and history", "blue")
    + box(44, 134, 170, 42, "r", "revoke", "blue")
    + box(226, 134, 170, 42, "s", "remind", "blue")
    + box(44, 188, 170, 42, "p", "purge", "blue")
    + box(226, 188, 170, 42, "/", "search", "blue")
    + box(504, 80, 170, 42, "send", "send", "dark")
    + box(686, 80, 170, 42, "list · status · log", "list, state, history", "dark")
    + box(504, 134, 170, 42, "revoke", "revoke", "dark")
    + box(686, 134, 170, 42, "remind", "remind", "dark")
    + box(504, 188, 170, 42, "purge", "purge", "dark")
    + box(686, 188, 170, 42, "version · --help", "version, help", "dark")
    + text(220, 262, "you see everything, it updates itself", 11.5, "#003a90", "600")
    + text(680, 262, "handy in scripts and over ssh", 11.5, "#003a90", "600")
    + box(290, 318, 320, 50, "The same AMS actions", "same result, same trace in the log", "navy")
    + path([(220, 294), (220, 343), (286, 343)], "#0050C0")
    + path([(680, 294), (680, 343), (614, 343)], "#0050C0"),
    900, 390, "«FIG» — Two ways of using AMS; every TUI key runs the corresponding command",
    "The TUI and the commands")

S1 = p("AMS can be used in two ways, which do exactly the same things. Typed on its own in a terminal, " + c("ams")
       + " opens the <b>TUI</b>, a full-screen interface inside the terminal: the list of messages, the state of "
       "every recipient, the keys to act. Followed by a command (" + c("ams send") + ", " + c("ams status")
       + "…) it does one single thing and returns to the prompt.", lead=True) + DUE_MODI + \
    table(["Situation", "Better to use"], [
        ["following a message while the confirmations come in", "the TUI: it updates itself every 3 seconds"],
        ["writing a long message calmly", "the TUI, with your own editor (" + key("Ctrl", "E") + ")"],
        ["sending a notice from a script or from cron", c("ams send")],
        ["copying the state into a report or an email", c("ams status") + " or " + c("ams log")],
        ["a small terminal (fewer than 80 columns or 20 lines)", "the commands: " + c("ams") + " on its own shows the help"],
    ], "«TAB» — When to use the TUI and when the commands") + \
    note("every TUI action runs the corresponding command and shows its answer: what you learn in one way "
         "also applies to the other.", "Same commands.")

ANATOMIA = fig(
    riquadro(40, 40, 820, 300, "#111827", "#334155", 8)
    + mono(58, 64, "┌─ AMS · messaggi inviati ──────────────", 12, "#67e8f9", "700")
    + mono(842, 64, "aggiornato alle 16:55:57 ─┐", 12, "#9ca3af", "400", "end")
    + mono(62, 96, "  ID  DATA         MESSAGGIO", 12, "#fde047", "700")
    + mono(420, 96, "DESTINATARI", 12, "#fde047", "700")
    + mono(62, 122, "   3  30/09 16:55  Il tuo account scade…", 12, "#e5e7eb")
    + '<rect x="58" y="134" width="786" height="20" fill="#e5e7eb"/>'
    + mono(62, 149, ">  2  30/09 16:55  Manutenzione · Sabato…", 12, "#111827", "700")
    + mono(62, 176, "   1  30/09 16:55  Aggiornamento del…", 12, "#e5e7eb")
    + barra(420, 111, 0, 12, 0, seg=10, h=13) + mono(548, 122, "1 consegnato", 12, "#facc15")
    + barra(420, 138, 6, 5, 1, seg=10, h=13) + mono(548, 149, "4 confermato · 3 consegnato · 1 inviato", 12, "#111827", "700")
    + barra(420, 165, 12, 0, 0, seg=10, h=13) + mono(548, 176, "tutti confermato (3)", 12, "#4ade80")
    + mono(62, 262, "█ confermato   ▒ consegnato   ░ inviato", 12, "#e5e7eb")
    + mono(58, 296, "├────────────────────────────────────────────────────", 12, "#6b7280")
    + mono(62, 322, "Invio apri  n nuovo  r ritira  s sollecita  p pulizia  / cerca  ? tasti  q esci", 12, "#e5e7eb")
    + numero(30, 60, 1) + numero(870, 60, 2) + numero(30, 96, 3) + numero(30, 146, 4) + numero(870, 146, 5)
    + numero(30, 258, 6) + numero(30, 318, 7),
    900, 360, "«FIG» — The parts of the main screen (the same as in the real screenshot below). On screen: «AMS · "
    "messaggi inviati» (“AMS · sent messages”), «aggiornato alle» (“updated at”); columns «DATA» (“DATE”), «MESSAGGIO» "
    "(“MESSAGE”), «DESTINATARI» (“RECIPIENTS”); the example titles «Il tuo account scade…» (“Your account expires…”), "
    "«Manutenzione · Sabato…» (“Maintenance · Saturday…”), «Aggiornamento del…» (“Update of the…”); «1 consegnato» "
    "(“1 delivered”), «4 confermato · 3 consegnato · 1 inviato» (“4 confirmed · 3 delivered · 1 sent”), «tutti "
    "confermato (3)» (“all confirmed (3)”); keys «Invio apri» (“Enter open”), «n nuovo» (“new”), «r ritira» "
    "(“revoke”), «s sollecita» (“remind”), «p pulizia» (“purge”), «/ cerca» (“search”), «? tasti» (“keys”), «q esci» "
    "(“quit”)",
    "")

S2 = p("The main screen of the TUI is the list of sent messages. All AMS screens have the same frame: the title "
       "at the top left, the time of the last update at the top right, the content in the middle and, at the "
       "bottom, the line of keys that can be pressed at that moment.", lead=True) + ANATOMIA + \
    table(["", "Part", "What it shows"], [
        ["1", "Title", "Where you are: " + c("AMS · messaggi inviati") + " (“AMS · sent messages”), "
         + c("Messaggio 2 · Manutenzione") + " (“Message 2 · Maintenance”), " + c("Nuovo messaggio") + " (“New message”)."],
        ["2", "Update", "The time at which AMS last reread the message store. It changes every 3 seconds: if it "
         "stops, the TUI is no longer receiving updates."],
        ["3", "Header", "The columns: message number, date and time of sending, title and first line of the text, "
         "recipients."],
        ["4", "Selected line", "In reverse video and preceded by " + c(">") + ": the message that "
         + key("Enter") + ", " + key("r") + " and " + key("s") + " act on. Move it with " + key("↑") + " " + key("↓") + "."],
        ["5", "Recipients", "The three-colour bar and the phrase with the recipients in the three states (" + rif(3, 3) + ")."],
        ["6", "Legend", "The colours of the bar; during a search, also the text searched for."],
        ["7", "Keys", "What can be done now. It changes with the screen and with the confirmation windows."],
    ], "«TAB» — The parts of the screen") + \
    schermata("list", "«FIG» — The list of messages: real TUI screenshot, in a 116-column terminal") + \
    ul([
        "The messages are sorted newest first. " + c("[ritirato]") + " and " + c("[scaduto]") + " before the text "
        "(“[revoked]” and “[expired]” in English) mark those that are no longer shown to the users.",
        "In a terminal narrower than 110 columns the phrase gives way to just the count of confirmations out of "
        "the total, for example " + c("4/8") + "; the bar stays.",
        "If the terminal becomes smaller than 80 columns or 20 lines while the TUI is open, the TUI closes "
        "and the terminal returns to how it was.",
        "With the " + c("NO_COLOR") + " variable the TUI has no colours (" + rif(10, 3) + ").",
    ])

STATI = fig(
    box(30, 100, 190, 70, "sent", "the message has left", "grey")
    + box(355, 100, 190, 70, "delivered", "copy in their mailbox", "amber")
    + box(680, 100, 190, 70, "confirmed ✓", "«Ho letto» or «s»", "green")
    + arrow(222, 135, 353, 135, "#0050C0", False, "copy written", 288, 124)
    + arrow(547, 135, 678, 135, "#16a34a", False, "the user confirms", 612, 124)
    + '<path d="M410 172 C 410 232, 490 232, 490 172" fill="none" stroke="#d97706" stroke-width="2" stroke-dasharray="5 4"/>'
    + text(450, 250, "postpones («Più tardi», «n»): stays delivered", 11.5, "#92400e", "600")
    + zone(30, 276, 840, 64, "Properties of the message, not states of the recipients")
    + text(250, 322, "revoked: ams revoke, key r", 12, "#475569", "600")
    + text(650, 322, "expired: the --expires time has passed", 12, "#475569", "600")
    + text(450, 70, "for each recipient, exactly one of the three states", 12, "#003a90", "700"),
    900, 360, "«FIG» — The three states of a recipient; revocation and expiry stop the message without changing the states. "
    "The user confirms with «Ho letto» (“I have read it”) or «s» (“y”, yes), and postpones with «Più tardi» (“Later”) "
    "or «n» (no)",
    "Sent, delivered, confirmed")

BARRA = fig(
    barra(60, 60, 6, 5, 1, seg=36, h=34)
    + text(164, 120, "6 marks: confirmed", 12, "#166534", "700")
    + text(366, 120, "5: delivered", 12, "#92400e", "700")
    + text(474, 120, "1: sent", 12, "#991b1b", "700")
    + mono(520, 84, "4 confermato · 3 consegnato · 1 inviato", 13, "#0f172a", "700")
    + text(450, 160, "8 recipients, 12 marks: each state takes its share; whoever is still “sent” always gets at least one mark",
           11.5, "#334155"),
    900, 180, "«FIG» — How to read the bar of a message with 8 recipients; the phrase «4 confermato · 3 consegnato · 1 "
    "inviato» means “4 confirmed · 3 delivered · 1 sent”", "The bar and the phrase")

S3 = p("There is only one concept you need to know to use AMS: every recipient of every message is in one of "
       "<b>three states</b>. There are no others.", lead=True) + STATI + \
    table(["State", "What it means", "What AMS does"], [
        [INVIATO, "The message has left, but the copy is not yet in the user's mailbox: usually because it "
         "could not be written, for example with a full disk.", "Retries by itself the next time " + c("ams") + " is used: a command such as " + c("list") + " or " + c("status")
         + ", or opening the TUI."],
        [CONSEGNATO, "The copy is in the user's mailbox: they see it at once if logged in, otherwise at the next "
         "login. They have not confirmed yet.", "Shows the message to them again until they confirm; if they "
         "postpone, it waits 30 minutes."],
        [CONFERMATO, "The user has stated that they have read it, with a click or by answering «s» (“y” in English).", "No longer "
         "shows it to them, in any session. Records date, time and channel."],
    ], "«TAB» — The three states of a recipient") + \
    p(RITIRATO + " and " + SCADUTO + ", on the other hand, are <b>properties of the message</b>: from that moment on "
      "the message is no longer shown or shown again to anyone, and whoever had not confirmed stays " + CONSEGNATO
      + ", with the indication «non confermato (ritirato)» or «(scaduto)» (“not confirmed (revoked)”, “(expired)”).") + BARRA + \
    p("The list summarises each message with its recipients in the three states, in two forms: the <b>bar</b> of "
      "12 coloured marks and the <b>phrase</b>, for example «4 confermato · 3 consegnato · 1 inviato» (“4 confirmed · "
      "3 delivered · 1 sent”). When everyone has confirmed, the phrase becomes «tutti confermato (8)» (“all "
      "confirmed (8)”) and the bar is entirely green.") + \
    tip("whoever has postponed is not in a separate state: they stay delivered. The message details say when "
        "they last postponed (" + rif(6, 2) + ").", "What about those who postpone?")

S4 = table(["I want to…", "In the TUI", "With a command", "Where"], [
    ["send a message", key("n") + ", then " + key("Ctrl", "S"), c("ams send --to … \"testo\"") + " (testo: “text”)",
     rif(5)],
    ["see all messages", "the main screen", c("ams list"), rif(6, 1)],
    ["see who has confirmed", key("Enter") + " on the message", c("ams status ID"), rif(6, 2)],
    ["see the history of a message", key("Enter") + ", then " + key("Tab"), c("ams log ID"), rif(6, 4)],
    ["find a message", key("/"), "—", rif(6, 6)],
    ["revoke a message", key("r"), c("ams revoke ID"), rif(7, 1)],
    ["remind whoever has not confirmed", key("s"), c("ams remind ID"), rif(7, 2)],
    ["delete old messages", key("p"), c("ams purge 90d"), rif(7, 3)],
    ["the list of keys", key("?"), "—", rif(3, 4)],
    ["the complete help", "—", c("ams --help"), rif(9)],
    ["quit", key("q"), "—", ""],
], "«TAB» — All of AMS in one table") + \
    p("In the TUI the " + key("?") + " key opens the list of keys over the message list; any key closes it. "
      "In the key line the entry is called «tasti» (“keys” in English); the complete list of commands is in "
      + c("ams --help") + ".") + \
    schermata_u("help", "«FIG» — The list of TUI keys (key ?)")

CHAPTER = ("AMS at a glance", [
    ("Two ways of working", S1),
    ("How the TUI is laid out", S2),
    ("The three states of a recipient", S3),
    ("Map of commands and keys", S4),
])
