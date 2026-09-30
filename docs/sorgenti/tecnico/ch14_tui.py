from build import arrow, box, c, fig, key, note, p, path, schermata, table, text, ul, warn, zone


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">capitolo {n}{"." + str(s) if s else ""}</a>'


ARCH = fig(
    zone(20, 44, 300, 250, "La TUI · src/tui.c")
    + box(40, 80, 260, 50, "lista", "carica_elenco → riassumi", "blue", 12)
    + box(40, 144, 260, 50, "dettaglio", "destinatari · storia", "blue", 12)
    + box(40, 208, 260, 50, "nuovo messaggio", "modulo, Ctrl+E, Ctrl+S", "blue", 12)
    + zone(360, 44, 240, 250, "Stesse funzioni di ams")
    + box(380, 80, 200, 50, "riassumi", "come ams list", "dark", 12)
    + box(380, 144, 200, 50, "destinatari", "come ams status", "dark", 12)
    + box(380, 208, 200, 50, "caselle_svuota", "a ogni aggiornamento", "soft", 12)
    + zone(640, 44, 240, 250, "In un processo figlio")
    + box(660, 80, 200, 40, "cmd_send", "", "navy", 12)
    + box(660, 128, 200, 40, "cmd_revoke · cmd_remind", "", "navy", 12)
    + box(660, 176, 200, 40, "cmd_purge", "", "navy", 12)
    + box(660, 224, 200, 40, "cmd_log · conta destinatari", "", "navy", 11)
    + arrow(302, 105, 378, 105) + arrow(302, 169, 378, 169)
    + path([(300, 150), (330, 150), (330, 30), (620, 30), (620, 100), (658, 100)], "#0050C0", True, "azioni", 475, 24)
    + text(460, 312, "uscita e errori raccolti su una pipe e mostrati in una finestra", 11.5, "#475569", "600"),
    900, 330, "«FIG» — La TUI legge con le funzioni dei comandi ed esegue i comandi stessi", "Nessun modo suo")

S1 = p(c("ams") + " senza argomenti, con stdin e stdout in un terminale di almeno 80 × 20, apre la TUI di "
       + c("src/tui.c") + " dopo il recupero; in una pipe, o in un terminale più piccolo, mostra la guida. La TUI "
       "<b>non ha un modo suo di fare le cose</b> e <b>non ha stati suoi</b>: legge l'archivio con le funzioni di "
       + c("ams list") + " e " + c("ams status") + ", e ogni azione è il comando stesso.", lead=True) + ARCH + ul([
    "<b>Stesse funzioni per leggere</b>: la lista usa " + c("riassumi") + " (i destinatari contati nei tre stati, "
    "ritirato e scaduto), il dettaglio " + c("destinatari") + " (la stessa riga di " + c("ams status") + ").",
    "<b>Le azioni sono i comandi</b>: invio, ritiro, sollecito e pulizia girano in un processo figlio che chiama "
    + c("cmd_send") + ", " + c("cmd_revoke") + ", " + c("cmd_remind") + ", " + c("cmd_purge") + " con stdout e "
    "stderr raccolti su una pipe e mostrati in una finestra. Un errore del comando (" + c("die") + ") chiude solo il "
    "figlio; l'uscita del figlio dà l'esito. Anche l'anteprima dei destinatari e la storia (" + c("cmd_log")
    + ") vengono da un figlio.",
    "La decisione dell'utente che ha voluto la TUI è anche un vincolo di progetto: discutendo le anteprime erano "
    "comparsi stati inventati («in attesa», «completo», «invio incompleto», «annullato»), tolti; "
    + c("tests/tui.py") + " controlla che nessuna di queste parole compaia sullo schermo.",
])

