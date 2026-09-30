from build import arrow, box, c, code, diamond, fig, flow, note, p, path, seq, table, term, text, ul, warn


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">capitolo {n}{"." + str(s) if s else ""}</a>'


S1 = p(c("cmd_send") + " di " + c("src/ams.c") + " controlla tutto ciò che può controllare <b>prima</b> di "
       "scrivere nell'archivio: opzioni, testo, scadenza, destinatari. Un errore in questa fase termina con "
       + c("die") + " senza lasciare nulla.", lead=True) + table(["Opzione", "Valore", "Controllo"], [
    [c("--to DEST"), "destinatari separati da virgole", "obbligatoria («manca --to»); risolta dopo il testo ("
     + cap(6, 1) + ")"],
    [c("--title TITOLO"), "una riga", "ripulito come il testo; a capo e tabulazioni diventano spazi"],
    [c("--expires DURATA"), c("30m") + ", " + c("2h") + ", " + c("3d") + " o una data", "calcolata subito; deve "
     "essere nel futuro («la scadenza è già passata»)"],
    [c("--file FILE"), "il testo da un file", "letto al più per 64 MiB; conta solo se non c'è testo sulla riga di "
     "comando"],
    [c("--"), "—", "fine delle opzioni: ciò che segue è testo anche se inizia con " + c("-")],
], "«TAB» — Le opzioni di ams send") + ul([
    "Le opzioni finiscono al primo argomento che non è un'opzione: da lì in poi gli argomenti, uniti da uno "
    "spazio, sono il testo. Senza testo e senza " + c("--file") + " il testo si legge da stdin (al più 64 MiB).",
    "Un'opzione sconosciuta («opzione sconosciuta: --level») o senza valore («manca il valore di --to») termina "
    "subito. " + c("--level") + " apparteneva alla versione 0.1.0 ed è rifiutata (" + c("tests/engine.sh")
    + ", gruppo 3).",
    "Una durata è un numero seguito da " + c("m") + ", " + c("h") + " o " + c("d") + "; tutto il resto lo interpreta "
    + c("date -d … +%s") + " in un processo figlio (per esempio " + c("\"2026-10-04 12:00\"") + "). Le date a parole "
    "sono quelle che capisce " + c("date") + ", in inglese.",
    "Dal testo si tolgono gli a capo finali, poi lo si ripulisce (" + cap(8, 7) + "). Un testo fatto solo di spazi "
    "è «messaggio vuoto»; oltre 65536 byte, dopo la pulizia, è «messaggio troppo lungo»: la finestra del desktop "
    "riceve il testo come argomento di zenity, e Linux non accetta un argomento oltre 128 KiB.",
])

INVIO = fig(
    box(20, 40, 150, 56, "prepara_archivio", "var, users, sent", "dark", 12)
    + box(190, 40, 130, 56, "prossimo_id", "flock su .seq.lock", "dark", 12)
    + box(340, 40, 130, 56, "lock + segno", "lock, incomplete", "navy", 12)
    + box(490, 40, 180, 56, "msg, recipients", "scrivi_atomico, sync", "navy", 12)
    + box(690, 40, 190, 56, "per ogni destinatario", "in ordine alfabetico", "blue", 12)
    + diamond(785, 150, 170, 60, "revoked?", "amber")
    + box(560, 204, 170, 56, "consegna_copia", "come U, verificata", "blue", 12)
    + box(370, 204, 170, 56, "terminali", "testo, al più 3 s ciascuno", "blue", 12)
    + box(180, 204, 170, 56, "sveglia_agente", "SIGUSR1 o systemd-run", "blue", 12)
    + box(20, 204, 140, 56, "delivery", "utente data n", "green", 12)
    + box(20, 300, 250, 56, "evento INVIATO", "elenco dei destinatari, autore", "soft", 12)
    + diamond(420, 328, 180, 60, "copie mancanti?", "amber")
    + box(560, 300, 150, 56, "die, uscita 1", "incomplete resta", "grey", 12)
    + box(730, 300, 150, 56, "syncfs, sync", "via incomplete", "green", 12)
    + arrow(172, 68, 188, 68) + arrow(322, 68, 338, 68) + arrow(472, 68, 488, 68) + arrow(672, 68, 688, 68)
    + arrow(785, 98, 785, 118)
    + path([(700, 150), (645, 150), (645, 202)], "#0050C0", False, "no", 672, 142)
    + arrow(558, 232, 542, 232) + arrow(368, 232, 352, 232) + arrow(178, 232, 162, 232)
    + path([(870, 150), (890, 150), (890, 286), (282, 286), (282, 312), (274, 312)], "#b45309", True,
           "sì: si ferma", 840, 236)
    + arrow(145, 262, 145, 298) + arrow(272, 328, 328, 328)
    + arrow(512, 328, 558, 328, "#475569", False, "sì", 535, 318)
    + path([(420, 360), (420, 372), (805, 372), (805, 358)], "#16a34a", False, "no", 610, 366),
    900, 390, "«FIG» — La sequenza di ams send", "Un invio, passo per passo")

