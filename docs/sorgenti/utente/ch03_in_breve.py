import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import arrow, box, c, fig, key, note, p, path, schermata, table, text, tip, ul, zone  # noqa: E402
from _aiuti import CONFERMATO, CONSEGNATO, INVIATO, RITIRATO, SCADUTO, barra, mono, numero, rif, riquadro, schermata_u  # noqa: E402

DUE_MODI = fig(
    zone(20, 44, 400, 250, "Nella TUI: ams, da solo")
    + zone(480, 44, 400, 250, "Con i comandi: ams COMANDO")
    + box(44, 80, 170, 42, "n", "scrivi e invia", "blue")
    + box(226, 80, 170, 42, "Invio", "destinatari e storia", "blue")
    + box(44, 134, 170, 42, "r", "ritira", "blue")
    + box(226, 134, 170, 42, "s", "sollecita", "blue")
    + box(44, 188, 170, 42, "p", "pulizia", "blue")
    + box(226, 188, 170, 42, "/", "cerca", "blue")
    + box(504, 80, 170, 42, "send", "invia", "dark")
    + box(686, 80, 170, 42, "list · status · log", "elenco, stato, storia", "dark")
    + box(504, 134, 170, 42, "revoke", "ritira", "dark")
    + box(686, 134, 170, 42, "remind", "sollecita", "dark")
    + box(504, 188, 170, 42, "purge", "pulizia", "dark")
    + box(686, 188, 170, 42, "version · --help", "versione, guida", "dark")
    + text(220, 262, "si vede tutto, si aggiorna da solo", 11.5, "#003a90", "600")
    + text(680, 262, "comodi negli script e con ssh", 11.5, "#003a90", "600")
    + box(290, 318, 320, 50, "Le stesse azioni di AMS", "stesso risultato, stessa traccia nel registro", "navy")
    + path([(220, 294), (220, 343), (286, 343)], "#0050C0")
    + path([(680, 294), (680, 343), (614, 343)], "#0050C0"),
    900, 390, "«FIG» — Due modi di usare AMS; ogni tasto della TUI esegue il comando corrispondente",
    "La TUI e i comandi")

S1 = p("AMS si usa in due modi, che fanno esattamente le stesse cose. Scritto da solo in un terminale, " + c("ams")
       + " apre la <b>TUI</b>, un'interfaccia a tutto schermo dentro il terminale: la lista dei messaggi, lo stato "
       "di ogni destinatario, i tasti per agire. Seguito da un comando (" + c("ams send") + ", " + c("ams status")
       + "…) fa una sola cosa e torna al prompt.", lead=True) + DUE_MODI + \
    table(["Situazione", "Conviene"], [
        ["seguire un messaggio mentre arrivano le conferme", "la TUI: si aggiorna da sola ogni 3 secondi"],
        ["scrivere un messaggio lungo con calma", "la TUI, con il proprio editor (" + key("Ctrl", "E") + ")"],
        ["mandare un avviso da uno script o da cron", c("ams send")],
        ["copiare lo stato in una segnalazione o in un'email", c("ams status") + " o " + c("ams log")],
        ["un terminale piccolo (meno di 80 colonne o 20 righe)", "i comandi: " + c("ams") + " da solo mostra la guida"],
    ], "«TAB» — Quando usare la TUI e quando i comandi") + \
    note("ogni azione della TUI esegue il comando corrispondente e ne mostra la risposta: ciò che si impara in un "
         "modo vale anche nell'altro.", "Stessi comandi.")

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
    + mono(62, 322, "Invio apri  n nuovo  r ritira  s sollecita  p pulizia  / cerca  ? guida  q esci", 12, "#e5e7eb")
    + numero(30, 60, 1) + numero(870, 60, 2) + numero(30, 96, 3) + numero(30, 146, 4) + numero(870, 146, 5)
    + numero(30, 258, 6) + numero(30, 318, 7),
    900, 360, "«FIG» — Le parti della schermata principale (le stesse della schermata vera qui sotto)",
    "")

