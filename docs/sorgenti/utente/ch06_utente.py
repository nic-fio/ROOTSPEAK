from build import arrow, box, c, dialog, fig, key, notification, note, p, seq, table, term, text, ul, ui

S1 = p("Sul desktop un messaggio con conferma compare da solo, sopra le altre finestre, pochi istanti dopo l'invio. "
       "L'utente non deve fare nulla per riceverlo.", lead=True) + \
    dialog("AMS · Messaggio dall'amministratore", "Manutenzione · 03/10 18:30",
           "Sabato dalle 8 alle 12 il server sarà spento.",
           "«FIG» — La finestra di conferma (su GNOME; l'aspetto segue il tema del desktop)") + \
    table(["L'utente preme", "Cosa succede"], [
        [ui("Ho letto"), "Il messaggio è confermato e non ricompare più, in nessuna sessione."],
        [ui("Più tardi") + ", o chiude la finestra", "La finestra ricompare dopo 30 minuti, finché l'utente non conferma."],
    ], "«TAB» — I due pulsanti") + \
    note("se ci sono più messaggi, le finestre compaiono una dopo l'altra, dal più vecchio al più recente.")

S2 = p("In una finestra di terminale, locale o collegata con ssh, il testo compare nel momento dell'invio, anche "
       "mentre l'utente sta lavorando:", lead=True) + term(
    "mario@server:~$\n"
    "── AMS · Messaggio dall'amministratore · Manutenzione · 03/10 18:30 ──\n"
    "Sabato dalle 8 alle 12 il server sarà spento.\n"
    "────────────────────────────────────────", "Nel momento dell'invio") + \
    p("Appena l'utente torna al prompt (se ci è già, basta premere " + key("Invio") + "), AMS gli chiede la conferma:") + \
    term("── AMS · Messaggio dall'amministratore · Manutenzione · 03/10 18:30 ──\n"
         "Sabato dalle 8 alle 12 il server sarà spento.\n"
         "────────────────────────────────────────\n"
         "[AMS] Confermi di aver letto il messaggio? [s/N] s\n"
         "[AMS] Confermato.\n"
         "mario@server:~$", "Al prompt successivo") + \
    p("Con qualunque altra risposta il messaggio è rimandato. Fino alla domanda successiva, a ogni prompt compare "
      "solo un promemoria di una riga:") + \
    term("[AMS] Confermi di aver letto il messaggio? [s/N] n\n"
         "[AMS] La domanda verrà riproposta tra 30 minuti.\n"
         "mario@server:~$ ls\n"
         "documenti  progetti\n"
         "[AMS] Hai 1 messaggio dell'amministratore da confermare.\n"
         "mario@server:~$", "Se l'utente rimanda") + \
    note("se l'utente sta usando un programma a tutto schermo, come un editor, il testo dell'invio si sovrappone alla "
         "schermata, come succede con " + c("wall") + ". Non si perde nulla: la schermata torna a posto da sola o con "
         + key("Ctrl", "L") + ".")

OFFLINE = seq([("Amministratore", "ams send", "dark"), ("AMS", "casella di Mario", "navy"), ("Mario", "non collegato", "light")], [
    (0, 1, "messaggio per mario"),
    (1, 1, "Mario non è collegato: il messaggio aspetta"),
    ("sep", "più tardi, Mario accede"),
    (2, 1, "login (desktop, console o ssh)"),
    (1, 2, "finestra, oppure testo e domanda"),
    (2, 1, "«Ho letto»"),
    (0, 1, "ams status 1", True),
    (1, 0, "confermato il … (desktop)", True),
], "«FIG» — Un messaggio per chi non è collegato", "Consegna al prossimo accesso")

S3 = p("Chi non è collegato trova il messaggio al primo accesso successivo, in qualunque modo entri.", lead=True) + \
    OFFLINE + ul([
        "<b>Dal desktop</b>, la finestra compare appena si apre la sessione.",
        "<b>Da una console o con ssh</b>, testo e domanda compaiono subito dopo l'accesso, prima del primo prompt. "
        "Al momento dell'accesso la domanda viene fatta anche se l'utente aveva rimandato.",
    ])

ONE = seq([("Desktop di Mario", "finestra", "blue"), ("AMS", "", "navy"), ("Terminale di Mario", "ssh", "blue")], [
    (1, 0, "finestra «Ho letto»"),
    (1, 2, "testo e domanda «Confermi?»"),
    (0, 1, "Mario preme «Ho letto»"),
    (1, 1, "registra la prima conferma"),
    (1, 2, "la domanda si ferma: «già confermato altrove»", True),
], "«FIG» — La prima conferma chiude tutte le altre richieste", "Una conferma vale per tutte le sessioni")

S4 = p("Un utente con più sessioni aperte, per esempio il desktop e due connessioni ssh, riceve il messaggio in tutte. "
       "Basta confermare una volta.", lead=True) + ONE + \
    p("La finestra si chiude da sola se l'utente conferma da un terminale, e viceversa. In " + c("ams status")
      + " resta la prima conferma, con il canale da cui è arrivata.")

TIMELINE = fig(
    '<line x1="60" y1="150" x2="860" y2="150" stroke="#94a3b8" stroke-width="2"/>'
    + "".join(f'<line x1="{x}" y1="144" x2="{x}" y2="156" stroke="#94a3b8" stroke-width="2"/>'
              + text(x, 176, t, 11.5, "#475569", "600") for x, t in
              [(80, "18:30"), (260, "18:32"), (460, "19:02"), (660, "19:32"), (820, "19:35")])
    + box(20, 60, 120, 54, "Inviato", "ams send", "dark")
    + box(200, 60, 120, 54, "Più tardi", "rimandato", "amber")
    + box(400, 60, 120, 54, "Ricompare", "Più tardi", "amber")
    + box(600, 60, 120, 54, "Ricompare", "", "light")
    + box(760, 60, 120, 54, "Ho letto ✓", "confermato", "green")
    + arrow(80, 116, 80, 144, "#475569") + arrow(260, 116, 260, 144, "#475569") + arrow(460, 116, 460, 144, "#475569")
    + arrow(660, 116, 660, 144, "#475569") + arrow(820, 116, 820, 144, "#475569")
    + text(360, 212, "30 minuti", 11.5, "#92400e", "700") + text(560, 212, "30 minuti", 11.5, "#92400e", "700")
    + '<path d="M262 196 h196 M462 196 h196" stroke="#d97706" stroke-width="2" stroke-dasharray="4 3"/>',
    900, 232, "«FIG» — Un messaggio rimandato due volte e poi confermato", "I solleciti")

S5 = p("AMS non blocca mai il lavoro: l'utente può sempre rimandare. Ma chi rimanda viene sollecitato di nuovo, a "
       "intervalli regolari, finché non conferma.", lead=True) + TIMELINE + \
    p("L'intervallo predefinito è di 30 minuti, uguale per la finestra e per il terminale; si cambia nelle impostazioni "
      "(capitolo 8). Intanto l'amministratore vede in " + c("ams status") + " chi non ha ancora confermato.")

CHAPTER = ("Cosa vedono gli utenti", [
    ("Sul desktop", S1),
    ("Nel terminale", S2),
    ("Chi non è collegato", S3),
    ("Più sessioni, una conferma", S4),
    ("Rimandare e solleciti", S5),
])
