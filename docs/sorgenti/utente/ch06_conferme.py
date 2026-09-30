import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import arrow, box, c, fig, key, note, p, schermata, table, term, text, tip, ui, ul, warn  # noqa: E402
from _aiuti import CONFERMATO, CONSEGNATO, INVIATO, RITIRATO, SCADUTO, rif, schermata_u  # noqa: E402


def colonna(s, w):
    return s[:w] + " " * (w - len(s[:w]))


def lista(righe):
    """L'uscita di ams list, con le stesse larghezze del programma."""
    out = ["admin@server:~$ ams list", f"{'ID':<5} {'DATA':<12} " + colonna("TESTO", 40) + "  DESTINATARI"]
    for i, data, testo, frase in righe:
        out.append(f"{i:<5} {data:<12} " + colonna(testo, 40) + "  " + frase)
    return "\n".join(out)


def stato(intestazione, corpo, righe, cmd):
    out = [f"admin@server:~$ {cmd}", intestazione]
    out += [f"  │ {r}" for r in corpo]
    out += ["", f"{'UTENTE':<16} STATO"]
    out += [f"{u:<16} {s}" for u, s in righe]
    return "\n".join(out)


LISTA = lista([
    ("1", "30/09 16:55", "Stanotte alle 23 il server di posta viene aggiornato.", "tutti confermato (3)"),
    ("2", "30/09 16:55", "Sabato dalle 8 alle 12 il server sarà spento per la manutenzione dei dischi.",
     "4 confermato · 3 consegnato · 1 inviato"),
    ("3", "30/09 16:55", "Il tuo account scade venerdì: passa dall'ufficio IT.", "1 consegnato"),
    ("4", "30/09 16:55", "[ritirato] Riavvio alle 13:00.", "2 consegnato"),
])

S1 = p("La schermata principale della TUI (" + rif(3, 2) + ") e il comando " + c("ams list") + " mostrano tutti i "
       "messaggi inviati, ognuno riassunto con i suoi destinatari nei tre stati. La TUI li mette dal più recente e "
       "si aggiorna da sola; " + c("ams list") + " li elenca dal più vecchio, una volta.", lead=True) + \
    term(LISTA, "Gli stessi quattro messaggi della schermata del capitolo 3") + \
    table(["Colonna", "Nella TUI", "In " + c("ams list")], [
        ["ID", "il numero del messaggio", "lo stesso: serve per " + c("status") + ", " + c("log") + ", "
         + c("revoke") + " e " + c("remind")],
        ["DATA", "giorno e ora dell'invio (giorno/mese ore:minuti)", "lo stesso"],
        ["MESSAGGIO / TESTO", "titolo in grassetto, poi la prima riga del testo", "la prima riga del testo, "
         "tagliata a 40 caratteri"],
        ["DESTINATARI", "barra a tre colori e frase (sotto 110 colonne, conferme sul totale)", "la frase"],
    ], "«TAB» — Le colonne della lista") + \
    table(["Segno davanti al testo", "Vuol dire"], [
        [c("[ritirato]"), "il messaggio è stato ritirato (" + rif(7, 1) + "): non viene più mostrato"],
        [c("[scaduto]"), "è passata la scadenza: non viene più mostrato"],
        [c("[invio annullato: interrotto prima del salvataggio]"), "solo in " + c("ams list") + ": un invio si è "
         "fermato prima ancora di salvare il messaggio (" + rif(12, 4) + ")"],
    ], "«TAB» — I segni della lista") + \
    note("la frase conta i destinatari, non le persone che hanno visto il messaggio: «3 consegnato» vuol dire tre "
         "persone con la copia nella casella che non hanno ancora confermato, collegate o no.", "Destinatari.")

DETTAGLIO_CLI = stato(
    "Messaggio 2 · Manutenzione · 30/09 16:55 · da root",
    ["Sabato dalle 8 alle 12 il server sarà spento per la manutenzione dei dischi.",
     "Salvate il lavoro entro venerdì sera."],
    [("admin", "confermato il 30/09 16:55 (terminale pts/0)"),
     ("anna", "confermato il 30/09 16:55 (desktop)"),
     ("dario", "inviato, non consegnato"),
     ("fabio", "confermato il 30/09 16:55 (desktop)"),
     ("kora", "consegnato, rimandato il 30/09 16:55"),
     ("luca", "consegnato"),
     ("mario", "consegnato, rimandato il 30/09 16:55"),
     ("zeno", "confermato il 30/09 16:55 (terminale pts/2)")],
    "ams status 2")