S2 = p("La schermata principale della TUI è la lista dei messaggi inviati. Tutte le schermate di AMS hanno la stessa "
       "cornice: il titolo in alto a sinistra, l'ora dell'ultimo aggiornamento in alto a destra, il contenuto al "
       "centro e, in fondo, la riga dei tasti che si possono premere in quel momento.", lead=True) + ANATOMIA + \
    table(["", "Parte", "Cosa mostra"], [
        ["1", "Titolo", "Dove si è: " + c("AMS · messaggi inviati") + ", " + c("Messaggio 2 · Manutenzione") + ", "
         + c("Nuovo messaggio") + "."],
        ["2", "Aggiornamento", "L'ora in cui AMS ha riletto l'archivio. Cambia ogni 3 secondi: se si ferma, la "
         "TUI non sta più ricevendo aggiornamenti."],
        ["3", "Intestazione", "Le colonne: numero del messaggio, data e ora dell'invio, titolo e prima riga del testo, "
         "destinatari."],
        ["4", "Riga scelta", "In negativo e con " + c(">") + " davanti: il messaggio su cui agiscono "
         + key("Invio") + ", " + key("r") + " e " + key("s") + ". Si sposta con " + key("↑") + " " + key("↓") + "."],
        ["5", "Destinatari", "La barra a tre colori e la frase con i destinatari nei tre stati (" + rif(3, 3) + ")."],
        ["6", "Legenda", "I colori della barra; durante una ricerca, anche il testo cercato."],
        ["7", "Tasti", "Cosa si può fare adesso. Cambia con la schermata e con le finestre di conferma."],
    ], "«TAB» — Le parti della schermata") + \
    schermata("lista", "«FIG» — La lista dei messaggi: schermata vera della TUI, in un terminale di 116 colonne") + \
    ul([
        "I messaggi sono in ordine dal più recente. " + c("[ritirato]") + " e " + c("[scaduto]") + " davanti al testo "
        "segnalano quelli che non vengono più mostrati agli utenti.",
        "In un terminale di meno di 110 colonne la frase lascia il posto al solo conteggio delle conferme sul totale, "
        "per esempio " + c("4/8") + "; la barra resta.",
        "Se il terminale diventa più piccolo di 80 colonne o di 20 righe mentre la TUI è aperta, la TUI si chiude "
        "e il terminale torna com'era.",
        "Con la variabile " + c("NO_COLOR") + " la TUI è senza colori (" + rif(10, 3) + ").",
    ])

STATI = fig(
    box(30, 100, 190, 70, "inviato", "il messaggio è partito", "grey")
    + box(355, 100, 190, 70, "consegnato", "copia nella sua casella", "amber")
    + box(680, 100, 190, 70, "confermato ✓", "«Ho letto» o «s»", "green")
    + arrow(222, 135, 353, 135, "#0050C0", False, "copia scritta", 288, 124)
    + arrow(547, 135, 678, 135, "#16a34a", False, "l'utente conferma", 612, 124)
    + '<path d="M410 172 C 410 232, 490 232, 490 172" fill="none" stroke="#d97706" stroke-width="2" stroke-dasharray="5 4"/>'
    + text(450, 250, "rimanda («Più tardi», «n»): resta consegnato", 11.5, "#92400e", "600")
    + zone(30, 276, 840, 64, "Proprietà del messaggio, non stati dei destinatari")
    + text(250, 322, "ritirato: ams revoke, tasto r", 12, "#475569", "600")
    + text(650, 322, "scaduto: passata la scadenza --expires", 12, "#475569", "600")
    + text(450, 70, "per ogni destinatario, uno solo dei tre stati", 12, "#003a90", "700"),
    900, 360, "«FIG» — I tre stati di un destinatario; ritiro e scadenza fermano il messaggio senza cambiare gli stati",
    "Inviato, consegnato, confermato")

BARRA = fig(
    barra(60, 60, 6, 5, 1, seg=36, h=34)
    + text(164, 120, "6 segni: confermato", 12, "#166534", "700")
    + text(366, 120, "5: consegnato", 12, "#92400e", "700")
    + text(474, 120, "1: inviato", 12, "#991b1b", "700")
    + mono(520, 84, "4 confermato · 3 consegnato · 1 inviato", 13, "#0f172a", "700")
    + text(450, 160, "8 destinatari, 12 segni: ogni stato occupa la sua parte; chi è ancora «inviato» ha sempre almeno un segno",
           11.5, "#334155"),
    900, 180, "«FIG» — Come si legge la barra di un messaggio con 8 destinatari", "La barra e la frase")

