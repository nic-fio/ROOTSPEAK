from build import arrow, box, c, code, file_map, fig, flow, note, p, steps, table, text, tree, warn


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">capitolo {n}{"." + str(s) if s else ""}</a>'


ALBERO = tree([
    "AMS/",
    "├── src/                  # il codice in C: due programmi, parti comuni",
    "├── po/                   # testi da tradurre (ams.pot) e traduzioni (it.po)",
    "├── etc/                  # agganci delle shell, avvio automatico, configurazione",
    "├── install.sh            # installazione, aggiornamento, rimozione",
    "├── Makefile              # compilazione, prove, analisi, sanitizer, testi",
    "├── docs/                 # i due manuali generati, decisioni, revisioni",
    "│   └── sorgenti/         # generatore, stile, un file per capitolo",
    "├── tests/                # motore, TUI, guida, unità, fuzzing, container, VM",
    "│   └── */risultati/      # esiti registrati con commit e impronta",
    "└── tools/                # coerenza dei manuali, impronta, schermate",
], "«FIG» — Le cartelle del repository")

S1 = p("Il repository contiene il codice in C, i cataloghi delle lingue, i file da installare nel sistema, i manuali "
       "con i loro sorgenti, le prove e i controlli di coerenza. La tabella che segue è la <b>mappa dei file</b>: "
       "le righe si contano a ogni generazione del manuale, e " + c("tools/check-docs.py") + " fallisce se un file "
       "di codice manca o se ne compare uno che non esiste.", lead=True) + ALBERO + file_map([
    ("src/ams.c", "Il comando degli amministratori: rilancio con sudo, destinatari, " + c("send") + ", " + c("list")
     + ", " + c("status") + ", " + c("revoke") + ", " + c("remind") + ", " + c("log") + ", " + c("purge")
     + ", riassunto dei messaggi, recupero."),
    ("src/ams.h", "Le parti di ams usate anche dalla TUI: stati dei destinatari, riassunto, comandi."),
    ("src/tui.c", "La TUI per gli amministratori: lista, dettaglio e storia, scrittura e invio, azioni con conferma."),
    ("src/guida.c", "La guida integrata: guida a schede, pagina in stile manuale, testo semplice."),
    ("src/guida.h", "Interfaccia di guida.c."),
    ("src/archivio.c", "Le operazioni sulle caselle, sempre con l'identità dell'utente; scrittura nei terminali; "
     "lingua dei terminali; sveglia dell'agente."),
    ("src/archivio.h", "Interfaccia di archivio.c."),
    ("src/ams-user.c", "L'aiutante che gira come utente: " + c("prompt") + " (aggancio della shell), " + c("agent")
     + " (desktop), registrazione delle conferme."),
    ("src/utente.c", c("come_utente") + ": un processo figlio con l'identità di un utente e un tempo massimo."),
    ("src/utente.h", "Interfaccia di utente.c."),
    ("src/sessioni.c", "Utenti umani, gruppi, sessioni e terminali, da passwd, group e logind."),
    ("src/sessioni.h", "Interfaccia di sessioni.c."),
    ("src/testo.c", "Pulizia del testo, formato dei messaggi, configurazione."),
    ("src/testo.h", "Interfaccia di testo.c: " + c("msg_t") + ", " + c("conf_t") + "."),
    ("src/lingua.c", "Scelta della lingua e lettore dei cataloghi .mo."),
    ("src/lingua.h", "Interfaccia di lingua.c: " + c("T") + ", " + c("TC") + ", " + c("tl") + ", " + c("tlc") + "."),
    ("src/evento.c", "Eventi strutturati nel journal e il loro testo in ogni lingua."),
    ("src/evento.h", "Interfaccia di evento.c."),
    ("src/comune.c", "Utilità: ambiente, errori, memoria, testi che crescono, lettura e scrittura sicura dei file."),
    ("src/comune.h", "Interfaccia di comune.c, versione (" + c("AMS_VERSION") + ") e limiti."),
    ("po/ams.pot", "I testi da tradurre, estratti dai sorgenti (" + c("make pot") + ")."),
    ("po/it.po", "La traduzione italiana; fonte anche del riferimento del manuale utente."),
    ("Makefile", "Compilazione, prove interne, analisi statica, sanitizer, estrazione dei testi."),
    ("install.sh", "Installazione, aggiornamento, rimozione."),
    ("etc/profile.d/ams.sh", "L'aggancio delle shell che leggono " + c("/etc/profile") + ", in sh semplice: rimanda "
     "bash ad " + c("ams.bash") + ", alle altre (tranne zsh) chiede al login."),
    ("etc/ams.bash", "L'aggancio a bash: la domanda al login e a ogni prompt."),
    ("etc/ams.zsh", "L'aggancio a zsh, richiamato dallo zshrc di sistema."),
    ("etc/ams.fish", "L'aggancio a fish, installato in " + c("/etc/fish/conf.d") + "."),
    ("etc/xdg/autostart/ams-agent.desktop", "Avvio automatico dell'agente del desktop."),
    ("etc/ams/ams.conf", "La configurazione predefinita."),
    ("tests/engine.sh", "Prove del motore in modalità di prova: conferme, consegna, stati, scadenza, configurazione, "
     "pulizia, agente, lingue, seconda revisione, sollecito."),
    ("tests/prove-unita.c", "Prove delle parti interne: pulizia, lingue, messaggi, configurazione, eventi."),
    ("tests/tui.py", "Prova della TUI su un terminale virtuale: lista, dettaglio, invio, editor, sollecito, ritiro, "
     "ricerca, dimensioni."),
    ("tests/help-tui.py", "Prova della guida integrata su un terminale virtuale."),
    ("tests/fuzz/fuzz.c", "Fuzzing con libFuzzer di ciò che legge dati non fidati (sei bersagli)."),
    ("tests/fuzz/esegui.sh", "Compila e lancia il fuzzing in un container con clang."),
    ("tests/container/Containerfile", "La macchina di prova: Debian 13 con systemd, sshd, utenti e shell diverse."),
    ("tests/container/esegui.sh", "Avvia la macchina di prova, installa AMS, esegue gli scenari, salva i risultati."),
    ("tests/container/scenari.py", "Gli scenari dal vero, eseguiti come root nella macchina di prova (anche nella "
     "VM, con quelli del desktop)."),
    ("tests/vm/esegui.sh", "Prove nella VM con desktop sul server delle prove: codice, VM pulita, scenari, "
     "schermate, risultati."),
    ("tests/vm/prepara.sh", "Costruisce una volta il disco base della VM (Debian 13, GNOME, utenti)."),
    ("tests/vm/user-data.tpl", "La configurazione cloud-init della VM: pacchetti, utenti, login automatico, "
     "accessibilità."),
    ("tests/vm/avvia.sh", "Avvia la VM da una copia pulita del disco base."),
    ("tests/vm/ferma.sh", "Spegne la VM e cancella il disco di lavoro."),
    ("tests/vm/cattura.py", "Cattura lo schermo della VM dal monitor di QEMU."),
    ("tests/vm/desktop.py", "Legge e preme i pulsanti delle finestre di AMS attraverso l'accessibilità di GNOME."),
    ("tools/check-docs.py", "Controlli di coerenza tra codice, guida, traduzioni, manuali e prove."),
    ("tools/impronta.sh", "Impronta del codice (SHA-256 di src, po, Makefile, etc, install.sh) e commit, registrati "
     "con i risultati delle prove."),
    ("tools/schermate-tui.sh", "Schermate vere della TUI per i manuali, catturate nella macchina di prova."),
    ("docs/sorgenti/build.py", "Generatore dei due manuali e funzioni per figure e tabelle."),
    ("docs/sorgenti/stile.css", "Lo stile dei manuali, quello di IR_Service."),
], "«TAB» — Mappa dei file") + \
    p("I capitoli dei manuali stanno in " + c("docs/sorgenti/utente/") + " e " + c("docs/sorgenti/tecnico/")
      + ", un file per capitolo; " + c("docs/decisioni-e-storia.md") + " e " + c("CLAUDE.md") + " raccolgono le "
      "decisioni e gli accordi di lavoro, " + c("docs/revisione-avversariale.md") + " le due revisioni esterne. Il "
      "prototipo in bash (versione 0.1.0) è nella storia del repository.")

