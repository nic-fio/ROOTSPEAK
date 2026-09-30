from build import arrow, box, c, fig, note, p, risultati_prove, table, term, text, ul, warn, zone


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">capitolo {n}{"." + str(s) if s else ""}</a>'


LIVELLI = fig(
    box(330, 20, 240, 44, "dal vivo", "dopo install.sh, dall'utente", "grey", 12)
    + box(250, 72, 400, 44, "tests/vm", "VM con GNOME su Wayland, root, finestre vere", "navy", 12)
    + box(170, 124, 560, 44, "tests/container", "Debian 13 con systemd, root, sessioni ssh vere, nove utenti", "navy",
          12)
    + box(90, 176, 720, 44, "tests/engine.sh · tests/tui.py · tests/help-tui.py",
          "modalità di prova, senza root, archivio temporaneo, terminali virtuali", "blue", 12)
    + box(20, 228, 860, 44, "make prove · make analizza · make sanitizer · tests/fuzz",
          "parti interne, analisi statica, AddressSanitizer e UBSan, libFuzzer", "dark", 12)
    + text(450, 300, "salendo: più vicino all'uso vero, più lento; scendendo: più veloce, più ripetibile", 11.5,
           "#475569", "600"),
    900, 318, "«FIG» — I livelli delle prove", "Le prove")

S1 = p("Ogni affermazione sul comportamento di AMS viene da un'esecuzione. Le prove sono a livelli: in basso le "
       "parti interne e il motore, veloci e senza root; in alto la macchina di prova e la VM, dove AMS gira come "
       "root con utenti, sessioni e finestre vere.", lead=True) + LIVELLI + \
    p("I numeri delle prove non si scrivono a mano: ogni suite registra il suo esito con il commit e l'<b>impronta</b> "
      "del codice provato (" + c("tools/impronta.sh") + ": SHA-256 di " + c("src/") + ", " + c("po/") + ", "
      + c("Makefile") + ", " + c("etc/") + " e " + c("install.sh") + "), e questa tabella li legge a ogni generazione "
      "del manuale. «Vale per il codice attuale» dice se l'impronta registrata è quella del codice di questo "
      "manuale.") + risultati_prove() + \
    note("il container non ha una sessione grafica: lo scenario della finestra vi risulta «non provato» e si prova "
         "nella VM. Nella VM mancano gli utenti con zsh, fish, ksh e dash: le shell si provano solo nel container.")

S2 = p(c("tests/engine.sh") + " prova il motore in modalità di prova, senza root, su un archivio temporaneo nuovo "
       "per ogni caso, con i programmi di " + c("build/") + " (o di " + c("AMS_BUILD") + ", per esempio i sanitizer). "
       "Ogni difetto corretto vi aggiunge i controlli che falliscono senza la correzione.", lead=True) + \
    table(["Gruppo", "Controlli"], [
        ["1. conferme", "conferma normale; scrittura impossibile (il messaggio resta, l'utente è avvisato, nessun file "
         "temporaneo, la domanda torna e poi riesce); conferma già presente (resta la prima); conferma registrata "
         "ma non spostata"],
        ["2. consegna", "invio normale a due destinatari; copia non scrivibile per uno (errore, l'altro la riceve, "
         "«inviato, non consegnato», segno di invio incompleto); guasto risolto e recupero; interruzione simulata a "
         "metà; recupero che non ripropone un messaggio confermato; invio non salvato annullato; invio in corso "
         "(lock occupato) non toccato, poi completato senza doppioni; invio appena iniziato non annullato"],
        ["3. stati", c("--level") + " rifiutato; consegnato dopo l'invio; nessun livello nel messaggio; rinvio "
         "mostrato come dettaglio e non richiesto subito; confermato al login successivo; " + c("ams list")
         + " con i destinatari nei tre stati e nessuno stato inventato; scaduto come «consegnato, non confermato»"],
        ["4. scadenza", "la domanda si ferma se il messaggio scade mentre è aperta, nessuna conferma registrata; una "
         "conferma con ora dopo la scadenza della copia di riferimento non vale e non è contata"],
        ["5. configurazione", "il file non viene eseguito come codice; valori validi letti, non validi, sconosciuti, "
         "zero e negativi ignorati; il messaggio dichiara " + c("format: 1")],
        ["6. pulizia", c("ams purge 7d") + " cancella un messaggio di 10 giorni fa con copie e conferme, lascia quello "
         "recente e gli invii incompleti o in corso, rifiuta una durata non valida"],
        ["7. agente", "PID scritto in " + c("ams-agent.pronto") + " quando è pronto; la sveglia a quel PID non lo "
         "uccide; il file sparisce all'uscita (solo con una sessione grafica, altrimenti saltato)"],
        ["8. lingua", "scelta della lingua secondo le regole di gettext (9 casi, valori strani compresi); utente, "
         "amministratore, errori e guida in inglese e in italiano; canale della conferma tradotto"],
        ["9. seconda revisione", c("ams revoke") + " aspetta un invio in corso; conferma successiva al ritiro non "
         "valida, dello stesso secondo valida; copia tolta mentre l'utente risponde; terminale di un altro utente "
         "non scritto; copia sparita dopo un'interruzione riscritta dal recupero; ritiro e cancellazione interrotti "
         "completati; 5000 file finti in " + c("acks/") + " senza rallentamenti; pipe al posto della conferma; testo "
         "oltre 65536 byte rifiutato, di 65536 accettato; commenti in " + c("ams.conf")],
        ["10. sollecito", "la domanda rimandata non torna subito; " + c("ams remind") + " la fa tornare; chi ha "
         "confermato non è sollecitato; un messaggio ritirato non si sollecita"],
    ], "«TAB» — I gruppi di tests/engine.sh") + \
    p("Alla fine " + c("tests/engine.sh") + " scrive " + c("tests/risultati/engine.json") + " con data, commit, "
      "impronta e conteggi; " + c("tools/check-docs.py") + " fallisce se quell'impronta non è quella del codice "
      "attuale. " + c("tests/prove-unita.c") + " (" + c("make prove") + ") prova le parti interne una per una: "
      "pulizia, lingue, messaggi, configurazione, testi degli eventi.")

