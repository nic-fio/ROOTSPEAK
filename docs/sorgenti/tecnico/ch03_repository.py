from build import c, dl, file_map, flow, p, steps, table, term, warn

S1 = p("Il repository contiene il codice in C, i cataloghi delle lingue, i file da installare nel sistema, i manuali "
       "con i loro sorgenti, le prove e i controlli di coerenza. Le righe di questa tabella sono contate a ogni "
       "generazione del manuale.", lead=True) + file_map([
    ("src/ams.c", "Il comando degli amministratori: rilancio con sudo, destinatari, " + c("send") + ", " + c("list")
                  + ", " + c("status") + ", " + c("revoke") + ", " + c("log") + ", " + c("purge") + ", recupero."),
    ("src/ams-user.c", "L'aiutante che gira come utente: " + c("prompt") + " (aggancio della shell) e " + c("agent")
                       + " (desktop), registrazione delle conferme."),
    ("src/archivio.c", "Le operazioni sulle caselle, sempre con l'identità dell'utente; scrittura nei terminali; "
                       "lingua dei terminali; sveglia dell'agente."),
    ("src/archivio.h", "Interfaccia di archivio.c."),
    ("src/utente.c", c("come_utente") + ": un processo figlio con l'identità di un utente, al posto di " + c("runuser") + "."),
    ("src/utente.h", "Interfaccia di utente.c."),
    ("src/sessioni.c", "Utenti umani, gruppi, sessioni e terminali, da passwd e da logind (libsystemd)."),
    ("src/sessioni.h", "Interfaccia di sessioni.c."),
    ("src/testo.c", "Pulizia del testo, formato dei messaggi, configurazione."),
    ("src/testo.h", "Interfaccia di testo.c."),
    ("src/lingua.c", "Scelta della lingua e lettore dei cataloghi .mo."),
    ("src/lingua.h", "Interfaccia di lingua.c."),
    ("src/evento.c", "Eventi strutturati nel journal e il loro testo in ogni lingua."),
    ("src/evento.h", "Interfaccia di evento.c."),
    ("src/ams.h", "Le parti di ams usate anche dalla TUI: riassunto dei messaggi, stati dei destinatari, comandi."),
    ("src/tui.c", "La TUI per gli amministratori: lista, dettaglio, scrittura e invio, azioni con conferma."),
    ("src/guida.c", "La guida integrata: guida a schede, pagina in stile manuale, testo semplice."),
    ("src/guida.h", "Interfaccia di guida.c."),
    ("src/comune.c", "Utilità: ambiente, errori, memoria, testi che crescono, lettura e scrittura sicura dei file."),
    ("src/comune.h", "Interfaccia di comune.c, versione e limiti."),
    ("po/ams.pot", "I testi da tradurre, estratti dai sorgenti (" + c("make pot") + ")."),
    ("po/it.po", "La traduzione italiana; fonte anche del riferimento del manuale utente."),
    ("Makefile", "Compilazione, prove interne, analisi statica, sanitizer, estrazione dei testi."),
    ("etc/profile.d/ams.sh", "L'aggancio delle shell che leggono " + c("/etc/profile") + ", in sh semplice: rimanda bash ad " + c("ams.bash") + ", alle altre chiede al login."),
    ("etc/ams.bash", "L'aggancio a bash: la domanda al login e a ogni prompt."),
    ("etc/ams.zsh", "L'aggancio a zsh, richiamato dallo zshrc di sistema."),
    ("etc/ams.fish", "L'aggancio a fish, installato in " + c("/etc/fish/conf.d") + "."),
    ("etc/xdg/autostart/ams-agent.desktop", "Avvio automatico dell'agente del desktop."),
    ("etc/ams/ams.conf", "La configurazione predefinita."),
    ("install.sh", "Installazione, aggiornamento, rimozione."),
    ("tests/engine.sh", "Prove del motore in modalità di prova: conferme, consegna, stati, scadenza, lingue, guasti."),
    ("tests/prove-unita.c", "Prove delle parti interne (pulizia, lingue, messaggi, configurazione, eventi)."),
    ("tests/fuzz/fuzz.c", "Fuzzing con libFuzzer di ciò che legge dati non fidati."),
    ("tests/fuzz/esegui.sh", "Compila e lancia il fuzzing in un container con clang."),
    ("tests/container/Containerfile", "La macchina di prova: Debian 13 con systemd, sshd, utenti e shell diverse."),
    ("tests/container/esegui.sh", "Avvia la macchina di prova, installa AMS, esegue gli scenari, salva i risultati."),
    ("tests/container/scenari.py", "Gli scenari dal vero, eseguiti come root dentro la macchina di prova (anche nella VM, con quelli del desktop)."),
    ("tests/vm/esegui.sh", "Prove nella VM con desktop sul server delle prove: codice, VM pulita, scenari, schermate, risultati."),
    ("tests/vm/prepara.sh", "Costruisce una volta il disco base della VM (Debian 13, GNOME, utenti)."),
    ("tests/vm/user-data.tpl", "La configurazione cloud-init della VM: pacchetti, utenti, login automatico, accessibilità."),
    ("tests/vm/avvia.sh", "Avvia la VM da una copia pulita del disco base."),
    ("tests/vm/ferma.sh", "Spegne la VM e cancella il disco di lavoro."),
    ("tests/vm/cattura.py", "Cattura lo schermo della VM dal monitor di QEMU."),
    ("tests/vm/desktop.py", "Legge e preme i pulsanti delle finestre di AMS attraverso l'accessibilità di GNOME."),
    ("tests/help-tui.py", "Prova della guida integrata su un terminale virtuale."),
    ("tests/tui.py", "Prova della TUI su un terminale virtuale: lista, dettaglio, invio, editor, sollecito, ritiro, ricerca."),
    ("tools/schermate-tui.sh", "Schermate vere della TUI per i manuali, catturate nella macchina di prova."),
    ("tools/check-docs.py", "Controlli di coerenza tra codice, guida, traduzioni, manuali e prove."),
    ("tools/impronta.sh", "Impronta del codice (SHA-256 di src, po, Makefile, etc, install.sh) e commit, registrati con i risultati delle prove."),
    ("docs/sorgenti/build.py", "Generatore dei due manuali."),
    ("docs/sorgenti/stile.css", "Lo stile dei manuali, quello di IR_Service."),
], "«TAB» — Mappa dei file") + \
    p("I capitoli dei manuali stanno in " + c("docs/sorgenti/utente/") + " e " + c("docs/sorgenti/tecnico/")
      + ", un file per capitolo; " + c("docs/decisioni-e-storia.md") + " e " + c("CLAUDE.md") + " raccolgono le "
      "decisioni e gli accordi di lavoro. Il prototipo in bash (versione 0.1.0) è nella storia del repository.")

