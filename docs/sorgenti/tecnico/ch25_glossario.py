from build import arrow, box, c, dl, fig, text


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">capitolo {n}{"." + str(s) if s else ""}</a>'


MAPPA = fig(
    box(20, 60, 150, 50, "messaggio", "sent/ID/msg", "navy", 12)
    + box(220, 60, 150, 50, "destinatario", "uno per riga", "navy", 12)
    + box(420, 20, 150, 50, "casella", "users/U/", "blue", 12)
    + box(420, 100, 150, 50, "stato", "uno di tre", "green", 12)
    + box(620, 20, 120, 50, "canale", "terminale, desktop", "light", 11)
    + box(620, 100, 120, 50, "conferma", "acks/ID", "green", 12)
    + box(780, 60, 100, 50, "evento", "journal", "soft", 12)
    + arrow(172, 85, 218, 85) + arrow(372, 78, 418, 50) + arrow(372, 92, 418, 122)
    + arrow(572, 45, 618, 45) + arrow(572, 125, 618, 125) + arrow(680, 72, 680, 98)
    + arrow(742, 115, 778, 92, "#475569", True)
    + text(450, 176, "i termini del glossario e come si collegano", 11.5, "#475569", "600"),
    900, 192, "«FIG» — I termini principali", "Mappa dei termini")

S1 = MAPPA + dl([
    ("agente", c("ams-user agent") + ": mostra le finestre di conferma nella sessione grafica; uno per utente ("
     + cap(12) + ")."),
    ("aggancio", "il file che collega AMS alla shell: " + c("ams.bash") + ", " + c("ams.zsh") + ", " + c("ams.fish")
     + " e, per le altre shell, " + c("/etc/profile.d/ams.sh") + " (" + cap(11) + ")."),
    ("archivio", "la cartella " + c("/var/lib/ams") + ": " + c("sent/") + " di root e le caselle degli utenti ("
     + cap(5) + ")."),
    ("autore", "l'amministratore che ha lanciato " + c("ams") + " (" + c("SUDO_USER") + "): il mittente dei messaggi "
     "e l'autore degli eventi."),
    ("canale", "da dove arriva una conferma: " + c("desktop") + " o " + c("terminale pts/N") + "; si salva senza "
     "lingua e si traduce quando si mostra."),
    ("casella", "la cartella " + c("/var/lib/ams/users/U") + " di un utente, sua, con permessi " + c("700") + "."),
    ("catalogo", "il file " + c(".mo") + " con le traduzioni di una lingua, compilato da " + c("po/LINGUA.po")
     + " (" + cap(16, 3) + ")."),
    ("come_utente", "la funzione di " + c("src/utente.c") + " che esegue un'operazione in un processo figlio con "
     "l'identità di un utente, con un tempo massimo (" + cap(7) + ")."),
    ("conferma", "la dichiarazione di lettura dell'utente in " + c("acks/ID") + ", con data e canale; vale la prima "
     "(" + cap(13) + ")."),
    ("confermato", "stato di un destinatario con una conferma valida: non successiva alla scadenza né al ritiro. È "
     "una dichiarazione dell'utente, non una prova di lettura."),
    ("consegnato", "stato di un destinatario la cui copia è stata scritta e verificata nella casella (riga in "
     + c("sent/ID/delivery") + ") e che non ha una conferma valida."),
    ("copia di riferimento", "il messaggio in " + c("sent/ID/msg") + ", accessibile solo a root: l'unica scadenza "
     "che conta."),
    ("destinatario", "un utente a cui il messaggio è indirizzato; l'elenco è in " + c("sent/ID/recipients") + "."),
    ("evento", "una riga strutturata nel journal, con i campi " + c("AMS_*") + " (" + cap(18) + ")."),
    ("gruppo degli amministratori", "il gruppo esistente " + c("sudo") + ", " + c("wheel") + " o " + c("admin")
     + ": AMS non ha un gruppo suo."),
    ("impronta", "lo SHA-256 abbreviato del codice (" + c("tools/impronta.sh") + "), registrato con i risultati delle "
     "prove (" + cap(21, 1) + ")."),
    ("inviato", "stato di un destinatario senza ancora la copia nella casella."),
    ("lock", "il file " + c("sent/ID/lock") + " usato con " + c("flock") + ": tenuto da " + c("ams send")
     + " per tutta la consegna, distingue un invio in corso da uno interrotto."),
], cls="gloss")

S2 = dl([
    ("messaggio", "un testo con titolo e scadenza facoltativi e un numero progressivo (ID)."),
    ("modalità di prova", c("AMS_TEST=1") + " con un archivio di prova: si prova il codice senza root ("
     + cap(4, 3) + ")."),
    ("proprietà del messaggio", "ritirato e scaduto: valgono per il messaggio, non per un destinatario, e non sono "
     "stati."),
    ("pronto", "un agente che ha preparato la ricezione della sveglia e ha scritto il suo PID in "
     + c("ams-agent.pronto") + "."),
    ("punto di linearizzazione", "l'istante in cui un'operazione si considera avvenuta per chiunque osservi ("
     + cap(20, 4) + ")."),
    ("recupero", c("recupera") + ": completa invii, ritiri e cancellazioni interrotti all'inizio dei comandi "
     "successivi (" + cap(8, 6) + ")."),
    ("riassunto", "un messaggio descritto con i conteggi dei destinatari nei tre stati, a parole e con una barra ("
     + cap(10, 3) + ")."),
    ("rinvio", "la risposta «no» o «Più tardi»: il file " + c("state/ID.term") + " o " + c("state/ID.gui")
     + ", la cui data di modifica conta per " + c("AMS_REMIND_MINUTES") + " minuti."),
    ("ritirato", "proprietà di un messaggio con " + c("sent/ID/revoked") + ": non si mostra più, e le conferme "
     "successive non valgono."),
    ("scaduto", "proprietà di un messaggio la cui scadenza è passata: non si mostra più, e le conferme successive "
     "non valgono."),
    ("segno interno", c("incomplete") + ", " + c("ritiro") + ", " + c("failed") + ", " + c(".cancella-ID")
     + ": file con cui il recupero sa che cosa completare o annullare. Non sono stati."),
    ("sollecito", c("ams remind") + ": toglie i rinvii di chi è consegnato e sveglia il suo agente ("
     + cap(9, 2) + ")."),
    ("sveglia", "il segnale " + c("SIGUSR1") + " che " + c("ams send") + " e " + c("ams remind") + " mandano "
     "all'agente pronto."),
    ("TUI", "l'interfaccia a tutto schermo per gli amministratori: " + c("ams") + " senza argomenti in un terminale "
     "(" + cap(14) + ")."),
    ("zenity", "il programma che disegna la finestra «Ho letto» / «Più tardi» sul desktop."),
], cls="gloss")

CHAPTER = ("Glossario", [
    ("Termini A–L", S1),
    ("Termini M–Z", S2),
])
