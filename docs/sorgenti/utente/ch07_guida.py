from build import c, key, note, p, table, term

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

S1 = p("Tutto quello che serve per usare " + c("ams") + " è anche dentro il comando stesso. " + c("ams --help")
       + ", oppure " + c("ams") + " da solo, apre una guida a tutto schermo divisa in schede.", lead=True) + \
    term(SCREEN, "La guida integrata, scheda Opzioni", tui=True) + \
    table(["Scheda", "Contiene"], [
        ["Info", "a cosa serve AMS e la forma dei comandi"],
        ["Comandi", c("send") + ", " + c("list") + ", " + c("status") + ", " + c("revoke") + ", " + c("version")],
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

CHAPTER = ("La guida integrata", [
    ("Aprire la guida", S1),
    ("Muoversi nella guida", S2),
    ("Terminali piccoli e testo semplice", S3),
])