S2 = p("Con " + key("Invio") + " sulla lista si apre il messaggio scelto: in alto titolo, data, mittente, scadenza "
       "ed eventuale ritiro, poi le prime righe del testo, poi due schede. La scheda " + ui("Destinatari")
       + " mostra per ogni utente il suo stato, con i colori della barra.", lead=True) + \
    schermata("dettaglio", "«FIG» — Un messaggio aperto nella TUI: lo stato di ogni destinatario") + \
    p("Lo stesso elenco, per un messaggio alla volta, si ottiene con " + c("ams status") + " seguito dal numero:") + \
    term(DETTAGLIO_CLI, "Lo stato dei destinatari con un comando") + \
    table(["Riga di stato", "Stato", "Cosa vuol dire"], [
        [c("inviato, non consegnato"), INVIATO, "la copia non è ancora nella casella: AMS riprova"],
        [c("inviato, non consegnato: la copia non è stata scritta (vedi il registro; il prossimo comando ams "
           "riproverà)"), INVIATO, "l'invio ha incontrato un errore per questo utente, di solito il disco pieno"],
        [c("consegnato"), CONSEGNATO, "ha la copia; non ha ancora confermato"],
        [c("consegnato, scritto su 2 terminali"), CONSEGNATO, "all'invio era collegato e il testo è comparso in due "
         "finestre di terminale"],
        [c("consegnato, rimandato il 30/09 16:55"), CONSEGNATO, "ha risposto «Più tardi» o «n»; l'ora è quella "
         "dell'ultimo rinvio"],
        [c("consegnato, non confermato (ritirato)"), CONSEGNATO, "il messaggio è stato ritirato prima della sua conferma"],
        [c("consegnato, non confermato (scaduto)"), CONSEGNATO, "il messaggio è scaduto prima della sua conferma"],
        [c("consegnato, non confermato (scaduto; conferma arrivata dopo la scadenza)"), CONSEGNATO,
         "ha confermato, ma troppo tardi: la conferma non vale"],
        [c("confermato il 30/09 16:55 (desktop)"), CONFERMATO, "ha premuto «Ho letto» nella finestra"],
        [c("confermato il 30/09 16:55 (terminale pts/2)"), CONFERMATO, "ha risposto «s» in una finestra di "
         "terminale o in una connessione ssh (" + c("pts") + ")"],
        [c("confermato il 30/09 16:55 (terminale tty3)"), CONFERMATO, "ha risposto «s» su una console della macchina"],
    ], "«TAB» — Le righe di stato di un destinatario") + \
    p("Sopra l'elenco, " + c("ams status") + " scrive " + c("RITIRATO il …") + " se il messaggio è stato ritirato e "
      + c("SCADUTO") + " se è passata la scadenza. Nella TUI le stesse informazioni sono nella riga in alto, in "
      "rosso per il ritiro.") + \
    tip("nella scheda " + ui("Destinatari") + " si scorre con " + key("↑") + " " + key("↓") + " e "
        + key("PgUp") + " " + key("PgDn") + "; " + key("s") + " sollecita e " + key("r") + " ritira proprio questo "
        "messaggio; " + key("Esc") + " torna alla lista.", "Tasti del messaggio.")

