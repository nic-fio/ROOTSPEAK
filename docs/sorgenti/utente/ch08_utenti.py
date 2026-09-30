import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import (arrow, box, c, dialog, fig, key, note, notification, p, seq, table, term, text, tip, ui,  # noqa: E402
                   ul, warn)
from _aiuti import CONFERMATO, CONSEGNATO, rif  # noqa: E402

S1 = p("Sul desktop il messaggio compare da solo, sopra le altre finestre, pochi istanti dopo l'invio. L'utente non "
       "deve fare nulla per riceverlo: all'accesso grafico parte un piccolo programma di AMS, l'<b>agente del "
       "desktop</b>, che resta in attesa dei messaggi.", lead=True) + \
    dialog("AMS · Messaggio dall'amministratore", "Manutenzione · 30/09 16:55",
           "Sabato dalle 8 alle 12 il server sarà spento per la manutenzione dei dischi.",
           "«FIG» — La finestra di conferma (su GNOME; l'aspetto segue il tema del desktop)") + \
    table(["L'utente…", "Cosa succede"], [
        ["preme " + ui("Ho letto"), "Il messaggio è " + CONFERMATO + " e non ricompare più, in nessuna sessione."],
        ["preme " + ui("Più tardi") + " o chiude la finestra", "Il messaggio è rimandato: la finestra ricompare dopo "
         "30 minuti, finché l'utente non conferma."],
        ["non fa nulla", "La finestra resta lì, senza bloccare niente: si può lavorare nelle altre finestre."],
        ["esce dalla sessione", "La finestra si chiude; il messaggio ricompare al prossimo accesso."],
    ], "«TAB» — Che cosa può fare l'utente con la finestra") + \
    ul([
        "In testa alla finestra ci sono il titolo del messaggio e la data dell'invio; se il messaggio non ha titolo, "
        "solo la data.",
        "Se ci sono più messaggi, le finestre compaiono una alla volta, dal più vecchio al più recente.",
        "La finestra si chiude da sola se l'utente conferma da un terminale, se l'amministratore ritira il messaggio "
        "o se il messaggio scade.",
    ]) + \
    notification("AMS · Conferma non registrata",
                 "Non è stato possibile registrare la conferma: il messaggio verrà riproposto.",
                 "«FIG» — L'avviso, raro, di una conferma che non si è potuta salvare") + \
    note("se la conferma non si può salvare (per esempio perché il disco è pieno), il desktop mostra l'avviso qui sopra "
         "e il messaggio viene riproposto: la conferma non si perde in silenzio. L'avviso richiede " + c("notify-send")
         + ".", "Conferma non registrata.")

S2 = p("In ogni finestra di terminale dell'utente, locale, dentro il desktop, in tmux o collegata con ssh, il testo "
       "compare nel momento dell'invio, anche mentre l'utente sta lavorando:", lead=True) + term(
    "mario@server:~/progetti$ make\n"
    "gcc -O2 -c main.c\n"
    "\n"
    "── AMS · Messaggio dall'amministratore · Manutenzione · 30/09 16:55 ──\n"
    "Sabato dalle 8 alle 12 il server sarà spento.\n"
    "────────────────────────────────────────\n"
    "gcc -O2 -o prova main.o", "Nel momento dell'invio") + \
    p("Appena l'utente torna al prompt (se è già al prompt, basta premere " + key("Invio") + "), AMS mostra di nuovo il "
      "messaggio e chiede la conferma:") + \
    term("── AMS · Messaggio dall'amministratore · Manutenzione · 30/09 16:55 ──\n"
         "Sabato dalle 8 alle 12 il server sarà spento.\n"
         "────────────────────────────────────────\n"
         "[AMS] Confermi di aver letto il messaggio? [s/N] s\n"
         "[AMS] Confermato.\n"
         "mario@server:~/progetti$", "Al prompt successivo") + \
    table(["L'utente risponde", "Cosa succede"], [
        [key("s") + " (o " + key("y") + ") e " + key("Invio"), "«[AMS] Confermato.»: il messaggio è confermato ovunque."],
        ["qualunque altra cosa, anche solo " + key("Invio"), "«[AMS] La domanda verrà riproposta tra 30 minuti.»"],
        ["nulla, perché ha confermato sul desktop", "«[AMS] Messaggio già confermato altrove (per esempio dal "
         "desktop).»: la domanda si chiude da sola"],
        ["nulla, e il messaggio viene ritirato", "«[AMS] L'amministratore ha ritirato il messaggio.»"],
        ["nulla, e il messaggio scade", "«[AMS] Il messaggio è scaduto.»"],
    ], "«TAB» — Le risposte alla domanda") + \
    p("Dopo un rinvio, fino alla domanda successiva, a ogni prompt compare solo un promemoria di una riga:") + \
    term("[AMS] Confermi di aver letto il messaggio? [s/N] n\n"
         "[AMS] La domanda verrà riproposta tra 30 minuti.\n"
         "mario@server:~/progetti$ ls\n"
         "main.c  main.o  prova\n"
         "[AMS] Hai 1 messaggio dell'amministratore da confermare.\n"
         "mario@server:~/progetti$", "Se l'utente rimanda") + \
    note("se l'utente sta usando un programma a tutto schermo, come un editor, il testo dell'invio si sovrappone alla "
         "schermata, come succede con " + c("wall") + ". Non si perde nulla: la schermata torna a posto da sola o con "
         + key("Ctrl", "L") + ", e la domanda arriva solo all'uscita dal programma.", "Programmi a tutto schermo.")

