from build import arrow, box, c, code, fig, note, p, seq, table, term, text, ul


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">capitolo {n}{"." + str(s) if s else ""}</a>'


FLUSSO = fig(
    box(20, 40, 180, 56, "ams (root)", "invio, ritiro, sollecito…", "navy")
    + box(20, 130, 180, 56, "ams-user (U)", "rinvio, conferma", "blue")
    + box(260, 84, 180, 58, "evento()", "src/evento.c", "dark")
    + box(500, 40, 180, 56, "journal", "sd_journal_send", "green")
    + box(500, 130, 180, 56, "syslog", "se il journal manca", "soft")
    + box(740, 40, 140, 56, "journalctl", "-t ams", "light")
    + box(740, 130, 140, 56, "ams log ID", "e la storia della TUI", "light", 12)
    + arrow(202, 68, 258, 104) + arrow(202, 158, 258, 124)
    + arrow(442, 104, 498, 70) + arrow(442, 122, 498, 156, "#475569", True)
    + arrow(682, 68, 738, 68) + arrow(682, 80, 738, 150)
    + text(350, 218, "testo leggibile nella lingua del sistema, più i campi AMS_*; il journal aggiunge _UID", 11.5,
           "#475569", "600"),
    900, 236, "«FIG» — Dagli eventi al registro, e ritorno", "Il registro")

S1 = p("Ogni fatto rilevante della vita di un messaggio diventa un <b>evento strutturato</b> nel journal di sistema. "
       "Il registro risponde a una domanda diversa da quella di " + c("ams status") + ": non «a che punto è» ma «che "
       "cosa è successo, quando e per mano di chi».", lead=True) + FLUSSO + ul([
    c("evento(EVENTO, ID, UTENTE, CANALE, DETTAGLI, AUTORE)") + " di " + c("src/evento.c") + " scrive con "
    + c("sd_journal_send") + " un testo leggibile (" + c("MESSAGE") + ") e i campi strutturati. Se il journal non "
    "risponde, scrive almeno il testo con " + c("syslog") + ".",
    "Il testo leggibile è nella <b>lingua del sistema</b> (" + c("/etc/default/locale") + " o "
    + c("/etc/locale.conf") + "), uguale per tutti; " + c("ams log") + " lo riscrive dai campi nella lingua di chi "
    "legge (scenario L4).",
    "I dettagli stanno su una riga sola: gli a capo diventano spazi.",
    "Il registro è la <b>storia</b>, non lo stato: gli stati si deducono sempre dall'archivio, mai dal journal ("
    + cap(20, 1) + "). La conservazione degli eventi segue le regole del journal, non quelle di AMS: " + c("ams purge")
    + " non li tocca.",
])

S2 = table(["Campo", "Contenuto", "Chi lo mette"], [
    [c("SYSLOG_IDENTIFIER"), c("ams") + ", per tutti gli eventi, anche quelli di " + c("ams-user"), "AMS"],
    [c("MESSAGE"), "il testo leggibile, nella lingua del sistema", "AMS"],
    [c("PRIORITY"), "6 (informazione)", "AMS"],
    [c("AMS_EVENTO"), "il nome dell'evento: " + c("INVIATO") + ", " + c("CONFERMATO") + "…", "AMS"],
    [c("AMS_MESSAGGIO"), "il numero del messaggio", "AMS"],
    [c("AMS_UTENTE"), "il destinatario, dove serve", "AMS"],
    [c("AMS_CANALE"), c("terminale pts/N") + ", " + c("desktop") + "; per i rinvii " + c("terminale") + " o "
     + c("desktop"), "AMS"],
    [c("AMS_DETTAGLI"), "destinatari, terminali scritti, numero di sollecitati o recuperati, durata, errore", "AMS"],
    [c("AMS_AUTORE"), "l'amministratore (" + c("SUDO_USER") + ")", "AMS"],
    [c("_UID") + ", " + c("_PID") + ", ora", "chi ha scritto davvero l'evento, e quando", "il journal"],
], "«TAB» — I campi di un evento") + \
    p("Per un audit, " + c("journalctl AMS_MESSAGGIO=12 -o verbose") + " mostra tutti i campi, " + c("_UID")
      + " compreso; " + c("journalctl -t ams") + " il testo di tutti gli eventi di AMS.")

