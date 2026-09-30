from build import c, key, note, p, schermata, table, term, tip, ul

SCREEN = """┌─ ams — guida ──────────────────────────────────────────────────────┐
│  Info  Comandi  Opzioni  Esempi  File                              │
├────────────────────────────────────────────────────────────────────┤
│ Opzioni di send                                                    │
│                                                                    │
│  --to DEST                                                         │
│     Destinatari, separati da virgole senza spazi: un utente        │
│     (mario), un gruppo Unix (@sviluppo), all (tutti gli utenti     │
│     umani) oppure online (solo quelli collegati adesso).           │
│                                                                    │
│  --title TITOLO                                                    │
│     Titolo mostrato nell'intestazione del messaggio e nella        │
│     finestra del desktop.                                          │
├────────────────────────────────────────────────────────────────────┤
│ ←/→ schede · ↑/↓ scorri · PgUp/PgDn · g/G · q esci   righe 1-10/18 │
└────────────────────────────────────────────────────────────────────┘"""

T1 = p("Scritto da solo in un terminale, " + c("ams") + " apre un'interfaccia a tutto schermo: la lista dei messaggi, "
       "con chi ha confermato e chi no, da cui si apre ogni messaggio, se ne scrive uno nuovo, si ritira, si "
       "sollecita. È la stessa cosa dei comandi, con tutto sotto gli occhi.", lead=True) + \
    schermata("lista", "«FIG» — La lista dei messaggi (schermata vera della TUI)") + ul([
        "Ogni riga è un messaggio, dal più recente. La barra e la frase dicono quanti destinatari sono in ciascuno "
        "dei tre stati: " + "<b>confermato</b> (verde), <b>consegnato</b> (giallo: ha la copia ma non ha ancora "
        "confermato), <b>inviato</b> (rosso: la copia non è ancora arrivata). «tutti confermato» vuol dire che hanno "
        "confermato tutti.",
        c("[ritirato]") + " e " + c("[scaduto]") + " segnalano i messaggi che non vengono più mostrati.",
        "La lista si aggiorna da sola ogni 3 secondi: si vedono arrivare le conferme. In alto a destra, l'ora "
        "dell'ultimo aggiornamento.",
        "In un terminale stretto (meno di 110 colonne) al posto della frase c'è il numero di conferme sul totale, "
        "per esempio " + c("4/8") + ". Sotto 80 colonne o 20 righe si apre la guida.",
    ])

T2 = p("Con " + key("Invio") + " si apre il messaggio scelto: il testo, e sotto due schede.", lead=True) + \
    schermata("dettaglio", "«FIG» — Un messaggio: lo stato di ogni destinatario") + \
    p("La scheda <b>Destinatari</b> mostra per ogni utente lo stesso stato di " + c("ams status") + "; "
      + key("Tab") + " passa alla scheda <b>Storia</b>, con gli eventi del registro di sistema, come "
      + c("ams log") + ".") + \
    schermata("storia", "«FIG» — La storia di un messaggio")

T3 = p("Con " + key("n") + " si scrive un messaggio nuovo.", lead=True) + \
    schermata("nuovo", "«FIG» — Un messaggio nuovo") + ul([
        "<b>A</b>: destinatari come per " + c("--to") + ": un utente, un " + c("@gruppo") + ", " + c("all")
        + " o " + c("online") + ", separati da virgole. Passando al campo successivo, a destra compare quanti "
        "destinatari sono (o l'errore, se un nome non esiste).",
        "<b>Titolo</b> e <b>Scadenza</b> sono facoltativi; la scadenza si scrive come per " + c("--expires") + ".",
        "Nel riquadro del <b>Testo</b> si scrive su più righe; " + key("Ctrl") + "+" + key("E") + " apre il testo "
        "nel proprio editor (quello di " + c("EDITOR") + ", altrimenti nano), comodo per i testi lunghi.",
        key("Ctrl") + "+" + key("S") + " invia, dopo una conferma che riassume destinatari, titolo e scadenza; "
        + key("Esc") + " lascia perdere.",
    ]) + schermata("invio", "«FIG» — La conferma prima dell'invio")