S3 = p("La domanda di conferma nel terminale dipende dalla shell dell'utente. Il testo all'invio arriva invece "
       "sempre, qualunque sia la shell.", lead=True) + \
    table(["Shell", "Testo all'invio", "Domanda di conferma"], [
        ["bash", "sì", "a ogni prompt; al login anche se era stata rimandata"],
        ["zsh", "sì", "a ogni prompt; al login anche se era stata rimandata"],
        ["fish", "sì", "a ogni prompt; al login anche se era stata rimandata"],
        ["sh, dash, ksh e le altre che leggono " + c("/etc/profile"), "sì", "solo al login"],
        ["tcsh, csh e le shell che non leggono " + c("/etc/profile"), "sì", "no (resta la finestra, se ha un desktop)"],
    ], "«TAB» — Le shell e la domanda di conferma") + \
    ul([
        "La domanda compare solo nelle shell <b>interattive</b>: script, cron, " + c("scp") + ", " + c("rsync")
        + " e i comandi lanciati con " + c("ssh server comando") + " non la vedono mai.",
        "Le finestre di terminale già aperte al momento dell'installazione ricevono il testo, ma la domanda solo "
        "dalla prossima finestra o dal prossimo accesso.",
        "Se zsh viene installata dopo AMS, per la domanda in zsh basta rilanciare " + c("./install.sh") + "; fish "
        "invece la riceve anche se installata dopo.",
    ]) + warn("con " + c("su - mario") + " la finestra di terminale resta di chi l'ha aperta: il testo all'invio non "
              "compare, la domanda al prompt sì. Con " + c("ssh mario@server") + " tutto funziona normalmente.",
              "Accessi con su.")

FUORI = seq([("Amministratore", "invia", "dark"), ("AMS", "casella di Luca", "navy"), ("Luca", "non collegato", "light")], [
    (0, 1, "messaggio per luca"),
    (1, 1, "Luca non è collegato: il messaggio aspetta"),
    ("sep", "il giorno dopo, Luca accede"),
    (2, 1, "accesso (desktop, console o ssh)"),
    (1, 2, "finestra, oppure testo e domanda"),
    (2, 1, "«Ho letto» o «s»"),
    (1, 0, "nella lista: tutti confermato", True),
], "«FIG» — Un messaggio per chi non è collegato", "Consegna al prossimo accesso")

S4 = p("Chi non è collegato trova il messaggio al primo accesso successivo, in qualunque modo entri. Nel frattempo "
       "è già " + CONSEGNATO + ": la copia è nella sua casella e lo aspetta.", lead=True) + FUORI + \
    table(["Accesso", "Cosa vede"], [
        ["desktop", "la finestra, appena si apre la sessione"],
        ["console o ssh", "testo e domanda subito dopo l'accesso, prima del primo prompt; al login la domanda viene "
         "fatta anche se l'utente aveva rimandato"],
        ["un comando via ssh, " + c("scp") + ", un servizio", "nulla: non è un accesso interattivo"],
    ], "«TAB» — Il messaggio al prossimo accesso")