VITA = fig(
    '<line x1="60" y1="170" x2="860" y2="170" stroke="#94a3b8" stroke-width="2"/>'
    + "".join(f'<line x1="{x}" y1="164" x2="{x}" y2="176" stroke="#94a3b8" stroke-width="2"/>'
              + text(x, 196, t, 11.5, "#475569", "600") for x, t in
              [(100, "16:55"), (290, "17:02"), (480, "17:32"), (660, "17:40"), (820, "17:41")])
    + box(30, 70, 140, 60, "inviato", "ams send", "grey")
    + box(220, 70, 140, 60, "consegnato", "copia nella casella", "amber")
    + box(410, 70, 140, 60, "rimandato", "resta consegnato", "amber", 12)
    + box(590, 70, 140, 60, "sollecitato", "ams remind", "blue", 12)
    + box(760, 70, 120, 60, "confermato", "«Ho letto»", "green")
    + arrow(100, 132, 100, 164, "#475569") + arrow(290, 132, 290, 164, "#475569")
    + arrow(480, 132, 480, 164, "#475569") + arrow(660, 132, 660, 164, "#475569")
    + arrow(820, 132, 820, 164, "#475569")
    + text(450, 236, "La storia di Mario per il messaggio 2: gli stati sono solo tre; rinvio e sollecito sono eventi",
           11.5, "#334155", "600")
    + text(450, 256, "che restano nel registro, e lo stato resta «consegnato» fino alla conferma.", 11.5, "#334155", "600"),
    900, 280, "«FIG» — La vita di un messaggio per un destinatario, dall'invio alla conferma", "Stati ed eventi")

S3 = p("Ogni messaggio vive una storia fatta di <b>eventi</b>: l'invio, la consegna a ciascuno, i rinvii, i "
       "solleciti, le conferme, un eventuale ritiro. Gli eventi cambiano lo stato di un destinatario solo in due "
       "punti: quando la copia arriva nella casella e quando l'utente conferma.", lead=True) + VITA + \
    table(["Evento", "Chi lo causa", "Effetto sullo stato del destinatario"], [
        ["invio", "l'amministratore", "tutti " + INVIATO + " per un istante"],
        ["consegna", "AMS", INVIATO + " → " + CONSEGNATO],
        ["rinvio", "l'utente («Più tardi», «n»)", "nessuno: resta " + CONSEGNATO],
        ["sollecito", "l'amministratore (" + key("s") + ", " + c("ams remind") + ")", "nessuno: resta "
         + CONSEGNATO + ", ma gli viene richiesto subito"],
        ["conferma", "l'utente («Ho letto», «s»)", CONSEGNATO + " → " + CONFERMATO],
        ["ritiro", "l'amministratore (" + key("r") + ", " + c("ams revoke") + ")", "nessuno; il messaggio diventa "
         + RITIRATO + " e non si mostra più"],
        ["scadenza", "il tempo", "nessuno; il messaggio diventa " + SCADUTO + " e non si mostra più"],
    ], "«TAB» — Gli eventi e gli stati") + \
    warn("una conferma è definitiva: non si può annullare, né dalla TUI né dai comandi. Per chiedere di nuovo a tutti "
         "si manda un messaggio nuovo.", "Nessun ritorno.")

LOG = ("admin@server:~$ ams log 2\n"
       "Messaggio 2 · Manutenzione · 30/09 16:55\n"
       "2026-09-30 16:55:57  messaggio 2 consegnato a admin (terminali scritti: 0)\n"
       "2026-09-30 16:55:57  messaggio 2 consegnato a anna (terminali scritti: 0)\n"
       "2026-09-30 16:55:57  messaggio 2 consegnato a mario (terminali scritti: 0)\n"
       "2026-09-30 16:55:57  messaggio 2 inviato da root a: admin anna dario fabio kora luca mario zeno\n"
       "2026-09-30 16:56:10  utente anna: confermata la lettura del messaggio 2 (desktop)\n"
       "2026-09-30 16:56:31  utente mario: rimandato il messaggio 2 (terminale)\n"
       "2026-09-30 17:02:04  messaggio 2: sollecitati 3 destinatari da admin")

