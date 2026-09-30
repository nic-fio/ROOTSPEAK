from build import c, dl

S1 = dl([
    ("aggancio", "il file che collega AMS alla shell: " + c("ams.bash") + ", " + c("ams.zsh") + ", " + c("ams.fish")
     + " e, per le altre shell, " + c("/etc/profile.d/ams.sh") + "."),
    ("agente", c("ams-user agent") + ": mostra le finestre di conferma nella sessione grafica."),
    ("consegnato", "stato di un destinatario la cui copia è nella casella (riga in " + c("sent/ID/delivery") + ")."),
    ("inviato", "stato di un destinatario senza ancora la copia nella casella."),
    ("come_utente", "funzione di " + c("src/utente.c") + " che esegue un'operazione in un processo figlio con l'identità "
     "di un utente, con un tempo massimo."),
    ("catalogo", "il file " + c(".mo") + " con le traduzioni di una lingua, compilato da " + c("po/LINGUA.po") + "."),
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