S2 = p("Dopo i controlli, l'invio è una sequenza fissa. L'ordine è scelto perché ogni interruzione lasci uno "
       "stato che il comando successivo sa riconoscere e riparare.", lead=True) + INVIO + table(["Passo", "Che cosa",
                                                                                               "Perché qui"], [
    ["1", c("prepara_archivio") + ": crea " + c("/var/lib/ams") + ", " + c("users/") + " (" + c("755") + ") e "
     + c("sent/") + " (" + c("700") + ") se mancano", "AMS funziona anche senza " + c("install.sh")
     + " (modalità di prova)"],
    ["2", c("prossimo_id") + ": il numero e la cartella " + c("sent/ID/"), "sotto flock: numeri unici ("
     + cap(5, 3) + ")"],
    ["3", c("sent/ID/lock") + " preso in modo esclusivo, poi il segno " + c("incomplete"), "da qui recupero, ritiro "
     "e cancellazione sanno che un invio è in corso"],
    ["4", c("msg") + " e " + c("recipients") + " con " + c("scrivi_atomico") + "; " + c("fsync") + " di "
     + c("incomplete") + ", di " + c("sent/ID/") + " e di " + c("sent/"), "messaggio, destinatari e segno su disco "
     "prima di ogni consegna"],
    ["5", "per ogni destinatario: se " + c("revoked") + " esiste ci si ferma; altrimenti copia, terminali, sveglia, "
     "riga in " + c("delivery") + ", evento " + c("CONSEGNATO"), "un ritiro ferma l'invio al destinatario successivo"],
    ["6", "evento " + c("INVIATO") + " con l'elenco dei destinatari e l'autore", "dopo le consegne: nel registro "
     "l'invio compare in fondo"],
    ["7a", "copie mancanti: «Messaggio N consegnato a X destinatari su Y.», poi " + c("die") + " con i nomi",
     c("incomplete") + " resta; il lock si libera all'uscita; il comando successivo riprova"],
    ["7b", "tutto consegnato: " + c("syncfs") + " di " + c("users/") + ", " + c("fsync") + " di " + c("sent/ID/")
     + ", via " + c("incomplete") + ", di nuovo " + c("fsync"), "quando il segno sparisce, copie e consegne sono "
     "su disco"],
], "«TAB» — I passi dell'invio") + term(
    "admin@server:~$ sudo ams send --to @sviluppo --title Manutenzione --expires 2d \"Sabato dalle 8 alle 12 il server sarà spento.\"\n"
    "Messaggio 12 inviato a 2 utenti.", "Un invio riuscito")

CONS = fig(
    box(20, 70, 170, 56, "prepara_casella", "root: users/U 700, lchown", "navy", 12)
    + box(230, 70, 150, 56, "come_utente", "20 s", "dark", 12)
    + diamond(480, 98, 150, 64, "già letto?", "amber")
    + box(580, 20, 150, 50, "esito 0", "nulla da scrivere", "green", 12)
    + box(580, 120, 150, 56, "inbox/ID.tmp", "O_EXCL, O_NOFOLLOW", "blue", 12)
    + box(750, 120, 130, 56, "rename, stat", "normale, non vuoto", "blue", 12)
    + box(750, 20, 130, 50, "delivery", "solo se esito 0", "green", 12)
    + arrow(192, 98, 228, 98) + arrow(382, 98, 403, 98)
    + path([(480, 66), (480, 45), (578, 45)], "#16a34a", False, "sì", 500, 38)
    + path([(557, 98), (570, 98), (570, 148), (578, 148)], "#0050C0", False, "no", 590, 106)
    + arrow(732, 148, 748, 148) + arrow(815, 118, 815, 72, "#16a34a") + arrow(732, 45, 748, 45, "#16a34a"),
    900, 196, "«FIG» — consegna_copia: la copia si scrive come l'utente e si verifica", "Consegna verificata")

