from build import arrow, box, c, diamond, fig, flow, p, path, seq, table, text, ul

S1 = flow([("bash interattiva", "$- contiene i", "dark"), ("/etc/profile.d/ams.sh", "una volta per shell", "blue"),
           ("PROMPT_COMMAND", "+ __ams_prompt", "blue"), ("casella vuota?", "compgen -G, nessun processo", "navy"),
           ("ams-user prompt", "solo se serve", "light")], "«FIG» — Dall'aggancio alla domanda") + ul([
    "L'aggancio agisce solo in bash interattiva, e una volta per shell (variabile " + c("__AMS_HOOK") + ").",
    "Aggiunge " + c("__ams_prompt") + " a " + c("PROMPT_COMMAND") + ": come elemento se è un array (bash 5.1 e "
    "successive), in testa se è una stringa.",
    c("__ams_prompt") + " conserva " + c("$?") + " e controlla la casella con " + c("compgen -G") + ", senza lanciare "
    "processi: con la casella vuota il prompt non costa nulla.",
    "In una shell di login chiama subito " + c("ams-user prompt --login") + ", così il messaggio compare prima del primo "
    "prompt.",
    "Su Debian le shell non di login non leggono " + c("/etc/profile.d") + ": l'aggancio è richiamato anche da "
    + c("/etc/bash.bashrc") + ".",
])

PROMPT = fig(
    box(20, 40, 170, 54, "pending", "inbox in ordine", "dark")
    + diamond(330, 67, 200, 70, "livello info?", "navy")
    + box(520, 40, 170, 54, "mostra", "mark_shown → read/", "light")
    + diamond(330, 180, 220, 76, "rimandato da poco?", "amber")
    + box(520, 153, 170, 54, "conta", "promemoria di una riga", "soft")
    + box(245, 262, 170, 54, "mostra e chiede", "ask: [s/N]", "blue")
    + box(520, 262, 170, 54, "esito", "ack · snooze · fermo", "green")
    + arrow(192, 67, 228, 67) + arrow(432, 67, 518, 67, "#0050C0", False, "sì", 472, 58)
    + arrow(330, 104, 330, 140, "#475569", False, "no", 346, 124)
    + arrow(442, 180, 518, 180, "#d97706", False, "sì (non al login)", 480, 170)
    + arrow(330, 220, 330, 260, "#475569", False, "no", 346, 244)
    + arrow(417, 289, 518, 289)
    + text(780, 60, "l'ultimo passo: se ci sono", 11, "#475569", "400") + text(780, 76, "messaggi rimandati, una riga", 11, "#475569")
    + text(780, 92, "«Hai N messaggi da confermare»", 11, "#92400e", "600"),
    900, 336, "«FIG» — ams-user prompt, per ogni messaggio della casella", "Il giro di ams-user prompt")

S2 = p(c("ams-user prompt") + " prende i messaggi della casella in ordine di numero. Quelli scaduti passano subito in "
       + c("read/") + ".", lead=True) + PROMPT + table(["Esito di ask", "Cosa fa", "Stampa"], [
    ["0 · «s»", c("ack ID \"terminale pts/N\""), "[AMS] Confermato."],
    ["1 · altro, o solo Invio", c("snooze ID term") + ": tocca " + c("state/ID.term"), "[AMS] La domanda verrà riproposta tra N minuti."],
    ["2 · confermato altrove", "sposta in " + c("read/"), "[AMS] Messaggio già confermato altrove…"],
    ["3 · ritirato", "nulla", "[AMS] L'amministratore ha ritirato il messaggio."],
], "«TAB» — Gli esiti della domanda")

ASK = seq([("Utente", "tastiera", "dark"), ("ask", "read -t 1", "blue"), ("Casella", "users/U", "soft")], [
    (1, 0, "[AMS] Confermi di aver letto il messaggio? [s/N]"),
    (1, 1, "attende 1 secondo"),
    (1, 2, "acks/ID comparso? inbox/ID sparito?"),
    (1, 1, "no: ricomincia"),
    ("sep", "intanto l'utente conferma dal desktop"),
    (1, 2, "acks/ID esiste"),
    (1, 0, "esito 2: «già confermato altrove»", True),
], "«FIG» — La domanda si accorge di ciò che succede altrove", "Una domanda che controlla ogni secondo")

S3 = p(c("ask") + " legge la risposta da " + c("/dev/tty") + " con " + c("read -t 1") + " in un ciclo. A ogni secondo "
       "senza risposta controlla la casella: se è comparsa la conferma, l'utente ha confermato altrove; se il messaggio "
       "è sparito, è stato ritirato.", lead=True) + ASK + \
    p("Il terminale resta in modo canonico: ciò che l'utente sta scrivendo resta nel buffer del terminale e non si "
      "perde fra un secondo e l'altro. Il rinvio vale " + c("AMS_REMIND_MINUTES") + " dalla data di modifica di "
      + c("state/ID.term") + "; con " + c("--login") + " non vale.")

CHAPTER = ("La ricezione nel terminale", [
    ("L'aggancio della shell", S1),
    ("ams-user prompt", S2),
    ("La domanda e l'attesa", S3),
])
