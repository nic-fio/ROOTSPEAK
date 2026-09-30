from build import c, p, table, tip

S1 = p("Quando un comando non va a buon fine, " + c("ams") + " stampa una riga che inizia con " + c("ams:")
       + " e dice cosa correggere.", lead=True) + table(["Messaggio", "Cosa significa", "Cosa fare"], [
    [c("manca --to"), "nessun destinatario", "aggiungere " + c("--to") + " (capitolo 4.1)"],
    [c("utente inesistente: NOME"), "il nome non è un utente della macchina", "controllare il nome"],
    [c("gruppo inesistente: NOME"), "il gruppo dopo " + c("@") + " non esiste", "controllare il nome del gruppo"],
    [c("nessun destinatario"), "i destinatari indicati sono vuoti, per esempio " + c("online") + " quando nessuno è collegato", "scegliere altri destinatari"],
    [c("livello non valido: X (info o ack)"), c("--level") + " accetta solo " + c("info") + " e " + c("ack"), "correggere il livello"],
    [c("messaggio vuoto"), "manca il testo, o contiene solo spazi", "scrivere il testo"],
    [c("scadenza non valida: X"), "la scadenza non è stata capita", "usare " + c("2h") + " o " + c('"2026-10-04 12:00"') + " (capitolo 4.4)"],
    [c("la scadenza è già passata"), "la data indicata è nel passato", "correggere la data"],
    [c("messaggio inesistente: ID"), "nessun messaggio con quel numero", "controllare con " + c("ams list")],
    [c("comando sconosciuto: X"), "comando scritto male", c("ams --help")],
    [c("opzione sconosciuta: X"), "opzione scritta male", c("ams --help")],
], "«TAB» — I messaggi di errore")

S2 = table(["Problema", "Causa probabile", "Rimedio"], [
    [c("ams: comando non trovato"), "AMS non è installato", "lanciare " + c("./install.sh")],
    [c("Permesso negato"), "l'utente non è un amministratore", "è voluto (capitolo 9.1)"],
    ["nel terminale arriva il testo ma non la domanda", "la finestra di terminale era aperta prima dell'installazione, oppure non usa bash",
     "aprire una nuova finestra; con zsh o fish, confermare dal desktop"],
    ["sul desktop non compare nessuna finestra", "manca " + c("zenity"), "installare " + c("zenity") + " e " + c("libnotify-bin") + " (capitolo 2.1)"],
    ["due finestre uguali", "lo stesso messaggio è stato mandato due volte (due numeri diversi in " + c("ams list") + ")",
     "ritirare il doppione con " + c("ams revoke")],
    ["un utente entrato con " + c("su") + " non vede il testo all'invio", "con " + c("su") + " la finestra di terminale resta di chi l'ha aperta",
     "vede comunque la domanda al prompt successivo; con " + c("ssh") + " tutto funziona normalmente"],
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
