from build import c, p, steps, table, term, tip, warn

S1 = p("AMS funziona su una distribuzione Linux con systemd. È provato su Debian 13 con GNOME su Wayland, dal vivo e "
       "con prove automatiche in un container e in una macchina virtuale. Con X11, altri desktop e altre distribuzioni "
       "dovrebbe funzionare allo stesso modo, ma non è stato provato; senza systemd non funziona.", lead=True) + \
    table(["Serve", "A cosa", "Pacchetto su Debian e Ubuntu"], [
        ["systemd", "trovare chi è collegato e dove", "già presente"],
        ["sudo e un gruppo di amministratori", "decidere chi può usare AMS", c("sudo") + " (gruppo " + c("sudo") + "; " + c("wheel") + " su Fedora)"],
        ["una shell: bash, zsh o fish", "la domanda di conferma nei terminali a ogni prompt (con sh, dash, ksh: solo al login)", "bash è già presente"],
        ["zenity", "la finestra «Ho letto» sul desktop", c("zenity")],
    ], "«TAB» — Cosa serve") + \
    term("admin@server:~$ sudo apt install zenity")

S2 = steps([
    "Aprire un terminale nella cartella di AMS.",
    "Lanciare l'installazione e inserire la password di sudo:" + term(
        "admin@server:~/AMS$ ./install.sh\n"
        "AMS installato. Comando: /usr/local/bin/ams (utilizzabile dal gruppo sudo).\n"
        "Manuali: /usr/local/share/doc/ams/AMS_Manuale_Utente.html e AMS_Manuale_Tecnico.html\n"
        "Le sessioni già aperte ricevono i messaggi sul terminale subito e la domanda\n"
        "di conferma dalla prossima shell o dal prossimo login.", ""),
    "Controllare che il comando risponda:" + term("admin@server:~$ ams version\n"
                                                  "AMS - Advanced Messaging System for linux 0.1.0", ""),
]) + tip("gli utenti già collegati ricevono subito i messaggi, anche sul desktop. La domanda di conferma nel terminale "
         "arriva invece dalla prossima finestra di terminale che aprono: quelle già aperte non hanno ancora caricato AMS.",
         "Utenti già collegati.")

S3 = table(["Dove", "Che cos'è"], [
    [c("/usr/local/bin/ams"), "Il comando degli amministratori. Solo il gruppo degli amministratori può eseguirlo."],
    [c("/etc/ams/ams.conf"), "Le impostazioni (capitolo 8). Un aggiornamento non le sovrascrive."],
    [c("/var/lib/ams/"), "I messaggi e le conferme."],
    [c("/usr/local/share/doc/ams/"), "Questo manuale e il manuale tecnico."],
    [c("/usr/local/lib/ams/"), "Le parti interne di AMS."],
    [c("/etc/profile.d/ams.sh") + ", " + c("/etc/fish/conf.d/ams.fish") + ", " + c("/etc/xdg/autostart/ams-agent.desktop"),
     "Ciò che collega AMS ai terminali e al desktop degli utenti."],
    [c("/etc/bash.bashrc") + " e, se c'è zsh, " + c("/etc/zsh/zshrc"), "Una riga in fondo, marcata " + c("# AMS hook") + "."],
], "«TAB» — Cosa viene installato")

S4 = table(["Per", "Comando", "Cosa succede"], [
    ["Aggiornare", c("./install.sh"), "Installa la versione nuova; messaggi e impostazioni restano."],
    ["Rimuovere AMS", c("./install.sh --uninstall"), "Toglie AMS; messaggi e impostazioni restano, per un'eventuale reinstallazione."],
    ["Rimuovere tutto", c("./install.sh --purge"), "Toglie AMS, i messaggi e le impostazioni."],
], "«TAB» — Aggiornare e rimuovere") + \
    warn(c("--purge") + " cancella anche l'elenco di chi ha confermato cosa. Se serve conservarlo, prima si copia "
         + c("/var/lib/ams") + " altrove.")

CHAPTER = ("Installazione", [
    ("Cosa serve", S1),
    ("Installare", S2),
    ("Cosa viene installato", S3),
    ("Aggiornare e rimuovere", S4),
])
