from build import c, flow, note, p, pill, steps, term, tip

S1 = p("Dall'installazione alla prima conferma ci sono quattro tappe. Ognuna rimanda al capitolo che la spiega "
       "nel dettaglio.", lead=True) + \
    flow([("1. Installa", "./install.sh", "dark"), ("2. Invia", "ams send", "blue"),
          ("3. L'utente conferma", "finestra o terminale", "blue"), ("4. Controlla", "ams status", "green")],
         "«FIG» — Le quattro tappe dei primi passi")

S2 = steps([
    "Scrivere il comando con il destinatario, un titolo e il testo:" + term(
        'admin@server:~$ ams send --to mario --title Manutenzione "Server spento sabato dalle 8 alle 12."\n'
        "[sudo] password di admin:\n"
        "Messaggio 1 inviato a 1 utente.", ""),
    "Inserire la password: " + c("ams") + " la chiede sempre, perché lavora come amministratore.",
    "Annotare il numero del messaggio (qui " + c("1") + "): serve per controllarlo o ritirarlo.",
]) + note("se Mario è collegato, il messaggio gli compare subito; altrimenti lo troverà al prossimo accesso. "
          "Il capitolo 6 mostra cosa vede.", "E Mario?")

S3 = p("Dopo qualche minuto si controlla chi ha letto:") + term(
    "admin@server:~$ ams status 1\n"
    "Messaggio 1 · ack · Manutenzione · 03/10 18:30 · da admin\n"
    "  │ Sabato dalle 8 alle 12 il server sarà spento.\n"
    "\n"
    "UTENTE           STATO\n"
    "mario            confermato il 03/10 18:31 (desktop)") + \
    p("Mario ha premuto " + pill("Ho letto", "ok") + " nella finestra del desktop un minuto dopo l'invio.") + \
    tip("con " + c("ams list") + " si vedono tutti i messaggi mandati, ognuno con quante conferme ha ricevuto "
        "(capitolo 5).", "E poi?")

CHAPTER = ("Primi passi", [
    ("Il percorso", S1),
    ("Mandare il primo messaggio", S2),
    ("Vedere chi ha letto", S3),
])
