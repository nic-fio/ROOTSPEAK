from build import arrow, box, c, code, diamond, fig, flow, note, p, seq, table, term, text, ul


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">capitolo {n}{"." + str(s) if s else ""}</a>'


S1 = p("Ogni shell ha il suo aggancio, installato dove quella shell lo legge. Tutti fanno la stessa cosa: se la "
       "casella contiene messaggi, lanciano " + c("ams-user prompt") + ", subito al login e poi prima di ogni "
       "prompt.", lead=True) + table(["Shell", "File installato", "Letto da", "Quando chiede"], [
    ["bash", c("/usr/local/lib/ams/ams.bash"), c("/etc/profile.d/ams.sh") + " (shell di login) e "
     + c("/etc/bash.bashrc") + " (le altre)", "al login e a ogni prompt (" + c("PROMPT_COMMAND") + ")"],
    ["zsh", c("/usr/local/lib/ams/ams.zsh"), "una riga in " + c("/etc/zsh/zshrc") + " (o " + c("/etc/zshrc") + ")",
     "al login e a ogni prompt (" + c("precmd") + ")"],
    ["fish", c("/etc/fish/conf.d/ams.fish"), "fish stessa, all'avvio", "al login e a ogni prompt (evento "
     + c("fish_prompt") + ")"],
    ["sh, dash, ksh…", c("/etc/profile.d/ams.sh"), c("/etc/profile") + ", nelle shell di login", "solo al login"],
], "«TAB» — Gli agganci delle shell") + \
    p("Il testo del messaggio arriva nel terminale all'invio con qualunque shell: lo scrive root, non la shell "
      "(" + cap(8, 4) + "). dash, ksh e le shell simili non hanno un punto in cui agganciarsi prima del prompt: la "
      "domanda arriva al login successivo, o dalla finestra del desktop (scenari K della macchina di prova). "
      + c("profile.d/ams.sh") + " è scritto in sh semplice perché lo leggono tutte: rimanda bash ad "
      + c("ams.bash") + ", lascia zsh al suo aggancio e alle altre chiede al login.") + \
    note("zsh legge lo zshrc di sistema: se viene installata dopo AMS, basta rilanciare " + c("install.sh")
         + " per aggiungere la riga. fish legge " + c("conf.d") + " anche se arriva dopo.")

S2 = flow([("bash interattiva", "$- contiene i", "dark"), ("profile.d/ams.sh", "→ ams.bash, una volta", "blue"),
           ("PROMPT_COMMAND", "+ __ams_prompt", "blue"), ("casella vuota?", "compgen -G", "navy"),
           ("ams-user prompt", "solo se serve", "light")], "«FIG» — Dall'aggancio alla domanda, in bash") + \
    code("""__ams_prompt() {
	local s=$?
	# Controllo senza processi esterni: con la casella vuota non costa nulla.
	if compgen -G "$__AMS_INBOX/[0-9]*" >/dev/null; then
		@LIBDIR@/ams-user prompt
	fi
	return $s
}""", "bash", "etc/ams.bash (estratto)") + ul([
    "L'aggancio agisce solo in una shell interattiva, se " + c("ams-user") + " esiste, e una volta per shell "
    "(variabile " + c("__AMS_HOOK") + ", in fish " + c("__ams_hook") + ").",
    "Aggiunge " + c("__ams_prompt") + " a " + c("PROMPT_COMMAND") + ": come elemento se è un array (bash 5.1 e "
    "successive), in testa se è una stringa. Conserva " + c("$?") + ": il prompt dell'utente vede l'esito del suo "
    "ultimo comando.",
    "Il controllo della casella usa " + c("compgen -G") + ", un comando interno di bash che non lancia processi: "
    "con la casella vuota il prompt non costa nulla. zsh fa lo stesso con il glob " + c("(N)") + ", fish con "
    + c("string match") + " sui nomi (i glob di fish non hanno " + c("[0-9]") + ").",
    "In una shell di login chiama subito " + c("ams-user prompt --login") + ": il messaggio compare prima del "
    "primo prompt (scenario C1b: circa 0,3 s dal login).",
    "Su Debian le shell interattive non di login (i terminali del desktop) non leggono " + c("/etc/profile.d")
    + ": l'aggancio è richiamato anche da " + c("/etc/bash.bashrc") + " (" + cap(3, 3) + ").",
])

GIRO = fig(
    box(20, 40, 170, 56, "in_attesa", "inbox in ordine di numero", "dark")
    + diamond(360, 68, 240, 72, "rimandato da poco?", "amber")
    + box(570, 40, 160, 56, "promemoria", "contato, non chiesto", "soft")
    + box(270, 160, 180, 56, "mostra e chiede", "testo, poi [s/N]", "blue")
    + box(560, 160, 170, 56, "esito", "conferma · rinvio · …", "green")
    + arrow(192, 68, 238, 68) + arrow(482, 68, 568, 68, "#d97706", False, "sì, non al login", 525, 58)
    + arrow(360, 106, 360, 158, "#475569", False, "no", 376, 134)
    + arrow(452, 188, 558, 188)
    + text(815, 60, "alla fine, se ce ne sono:", 11, "#475569")
    + text(815, 78, "«Hai N messaggi", 11, "#92400e", "600")
    + text(815, 94, "dell'amministratore", 11, "#92400e", "600")
    + text(815, 110, "da confermare.»", 11, "#92400e", "600")
    + text(105, 130, "confermati e scaduti", 11, "#475569")
    + text(105, 146, "passano in read/", 11, "#475569"),
    900, 236, "«FIG» — ams-user prompt, per ogni messaggio della casella", "Il giro di ams-user prompt")

