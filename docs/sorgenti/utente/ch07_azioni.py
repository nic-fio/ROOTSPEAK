import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import c, key, note, p, schermata, seq, steps, table, term, tip, ui, ul, warn  # noqa: E402
from _aiuti import CONFERMATO, CONSEGNATO, INVIATO, RITIRATO, SCADUTO, rif, schermata_u  # noqa: E402

RITIRO = seq([("Amministratore", "tasto r o ams revoke", "dark"), ("AMS", "archivio", "navy"),
              ("Anna", "finestra aperta", "blue"), ("Luca", "non ancora collegato", "light")], [
    (0, 1, "ritira il messaggio 4"),
    (1, 1, "segna il messaggio come ritirato"),
    (1, 3, "toglie la copia dalla casella di Luca"),
    (1, 2, "toglie la copia; la finestra si chiude da sola", True),
    (1, 0, "«Messaggio 4 ritirato.»", True),
    ("sep", "più tardi"),
    (3, 1, "Luca accede: non vede nulla"),
], "«FIG» — Che cosa succede quando si ritira un messaggio", "Il ritiro")

S1 = p("Un messaggio mandato per errore, o non più valido, si <b>ritira</b>: nella TUI con " + key("r") + " sul "
       "messaggio scelto (nella lista o nel messaggio aperto), con un comando con " + c("ams revoke") + ". Prima "
       "di ritirare, la TUI chiede sempre conferma.", lead=True) + \
    schermata_u("ritira", "«FIG» — La conferma del ritiro: titolo e destinatari nei tre stati") + \
    term("admin@server:~$ ams revoke 4\nMessaggio 4 ritirato.", "Con un comando") + RITIRO + \
    table(["Chi", "Cosa succede"], [
        ["chi non l'ha ancora visto (non collegato)", "non lo vedrà più: la copia sparisce dalla sua casella"],
        ["chi ha una finestra di conferma aperta", "la finestra si chiude da sola entro un secondo"],
        ["chi ha la domanda nel terminale", "la domanda si interrompe con «[AMS] L'amministratore ha ritirato il "
         "messaggio.»"],
        ["chi aveva già confermato", "resta " + CONFERMATO + ": le conferme già arrivate valgono"],
        ["chi conferma dopo il ritiro", "la conferma non vale: resta " + CONSEGNATO + ", «non confermato (ritirato)»"],
        ["l'amministratore", "nella lista il messaggio ha " + c("[ritirato]") + " davanti; " + c("ams status")
         + " scrive «RITIRATO il …»"],
    ], "«TAB» — Gli effetti del ritiro") + \
    warn("il testo già comparso nei terminali al momento dell'invio non si può cancellare: è già sullo schermo "
         "dell'utente. Il ritiro ferma soltanto le richieste di conferma e le finestre.", "Il testo già scritto resta.") + \
    note("se il messaggio si sta ancora inviando a molti destinatari, il ritiro aspetta un istante e ferma la "
         "consegna al destinatario successivo; chi ha già la copia la perde. Se qualche casella non si può "
         "raggiungere, AMS lo dice («alcune copie non si sono potute togliere dalle caselle») e riprova da solo.",
         "Ritiro durante l'invio.")

S2 = p("Chi ha rimandato rivede il messaggio dopo 30 minuti. Se serve prima, si <b>sollecita</b>: nella TUI con "
       + key("s") + ", con un comando con " + c("ams remind") + ". La domanda torna al prompt successivo e la "
       "finestra ricompare subito sul desktop, anche se l'utente l'aveva appena rimandata.", lead=True) + \
    schermata("sollecito", "«FIG» — La conferma del sollecito, con quante persone riguarda") + \
    term("admin@server:~$ ams remind 2\nMessaggio 2: sollecitati 3 destinatari.", "Con un comando") + \
    table(["Destinatario", "Sollecitato?"], [
        [CONSEGNATO + " (ha la copia, non ha confermato)", "sì: domanda al prossimo prompt, finestra subito"],
        [CONFERMATO, "no: non viene disturbato"],
        [INVIATO, "no: non ha ancora la copia; AMS riprova a consegnarla da solo"],
    ], "«TAB» — Chi riceve il sollecito") + ul([
        "Un messaggio " + RITIRATO + " o " + SCADUTO + " non si sollecita: il comando risponde «il messaggio 4 è "
        "stato ritirato: nessuno da sollecitare» o «… è scaduto: nessuno da sollecitare».",
        "Il sollecito finisce nella storia del messaggio e nel registro, con chi l'ha chiesto.",
        "Per chi non è collegato il sollecito non cambia nulla: vedrà comunque il messaggio al prossimo accesso.",
    ]) + tip("un sollecito ogni tanto funziona meglio di molti: chi ha la finestra davanti ogni cinque minuti tende a "
             "confermare senza leggere.", "Con misura.")

