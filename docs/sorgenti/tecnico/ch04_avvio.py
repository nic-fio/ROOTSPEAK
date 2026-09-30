from build import arrow, box, c, code, diamond, dl, fig, note, p, path, table, term, text, ul, warn


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">capitolo {n}{"." + str(s) if s else ""}</a>'


AVVIO = fig(
    box(20, 40, 170, 56, "ams_init", "ambiente, AMS_TEST", "dark")
    + box(20, 120, 170, 56, "lingua_init", "LANG, LANGUAGE…", "dark")
    + diamond(330, 148, 220, 76, "root o AMS_TEST?", "navy")
    + box(250, 232, 160, 50, "execvp sudo", "sudo -- /proc/self/exe", "grey")
    + diamond(600, 148, 200, 76, "nessun argomento?", "navy")
    + box(520, 232, 160, 50, "recupera, TUI", "stdin e stdout tty", "blue")
    + box(720, 40, 160, 50, "guida, versione", "help, --help, version", "light")
    + box(720, 120, 160, 56, "comando", "recupera, poi il comando", "blue")
    + box(720, 232, 160, 50, "die", "«ams: comando sconosciuto»", "amber")
    + arrow(105, 98, 105, 118) + path([(192, 148), (218, 148)], "#0050C0")
    + arrow(330, 188, 330, 230, "#475569", False, "no", 346, 212)
    + arrow(442, 148, 498, 148, "#0050C0", False, "sì", 470, 138)
    + arrow(600, 188, 600, 230, "#0050C0", False, "sì", 616, 212)
    + path([(700, 148), (710, 148), (710, 65), (718, 65)], "#0050C0")
    + arrow(700, 148, 718, 148, "#0050C0")
    + path([(700, 160), (706, 160), (706, 257), (718, 257)], "#b45309", True)
    + text(160, 250, "si rilancia uguale", 11, "#475569"),
    900, 300, "«FIG» — L'avvio di ams: ambiente, lingua, root, poi il comando", "L'avvio di ams")

S1 = p("Il " + c("main") + " di " + c("src/ams.c") + " è breve e il suo ordine è una regola: <b>nulla gira senza "
       "root</b>, nemmeno la guida. Prima di guardare gli argomenti legge l'ambiente e la lingua; poi, se non è root "
       "e non è in modalità di prova, si rilancia con sudo.", lead=True) + AVVIO + code("""int main(int argc, char **argv)
{
	const char *cmd = argc > 1 ? argv[1] : "";

	ams_init("ams");
	lingua_init();
	if (geteuid() != 0 && !ams_test)       /* anche per la guida e la versione */
		rilancia_con_sudo(argv);           /* execvp("sudo", "--", /proc/self/exe, …) */
	umask(022);
	if (!*cmd && isatty(0) && isatty(1)) { /* ams da solo in un terminale */
		recupera();
		if (ams_tui())
			return 0;                      /* terminale troppo piccolo: la guida */
	}
	if (!*cmd || !strcmp(cmd, "help") || !strcmp(cmd, "-h") || !strcmp(cmd, "--help"))
		{ ams_guida(); return 0; }
	if (!strcmp(cmd, "version") || !strcmp(cmd, "--version")) { … }
	/* comando sconosciuto: die(); purge escluso, prima di ogni comando: recupera() */
	…
}""", "c", "src/ams.c (in breve)") + ul([
    c("rilancia_con_sudo") + " legge il proprio percorso da " + c("/proc/self/exe") + " e chiama "
    + c("execvp(\"sudo\", [\"sudo\", \"--\", percorso, argomenti…])") + ": gli argomenti arrivano identici, e "
    + c("--") + " impedisce che vengano presi per opzioni di sudo.",
    "Sotto sudo l'ambiente è quello che sudo conserva: di solito " + c("LANG") + " e le variabili di lingua sì, "
    + c("AMS_TEST") + " no. " + c("SUDO_USER") + " dice chi ha lanciato il comando: diventa il mittente ("
    + c("from") + ") e l'autore degli eventi.",
    "Il recupero degli invii interrotti (" + cap(8, 6) + ") gira prima di " + c("send") + ", " + c("list") + ", "
    + c("status") + ", " + c("revoke") + ", " + c("remind") + ", " + c("log") + " e della TUI; non prima di "
    + c("purge") + ", che salta da sé gli invii incompleti.",
    "Un comando sconosciuto termina con " + c("die") + ": " + c("ams: comando sconosciuto: X (ams --help per la guida)")
    + ", uscita 1.",
])

