import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import VERSION, arrow, box, c, fig, key, note, p, path, table, text, tip, ui, ul, warn  # noqa: E402
from _aiuti import CONFERMATO, CONSEGNATO, INVIATO, RITIRATO, SCADUTO, rif  # noqa: E402

PANORAMA = fig(
    box(20, 128, 170, 64, "Amministratore", "sudo ams · TUI o comandi", "dark")
    + box(240, 128, 170, 64, "AMS", "una casella per utente", "navy")
    + box(462, 38, 220, 64, "Nel terminale", "testo subito, domanda al prompt", "blue")
    + box(462, 128, 220, 64, "Sul desktop", "finestra «Ho letto» / «Più tardi»", "blue")
    + box(462, 218, 220, 64, "Al prossimo accesso", "per chi non è collegato", "light")
    + box(730, 128, 150, 64, "Conferma ✓", "chi, quando, da dove", "green")
    + arrow(192, 160, 238, 160)
    + path([(412, 150), (436, 150), (436, 70), (460, 70)])
    + arrow(412, 160, 460, 160)
    + path([(412, 170), (436, 170), (436, 250), (460, 250)])
    + path([(684, 70), (706, 70), (706, 150), (728, 150)], "#16a34a", True)
    + arrow(684, 160, 728, 160, "#16a34a", True)
    + path([(684, 250), (706, 250), (706, 170), (728, 170)], "#16a34a", True)
    + path([(805, 194), (805, 318), (105, 318), (105, 194)], "#475569", True)
    + text(455, 309, "la lista dei messaggi e ams status: chi ha confermato e chi no", 11.5, "#334155", "600"),
    900, 340, "«FIG» — Un messaggio raggiunge ogni sessione dell'utente; la prima conferma torna all'amministratore",
    "Il percorso di un messaggio")

S1 = p("<b>AMS - Advanced Messaging System for linux</b> permette a chi amministra una macchina Linux di mandare un "
       "messaggio agli utenti e di sapere, per ciascuno, se ha confermato di averlo letto. È pensato per gli avvisi "
       "che contano: una manutenzione, un riavvio, una nuova regola, un account in scadenza.", lead=True) + \
    p("L'amministratore scrive il messaggio nell'interfaccia a tutto schermo di " + c("ams") + " oppure con un comando. "
      "AMS lo fa arrivare dovunque l'utente si trovi: nelle finestre di terminale (anche collegate con ssh), sul "
      "desktop, oppure al prossimo accesso se in quel momento non è collegato. L'utente conferma con un clic o con "
      "una lettera, e l'amministratore vede chi ha confermato, quando e da dove.") + PANORAMA + \
    p("Per chi amministra, AMS offre un solo posto in cui:") + ul([
        "scrivere un messaggio e mandarlo a un utente, a un gruppo, a tutti o solo a chi è collegato;",
        "vedere per ogni destinatario a che punto è: " + INVIATO + ", " + CONSEGNATO + " o " + CONFERMATO + ";",
        "sollecitare chi non ha ancora confermato, ritirare un messaggio sbagliato, dargli una scadenza;",
        "ritrovare la storia di ogni messaggio nel registro di sistema;",
        "cancellare i messaggi vecchi quando non servono più.",
    ]) + note("la conferma è una <b>dichiarazione</b> dell'utente («ho letto»), registrata con data, ora e canale. "
              "AMS non può sapere se il messaggio è stato letto davvero, come nessun altro sistema di messaggi.",
              "Cosa dice una conferma.")