S3 = p(c("tests/container/esegui.sh") + " prova AMS <b>dal vero</b> in una macchina di prova isolata: un container "
       "Debian 13 con systemd acceso (logind, sshd), senza root sul sistema che lo ospita. AMS vi è installato con "
       + c("install.sh") + "; gli utenti sono " + c("admin") + " (gruppo sudo), " + c("mario") + " e " + c("anna")
       + " (gruppo sviluppo), " + c("luca") + ", " + c("servizio") + " (senza shell) e quattro utenti con altre "
       "shell: " + c("zeno") + " (zsh), " + c("fabio") + " (fish), " + c("kora") + " (ksh), " + c("dario")
       + " (dash). " + c("scenari.py") + " gira come root, apre vere sessioni ssh con terminale, risponde alle "
       "domande come farebbe una persona, misura i tempi e registra ogni esito.", lead=True) + table(
    ["Area", "Scenari"], [
        ["A. Accesso", "root invia; un amministratore invia passando da sudo; un utente normale non esegue "
         + c("ams") + ", nemmeno la guida"],
        ["B. Destinatari", "utente, lista con doppioni, gruppo, " + c("all") + " (esclusi root e nologin), "
         + c("online") + ", utente inesistente, gruppo vuoto"],
        ["C. Consegna", "utente scollegato poi al login; utente collegato (tempo al terminale); ssh senza terminale; "
         "due sessioni, conferma in una che ferma l'altra"],
        ["D. Conferma", "rinvio, promemoria al prompt, sollecito, domanda di nuovo al login, conferma con canale"],
        ["E. Scadenza e ritiro", "messaggio scaduto non mostrato; ritiro con la domanda in attesa; ritiro prima del "
         "login"],
        ["F. Guasti", "copia non scrivibile e recupero; " + c("ams send") + " ucciso con SIGKILL a metà; cartella "
         "dell'utente rimasta di root; " + c("ams revoke") + " durante un invio a molti utenti; recupero concorrente "
         "con un invio in corso; conferma non scrivibile"],
        ["G. Sicurezza", "casella trasformata in collegamento a " + c("/etc") + "; sequenze di escape; conferma "
         "fabbricata; " + c("AMS_TEST") + " da utente normale"],
        ["J. Registro", c("ams log") + " ricostruisce la storia; la conferma porta il " + c("_UID") + " di chi l'ha "
         "scritta; un evento falso scritto da un utente è segnalato"],
        ["T. TUI", c("ams") + " da solo come root: lista con i destinatari nei tre stati, dettaglio e storia, uscita"],
        ["K. Shell", "zsh, fish, ksh e dash: domanda al login; testo all'invio; domanda al prompt in zsh e fish, "
         "non in ksh e dash"],
        ["L. Lingua", "stesso messaggio a un utente in inglese e a uno in italiano; domanda, conferma, "
         + c("ams status") + " e " + c("ams log") + " nella lingua di chi legge"],
        ["H. Prestazioni", "invio a tutti (una sessantina di utenti); " + c("list") + " con 10 messaggi; " + c("status")],
        ["I. Desktop", "nel container non provato (nessuna sessione grafica); nella VM sì"],
    ], "«TAB» — Gli scenari dal vero") + \
    p(c("tests/vm/esegui.sh") + " esegue gli stessi scenari in una <b>macchina virtuale con desktop</b>, sul server "
      "delle prove (QEMU con KVM, senza root né libvirt), più quelli della finestra. La VM è Debian 13 con GNOME su "
      "Wayland; " + c("sara") + " entra da sola nel desktop. Ogni esecuzione parte da una copia pulita di un disco "
      "base preparato una volta (" + c("prepara.sh") + ", cloud-init). I pulsanti della finestra si premono "
      "attraverso l'accessibilità di GNOME (" + c("desktop.py") + ", AT-SPI), come farebbe una persona, e le "
      "schermate arrivano dal monitor di QEMU (" + c("cattura.py") + ").") + table(
    ["Scenario", "Esito e misura (ultima esecuzione registrata)"], [
        ["I1 · la finestra compare dopo l'invio, nella lingua della sessione", "0,58 s"],
        ["I2 · «Ho letto» chiude la finestra e registra la conferma (desktop)", "riuscito"],
        ["I3, I4 · «Più tardi», poi la finestra ricompare (rinvio di prova: 1 minuto)", "ricompare dopo 60,23 s"],
        ["I11 · " + c("ams remind") + " dopo «Più tardi»: la finestra ricompare subito", "0,37 s"],
        ["I5 · conferma da un terminale con la finestra aperta", "la finestra si chiude in 0,65 s"],
        ["I6 · ritiro con la finestra aperta", "la finestra si chiude in 0,67 s"],
        ["I7 · due messaggi, una finestra dopo l'altra, dal più vecchio", "riuscito"],
        ["I8 · agente assente: " + c("ams send") + " lo avvia", "finestra in 0,53 s"],
        ["I9 · messaggio a desktop chiuso, poi login grafico", "finestra 2,64 s dopo il riavvio del login"],
        ["I10 · «Ho letto» e uscita dalla sessione dopo 0,1 s", "conferma registrata"],
    ], "«TAB» — Gli scenari del desktop nella VM") + ul([
    "Il desktop di prova è in italiano; " + c("AMS_PROVA_LINGUA=en") + " lo mette in inglese, "
    + c("AMS_PROVA_SOLO=i_desktop") + " esegue solo gli scenari del desktop.",
    "Ogni esecuzione scrive " + c("risultati.json") + " e " + c("rapporto.md") + " in " + c("tests/container/risultati/")
    + " e " + c("tests/vm/risultati/") + ", con le misure di ogni scenario.",
])

