import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import arrow, box, c, diamond, fig, flow, key, note, p, path, steps, table, term, text, tip, warn  # noqa: E402
from _aiuti import CONFERMATO, CONSEGNATO, INVIATO, rif  # noqa: E402

S1 = p("Quando un comando non va a buon fine, " + c("ams") + " stampa una riga in rosso che inizia con " + c("ams:")
       + ", dice cosa correggere ed esce con esito 1. Nella TUI la stessa riga compare nella finestra "
       "dell'esito.", lead=True) + term(
    'admin@server:~$ ams send --to mrio "Riunione alle 11."\n'
    "ams: utente inesistente: mrio", "Un errore tipico") + \
    table(["Messaggio", "Cosa significa", "Cosa fare"], [
        [c("manca --to"), "nessun destinatario", "aggiungere " + c("--to") + " (" + rif(5, 1) + ")"],
        [c("manca il valore di --to"), "un'opzione senza il suo valore (vale anche per " + c("--title") + ", "
         + c("--expires") + ", " + c("--file") + ")", "scrivere il valore dopo l'opzione"],
        [c("utente inesistente: NOME"), "il nome non è un utente della macchina", "controllare il nome"],
        [c("gruppo inesistente: NOME"), "il gruppo dopo " + c("@") + " non esiste", "controllare il nome del gruppo"],
        [c("nessun destinatario"), "i destinatari indicati sono vuoti, per esempio " + c("online") + " quando nessuno "
         "è collegato", "scegliere altri destinatari"],
        [c("messaggio vuoto"), "manca il testo, o contiene solo spazi", "scrivere il testo"],
        [c("messaggio troppo lungo: N byte (al massimo 65536)"), "il testo supera i 64 KB", "accorciarlo, o mettere "
         "il testo completo in un file condiviso e mandare il messaggio con il percorso"],
        [c("scadenza non valida: X"), "la scadenza non è stata capita", "usare " + c("2h") + " o "
         + c('"2026-10-04 12:00"') + " (" + rif(5, 3) + ")"],
        [c("la scadenza è già passata"), "la data indicata è nel passato", "correggere la data"],
        [c("opzione sconosciuta: X"), "opzione scritta male", c("ams --help")],
        [c("comando sconosciuto: X (ams --help per la guida)"), "comando scritto male", c("ams --help")],
        [c("manca l'ID del messaggio"), c("status") + ", " + c("revoke") + ", " + c("remind") + " o " + c("log")
         + " senza numero", "aggiungere il numero, da " + c("ams list")],
        [c("messaggio inesistente: ID"), "nessun messaggio con quel numero (o già cancellato)", "controllare con "
         + c("ams list")],
        [c("manca la durata, per esempio 90d") + "<br>" + c("durata non valida: X (per esempio 90d, 12h, 30m)"),
         c("ams purge") + " senza durata o con una durata scritta male", "scrivere un numero seguito da "
         + c("d") + ", " + c("h") + " o " + c("m")],
        [c("il messaggio N è stato ritirato: nessuno da sollecitare") + "<br>" + c("il messaggio N è scaduto: nessuno "
           "da sollecitare"), "sollecito di un messaggio che non si mostra più", "nulla; per chiedere di nuovo, un "
         "messaggio nuovo"],
        [c("messaggio N non consegnato a: … (vedi il registro; il prossimo comando ams riproverà)"), "per quegli utenti "
         "la copia non si è potuta scrivere; gli altri l'hanno ricevuta", "risolvere la causa, spesso il disco pieno "
         "(" + rif(12, 4) + ")"],
        [c("messaggio N ritirato, ma alcune copie non si sono potute togliere dalle caselle: il prossimo comando ams "
           "riproverà"), "durante il ritiro la casella di un utente non era raggiungibile", "nulla: AMS riprova"],
        [c("FILE: …"), "con " + c("--file") + ": il file non esiste o non si può leggere; la spiegazione è quella del "
         "sistema, in inglese (per esempio " + c("No such file or directory") + ")", "controllare il percorso"],
    ], "«TAB» — I messaggi di errore")

