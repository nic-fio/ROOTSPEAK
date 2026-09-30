import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import arrow, box, c, code, diamond, fig, key, note, p, schermata, seq, steps, table, term, text, tip, ui, ul, warn  # noqa: E402
from _aiuti import CONSEGNATO, INVIATO, rif  # noqa: E402

INSIEMI = fig(
    '<rect x="20" y="44" width="860" height="236" rx="18" fill="#eef4ff" stroke="#0050C0" stroke-width="2"/>'
    + text(40, 70, "all: tutti gli utenti della macchina", 13, "#003a90", "700", "start")
    + text(40, 88, "con UID da 1000 in su e una shell vera; niente root né account di servizio", 11, "#475569", "400", "start")
    + '<ellipse cx="330" cy="182" rx="210" ry="76" fill="#0050C0" fill-opacity="0.13" stroke="#0050C0" stroke-width="1.6"/>'
    + text(210, 170, "online", 13, "#003a90", "700")
    + text(210, 188, "chi è collegato adesso", 11, "#334155")
    + '<ellipse cx="560" cy="182" rx="200" ry="70" fill="#d97706" fill-opacity="0.14" stroke="#d97706" stroke-width="1.6"/>'
    + text(670, 170, "@sviluppo", 13, "#92400e", "700")
    + text(670, 188, "i membri di un gruppo", 11, "#334155")
    + text(446, 176, "collegati e", 11, "#334155") + text(446, 192, "del gruppo", 11, "#334155")
    + '<circle cx="818" cy="112" r="7" fill="#003a90"/>' + text(818, 134, "mario", 11.5, "#003a90", "700")
    + text(818, 150, "un utente", 10.5, "#475569"),
    900, 300, "«FIG» — I destinatari si possono combinare: --to mario,@sviluppo manda a Mario e a tutto il gruppo",
    "Chi riceve il messaggio")

S1 = p("Il campo " + ui("A") + " della TUI e l'opzione " + c("--to") + " dei comandi dicono chi riceve il messaggio. "
       "Si possono indicare più destinatari separati da virgole, senza spazi: chi compare più volte, per esempio "
       "perché è in due gruppi, riceve il messaggio una volta sola.", lead=True) + \
    table(["Scrivi", "Chi riceve", "Esempio"], [
        ["un nome", "quell'utente, anche se non è collegato", c("mario")],
        ["più nomi", "ognuno di loro", c("mario,anna,luca")],
        [c("@gruppo"), "i membri di un gruppo del sistema, compresi quelli che l'hanno come gruppo principale",
         c("@sviluppo")],
        [c("all"), "tutti gli utenti della macchina, collegati o no: UID da 1000 in su (i limiti di "
         + c("/etc/login.defs") + ") e una shell vera, cioè non " + c("nologin") + " né " + c("false"), c("all")],
        [c("online"), "fra gli utenti di " + c("all") + ", chi è collegato in questo momento, in qualunque modo "
         "(desktop, console, ssh)", c("online")],
        ["una combinazione", "l'unione di tutti", c("mario,@sviluppo")],
    ], "«TAB» — Come indicare i destinatari") + INSIEMI + \
    note("un gruppo con " + c("@") + " comprende tutti i suoi membri, anche gli account che " + c("all") + " esclude. "
         "Nella TUI, passando dal campo " + ui("A") + " al successivo, a destra compare quanti destinatari sono, "
         "oppure l'errore se un nome non esiste: si controlla prima di inviare.", "Da sapere.") + \
    warn(c("online") + " si calcola al momento dell'invio: chi si collega un minuto dopo non riceve il messaggio. "
         "Per un avviso che deve raggiungere tutti prima o poi si usa " + c("all") + ".", "online è una fotografia.")