S4 = p("Le due interfacce a tutto schermo si provano su uno pseudo-terminale, premendo tasti come una persona e "
       "controllando l'ultimo schermo disegnato dopo ciascuno.", lead=True) + table(["Prova", "Controllo"], [
    ["apertura", "lista con barra e frase, dimensioni giuste; nessuno stato inventato"],
    [c("Invio") + ", " + c("Tab"), "dettaglio con i destinatari e lo stato di " + c("ams status") + "; storia dal "
     "registro"],
    [c("n") + ", " + c("Ctrl+E") + ", " + c("Ctrl+S"), "modulo, anteprima dei destinatari, testo su due righe; il "
     "testo passa dall'editor e torna; conferma con destinatari, titolo e scadenza; esito dell'invio in una sola "
     "finestra; il messaggio è nell'archivio e in cima alla lista"],
    [c("s") + ", " + c("r"), "sollecito eseguito; conferma prima del ritiro, ritiro annullato con " + c("n")
     + ", poi eseguito: «[ritirato]» nella lista e nell'archivio"],
    [c("/"), "la ricerca mostra solo i messaggi che contengono il testo"],
    ["80 × 24", "barra e «confermati/totale» al posto della frase"],
    [c("q"), "uscita pulita"],
    ["60 × 15, pipe", "niente TUI: la guida"],
], "«TAB» — Le prove di tests/tui.py") + table(["Prova", "Controllo"], [
    ["apertura su 100 × 30", "schermo alternativo, cornice, scheda Info"],
    [c("→"), "scheda Comandi"],
    [c("3"), "scheda Opzioni"],
    [c("4") + " " + c("G"), "fine della scheda Esempi"],
    [c("PgUp") + " " + c("g"), "inizio della scheda"],
    ["ridimensionamento a 70 × 20", "20 righe da 70 colonne"],
    [c("q"), "ritorno allo schermo principale, uscita con codice 0"],
    ["terminale 40 × 8", "pagina in stile manuale attraverso il pager"],
], "«TAB» — Le prove di tests/help-tui.py") + \
    p(c("tools/schermate-tui.sh") + " usa la macchina di prova per catturare le schermate vere della TUI mostrate "
      "nel " + cap(14) + ": i colori sono quelli che vede l'amministratore.")