S2 = table(["Problema", "Causa probabile", "Rimedio"], [
    [c("ams: comando non trovato"), "AMS non è installato", "lanciare " + c("./install.sh") + " (" + rif(2, 2) + ")"],
    [c("Permesso negato"), "chi lo lancia non è un amministratore", "è voluto (" + rif(11, 1) + ")"],
    [c("ams") + " da solo mostra la guida invece della TUI", "il terminale è più piccolo di 80 colonne o di 20 righe, "
     "oppure l'uscita non è un terminale", "allargare la finestra, oppure usare i comandi"],
    ["la TUI si è chiusa da sola", "la finestra è stata rimpicciolita sotto 80 × 20", "allargarla e riaprire " + c("ams")],
    ["nel terminale arriva il testo ma non la domanda", "la finestra di terminale era aperta prima "
     "dell'installazione; oppure la shell è sh, dash o ksh (domanda solo al login) o tcsh (nessuna domanda); "
     "oppure zsh è stata installata dopo AMS", "aprire una nuova finestra o rientrare; per zsh installata dopo, "
     "rilanciare " + c("./install.sh") + " (" + rif(8, 3) + ")"],
    ["AMS compare in inglese a un utente", "la sua sessione non ha una lingua italiana (" + c("LANG") + " vuota, "
     + c("C") + " o un'altra lingua)", "impostare " + c("LANG=it_IT.UTF-8") + " per l'utente o per il sistema"],
    ["sul desktop non compare nessuna finestra", "manca " + c("zenity") + ", oppure la sessione grafica è stata "
     "aperta prima dell'installazione e l'agente non è partito", "installare " + c("zenity") + "; l'agente parte da "
     "solo al primo messaggio nuovo o al prossimo accesso"],
    ["due finestre uguali", "lo stesso messaggio è stato mandato due volte (due numeri diversi nella lista)",
     "ritirare il doppione (" + rif(7, 1) + ")"],
    ["un utente entrato con " + c("su") + " non vede il testo all'invio", "con " + c("su") + " la finestra di "
     "terminale resta di chi l'ha aperta", "vede comunque la domanda al prompt successivo; con " + c("ssh")
     + " tutto funziona normalmente"],
    ["un utente vede «Non è stato possibile registrare la conferma»", "la sua casella non è scrivibile, per esempio "
     "perché il disco è pieno", "liberare spazio: il messaggio viene richiesto di nuovo e la conferma non va persa"],
    ["un destinatario resta " + INVIATO, "la sua copia non si è potuta scrivere", "vedere " + rif(12, 4)],
    [key("Ctrl", "E") + " apre nano e non il mio editor", "sudo non conserva " + c("VISUAL") + " ed " + c("EDITOR"),
     rif(10, 3)],
    ["un utente dice di non aver visto nulla", "—", "seguire la procedura del " + rif(12, 3)],
], "«TAB» — Problemi frequenti")

DIAGNOSI = fig(
    diamond(170, 110, 260, 90, "Che stato ha?", "navy")
    + box(360, 40, 240, 54, "inviato", "la copia non è arrivata: 12.4", "grey")
    + box(360, 118, 240, 54, "consegnato", "ha la copia, non ha confermato", "amber")
    + box(360, 196, 240, 54, "confermato", "ha dichiarato di aver letto", "green")
    + box(650, 118, 230, 54, "Era collegato? Rimanda?", "dettaglio e storia del messaggio", "blue")
    + box(650, 196, 230, 54, "Da dove, e quando", "desktop o terminale, con l'ora", "blue")
    + path([(210, 80), (210, 67), (356, 67)], "#475569")
    + arrow(300, 110, 356, 140, "#475569")
    + path([(210, 140), (210, 223), (356, 223)], "#475569")
    + arrow(602, 145, 646, 145, "#0050C0") + arrow(602, 223, 646, 223, "#0050C0")
    + text(450, 290, "Il punto di partenza è sempre il dettaglio del messaggio (Invio nella TUI, o ams status)",
           11.5, "#334155", "600"),
    900, 310, "«FIG» — Da dove partire quando un utente dice di non aver visto un messaggio", "La diagnosi")

S3 = p("È la domanda più comune. La risposta è quasi sempre nel dettaglio del messaggio e nella sua storia.",
       lead=True) + DIAGNOSI + steps([
        "Aprire il messaggio nella TUI (" + key("Invio") + ") oppure lanciare " + c("ams status ID") + ", e trovare "
        "la riga dell'utente.",
        "Se è " + CONFERMATO + ", la riga dice quando e da dove: per esempio «confermato il 30/09 16:56 (desktop)». "
        "L'utente ha confermato, forse senza leggere con attenzione (" + rif(11, 3) + ").",
        "Se è " + CONSEGNATO + ", guardare i dettagli: «scritto su 2 terminali» vuol dire che il testo è comparso "
        "sui suoi schermi; «rimandato il …» che ha visto la domanda o la finestra e ha rimandato. Se non c'è nessuno "
        "dei due, probabilmente non si è ancora collegato.",
        "Se è " + INVIATO + ", la copia non è arrivata nella sua casella: vedere " + rif(12, 4) + ".",
        "Nella scheda " + key("Tab") + " " + "«Storia» (o con " + c("ams log ID") + ") ci sono tutti gli eventi, "
        "rinvii compresi, al secondo.",
        "Se serve, sollecitarlo (" + rif(7, 2) + "): la finestra torna subito sul suo desktop.",
    ]) + tip("un utente che lavora solo con ssh e con una shell come tcsh non riceve la domanda nel terminale: vede il "
             "testo all'invio, ma può confermare solo dal desktop. Con bash, zsh o fish il problema non c'è.",
             "Shell insolite.")