S3 = p("«Consegnato» vuol dire che la copia <b>c'era</b> nella casella, verificata, al momento della consegna. "
       + c("consegna_copia") + " di " + c("src/archivio.c") + " scrive e controlla nello stesso processo figlio; "
       "solo se riesce, " + c("ams send") + " annota la riga in " + c("delivery") + ".", lead=True) + CONS + ul([
    "Root prepara solo " + c("users/U") + " (" + cap(7, 1) + "); sottocartelle e copia le scrive il figlio con "
    "l'identità di U.",
    "Se il messaggio è già in " + c("read/") + " o " + c("acks/") + " la copia non si riscrive: il recupero non "
    "ripropone a un utente un messaggio già letto o confermato (" + c("tests/engine.sh") + ", gruppo 2).",
    "La copia nasce come " + c("inbox/ID.tmp") + " e diventa " + c("inbox/ID") + " con una rinomina: "
    + c("ams-user") + ", che elenca solo i nomi fatti di cifre, non vede mai un file a metà.",
    "Un guasto per un destinatario (casella non scrivibile, collegamento a " + c("/etc") + ", tempo scaduto) non "
    "ferma gli altri: l'evento " + c("NON_CONSEGNATO") + " va nel registro e l'invio prosegue (scenario F1).",
])

S4 = p("Per ogni terminale di " + c("terminali_utente") + " (" + cap(6, 3) + "), " + c("ams send") + " scrive il "
       "testo formattato nella lingua di chi usa <b>quel</b> terminale. Scrivere nel terminale non vale come "
       "conferma: la domanda arriva al prompt successivo.", lead=True) + term(
    "\n── AMS · Messaggio dall'amministratore · Manutenzione · 30/09 16:55 ──\n"
    "Sabato dalle 8 alle 12 il server sarà spento.\n"
    "────────────────────────────────────────", "Il testo scritto nel terminale di un utente in italiano") + \
    table(["Passo", "Che cosa", "Perché"], [
        [c("lingua_terminale"), "cerca in " + c("/proc") + " il primo processo con quel terminale (di solito la "
         "shell) e ne legge l'ambiente; se root non può (un container senza " + c("CAP_SYS_PTRACE") + "), lo legge "
         "l'utente stesso in un figlio", "ognuno legge nella sua lingua (" + cap(16, 1) + "); senza processi, "
         "la lingua del sistema"],
        [c("testo_terminale"), "intestazione con titolo e data, testo, riga di chiusura; ogni " + c("\\n")
         + " diventa " + c("\\r\\n"), "il terminale può essere in modo grezzo, per esempio dentro un editor"],
        [c("scrivi_terminale"), "apre con " + c("O_WRONLY|O_NOCTTY|O_NONBLOCK") + "; " + c("fstat")
         + " del terminale <b>aperto</b>: dispositivo a caratteri e proprietario uguale al destinatario",
         "fra la ricerca e l'apertura " + c("/dev/pts/N") + " può passare a un altro utente"],
        ["scrittura", "a pezzi, con " + c("poll") + " di 100 ms fra un tentativo e l'altro, per al più 3 secondi",
         "un terminale bloccato (Ctrl+S, rete lenta) non ferma l'invio"],
        ["conteggio", "i terminali scritti per intero finiscono nella riga di " + c("delivery"), "«scritto su 2 "
         "terminali» in " + c("ams status")],
    ], "«TAB» — Scrivere nei terminali") + \
    note("in modalità di prova l'unico «terminale» è il file " + c("AMS_TEST_TTY") + ", e il controllo sul tipo di "
         "file è saltato; quello sul proprietario resta: " + c("tests/engine.sh") + " (gruppo 9) verifica che "
         + c("/dev/null") + ", di root, non venga scritto.")