S2 = p(c("ams-user") + " non si rilancia mai: gira con l'identità di chi lo lancia, cioè dell'utente. Il suo "
       + c("main") + " ha un ordine diverso, dettato dall'agente del desktop.", lead=True) + table(
    ["Passo", "Perché"], [
        ["1. gestore di " + c("SIGUSR1"), "è la <b>prima istruzione</b>: " + c("SIGUSR1") + " per difetto termina il "
         "processo, e " + c("ams send") + " potrebbe mandarlo a un agente appena partito (" + cap(12, 2) + ")"],
        ["2. " + c("ams_init(\"ams-user\")") + ", " + c("lingua_init") + ", " + c("conf_leggi"),
         "ambiente, lingua dell'utente, configurazione"],
        ["3. utente da " + c("getuid") + " e " + c("getpwuid"), "la casella è " + c("users/<nome>") + ": il nome non "
         "viene mai da un argomento"],
        ["4. " + c("prompt [--login]"), "la domanda nel terminale (" + cap(11) + ")"],
        ["5. " + c("agent"), "l'agente del desktop (" + cap(12) + ")"],
        ["6. " + c("conferma ID CANALE"), "solo in modalità di prova: la registrazione della conferma da sola, per "
         + c("tests/engine.sh")],
        ["altrimenti", "«ams-user: helper interno di AMS, non va usato direttamente», uscita 1"],
    ], "«TAB» — L'avvio di ams-user")

S3 = p(c("ams_init") + " di " + c("src/comune.c") + " imposta le cartelle di lavoro. I valori predefiniti sono "
       "scritti nel programma; le variabili d'ambiente contano <b>solo in modalità di prova</b>: un programma di root "
       "non prende cartelle dall'ambiente di chi lo lancia.", lead=True) + table(
    ["Variabile globale", "Predefinito", "In modalità di prova"], [
        [c("ams_var"), c("/var/lib/ams"), c("AMS_VAR")],
        [c("ams_libdir"), c("LIBDIR") + " del Makefile (" + c("/usr/local/lib/ams") + ")", c("AMS_LIB")],
        [c("ams_localedir"), c("LOCALEDIR") + " (" + c("/usr/local/share/locale") + ")", c("AMS_LOCALEDIR")],
        [c("ams_conf_path"), c("/etc/ams/ams.conf"), c("AMS_CONF")],
        [c("ams_test"), "falso", "vero se " + c("AMS_TEST") + " non è vuota"],
        [c("ams_nome"), "—", c("\"ams\"") + " o " + c("\"ams-user\"") + ": il prefisso dei messaggi d'errore"],
    ], "«TAB» — L'ambiente di AMS") + dl([
    ("AMS_TEST=1", c("ams") + " non si rilancia con sudo, non sveglia né avvia agenti, non cambia identità nei "
     "processi figli e scrive solo nel «terminale» " + c("AMS_TEST_TTY") + ". Un utente normale che la imposta "
     "resta con i suoi permessi (scenario G4: «Permesso negato» già all'esecuzione di " + c("ams") + "), e sudo "
     "la toglie dall'ambiente."),
    ("AMS_TEST_TTY=file", "il «terminale» su cui " + c("ams send") + " scrive in modalità di prova; vuota: nessuno."),
    ("AMS_BUILD=cartella", "per le prove: i programmi da provare (per esempio " + c("build-san") + ")."),
])

