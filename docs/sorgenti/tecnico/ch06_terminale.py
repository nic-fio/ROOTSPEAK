from build import arrow, box, c, diamond, fig, flow, p, path, seq, table, text, ul

S1 = p("Ogni shell ha il suo aggancio, installato dove quella shell lo legge. Tutti fanno la stessa cosa: se la "
       "casella contiene messaggi, lanciano " + c("ams-user prompt") + ", subito al login e poi prima di ogni prompt.",
       lead=True) + table(["Shell", "File", "Letto da", "Quando chiede"], [
    ["bash", c("lib/ams/ams.bash"), c("/etc/profile.d/ams.sh") + " e " + c("/etc/bash.bashrc"), "al login e a ogni prompt (" + c("PROMPT_COMMAND") + ")"],
    ["zsh", c("lib/ams/ams.zsh"), "una riga in " + c("/etc/zsh/zshrc") + " (o " + c("/etc/zshrc") + ")", "al login e a ogni prompt (" + c("precmd") + ")"],
    ["fish", c("/etc/fish/conf.d/ams.fish"), "fish stessa, all'avvio", "al login e a ogni prompt (evento " + c("fish_prompt") + ")"],
    ["sh, dash, ksh…", c("/etc/profile.d/ams.sh"), c("/etc/profile") + ", nelle shell di login", "solo al login"],
], "«TAB» — Gli agganci delle shell") + \
    p("Il testo del messaggio arriva nel terminale all'invio con qualunque shell: lo scrive root, non la shell. "
      "dash e le shell simili non hanno un punto in cui agganciarsi prima del prompt: la domanda arriva al login "
      "successivo, o dalla finestra del desktop. " + c("profile.d/ams.sh") + " è scritto in sh semplice perché lo "
      "leggono tutte; il codice proprio di bash sta in " + c("ams.bash") + ". Se zsh viene installata dopo AMS, "
      "basta rilanciare " + c("install.sh") + " per aggiungere la riga allo zshrc; fish legge " + c("conf.d")
      + " anche se arriva dopo.") + \
    flow([("bash interattiva", "$- contiene i", "dark"), ("profile.d/ams.sh", "→ ams.bash, una volta", "blue"),
           ("PROMPT_COMMAND", "+ __ams_prompt", "blue"), ("casella vuota?", "compgen -G, nessun processo", "navy"),
           ("ams-user prompt", "solo se serve", "light")], "«FIG» — Dall'aggancio alla domanda, in bash") + ul([
    "L'aggancio agisce solo in shell interattiva, e una volta per shell (variabile " + c("__AMS_HOOK") + ", in fish "
    + c("__ams_hook") + ").",
    "Aggiunge " + c("__ams_prompt") + " a " + c("PROMPT_COMMAND") + ": come elemento se è un array (bash 5.1 e "
    "successive), in testa se è una stringa.",
    c("__ams_prompt") + " conserva " + c("$?") + " e controlla la casella con " + c("compgen -G") + ", senza lanciare "
    "processi: con la casella vuota il prompt non costa nulla.",
    "In una shell di login chiama subito " + c("ams-user prompt --login") + ", così il messaggio compare prima del primo "
    "prompt.",
    "zsh e fish controllano la casella allo stesso modo senza lanciare processi: zsh con il glob " + c("(N)")
    + ", fish con " + c("string match") + " sui nomi (i glob di fish non hanno " + c("[0-9]") + ").",
    "Su Debian le shell non di login non leggono " + c("/etc/profile.d") + ": l'aggancio è richiamato anche da "
    + c("/etc/bash.bashrc") + ".",
])

PROMPT = fig(
    box(20, 40, 170, 54, "pending", "inbox in ordine", "dark")
    + diamond(360, 67, 220, 76, "rimandato da poco?", "amber")
    + box(560, 40, 170, 54, "conta", "promemoria di una riga", "soft")
    + box(275, 170, 170, 54, "mostra e chiede", "ask: [s/N]", "blue")
    + box(560, 170, 170, 54, "esito", "ack · snooze · fermo", "green")
    + arrow(192, 67, 248, 67) + arrow(472, 67, 558, 67, "#d97706", False, "sì (non al login)", 515, 57)
    + arrow(360, 107, 360, 168, "#475569", False, "no", 376, 140)
    + arrow(447, 197, 558, 197)
    + text(820, 60, "alla fine, se ci sono", 11, "#475569") + text(820, 76, "messaggi rimandati:", 11, "#475569")
    + text(820, 92, "«Hai N messaggi", 11, "#92400e", "600") + text(820, 108, "da confermare»", 11, "#92400e", "600"),
    900, 246, "«FIG» — ams-user prompt, per ogni messaggio della casella", "Il giro di ams-user prompt")

S2 = p(c("ams-user prompt") + " prende i messaggi della casella in ordine di numero. Quelli scaduti passano subito in "
       + c("read/") + ".", lead=True) + PROMPT + table(["Esito di ask", "Cosa fa", "Stampa"], [
    ["0 · «s»", c("ack ID \"terminale pts/N\""), "[AMS] Confermato. (se la scrittura fallisce: «Non è stato possibile registrare la conferma…», e il messaggio resta)"],
    ["1 · altro, o solo Invio", c("snooze ID term") + ": tocca " + c("state/ID.term"), "[AMS] La domanda verrà riproposta tra N minuti."],
    ["2 · confermato altrove", "sposta in " + c("read/"), "[AMS] Messaggio già confermato altrove…"],
    ["3 · ritirato", "nulla", "[AMS] L'amministratore ha ritirato il messaggio."],
    ["4 · scaduto mentre la domanda era aperta", "sposta in " + c("read/"), "[AMS] Il messaggio è scaduto."],
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
       "è sparito, è stato ritirato; se è scaduto, la domanda si ferma.", lead=True) + ASK + \
    p("Il terminale resta in modo canonico: ciò che l'utente sta scrivendo resta nel buffer del terminale e non si "
      "perde fra un secondo e l'altro. Il rinvio vale " + c("AMS_REMIND_MINUTES") + " dalla data di modifica di "
      + c("state/ID.term") + "; con " + c("--login") + " non vale.")

CHAPTER = ("La ricezione nel terminale", [
    ("L'aggancio della shell", S1),
    ("ams-user prompt", S2),
    ("La domanda e l'attesa", S3),
])
