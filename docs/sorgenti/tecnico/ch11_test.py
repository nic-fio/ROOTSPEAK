from build import c, p, table, term

S1 = p(c("tests/help-tui.py") + " apre " + c("bin/ams --help") + " (con " + c("AMS_TEST=1") + ") su uno "
       "pseudo-terminale, preme tasti e controlla l'ultimo schermo disegnato dopo ciascuno.", lead=True) + \
    table(["Prova", "Controllo"], [
        ["apertura su 100 × 30", "schermo alternativo, cornice, scheda Info, 30 righe da 100 colonne"],
        [c("→"), "scheda Comandi"],
        [c("3"), "scheda Opzioni"],
        [c("4") + " " + c("G"), "fine della scheda Esempi"],
        [c("PgUp") + " " + c("g"), "inizio della scheda"],
        ["ridimensionamento a 70 × 20", "20 righe da 70 colonne"],
        [c("q"), "ritorno allo schermo principale, uscita con codice 0"],
        ["terminale 40 × 8", "pagina in stile manuale attraverso il pager"],
    ], "«TAB» — Le prove di tests/help-tui.py") + term("nicfio@server:~/AMS$ python3 tests/help-tui.py\nOK")

S2 = table(["Controllo", "Fallisce se"], [
    ["manuali aggiornati", "i due manuali in " + c("docs/") + " non coincidono con quelli rigenerati dai sorgenti"],
    ["riferimento", "una voce di " + c("AMS_HELP_COMMANDS") + " o " + c("AMS_HELP_OPTIONS") + " manca dal manuale utente, "
     "ha una descrizione diversa, o il manuale ne documenta una inesistente"],
    ["mappa dei file", "un file di codice non compare nella mappa del capitolo 3.1, o la mappa ne cita uno inesistente"],
    ["versione", c("AMS_VERSION") + " non compare nei due manuali"],
    ["link", "un link " + c("#ancora") + " non porta a nessun id"],
], "«TAB» — I controlli di tools/check-docs.py") + term(
    "nicfio@server:~/AMS$ tools/check-docs.py\n"
    "documentazione allineata: 2 manuali, 11 voci della guida, 12 file nella mappa, versione 0.1.0")

S3 = p("La consegna reale richiede root, sessioni vere e un desktop, e non è automatizzata. Nella versione 0.1.0 è stata "
       "provata dal vivo su Debian 13 con GNOME 48 su Wayland, con due account.", lead=True) + table(["Provato", "Come"], [
    ["finestra immediata a un utente collegato", "dal vivo"],
    ["finestra al login di un utente non collegato", "dal vivo, con un secondo account"],
    ["testo e domanda nel terminale, anche via ssh", "dal vivo, con " + c("ssh user@localhost")],
    ["conferma unica fra finestra e terminale", "dal vivo"],
    ["avvisi " + c("info") + ", " + c("list") + ", " + c("status"), "dal vivo"],
    [c("revoke") + " con domanda in attesa, scadenze, errori, pulizia del testo", "in modalità di prova"],
], "«TAB» — Cosa è stato provato")

CHAPTER = ("Test e controlli", [
    ("La guida integrata: tests/help-tui.py", S1),
    ("La documentazione: tools/check-docs.py", S2),
    ("Prove dal vivo", S3),
])