MAKE = fig(
    box(20, 40, 170, 56, "make", "ams, ams-user, .mo", "navy")
    + box(20, 116, 170, 56, "make prove", "build/prove-unita", "blue")
    + box(20, 192, 170, 56, "make pot", "xgettext, msgmerge", "soft")
    + box(250, 40, 190, 56, "build/", "PIE, RELRO, avvisi = errori", "dark")
    + box(250, 116, 190, 56, "make sanitizer", "build-san/ · ASan, UBSan", "amber")
    + box(250, 192, 190, 56, "make analizza", "build-analisi/ · -fanalyzer", "amber")
    + box(500, 40, 180, 56, "install.sh", "installa da build/", "navy")
    + box(500, 116, 180, 56, "tests/engine.sh", "AMS_BUILD=build-san", "green")
    + box(740, 40, 140, 56, "sistema", "/usr/local", "light")
    + box(740, 116, 140, 56, "risultati", "engine.json", "light")
    + arrow(192, 68, 248, 68) + arrow(442, 68, 498, 68) + arrow(682, 68, 738, 68)
    + arrow(442, 144, 498, 144, "#d97706") + arrow(682, 144, 738, 144, "#16a34a"),
    900, 268, "«FIG» — I bersagli del Makefile e dove portano", "Compilare")