T4 = p("Nessuna azione parte senza una conferma: il messaggio da ritirare, le persone da sollecitare, i messaggi "
       "da cancellare sono sempre scritti prima.", lead=True) + \
    schermata("sollecito", "«FIG» — La conferma di un sollecito") + \
    table(["Tasti", "Azione"], [
        [key("↑") + " " + key("↓") + ", " + key("PgUp") + " " + key("PgDn"), "scorri la lista"],
        [key("Invio"), "apri il messaggio: destinatari e storia (" + key("Tab") + " tra le due schede, "
         + key("Esc") + " per tornare)"],
        [key("n"), "scrivi e invia un messaggio nuovo"],
        [key("r"), "ritira il messaggio scelto (come " + c("ams revoke") + ")"],
        [key("s"), "sollecita chi non ha confermato (come " + c("ams remind") + ")"],
        [key("p"), "cancella i messaggi più vecchi di una durata (come " + c("ams purge") + ")"],
        [key("/"), "mostra solo i messaggi che contengono un testo; " + key("Esc") + " toglie la ricerca"],
        [key("?"), "l'elenco dei tasti"],
        [key("q"), "esci"],
    ], "«TAB» — I tasti della TUI") + \
    tip("ogni azione della TUI è il comando corrispondente: stesso risultato, stessi messaggi, stessa traccia nel "
        "registro di sistema.", "Stessi comandi.")

S1 = p("Tutto quello che serve per usare " + c("ams") + " è anche dentro il comando stesso: " + c("ams --help")
       + " apre una guida a tutto schermo divisa in schede.", lead=True) + \
    term(SCREEN, "La guida integrata, scheda Opzioni", tui=True) + \
    table(["Scheda", "Contiene"], [
        ["Info", "a cosa serve AMS e la forma dei comandi"],
        ["Comandi", c("ams") + " da solo, " + c("send") + ", " + c("list") + ", " + c("status") + ", " + c("revoke")
         + ", " + c("remind") + ", " + c("log") + ", " + c("purge") + ", " + c("version")],
        ["Opzioni", "le opzioni di " + c("send") + ": destinatari, titolo, scadenza, file"],
        ["Esempi", "comandi pronti da copiare"],
        ["File", "dove stanno impostazioni, messaggi, registro e manuali"],
    ], "«TAB» — Le schede della guida") + \
    note("come ogni comando di " + c("ams") + ", anche la guida chiede la password di sudo.")

S2 = table(["Tasti", "Azione"], [
    [key("←") + " " + key("→") + ", " + key("Tab") + ", " + key("Invio"), "scheda precedente o successiva"],
    [key("1") + " … " + key("5"), "vai direttamente a una scheda"],
    [key("↑") + " " + key("↓"), "scorri di una riga"],
    [key("PgUp") + " " + key("PgDn") + ", " + key("spazio"), "scorri di una pagina"],
    [key("g") + " " + key("G") + ", " + key("Home") + " " + key("End"), "inizio o fine della scheda"],
    [key("q") + ", " + key("Esc"), "esci dalla guida"],
], "«TAB» — I tasti della guida") + \
    p("La guida si adatta quando si ridimensiona la finestra. All'uscita il terminale torna esattamente com'era.")

S3 = table(["Situazione", "Cosa mostra " + c("ams --help")], [
    ["un terminale normale", "la guida a schede"],
    ["un terminale molto piccolo (meno di 44 colonne o 10 righe)", "la stessa guida come pagina unica, da scorrere con le frecce; " + key("q") + " per uscire"],
    ["l'uscita va in un file o in un altro comando", "testo semplice, per esempio " + c("ams --help | grep expires")],
], "«TAB» — La guida nelle diverse situazioni")

CHAPTER = ("La TUI e la guida integrata", [
    ("La lista dei messaggi", T1),
    ("Un messaggio: destinatari e storia", T2),
    ("Scrivere e inviare", T3),
    ("Azioni e tasti", T4),
    ("Aprire la guida", S1),
    ("Muoversi nella guida", S2),
    ("Terminali piccoli e testo semplice", S3),
])
