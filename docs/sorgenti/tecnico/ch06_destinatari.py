from build import arrow, box, c, fig, note, p, path, table, text, ul, zone


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">capitolo {n}{"." + str(s) if s else ""}</a>'


RISOLVI = fig(
    box(20, 110, 180, 56, "--to DEST", "mario,@sviluppo,online", "dark")
    + box(250, 110, 130, 56, "strtok_r", "divide sulle virgole", "navy")
    + box(440, 20, 200, 44, "all", "utenti_umani", "blue", 12)
    + box(440, 74, 200, 44, "online", "utenti_online", "blue", 12)
    + box(440, 128, 200, 44, "@gruppo", "membri_gruppo", "blue", 12)
    + box(440, 182, 200, 44, "nome", "getpwnam: deve esistere", "blue", 12)
    + box(700, 110, 180, 56, "elenco", "senza doppioni, in ordine", "green")
    + arrow(202, 138, 248, 138)
    + arrow(382, 130, 438, 42) + arrow(382, 134, 438, 96) + arrow(382, 142, 438, 150) + arrow(382, 146, 438, 204)
    + arrow(642, 42, 698, 128) + arrow(642, 96, 698, 134) + arrow(642, 150, 698, 142) + arrow(642, 204, 698, 150)
    + text(540, 250, "gruppo o utente inesistente: die, nessun messaggio creato", 11, "#b91c1c", "600"),
    900, 266, "«FIG» — Da --to all'elenco dei destinatari (risolvi_destinatari)", "Risolvere i destinatari")

S1 = p(c("risolvi_destinatari") + " di " + c("src/ams.c") + " trasforma il valore di " + c("--to") + " nell'elenco "
       "dei destinatari. Lo fa <b>prima</b> di prendere un numero e di scrivere qualunque cosa: un errore qui non lascia "
       "tracce nell'archivio.", lead=True) + RISOLVI + ul([
    "Il valore si divide sulle virgole; ogni parte è una delle quattro forme della figura. Le parti vuote (due "
    "virgole di fila) si saltano; uno spazio invece fa parte del nome, che quindi non esiste: per questo la guida "
    "chiede di separare con virgole senza spazi.",
    "Un utente o un gruppo inesistente termina con " + c("die") + " («utente inesistente: pippo», «gruppo "
    "inesistente: x»); per l'utente è lo scenario B6 della macchina di prova.",
    "I doppioni si tolgono man mano (scenario B2) e l'elenco finale è in ordine alfabetico: è l'ordine delle "
    "consegne e di " + c("sent/ID/recipients") + ".",
    "Un elenco vuoto (per esempio un gruppo senza membri) termina con «nessun destinatario» (scenario B7).",
    "Un nome esplicito può essere anche un account di sistema o root: il filtro degli utenti umani vale solo per "
    + c("all") + " e " + c("online") + ".",
])

S2 = table(["Funzione (src/sessioni.c)", "Cosa restituisce", "Fonte"], [
    [c("utenti_umani"), "gli utenti con UID fra " + c("UID_MIN") + " e " + c("UID_MAX") + " e una shell che non "
     "finisce con " + c("nologin") + " o " + c("false"), c("/etc/login.defs") + " (predefiniti 1000 e 60000), "
     + c("getpwent")],
    [c("utenti_online"), "gli utenti umani con almeno una sessione logind di classe " + c("user"),
     c("sd_get_sessions") + ", " + c("sd_session_get_class") + ", " + c("sd_session_get_uid")],
    [c("membri_gruppo G"), "i membri elencati nel gruppo più gli utenti che hanno G come gruppo principale; falso "
     "se il gruppo non esiste", c("getgrnam") + ", " + c("getpwent")],
    [c("terminali_utente U"), "gli pseudo-terminali di U e le console delle sue sessioni testuali", "vedi " + cap(6, 3)],
    [c("sessione_grafica U"), "vero se U ha una sessione di tipo " + c("x11") + " o " + c("wayland"),
     c("sd_session_get_type")],
], "«TAB» — Destinatari e sessioni") + \
    p("Tutto passa dalle interfacce del sistema (" + c("getpwent") + ", " + c("getgrnam") + ", la libreria "
      + c("sd-login") + " di libsystemd): utenti LDAP o di altri servizi di nomi funzionano se il sistema li espone "
      "così. " + c("all") + " esclude root e gli account di sistema perché hanno UID sotto " + c("UID_MIN")
      + " o una shell di non accesso (scenario B4).") + \
    note("<b>online</b> conta le sessioni di classe " + c("user") + " e poi filtra con gli utenti umani: la VM di "
         "prova ha mostrato che root e gli account di sistema collegati (per esempio il gestore del login grafico) "
         "finivano fra i destinatari (scenario B5). Ora restano esclusi anche se collegati.")

