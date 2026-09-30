import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import box, c, fig, note, p, table, term, text, tip, tree, ul, warn, zone  # noqa: E402
from _aiuti import CONFERMATO, rif  # noqa: E402

S1 = p("Solo gli amministratori della macchina possono usare " + c("ams") + ": i membri del gruppo " + c("sudo")
       + " (su Fedora e simili " + c("wheel") + "). AMS non ha un elenco suo: chi entra o esce dal gruppo ottiene o "
       "perde l'accesso dal suo prossimo accesso alla macchina (" + rif(2, 4) + ").", lead=True) + term(
    "mario@server:~$ ams list\n"
    "bash: /usr/local/bin/ams: Permesso negato", "Un utente normale non può nemmeno avviare il comando") + \
    ul([
        c("ams") + " lavora sempre come amministratore, anche per mostrare la guida o la versione: se non è già "
        "root, si rilancia da solo con sudo, che chiede la password.",
        "Nei messaggi e nel registro l'autore è l'amministratore che ha usato sudo, non un generico «root»: «messaggio "
        "3 inviato da admin a: …». Chi lancia " + c("ams") + " direttamente da root (per esempio da cron) compare "
        "come " + c("root") + ".",
        "Gli utenti non hanno alcun comando di AMS: non possono mandare messaggi né vedere chi ha confermato.",
    ])

CASELLE = fig(
    zone(20, 44, 860, 110, "/var/lib/ams/sent/: le copie di riferimento")
    + box(44, 84, 250, 52, "solo root", "gli amministratori, con ams", "dark")
    + text(600, 104, "messaggio, destinatari, consegne, ritiro:", 12, "#334155")
    + text(600, 122, "è da qui che ams status legge chi è stato raggiunto", 12, "#334155")
    + zone(20, 170, 860, 150, "/var/lib/ams/users/: una casella per utente")
    + box(44, 210, 190, 52, "users/mario/", "solo Mario (e root)", "blue")
    + box(254, 210, 190, 52, "users/anna/", "solo Anna (e root)", "blue")
    + box(464, 210, 190, 52, "users/luca/", "solo Luca (e root)", "blue")
    + text(770, 232, "da leggere", 12, "#334155") + text(770, 250, "conferme, rinvii", 12, "#334155")
    + text(450, 296, "Anna non può aprire la casella di Mario, e nessun utente può aprire sent/", 12, "#991b1b", "600"),
    900, 340, "«FIG» — Chi può leggere cosa nell'archivio di AMS", "L'archivio dei messaggi")

S2 = p("Ogni utente vede solo i messaggi mandati a lui. L'archivio in " + c("/var/lib/ams/") + " è diviso in due "
       "parti con permessi diversi.", lead=True) + CASELLE + \
    tree([
        "/var/lib/ams/  # root, leggibile da tutti (solo l'elenco)",
        "├── sent/  # root, 700: solo root",
        "│   └── 3/  # il messaggio 3: testo, destinatari, consegne, ritiro",
        "└── users/",
        "    └── mario/  # di Mario, 700: solo Mario e root",
        "        ├── inbox/  # messaggi da confermare",
        "        ├── read/  # messaggi confermati o scaduti",
        "        ├── acks/  # le conferme, con data e canale",
        "        └── state/  # i rinvii",
    ], "«FIG» — L'archivio visto dall'alto") + \
    table(["Chi", "Cosa vede"], [
        ["un amministratore", "tutti i messaggi mandati, i destinatari, le conferme, la storia"],
        ["un utente", "solo i messaggi indirizzati a lui, uno alla volta, finché non li conferma"],
        ["gli altri utenti", "nulla dei messaggi di un collega, nemmeno che esistano"],
    ], "«TAB» — Chi vede cosa") + \
    note("AMS entra nella casella di un utente sempre con l'identità di quell'utente, anche quando lo comanda "
         "l'amministratore: così un utente non può ingannare root facendogli scrivere dove non dovrebbe.",
         "Root non entra da root.")

