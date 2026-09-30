from build import c, p, table, tip

S1 = p("Quando un comando non va a buon fine, " + c("ams") + " stampa una riga che inizia con " + c("ams:")
       + " e dice cosa correggere.", lead=True) + table(["Messaggio", "Cosa significa", "Cosa fare"], [
    [c("manca --to"), "nessun destinatario", "aggiungere " + c("--to") + " (capitolo 4.1)"],
    [c("utente inesistente: NOME"), "il nome non è un utente della macchina", "controllare il nome"],
    [c("gruppo inesistente: NOME"), "il gruppo dopo " + c("@") + " non esiste", "controllare il nome del gruppo"],
    [c("nessun destinatario"), "i destinatari indicati sono vuoti, per esempio " + c("online") + " quando nessuno è collegato", "scegliere altri destinatari"],
    [c("messaggio vuoto"), "manca il testo, o contiene solo spazi", "scrivere il testo"],
    [c("messaggio troppo lungo: N byte (al massimo 65536)"), "il testo supera i 64 KB", "accorciarlo, o mettere il "
     "testo completo in un file condiviso e mandare il messaggio con il percorso"],
    [c("… alcune copie non si sono potute togliere dalle caselle"), "durante " + c("ams revoke") + " la casella di un "
     "utente non era raggiungibile", "nulla: il prossimo comando " + c("ams") + " riprova"],
    [c("[non attendibile: scritto da UID N]") + " in " + c("ams log"), "un evento del registro è stato scritto da un "
     "utente diverso da quello che avrebbe dovuto scriverlo, per esempio una conferma falsa", "non considerarlo; "
     "lo stato vero è quello di " + c("ams status")],
    [c("scadenza non valida: X"), "la scadenza non è stata capita", "usare " + c("2h") + " o " + c('"2026-10-04 12:00"') + " (capitolo 4.4)"],
    [c("la scadenza è già passata"), "la data indicata è nel passato", "correggere la data"],
    [c("messaggio inesistente: ID"), "nessun messaggio con quel numero", "controllare con " + c("ams list")],
    [c("messaggio N non consegnato a: …"), "per quegli utenti la copia non si è potuta scrivere; gli altri l'hanno ricevuta",
     "risolvere la causa (spesso il disco pieno): il prossimo comando " + c("ams") + " completa la consegna"],
    [c("completata la consegna del messaggio N"), "un invio precedente si era interrotto a metà ed è stato completato", "nulla"],
    [c("il messaggio N … è stato annullato"), "un invio si era interrotto prima ancora di salvare il messaggio", "mandarlo di nuovo"],
    [c("comando sconosciuto: X"), "comando scritto male", c("ams --help")],
    [c("opzione sconosciuta: X"), "opzione scritta male", c("ams --help")],
], "«TAB» — I messaggi di errore")

S2 = table(["Problema", "Causa probabile", "Rimedio"], [
    [c("ams: comando non trovato"), "AMS non è installato", "lanciare " + c("./install.sh")],
    [c("Permesso negato"), "l'utente non è un amministratore", "è voluto (capitolo 9.1)"],
    ["nel terminale arriva il testo ma non la domanda", "la finestra di terminale era aperta prima dell'installazione; "
     "oppure l'utente usa sh, dash o ksh, che ricevono la domanda solo al login; oppure zsh è stata installata dopo AMS",
     "aprire una nuova finestra o rientrare; per zsh installata dopo, rilanciare " + c("./install.sh")],
    ["AMS compare in inglese", "la sessione non ha una lingua italiana (" + c("LANG") + " vuota, " + c("C")
     + " o un'altra lingua)", "impostare " + c("LANG=it_IT.UTF-8") + " per l'utente o per il sistema"],
    ["sul desktop non compare nessuna finestra", "manca " + c("zenity"), "installare " + c("zenity") + " (capitolo 2.1)"],
    ["due finestre uguali", "lo stesso messaggio è stato mandato due volte (due numeri diversi in " + c("ams list") + ")",
     "ritirare il doppione con " + c("ams revoke")],
    ["un utente entrato con " + c("su") + " non vede il testo all'invio", "con " + c("su") + " la finestra di terminale resta di chi l'ha aperta",
     "vede comunque la domanda al prompt successivo; con " + c("ssh") + " tutto funziona normalmente"],
    ["un utente vede «Non è stato possibile registrare la conferma»", "la sua casella non è scrivibile, per esempio "
     "perché il disco è pieno", "liberare spazio; il messaggio viene richiesto di nuovo e la conferma non va persa"],
    ["un utente dice di non aver visto nulla", "—", "guardare " + c("ams status") + " (era collegato? il testo è stato scritto nei suoi terminali?) e il registro (capitolo 5.5)"],
], "«TAB» — Problemi frequenti") + \
    tip("quando qualcosa non torna, i posti da guardare sono, nell'ordine: " + c("ams status") + " del messaggio, il "
        "registro con " + c("sudo journalctl -t ams") + ", e la guida integrata.", "Dove guardare.")

S3 = table(["Cosa", "Dove"], [
    ["il comando", c("/usr/local/bin/ams")],
    ["le impostazioni", c("/etc/ams/ams.conf")],
    ["i messaggi e le conferme", c("/var/lib/ams/")],
    ["il registro", c("sudo journalctl -t ams")],
    ["i manuali", c("/usr/local/share/doc/ams/")],
    ["il codice", c("https://github.com/nic-fio/AMS") + " (privato)"],
], "«TAB» — Dove trovare le cose")

CHAPTER = ("Risoluzione dei problemi", [
    ("Messaggi di errore", S1),
    ("Problemi frequenti", S2),
    ("Dove trovare le cose", S3),
])
