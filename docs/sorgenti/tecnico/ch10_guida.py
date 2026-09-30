from build import arrow, box, c, diamond, fig, p, path, table, text, ul

SOURCES = fig(
    box(20, 120, 190, 64, "lingue/aiuto-it.sh", "AMS_HELP_* : «etichetta¦testo»", "navy")
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

S1 = p("I testi della guida stanno in " + c("lib/lingue/aiuto-LINGUA.sh") + " (uno per lingua; " + c("lib/ams-help.sh")
       + " ha solo il codice), in array bash con voci "
       + c("\"etichetta¦descrizione\"") + ": " + c("AMS_HELP_COMMANDS") + ", " + c("AMS_HELP_OPTIONS") + ", "
       + c("AMS_HELP_EXAMPLES") + ", " + c("AMS_HELP_FILES") + ", più sintassi e descrizione.", lead=True) + SOURCES + \
    p("Il generatore dei manuali legge gli array italiani e ne ricava il riferimento del manuale utente, con l'attributo "
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

LINGUE = fig(
    box(20, 30, 200, 54, "amministratore", "ambiente dopo sudo", "dark")
    + box(20, 110, 200, 54, "terminale dell'utente", "/proc/PID/environ", "dark")
    + box(20, 190, 200, 54, "shell, agente", "il loro ambiente", "dark")
    + box(330, 110, 220, 54, "ams_pick_lang", "regole di gettext", "navy")
    + box(660, 30, 220, 54, "lingue/it.sh, en.sh", "AMS_T_xx[chiave]", "blue")
    + box(660, 110, 220, 54, "lingue/aiuto-xx.sh", "guida", "blue")
    + box(660, 190, 220, 54, "inglese", "se la lingua non c'è", "light")
    + arrow(222, 57, 328, 128) + arrow(222, 137, 328, 137) + arrow(222, 217, 328, 146)
    + arrow(552, 130, 658, 60) + arrow(552, 137, 658, 137) + arrow(552, 144, 658, 214, "#475569"),
    900, 262, "«FIG» — Da dove viene la lingua, e dove sono i testi", "Ognuno nella sua lingua")

S4 = p("Ogni persona legge AMS nella sua lingua; il testo dei messaggi non si traduce.", lead=True) + LINGUE + \
    table(["Chi legge", "Lingua", "Da dove"], [
        ["l'amministratore: uscite, errori, guida", "la sua", "il suo ambiente: sudo conserva " + c("LANG") + ", " + c("LANGUAGE") + " e " + c("LC_*")],
        ["l'utente, all'invio: l'intestazione nel terminale", "quella del terminale",
         "l'ambiente del primo processo del terminale, di solito la shell; se root non può leggerlo (un container "
         "senza " + c("CAP_SYS_PTRACE") + "), lo legge l'utente stesso con " + c("as_user")],
        ["l'utente, al prompt: domanda e risposte", "quella della shell", "l'ambiente di " + c("ams-user prompt")],
        ["l'utente, sul desktop: finestra e notifiche", "quella della sessione grafica", "l'ambiente dell'agente"],
        ["il journal", "quella del sistema", c("/etc/default/locale") + " o " + c("/etc/locale.conf")],
    ], "«TAB» — Chi legge in quale lingua") + ul([
    c("ams_pick_lang") + " segue gettext: conta il primo impostato fra " + c("LC_ALL") + ", " + c("LC_MESSAGES")
    + " e " + c("LANG") + "; con " + c("C") + " o " + c("POSIX") + " vale l'inglese, altrimenti si prova prima "
    "l'elenco di " + c("LANGUAGE") + ". Vince la prima lingua che ha un file in " + c("lib/lingue/") + "; se nessuna, "
    "l'inglese. Un valore che non è un codice di lettere (" + c("../") + ", " + c("/") + ") non porta mai a leggere un file.",
    "I testi sono formati di " + c("printf") + " con " + c("%s") + " al posto dei dati, in array associativi "
    + c("AMS_T_it") + ", " + c("AMS_T_en") + ": " + c("t CHIAVE dati") + " stampa nella lingua di chi usa AMS, "
    + c("tl LINGUA CHIAVE dati") + " in una lingua data, " + c("tv VARIABILE CHIAVE dati") + " scrive in una "
    "variabile senza sottoprocessi (per i cicli di " + c("ams status") + ").",
    "Ciò che si salva resta senza lingua: il canale di una conferma è " + c("terminale pts/N") + " o " + c("desktop")
    + " e si traduce solo quando si mostra (" + c("ams_channel") + "); gli eventi si riscrivono dai campi.",
    "La domanda accetta " + c("s") + ", " + c("S") + ", " + c("y") + " e " + c("Y") + " in ogni lingua.",
    c("tools/check-docs.py") + " controlla che ogni lingua abbia le stesse chiavi, con lo stesso numero di " + c("%s")
    + ", e la guida le stesse voci. Per una lingua nuova bastano " + c("lib/lingue/XX.sh") + " e "
    + c("lib/lingue/aiuto-XX.sh") + ".",
])

CHAPTER = ("La guida integrata e le lingue", [
    ("Una sola fonte", S1),
    ("Le tre forme", S2),
    ("La guida a schede", S3),
    ("Le lingue", S4),
])
