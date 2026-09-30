from build import arrow, box, c, diamond, fig, p, path, table, text, ul

SOURCES = fig(
    box(20, 120, 190, 64, "lib/ams-help.sh", "AMS_HELP_* : «etichetta¦testo»", "navy")
    + box(290, 30, 190, 54, "guida a schede", "_help_tui", "blue")
    + box(290, 110, 190, 54, "pagina con pager", "_help_page a colori", "blue")
    + box(290, 190, 190, 54, "testo semplice", "_help_page 0 80", "blue")
    + box(570, 70, 150, 54, "build.py", "help_reference", "dark")
    + box(760, 70, 120, 54, "Manuale", "capitolo 11", "light")
    + box(570, 190, 310, 54, "tools/check-docs.py", "manuale generato = guida", "green")
    + arrow(212, 140, 288, 60) + arrow(212, 152, 288, 137) + arrow(212, 164, 288, 214)
    + path([(200, 118), (200, 14), (645, 14), (645, 68)], "#0050C0")
    + arrow(722, 97, 758, 97)
    + arrow(645, 126, 645, 188, "#16a34a", True),
    900, 262, "«FIG» — Una sola fonte per guida, pagina, testo e riferimento del manuale", "Da dove vengono i testi")

S1 = p("I testi della guida stanno solo in " + c("lib/ams-help.sh") + ", in array bash con voci "
       + c("\"etichetta¦descrizione\"") + ": " + c("AMS_HELP_COMMANDS") + ", " + c("AMS_HELP_OPTIONS") + ", "
       + c("AMS_HELP_EXAMPLES") + ", " + c("AMS_HELP_FILES") + ", più sintassi e descrizione.", lead=True) + SOURCES + \
    p("Il generatore dei manuali legge gli stessi array e ne ricava il riferimento del manuale utente, con l'attributo "
      + c("data-help") + " su ogni voce; " + c("tools/check-docs.py") + " controlla che coincidano.")

LEVELS = fig(
    diamond(170, 90, 240, 80, "stdin e stdout terminali?", "navy")
    + diamond(470, 90, 230, 80, "almeno 44 × 10?", "navy")
    + box(640, 62, 240, 56, "guida a schede", "_help_tui", "blue")
    + box(50, 190, 240, 56, "testo semplice, 80 colonne", "senza colori", "dark")
    + box(355, 190, 240, 56, "pagina in stile manuale", "$PAGER o less -R -F -X", "light")
    + arrow(292, 90, 353, 90, "#0050C0", False, "sì", 322, 80)
    + arrow(587, 90, 638, 90, "#0050C0", False, "sì", 612, 80)
    + arrow(170, 132, 170, 188, "#475569", False, "no", 186, 164)
    + arrow(470, 132, 470, 188, "#475569", False, "no", 486, 164),
    900, 266, "«FIG» — Quale forma prende ams --help", "")

S2 = LEVELS + p(c("ams_help") + " disattiva " + c("-e") + " e " + c("-u") + " di " + c("bin/ams") + " e sceglie la forma. "
                "Colori disattivati con " + c("NO_COLOR") + "; " + c("PAGER") + " e " + c("NO_COLOR")
                + " arrivano solo se sudo li conserva.")

S3 = table(["Parte", "Come funziona"], [
    ["terminale", c("stty -echo -icanon") + ", schermo alternativo e cursore nascosto; " + c("_help_restore")
     + " rimette tutto com'era all'uscita e su " + c("INT") + ", " + c("TERM") + ", " + c("HUP")],
    ["tasti", c("_help_key") + " legge un carattere con " + c("read -rsn1 -t 0.3") + "; dopo " + c("ESC")
     + " legge il resto con un'attesa breve: " + c("ESC") + " da solo esce, frecce e " + c("PgUp") + " vengono riconosciuti"],
    ["ridimensionamento", "bash non interrompe " + c("read") + " su " + c("SIGWINCH") + ": a ogni scadenza di 0,3 s la "
     "guida confronta " + c("stty size") + " con l'ultima dimensione e ridisegna"],
    ["disegno", c("_help_tab_lines") + " prepara le righe senza colori, così le lunghezze sono quelle visibili; "
     + c("_help_draw") + " compone cornice, schede e stato e scrive tutto con un solo " + c("printf")],
    ["codifica", "le lunghezze sono in caratteri con una localizzazione UTF-8; con " + c("C") + " la cornice si "
     "disallinea sulle lettere accentate"],
], "«TAB» — La guida a schede")

CHAPTER = ("La guida integrata", [
    ("Una sola fonte", S1),
    ("Le tre forme", S2),
    ("La guida a schede", S3),
])