S4 = p("Il codice si prova dalla cartella del repository come utente normale, su un archivio di prova, dopo "
       + c("make") + ". È il modo in cui girano " + c("tests/engine.sh") + ", " + c("tests/tui.py") + " e "
       + c("tests/help-tui.py") + ".", lead=True) + term(
    "nicfio@server:~/AMS$ make\n"
    "nicfio@server:~/AMS$ export AMS_TEST=1 AMS_LIB=$PWD/build AMS_LOCALEDIR=$PWD/build/locale\n"
    "nicfio@server:~/AMS$ export AMS_VAR=/tmp/prova AMS_CONF=/dev/null AMS_TEST_TTY=/tmp/tty\n"
    "nicfio@server:~/AMS$ build/ams send --to nicfio \"Prova\"\n"
    "Messaggio 1 inviato a 1 utente.\n"
    "nicfio@server:~/AMS$ script -qec 'build/ams-user prompt' /dev/null", "Una prova senza root") + \
    warn("senza " + c("AMS_TEST") + ", " + c("build/ams") + " passa da sudo; se le credenziali di sudo sono ancora "
         "valide parte come root senza chiedere nulla, sull'archivio vero. Nelle prove impostare sempre la "
         "modalità di prova.") + \
    note("in modalità di prova i destinatari sono utenti veri della macchina (" + c("getpwnam") + "), ma le loro "
         "caselle sono cartelle dell'archivio di prova scritte con l'identità di chi lancia la prova: "
         + c("tests/engine.sh") + " usa come secondo destinatario " + c("root") + ".")

CONF = fig(
    box(20, 50, 200, 60, "/etc/ams/ams.conf", "letto con leggi_file", "dark")
    + box(270, 50, 200, 60, "conf_da_testo", "riga per riga", "navy")
    + diamond(600, 80, 200, 70, "chiave nota?", "navy")
    + box(740, 50, 140, 60, "conf_t", "remind, poll", "green")
    + box(520, 160, 160, 48, "ignorata", "", "grey")
    + arrow(222, 80, 268, 80) + arrow(472, 80, 498, 80)
    + arrow(702, 80, 738, 80, "#16a34a", False, "sì", 720, 70)
    + arrow(600, 117, 600, 158, "#475569", False, "no", 616, 140)
    + text(370, 150, "commenti # e spazi tolti; al più 255 caratteri", 11, "#475569")
    + text(370, 168, "valore: solo cifre, al più 6, maggiore di zero", 11, "#475569"),
    900, 228, "«FIG» — Come si legge la configurazione", "Dati, non codice")

S5 = p("La configurazione è un file di <b>dati</b>, non uno script: nel prototipo in bash era letta con "
       + c("source") + ", da root e dagli utenti, e poteva eseguire codice. Ora " + c("conf_leggi") + " di "
       + c("src/testo.c") + " la legge al più per 65536 byte e " + c("conf_da_testo") + " accetta solo due chiavi, "
       "con interi positivi.", lead=True) + code("""# Dopo quanti minuti riproporre un messaggio rimandato dall'utente
AMS_REMIND_MINUTES=30

# Ogni quanti secondi l'agente del desktop ricontrolla i messaggi
# (i nuovi messaggi lo svegliano comunque subito)
AMS_AGENT_POLL=60""", "conf", "etc/ams/ams.conf") + CONF + table(["Chiave", "Predefinito", "Chi la usa", "Quando si rilegge"], [
    [c("AMS_REMIND_MINUTES"), "30", c("ams-user prompt") + " e l'agente: quanto vale un rinvio",
     "a ogni " + c("ams-user prompt") + "; a ogni giro dell'agente"],
    [c("AMS_AGENT_POLL"), "60", "l'agente: il controllo periodico, oltre alla sveglia", "a ogni giro dell'agente"],
], "«TAB» — Le chiavi della configurazione") + ul([
    "Ogni riga perde il commento (da " + c("#") + " in poi) e tutti gli spazi; una riga che resta più lunga di 255 "
    "caratteri non vale.",
    "Il valore deve essere fatto di sole cifre, al più 6, e maggiore di zero: " + c("0") + ", " + c("-3") + ", "
    + c("abc") + " e " + c("$(…)") + " sono ignorati e resta il predefinito (" + c("tests/engine.sh") + ", gruppo 5).",
    "Chiavi sconosciute sono ignorate; un file che manca, o che non è un file normale, vale come vuoto.",
    c("ams") + " stesso non legge la configurazione: le due chiavi riguardano solo ciò che fa " + c("ams-user") + ".",
])

CHAPTER = ("Avvio e configurazione", [
    ("L'avvio di ams", S1),
    ("L'avvio di ams-user", S2),
    ("L'ambiente e la modalità di prova", S3),
    ("Provare senza root", S4),
    ("La configurazione: ams.conf", S5),
])