S2 = p("La compilazione è un Makefile senza strumenti esterni oltre a gcc, pkg-config (per libsystemd) e gettext. "
       "Tutto finisce in " + c("build/") + " (o in una cartella scelta con " + c("B=") + "); le cartelle "
       "d'installazione sono scritte nel programma con " + c("-DLIBDIR") + " e " + c("-DLOCALEDIR") + ".",
       lead=True) + MAKE + table(["Bersaglio", "Cosa fa"], [
    [c("make"), "compila " + c("build/ams") + ", " + c("build/ams-user") + " e un " + c("ams.mo") + " per ogni "
     + c("po/*.po") + " (con " + c("msgfmt --check") + ")"],
    [c("make prove"), "compila ed esegue " + c("build/prove-unita") + " in modalità di prova"],
    [c("make analizza"), "ricompila tutto in " + c("build-analisi/") + " con " + c("-fanalyzer")],
    [c("make sanitizer"), "ricompila in " + c("build-san/") + " con AddressSanitizer e UBSan, più "
     + c("prove-unita") + "; poi " + c("AMS_BUILD=build-san tests/engine.sh")],
    [c("make pot"), "estrae i testi in " + c("po/ams.pot") + " e aggiorna i " + c(".po") + " con " + c("msgmerge")],
    [c("make clean"), "toglie " + c("build") + ", " + c("build-analisi") + " e " + c("build-san")],
], "«TAB» — I bersagli del Makefile") + code("""AVVISI = -Wall -Wextra -Wpedantic -Wformat=2 -Wformat-security -Wshadow -Wpointer-arith \\
         -Wcast-qual -Wwrite-strings -Wstrict-prototypes -Wmissing-prototypes -Wvla \\
         -Wnull-dereference -Wimplicit-fallthrough -Wundef -Werror
DIFESE = -D_FORTIFY_SOURCE=3 -fstack-protector-strong -fstack-clash-protection -fcf-protection -fPIE
LDFLAGS += -pie -Wl,-z,relro,-z,now -Wl,-z,noexecstack""", "text", "Makefile (estratto)") + \
    p("Gli avvisi sono errori (" + c("-Werror") + "): il codice non compila se gcc trova qualcosa da ridire. Il "
      "significato di ogni difesa è nel " + cap(17, 3) + ".")

S3 = flow([("Compilazione", "make, se serve", "dark"), ("Programmi", "ams 750 · ams-user", "blue"),
           ("Lingue, agganci", "locale/, etc/", "blue"), ("/var/lib/ams", "users 755 · sent 700", "blue"),
           ("Agenti", "chiusi e riavviati", "navy")], "«FIG» — Le tappe di install.sh") + steps([
    "Si rilancia con " + c("sudo") + " se non è root, e sceglie il gruppo degli amministratori: il primo esistente "
    "fra " + c("sudo") + ", " + c("wheel") + ", " + c("admin") + " (altrimenti " + c("root") + "). Avvisa se mancano "
    + c("zenity") + ", " + c("loginctl") + " o " + c("systemd-run") + ".",
    "Se in " + c("build/") + " mancano i programmi, o sono stati compilati per altre cartelle (il percorso di "
    + c("LIBDIR") + " non compare dentro " + c("build/ams") + "), li compila con " + c("make PREFIX=…")
    + " (servono gcc, make, pkg-config, libsystemd-dev e gettext).",
    "Installa " + c("$PREFIX/lib/ams/ams-user") + " (" + c("755") + "), i cataloghi in "
    + c("$PREFIX/share/locale/LINGUA/LC_MESSAGES/ams.mo") + " e " + c("$PREFIX/bin/ams") + " con proprietario "
    + c("root:gruppo") + " e permessi " + c("750") + "; toglie i file del prototipo in bash e un vecchio "
    + c("sbin/ams") + ". " + c("PREFIX") + " vale " + c("/usr/local") + ".",
    "Installa i manuali in " + c("$PREFIX/share/doc/ams/") + ", la configurazione (solo se manca), gli agganci delle "
    "shell e l'avvio automatico, sostituendo " + c("@LIBDIR@") + " e " + c("@VARDIR@") + ".",
    "Aggiunge a " + c("/etc/bash.bashrc") + " la riga marcata " + c("# AMS hook") + " (su Debian le shell interattive "
    "non di login non leggono " + c("/etc/profile.d") + "); se lo zshrc di sistema esiste, vi aggiunge il richiamo "
    "di " + c("ams.zsh") + "; per fish scrive " + c("/etc/fish/conf.d/ams.fish") + ".",
    "Crea " + c("/var/lib/ams") + " e " + c("users/") + " (" + c("755") + ") e " + c("sent/") + " (" + c("700") + ").",
    "Chiude gli agenti della versione precedente (anche quelli in bash): ripartono aggiornati al primo invio o al "
    "login.",
]) + table(["Opzione", "Effetto"], [
    ["nessuna", "installa o aggiorna"],
    [c("--uninstall"), "toglie programmi, cataloghi, manuali, agganci e righe marcate di " + c("bash.bashrc")
     + " e dello zshrc, ferma gli agenti; conserva messaggi e configurazione"],
    [c("--purge"), "come " + c("--uninstall") + ", e toglie anche " + c("/var/lib/ams") + " e " + c("/etc/ams")],
], "«TAB» — Le modalità di install.sh")

