import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import c, dialog, flow, key, note, p, steps, table, term, tip, ui  # noqa: E402
from _aiuti import CONFERMATO, CONSEGNATO, rif  # noqa: E402

S1 = p("Questo percorso porta da un AMS appena installato alla prima conferma, in quattro tappe. Il destinatario del "
       "primo messaggio può essere l'amministratore stesso: così si vede con i propri occhi cosa ricevono gli "
       "utenti. Ogni tappa rimanda al capitolo che la spiega nel dettaglio.", lead=True) + \
    flow([("1. Installa", "make, ./install.sh", "dark"), ("2. Scrivi e invia", "ams, tasto n", "blue"),
          ("3. L'utente conferma", "finestra o terminale", "blue"), ("4. Controlla", "Invio sul messaggio", "green")],
         "«FIG» — Le quattro tappe dei primi passi", "Dal nulla alla prima conferma") + \
    table(["Tappa", "Cosa si fa", "Capitolo"], [
        ["1", "Installare AMS e controllare che risponda", rif(2)],
        ["2", "Scrivere il messaggio nella TUI (o con " + c("ams send") + ") e inviarlo", rif(5)],
        ["3", "Il destinatario vede la finestra o la domanda e conferma", rif(8)],
        ["4", "Aprire il messaggio e vedere chi ha confermato", rif(6)],
    ], "«TAB» — Il percorso")

S2 = p("Il modo più semplice è la TUI. Qui il messaggio va a Mario; per una prova su di sé basta scrivere il proprio "
       "nome.", lead=True) + steps([
        "Aprire un terminale e scrivere " + c("ams") + ". Alla richiesta, inserire la propria password: " + c("ams")
        + " la chiede sempre, perché lavora come amministratore." + term(
            "admin@server:~$ ams\n[sudo] password di admin:"),
        "Nella lista dei messaggi premere " + key("n") + ": si apre la schermata " + ui("Nuovo messaggio") + ".",
        "Nel campo " + ui("A") + " scrivere " + c("mario") + " e premere " + key("Tab") + ": a destra compare "
        + ui("1 destinatario") + ".",
        "Nel campo " + ui("Titolo") + " scrivere " + c("Manutenzione") + "; lasciare vuota la " + ui("Scadenza")
        + " e passare al " + ui("Testo") + " con " + key("Tab") + ".",
        "Scrivere il testo: " + c("Sabato dalle 8 alle 12 il server sarà spento.") + " Si va a capo con "
        + key("Invio") + ".",
        "Premere " + key("Ctrl", "S") + ". Compare il riassunto " + ui("Inviare il messaggio?") + ": premere "
        + key("s") + " per confermare.",
        "La finestra " + ui("Messaggio inviato") + " riporta la risposta di AMS, per esempio «Messaggio 1 inviato a 1 "
        "utente.». Un tasto qualsiasi riporta alla lista, dove il messaggio è in cima.",
    ]) + p("Lo stesso messaggio, con un comando solo:") + term(
        'admin@server:~$ ams send --to mario --title Manutenzione "Sabato dalle 8 alle 12 il server sarà spento."\n'
        "Messaggio 1 inviato a 1 utente.") + \
    tip("il numero del messaggio (qui " + c("1") + ") serve per i comandi " + c("status") + ", " + c("log") + ", "
        + c("revoke") + " e " + c("remind") + ". Nella TUI non serve: si sceglie il messaggio dalla lista.",
        "Il numero.")

S3 = p("Se Mario è collegato, il messaggio gli arriva subito, in tutte le sue sessioni. Sul desktop compare questa "
       "finestra, sopra le altre:", lead=True) + \
    dialog("AMS · Messaggio dall'amministratore", "Manutenzione · 30/09 16:55",
           "Sabato dalle 8 alle 12 il server sarà spento.",
           "«FIG» — La finestra di conferma sul desktop di Mario") + \
    p("Nelle finestre di terminale il testo compare subito; al prompt successivo AMS chiede la conferma:") + term(
        "── AMS · Messaggio dall'amministratore · Manutenzione · 30/09 16:55 ──\n"
        "Sabato dalle 8 alle 12 il server sarà spento.\n"
        "────────────────────────────────────────\n"
        "[AMS] Confermi di aver letto il messaggio? [s/N] s\n"
        "[AMS] Confermato.\n"
        "mario@server:~$", "Nel terminale di Mario") + \
    note("basta confermare una volta, in un posto qualsiasi: la finestra si chiude da sola se Mario risponde nel "
         "terminale, e viceversa. Se Mario non è collegato, troverà il messaggio al prossimo accesso. Il " + rif(8)
         + " descrive tutto quello che vedono gli utenti.", "Una conferma basta.")

S4 = p("Nella lista il messaggio mostra i destinatari nei tre stati: prima dell'accesso di Mario "
       "«1 consegnato», dopo la sua conferma «tutti confermato (1)». Con " + key("Invio") + " si apre il messaggio "
       "e si vede lo stato di ogni destinatario, con data, ora e canale della conferma.", lead=True) + term(
    "admin@server:~$ ams status 1\n"
    "Messaggio 1 · Manutenzione · 30/09 16:55 · da admin\n"
    "  │ Sabato dalle 8 alle 12 il server sarà spento.\n"
    "\n"
    "UTENTE           STATO\n"
    "mario            confermato il 30/09 16:56 (desktop)", "Lo stesso, con un comando") + \
    table(["Se lo stato è…", "Vuol dire", "Cosa fare"], [
        [CONSEGNATO, "Mario ha la copia ma non ha ancora confermato", "aspettare, oppure sollecitarlo (" + rif(7, 2) + ")"],
        [CONFERMATO + " (desktop)", "ha premuto " + ui("Ho letto") + " nella finestra", "nulla: è fatto"],
        [CONFERMATO + " (terminale pts/1)", "ha risposto " + c("s") + " in una finestra di terminale", "nulla: è fatto"],
    ], "«TAB» — Leggere il risultato") + \
    tip("la TUI si aggiorna da sola ogni 3 secondi: tenendola aperta sul messaggio si vedono arrivare le conferme "
        "una dopo l'altra.", "E poi?")

CHAPTER = ("Primi passi", [
    ("Il percorso", S1),
    ("Mandare il primo messaggio", S2),
    ("Cosa vede l'utente", S3),
    ("Vedere chi ha letto", S4),
])
