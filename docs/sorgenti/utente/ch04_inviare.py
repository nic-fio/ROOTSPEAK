from build import arrow, box, c, code, diamond, fig, note, p, table, term, text, tip, warn

SETS = fig(
    '<rect x="20" y="44" width="860" height="236" rx="18" fill="#eef4ff" stroke="#0050C0" stroke-width="2"/>'
    + text(40, 70, "all — tutti gli utenti della macchina", 13, "#003a90", "700", "start")
    + text(40, 88, "esclusi root e gli account di sistema", 11, "#475569", "400", "start")
    + '<ellipse cx="340" cy="178" rx="210" ry="78" fill="#0050C0" fill-opacity="0.13" stroke="#0050C0" stroke-width="1.6"/>'
    + text(200, 166, "online", 13, "#003a90", "700")
    + text(200, 184, "chi è collegato adesso", 11, "#334155")
    + '<ellipse cx="560" cy="178" rx="200" ry="72" fill="#d97706" fill-opacity="0.14" stroke="#d97706" stroke-width="1.6"/>'
    + text(680, 166, "@sviluppo", 13, "#92400e", "700")
    + text(680, 184, "i membri di un gruppo", 11, "#334155")
    + text(450, 172, "collegati e", 11, "#334155") + text(450, 188, "del gruppo", 11, "#334155")
    + '<circle cx="808" cy="112" r="7" fill="#003a90"/>' + text(808, 134, "mario", 11.5, "#003a90", "700")
    + text(808, 150, "un utente", 10.5, "#475569"),
    900, 300, "«FIG» — I destinatari si possono combinare: " "--to mario,@sviluppo manda a Mario e a tutto il gruppo",
    "Chi riceve il messaggio")

S1 = p("L'opzione " + c("--to") + " dice chi riceve il messaggio. Si possono indicare più destinatari separati da "
       "virgole, senza spazi: chi compare più volte riceve il messaggio una volta sola.", lead=True) + \
    table(["Scrivi", "Chi riceve", "Esempio"], [
        ["un nome", "quell'utente", c("--to mario")],
        ["più nomi", "ognuno di loro", c("--to mario,anna,luca")],
        [c("@gruppo"), "i membri di un gruppo del sistema", c("--to @sviluppo")],
        [c("online"), "chi è collegato in questo momento, in qualunque modo", c("--to online")],
        [c("all"), "tutti gli utenti della macchina, collegati o no", c("--to all")],
    ], "«TAB» — Come indicare i destinatari") + SETS + \
    note("le opzioni vanno scritte <b>prima</b> del testo: tutto quello che viene dopo il testo è considerato parte "
         "del messaggio.")

LEVEL = fig(
    diamond(250, 150, 250, 104, "Devi sapere chi ha letto?", "navy")
    + box(560, 48, 320, 72, "ack — con conferma", "chiede «Ho letto» e insiste finché non arriva", "blue")
    + box(560, 180, 320, 72, "info — solo avviso", "compare una volta, senza domande", "dark")
    + arrow(375, 140, 556, 90, "#0050C0", False, "sì", 470, 104)
    + arrow(375, 160, 556, 212, "#475569", False, "no", 470, 204)
    + text(250, 238, "È il livello predefinito: ack", 11.5, "#334155", "600"),
    900, 272, "«FIG» — Come scegliere il livello del messaggio", "Quale livello")

S2 = p("Ogni messaggio ha un <b>livello</b>, scelto con " + c("--level") + ". Senza indicarlo si usa " + c("ack") + ".",
       lead=True) + LEVEL + table(["", c("ack") + " (predefinito)", c("info")], [
        ["Sul desktop", "finestra con «Ho letto» e «Più tardi»", "notifica che sparisce da sola"],
        ["Nel terminale", "il testo, poi la domanda «Confermi?»", "solo il testo"],
        ["Se l'utente rimanda", "glielo si ripropone dopo 30 minuti", "—"],
        ["In " + c("ams status"), "chi ha confermato, quando e da dove", "a chi è stato mostrato"],
        ["Adatto per", "manutenzioni, nuove regole, scadenze", "avvisi brevi: «il servizio riparte tra 5 minuti»"],
    ], "«TAB» — I due livelli a confronto") + term(
        'admin@server:~$ ams send --to online --level info "Il servizio web riparte tra 5 minuti."\n'
        "Messaggio 2 inviato a 3 utenti.")

S3 = p("Il testo si può scrivere in tre modi. Per messaggi lunghi conviene prepararlo in un file.", lead=True) + \
    table(["Modo", "Esempio"], [
        ["tra virgolette, alla fine del comando", c('ams send --to mario "Testo del messaggio"')],
        ["da un file, con " + c("--file"), c("ams send --to @sviluppo --file avviso.txt")],
        ["scritto al momento: si preme Invio e alla fine " + '<span class="key">Ctrl</span>+<span class="key">D</span>',
         c("ams send --to mario")],
    ], "«TAB» — Tre modi di dare il testo") + \
    p("Il testo può avere più righe. " + c("--title") + " aggiunge un titolo, che compare in testa al messaggio e nella "
      "finestra del desktop.") + \
    code("Da lunedì 15 ottobre le password scadono ogni 90 giorni.\n"
         "Al primo accesso dopo la scadenza il sistema chiederà di cambiarla.\n"
         "Per problemi: ufficio IT, interno 214.", "text", "avviso.txt") + \
    term('admin@server:~$ ams send --to all --title "Nuova regola per le password" --file avviso.txt\n'
         "Messaggio 3 inviato a 24 utenti.") + \
    tip("AMS toglie dal testo i caratteri invisibili e i codici di colore: si può incollare testo da qualunque parte "
        "senza rischiare di disturbare i terminali degli utenti.", "Testo sicuro.")

S4 = p("Con " + c("--expires") + " un messaggio smette di essere mostrato dopo un certo tempo. Serve per gli avvisi "
       "che perdono senso: chi non l'ha visto in tempo non lo vedrà più.", lead=True) + \
    table(["Scrivi", "Il messaggio scade"], [
        [c("--expires 30m"), "tra 30 minuti"],
        [c("--expires 2h"), "tra 2 ore"],
        [c("--expires 3d"), "tra 3 giorni"],
        [c('--expires "2026-10-04 12:00"'), "sabato 4 ottobre 2026 alle 12"],
    ], "«TAB» — Come indicare la scadenza") + \
    warn("le date scritte a parole vanno in inglese (" + c('"saturday 12:00"') + "); " + c('"sabato 12:00"')
         + " non viene capito. Il formato anno-mese-giorno funziona sempre.")

S5 = table(["Voglio…", "Comando"], [
    ["avvisare un utente e sapere se ha letto", c('ams send --to anna "Il tuo account scade venerdì."')],
    ["avvisare chi è collegato che sto per riavviare",
     c('ams send --to online --level info --expires 15m "Riavvio alle 13:00: salvate il lavoro."')],
    ["informare tutti di una nuova regola", c('ams send --to all --title "Password" --file regola.txt')],
    ["scrivere a un gruppo di lavoro", c('ams send --to @sviluppo --expires 2d "Consegna entro giovedì alle 18."')],
    ["scrivere a due persone e a un gruppo", c('ams send --to mario,anna,@stagisti "Riunione alle 11."')],
], "«TAB» — Comandi pronti per i casi più comuni")

CHAPTER = ("Mandare messaggi", [
    ("Scegliere i destinatari", S1),
    ("Scegliere il livello", S2),
    ("Titolo, testi lunghi e file", S3),
    ("Scadenza", S4),
    ("Comandi pronti", S5),
])
