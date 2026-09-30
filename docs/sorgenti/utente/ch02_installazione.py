import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import c, flow, note, p, steps, table, term, tip, tree, warn  # noqa: E402
from _aiuti import rif  # noqa: E402

S1 = p("AMS funziona su una distribuzione Linux con systemd. È provato su Debian 13 con GNOME su Wayland: dal vivo, "
       "e con prove automatiche in una macchina di prova e in una macchina virtuale con desktop. Con X11, altri desktop "
       "e altre distribuzioni con systemd dovrebbe funzionare allo stesso modo, ma non è stato provato; senza systemd "
       "non funziona.", lead=True) + \
    table(["Requisito", "A cosa serve", "Pacchetto su Debian e Ubuntu"], [
        ["systemd", "sapere chi è collegato e dove, e aprire la finestra sul desktop", "già presente"],
        ["sudo e un gruppo di amministratori", "decidere chi può usare " + c("ams"),
         c("sudo") + " (gruppo " + c("sudo") + "; su Fedora e simili " + c("wheel") + ")"],
        ["una shell: bash, zsh o fish", "la domanda di conferma nei terminali a ogni prompt; con sh, dash e ksh "
         "solo al login", "bash è già presente"],
        ["zenity", "la finestra «Ho letto» / «Più tardi» sul desktop", c("zenity")],
        ["notify-send (facoltativo)", "l'avviso sul desktop quando una conferma non si è potuta registrare",
         c("libnotify-bin")],
        ["gli strumenti per compilare, solo per installare", "AMS è scritto in C: " + c("install.sh") + " lo compila "
         "se serve", c("gcc make pkg-config libsystemd-dev gettext")],
    ], "«TAB» — I requisiti") + \
    term("admin@server:~$ sudo apt install zenity libnotify-bin gcc make pkg-config libsystemd-dev gettext",
         "Installare i pacchetti su Debian e Ubuntu") + \
    note("sulle macchine senza desktop zenity non serve: AMS usa solo i terminali. L'installazione segnala "
         "«Attenzione: manca zenity» ma prosegue.", "Server senza desktop.")

PERCORSO = flow([("make", "compila, come utente", "dark"), ("./install.sh", "installa, con sudo", "navy"),
                 ("ams version", "risponde?", "blue"), ("ams", "la TUI, vuota", "green")],
                "«FIG» — Dall'archivio dei sorgenti al primo avvio", "Installazione in quattro passi")

S2 = PERCORSO + steps([
    "Aprire un terminale nella cartella di AMS e compilare, come utente normale:" + term(
        "admin@server:~/AMS$ make"),
    "Lanciare l'installazione: lo script si rilancia da solo con sudo e chiede la password." + term(
        "admin@server:~/AMS$ ./install.sh\n"
        "[sudo] password di admin:\n"
        "AMS installato. Comando: /usr/local/bin/ams (utilizzabile dal gruppo sudo).\n"
        "Manuali: /usr/local/share/doc/ams/AMS_Manuale_Utente.html e AMS_Manuale_Tecnico.html\n"
        "Le sessioni già aperte ricevono i messaggi sul terminale subito e la domanda\n"
        "di conferma dalla prossima shell o dal prossimo login."),
    "Controllare che il comando risponda:" + term("admin@server:~$ ams version\n"
                                                  "AMS - Advanced Messaging System for linux 0.2.0"),
]) + tip("se " + c("make") + " non è stato lanciato, o se i programmi erano stati compilati per altre cartelle, "
         + c("install.sh") + " compila da solo. Se la compilazione non riesce scrive «Compilazione non riuscita: "
         "servono gcc, make, pkg-config, libsystemd-dev e gettext».", "Compilazione automatica.") + \
    note("gli utenti già collegati ricevono subito i messaggi, anche sul desktop. La domanda di conferma nel "
         "terminale arriva invece dalla prossima finestra di terminale che aprono: quelle già aperte non hanno ancora "
         "caricato AMS.", "Utenti già collegati.")

ALBERO = tree([
    "/usr/local/bin/ams  # il comando degli amministratori (root:sudo, 750)",
    "/usr/local/lib/ams/  # le parti interne",
    "├── ams-user  # mostra i messaggi e registra le conferme, come l'utente",
    "├── ams.bash  # aggancio di bash",
    "└── ams.zsh  # aggancio di zsh",
    "/usr/local/share/locale/it/LC_MESSAGES/ams.mo  # la traduzione italiana",
    "/usr/local/share/doc/ams/  # questo manuale e il manuale tecnico",
    "/etc/ams/ams.conf  # le impostazioni (non sovrascritte da un aggiornamento)",
    "/etc/profile.d/ams.sh  # aggancio delle shell al login",
    "/etc/fish/conf.d/ams.fish  # aggancio di fish",
    "/etc/xdg/autostart/ams-agent.desktop  # avvio automatico sul desktop",
    "/var/lib/ams/  # i messaggi e le conferme",
    "├── sent/  # le copie di riferimento (solo root)",
    "└── users/  # una casella per utente",
], "«FIG» — I file installati da install.sh")

