from build import arrow, box, c, code, diamond, fig, key, note, p, path, table, term, text, ul


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">capitolo {n}{"." + str(s) if s else ""}</a>'


SOURCES = fig(
    box(20, 120, 190, 64, "src/guida.c", "voci «etichetta¦testo»", "navy")
    + box(290, 30, 190, 54, "guida a schede", "guida_a_schede", "blue")
    + box(290, 110, 190, 54, "pagina con pager", "pagina(), a colori", "blue")
    + box(290, 190, 190, 54, "testo semplice", "pagina(), 80 colonne", "blue")
    + box(570, 20, 150, 54, "po/it.po", "traduzione italiana", "soft")
    + box(570, 110, 150, 54, "build.py", "help_reference", "dark")
    + box(760, 110, 120, 54, "Manuale", "utente", "light")
    + box(570, 200, 310, 54, "tools/check-docs.py", "manuale generato = guida", "green")
    + arrow(212, 140, 288, 60) + arrow(212, 152, 288, 137) + arrow(212, 164, 288, 214)
    + path([(200, 118), (200, 10), (560, 10), (560, 40), (568, 40)], "#0050C0", False, "make pot, traduzione", 380, 22)
    + arrow(645, 76, 645, 108)
    + arrow(722, 137, 758, 137)
    + arrow(645, 166, 645, 198, "#16a34a", True),
    900, 272, "«FIG» — Una sola fonte per guida, pagina, testo e riferimento del manuale", "Da dove vengono i testi")

S1 = p("La guida integrata di " + c("ams --help") + " è sul modello di quella di MTERM: niente pagine di manuale "
       "del sistema, ma una guida a schede nel terminale. I suoi testi stanno in " + c("src/guida.c") + ", in "
       "inglese, come voci " + c("\"etichetta¦descrizione\"") + " con un contesto per gruppo; le traduzioni stanno "
       "nei cataloghi " + c("po/") + ", come tutti gli altri testi (" + cap(16) + ").", lead=True) + SOURCES + \
    table(["Contesto", "Contenuto", "Nel manuale utente"], [
        [c("guida-comandi"), "i comandi: " + c("send") + ", " + c("list") + ", " + c("status") + ", " + c("revoke")
         + ", " + c("remind") + ", " + c("log") + ", " + c("purge") + ", " + c("version") + ", " + c("help")
         + " e " + c("ams") + " da solo", "riferimento, con " + c("data-help")],
        [c("guida-opzioni"), c("--to") + ", " + c("--title") + ", " + c("--expires") + ", " + c("--file"),
         "riferimento, con " + c("data-help")],
        [c("guida-esempi"), "comandi d'esempio con la loro spiegazione", "—"],
        [c("guida-file"), "configurazione, archivio, registro, manuale", "—"],
        [c("guida-sintassi"), "le righe della sintassi", "—"],
    ], "«TAB» — I gruppi di testi della guida") + \
    p("Il generatore dei manuali legge le voci italiane da " + c("po/it.po") + ", nell'ordine del codice, e ne "
      "ricava il riferimento del manuale utente, con l'attributo " + c("data-help") + " su ogni voce; "
      + c("tools/check-docs.py") + " controlla che comandi e opzioni coincidano, parola per parola (" + cap(21, 5)
      + ").")

LEVELS = fig(
    diamond(170, 90, 240, 80, "stdin e stdout tty?", "navy")
    + diamond(470, 90, 230, 80, "almeno 44 × 10?", "navy")
    + box(640, 62, 240, 56, "guida a schede", "guida_a_schede", "blue")
    + box(50, 190, 240, 56, "testo semplice, 80 colonne", "senza colori", "dark", 12)
    + box(355, 190, 240, 56, "pagina in stile manuale", "$PAGER o less -R -F -X", "light", 12)
    + arrow(292, 90, 353, 90, "#0050C0", False, "sì", 322, 80)
    + arrow(587, 90, 638, 90, "#0050C0", False, "sì", 612, 80)
    + arrow(170, 132, 170, 188, "#475569", False, "no", 186, 164)
    + arrow(470, 132, 470, 188, "#475569", False, "no", 486, 164)
    + text(760, 150, "rimpicciolita sotto 44 × 10:", 11, "#475569")
    + text(760, 166, "la guida esce", 11, "#475569"),
    900, 266, "«FIG» — Quale forma prende ams --help", "Tre forme")

