from build import c, esc, help_items, help_reference, p, table

S1 = p("I comandi di " + c("ams") + ". I testi sono gli stessi della guida integrata (" + c("ams --help")
       + "), da cui questa pagina è generata.", lead=True) + help_reference("AMS_HELP_COMMANDS", "command")

S2 = p("Le opzioni di " + c("ams send") + ". Vanno scritte prima del testo del messaggio.", lead=True) + \
    help_reference("AMS_HELP_OPTIONS", "option")

S3 = table(["Comando", "Cosa fa"], [[c(cmd), esc(desc)] for cmd, desc in help_items("AMS_HELP_EXAMPLES")],
           "«TAB» — Gli esempi della guida integrata")

CHAPTER = ("Riferimento dei comandi", [
    ("Comandi", S1),
    ("Opzioni di send", S2),
    ("Esempi", S3),
])
