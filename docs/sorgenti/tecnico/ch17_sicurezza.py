from build import arrow, box, c, fig, note, p, table, text, ul, zone


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">capitolo {n}{"." + str(s) if s else ""}</a>'


TRUST = fig(
    zone(20, 44, 270, 220, "Fidato: amministratori")
    + box(44, 84, 222, 56, "ams (root)", "sudo, gruppo admin, 750", "navy")
    + box(44, 158, 222, 56, "sent/ · ams.conf · .mo", "solo root scrive", "dark")
    + zone(330, 44, 240, 220, "Confine")
    + box(352, 84, 196, 56, "come_utente", "figlio con l'identità di U", "green")
    + box(352, 158, 196, 56, "pulisci, limiti", "testi, 200 byte, tempi", "green")
    + zone(610, 44, 270, 220, "Non fidato: utenti")
    + box(634, 84, 222, 56, "users/U/", "casella: U può tutto", "amber")
    + box(634, 158, 222, 56, "acks/ID · environ", "scritti dall'utente", "amber")
    + arrow(268, 112, 350, 112) + arrow(550, 112, 632, 112)
    + arrow(632, 186, 550, 186, "#d97706") + arrow(350, 186, 268, 186, "#d97706")
    + text(450, 238, "tutto ciò che passa", 11.5, "#166534", "700") + text(450, 254, "il confine passa di qui", 11.5, "#166534", "700"),
    900, 282, "«FIG» — Il modello di fiducia di AMS", "Chi è fidato")

S1 = p("Gli amministratori sono fidati: possono già fare tutto sulla macchina, e AMS non li protegge da se stessi. "
       "Gli utenti <b>non</b> sono fidati: controllano la propria casella, i propri terminali, l'ambiente dei propri "
       "processi, e possono scrivere nel journal. Tutto ciò che va da root a un utente, o torna da un utente a root, "
       "attraversa un confine controllato.", lead=True) + TRUST + table(["Direzione", "Che cosa passa", "Controllo"], [
    ["root → casella", "copie, ritiri, solleciti, cancellazioni", "sempre come l'utente, con un tempo massimo ("
     + cap(7) + ")"],
    ["root → terminale", "il testo del messaggio", "ripulito; proprietario del terminale aperto; 3 s al più ("
     + cap(8, 4) + ")"],
    ["root → agente", c("SIGUSR1"), "da un figlio come l'utente, solo al PID pronto con la riga di comando esatta"],
    ["casella → root", "conferme e date dei rinvii", "lette come l'utente, 200 byte, solo file normali, ripulite ("
     + cap(10, 2) + ")"],
    ["processo → root", "l'ambiente per la lingua", "al più 1 MiB; solo codici di lingua validi ("
     + cap(16, 2) + ")"],
    ["journal → root", "eventi con i campi " + c("AMS_*"), c("_UID") + " confrontato con chi doveva scriverli; "
     "gli stati mai dal journal (" + cap(18, 4) + ")"],
], "«TAB» — Il confine, direzione per direzione")