S3 = p(c("ams-user prompt") + " di " + c("src/ams-user.c") + " prende i messaggi della casella in ordine di "
       "numero. Se lo stdin non è un terminale non fa nulla; il canale della conferma è il nome del terminale ("
       + c("terminale pts/3") + ").", lead=True) + GIRO + ul([
    c("in_attesa") + " elenca " + c("inbox/") + " (solo nomi fatti di cifre e file normali). Un messaggio con "
    "la conferma già presente, per un'interruzione fra la conferma e lo spostamento, passa in " + c("read/")
    + " senza chiedere; uno scaduto passa in " + c("read/") + " senza conferma.",
    "Un messaggio rimandato da meno di " + c("AMS_REMIND_MINUTES") + " minuti (data di modifica di "
    + c("state/ID.term") + ") non si chiede: si conta, e alla fine compare il promemoria di una riga. Con "
    + c("--login") + " il rinvio non vale.",
]) + table(["Esito di chiedi", "Cosa fa", "Stampa"], [
    ["0 · «s», «S», «y» o «Y»", c("conferma(ID, \"terminale pts/N\")"), "[AMS] Confermato. (oppure scaduto, "
     "ritirato, o «Non è stato possibile registrare la conferma: la domanda verrà ripetuta.»)"],
    ["1 · altro, o solo Invio", c("rimanda(ID, \"term\")") + ": tocca " + c("state/ID.term") + ", evento "
     + c("RINVIATO"), "[AMS] La domanda verrà riproposta tra 30 minuti."],
    ["2 · confermato altrove", "sposta in " + c("read/"), "[AMS] Messaggio già confermato altrove (per esempio "
     "dal desktop)."],
    ["3 · ritirato", "nulla", "[AMS] L'amministratore ha ritirato il messaggio."],
    ["4 · scaduto mentre la domanda era aperta", "sposta in " + c("read/"), "[AMS] Il messaggio è scaduto."],
], "«TAB» — Gli esiti della domanda") + term(
    "mario@server:~$ \n"
    "── AMS · Messaggio dall'amministratore · Manutenzione · 30/09 16:55 ──\n"
    "Sabato dalle 8 alle 12 il server sarà spento.\n"
    "────────────────────────────────────────\n"
    "[AMS] Confermi di aver letto il messaggio? [s/N] s\n"
    "[AMS] Confermato.\n"
    "mario@server:~$ ", "La domanda al prompt") + \
    note(c("ams-user") + " gira dentro il prompt dell'utente: non termina mai con un errore che interrompa la "
         "shell, e ogni suo problema (casella illeggibile, terminale assente) si traduce nel non fare nulla.")

ASK = seq([("Utente", "tastiera", "dark"), ("chiedi", "poll 1 s su /dev/tty", "blue"),
           ("Casella", "users/U", "soft")], [
    (1, 0, "[AMS] Confermi di aver letto…? [s/N]"),
    ("nota", 1, "attende al più 1 secondo"),
    (1, 2, "acks/ID? inbox/ID? scaduto?"),
    ("nota", 1, "niente di nuovo: ricomincia"),
    ("sep", "intanto l'utente conferma dal desktop"),
    (1, 2, "acks/ID esiste"),
    (1, 0, "esito 2: «già confermato altrove»", True),
], "«FIG» — La domanda si accorge di ciò che succede altrove", "Una domanda che controlla ogni secondo")

S4 = p(c("chiedi") + " aspetta la risposta su " + c("/dev/tty") + " con " + c("poll") + ", un secondo alla volta, "
       "poi la legge con " + c("read") + ". A ogni secondo senza risposta controlla la casella: se è comparsa la "
       "conferma, l'utente ha confermato altrove; se il messaggio è sparito, è stato ritirato; se è scaduto, la "
       "domanda si ferma.", lead=True) + ASK + ul([
    "Il terminale resta in modo canonico: ciò che l'utente sta scrivendo resta nel buffer del terminale e non si "
    "perde fra un secondo e l'altro.",
    "La domanda si chiude entro circa un secondo: conferma da un'altra sessione (scenario C4b, 0,95 s), ritiro "
    "(scenario E3, 1,0 s), scadenza (" + c("tests/engine.sh") + ", gruppo 4).",
    "Senza " + c("/dev/tty") + " (nessun terminale di controllo) la risposta vale «no»: il messaggio resta e torna "
    "più tardi.",
    "La risposta si confronta solo con il primo carattere: " + c("s") + ", " + c("S") + ", " + c("y") + " e "
    + c("Y") + " valgono sì in ogni lingua.",
])

CHAPTER = ("La ricezione nel terminale", [
    ("Gli agganci delle shell", S1),
    ("Dall'aggancio alla domanda", S2),
    ("ams-user prompt", S3),
    ("La domanda e l'attesa", S4),
])