UNA = seq([("Desktop di Anna", "finestra", "blue"), ("AMS", "", "navy"), ("Terminale di Anna", "ssh", "blue")], [
    (1, 0, "finestra «Ho letto» / «Più tardi»"),
    (1, 2, "testo e domanda «Confermi?»"),
    (0, 1, "Anna preme «Ho letto»"),
    (1, 1, "registra la prima conferma"),
    (1, 2, "«Messaggio già confermato altrove»", True),
], "«FIG» — La prima conferma chiude tutte le altre richieste", "Una conferma vale per tutte le sessioni")

S5 = p("Un utente con più sessioni aperte, per esempio il desktop e due connessioni ssh, riceve il messaggio in tutte. "
       "Basta confermare una volta.", lead=True) + UNA + \
    p("La finestra si chiude da sola se l'utente conferma da un terminale, e la domanda nel terminale si chiude se "
      "conferma dal desktop. Nello stato del messaggio resta la prima conferma, con il canale da cui è arrivata: "
      + c("desktop") + " oppure " + c("terminale pts/2") + ".") + \
    note("il rinvio invece vale per il canale in cui viene dato: chi preme «Più tardi» sul desktop vede comunque la "
         "domanda nel terminale, e viceversa.", "Rinvii separati.")

TEMPI = fig(
    '<line x1="60" y1="150" x2="860" y2="150" stroke="#94a3b8" stroke-width="2"/>'
    + "".join(f'<line x1="{x}" y1="144" x2="{x}" y2="156" stroke="#94a3b8" stroke-width="2"/>'
              + text(x, 176, t, 11.5, "#475569", "600") for x, t in
              [(80, "16:55"), (260, "16:57"), (460, "17:27"), (640, "17:30"), (820, "17:31")])
    + box(20, 60, 120, 54, "Invio", "ams send", "dark")
    + box(200, 60, 120, 54, "Più tardi", "rimandato", "amber")
    + box(400, 60, 120, 54, "Ricompare", "rimanda ancora", "amber")
    + box(580, 60, 120, 54, "Sollecito", "ams remind", "blue")
    + box(760, 60, 120, 54, "Ho letto ✓", "confermato", "green")
    + arrow(80, 116, 80, 144, "#475569") + arrow(260, 116, 260, 144, "#475569") + arrow(460, 116, 460, 144, "#475569")
    + arrow(640, 116, 640, 144, "#475569") + arrow(820, 116, 820, 144, "#475569")
    + text(360, 212, "30 minuti", 11.5, "#92400e", "700")
    + '<path d="M262 196 h196" stroke="#d97706" stroke-width="2" stroke-dasharray="4 3"/>'
    + text(550, 230, "il sollecito non aspetta: la finestra torna subito", 11.5, "#1e40af", "600"),
    900, 250, "«FIG» — Un messaggio rimandato, riproposto, sollecitato e infine confermato", "Rinvii e solleciti")

S6 = p("AMS non blocca mai il lavoro: l'utente può sempre rimandare. Ma chi rimanda viene richiesto di nuovo, a "
       "intervalli regolari, finché non conferma.", lead=True) + TEMPI + \
    table(["Quando", "Nel terminale", "Sul desktop"], [
        ["dopo un rinvio", "promemoria di una riga a ogni prompt", "niente finestra"],
        ["passati 30 minuti", "testo e domanda al prompt successivo", "la finestra ricompare (entro un minuto)"],
        ["al login", "testo e domanda subito, anche se aveva rimandato", "la finestra all'apertura della sessione"],
        ["dopo un sollecito", "testo e domanda al prompt successivo", "la finestra subito"],
        ["alla scadenza o al ritiro", "più nulla", "più nulla"],
    ], "«TAB» — Quando il messaggio torna") + \
    p("L'intervallo di 30 minuti è uguale per la finestra e per il terminale e si cambia nelle impostazioni ("
      + rif(10) + "). Intanto l'amministratore vede nel dettaglio del messaggio chi ha rimandato e quando.")