S2 = p("Il <b>titolo</b> è facoltativo, su una riga: compare in testa al messaggio nel terminale, nella finestra del "
       "desktop e nella lista della TUI. Il <b>testo</b> può avere più righe.", lead=True) + \
    table(["Modo", "Dove", "Esempio"], [
        ["scritto nella TUI", "campo " + ui("Testo") + "; " + key("Invio") + " va a capo", "—"],
        ["scritto nel proprio editor", "TUI, " + key("Ctrl", "E") + " (" + rif(5, 5) + ")", "—"],
        ["tra virgolette, alla fine del comando", c("ams send"), c('ams send --to mario "Testo del messaggio"')],
        ["da un file", c("ams send --file"), c("ams send --to @sviluppo --file avviso.txt")],
        ["da un altro comando", c("ams send") + ", senza testo né " + c("--file"), c("df -h | ams send --to anna")],
        ["scritto al momento", c("ams send") + " in un terminale: si scrive, poi " + key("Ctrl", "D"),
         c("ams send --to mario")],
    ], "«TAB» — I modi di dare il testo") + \
    code("Da lunedì 15 ottobre le password scadono ogni 90 giorni.\n"
         "Al primo accesso dopo la scadenza il sistema chiederà di cambiarla.\n"
         "Per problemi: ufficio IT, interno 214.", "text", "avviso.txt") + \
    term('admin@server:~$ ams send --to all --title "Nuova regola per le password" --file avviso.txt\n'
         "Messaggio 3 inviato a 24 utenti.") + \
    table(["Regola", "Perché"], [
        ["al massimo 64 KB di testo (65536 byte: circa 30 pagine)", "oltre, la finestra del desktop non potrebbe "
         "mostrarlo; AMS rifiuta con «messaggio troppo lungo». La TUI mostra il conteggio sotto il testo, in rosso "
         "quando si supera"],
        ["il testo non può essere vuoto o fatto solo di spazi", "AMS rifiuta con «messaggio vuoto»"],
        ["le righe vuote in fondo al testo si tolgono", "il messaggio finisce con l'ultima riga scritta"],
        ["il titolo sta su una riga", "gli a capo e le tabulazioni del titolo diventano spazi"],
        ["i caratteri invisibili e i codici di colore si tolgono", "un messaggio non può disturbare i terminali "
         "degli utenti (" + rif(11, 4) + ")"],
    ], "«TAB» — Le regole del testo") + \
    note("nei comandi le opzioni vanno scritte <b>prima</b> del testo: tutto quello che segue la prima parola che non "
         "è un'opzione fa parte del messaggio.", "L'ordine conta.")

URGENTE = fig(
    diamond(250, 150, 280, 104, "Perde senso dopo un po'?", "navy")
    + box(566, 48, 314, 72, "scadenza: 15m, 2h, 3d…", "dopo non si mostra né si ripropone più", "blue")
    + box(566, 180, 314, 72, "senza scadenza", "resta finché ognuno non conferma", "dark")
    + arrow(390, 140, 562, 90, "#0050C0", False, "sì", 474, 104)
    + arrow(390, 160, 562, 212, "#475569", False, "no", 474, 204)
    + text(250, 238, "in entrambi i casi si chiede la conferma", 11.5, "#334155", "600"),
    900, 272, "«FIG» — La scadenza serve per gli avvisi che valgono solo per poco", "Scadenza sì o no")

S3 = p("Ogni messaggio chiede la conferma. Per gli avvisi che valgono solo per poco, come «il servizio riparte tra "
       "5 minuti», si aggiunge una <b>scadenza</b>: passato quel momento il messaggio non viene più mostrato né "
       "riproposto, e chi non l'ha visto in tempo non lo vedrà più.", lead=True) + URGENTE + \
    table(["Scrivi (campo " + ui("Scadenza") + " o " + c("--expires") + ")", "Il messaggio scade"], [
        [c("30m"), "tra 30 minuti"],
        [c("2h"), "tra 2 ore"],
        [c("3d"), "tra 3 giorni"],
        [c("2026-10-04 12:00"), "sabato 4 ottobre 2026 alle 12 (nel comando, tra virgolette: "
         + c('--expires "2026-10-04 12:00"') + ")"],
        [c("tomorrow 18:00"), "domani alle 18: le date a parole vanno scritte in inglese"],
    ], "«TAB» — Come indicare la scadenza") + \
    term('admin@server:~$ ams send --to online --expires 15m "Il servizio web riparte alle 13:00."\n'
         "Messaggio 2 inviato a 3 utenti.") + ul([
        "Alla scadenza una finestra ancora aperta si chiude da sola, e una domanda in attesa nel terminale si "
        "interrompe con «[AMS] Il messaggio è scaduto.».",
        "Una conferma data dopo la scadenza non vale: il destinatario resta " + CONSEGNATO + ", «non confermato "
        "(scaduto)».",
        "Nella lista il messaggio compare con " + c("[scaduto]") + " davanti; il dettaglio dice quando è scaduto.",
    ]) + warn(c('"sabato 12:00"') + " non viene capito: le date a parole si scrivono in inglese ("
              + c('"saturday 12:00"') + "). Il formato anno-mese-giorno ore:minuti funziona sempre. Una data già "
              "passata viene rifiutata con «la scadenza è già passata».", "Date in italiano.")