S4 = table(["Percorso", "Proprietario", "Permessi", "Contenuto"], [
    [c("/usr/local/bin/ams"), "root:sudo (o wheel, admin)", c("750"), "il comando degli amministratori"],
    [c("/usr/local/lib/ams/ams-user"), "root", c("755"), "l'aiutante, fuori dal PATH"],
    [c("/usr/local/lib/ams/ams.bash") + ", " + c("ams.zsh"), "root", c("644"), "gli agganci di bash e zsh"],
    [c("/usr/local/share/locale/*/LC_MESSAGES/ams.mo"), "root", c("644"), "i cataloghi delle lingue"],
    [c("/usr/local/share/doc/ams/"), "root", c("644"), "i due manuali HTML"],
    [c("/etc/ams/ams.conf"), "root", c("644"), "la configurazione (non sovrascritta)"],
    [c("/etc/profile.d/ams.sh"), "root", c("644"), "l'aggancio per le shell che leggono " + c("/etc/profile")],
    [c("/etc/fish/conf.d/ams.fish"), "root", c("644"), "l'aggancio di fish"],
    [c("/etc/xdg/autostart/ams-agent.desktop"), "root", c("644"), "l'avvio automatico dell'agente"],
    [c("/etc/bash.bashrc") + ", zshrc", "—", "—", "una riga marcata " + c("# AMS hook")],
    [c("/var/lib/ams/"), "root", c("755") + " (" + c("sent/") + " " + c("700") + ")", "l'archivio (" + cap(5) + ")"],
], "«TAB» — Che cosa installa install.sh, e dove") + \
    note("gli utenti non hanno un comando: " + c("ams-user") + " non è nel PATH e, lanciato a mano senza "
         + c("prompt") + " o " + c("agent") + ", risponde che è un aiutante interno ed esce con 1.")

S5 = steps([
    c("make") + " (tutti gli avvisi sono errori) e " + c("make prove") + ".",
    c("make pot") + " se sono cambiati testi da tradurre, poi la traduzione in " + c("po/it.po") + ".",
    c("python3 docs/sorgenti/build.py") + ", poi " + c("tools/check-docs.py") + ": manuali generati aggiornati, "
    "riferimento allineato alla guida, cataloghi completi, mappa dei file completa, link interni validi, prove "
    "eseguite sul codice attuale (" + cap(21, 5) + ").",
    c("tests/engine.sh") + " sempre; " + c("tests/help-tui.py") + " se è cambiata la guida; " + c("tests/tui.py")
    + " e " + c("tools/schermate-tui.sh") + " se è cambiata la TUI; " + c("make sanitizer") + " con "
    + c("AMS_BUILD=build-san tests/engine.sh") + ", " + c("make analizza") + " e " + c("tests/fuzz/esegui.sh")
    + " se è cambiato il codice che legge dati; " + c("tests/container/esegui.sh") + " se sono cambiati invio, "
    "consegna, conferme o permessi; " + c("tests/vm/esegui.sh") + " se è cambiato il desktop.",
    "Una prova del flusso toccato in modalità di prova (" + cap(4, 4) + "); per desktop, sudo e altri utenti, una "
    "prova dal vivo dopo " + c("./install.sh") + ", fatta da chi ha la password di root.",
]) + warn("i risultati delle prove si registrano insieme alla modifica: ogni suite scrive il suo esito con il "
          "commit e l'impronta del codice, e il " + cap(21) + " li mostra accanto all'impronta attuale.")

CHAPTER = ("Repository, compilazione e installazione", [
    ("Mappa dei file", S1),
    ("La compilazione: il Makefile", S2),
    ("install.sh passo per passo", S3),
    ("Che cosa installa, e dove", S4),
    ("Prima di registrare una modifica", S5),
])