S2 = flow([("Compilazione", "make, se serve", "dark"), ("Programmi", "ams 750 · ams-user", "blue"),
           ("Lingue, agganci", "locale/, etc", "blue"), ("/var/lib/ams", "users 755 · sent 700", "blue"),
           ("Agenti", "chiusi e riavviati", "navy")], "«FIG» — Le tappe di install.sh") + steps([
    "Si rilancia con sudo se serve, e sceglie il gruppo degli amministratori: il primo esistente fra " + c("sudo") + ", "
    + c("wheel") + ", " + c("admin") + " (altrimenti " + c("root") + ").",
    "Se in " + c("build/") + " mancano i programmi, o sono stati compilati per altre cartelle, li compila con "
    + c("make PREFIX=…") + " (servono gcc, make, pkg-config, libsystemd-dev e gettext).",
    "Installa " + c("$PREFIX/bin/ams") + " con proprietario " + c("root:gruppo") + " e permessi " + c("750") + ", "
    + c("$PREFIX/lib/ams/ams-user") + " e i cataloghi in " + c("$PREFIX/share/locale/LINGUA/LC_MESSAGES/ams.mo") + "; "
    "toglie i file del prototipo in bash. " + c("PREFIX") + " vale " + c("/usr/local") + ".",
    "Installa i manuali, la configurazione (solo se manca), gli agganci delle shell (bash, zsh, fish, sh) e "
    "l'avvio automatico, sostituendo " + c("@LIBDIR@") + " e " + c("@VARDIR@") + ".",
    "Aggiunge a " + c("/etc/bash.bashrc") + " la riga marcata " + c("# AMS hook") + ": su Debian le shell interattive "
    "non di login non leggono " + c("/etc/profile.d") + ". Se zsh è installata, aggiunge la stessa riga allo "
    "zshrc di sistema.",
    "Crea " + c("/var/lib/ams") + " e " + c("users/") + " (" + c("755") + ") e " + c("sent/") + " (" + c("700") + ").",
    "Chiude gli agenti della versione precedente (anche quelli in bash): ripartono aggiornati al primo invio o al login.",
]) + table(["Opzione", "Effetto"], [
    ["nessuna", "installa o aggiorna"],
    [c("--uninstall"), "toglie programmi, cataloghi, file e righe di " + c("bash.bashrc") + " e zshrc, ferma gli agenti; "
     "conserva messaggi e configurazione"],
    [c("--purge"), "come " + c("--uninstall") + ", e toglie anche " + c("/var/lib/ams") + " e " + c("/etc/ams")],
], "«TAB» — Le modalità di install.sh")