S2 = p("La lista mostra i messaggi dal più recente, uno per riga, con il riassunto dei destinatari: barra a tre "
       "colori e frase. Si aggiorna da sola ogni 3 secondi.", lead=True) + \
    schermata("lista", "«FIG» — La lista dei messaggi (schermata vera, catturata da tools/schermate-tui.sh)") + \
    table(["Colonna", "Contenuto"], [
        ["ID, DATA", "numero e data d'invio; " + c(">") + " segna la riga scelta, disegnata in negativo"],
        ["MESSAGGIO", c("[ritirato]") + " e " + c("[scaduto]") + " in grigio, il titolo in grassetto, la prima riga "
         "del testo, tagliata alla larghezza disponibile"],
        ["DESTINATARI", "la barra di 12 segni e la frase del riassunto (" + cap(10, 3) + "); sotto 106 colonne "
         "interne, al posto della frase, «confermati/totale» (per esempio " + c("4/8") + ")"],
        ["legenda", "sempre in fondo: " + c("█") + " confermato, " + c("▒") + " consegnato, " + c("░") + " inviato; "
         "con una ricerca attiva, il testo cercato"],
    ], "«TAB» — Le colonne della lista") + table(["Tasto", "Effetto"], [
    [key("↑") + " " + key("↓") + " " + key("PgUp") + " " + key("PgDn") + " " + key("Home") + " " + key("End"),
     "scorre la lista"],
    [key("Invio"), "apre il dettaglio del messaggio scelto"],
    [key("n"), "scrive e invia un messaggio nuovo"],
    [key("r"), "ritira il messaggio scelto, se non è già ritirato (con conferma)"],
    [key("s"), "sollecita chi non ha confermato: solo se il messaggio non è ritirato né scaduto e ha almeno un "
     "destinatario consegnato (con conferma)"],
    [key("p"), "cancella i messaggi più vecchi di una durata (con conferma; proposta " + c("90d") + ")"],
    [key("/"), "cerca per testo o titolo, senza distinguere maiuscole e minuscole; " + key("Esc") + " toglie la "
     "ricerca"],
    [key("?"), "la guida dei tasti"],
    [key("q"), "esce e ridà il terminale com'era"],
], "«TAB» — I tasti della lista")

S3 = p("Il dettaglio di un messaggio ha due schede: i destinatari, con la riga di stato di " + c("ams status")
       + " colorata secondo lo stato, e la storia, cioè l'uscita di " + c("ams log") + ". Si rilegge ogni 3 "
       "secondi e dopo ogni azione; si esce con " + key("Esc") + ".", lead=True) + \
    schermata("dettaglio", "«FIG» — Il dettaglio: un destinatario per riga, nei tre stati (schermata vera)") + \
    schermata("storia", "«FIG» — La scheda Storia: gli eventi del registro, riscritti nella lingua di chi legge "
                        "(schermata vera)") + ul([
    "L'intestazione riporta titolo, data, mittente, scadenza («scade il …» o «scaduto il …») e ritiro («ritirato "
    "il …», in rosso); poi al più sei righe del testo, rientrate.",
    "La riga delle schede ripete barra e frase: il riassunto resta visibile mentre si scorre l'elenco.",
    "Colori della colonna STATO: verde confermato, giallo consegnato, rosso inviato. Sono i tre stati, e solo "
    "quelli.",
    "Tasti: " + key("Tab") + " cambia scheda, " + key("↑") + " " + key("↓") + " scorrono, " + key("s") + " e "
    + key("r") + " sollecitano e ritirano con le stesse regole della lista.",
])

S4 = p("Il modulo del nuovo messaggio ha quattro campi: destinatari, titolo, scadenza e testo. Quando si lascia il "
       "campo dei destinatari, un figlio esegue la stessa risoluzione di " + c("ams send") + " e ne mostra il "
       "numero, o l'errore in rosso.", lead=True) + \
    schermata("nuovo", "«FIG» — Il modulo del nuovo messaggio, con l'anteprima dei destinatari (schermata vera)") + \
    schermata("invio", "«FIG» — La conferma prima dell'invio (schermata vera)") + table(["Tasto", "Effetto"], [
    [key("Tab") + ", " + key("Maiusc", "Tab"), "campo successivo o precedente"],
    [key("Ctrl", "E"), "apre il testo nell'editor dell'amministratore"],
    [key("Ctrl", "S"), "chiede conferma e invia: " + c("cmd_send") + " in un figlio, con il testo su stdin"],
    [key("Esc"), "lascia perdere il messaggio, con conferma se qualcosa è stato scritto"],
], "«TAB» — I tasti del modulo") + ul([
    "I campi di una riga accettano al più 1000 byte; il testo mostra il conteggio «85 di 65536 byte». I controlli "
    "veri sono quelli di " + c("ams send") + ": un errore arriva nella finestra d'esito, «Messaggio non inviato».",
    "<b>Editor</b>: " + key("Ctrl", "E") + " scrive il testo in un file temporaneo di " + c("/tmp") + " ("
    + c("mkstemp") + "), lo cede all'amministratore di " + c("SUDO_USER") + " e apre " + c("VISUAL") + ", "
    + c("EDITOR") + ", " + c("nano") + " o " + c("vi") + " <b>con la sua identità</b>, non come root; poi rilegge il "
    "file (al più il doppio della lunghezza massima, senza seguire collegamenti) e lo cancella.",
    "Dopo l'invio la lista si ricarica e il nuovo messaggio compare in cima (" + c("tests/tui.py") + ").",
]) + note("un difetto trovato scrivendo " + c("tests/tui.py") + ": il figlio che esegue l'invio ereditava anche "
          "il capo della pipe da cui il padre scrive il testo, e non vedeva mai la fine del testo. Ora lo chiude "
          "prima di chiamare " + c("cmd_send") + ".")