S3 = p("Il concetto da conoscere per usare AMS è uno solo: ogni destinatario di ogni messaggio è in uno di "
       "<b>tre stati</b>. Non ce ne sono altri.", lead=True) + STATI + \
    table(["Stato", "Cosa vuol dire", "Cosa fa AMS"], [
        [INVIATO, "Il messaggio è partito, ma la copia non è ancora nella casella dell'utente: di solito perché "
         "non si è potuta scrivere, per esempio con il disco pieno.", "Riprova da solo quando si usa di nuovo " + c("ams") + ": un comando come " + c("list") + " o " + c("status")
         + ", o l'apertura della TUI."],
        [CONSEGNATO, "La copia è nella casella dell'utente: la vede subito se è collegato, altrimenti al prossimo "
         "accesso. Non ha ancora confermato.", "Gli ripropone il messaggio finché non conferma; se rimanda, "
         "aspetta 30 minuti."],
        [CONFERMATO, "L'utente ha dichiarato di averlo letto, con un clic o rispondendo «s».", "Non glielo mostra "
         "più, in nessuna sessione. Registra data, ora e canale."],
    ], "«TAB» — I tre stati di un destinatario") + \
    p(RITIRATO + " e " + SCADUTO + " sono invece <b>proprietà del messaggio</b>: da quel momento il messaggio non "
      "viene più mostrato né riproposto a nessuno, e chi non aveva confermato resta " + CONSEGNATO + ", con "
      "l'indicazione «non confermato (ritirato)» o «(scaduto)».") + BARRA + \
    p("La lista riassume ogni messaggio con i suoi destinatari nei tre stati, in due forme: la <b>barra</b> di 12 "
      "segni colorati e la <b>frase</b>, per esempio «4 confermato · 3 consegnato · 1 inviato». Quando hanno "
      "confermato tutti, la frase diventa «tutti confermato (8)» e la barra è tutta verde.") + \
    tip("chi ha rimandato non è in uno stato a parte: resta consegnato. Il dettaglio del messaggio dice quando "
        "ha rimandato l'ultima volta (" + rif(6, 2) + ").", "E chi rimanda?")

S4 = table(["Voglio…", "Nella TUI", "Con un comando", "Dove"], [
    ["mandare un messaggio", key("n") + ", poi " + key("Ctrl", "S"), c("ams send --to … \"testo\""), rif(5)],
    ["vedere tutti i messaggi", "la schermata principale", c("ams list"), rif(6, 1)],
    ["vedere chi ha confermato", key("Invio") + " sul messaggio", c("ams status ID"), rif(6, 2)],
    ["vedere la storia di un messaggio", key("Invio") + ", poi " + key("Tab"), c("ams log ID"), rif(6, 4)],
    ["trovare un messaggio", key("/"), "—", rif(6, 6)],
    ["ritirare un messaggio", key("r"), c("ams revoke ID"), rif(7, 1)],
    ["sollecitare chi non ha confermato", key("s"), c("ams remind ID"), rif(7, 2)],
    ["cancellare i messaggi vecchi", key("p"), c("ams purge 90d"), rif(7, 3)],
    ["l'elenco dei tasti", key("?"), "—", rif(3, 4)],
    ["la guida completa", "—", c("ams --help"), rif(9)],
    ["uscire", key("q"), "—", ""],
], "«TAB» — Tutto AMS in una tabella") + \
    p("Nella TUI il tasto " + key("?") + " apre l'elenco dei tasti sopra la lista; un tasto qualsiasi lo chiude. "
      "Nella riga dei tasti la voce si chiama «tasti»; l'elenco completo dei comandi è in " + c("ams --help") + ".") + \
    schermata_u("aiuto", "«FIG» — L'elenco dei tasti della TUI (tasto ?)")

CHAPTER = ("AMS in breve", [
    ("Due modi di lavorare", S1),
    ("Com'è fatta la TUI", S2),
    ("I tre stati di un destinatario", S3),
    ("Mappa dei comandi e dei tasti", S4),
])