S4 = p("Nella TUI il tasto " + key("n") + " apre la schermata " + ui("Nuovo messaggio") + ": tre campi su una riga e "
       "il riquadro del testo.", lead=True) + \
    schermata("nuovo", "«FIG» — La schermata Nuovo messaggio (schermata vera)") + \
    table(["Campo", "Cosa scrivere", "Obbligatorio"], [
        [ui("A"), "i destinatari, come in " + rif(5, 1) + "; a destra, uscendo dal campo, quanti sono", "sì"],
        [ui("Titolo"), "una riga", "no"],
        [ui("Scadenza"), c("30m") + ", " + c("2h") + ", " + c("3d") + " o una data, come in " + rif(5, 3), "no"],
        [ui("Testo"), "il messaggio, su più righe; sotto, il conteggio «85 di 65536 byte»", "sì"],
    ], "«TAB» — I campi del nuovo messaggio") + \
    table(["Tasti", "Cosa fanno"], [
        [key("Tab") + " / " + key("Maiusc", "Tab"), "campo successivo / precedente, compreso il testo"],
        [key("Invio") + " o " + key("↓") + " in un campo", "passa al campo sotto"],
        [key("Invio") + " nel testo", "va a capo"],
        [key("←") + " " + key("→") + " " + key("↑") + " " + key("↓") + ", " + key("Home") + " " + key("Fine"),
         "spostano il cursore"],
        [key("⌫") + " " + key("Canc"), "cancellano un carattere"],
        [key("Ctrl", "E"), "apre il testo nel proprio editor (" + rif(5, 5) + ")"],
        [key("Ctrl", "S"), "invia, dopo il riassunto"],
        [key("Esc"), "lascia perdere; se c'è già qualcosa scritto chiede conferma: " + ui("Lasciare perdere il messaggio?")],
    ], "«TAB» — I tasti del nuovo messaggio") + \
    p(key("Ctrl", "S") + " mostra un riassunto con destinatari (e quanti sono), titolo, scadenza e lunghezza del "
      "testo. " + key("s") + " invia, " + key("n") + " o " + key("Esc") + " torna al messaggio senza perdere nulla.") + \
    schermata("invio", "«FIG» — Il riassunto prima dell'invio") + \
    ul([
        "Se l'invio riesce compare " + ui("Messaggio inviato") + " con la risposta di AMS; un tasto riporta alla lista.",
        "Se qualcosa non va compare " + ui("Esito dell'invio") + " con il motivo: un destinatario sbagliato "
        "(per esempio «ams: utente inesistente: mrio») ferma l'invio, e un tasto riporta al messaggio da correggere; "
        "una copia che non si è potuta scrivere viene elencata, e AMS ritenta da solo al comando successivo.",
    ])

S5 = p("Per i testi lunghi è più comodo il proprio editor. " + key("Ctrl", "E") + " chiude per un momento la TUI e "
       "apre il testo scritto fin lì nell'editor; salvando e uscendo si torna alla TUI con il testo aggiornato.",
       lead=True) + steps([
        "Nel nuovo messaggio premere " + key("Ctrl", "E") + ".",
        "Scrivere o incollare il testo nell'editor, salvare e uscire (con nano: " + key("Ctrl", "O") + ", "
        + key("Invio") + ", " + key("Ctrl", "X") + ").",
        "Controllare il testo nel riquadro e inviare con " + key("Ctrl", "S") + ".",
    ]) + table(["Editor usato", "Quando"], [
        ["quello indicato in " + c("VISUAL") + " o, se manca, in " + c("EDITOR"), "se sudo conserva queste "
         "variabili (" + rif(10, 3) + ")"],
        [c("nano"), "altrimenti"],
        [c("vi"), "se nano non è installato"],
    ], "«TAB» — Quale editor si apre") + \
    note("l'editor gira con l'identità dell'amministratore, non come root: apre un file temporaneo che appartiene "
         "a lui e che AMS cancella al ritorno.", "Sicurezza.")

