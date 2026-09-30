from build import c, dl

S1 = dl([
    ("agente del desktop", "La parte di AMS che, nella sessione grafica dell'utente, mostra le finestre di conferma."),
    ("casella", "Lo spazio in cui AMS tiene i messaggi di un utente finché non li ha confermati."),
    ("confermato", "Terzo e ultimo stato di un destinatario: ha dichiarato di aver letto il messaggio. È la sua "
     "dichiarazione, non una prova che l'abbia letto davvero."),
    ("consegnato", "Secondo stato: la copia del messaggio è nella casella dell'utente."),
    ("conferma", "La dichiarazione dell'utente di aver letto un messaggio: un clic su «Ho letto» o la risposta «s»."),
    ("destinatari", "Gli utenti che ricevono un messaggio: nomi, gruppi, " + c("online") + ", " + c("all") + "."),
    ("inviato", "Primo stato: il messaggio è partito, ma la copia non è ancora nella casella dell'utente."),
    ("rimandare", "Premere «Più tardi» o rispondere «no»: il messaggio viene riproposto dopo 30 minuti."),
    ("ritirare", "Togliere un messaggio con " + c("ams revoke") + ": chi non l'ha visto non lo vedrà più."),
    ("scadenza", "Il momento dopo il quale un messaggio non viene più mostrato (" + c("--expires") + ")."),
    ("sessione", "Un accesso di un utente alla macchina: il desktop, una console, una connessione ssh."),
    ("sollecitare", "Chiedere di nuovo, subito, la conferma a chi non l'ha ancora data: " + c("ams remind") + " o il tasto "
     + c("s") + " della TUI."),
    ("TUI", "L'interfaccia a tutto schermo che si apre scrivendo " + c("ams") + " da solo in un terminale."),
], cls="gloss")

CHAPTER = ("Glossario", [
    ("Termini", S1),
])