S4 = p("La scheda " + ui("Storia") + " del messaggio, che si apre con " + key("Tab") + ", elenca gli eventi del "
       "messaggio presi dal registro di sistema, dal più vecchio, con data e ora al secondo.", lead=True) + \
    schermata("storia", "«FIG» — La storia di un messaggio nella TUI") + \
    p("Con un comando, la stessa storia si legge con " + c("ams log") + ":") + term(LOG, "La storia con un comando") + \
    table(["Riga", "Quando compare"], [
        [c("messaggio N consegnato a U (terminali scritti: K)"), "per ogni copia arrivata nella casella; K è il "
         "numero di finestre di terminale in cui il testo è comparso all'invio"],
        [c("messaggio N inviato da A a: …"), "alla fine di ogni invio, con l'elenco dei destinatari"],
        [c("messaggio N: ERRORE, copia per U non scritta"), "quando una consegna non riesce"],
        [c("messaggio N consegnato a U (recupero)"), "quando AMS completa una consegna rimasta indietro"],
        [c("utente U: rimandato il messaggio N (terminale)") + " o " + c("(desktop)"), "quando l'utente rimanda"],
        [c("utente U: confermata la lettura del messaggio N (canale)"), "alla conferma"],
        [c("utente U: ERRORE, conferma del messaggio N non registrata (…)"), "quando la conferma non si è potuta "
         "salvare, per esempio con il disco pieno"],
        [c("messaggio N: sollecitati K destinatari da A"), "a ogni sollecito"],
        [c("messaggio N ritirato da A"), "al ritiro"],
    ], "«TAB» — Le righe della storia") + \
    note("la storia viene dal registro di sistema, che la macchina può ruotare e cancellare dopo un po' secondo le "
         "sue impostazioni. Lo stato dei destinatari invece viene dall'archivio di AMS e resta finché il messaggio "
         "non viene cancellato.", "Storia e stato.")

S5 = p("Ogni evento viene scritto anche nel registro di sistema della macchina, con l'etichetta " + c("ams") + ". È la "
       "traccia da usare se qualcuno chiede «chi ha mandato cosa, e quando», anche per i messaggi già cancellati.",
       lead=True) + term(
    "admin@server:~$ sudo journalctl -t ams --since today\n"
    "set 30 16:55:57 server ams[20914]: messaggio 2 consegnato a anna (terminali scritti: 0)\n"
    "set 30 16:55:57 server ams[20914]: messaggio 2 inviato da root a: admin anna dario fabio kora luca mario zeno\n"
    "set 30 16:56:10 server ams[21310]: utente anna: confermata la lettura del messaggio 2 (desktop)",
    "Il registro di sistema") + \
    table(["Per vedere…", "Comando"], [
        ["tutti gli eventi di AMS di oggi", c("sudo journalctl -t ams --since today")],
        ["gli eventi dell'ultima ora", c('sudo journalctl -t ams --since "1 hour ago"')],
        ["gli eventi che arrivano, mentre arrivano", c("sudo journalctl -t ams -f")],
        ["la storia di un messaggio, ben ordinata", c("ams log 2")],
    ], "«TAB» — Leggere il registro") + \
    ul([
        "Nel registro le righe sono nella lingua della macchina; " + c("ams log") + " e la TUI le riscrivono nella "
        "lingua di chi le legge.",
        "Gli eventi degli utenti (rinvii, conferme) sono scritti dagli utenti stessi: " + c("ams log") + " controlla "
        "chi li ha scritti e segnala quelli sospetti (" + rif(11, 5) + ").",
        "Una cancellazione con " + c("ams purge") + " toglie il messaggio dall'archivio, ma i suoi eventi restano nel "
        "registro.",
    ])

S6 = p("Quando i messaggi sono tanti, il tasto " + key("/") + " della TUI mostra solo quelli che contengono un "
       "testo, cercato nel titolo e in tutto il messaggio, senza distinguere maiuscole e minuscole.", lead=True) + \
    schermata_u("cerca", "«FIG» — La ricerca: si scrive il testo e si preme Invio") + \
    schermata_u("cercato", "«FIG» — Il risultato: in basso a destra il testo cercato") + \
    table(["Tasto", "Cosa fa"], [
        [key("/"), "apre la ricerca; se ce n'era già una, la ripropone da modificare"],
        [key("Invio"), "applica la ricerca"],
        [key("Esc") + " nella finestra di ricerca", "lascia la lista com'era"],
        [key("Esc") + " nella lista", "toglie la ricerca e mostra di nuovo tutti i messaggi"],
    ], "«TAB» — I tasti della ricerca") + \
    note("se nessun messaggio contiene il testo, la lista dice «Nessun messaggio contiene il testo cercato.». "
         "Le lettere accentate vanno scritte con lo stesso carattere maiuscolo o minuscolo del messaggio.",
         "Nessun risultato.")

CHAPTER = ("Seguire le conferme", [
    ("La lista dei messaggi", S1),
    ("Lo stato di ogni destinatario", S2),
    ("La vita di un messaggio", S3),
    ("La storia di un messaggio", S4),
    ("Il registro di sistema", S5),
    ("Cercare un messaggio", S6),
])