S3 = p("Il codice si prova dalla cartella del repository come utente normale, su un archivio di prova, dopo "
       + c("make") + ".", lead=True) + dl([
    ("AMS_TEST=1", c("ams") + " non si rilancia con sudo, non sveglia né avvia agenti e scrive solo nel «terminale» "
     + c("AMS_TEST_TTY") + ". Solo in questa modalità valgono le variabili qui sotto: un programma di root non prende "
     "cartelle dall'ambiente di chi lo lancia. Un utente normale che la imposta resta con i suoi permessi, e sotto "
     "sudo la variabile viene tolta."),
    ("AMS_VAR=cartella", "archivio al posto di " + c("/var/lib/ams") + "."),
    ("AMS_LIB=cartella", "dove sta " + c("ams-user") + " (per la riga di comando dell'agente)."),
    ("AMS_LOCALEDIR=cartella", "dove stanno i cataloghi: " + c("build/locale") + " dopo " + c("make") + "."),
    ("AMS_CONF=file", "configurazione al posto di " + c("/etc/ams/ams.conf") + " (" + c("/dev/null") + " per i valori predefiniti)."),
    ("AMS_TEST_TTY=file", "il «terminale» su cui " + c("ams send") + " scrive in modalità di prova."),
]) + term("nicfio@server:~/AMS$ make\n"
          "nicfio@server:~/AMS$ export AMS_TEST=1 AMS_LIB=$PWD/build AMS_LOCALEDIR=$PWD/build/locale\n"
          "nicfio@server:~/AMS$ export AMS_VAR=/tmp/prova AMS_CONF=/dev/null AMS_TEST_TTY=/tmp/tty\n"
          "nicfio@server:~/AMS$ build/ams send --to nicfio \"Prova\"\n"
          "Messaggio 1 inviato a 1 utente.\n"
          "nicfio@server:~/AMS$ script -qec 'build/ams-user prompt' /dev/null", "Una prova senza root") + \
    warn("senza " + c("AMS_TEST") + ", " + c("build/ams") + " passa da sudo; se le credenziali di sudo sono ancora "
         "valide parte come root senza chiedere nulla, sull'archivio vero.")

S4 = steps([
    c("make") + " (tutti gli avvisi sono errori) e " + c("make prove") + ".",
    c("make pot") + " se sono cambiati testi da tradurre, poi la traduzione in " + c("po/it.po") + ".",
    c("python3 docs/sorgenti/build.py") + ", poi " + c("tools/check-docs.py") + ": manuali generati aggiornati, "
    "riferimento allineato alla guida, cataloghi completi, mappa dei file completa, link interni validi, prove "
    "eseguite sul codice attuale (capitolo 11.5).",
    c("tests/engine.sh") + " sempre; " + c("tests/help-tui.py") + " se è cambiata la guida; " + c("tests/tui.py")
    + " e " + c("tools/schermate-tui.sh") + " se è cambiata la TUI; "
    + c("make sanitizer") + " con " + c("AMS_BUILD=build-san tests/engine.sh") + ", " + c("make analizza") + " e "
    + c("tests/fuzz/esegui.sh") + " se è cambiato il codice che legge dati; " + c("tests/container/esegui.sh")
    + " se sono cambiati invio, consegna, conferme o permessi; " + c("tests/vm/esegui.sh") + " se è cambiato il desktop.",
    "Una prova del flusso toccato in modalità di prova; per desktop, sudo e altri utenti, una prova dal vivo dopo "
    + c("./install.sh") + ".",
])

CHAPTER = ("Repository e installazione", [
    ("Mappa dei file", S1),
    ("install.sh passo per passo", S2),
    ("Provare senza root", S3),
    ("Prima di registrare una modifica", S4),
])