RECUPERO = flow([("Invio interrotto", "disco pieno, corrente…", "grey"), ("Prossimo ams", "list, status, TUI…", "navy"),
                 ("Recupero", "riscrive le copie mancanti", "blue"), ("Tutti consegnati", "o l'avviso di chi manca", "green")],
                "«FIG» — AMS completa da solo le consegne rimaste indietro", "Il recupero")

S4 = p("Se un invio si interrompe a metà (il disco si riempie, " + c("ams") + " viene fermato, manca la corrente) "
       "AMS non perde il messaggio: al primo uso successivo lo riprende da dove si era fermato.", lead=True) + \
    RECUPERO + \
    table(["Avviso", "Cosa vuol dire", "Cosa fare"], [
        [c("ams: completata la consegna del messaggio N a K destinatari"), "le copie mancanti sono state scritte: "
         "quei destinatari sono ora " + CONSEGNATO, "nulla"],
        [c("ams: messaggio N ancora non consegnato a K destinatari (vedi ams status N)"), "per qualcuno la copia "
         "ancora non si scrive", "risolvere la causa, di solito lo spazio su disco; poi usare di nuovo " + c("ams")],
        [c("ams: il messaggio N era stato interrotto prima di essere salvato ed è stato annullato"), "l'invio si è "
         "fermato prima ancora di salvare il messaggio: nessuno l'ha ricevuto", "mandarlo di nuovo"],
        [c("[invio annullato: interrotto prima del salvataggio]") + " in " + c("ams list"), "lo stesso caso, "
         "nell'elenco", "mandarlo di nuovo"],
    ], "«TAB» — Gli avvisi del recupero") + \
    note("il recupero parte all'inizio di " + c("ams send") + ", " + c("list") + ", " + c("status") + ", "
         + c("revoke") + ", " + c("remind") + ", " + c("log") + " e all'apertura della TUI. Non serve fare altro che "
         "usare AMS.", "Quando parte.") + \
    warn("con il disco pieno anche le conferme degli utenti non si possono salvare: gli utenti vedono «Non è stato "
         "possibile registrare la conferma» e il messaggio viene richiesto di nuovo. Liberare spazio in "
         + c("/var/lib") + " risolve entrambe le cose.", "Disco pieno.")

S5 = table(["Cosa", "Dove"], [
    ["il comando", c("/usr/local/bin/ams")],
    ["le impostazioni", c("/etc/ams/ams.conf")],
    ["i messaggi e le conferme", c("/var/lib/ams/")],
    ["il registro", c("sudo journalctl -t ams")],
    ["la guida", c("ams --help")],
    ["i manuali", c("/usr/local/share/doc/ams/AMS_Manuale_Utente.html") + " e " + c("AMS_Manuale_Tecnico.html")],
    ["gli agganci delle shell", c("/etc/profile.d/ams.sh") + ", " + c("/usr/local/lib/ams/ams.bash") + ", "
     + c("ams.zsh") + ", " + c("/etc/fish/conf.d/ams.fish")],
    ["l'avvio sul desktop", c("/etc/xdg/autostart/ams-agent.desktop")],
    ["il codice", c("https://github.com/nic-fio/AMS") + " (privato)"],
], "«TAB» — Dove trovare le cose") + \
    tip("quando qualcosa non torna, i posti da guardare sono, nell'ordine: il dettaglio del messaggio, la sua storia, "
        "il registro con " + c("sudo journalctl -t ams") + ", e la guida integrata.", "Dove guardare.")

CHAPTER = ("Risoluzione dei problemi", [
    ("Messaggi di errore", S1),
    ("Problemi frequenti", S2),
    ("«Non ho visto nessun messaggio»", S3),
    ("Invii interrotti", S4),
    ("File e cartelle utili", S5),
])
