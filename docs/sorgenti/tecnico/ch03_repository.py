from build import c, dl, file_map, flow, p, steps, table, term, warn

S1 = p("Il repository contiene il codice, i file da installare nel sistema, i manuali con i loro sorgenti, "
       "un test e un controllo di coerenza. Le righe di questa tabella sono contate a ogni generazione del manuale.",
       lead=True) + file_map([
    ("bin/ams", "Il comando degli amministratori: rilancio con sudo, destinatari, sessioni, archivio, "
                + c("send") + ", " + c("list") + ", " + c("status") + ", " + c("revoke") + "."),
    ("lib/ams-common.sh", "Libreria comune: configurazione, versione, pulizia del testo, lettura e formattazione dei messaggi."),
    ("lib/ams-user", "L'aiutante che gira come utente: " + c("prompt") + " (aggancio della shell) e " + c("agent")
                     + " (desktop), registrazione delle conferme."),
    ("lib/ams-help.sh", "La guida integrata: testi, guida a schede, pagina in stile manuale."),
    ("etc/profile.d/ams.sh", "L'aggancio delle shell che leggono " + c("/etc/profile") + ", in sh semplice: rimanda bash ad " + c("ams.bash") + ", alle altre chiede al login."),
    ("etc/ams.bash", "L'aggancio a bash: la domanda al login e a ogni prompt."),
    ("etc/ams.zsh", "L'aggancio a zsh, richiamato dallo zshrc di sistema."),
    ("etc/ams.fish", "L'aggancio a fish, installato in " + c("/etc/fish/conf.d") + "."),
    ("etc/xdg/autostart/ams-agent.desktop", "Avvio automatico dell'agente del desktop."),
    ("etc/ams/ams.conf", "La configurazione predefinita."),
    ("install.sh", "Installazione, aggiornamento, rimozione."),
    ("tests/engine.sh", "Test del motore in modalità di prova: conferme, casella, guasti."),
    ("tests/container/Containerfile", "La macchina di prova: Debian 13 con systemd, sshd e utenti."),
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
    ("tools/check-docs.py", "Controlli di coerenza tra codice, guida e manuali."),
    ("docs/sorgenti/build.py", "Generatore dei due manuali."),
    ("docs/sorgenti/stile.css", "Lo stile dei manuali, quello di IR_Service."),
], "«TAB» — Mappa dei file") + \
    p("I capitoli dei manuali stanno in " + c("docs/sorgenti/utente/") + " e " + c("docs/sorgenti/tecnico/")
      + ", un file per capitolo; " + c("docs/decisioni-e-storia.md") + " e " + c("CLAUDE.md") + " raccolgono le "
      "decisioni e gli accordi di lavoro.")

S2 = flow([("Gruppo admin", "sudo, wheel, admin", "dark"), ("File", "lib, bin, etc, manuali", "blue"),
           ("bashrc, zshrc", "riga # AMS hook", "blue"), ("/var/lib/ams", "users 755 · sent 700", "blue"),
           ("Agenti", "chiusi e riavviati", "navy")], "«FIG» — Le tappe di install.sh") + steps([
    "Si rilancia con sudo se serve, e sceglie il gruppo degli amministratori: il primo esistente fra " + c("sudo") + ", "
    + c("wheel") + ", " + c("admin") + " (altrimenti " + c("root") + ").",
    "Copia la libreria in " + c("$PREFIX/lib/ams") + "; installa " + c("$PREFIX/bin/ams") + " sostituendo la riga "
    + c("AMS_LIB=") + ", con proprietario " + c("root:gruppo") + " e permessi " + c("750") + ". " + c("PREFIX")
    + " vale " + c("/usr/local") + ".",
    "Installa i manuali, la configurazione (solo se manca), gli agganci delle shell (bash, zsh, fish, sh) e "
    "l'avvio automatico, sostituendo "
    + c("@LIBDIR@") + " e " + c("@VARDIR@") + ".",
    "Aggiunge a " + c("/etc/bash.bashrc") + " la riga marcata " + c("# AMS hook") + ": su Debian le shell interattive "
    "non di login non leggono " + c("/etc/profile.d") + ". Se zsh è installata, aggiunge la stessa riga allo "
    "zshrc di sistema.",
    "Crea " + c("/var/lib/ams") + " e " + c("users/") + " (" + c("755") + ") e " + c("sent/") + " (" + c("700") + ").",
    "Chiude gli agenti della versione precedente: ripartono aggiornati al primo invio o al login.",
]) + table(["Opzione", "Effetto"], [
    ["nessuna", "installa o aggiorna"],
    [c("--uninstall"), "toglie file e righe di " + c("bash.bashrc") + " e zshrc, ferma gli agenti; conserva messaggi e configurazione"],
    [c("--purge"), "come " + c("--uninstall") + ", e toglie anche " + c("/var/lib/ams") + " e " + c("/etc/ams")],
], "«TAB» — Le modalità di install.sh")