S5 = p("Ritiro, sollecito e pulizia chiedono sempre una conferma che descrive l'azione con i numeri veri; l'esito "
       "del comando compare poi in una finestra.", lead=True) + \
    schermata("sollecito", "«FIG» — La conferma di un sollecito, sopra la lista (schermata vera)") + table(
    ["Azione", "La conferma dice", "Poi"], [
        ["ritiro", "«Ritirare il messaggio N?», titolo e riassunto; «Chi non l'ha ancora visto non lo vedrà più; "
         "finestre e domande aperte si chiudono da sole.»", c("cmd_revoke") + " in un figlio"],
        ["sollecito", "quanti destinatari non hanno ancora confermato; «La domanda torna subito: al prompt "
         "successivo e con la finestra sul desktop.»", c("cmd_remind") + " in un figlio"],
        ["pulizia", "prima la durata («Cancellare i messaggi inviati da più di…»), poi «I messaggi più vecchi di "
         "D, con copie e conferme. Gli eventi restano nel registro di sistema.»", c("cmd_purge") + " in un figlio"],
        ["invio", "destinatari con il loro numero, titolo, scadenza, byte del testo", c("cmd_send") + " in un figlio"],
    ], "«TAB» — Le azioni con conferma") + \
    p("Finestre e conferme si disegnano su una copia dello schermo di base: una finestra successiva non resta "
      "sopra quella di prima. " + key("s") + " conferma, " + key("n") + " o " + key("Esc") + " annulla.")

S6 = table(["Parte", "Come funziona"], [
    ["terminale", c("/dev/tty") + " senza eco né modo canonico; senza " + c("IXON") + " (così " + key("Ctrl", "S")
     + " arriva alla TUI) e senza " + c("ICRNL") + "; schermo alternativo e cursore nascosto. All'uscita, e su "
     + c("SIGINT") + ", " + c("SIGTERM") + ", " + c("SIGHUP") + ", tutto torna com'era"],
    ["disegno", "senza ncurses: ogni schermata è composta in memoria e scritta con una sola scrittura; le lunghezze "
     "si contano in caratteri visibili (UTF-8, senza le sequenze di colore)"],
    ["tasti", "un byte alla volta con " + c("poll") + " di 500 ms; dopo " + c("ESC") + " il resto della sequenza "
     "con un'attesa di 40 ms: " + key("Esc") + " da solo, frecce, " + key("PgUp") + ", " + key("PgDn") + ", "
     + key("Home") + ", " + key("End") + ", " + key("Canc") + " e " + key("Maiusc", "Tab") + " sono riconosciuti"],
    ["aggiornamento", "ogni 6 attese a vuoto (3 secondi) la lista o il dettaglio si rileggono, dimenticando le "
     "caselle lette (" + c("caselle_svuota") + "); in alto a destra «aggiornato alle …»"],
    ["dimensioni", "a ogni attesa si confronta la dimensione (" + c("TIOCGWINSZ") + ") e si ridisegna; sotto "
     "80 × 20 la TUI esce"],
    ["colori", "disattivati con " + c("NO_COLOR") + " (se sudo la conserva)"],
], "«TAB» — Terminale, tasti e aggiornamento") + \
    warn("la TUI gira come root. Tutto ciò che mostra e che viene dagli utenti (conferme, storia) passa da "
         + c("pulisci") + " come nei comandi; l'unico programma esterno che la TUI lancia di suo, l'editor, gira con l'identità "
         "dell'amministratore.")

CHAPTER = ("La TUI per gli amministratori", [
    ("Architettura: stessi dati, stessi comandi", S1),
    ("La lista", S2),
    ("Il dettaglio e la storia", S3),
    ("Scrivere e inviare", S4),
    ("Le azioni con conferma", S5),
    ("Terminale, tasti e aggiornamento", S6),
])
