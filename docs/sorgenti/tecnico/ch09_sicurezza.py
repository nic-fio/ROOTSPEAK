from build import arrow, box, c, fig, p, table, text, zone

TRUST = fig(
    zone(20, 44, 270, 220, "Fidato: amministratori")
    + box(44, 84, 222, 56, "ams (root)", "sudo, gruppo admin, 750", "navy")
    + box(44, 158, 222, 56, "sent/ · ams.conf", "solo root scrive", "dark")
    + zone(330, 44, 240, 220, "Confine")
    + box(352, 84, 196, 56, "come_utente", "figlio con l'identità dell'utente", "green")
    + box(352, 158, 196, 56, "pulisci", "testo e conferme", "green")
    + zone(610, 44, 270, 220, "Non fidato: utenti")
    + box(634, 84, 222, 56, "users/U/", "casella: U può tutto", "amber")
    + box(634, 158, 222, 56, "acks/ID", "scritto dall'utente", "amber")
    + arrow(268, 112, 350, 112) + arrow(550, 112, 632, 112)
    + arrow(632, 186, 550, 186, "#d97706") + arrow(350, 186, 268, 186, "#d97706")
    + text(450, 250, "tutto ciò che passa il confine passa di qui", 11.5, "#166534", "700"),
    900, 282, "«FIG» — Il modello di fiducia di AMS", "Chi è fidato")

S1 = p("Gli amministratori sono fidati; gli utenti no. Tutto ciò che va da root a una casella, o torna da una casella a "
       "root, attraversa un confine controllato.", lead=True) + TRUST

S2 = table(["Rischio", "Contromisura"], [
    ["un utente normale usa " + c("ams"), "permessi " + c("750 root:gruppo admin") + "; rilancio con sudo, che applica le sue regole"],
    ["collegamenti simbolici nella casella", "ogni accesso di root alle caselle avviene in un figlio con l'identità dell'utente, con un tempo massimo (capitolo 5.3)"],
    ["sequenze di escape nei messaggi", c("pulisci") + " su testo e titolo; " + c("--no-markup") + " in zenity"],
    ["conferme fabbricate", "lette come l'utente, al massimo 200 byte, ripulite (capitolo 8.2); una conferma resta "
     "comunque una dichiarazione dell'utente, non una prova (capitolo 14.1)"],
    ["eventi falsi nel journal", "chiunque può scrivere un evento con i campi " + c("AMS_*") + ", ma il journal "
     "aggiunge " + c("_UID") + ", l'utente che l'ha scritto davvero; " + c("ams log") + " segnala come «non "
     "attendibile» un evento scritto dall'utente sbagliato; gli stati si leggono dall'archivio, mai dal journal"],
    ["testo destinato a un utente scritto sul terminale di un altro", "si controlla il proprietario del terminale "
     "dopo averlo aperto, non del nome " + c("/dev/pts/N") + " (capitolo 5.5)"],
    ["caselle anomale (pipe, migliaia di file) contro i comandi di root", "si leggono solo file normali e solo i "
     "messaggi esistenti, con un tempo massimo (capitolo 5.9)"],
    ["testo troppo lungo per la finestra", "al più 65536 byte: zenity riceve il testo come argomento, e Linux non "
     "accetta argomenti oltre 128 KiB"],
    ["segnali a processi sbagliati", "il segnale parte da un figlio con l'identità dell'utente, e solo verso il PID "
     "pronto con la riga di comando esatta dell'agente"],
    ["errori di memoria in un programma di root", "C compilato con tutti gli avvisi come errori e le difese di gcc "
     "(" + c("_FORTIFY_SOURCE=3") + ", stack protector, PIE, RELRO); " + c("-fanalyzer") + "; tutte le prove anche con "
     "AddressSanitizer e UBSan; fuzzing di ciò che legge dati degli utenti (capitolo 11)"],
    ["configurazione come codice", c("ams.conf") + " è un file di dati: " + c("ams_load_conf") + " accetta solo le chiavi "
     "note con valori interi positivi e non esegue nulla (prima era letto come script da root e dagli utenti)"],
    ["messaggi letti da altri utenti", "caselle " + c("700") + "; " + c("sent/ 700 root")],
    ["un terminale bloccato ferma l'invio", c("timeout 3") + " su ogni scrittura"],
    [c("AMS_TEST") + " usata per aggirare sudo", "non concede nulla: senza root, un utente resta con i suoi permessi; sudo toglie la variabile"],
], "«TAB» — Rischi e contromisure")

CHAPTER = ("Sicurezza", [
    ("Il modello di fiducia", S1),
    ("Rischi e contromisure", S2),
])
