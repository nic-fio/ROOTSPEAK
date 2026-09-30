import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import arrow, box, c, diamond, fig, key, note, p, table, term, text, tip  # noqa: E402
from _aiuti import rif, schermata_u  # noqa: E402

S1 = p("Tutto quello che serve per usare " + c("ams") + " è anche dentro il comando stesso: " + c("ams --help")
       + " (oppure " + c("ams help") + " o " + c("ams -h") + ") apre una guida a tutto schermo, divisa in cinque "
       "schede, nella lingua dell'amministratore.", lead=True) + \
    schermata_u("guida-info", "«FIG» — La guida integrata, scheda Info (schermata vera, terminale di 78 colonne)") + \
    table(["Scheda", "Contiene"], [
        ["Info", "nome, sintassi di tutti i comandi, descrizione di AMS, versione e percorso di questo manuale"],
        ["Comandi", c("ams") + " da solo, " + c("send") + ", " + c("list") + ", " + c("status") + ", " + c("revoke")
         + ", " + c("remind") + ", " + c("log") + ", " + c("purge") + ", " + c("version") + ", " + c("help")],
        ["Opzioni", "le opzioni di " + c("send") + ": destinatari, titolo, scadenza, file"],
        ["Esempi", "comandi pronti da copiare"],
        ["File", "dove stanno impostazioni, messaggi, registro e manuale"],
    ], "«TAB» — Le schede della guida") + \
    schermata_u("guida-opzioni", "«FIG» — La scheda Opzioni") + \
    note("come ogni comando di " + c("ams") + ", anche la guida chiede la password di sudo. I testi delle schede "
         "Comandi e Opzioni sono gli stessi del " + rif(13) + " di questo manuale.", "Sempre con sudo.")

S2 = table(["Tasti", "Azione"], [
    [key("←") + " " + key("→") + ", " + key("Tab") + " " + key("Maiusc", "Tab") + ", " + key("h") + " " + key("l"),
     "scheda precedente o successiva"],
    [key("Invio"), "scheda successiva"],
    [key("1") + " … " + key("5"), "vai direttamente a una scheda"],
    [key("↑") + " " + key("↓") + ", " + key("k") + " " + key("j"), "scorri di una riga"],
    [key("PgUp") + " " + key("PgDn") + ", " + key("b") + " " + key("spazio"), "scorri di una pagina"],
    [key("g") + " " + key("G") + ", " + key("Home") + " " + key("Fine"), "inizio o fine della scheda"],
    [key("q") + ", " + key("Esc"), "esci dalla guida"],
], "«TAB» — I tasti della guida") + \
    p("In basso a destra la guida dice quali righe della scheda si stanno guardando, per esempio «righe 1-16/18». "
      "Ogni scheda ricorda il punto a cui si era arrivati. La guida si adatta quando si ridimensiona la finestra; "
      "all'uscita il terminale torna esattamente com'era.") + \
    tip("i tasti " + key("h") + " " + key("j") + " " + key("k") + " " + key("l") + " sono gli stessi di vi e di "
        "less: chi li conosce li può usare anche qui.", "Per chi usa vi.")

FORME = fig(
    diamond(180, 130, 250, 96, "L'uscita è un terminale?", "navy")
    + diamond(520, 130, 250, 96, "Almeno 44 × 10?", "navy")
    + box(700, 44, 180, 60, "Guida a schede", "come nelle figure qui sopra", "green")
    + box(700, 156, 180, 60, "Pagina unica", "con less (o PAGER)", "blue")
    + box(90, 236, 180, 60, "Testo semplice", "80 colonne, senza colori", "dark")
    + arrow(305, 130, 393, 130, "#0050C0", False, "sì", 349, 120)
    + arrow(180, 178, 180, 234, "#475569", False, "no, una pipe", 232, 212)
    + arrow(630, 110, 698, 76, "#16a34a", False, "sì", 664, 84)
    + arrow(630, 150, 698, 184, "#475569", False, "no", 664, 180),
    900, 316, "«FIG» — La guida sceglie da sola la forma adatta a dove viene mostrata", "Tre forme della stessa guida")

S3 = p("La stessa guida ha tre forme, e " + c("ams") + " sceglie quella giusta da solo.", lead=True) + FORME + \
    table(["Situazione", "Cosa mostra " + c("ams --help")], [
        ["un terminale normale", "la guida a schede"],
        ["un terminale molto piccolo (meno di 44 colonne o di 10 righe)", "la stessa guida come pagina unica, da "
         "scorrere con il pager: " + c("less") + ", o il programma indicato in " + c("PAGER") + "; " + key("q")
         + " per uscire"],
        ["l'uscita va in un file o in un altro comando", "testo semplice a 80 colonne, senza colori; in più delle "
         "schede ha le variabili d'ambiente e l'esito dei comandi (" + rif(13, 5) + ")"],
    ], "«TAB» — La guida nelle diverse situazioni") + \
    term("admin@server:~$ ams --help | grep -A2 -- '--expires DURATA'\n"
         "       --expires DURATA\n"
         "              Scadenza, dopo la quale il messaggio non viene più mostrato: 30m,\n"
         "              2h, 3d oppure data e ora (\"2026-10-04 12:00\"; le date a parole",
         "Cercare nella guida con grep") + \
    note("anche " + c("ams") + " da solo, in una pipe o in un terminale più piccolo di 80 colonne o di 20 righe, "
         "mostra la guida invece della TUI.", "E ams da solo?")

CHAPTER = ("La guida integrata", [
    ("Aprire la guida", S1),
    ("Muoversi nella guida", S2),
    ("Terminali piccoli e testo semplice", S3),
])