INVIO = seq([("Amministratore", "Ctrl+S o ams send", "dark"), ("AMS", "archivio", "navy"),
             ("Casella di Mario", "/var/lib/ams/users", "light"), ("Sessioni di Mario", "terminali e desktop", "blue")], [
    (0, 1, "messaggio e destinatari"),
    (1, 1, "copia di riferimento, numero 3"),
    (1, 2, "copia per Mario (come Mario)"),
    ("nota", 2, "consegnato"),
    (1, 3, "testo in ogni terminale aperto"),
    (1, 3, "sveglia l'agente del desktop: finestra"),
    (1, 0, "«Messaggio 3 inviato a 1 utente.»", True),
    ("sep", "dopo, al prompt successivo o all'accesso"),
    (2, 3, "domanda di conferma, finché non conferma"),
], "«FIG» — Che cosa succede quando si invia un messaggio a Mario", "L'invio passo per passo")

S6 = p("All'invio AMS salva il messaggio, ne mette una copia nella casella di ogni destinatario e lo fa comparire "
       "subito dove l'utente è collegato. Tutto avviene in pochi istanti.", lead=True) + INVIO + \
    table(["Risposta di AMS", "Cosa vuol dire"], [
        [c("Messaggio 3 inviato a 24 utenti."), "Tutte le copie sono nelle caselle: ogni destinatario è "
         + CONSEGNATO + "."],
        [c("Messaggio 3 consegnato a 23 destinatari su 24.") + "<br>" + c("ams: messaggio 3 non consegnato a: sara "
         "(vedi il registro; il prossimo comando ams riproverà)"), "Una copia non si è potuta scrivere, di solito per "
         "il disco pieno: Sara è " + INVIATO + ". AMS riprova da solo (" + rif(12, 4) + ")."],
        [c("Messaggio 3 ritirato durante l'invio: consegna interrotta."), "Un altro amministratore l'ha ritirato "
         "mentre partiva."],
        [c("ams: …"), "Un errore: il messaggio non è partito (" + rif(12, 1) + ")."],
    ], "«TAB» — Le risposte dell'invio") + \
    p("Il testo scritto nei terminali all'invio compare anche se l'utente sta lavorando; la domanda di conferma "
      "arriva invece solo quando torna al prompt, per non interromperlo a metà di un comando.")

S7 = table(["Voglio…", "Comando"], [
    ["avvisare un utente e sapere se ha letto", c('ams send --to anna "Il tuo account scade venerdì."')],
    ["avvisare chi è collegato che sto per riavviare",
     c('ams send --to online --expires 15m "Riavvio alle 13:00: salvate il lavoro."')],
    ["informare tutti di una nuova regola", c('ams send --to all --title "Password" --file regola.txt')],
    ["scrivere a un gruppo di lavoro", c('ams send --to @sviluppo --expires 2d "Consegna entro giovedì alle 18."')],
    ["scrivere a due persone e a un gruppo", c('ams send --to mario,anna,@stagisti "Riunione alle 11."')],
    ["mandare l'uscita di un comando", c("df -h /home | ams send --to anna --title \"Spazio disco\"")],
    ["mandare un avviso da cron, ogni lunedì alle 8", c("0 8 * * 1  /usr/local/bin/ams send --to all --file /etc/avviso-settimanale.txt")],
], "«TAB» — Comandi pronti per i casi più comuni") + \
    tip("in cron (quello di root, " + c("sudo crontab -e") + ") " + c("ams") + " è già root e non chiede la "
        "password. Conviene indicare il percorso completo del comando.", "Invii automatici.")

CHAPTER = ("Scrivere e inviare messaggi", [
    ("Scegliere i destinatari", S1),
    ("Titolo e testo", S2),
    ("La scadenza", S3),
    ("Scrivere nella TUI", S4),
    ("Il proprio editor", S5),
    ("Cosa succede all'invio", S6),
    ("Comandi pronti", S7),
])
