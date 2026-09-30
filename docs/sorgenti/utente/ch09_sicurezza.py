from build import c, note, p, table, term, tip

S1 = p("Solo gli amministratori della macchina possono usare " + c("ams") + ": i membri del gruppo " + c("sudo")
       + " (su Fedora e simili " + c("wheel") + "). AMS non ha un elenco suo: chi entra o esce dal gruppo ottiene "
       "o perde subito l'accesso.", lead=True) + term(
    "mario@server:~$ ams list\n"
    "bash: /usr/local/bin/ams: Permesso negato", "Un utente normale") + \
    p(c("ams") + " lavora sempre come amministratore, anche per mostrare la guida: per questo chiede la password di "
      "sudo. Per aggiungere un amministratore:") + term("admin@server:~$ sudo usermod -aG sudo anna", "") + \
    p("Anna deve poi uscire e rientrare perché la modifica abbia effetto.")

S2 = table(["Chi", "Cosa vede"], [
    ["un amministratore", "tutti i messaggi mandati, i destinatari e le conferme"],
    ["un utente", "solo i messaggi indirizzati a lui"],
    ["gli altri utenti", "nulla dei messaggi di un collega"],
], "«TAB» — Chi vede cosa") + \
    p("Gli utenti non hanno comandi di AMS: non possono mandare messaggi, né vedere chi ha confermato.")

S3 = p("La conferma registra che l'utente <b>dichiara</b> di aver letto il messaggio, come le spunte di lettura di "
       "un'app di messaggistica. Non può provare che l'abbia letto davvero.", lead=True) + \
    note("per la stessa ragione un utente esperto potrebbe confermare un messaggio senza aprirlo. Resta comunque una "
         "sua dichiarazione, con data e ora, come il clic su «Ho letto».")

S4 = p("Prima di salvare un messaggio, AMS toglie dal testo e dal titolo i caratteri invisibili e i codici che "
       "cambiano colori o titolo delle finestre di terminale. Un messaggio non può quindi alterare i terminali "
       "degli utenti, anche se il testo è stato incollato da una fonte sconosciuta.", lead=True) + \
    tip("i dettagli, per chi deve valutare la sicurezza di AMS, sono nel manuale tecnico.", "Approfondire.")

CHAPTER = ("Sicurezza e riservatezza", [
    ("Chi può usare AMS", S1),
    ("Chi vede i messaggi", S2),
    ("Cosa vale una conferma", S3),
    ("Testo sicuro", S4),
])
