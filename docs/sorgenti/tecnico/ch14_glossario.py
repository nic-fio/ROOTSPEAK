from build import c, dl

S1 = dl([
    ("aggancio", c("/etc/profile.d/ams.sh") + ": collega AMS al prompt di bash."),
    ("agente", c("ams-user agent") + ": mostra le finestre di conferma nella sessione grafica."),
    ("consegnato", "stato di un destinatario la cui copia è nella casella (riga in " + c("sent/ID/delivery") + ")."),
    ("inviato", "stato di un destinatario senza ancora la copia nella casella."),
    ("as_user", "funzione di " + c("bin/ams") + " che esegue un comando con l'identità di un utente (" + c("runuser") + ")."),
    ("canale", "da dove arriva una conferma: " + c("desktop") + " o " + c("terminale pts/N") + "."),
    ("casella", "la cartella " + c("/var/lib/ams/users/U") + " di un utente."),
    ("copia di riferimento", "il messaggio in " + c("sent/ID/msg") + ", accessibile solo a root."),
    ("modalità di prova", c("AMS_TEST=1") + " con un archivio di prova: si prova il codice senza root."),
    ("rinvio", "la risposta «no» o «Più tardi»: il file " + c("state/ID.term") + " o " + c("state/ID.gui") + "."),
    ("sveglia", "il segnale " + c("SIGUSR1") + " che " + c("ams send") + " manda all'agente."),
], cls="gloss")

CHAPTER = ("Glossario", [
    ("Termini", S1),
])