S2 = p(c("ams_guida") + " sceglie la forma secondo dove finisce l'uscita. Tutte e tre hanno lo stesso contenuto.",
       lead=True) + LEVELS + table(["Forma", "Quando", "Come"], [
    ["guida a schede", "stdin e stdout in un terminale di almeno 44 × 10", "cinque schede: Info, Comandi, Opzioni, "
     "Esempi, File"],
    ["pagina in stile manuale", "terminale più piccolo", "la pagina (NOME, SINTASSI, DESCRIZIONE, COMANDI, OPZIONI "
     "DI SEND, ESEMPI, FILE, AMBIENTE, STATO DI USCITA, VEDERE ANCHE) larga quanto il terminale, fra 60 e 100 "
     "colonne, attraverso " + c("$PAGER") + " o " + c("less -R -F -X") + " se è nel " + c("PATH") + "; altrimenti "
     "direttamente"],
    ["testo semplice", "stdin o stdout non sono un terminale (una pipe, un file)", "la stessa pagina, 80 colonne, "
     "senza colori"],
], "«TAB» — Le tre forme della guida") + ul([
    "I colori si spengono con " + c("NO_COLOR") + "; " + c("PAGER") + " e " + c("NO_COLOR") + " arrivano ad "
    + c("ams") + " solo se sudo li conserva (" + c("env_keep") + " in sudoers): la guida lo dice nella sezione "
    "AMBIENTE.",
    "Anche la guida richiede root: " + c("ams --help") + " si rilancia con sudo come ogni altro comando ("
    + cap(4, 1) + "). È una decisione dell'utente, a costo di chiedere la password anche per l'aiuto.",
    c("ams") + " da solo in una pipe mostra la guida in testo semplice (" + c("tests/tui.py") + ").",
]) + term("admin@server:~$ sudo ams --help | head -5\n"
          "AMS(1)                           Manuale di ams                           AMS(1)\n"
          "\n"
          "NOME\n"
          "       ams — invia messaggi agli utenti della macchina e ne segue la conferma di\n"
          "       lettura",
          "La guida in una pipe (inizio)")

S3 = table(["Parte", "Come funziona"], [
    ["terminale", c("/dev/tty") + " senza eco né modo canonico (" + c("termios") + "), schermo alternativo e cursore "
     "nascosto; all'uscita e su " + c("SIGINT") + ", " + c("SIGTERM") + ", " + c("SIGHUP") + " tutto torna com'era"],
    ["tasti", "un byte alla volta con " + c("poll") + " di 0,3 s; dopo " + c("ESC") + " il resto con un'attesa di "
     "50 ms: " + key("Esc") + " da solo esce; frecce, " + key("PgUp") + ", " + key("PgDn") + ", " + key("Home")
     + ", " + key("End") + " vengono riconosciuti"],
    ["schede", key("←") + " " + key("→") + ", " + key("Tab") + ", " + key("Maiusc", "Tab") + ", " + key("h") + " "
     + key("l") + ", " + key("Invio") + ", o le cifre " + key("1") + "…" + key("5")],
    ["scorrimento", key("↑") + " " + key("↓") + " (" + key("k") + " " + key("j") + "), " + key("PgUp") + " "
     + key("PgDn") + " (" + key("b") + " " + key("spazio") + "), " + key("g") + " " + key("G") + "; ogni scheda "
     "ricorda la sua posizione; in basso «righe 1-20/57»"],
    ["ridimensionamento", "a ogni attesa di 0,3 s la guida confronta la dimensione (" + c("TIOCGWINSZ")
     + ") con l'ultima e ridisegna; sotto 44 × 10 esce"],
    ["disegno", "le righe della scheda si preparano senza colori, così le lunghezze sono quelle visibili; cornice, "
     "schede e riga di stato si scrivono in una sola scrittura; la riga di stato si accorcia se non ci sta"],
    ["uscita", key("q") + " o " + key("Esc") + ": schermo principale ripristinato, codice 0"],
], "«TAB» — La guida a schede") + \
    p(c("tests/help-tui.py") + " apre la guida su uno pseudo-terminale di 100 × 30, preme i tasti come una persona e "
      "controlla ogni schermo: apertura e cornice, cambio di scheda con freccia e cifra, fine e inizio scheda, "
      "ridimensionamento a 70 × 20, uscita pulita, e la pagina con il pager in un terminale di 40 × 8 ("
      + cap(21, 4) + ").")

CHAPTER = ("La guida integrata", [
    ("Una sola fonte", S1),
    ("Le tre forme", S2),
    ("La guida a schede", S3),
])