S2 = table(["Rischio", "Contromisura", "Prova"], [
    ["un utente normale usa " + c("ams"), "permessi " + c("750 root:gruppo admin") + "; rilancio con sudo, che "
     "applica le sue regole", "scenari A3, A4"],
    [c("AMS_TEST") + " usata per aggirare sudo", "non concede nulla: senza root un utente resta con i suoi permessi; "
     "le variabili di prova valgono solo in modalità di prova", "scenario G4"],
    ["collegamenti simbolici nella casella", "ogni accesso di root alle caselle in un figlio con l'identità "
     "dell'utente, con un tempo massimo", "scenario G1"],
    ["caselle anomale (pipe, migliaia di file) contro i comandi di root", "si leggono solo file normali e solo i "
     "messaggi esistenti, con un tempo massimo", c("engine.sh") + ", gruppo 9"],
    ["sequenze di escape nei messaggi", c("pulisci") + " su testo e titolo; " + c("--no-markup") + " in zenity",
     "scenario G2"],
    ["conferme fabbricate", "lette come l'utente, al più 200 byte, ripulite; una conferma resta una dichiarazione "
     "dell'utente, non una prova", "scenario G3"],
    ["eventi falsi nel journal", "il journal aggiunge " + c("_UID") + "; " + c("ams log") + " segnala come «non "
     "attendibile» un evento scritto dall'utente sbagliato; gli stati si leggono dall'archivio", "scenario J3"],
    ["testo destinato a un utente scritto sul terminale di un altro", "si controlla il proprietario del terminale "
     "dopo averlo aperto, non il nome " + c("/dev/pts/N"), c("engine.sh") + ", gruppo 9"],
    ["segnali a processi sbagliati", "il segnale parte da un figlio con l'identità dell'utente, e solo verso il "
     "PID pronto con la riga di comando esatta dell'agente", c("engine.sh") + ", gruppo 7"],
    ["un terminale bloccato ferma l'invio", "scrittura non bloccante, al più 3 s per terminale", "—"],
    ["un utente ferma il figlio di root (" + c("SIGSTOP") + ")", "tempo massimo anche dopo la fine dell'uscita, poi "
     + c("SIGKILL"), "—"],
    ["configurazione come codice", c("ams.conf") + " è un file di dati: due chiavi, interi positivi", c("engine.sh")
     + ", gruppo 5"],
    ["un editor aperto come root dalla TUI", "l'editor gira con l'identità dell'amministratore di "
     + c("SUDO_USER"), "—"],
    ["testo troppo lungo per la finestra", "al più 65536 byte: zenity riceve il testo come argomento, e Linux non "
     "accetta argomenti oltre 128 KiB", c("engine.sh") + ", gruppo 9"],
    ["messaggi letti da altri utenti", "caselle " + c("700") + "; " + c("sent/") + " di root " + c("700"), "—"],
    ["errori di memoria in un programma di root", "le difese del compilatore, l'analisi statica, i sanitizer, il "
     "fuzzing (" + cap(17, 3) + ")", cap(21, 7)],
], "«TAB» — Rischi e contromisure") + \
    note("fuori dal modello: un collegamento simbolico " + c("/var/lib/ams") + " creato prima dell'installazione. "
         "In " + c("/var/lib") + " scrive solo root, che è già fidato (seconda revisione, rilievo non accolto).")

S3 = p("Un programma di root in C che legge dati degli utenti non deve avere errori di memoria. Oltre alle regole "
       "di scrittura (" + c("buf_t") + " per ogni testo che viene da fuori, nessun array a lunghezza variabile, "
       + c("O_CLOEXEC") + " ovunque), il codice è compilato con le difese che gcc e il linker offrono.", lead=True) + \
    table(["Opzione", "Che cosa fa"], [
        [c("-Wall -Wextra -Wpedantic … -Werror"), "tutti gli avvisi utili, come errori: fra gli altri formati ("
         + c("-Wformat=2") + ", " + c("-Wformat-security") + "), nomi che si nascondono (" + c("-Wshadow")
         + "), puntatori nulli (" + c("-Wnull-dereference") + "), array a lunghezza variabile (" + c("-Wvla") + ")"],
        [c("-D_FORTIFY_SOURCE=3"), "controlli sulle dimensioni nelle funzioni di libreria (copie, formati)"],
        [c("-fstack-protector-strong"), "un canarino sullo stack delle funzioni con array o indirizzi di variabili "
         "locali"],
        [c("-fstack-clash-protection"), "lo stack non può saltare oltre la pagina di guardia"],
        [c("-fcf-protection"), "protezione del flusso di controllo (dove il processore la offre)"],
        [c("-fPIE -pie"), "eseguibile a indirizzi casuali"],
        [c("-z relro -z now"), "tabelle di collegamento in sola lettura dopo l'avvio"],
        [c("-z noexecstack"), "stack non eseguibile"],
        [c("-fanalyzer") + " (" + c("make analizza") + ")", "analisi statica di gcc: percorsi d'errore, descrittori "
         "non chiusi, uso dopo la liberazione"],
        [c("-fsanitize=address,undefined") + " (" + c("make sanitizer") + ")", "AddressSanitizer e UBSan nelle "
         "prove: ogni accesso fuori dai limiti o comportamento indefinito ferma la prova"],
    ], "«TAB» — Le difese del compilatore (Makefile)") + ul([
    "Il fuzzing con libFuzzer (" + c("tests/fuzz/") + ") prova, con AddressSanitizer e UBSan, tutto ciò che legge "
    "dati non fidati: pulizia del testo, formato dei messaggi, uscita della lettura delle caselle, ambiente di un "
    "processo, configurazione, cataloghi " + c(".mo") + ".",
    "La scelta del C, invece di un linguaggio che eviti per costruzione gli errori di memoria, è dell'utente: le "
    "difese di questa tabella sono la condizione con cui è stata presa (" + cap(22, 3) + ").",
])

CHAPTER = ("Sicurezza", [
    ("Il modello di fiducia", S1),
    ("Rischi e contromisure", S2),
    ("Le difese del compilatore", S3),
])