S7 = p("Ognuno vede AMS nella sua lingua: finestra, pulsanti, intestazione, domanda e avvisi seguono la lingua della "
       "sessione dell'utente. Il <b>testo del messaggio</b> arriva com'è stato scritto: non si traduce.", lead=True) + \
    term("── AMS · Message from the administrator · Manutenzione · 30/09 16:55 ──\n"
         "Sabato dalle 8 alle 12 il server sarà spento.\n"
         "────────────────────────────────────────\n"
         "[AMS] Do you confirm you have read the message? [y/N] y\n"
         "[AMS] Confirmed.", "Lo stesso messaggio per un utente che lavora in inglese") + \
    table(["Lingua della sessione (" + c("LANG") + ", " + c("LC_MESSAGES") + ", " + c("LC_ALL") + ", "
           + c("LANGUAGE") + ")", "AMS si mostra in"], [
        ["italiano, per esempio " + c("LANG=it_IT.UTF-8"), "italiano"],
        ["inglese, o una lingua che AMS non ha ancora", "inglese"],
        [c("C") + " o " + c("POSIX") + ", o nessuna lingua", "inglese"],
    ], "«TAB» — Le lingue di AMS") + ul([
        "La domanda accetta " + key("s") + " e " + key("y") + " in ogni lingua.",
        "Il testo scritto nei terminali all'invio usa la lingua della shell di quel terminale; se non si riesce a "
        "saperla, quella della macchina.",
        c("ams") + " e la TUI parlano la lingua dell'amministratore che li usa.",
        "Il registro di sistema è nella lingua della macchina; " + c("ams log") + " e la TUI lo riscrivono in quella "
        "di chi legge.",
    ]) + dialog("AMS · Message from the administrator", "Manutenzione · 30/09 16:55",
                "Sabato dalle 8 alle 12 il server sarà spento.",
                "«FIG» — La finestra per un utente in inglese: pulsanti «I have read it» e «Later»").replace(
        "<span>Più tardi</span><span>Ho letto</span>", "<span>Later</span><span>I have read it</span>")

S8 = p("Gli utenti non hanno comandi di AMS e non devono imparare nulla. Può però servire rispondere a qualche "
       "domanda: la tabella raccoglie le più comuni, con risposte vere e brevi da girare così come sono.",
       lead=True) + \
    table(["Domanda dell'utente", "Risposta"], [
        ["«Cos'è questa finestra?»", "Un messaggio degli amministratori della macchina. «Ho letto» conferma di "
         "averlo letto; «Più tardi» lo rimanda di mezz'ora."],
        ["«Se premo Più tardi succede qualcosa?»", "No, si continua a lavorare. Il messaggio torna dopo 30 minuti "
         "finché non si conferma."],
        ["«Devo confermare anche nel terminale?»", "No: una conferma vale ovunque. La domanda nel terminale si chiude "
         "da sola."],
        ["«Posso rileggere un messaggio già confermato?»", "No: dopo la conferma non ricompare. Se serve, chiedere "
         "all'amministratore."],
        ["«Posso rispondere?»", "No: AMS serve solo agli avvisi degli amministratori. Per rispondere si usano i "
         "canali di sempre."],
        ["«Gli altri vedono i miei messaggi?»", "No: ognuno vede solo i messaggi mandati a lui."],
        ["«Perché è in inglese?»", "La sessione non ha la lingua italiana impostata (" + rif(12, 2) + ")."],
    ], "«TAB» — Le domande degli utenti") + \
    tip("per un avviso importante conviene dire agli utenti, con il primo messaggio, cosa sono la finestra e la "
        "domanda: il primo messaggio può spiegare AMS stesso.", "Il primo messaggio.")

CHAPTER = ("Cosa vedono gli utenti", [
    ("Sul desktop", S1),
    ("Nel terminale", S2),
    ("Le shell", S3),
    ("Chi non è collegato", S4),
    ("Più sessioni, una conferma", S5),
    ("Rimandare e solleciti", S6),
    ("In quale lingua", S7),
    ("Spiegare AMS agli utenti", S8),
])
