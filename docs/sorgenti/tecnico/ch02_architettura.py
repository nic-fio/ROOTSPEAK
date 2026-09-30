from build import arrow, box, c, fig, note, p, path, seq, table, text, ul, zone


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">capitolo {n}{"." + str(s) if s else ""}</a>'


PRINCIPI = fig(
    box(20, 50, 205, 64, "Nessun demone", "consegna al momento dell'invio", "navy")
    + box(245, 50, 205, 64, "Sempre come root", "sudo prima di tutto", "navy")
    + box(470, 50, 205, 64, "Mai bloccare", "si può sempre rimandare", "navy")
    + box(695, 50, 185, 64, "Tre stati", "per ogni destinatario", "navy")
    + box(20, 140, 205, 64, "Root non si fida", "caselle come l'utente", "blue")
    + box(245, 140, 205, 64, "Dati, non codice", "ams.conf, messaggi, .mo", "blue")
    + box(470, 140, 205, 64, "Nessuno stato scritto", "si deduce dai file", "blue")
    + box(695, 140, 185, 64, "Una sola fonte", "per stati e testi", "blue"),
    900, 228, "«FIG» — Gli otto principi che guidano il codice", "Principi")

S1 = p("AMS è piccolo di proposito: due programmi, file in un'unica cartella, le librerie di systemd già "
       "presenti nel sistema. Il disegno privilegia la <b>verificabilità</b>: ogni stato si può ricostruire "
       "guardando i file, e ogni passo che può interrompersi lascia un segno che il comando successivo sa "
       "riparare.", lead=True) + PRINCIPI + table(["Principio", "Cosa comporta nel codice"], [
    ["<b>Nessun demone</b>", "La consegna la fa " + c("ams send") + " nel momento dell'invio; il resto lo fanno "
     "l'aggancio della shell e l'agente del desktop, che partono con le sessioni dell'utente. Il recupero degli "
     "invii interrotti gira all'inizio dei comandi successivi."],
    ["<b>" + c("ams") + " sempre come root</b>", "Il comando si rilancia con " + c("sudo") + " prima di guardare gli "
     "argomenti, compresi " + c("--help") + " e " + c("version") + " (" + cap(4, 1) + ")."],
    ["<b>Mai bloccare</b>", "Ogni messaggio chiede la conferma e insiste con i solleciti, ma l'utente può sempre "
     "rimandare. Le sessioni senza terminale non vengono toccate."],
    ["<b>Tre stati</b>", "Per ogni destinatario: inviato, consegnato, confermato. Scadenza e ritiro sono proprietà "
     "del messaggio; l'enumerazione " + c("stato_e") + " di " + c("src/ams.h") + " ha solo tre valori."],
    ["<b>Root non si fida delle caselle</b>", "Ogni accesso di root a " + c("users/U") + " avviene in un processo "
     "figlio con l'identità di U, con un tempo massimo (" + cap(7) + ")."],
    ["<b>Dati, non codice</b>", "Configurazione, messaggi, conferme e cataloghi sono file di dati letti con limiti "
     "di misura; nulla di ciò che viene da fuori viene eseguito."],
    ["<b>Nessuno stato scritto</b>", "Lo stato di un destinatario non è scritto da nessuna parte: si deduce da "
     + c("sent/ID/delivery") + " e dalla casella (" + cap(10, 1) + ")."],
    ["<b>Una sola fonte</b>", "La TUI usa le stesse funzioni di " + c("ams list") + " e " + c("ams status")
     + "; guida integrata e riferimento del manuale utente vengono dagli stessi testi."],
], "«TAB» — I principi e le loro conseguenze")

