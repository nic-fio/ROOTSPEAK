from build import arrow, box, c, diamond, fig, p, path, table, text, ul

SOURCES = fig(
    box(20, 120, 190, 64, "src/guida.c", "voci «etichetta¦testo»", "navy")
    + box(290, 30, 190, 54, "guida a schede", "guida_a_schede", "blue")
    + box(290, 110, 190, 54, "pagina con pager", "pagina a colori", "blue")
    + box(290, 190, 190, 54, "testo semplice", "pagina, 80 colonne", "blue")
    + box(570, 20, 150, 54, "po/it.po", "traduzione italiana", "soft")
    + box(570, 110, 150, 54, "build.py", "help_reference", "dark")
    + box(760, 110, 120, 54, "Manuale", "capitolo 11", "light")
    + box(570, 200, 310, 54, "tools/check-docs.py", "manuale generato = guida", "green")
    + arrow(212, 140, 288, 60) + arrow(212, 152, 288, 137) + arrow(212, 164, 288, 214)
    + path([(200, 118), (200, 10), (560, 10), (560, 40), (568, 40)], "#0050C0")
    + arrow(645, 76, 645, 108)
    + arrow(722, 137, 758, 137)
    + arrow(645, 166, 645, 198, "#16a34a", True),
    900, 272, "«FIG» — Una sola fonte per guida, pagina, testo e riferimento del manuale", "Da dove vengono i testi")

S1 = p("I testi della guida stanno in " + c("src/guida.c") + ", in inglese, come voci " + c("\"etichetta¦descrizione\"")
       + " con un contesto per gruppo (" + c("guida-comandi") + ", " + c("guida-opzioni") + ", " + c("guida-esempi")
       + ", " + c("guida-file") + ", " + c("guida-sintassi") + "); le traduzioni stanno nei cataloghi " + c("po/")
       + ", come tutti gli altri testi.", lead=True) + SOURCES + \
    p("Il generatore dei manuali legge le voci italiane da " + c("po/it.po") + ", nell'ordine del codice, e ne ricava "
      "il riferimento del manuale utente, con l'attributo " + c("data-help") + " su ogni voce; "
      + c("tools/check-docs.py") + " controlla che coincidano.")

LEVELS = fig(
    diamond(170, 90, 240, 80, "stdin e stdout terminali?", "navy")
    + diamond(470, 90, 230, 80, "almeno 44 × 10?", "navy")
    + box(640, 62, 240, 56, "guida a schede", "guida_a_schede", "blue")
    + box(50, 190, 240, 56, "testo semplice, 80 colonne", "senza colori", "dark")
    + box(355, 190, 240, 56, "pagina in stile manuale", "$PAGER o less -R -F -X", "light")
    + arrow(292, 90, 353, 90, "#0050C0", False, "sì", 322, 80)
    + arrow(587, 90, 638, 90, "#0050C0", False, "sì", 612, 80)
    + arrow(170, 132, 170, 188, "#475569", False, "no", 186, 164)
    + arrow(470, 132, 470, 188, "#475569", False, "no", 486, 164),
    900, 266, "«FIG» — Quale forma prende ams --help", "")

S2 = LEVELS + p(c("ams_guida") + " sceglie la forma. Colori disattivati con " + c("NO_COLOR") + "; " + c("PAGER")
                + " e " + c("NO_COLOR") + " arrivano solo se sudo li conserva. Il pager si avvia con " + c("popen")
                + " solo se " + c("less") + " è nel " + c("PATH") + " o " + c("PAGER") + " è impostata.")

S3 = table(["Parte", "Come funziona"], [
    ["terminale", c("/dev/tty") + " senza eco né modo canonico (" + c("termios") + "), schermo alternativo e cursore "
     "nascosto; all'uscita e su " + c("INT") + ", " + c("TERM") + ", " + c("HUP") + " tutto torna com'era"],
    ["tasti", c("tasto") + " legge un byte con " + c("poll") + " di 0,3 s; dopo " + c("ESC") + " legge il resto con "
     "un'attesa breve: " + c("ESC") + " da solo esce, frecce, " + c("PgUp") + " e " + c("PgDn") + " vengono riconosciuti"],
    ["ridimensionamento", "a ogni scadenza di 0,3 s la guida confronta la dimensione (" + c("TIOCGWINSZ")
     + ") con l'ultima e ridisegna; sotto 44 × 10 esce"],
    ["disegno", c("righe_scheda") + " prepara le righe senza colori, così le lunghezze sono quelle visibili; "
     + c("disegna") + " compone cornice, schede e stato e scrive tutto in una sola scrittura; la riga di stato "
     "si accorcia se non ci sta"],
    ["codifica", "le lunghezze sono in caratteri UTF-8, qualunque sia la localizzazione del sistema"],
], "«TAB» — La guida a schede")

