import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import c, esc, help_items, help_reference, note, p, table, term  # noqa: E402
from _aiuti import rif  # noqa: E402

SINTASSI = ("admin@server:~$ ams --help | head -16\n"
            "AMS(1)                           Manuale di ams                           AMS(1)\n"
            "\n"
            "NOME\n"
            "       ams — invia messaggi agli utenti della macchina e ne segue la conferma di\n"
            "       lettura\n"
            "\n"
            "SINTASSI\n"
            "       ams send --to DEST [opzioni] [TESTO]\n"
            "       ams list\n"
            "       ams status ID\n"
            "       ams\n"
            "       ams revoke ID\n"
            "       ams remind ID\n"
            "       ams log ID\n"
            "       ams purge DURATA\n"
            "       ams version")

S1 = p("Questo capitolo riporta tutti i comandi e le opzioni di " + c("ams") + ". I testi dei comandi, delle opzioni "
       "e degli esempi sono gli stessi della guida integrata (" + c("ams --help") + ", " + rif(9) + "), da cui "
       "questa pagina è generata: le due cose non possono divergere.", lead=True) + \
    term(SINTASSI, "La sintassi, dalla guida in forma di testo") + \
    table(["Parte", "Significato"], [
        [c("ID"), "il numero di un messaggio, come compare nella lista"],
        [c("DEST"), "i destinatari: nomi, " + c("@gruppo") + ", " + c("all") + ", " + c("online") + ", separati da "
         "virgole senza spazi"],
        [c("DURATA"), "un numero seguito da " + c("m") + " (minuti), " + c("h") + " (ore) o " + c("d") + " (giorni); "
         "per " + c("--expires") + " anche una data e un'ora"],
        [c("[opzioni]") + ", " + c("[TESTO]"), "le parti tra parentesi quadre si possono omettere"],
    ], "«TAB» — Come si legge la sintassi") + \
    note("ogni comando, compresi " + c("version") + " e " + c("--help") + ", si rilancia con sudo se non è già root.",
         "Sempre come root.")

S2 = p("I comandi di " + c("ams") + ", con il testo della guida integrata.", lead=True) + \
    help_reference("AMS_HELP_COMMANDS", "command")

S3 = p("Le opzioni di " + c("ams send") + ". Vanno scritte prima del testo del messaggio; nella TUI corrispondono ai "
       "campi del nuovo messaggio (" + rif(5, 4) + ").", lead=True) + \
    help_reference("AMS_HELP_OPTIONS", "option") + \
    table(["Opzione", "Campo della TUI"], [
        [c("--to"), "A"],
        [c("--title"), "Titolo"],
        [c("--expires"), "Scadenza"],
        [c("--file"), "Testo (o " + "Ctrl+E" + " per aprirlo nell'editor)"],
    ], "«TAB» — Opzioni e campi della TUI")

S4 = table(["Comando", "Cosa fa"], [[c(cmd), esc(desc)] for cmd, desc in help_items("AMS_HELP_EXAMPLES")],
           "«TAB» — Gli esempi della guida integrata")

S5 = table(["Esito", "Significato"], [
    [c("0"), "Completato con successo."],
    [c("1"), "Errore: il messaggio d'errore, che inizia con «ams:», dice quale (" + rif(12, 1) + ")."],
], "«TAB» — L'esito dei comandi") + \
    p("L'esito permette di usare " + c("ams") + " negli script:") + \
    term('admin@server:~$ ams send --to online --expires 15m "Riavvio alle 13:00." || echo "invio non riuscito"\n'
         "Messaggio 7 inviato a 3 utenti.", "In uno script") + \
    table(["Variabile", "Effetto"], [
        [c("PAGER"), "il programma che impagina la guida nei terminali piccoli (predefinito: less)"],
        [c("NO_COLOR"), "se impostata, disabilita i colori"],
        [c("VISUAL") + ", " + c("EDITOR"), "l'editor aperto con Ctrl+E nel nuovo messaggio"],
    ], "«TAB» — Le variabili d'ambiente (arrivano ad ams solo se sudo le conserva, " + rif(10, 3) + ")")

CHAPTER = ("Riferimento dei comandi", [
    ("Sintassi", S1),
    ("Comandi", S2),
    ("Opzioni di send", S3),
    ("Esempi", S4),
    ("Esito dei comandi e ambiente", S5),
])