AMBITI = fig(
    zone(20, 44, 270, 250, "Fidato · root")
    + box(42, 80, 226, 56, "ams", "root:gruppo admin · 750", "navy")
    + box(42, 150, 226, 56, "sent/ · ams.conf", "scritti solo da root", "dark")
    + box(42, 220, 226, 56, "journal", "_UID messo dal sistema", "soft")
    + zone(315, 44, 270, 250, "Confine")
    + box(337, 80, 226, 56, "come_utente", "figlio con l'identità di U", "green")
    + box(337, 150, 226, 56, "pulisci", "testi e conferme ripuliti", "green")
    + box(337, 220, 226, 56, "limiti di misura e tempo", "200 byte, 20 secondi", "green", 12)
    + zone(610, 44, 270, 250, "Non fidato · utente U")
    + box(632, 80, 226, 56, "users/U/", "U può tutto nella sua casella", "amber")
    + box(632, 150, 226, 56, "ams-user", "gira come U", "amber")
    + box(632, 220, 226, 56, "terminali di U", "/dev/pts/N di U", "amber")
    + arrow(270, 108, 335, 108) + arrow(565, 108, 630, 108)
    + arrow(630, 178, 565, 178, "#d97706") + arrow(335, 178, 270, 178, "#d97706"),
    900, 312, "«FIG» — I tre ambiti di privilegio e il confine fra root e gli utenti", "Chi è fidato")

S2 = p("Un messaggio attraversa tre ambiti con privilegi diversi. La regola è semplice: <b>tutto ciò che passa fra "
       "root e un utente attraversa un confine controllato</b>, in entrambe le direzioni.", lead=True) + AMBITI + \
    table(["Ambito", "Chi", "Scrive", "Legge"], [
        ["amministratore", c("ams") + ", come root", c("sent/") + ", le caselle (solo come l'utente), i terminali "
         "degli utenti, il journal", "tutto l'archivio; le caselle solo come l'utente"],
        ["utente", c("ams-user") + ", come U", "la propria casella, il journal (con il proprio " + c("_UID") + ")",
         "la propria casella; mai " + c("sent/")],
    ], "«TAB» — Chi scrive e chi legge") + \
    note("la TUI non è un ambito a parte: è " + c("ams") + " stesso, e le sue azioni sono i comandi eseguiti in un "
         "processo figlio (" + cap(14, 1) + ").")

PROGRAMMI = fig(
    box(20, 60, 190, 60, "src/*.c", "11 moduli, 9 intestazioni", "dark")
    + box(290, 30, 250, 56, "build/ams", "ams, tui, guida, archivio + comuni", "navy")
    + box(290, 110, 250, 56, "build/ams-user", "ams-user + comuni", "blue")
    + box(620, 30, 260, 56, "$PREFIX/bin/ams", "root:sudo · 750", "navy")
    + box(620, 110, 260, 56, "$PREFIX/lib/ams/ams-user", "fuori dal PATH · 755", "blue", 12)
    + box(290, 190, 250, 56, "build/locale/*/ams.mo", "msgfmt --check da po/", "soft")
    + box(620, 190, 260, 56, "$PREFIX/share/locale/", "un .mo per lingua", "soft")
    + arrow(212, 72, 288, 58) + arrow(212, 90, 288, 138) + arrow(212, 108, 288, 218)
    + arrow(542, 58, 618, 58) + arrow(542, 138, 618, 138) + arrow(542, 218, 618, 218)
    + text(115, 144, "make", 11, "#475569", "600") + text(580, 100, "install.sh", 11, "#475569", "600"),
    900, 272, "«FIG» — Dai sorgenti ai programmi installati", "Due programmi")

S3 = p("Il Makefile produce due eseguibili e un catalogo per lingua. Le parti comuni ("
       + c("comune testo lingua evento utente sessioni") + ") entrano in entrambi; " + c("ams") + " aggiunge "
       + c("ams.o") + ", " + c("guida.o") + ", " + c("archivio.o") + " e " + c("tui.o") + ".", lead=True) + \
    PROGRAMMI + table(["Programma", "Dove", "Permessi", "Chi lo lancia"], [
        [c("ams"), c("/usr/local/bin/ams"), c("750") + ", " + c("root:") + " gruppo degli amministratori",
         "un amministratore; si rilancia con sudo"],
        [c("ams-user"), c("/usr/local/lib/ams/ams-user"), c("755"), "l'aggancio della shell ("
         + c("prompt") + ") e l'avvio automatico del desktop (" + c("agent") + "); mai l'utente a mano"],
    ], "«TAB» — I due programmi") + \
    p("Entrambi dipendono solo da glibc e da libsystemd (" + c("sd-login") + " per le sessioni, "
      + c("sd-journal") + " per il registro). All'esecuzione servono anche " + c("sudo") + ", " + c("zenity")
      + ", " + c("systemd-run") + " e " + c("date") + "; " + c("notify-send") + " se c'è.")