S5 = table(["Controllo", "Fallisce se"], [
    ["manuali aggiornati", "i due manuali in " + c("docs/") + " non coincidono con quelli rigenerati dai sorgenti"],
    ["riferimento", "una voce dei comandi o delle opzioni della guida integrata manca dal manuale utente, ha una "
     "descrizione diversa, o il manuale ne documenta una inesistente"],
    ["mappa dei file", "un file di codice non compare nella mappa del " + cap(3, 1) + ", o la mappa ne cita uno "
     "inesistente"],
    ["versione", c("AMS_VERSION") + " non compare nei due manuali"],
    ["link", "un link " + c("#ancora") + " non porta a nessun id"],
    ["lingue", "un catalogo " + c("po/*.po") + " non passa " + c("msgfmt --check") + ", ha traduzioni da rivedere o "
     "manca di testi presenti nel codice (estratti di nuovo con " + c("xgettext") + ")"],
    ["prove", "l'ultima esecuzione di " + c("tests/engine.sh") + " non ha l'impronta del codice attuale, o ha "
     "controlli falliti"],
], "«TAB» — I controlli di tools/check-docs.py") + \
    p(c("tools/check-docs.py") + " è l'ultimo passo prima di registrare una modifica (" + cap(3, 5) + "): se passa, "
      "stampa «documentazione allineata» con il numero di voci della guida, di file nella mappa, la versione e le "
      "lingue.")

S6 = p("Prima della riscrittura in C, il prototipo 0.1.0 è stato provato anche <b>dal vivo</b> su Debian 13 con "
       "GNOME 48 su Wayland, con due account. La versione in C non è ancora stata provata dal vivo sul PC "
       "dell'utente: le sue prove sono quelle delle suite.", lead=True) + table(["Provato (prototipo 0.1.0)", "Come"], [
    ["finestra immediata a un utente collegato", "dal vivo"],
    ["finestra al login di un utente non collegato", "dal vivo, con un secondo account"],
    ["testo e domanda nel terminale, anche via ssh", "dal vivo, con " + c("ssh user@localhost")],
    ["conferma unica fra finestra e terminale", "dal vivo"],
    [c("list") + ", " + c("status"), "dal vivo"],
    [c("revoke") + " con domanda in attesa, scadenze, errori, pulizia del testo", "in modalità di prova"],
], "«TAB» — Le prove dal vivo") + \
    warn("le prove dal vivo come root le lancia chi ha la password di root, dopo " + c("./install.sh") + "; nelle "
         "prove fatte da chi lavora al codice va sempre impostata la modalità di prova (" + cap(4, 4) + ").")

S7 = p("Un programma di root in C che legge dati degli utenti non deve avere errori di memoria. Oltre alle prove di "
       "comportamento, la versione 0.2.0 ha queste difese, da riprendere quando cambia il codice che legge dati.",
       lead=True) + table(["Difesa", "Come si lancia", "Che cosa ha trovato"], [
    ["tutti gli avvisi di gcc come errori, e le difese del compilatore (" + cap(17, 3) + ")", c("make"),
     "nulla da correggere: il codice nasce così"],
    ["prove delle parti interne (" + c("tests/prove-unita.c") + ")", c("make prove"), "—"],
    ["AddressSanitizer e UBSan su tutte le prove del motore e della guida, con i rapporti su file (nessuno ammesso)",
     c("make sanitizer") + ", poi " + c("AMS_BUILD=build-san tests/engine.sh"), "nessun errore di memoria"],
    ["analisi statica di gcc", c("make analizza"), "pipe non chiuse in un caso d'errore di " + c("come_utente")
     + " (corretto); restano 3 falsi allarmi sulle copie dei descrittori standard in un figlio che esce subito"],
    ["fuzzing con libFuzzer, in un container con clang, di: pulizia del testo, formato dei messaggi, uscita della "
     "lettura delle caselle, ambiente di un processo, configurazione, cataloghi " + c(".mo"),
     c("tests/fuzz/esegui.sh SECONDI"), "una funzione che presupponeva una struttura già azzerata (corretto); poi "
     "30 minuti senza difetti"],
    ["confronto con il prototipo: la pulizia del testo in C e in bash su 2000 testi casuali", "(prima di togliere "
     "il prototipo)", "risultati identici"],
], "«TAB» — Le difese del C") + \
    note("gli esiti di analisi statica, sanitizer e fuzzing non hanno un file di risultati con l'impronta: sono "
         "quelli dell'ultima esecuzione fatta al momento della riscrittura (30 settembre 2026).")

CHAPTER = ("Test e controlli", [
    ("Le prove e i loro risultati", S1),
    ("Il motore: tests/engine.sh", S2),
    ("Dal vero: la macchina di prova e la VM", S3),
    ("Le interfacce: tests/tui.py e tests/help-tui.py", S4),
    ("La documentazione: tools/check-docs.py", S5),
    ("Prove dal vivo", S6),
    ("Le difese del C", S7),
])
