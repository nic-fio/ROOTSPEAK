from build import c, p, table, term

S0 = p(c("tests/engine.sh") + " prova il motore in modalità di prova, senza root, su un archivio temporaneo nuovo per "
       "ogni caso. Ogni difetto corretto vi aggiunge i controlli che falliscono senza la correzione.", lead=True) + \
    table(["Gruppo", "Controlli"], [
        ["conferme", "conferma normale; scrittura impossibile (il messaggio resta, l'utente è avvisato, nessun file "
         "temporaneo, la domanda torna e poi riesce); conferma già presente (resta la prima)"],
        ["consegna", "invio normale a due destinatari; copia non scrivibile per uno (errore, l'altro la riceve, "
         "«non consegnato», segno di invio incompleto); guasto risolto e recupero; interruzione simulata a metà; "
         "recupero che non ripropone un messaggio confermato; invio interrotto prima del salvataggio (annullato)"],
        ["scadenza", "la domanda si ferma se il messaggio scade mentre è aperta, nessuna conferma registrata; una "
         "conferma con ora dopo la scadenza della copia di riferimento non vale e non è contata"],
        ["configurazione", "il file non viene eseguito come codice; valori validi letti, non validi, sconosciuti, zero e "
         "negativi ignorati; il messaggio dichiara " + c("format: 1")],
        ["pulizia", c("ams purge 7d") + " cancella un messaggio di 10 giorni fa con copie e conferme, lascia quello "
         "recente e gli invii incompleti o in corso, rifiuta una durata non valida"],
        ["agente", "PID scritto in " + c("ams-agent.pronto") + " quando è pronto; la sveglia a quel PID non lo uccide; "
         "il file sparisce all'uscita (solo con una sessione grafica)"],
        ["stati", c("--level") + " rifiutato; consegnato dopo l'invio; nessun livello nel messaggio; rinvio mostrato come "
         "dettaglio e non richiesto subito; confermato al login successivo; " + c("ams list") + " senza colonna del livello; "
         "scaduto come «consegnato, non confermato»"],
    ], "«TAB» — I controlli di tests/engine.sh") + term("nicfio@server:~/AMS$ tests/engine.sh\n1. conferme\n2. consegna\n3. stati\n4. scadenza\n5. configurazione\n6. pulizia\n7. agente\n\nOK: 45 controlli")

SC = p(c("tests/container/esegui.sh") + " prova AMS <b>dal vero</b>, in una macchina di prova isolata: un container "
       "Debian 13 con systemd acceso (logind, sshd), senza root sul sistema che lo ospita. AMS vi è installato con "
       + c("install.sh") + "; gli utenti sono " + c("admin") + " (gruppo sudo), " + c("mario") + " e " + c("anna")
       + " (gruppo sviluppo), " + c("luca") + " e " + c("servizio") + " (senza shell). " + c("scenari.py")
       + " gira come root, apre vere sessioni ssh degli utenti con terminale, risponde alle domande come farebbe una "
       "persona, misura i tempi e registra ogni esito in " + c("tests/container/risultati/") + " ("
       + c("risultati.json") + " e " + c("rapporto.md") + ").", lead=True) + table(["Area", "Scenari"], [
        ["A. Accesso", "root invia; un amministratore invia passando da sudo; un utente normale non esegue " + c("ams")
         + ", nemmeno la guida"],
        ["B. Destinatari", "utente, lista con doppioni, gruppo, " + c("all") + " (esclusi root e nologin), " + c("online")
         + ", utente inesistente, gruppo vuoto"],
        ["C. Consegna", "utente scollegato poi al login; utente collegato (tempo al terminale); ssh senza terminale; due "
         "sessioni, conferma in una che ferma l'altra"],
        ["D. Conferma", "rinvio, promemoria al prompt, domanda di nuovo al login, conferma registrata con canale"],
        ["E. Scadenza e ritiro", "messaggio scaduto non mostrato; ritiro con la domanda in attesa; ritiro prima del login"],
        ["F. Guasti", "copia non scrivibile e recupero; " + c("ams send") + " ucciso con SIGKILL a metà; recupero "
         "concorrente con un invio in corso; conferma non scrivibile"],
        ["G. Sicurezza", "casella trasformata in collegamento a " + c("/etc") + "; sequenze di escape; conferma "
         "fabbricata; " + c("AMS_TEST") + " da utente normale"],
        ["J. Registro", c("ams log") + " ricostruisce invio, consegne, rinvio, conferma e ritiro; la conferma nel journal "
         "porta il " + c("_UID") + " vero"],
        ["H. Prestazioni", "invio a oltre 50 utenti; " + c("list") + " e " + c("status") + " con 10 messaggi"],
        ["I. Desktop", "nel container non provato (nessuna sessione grafica); nella VM sì, capitolo 11.3"],
    ], "«TAB» — Gli scenari dal vero") + table(["Misura", "Valore (30 settembre 2026)"], [
        ["dall'invio al testo nel terminale di un utente collegato", "circa 0,2 s"],
        ["dal login alla domanda di conferma", "circa 0,3 s"],
        ["invio a 54 destinatari", "circa 2,6 s (circa 50 ms per destinatario)"],
        [c("ams list") + " con 10 messaggi × 54 destinatari", "circa 0,7 s (circa 6 s prima della lettura per utente)"],
        [c("ams status") + " di un messaggio con 54 destinatari", "circa 0,7 s (circa 1,3 s prima)"],
    ], "«TAB» — Le misure della prima esecuzione") + term(
        "nicfio@server:~/AMS$ tests/container/esegui.sh\n…\n43 riusciti, 0 falliti, 1 non provati su 44; risultati in /opt/risultati")

