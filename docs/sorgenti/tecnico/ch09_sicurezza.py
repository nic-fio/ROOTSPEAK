from build import arrow, box, c, fig, p, table, text, zone

TRUST = fig(
    zone(20, 44, 270, 220, "Fidato: amministratori")
    + box(44, 84, 222, 56, "ams (root)", "sudo, gruppo admin, 750", "navy")
    + box(44, 158, 222, 56, "sent/ · ams.conf", "solo root scrive", "dark")
    + zone(330, 44, 240, 220, "Confine")
    + box(352, 84, 196, 56, "as_user / runuser", "identità dell'utente", "green")
    + box(352, 158, 196, 56, "ams_sanitize", "testo e conferme", "green")
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
    ["collegamenti simbolici nella casella", "ogni accesso di root alle caselle passa da " + c("as_user") + " (capitolo 5.3)"],
    ["sequenze di escape nei messaggi", c("ams_sanitize") + " su testo e titolo; " + c("--no-markup") + " in zenity"],
    ["conferme fabbricate", "lette come l'utente, al massimo 200 byte, ripulite (capitolo 8.2); nel journal ogni "
     "conferma porta " + c("_UID") + ", l'utente che l'ha scritta, messo dal journal e non falsificabile"],
    ["segnali a processi sbagliati", c("pkill") + " eseguito come l'utente, sulla riga di comando esatta dell'agente"],
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