WAKE = seq([("ams send", "root", "navy"), ("figlio come U", "5 s", "dark"), ("Agente di U", "ppoll", "blue"),
            ("systemd --user", "di U", "soft")], [
    ("nota", 0, "sessione_grafica(U)?"),
    (0, 1, "come_utente(op_sveglia)"),
    ("nota", 1, "PID da ams-agent.pronto"),
    ("nota", 1, "cmdline = …/ams-user agent?"),
    (1, 2, "kill(PID, SIGUSR1)"),
    ("nota", 2, "l'attesa si interrompe"),
    ("sep", "nessun agente pronto"),
    (0, 3, "systemd-run --user --machine=U@.host"),
    (3, 2, "avvia ams-user agent", True),
], "«FIG» — La sveglia dell'agente del desktop, o il suo avvio", "Sveglia o avvio")

S5 = p("Dopo la copia, " + c("sveglia_agente") + " fa comparire subito la finestra sul desktop, senza aspettare il "
       "controllo periodico dell'agente. Se l'utente non ha una sessione grafica (o in modalità di prova) non fa "
       "nulla.", lead=True) + WAKE + ul([
    "Il segnale va solo a un agente <b>pronto</b>: il PID scritto in " + c("/run/user/UID/ams-agent.pronto")
    + " (al più 64 byte, senza seguire collegamenti), che l'agente scrive dopo aver preparato la ricezione del "
    "segnale (" + cap(12, 2) + ").",
    "Il segnale parte da un figlio <b>con l'identità di U</b>, e solo se " + c("/proc/PID/cmdline") + " è "
    "<b>esattamente</b> " + c("LIBDIR/ams-user") + " seguito da " + c("agent") + ": non può raggiungere processi "
    "d'altri, né un processo di U che avesse ereditato un PID vecchio.",
    "Se non c'è un agente pronto, " + c("systemd-run --user --machine=U@.host --collect --quiet") + " ne avvia uno "
    "nel gestore utente di systemd, che conosce già l'ambiente grafico della sessione. Se un agente stava partendo, "
    "il nuovo trova il lock ed esce; quello che partiva legge comunque la casella al primo giro (scenario I8: "
    "finestra in circa mezzo secondo).",
]) + note("l'agente scrive " + c("ams-agent.pronto") + " in " + c("$XDG_RUNTIME_DIR") + ", mentre " + c("ams send")
          + " lo cerca in " + c("/run/user/UID") + ": coincidono nelle sessioni avviate da logind, che è il caso "
          "supportato.")

RECOVER = seq([("ams send", "root", "navy"), ("sent/ID", "", "dark"), ("Casella U1", "", "blue"),
               ("Casella U2", "", "blue"), ("ams (dopo)", "qualunque comando", "light")], [
    (0, 1, "lock, incomplete, msg"),
    (0, 2, "copia, verifica"),
    (0, 1, "delivery: U1"),
    ("sep", "interruzione: U2 non ha la copia"),
    (4, 1, "incomplete? lock libero?"),
    (4, 2, "ricontrolla la copia"),
    (4, 3, "scrive la copia"),
    (4, 1, "delivery: U2; via incomplete"),
], "«FIG» — Un invio interrotto viene completato dal comando successivo", "Il recupero", width=920)