SV = p(c("tests/vm/esegui.sh") + " esegue gli stessi scenari in una <b>macchina virtuale con desktop</b>, sul server "
       "delle prove (QEMU con KVM, senza root né libvirt), per coprire anche la finestra di conferma. La VM è Debian 13 "
       "con GNOME su Wayland e zenity 4.1.90; " + c("sara") + " entra da sola nel desktop. Ogni esecuzione parte da una "
       "copia pulita di un disco base preparato una volta (" + c("prepara.sh") + ", cloud-init). I pulsanti della "
       "finestra si premono attraverso l'accessibilità di GNOME (" + c("desktop.py") + ", AT-SPI), come farebbe una "
       "persona, e le schermate arrivano dal monitor di QEMU.", lead=True) + table(["Scenario", "Esito e misura (30 settembre 2026)"], [
        ["I1 · la finestra compare dopo l'invio", "circa 0,5 s"],
        ["I2 · «Ho letto» chiude la finestra e registra la conferma (desktop)", "riuscito"],
        ["I3, I4 · «Più tardi», poi la finestra ricompare (rinvio di prova: 1 minuto)", "ricompare dopo circa 60,5 s"],
        ["I5 · conferma da un terminale con la finestra aperta", "la finestra si chiude in circa 0,8 s"],
        ["I6 · ritiro con la finestra aperta", "la finestra si chiude in circa 1 s"],
        ["I7 · due messaggi, una finestra dopo l'altra", "riuscito"],
        ["I8 · agente assente: ams send lo avvia", "finestra in circa 0,5 s"],
        ["I9 · messaggio a desktop chiuso, poi login grafico", "finestra circa 2,7 s dopo il riavvio del login"],
        ["I10 · «Ho letto» e uscita dalla sessione dopo 0,1 s", "conferma registrata"],
    ], "«TAB» — Gli scenari del desktop nella VM") + p("Esito complessivo nella VM: <b>54 scenari su 54</b>, compresi "
      "quelli del container. La VM ha trovato tre difetti di AMS, tutti corretti: " + c("online") + " includeva root "
      "e gli account di sistema collegati (capitolo 5.2); il lock dell'agente passava ai processi figli (capitolo 7.1); "
      "un'uscita dalla sessione subito dopo «Ho letto» poteva perdere la conferma (capitolo 7.2).")

S1 = p(c("tests/help-tui.py") + " apre " + c("bin/ams --help") + " (con " + c("AMS_TEST=1") + ") su uno "
       "pseudo-terminale, preme tasti e controlla l'ultimo schermo disegnato dopo ciascuno.", lead=True) + \
    table(["Prova", "Controllo"], [
        ["apertura su 100 × 30", "schermo alternativo, cornice, scheda Info, 30 righe da 100 colonne"],
        [c("→"), "scheda Comandi"],
        [c("3"), "scheda Opzioni"],
        [c("4") + " " + c("G"), "fine della scheda Esempi"],
        [c("PgUp") + " " + c("g"), "inizio della scheda"],
        ["ridimensionamento a 70 × 20", "20 righe da 70 colonne"],
        [c("q"), "ritorno allo schermo principale, uscita con codice 0"],
        ["terminale 40 × 8", "pagina in stile manuale attraverso il pager"],
    ], "«TAB» — Le prove di tests/help-tui.py") + term("nicfio@server:~/AMS$ python3 tests/help-tui.py\nOK")

S2 = table(["Controllo", "Fallisce se"], [
    ["manuali aggiornati", "i due manuali in " + c("docs/") + " non coincidono con quelli rigenerati dai sorgenti"],
    ["riferimento", "una voce di " + c("AMS_HELP_COMMANDS") + " o " + c("AMS_HELP_OPTIONS") + " manca dal manuale utente, "
     "ha una descrizione diversa, o il manuale ne documenta una inesistente"],
    ["mappa dei file", "un file di codice non compare nella mappa del capitolo 3.1, o la mappa ne cita uno inesistente"],
    ["versione", c("AMS_VERSION") + " non compare nei due manuali"],
    ["link", "un link " + c("#ancora") + " non porta a nessun id"],
], "«TAB» — I controlli di tools/check-docs.py") + term(
    "nicfio@server:~/AMS$ tools/check-docs.py\n"
    "documentazione allineata: 2 manuali, 11 voci della guida, 13 file nella mappa, versione 0.1.0")

S3 = p("Oltre alle suite, nella versione 0.1.0 AMS è stato provato anche dal vivo su Debian 13 con GNOME 48 su "
       "Wayland, con due account.", lead=True) + table(["Provato", "Come"], [
    ["finestra immediata a un utente collegato", "dal vivo"],
    ["finestra al login di un utente non collegato", "dal vivo, con un secondo account"],
    ["testo e domanda nel terminale, anche via ssh", "dal vivo, con " + c("ssh user@localhost")],
    ["conferma unica fra finestra e terminale", "dal vivo"],
    [c("list") + ", " + c("status"), "dal vivo"],
    [c("revoke") + " con domanda in attesa, scadenze, errori, pulizia del testo", "in modalità di prova"],
], "«TAB» — Cosa è stato provato")

CHAPTER = ("Test e controlli", [
    ("Il motore: tests/engine.sh", S0),
    ("Dal vero: tests/container", SC),
    ("Col desktop: tests/vm", SV),
    ("La guida integrata: tests/help-tui.py", S1),
    ("La documentazione: tools/check-docs.py", S2),
    ("Prove dal vivo", S3),
])