S3 = p("La conferma registra che l'utente <b>dichiara</b> di aver letto il messaggio, con data, ora e canale, come le "
       "spunte di lettura di un'app di messaggistica. Non può provare che l'abbia letto davvero.", lead=True) + \
    table(["La conferma dice", "La conferma non dice"], [
        ["che l'utente ha premuto «Ho letto» o risposto «s»", "che ha letto con attenzione"],
        ["quando (giorno e ora) e da dove (desktop o quale terminale)", "chi c'era davanti allo schermo"],
        ["che il messaggio non era scaduto né ritirato in quel momento", "che ha capito il contenuto"],
    ], "«TAB» — Il valore di una conferma") + \
    note("la casella è dell'utente: un utente esperto potrebbe registrare una conferma senza aprire la finestra. "
         "Resta comunque una sua dichiarazione, come il clic su «Ho letto».", "Una dichiarazione.") + \
    tip("per gli avvisi che richiedono un impegno vero (una regola da rispettare, un'autorizzazione) la conferma di AMS "
        "è un promemoria, non una firma: serve un documento a parte.", "Quando serve di più.")

PULIZIA = fig(
    box(30, 60, 250, 70, "Testo incollato", "con colori, titoli, caratteri invisibili", "grey")
    + box(325, 60, 250, 70, "AMS lo pulisce", "prima di salvarlo", "navy")
    + box(620, 60, 250, 70, "Testo sicuro", "lettere, tabulazioni, a capo", "green")
    + '<path d="M282 95 H 321" stroke="#0050C0" stroke-width="2.2"/><path d="M577 95 H 616" stroke="#0050C0" stroke-width="2.2"/>'
    + text(450, 160, "nessun messaggio può cambiare colori, titolo o comportamento del terminale di un utente",
           11.5, "#334155", "600"),
    900, 180, "«FIG» — Il testo di ogni messaggio viene ripulito prima di essere salvato", "Testo sicuro")

S4 = p("Prima di salvare un messaggio, AMS toglie dal testo e dal titolo i caratteri invisibili e i codici che "
       "cambiano colori, titolo o comportamento delle finestre di terminale. Un messaggio non può quindi alterare i "
       "terminali degli utenti, anche se il testo è stato incollato da una fonte sconosciuta.", lead=True) + PULIZIA + \
    table(["Nel testo", "Cosa succede"], [
        ["lettere, numeri, punteggiatura, lettere accentate, simboli", "restano"],
        ["tabulazioni e a capo", "restano (nel titolo gli a capo diventano spazi)"],
        ["codici di colore e di movimento del cursore", "tolti"],
        ["codici che cambiano il titolo della finestra del terminale", "tolti"],
        ["altri caratteri di controllo invisibili", "tolti"],
    ], "«TAB» — Cosa resta del testo") + \
    p("Anche ciò che AMS legge dalle caselle degli utenti (conferme, rinvii) viene ripulito prima di mostrarlo "
      "all'amministratore.")

S5 = p("Il registro di sistema è una traccia comoda, ma chiunque sulla macchina può scriverci righe con l'etichetta "
       + c("ams") + ". Per questo " + c("ams log") + " e la TUI controllano chi ha scritto davvero ogni evento e "
       "segnalano quelli sospetti.", lead=True) + term(
    "admin@server:~$ ams log 3\n"
    "Messaggio 3 · Nuova regola per le password · 30/09 19:05\n"
    "2026-09-30 19:05:12  messaggio 3 consegnato a anna (terminali scritti: 1)\n"
    "2026-09-30 19:05:12  messaggio 3 inviato da admin a: anna luca\n"
    "2026-09-30 19:06:40  [non attendibile: scritto da UID 1003] utente anna: confermata la lettura del messaggio 3 (desktop)",
    "Una conferma falsa: Luca (UID 1003) ha scritto una riga a nome di Anna") + \
    table(["Evento", "Deve averlo scritto"], [
        ["invio, consegna, sollecito, ritiro, cancellazione", "root (cioè " + c("ams") + ")"],
        ["rinvio, conferma, conferma non registrata", "l'utente di cui parla"],
    ], "«TAB» — Chi scrive ogni evento") + \
    warn("una riga «non attendibile» non va considerata. Lo stato vero di un destinatario è quello del dettaglio del "
         "messaggio e di " + c("ams status") + ", che non viene dal registro ma dall'archivio: lì " + CONFERMATO
         + " vuol dire che la conferma è nella casella dell'utente.", "Fidarsi dello stato.")

CHAPTER = ("Sicurezza e riservatezza", [
    ("Chi può usare AMS", S1),
    ("Chi vede i messaggi", S2),
    ("Cosa vale una conferma", S3),
    ("Testo sicuro", S4),
    ("L'affidabilità del registro", S5),
])