S3 = p("Il codice si prova dalla cartella del repository come utente normale, su un archivio di prova.", lead=True) + dl([
    ("AMS_TEST=1", c("ams") + " non si rilancia con sudo, non scrive nei terminali veri (solo in " + c("AMS_TEST_TTY")
     + ") e non sveglia né avvia agenti. Non apre nessuna porta: un utente normale che la imposta resta con i suoi "
     "permessi, e sotto sudo la variabile viene tolta."),
    ("AMS_VAR=cartella", "archivio al posto di " + c("/var/lib/ams") + "."),
    ("AMS_LIB=cartella", "libreria da usare: dopo un'installazione, senza questa variabile " + c("bin/ams")
     + " carica quella in " + c("/usr/local/lib/ams") + "."),
    ("AMS_CONF=file", "configurazione al posto di " + c("/etc/ams/ams.conf") + " (" + c("/dev/null") + " per i valori predefiniti)."),
    ("AMS_TEST_TTY=file", "il «terminale» su cui " + c("ams send") + " scrive in modalità di prova."),
]) + term("nicfio@server:~/AMS$ export AMS_TEST=1 AMS_LIB=$PWD/lib AMS_VAR=/tmp/prova\n"
          "nicfio@server:~/AMS$ export AMS_CONF=/dev/null AMS_TEST_TTY=/tmp/tty\n"
          "nicfio@server:~/AMS$ bin/ams send --to nicfio \"Prova\"\n"
          "Messaggio 1 inviato a 1 utente.\n"
          "nicfio@server:~/AMS$ script -qec 'lib/ams-user prompt' /dev/null", "Una prova senza root") + \
    warn("senza " + c("AMS_TEST") + ", " + c("bin/ams") + " passa da sudo; se le credenziali di sudo sono ancora "
         "valide parte come root senza chiedere nulla, sull'archivio vero.")

S4 = steps([
    c("bash -n") + " su tutti gli script.",
    c("python3 docs/sorgenti/build.py") + " se sono cambiati i manuali o la guida integrata.",
    c("tools/check-docs.py") + ": manuali generati aggiornati, riferimento allineato alla guida, mappa dei file "
    "completa, link interni validi (capitolo 11.2).",
    c("tests/engine.sh") + " sempre; " + c("tests/help-tui.py") + " se è cambiata la guida; "
    + c("tests/container/esegui.sh") + " se sono cambiati invio, consegna, conferme o permessi.",
    "Una prova del flusso toccato in modalità di prova; per desktop, sudo e altri utenti, una prova dal vivo dopo "
    + c("./install.sh") + ".",
])

CHAPTER = ("Repository e installazione", [
    ("Mappa dei file", S1),
    ("install.sh passo per passo", S2),
    ("Provare senza root", S3),
    ("Prima di registrare una modifica", S4),
])