LINGUE = fig(
    box(20, 30, 200, 54, "amministratore", "ambiente dopo sudo", "dark")
    + box(20, 110, 200, 54, "terminale dell'utente", "/proc/PID/environ", "dark")
    + box(20, 190, 200, 54, "shell, agente", "il loro ambiente", "dark")
    + box(330, 110, 220, 54, "lingua_scegli", "regole di gettext", "navy")
    + box(660, 30, 220, 54, "LINGUA/LC_MESSAGES/ams.mo", "letto da lingua.c", "blue")
    + box(660, 110, 220, 54, "po/LINGUA.po", "sorgente delle traduzioni", "blue")
    + box(660, 190, 220, 54, "inglese", "i testi del codice", "light")
    + arrow(222, 57, 328, 128) + arrow(222, 137, 328, 137) + arrow(222, 217, 328, 146)
    + arrow(552, 130, 658, 60) + arrow(770, 108, 770, 86, "#475569", True, "msgfmt", 810, 100)
    + arrow(552, 144, 658, 214, "#475569"),
    900, 262, "«FIG» — Da dove viene la lingua, e dove sono i testi", "Ognuno nella sua lingua")

S4 = p("Ogni persona legge AMS nella sua lingua; il testo dei messaggi non si traduce.", lead=True) + LINGUE + \
    table(["Chi legge", "Lingua", "Da dove"], [
        ["l'amministratore: uscite, errori, guida", "la sua", "il suo ambiente: sudo conserva " + c("LANG") + ", " + c("LANGUAGE") + " e " + c("LC_*")],
        ["l'utente, all'invio: l'intestazione nel terminale", "quella del terminale",
         "l'ambiente del primo processo del terminale, di solito la shell; se root non può leggerlo (un container "
         "senza " + c("CAP_SYS_PTRACE") + "), lo legge l'utente stesso, in un figlio con la sua identità"],
        ["l'utente, al prompt: domanda e risposte", "quella della shell", "l'ambiente di " + c("ams-user prompt")],
        ["l'utente, sul desktop: finestra e notifiche", "quella della sessione grafica", "l'ambiente dell'agente"],
        ["il journal", "quella del sistema", c("/etc/default/locale") + " o " + c("/etc/locale.conf")],
    ], "«TAB» — Chi legge in quale lingua") + ul([
    "<b>Formato e strumenti di gettext</b>: nel codice i testi sono in inglese dentro " + c("T(\"…\")") + " (o "
    + c("TC(contesto, \"…\")") + ", " + c("tl(lingua, \"…\")") + " per una lingua data); " + c("make pot")
    + " li estrae in " + c("po/ams.pot") + " con " + c("xgettext") + " e aggiorna i " + c(".po") + " con "
    + c("msgmerge") + "; " + c("make") + " li compila in " + c(".mo") + " con " + c("msgfmt --check") + ", che "
    "controlla anche che ogni traduzione abbia gli stessi " + c("%s") + ".",
    "<b>Il lettore dei " + c(".mo") + " è di AMS</b> (" + c("src/lingua.c") + "), non la libintl: con la libintl una "
    "lingua non installata nel sistema resta non tradotta anche forzando " + c("LANGUAGE") + " (provato: con "
    + c("C.UTF-8") + " la libreria ignora " + c("LANGUAGE") + "), e root deve scrivere a ogni terminale nella lingua "
    "del suo utente. Il lettore controlla ogni posizione del file prima di usarla e cerca con la ricerca binaria.",
    c("lingua_scegli") + " segue gettext: conta il primo impostato fra " + c("LC_ALL") + ", " + c("LC_MESSAGES")
    + " e " + c("LANG") + "; con " + c("C") + " o " + c("POSIX") + " vale l'inglese, altrimenti si prova prima "
    "l'elenco di " + c("LANGUAGE") + ". Vince la prima lingua che ha un catalogo; se nessuna, l'inglese. Un valore "
    "che non è un codice di 2 o 3 lettere minuscole (" + c("../") + ", " + c("/") + ") non porta mai a leggere un file.",
    "Ciò che si salva resta senza lingua: il canale di una conferma è " + c("terminale pts/N") + " o " + c("desktop")
    + " e si traduce solo quando si mostra (" + c("canale_testo") + "); gli eventi si riscrivono dai campi.",
    "La domanda accetta " + c("s") + ", " + c("S") + ", " + c("y") + " e " + c("Y") + " in ogni lingua.",
    c("tools/check-docs.py") + " controlla che ogni catalogo passi " + c("msgfmt --check") + ", non abbia traduzioni "
    "da rivedere e contenga tutti i testi del codice. Per una lingua nuova basta " + c("po/XX.po") + " (per esempio "
    "con " + c("msginit") + ").",
])

CHAPTER = ("La guida integrata e le lingue", [
    ("Una sola fonte", S1),
    ("Le tre forme", S2),
    ("La guida a schede", S3),
    ("Le lingue", S4),
])