S2 = table(["", c("wall") + " / " + c("write"), c("/etc/motd") + " e banner", "AMS"], [
    ["Scrive nei terminali degli utenti collegati", "sì", "no", "sì"],
    ["Compare sul desktop (X11 e Wayland)", "no", "no", "sì, in una finestra"],
    ["Raggiunge chi non è collegato", "no", "sì, a ogni accesso testuale", "sì, al prossimo accesso"],
    ["Chiede la conferma di lettura", "no", "no", "sì, per ogni messaggio"],
    ["Ripropone il messaggio a chi non ha confermato", "no", "no", "sì, ogni 30 minuti"],
    ["Dice all'amministratore chi ha letto", "no", "no", "sì, con data, ora e canale"],
    ["Parla la lingua di ciascun utente", "no", "no", "sì (italiano, inglese)"],
], "«TAB» — AMS e gli strumenti classici di Linux") + \
    p("AMS invece <b>non</b> fa queste cose, per scelta:") + ul([
        "<b>Non blocca nessuno.</b> Nessuna schermata bloccata, nessun accesso negato, nessuna disconnessione: "
        "l'utente può sempre rimandare e continuare a lavorare. Il messaggio torna più tardi.",
        "<b>Non è una chat.</b> Gli utenti ricevono e confermano; non rispondono, non scrivono ad altri e non hanno "
        "comandi da imparare.",
        "<b>Non va in rete.</b> Raggiunge gli utenti di questa macchina, anche quelli collegati da remoto con ssh, "
        "ma non altre macchine.",
        "<b>Non disturba i programmi automatici.</b> Backup, cron, copie con " + c("scp") + " o " + c("rsync")
        + " non vedono mai la domanda di AMS: compare solo nelle shell interattive.",
    ])

S3 = table(["Chi", "Cosa fa con AMS", "Capitoli"], [
    ["Amministratore della macchina", "Installa AMS, manda i messaggi, segue le conferme, ritira e sollecita, "
     "cambia le impostazioni.", "2 - 7, 9 - 13"],
    ["Chi deve spiegare AMS agli utenti", "Sa cosa vedono gli utenti nel terminale e sul desktop, e cosa rispondere "
     "alle loro domande.", "8"],
    ["Chi valuta la sicurezza", "Sa chi può usare AMS, chi vede cosa e quanto vale una conferma.", "11"],
], "«TAB» — I lettori di questo manuale") + \
    p("Chi usa AMS per la prima volta può seguire il percorso guidato del " + rif(4) + ", che porta "
      "dall'installazione alla prima conferma in pochi passi. Gli utenti che ricevono i messaggi non hanno bisogno "
      "di leggere nulla: finestra e domanda si spiegano da sole, e non esiste un comando per loro.") + \
    tip("il funzionamento interno (archivio dei messaggi, consegna, sicurezza) è descritto nel Manuale Tecnico, "
        "installato accanto a questo in " + c("/usr/local/share/doc/ams/") + ".", "Per approfondire.")

S4 = table(["Convenzione", "Significato"], [
    [ui("Ho letto"), "Testo che compare sullo schermo: pulsanti, titoli delle finestre, campi, messaggi di AMS."],
    [c("ams send --to mario"), "Comandi, nomi di file e valori da scrivere così come sono."],
    [key("Ctrl", "S") + " " + key("Invio"), "Tasti da premere; il segno + vuol dire «insieme»."],
    [INVIATO + " " + CONSEGNATO + " " + CONFERMATO, "I tre stati di un destinatario, sempre con questi colori, "
     "gli stessi della TUI."],
    [RITIRATO + " " + SCADUTO, "Proprietà del messaggio, non stati dei destinatari: da quel momento il messaggio "
     "non viene più mostrato."],
    ["Riquadro blu <b>Nota</b>", "Informazione utile per capire."],
    ["Riquadro verde <b>Consiglio</b>", "Un modo migliore o più sicuro di fare una cosa."],
    ["Riquadro giallo <b>Attenzione</b>", "Un comportamento che può sorprendere o far perdere dati."],
], "«TAB» — Le convenzioni del manuale") + \
    p("Negli esempi " + c("admin") + " è un amministratore; " + c("mario") + ", " + c("anna") + " e " + c("luca")
      + " sono utenti della macchina " + c("server") + ", " + c("@sviluppo") + " è un gruppo. Nei riquadri scuri "
      "le righe che iniziano con il prompt (" + c("admin@server:~$") + ") sono comandi da scrivere; le righe "
      "arancioni sono quelle che AMS mostra agli utenti; quelle rosse sono errori. Le schermate della TUI sono "
      "vere, prese da AMS in funzione.") + \
    note("questo manuale descrive AMS " + VERSION + ". Il comando " + c("ams version") + " mostra la versione "
         "installata.", "Versione.") + \
    warn(c("ams") + " lavora sempre come amministratore (root) e chiede la password di sudo, anche solo per "
         "mostrare la guida: è una scelta, non un errore.", "Sempre con sudo.")

CHAPTER = ("Benvenuto", [
    ("Che cos'è AMS", S1),
    ("Cosa fa, e cosa no", S2),
    ("A chi è rivolto questo manuale", S3),
    ("Convenzioni", S4),
])