S3 = p("L'installazione mette ogni cosa nei posti abituali di Linux. Oltre a questi file aggiunge una riga, marcata "
       + c("# AMS hook") + ", in fondo a " + c("/etc/bash.bashrc") + " e, se zsh è installata, allo zshrc di "
       "sistema: è ciò che fa comparire la domanda nei terminali del desktop.", lead=True) + ALBERO + \
    table(["Dove", "Che cos'è", "Chi lo usa"], [
        [c("/usr/local/bin/ams"), "Il comando. Solo il gruppo degli amministratori può eseguirlo.", "amministratori"],
        [c("/usr/local/lib/ams/ams-user"), "L'aiutante che mostra i messaggi e registra le conferme. Non è un "
         "comando: gli utenti non lo lanciano mai, parte da solo.", "shell e desktop degli utenti"],
        [c("/etc/ams/ams.conf"), "Le impostazioni (" + rif(10) + ").", "tutti, in lettura"],
        [c("/var/lib/ams/"), "I messaggi, le caselle degli utenti, le conferme.", "AMS"],
        [c("/etc/xdg/autostart/ams-agent.desktop"), "Avvia l'agente del desktop a ogni accesso grafico.",
         "il desktop degli utenti"],
    ], "«TAB» — Cosa viene installato")

S4 = p("Il comando " + c("ams") + " appartiene a root e al gruppo degli amministratori che la macchina ha già: "
       + c("sudo") + " su Debian e Ubuntu, " + c("wheel") + " su Fedora e simili (in mancanza, " + c("admin") + " o "
       + c("root") + "). AMS non ha un suo elenco di amministratori.", lead=True) + \
    term("admin@server:~$ stat -c '%U:%G %a %n' /usr/local/bin/ams\n"
         "root:sudo 750 /usr/local/bin/ams", "Il comando e i suoi permessi: root e il gruppo sudo, nessun altro") + \
    table(["Per", "Comando", "Quando vale"], [
        ["dare l'accesso ad AMS", c("sudo usermod -aG sudo anna"), "dal prossimo accesso di anna"],
        ["toglierlo", c("sudo gpasswd -d anna sudo"), "dal prossimo accesso di anna"],
        ["sapere chi può usarlo", c("getent group sudo"), "subito"],
    ], "«TAB» — Gestire gli amministratori") + \
    warn("entrare nel gruppo " + c("sudo") + " vuol dire poter diventare root su tutta la macchina, non solo usare "
         "AMS. È voluto: mandare messaggi a tutti gli utenti è un compito da amministratore.", "Un solo gruppo.")

S5 = p("Subito dopo l'installazione conviene fare tre prove, tutte senza disturbare nessuno.", lead=True) + steps([
    "Aprire la guida integrata: " + c("ams --help") + " (" + rif(9) + "). Si esce con " + c("q") + ".",
    "Controllare l'elenco dei messaggi: è vuoto, perché non è ancora partito nulla." + term(
        "admin@server:~$ ams list\nNessun messaggio inviato."),
    "Aprire la TUI scrivendo " + c("ams") + " da solo: mostra «Nessun messaggio inviato.» e i tasti in basso. Si "
    "esce con " + c("q") + ".",
    "Per una prova completa mandare un messaggio a se stessi, come nel " + rif(4) + ".",
]) + tip("un messaggio mandato a se stessi mostra in pochi secondi tutto quello che vedranno gli utenti: il testo "
         "nel terminale, la domanda al prompt, la finestra sul desktop.", "Prova su di sé.")

S6 = table(["Per", "Comando", "Cosa succede"], [
    ["Aggiornare", c("./install.sh") + " dalla cartella della versione nuova",
     "Installa la versione nuova; messaggi e impostazioni restano. Gli agenti del desktop della versione precedente "
     "vengono chiusi: ne parte uno nuovo al primo messaggio o al prossimo accesso."],
    ["Rimuovere AMS", c("./install.sh --uninstall"), "Toglie comando, agganci, manuali e traduzioni; messaggi "
     "(" + c("/var/lib/ams") + ") e impostazioni (" + c("/etc/ams") + ") restano, per un'eventuale reinstallazione."],
    ["Rimuovere tutto", c("./install.sh --purge"), "Come sopra, e in più cancella i messaggi e le impostazioni."],
], "«TAB» — Aggiornare e rimuovere") + \
    term("admin@server:~/AMS$ ./install.sh --uninstall\n"
         "AMS rimosso. Messaggi (/var/lib/ams) e configurazione (/etc/ams) conservati.", "Rimozione") + \
    warn(c("--purge") + " cancella anche l'elenco di chi ha confermato cosa. Se serve conservarlo, prima si copia "
         + c("/var/lib/ams") + " altrove. Gli eventi restano comunque nel registro di sistema.",
         "Prima di --purge.")

CHAPTER = ("Installazione e primo avvio", [
    ("Requisiti", S1),
    ("Compilare e installare", S2),
    ("Cosa viene installato", S3),
    ("Gli amministratori", S4),
    ("Primo avvio", S5),
    ("Aggiornare e rimuovere", S6),
])