TERM = fig(
    zone(20, 44, 400, 200, "Pseudo-terminali · /dev/pts")
    + box(44, 84, 170, 56, "/dev/pts/N", "proprietario = U?", "blue")
    + box(230, 84, 170, 56, "ssh, emulatori", "tmux, terminali grafici", "soft", 12)
    + text(220, 180, "lstat: dispositivo a caratteri di U", 11, "#475569")
    + text(220, 198, "nomi fatti di sole cifre", 11, "#475569")
    + zone(480, 44, 400, 200, "Console · logind")
    + box(504, 84, 170, 56, "sessione di U", "tipo tty", "navy")
    + box(690, 84, 170, 56, "/dev/ttyN", "sd_session_get_tty", "blue")
    + text(680, 180, "solo nomi «tty» + cifre", 11, "#475569")
    + arrow(676, 112, 688, 112)
    + box(300, 262, 300, 48, "terminali_utente(U)", "senza doppioni, in ordine", "green", 12)
    + arrow(220, 216, 380, 260, "#16a34a") + arrow(680, 216, 520, 260, "#16a34a"),
    900, 326, "«FIG» — Le due fonti dei terminali di un utente", "Dove sono i terminali")

S3 = p(c("terminali_utente") + " raccoglie i terminali su cui " + c("ams send") + " scrive il testo all'invio. Le "
       "fonti sono due, perché nessuna delle due basta da sola.", lead=True) + TERM + table(["Fonte", "Che cosa trova",
                                                                                         "Che cosa non trova"], [
    [c("/dev/pts/N") + " di proprietà di U", "ssh con terminale, emulatori di terminale del desktop, tmux e screen",
     "le console di testo; i terminali aperti con " + c("su") + " (restano di chi li ha aperti)"],
    ["sessioni logind di U di tipo " + c("tty"), "le console di testo (" + c("tty1") + "…" + c("tty6") + ")",
     "gli pseudo-terminali che non sono una sessione (tmux, emulatori)"],
], "«TAB» — Le fonti dei terminali") + ul([
    "Il proprietario di " + c("/dev/pts/N") + " qui serve solo a <b>trovare</b> i candidati: al momento di scrivere, "
    + c("scrivi_terminale") + " riapre il terminale e controlla il proprietario del terminale aperto (" + cap(8, 4)
    + "). Il nome " + c("/dev/pts/N") + " non identifica una sessione: fra la ricerca e la scrittura potrebbe passare "
    "a un altro utente.",
    "In modalità di prova c'è un solo «terminale»: il file " + c("AMS_TEST_TTY") + ", se impostato.",
    "Una sessione ssh senza terminale (" + c("scp") + ", comandi remoti) e i servizi non hanno terminali: non vengono "
    "toccati (scenario C3).",
])

S4 = p(c("sessione_grafica") + " dice se un utente ha una sessione X11 o Wayland aperta. Serve in due punti, con "
       "lo stesso codice.", lead=True) + table(["Chi la chiama", "Perché"], [
    [c("ams send") + ", tramite " + c("sveglia_agente"), "solo chi ha un desktop aperto riceve la sveglia o un agente "
     "nuovo (" + cap(8, 5) + ")"],
    [c("ams-user agent"), "l'agente resta vivo finché l'utente ha una sessione grafica, poi esce (" + cap(12, 1) + ")"],
], "«TAB» — Chi usa sessione_grafica") + \
    p("Un utente con più sessioni grafiche (per esempio un desktop locale e uno remoto che crea una sessione nuova) "
      "ha comunque un solo agente: il lock " + c("ams-agent.lock") + " sta in " + c("$XDG_RUNTIME_DIR") + ", che è "
      "unico per utente (" + cap(12, 1) + "). Il comportamento con più desktop contemporanei dello stesso utente non "
      "è stato provato.")

CHAPTER = ("Destinatari e sessioni", [
    ("Da --to all'elenco", S1),
    ("Utenti umani, collegati, gruppi", S2),
    ("I terminali di un utente", S3),
    ("La sessione grafica", S4),
])