S3 = table(["Evento", "Chi lo scrive", "Quando", "Testo (italiano)"], [
    [c("INVIATO"), "ams (root)", "alla fine di " + c("ams send") + ", dopo le consegne",
     "messaggio 12 inviato da admin a: anna mario"],
    [c("CONSEGNATO"), "ams (root)", "per ogni copia scritta e verificata; anche dal recupero",
     "messaggio 12 consegnato a mario (terminali scritti: 1) · (recupero)"],
    [c("NON_CONSEGNATO"), "ams (root)", "copia non scritta", "messaggio 12: ERRORE, copia per anna non scritta"],
    [c("RECUPERATO"), "ams (root)", "recupero di un invio interrotto", "messaggio 12: consegna completata per 3 "
     "destinatari dopo un'interruzione"],
    [c("ANNULLATO"), "ams (root)", "recupero di un invio non salvato", "messaggio 12: invio interrotto prima del "
     "salvataggio, annullato"],
    [c("RITIRATO"), "ams (root)", c("ams revoke") + ", la prima volta", "messaggio 12 ritirato da admin"],
    [c("SOLLECITATO"), "ams (root)", c("ams remind"), "messaggio 12: sollecitati 3 destinatari da admin"],
    [c("CANCELLATO"), "ams (root)", c("ams purge") + ", alla rinomina", "messaggio 12 cancellato da admin (più "
     "vecchio di 90d)"],
    [c("RINVIATO"), "ams-user (U)", "«Più tardi» o risposta diversa da sì", "utente mario: rimandato il messaggio "
     "12 (terminale)"],
    [c("CONFERMATO"), "ams-user (U)", "conferma registrata", "utente mario: confermata la lettura del messaggio 12 "
     "(desktop)"],
    [c("CONFERMA_FALLITA"), "ams-user (U)", "conferma non registrabile", "utente mario: ERRORE, conferma del "
     "messaggio 12 non registrata (desktop): …"],
], "«TAB» — Gli eventi")

LOG = seq([("ams log 12", "root", "navy"), ("journal", "sd_journal", "green"), ("Chi legge", "terminale, TUI", "light")], [
    ("nota", 0, "carica sent/12/msg: la data"),
    (0, 1, "ams e AMS_MESSAGGIO=12"),
    (0, 1, "dalla data dell'invio meno 1 s"),
    (1, 0, "un evento alla volta, con _UID", True),
    ("nota", 0, "_UID atteso? se no: «non attendibile»"),
    (0, 2, "testo nella lingua di chi legge, ripulito"),
], "«FIG» — ams log: la storia di un messaggio, riscritta dai campi", "ams log")

S4 = p(c("ams log ID") + " ricostruisce la storia di un messaggio dagli eventi, nella lingua di chi lo lancia; la "
       "scheda Storia della TUI mostra la stessa uscita.", lead=True) + LOG + ul([
    "Gli eventi si cercano con due condizioni insieme: " + c("SYSLOG_IDENTIFIER=ams") + " e " + c("AMS_MESSAGGIO=ID")
    + ", e solo <b>dalla data d'invio</b> del messaggio (meno un secondo): un archivio azzerato riusa i numeri, il "
    "journal no.",
    "Chiunque può scrivere nel journal un evento con i campi " + c("AMS_*") + ": " + c("_UID") + " dice chi l'ha "
    "scritto, non che sia vero. " + c("ams log") + " si aspetta root (in modalità di prova, chi lancia) per gli "
    "eventi dell'amministratore e il destinatario stesso per " + c("RINVIATO") + ", " + c("CONFERMATO") + " e "
    + c("CONFERMA_FALLITA") + "; se " + c("_UID") + " è diverso, la riga comincia con «[non attendibile: scritto "
    "da UID N]» (scenario J3).",
    "Un evento dal nome sconosciuto si mostra con il suo " + c("MESSAGE") + "; ogni riga passa da " + c("pulisci")
    + " prima di arrivare al terminale.",
]) + term("admin@server:~$ sudo ams log 1\n"
          "Messaggio 1 · Manutenzione · 30/09 20:42\n"
          "2026-09-30 20:42:25  messaggio 1 consegnato a mario (terminali scritti: 1)\n"
          "2026-09-30 20:42:25  messaggio 1 consegnato a anna (terminali scritti: 0)\n"
          "2026-09-30 20:42:25  messaggio 1 inviato da admin a: anna mario\n"
          "2026-09-30 20:43:02  utente mario: confermata la lettura del messaggio 1 (terminale pts/2)",
          "Una storia") + \
    note("scrivere un evento è un'azione a parte rispetto al cambiamento che racconta: se il journal non risponde, "
         "lo stato nell'archivio resta giusto; della storia resta solo il testo scritto con " + c("syslog") + ", che "
         + c("ams log") + " non legge.")

CHAPTER = ("Il registro degli eventi", [
    ("Eventi strutturati nel journal", S1),
    ("I campi di un evento", S2),
    ("Gli eventi", S3),
    ("ams log e l'attendibilità", S4),
])