PERCORSO = seq([("ams send", "root", "navy"), ("sent/ID", "archivio", "dark"), ("Casella U", "users/U", "blue"),
                ("Terminali", "/dev/pts/N", "blue"), ("Agente di U", "desktop", "light")], [
    (0, 1, "incomplete, msg, recipients"),
    (0, 2, "copia come U, verifica"),
    (0, 1, "riga in delivery"),
    (0, 3, "testo, al più 3 s"),
    (0, 4, "SIGUSR1 (come U)"),
    ("sep", "l'utente risponde"),
    (4, 2, "legge inbox/ID"),
    (4, 2, "«Ho letto»: acks/ID"),
    ("nota", 2, "inbox/ID → read/ID"),
], "«FIG» — Il percorso di un messaggio, dall'invio alla conferma", "Il percorso di un messaggio", width=920)

S4 = p("Il percorso completo tocca tutti i sottosistemi. Qui in breve; ogni passo ha il suo capitolo.",
       lead=True) + PERCORSO + table(["Passo", "Chi", "Effetto", "Dove"], [
    ["1", c("ams send"), "risolve i destinatari, pulisce testo e titolo, prende un ID, scrive " + c("sent/ID/")
     + " con il segno " + c("incomplete"), cap(8, 2)],
    ["2", c("ams send") + " come U", "scrive " + c("users/U/inbox/ID") + " (prima " + c(".tmp") + ", poi rinomina), "
     "controlla che ci sia, poi annota la consegna in " + c("sent/ID/delivery"), cap(8, 3)],
    ["3", c("ams send"), "scrive il testo su ogni terminale di U, nella lingua di quel terminale", cap(8, 4)],
    ["4", c("ams send") + " come U", "sveglia l'agente del desktop con " + c("SIGUSR1") + ", o lo avvia con "
     + c("systemd-run --user"), cap(8, 5)],
    ["5", "aggancio o agente", "mostrano il messaggio e chiedono la conferma", cap(11) + ", " + cap(12)],
    ["6", c("ams-user"), "crea " + c("acks/ID") + " (vale la prima) e sposta il messaggio in " + c("read/"), cap(13)],
    ["7", c("ams status") + ", TUI", "deducono lo stato confrontando " + c("sent/ID") + " con le caselle", cap(10)],
], "«TAB» — I passi di un messaggio")

S5 = p("AMS non usa utmp, che non registra molti terminali moderni, ma <b>logind</b> e i dispositivi dei "
       "terminali. La domanda utile non è «come è collegato l'utente» ma «su quali canali posso raggiungerlo "
       "adesso».", lead=True) + table(["Sessione dell'utente", "Come la trova AMS", "Canale"], [
    ["console di testo (" + c("tty3") + ")", "sessione logind di tipo " + c("tty") + " con terminale " + c("tty3"),
     "terminale"],
    ["ssh con terminale", "pseudo-terminale " + c("/dev/pts/N") + " di proprietà dell'utente", "terminale"],
    ["terminale del desktop, tmux", "pseudo-terminale di proprietà dell'utente", "terminale"],
    ["desktop X11 o Wayland", "sessione logind di tipo " + c("x11") + " o " + c("wayland"), "agente del desktop"],
    ["ssh senza terminale, scp, cron", "nessun terminale", "nessuno: non vengono toccate"],
    ["utente non collegato", "—", "la casella, letta al prossimo accesso"],
], "«TAB» — Le sessioni e i canali di consegna") + ul([
    "La casella fa da coda: un messaggio che non raggiunge nessun canale all'invio compare al login successivo "
    "(domanda nel terminale) o al primo giro dell'agente (finestra).",
    "Scrivere il testo in un terminale non vale come conferma: la domanda arriva al prompt successivo.",
]) + note("un terminale in cui l'utente è entrato con " + c("su") + " resta di proprietà di chi l'ha aperto: "
          + c("ams send") + " non ci scrive. L'aggancio della shell lo raggiunge comunque al prompt successivo.")

CHAPTER = ("Architettura generale", [
    ("Principi architetturali", S1),
    ("I tre ambiti di privilegio", S2),
    ("I due programmi", S3),
    ("Il percorso di un messaggio", S4),
    ("Sessioni e canali", S5),
])