S3 = p("Messaggi e conferme restano nell'archivio finché non si cancellano. La <b>pulizia</b> toglie i messaggi "
       "inviati da più di un certo tempo, con le copie e le conferme nelle caselle degli utenti.", lead=True) + \
    steps([
        "Nella lista premere " + key("p") + ": si apre " + ui("Cancellare i messaggi vecchi") + ", con "
        + c("90d") + " già scritto.",
        "Cambiare la durata se serve (" + c("90d") + " giorni, " + c("12h") + " ore, " + c("30m") + " minuti) e "
        "premere " + key("Invio") + ".",
        "Leggere il riassunto " + ui("Cancellare i messaggi vecchi?") + " e confermare con " + key("s") + ".",
        "La finestra successiva riporta la risposta di AMS, per esempio «Cancellati 12 messaggi più vecchi di 90d.».",
    ]) + schermata_u("pulizia", "«FIG» — La richiesta della durata") + \
    term("admin@server:~$ ams purge 90d\nCancellati 12 messaggi più vecchi di 90d.", "Con un comando") + ul([
        "Un messaggio cancellato sparisce dalla lista e da " + c("ams status") + "; se qualcuno non l'aveva ancora "
        "confermato, non gli verrà più chiesto.",
        "Un invio ancora in corso non viene toccato.",
        "Nel registro di sistema restano gli eventi del messaggio e quello della cancellazione "
        "(«messaggio 1 cancellato da admin (più vecchio di 90d)»).",
        "I numeri dei messaggi non vengono riusati: il prossimo messaggio prende il numero successivo all'ultimo.",
    ]) + warn("la cancellazione non si annulla. Se serve conservare l'elenco delle conferme, prima si salva l'uscita di "
              + c("ams status") + " dei messaggi che interessano.", "Definitivo.")

S4 = p("Non tutte le azioni hanno senso su ogni messaggio. Quando un tasto non ha effetto, la TUI semplicemente "
       "non fa nulla; i comandi invece rispondono con un errore.", lead=True) + \
    table(["Azione", "Non si può quando…", "Risposta del comando"], [
        [key("r") + " / " + c("ams revoke"), "il messaggio è già ritirato", "nessun errore: «Messaggio 4 ritirato.»"],
        [key("s") + " / " + c("ams remind"), "il messaggio è ritirato", c("ams: il messaggio 4 è stato ritirato: nessuno da sollecitare")],
        [key("s") + " / " + c("ams remind"), "il messaggio è scaduto", c("ams: il messaggio 4 è scaduto: nessuno da sollecitare")],
        [key("s") + " / " + c("ams remind"), "nessuno è " + CONSEGNATO, "nella TUI nulla; il comando risponde "
         "«sollecitati 0 destinatari»"],
        [key("Invio") + " / " + c("ams status"), "il numero non esiste", c("ams: messaggio inesistente: 99")],
        [key("p") + " / " + c("ams purge"), "la durata è scritta male", c("ams: durata non valida: 3 (per esempio 90d, 12h, 30m)")],
    ], "«TAB» — Quando un'azione non si può fare") + \
    note("nessuna azione della TUI parte senza una conferma: messaggio da ritirare, persone da sollecitare, messaggi "
         "da cancellare sono sempre scritti prima. " + key("n") + " o " + key("Esc") + " annullano.",
         "Sempre una conferma.") + \
    p("Tutte queste azioni sono riservate agli amministratori e finiscono nel registro con il loro nome: per " + c("ams")
      + " l'autore è chi ha usato sudo, non root (" + rif(11, 1) + ").")

CHAPTER = ("Ritirare, sollecitare, fare pulizia", [
    ("Ritirare un messaggio", S1),
    ("Sollecitare chi non ha confermato", S2),
    ("Cancellare i messaggi vecchi", S3),
    ("Quando un'azione non si può fare", S4),
])