S6 = p(c("recupera") + " gira all'inizio di quasi tutti i comandi (" + cap(4, 1) + ") e ripara ciò che un comando "
       "interrotto ha lasciato a metà: invii, ritiri, cancellazioni. È <b>idempotente</b>: ripeterlo non cambia "
       "nulla.", lead=True) + RECOVER + table(["Trova", "Condizione", "Fa"], [
    [c("sent/ID/incomplete"), "lock libero, ma " + c("msg") + " o " + c("recipients") + " mancano o non si leggono",
     "scrive " + c("failed") + " con la data, toglie " + c("incomplete") + ", evento " + c("ANNULLATO")
     + ", avviso «il messaggio N era stato interrotto prima di essere salvato ed è stato annullato»"],
    [c("sent/ID/incomplete"), "lock libero, messaggio ritirato o scaduto", "toglie il segno senza consegnare"],
    [c("sent/ID/incomplete"), "lock libero, messaggio valido", "per ogni destinatario " + c("consegna_copia")
     + ", <b>anche per quelli già annotati</b>; per i nuovi: riga in " + c("delivery") + " con 0 terminali, evento "
     + c("CONSEGNATO") + ", sveglia; se nessuno manca: " + c("syncfs") + ", " + c("fsync") + ", via "
     + c("incomplete") + "; evento " + c("RECUPERATO") + " con il numero dei nuovi"],
    [c("sent/ID/ritiro"), "lock libero", "toglie le copie rimaste (" + cap(9, 1) + ")"],
    [c("sent/.cancella-ID/"), "sempre", "completa la cancellazione (" + cap(9, 3) + ")"],
    ["qualunque segno", "lock occupato", "nulla: è un invio in corso, non un invio interrotto"],
], "«TAB» — Che cosa ripara il recupero") + ul([
    "Il lock distingue un invio <b>in corso</b> da uno <b>interrotto</b>: " + c("ams send") + " lo tiene per tutta "
    "la consegna e il kernel lo rilascia quando il processo muore, anche con " + c("SIGKILL") + ". Senza questa "
    "regola il recupero, lanciato durante un invio lungo, consegnava in parallelo e annotava doppioni (trovato "
    "dalla suite dal vero; scenari F3 e F5).",
    "Le copie già annotate si ricontrollano perché, dopo un'interruzione di corrente, una riga di " + c("delivery")
    + " potrebbe essere su disco e la copia no (" + c("tests/engine.sh") + ", gruppo 9).",
    "Nell'ultima esecuzione registrata della macchina di prova (scenario F3), un " + c("ams send") + " ucciso con "
    + c("SIGKILL") + " dopo 4 consegne su 68 è stato completato dal comando successivo in meno di un secondo.",
]) + warn("il recupero di un invio in cui qualche copia ancora non si scrive lascia " + c("incomplete")
          + " e avvisa: «messaggio N ancora non consegnato a K destinatari (vedi ams status N)». Ogni comando "
          "successivo riprova.")

S7 = p("Testo e titolo di un messaggio arrivano da un amministratore ma finiscono nei terminali degli utenti: "
       "non devono poter muovere il cursore, cambiare il titolo della finestra o scrivere negli appunti. "
       + c("pulisci") + " di " + c("src/testo.c") + " toglie, in tre passaggi, tutto ciò che un terminale potrebbe "
       "interpretare come comando.", lead=True) + table(["Passaggio", "Tolto", "Esempio", "Perché"], [
    ["1, per riga", "sequenze CSI: " + c("ESC [") + ", cifre, " + c(";") + " o " + c("?") + ", un carattere finale",
     c("ESC [ 31 m"), "colori, movimenti del cursore, cancellazioni"],
    ["1, per riga", "sequenze OSC: " + c("ESC ]") + " … " + c("BEL"), c("ESC ] 0 ; titolo BEL"),
     "titolo della finestra, collegamenti, appunti"],
    ["2", "caratteri di controllo C0, tranne tabulazione e a capo; " + c("DEL"), c("0x01") + ", " + c("\\r") + ", "
     + c("0x7F"), "campanello, ritorno a capo, escape rimasti isolati"],
    ["3", "caratteri C1 in UTF-8", c("C2 80") + " … " + c("C2 9F"), "alcuni terminali li interpretano come comandi"],
], "«TAB» — Che cosa toglie pulisci, nell'ordine") + ul([
    "Una sequenza OSC senza " + c("BEL") + " finale non si toglie come sequenza: il suo " + c("ESC") + " sparisce "
    "al passaggio 2 e il resto resta come testo innocuo (" + c("tests/prove-unita.c") + ").",
    "Il testo UTF-8 normale resta intatto, compresi gli spazi non separabili (" + c("C2 A0") + ").",
    c("pulisci") + " si applica a testo e titolo prima di salvarli, a ciò che " + c("ams") + " legge dalle caselle "
    "(" + cap(10, 2) + "), alle righe di " + c("ams log") + " e a ciò che la TUI mostra dei comandi eseguiti.",
    "Dà lo stesso risultato del prototipo in bash (" + c("sed") + " e " + c("tr") + "): confrontati su 2000 testi "
    "casuali pieni di sequenze e caratteri di controllo prima di togliere il prototipo. Lo scenario G2 verifica che "
    "nessun " + c("ESC") + " arrivi al terminale.",
])

CHAPTER = ("L'invio e il recupero", [
    ("Le opzioni e il testo", S1),
    ("La sequenza d'invio", S2),
    ("La consegna verificata", S3),
    ("Scrivere nei terminali", S4),
    ("Svegliare o avviare l'agente", S5),
    ("Il recupero", S6),
    ("La pulizia del testo", S7),
])
