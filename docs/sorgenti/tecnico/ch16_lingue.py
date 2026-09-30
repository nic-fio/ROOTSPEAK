from build import arrow, box, c, code, diamond, fig, flow, note, p, path, table, text, ul, warn


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">capitolo {n}{"." + str(s) if s else ""}</a>'


LINGUE = fig(
    box(20, 50, 210, 54, "amministratore", "il suo ambiente, dopo sudo", "dark")
    + box(20, 130, 210, 54, "terminale dell'utente", "/proc/PID/environ", "dark")
    + box(20, 210, 210, 54, "shell, agente", "il loro ambiente", "dark")
    + box(20, 290, 210, 54, "journal", "/etc/default/locale", "dark")
    + box(330, 170, 200, 54, "lingua_scegli", "regole di gettext", "navy")
    + box(640, 80, 240, 54, "LINGUA/LC_MESSAGES/ams.mo", "letto da lingua.c", "blue", 12)
    + box(640, 170, 240, 54, "inglese", "i testi del codice", "light")
    + box(640, 260, 240, 54, "testo del messaggio", "mai tradotto", "soft")
    + arrow(232, 77, 328, 185) + arrow(232, 157, 328, 192) + arrow(232, 237, 328, 204) + arrow(232, 317, 328, 216)
    + arrow(532, 188, 638, 110, "#0050C0", False, "se c'è", 590, 138) + arrow(532, 200, 638, 198, "#475569", False,
                                                                           "altrimenti", 590, 190),
    900, 362, "«FIG» — Da dove viene la lingua di chi legge, e dove sono i testi", "Ognuno nella sua lingua")

S1 = p("Ogni persona legge AMS nella sua lingua: l'amministratore i comandi, ciascun utente la domanda, la finestra "
       "e i pulsanti. Il testo dei messaggi non si traduce mai. Oggi AMS ha l'italiano e l'inglese; l'inglese è la "
       "lingua dei testi nel codice e quella di ripiego.", lead=True) + LINGUE + table(["Chi legge", "Lingua",
                                                                                     "Da dove"], [
    ["l'amministratore: uscite, errori, guida, TUI", "la sua", "il suo ambiente: sudo conserva di solito "
     + c("LANG") + ", " + c("LANGUAGE") + " e " + c("LC_*")],
    ["l'utente, all'invio: l'intestazione nel terminale", "quella del terminale", "l'ambiente del primo processo "
     "del terminale, di solito la shell; se root non può leggerlo, lo legge l'utente stesso (" + cap(7, 4) + "); "
     "senza processi, la lingua del sistema"],
    ["l'utente, al prompt: domanda e risposte", "quella della shell", "l'ambiente di " + c("ams-user prompt")],
    ["l'utente, sul desktop: finestra, pulsanti, notifica", "quella della sessione grafica", "l'ambiente dell'agente"],
    ["il journal (" + c("MESSAGE") + ")", "quella del sistema", c("/etc/default/locale") + " o "
     + c("/etc/locale.conf")],
    [c("ams log") + ", storia della TUI", "di chi legge", "riscritto dai campi " + c("AMS_*") + " (" + cap(18, 4)
     + ")"],
], "«TAB» — Chi legge in quale lingua") + ul([
    "Ciò che si salva resta <b>senza lingua</b>: il canale di una conferma è " + c("terminale pts/N") + " o "
    + c("desktop") + " e si traduce solo quando si mostra (" + c("canale_testo") + "); gli eventi si riscrivono dai "
    "loro campi. Un amministratore in inglese legge «confirmed on 30/09 17:10 (terminal pts/19)» della stessa "
    "conferma che uno in italiano legge «confermato il … (terminale pts/19)» (scenario L3).",
    "La domanda accetta " + c("s") + ", " + c("S") + ", " + c("y") + " e " + c("Y") + " in ogni lingua (scenario L2).",
])

SCELTA = fig(
    box(20, 40, 230, 56, "LC_ALL › LC_MESSAGES › LANG", "il primo impostato", "dark", 12)
    + diamond(390, 68, 190, 64, "C o POSIX?", "navy")
    + box(310, 150, 160, 48, "inglese", "LANGUAGE ignorata", "light", 12)
    + box(530, 40, 170, 56, "elenco LANGUAGE", "de:it → prova de, poi it", "blue", 12)
    + box(740, 40, 140, 56, "lingua di LANG", "it_IT.UTF-8 → it", "blue", 12)
    + box(620, 150, 260, 48, "vince la prima con un .mo", "altrimenti l'inglese", "green", 12)
    + arrow(252, 68, 293, 68)
    + arrow(390, 102, 390, 148, "#475569", False, "sì", 404, 126)
    + arrow(487, 68, 528, 68, "#0050C0", False, "no", 507, 58)
    + arrow(702, 68, 738, 68)
    + arrow(810, 98, 810, 148, "#16a34a") + arrow(615, 98, 680, 148, "#16a34a"),
    900, 222, "«FIG» — lingua_scegli, le regole di gettext", "La scelta della lingua")

S2 = p(c("lingua_scegli") + " di " + c("src/lingua.c") + " segue le regole di gettext, con una restrizione: si "
       "accettano solo codici di 2 o 3 lettere minuscole.", lead=True) + SCELTA + ul([
    "Conta il primo impostato fra " + c("LC_ALL") + ", " + c("LC_MESSAGES") + " e " + c("LANG") + ". Se è "
    + c("C") + " o " + c("POSIX") + " (anche " + c("C.UTF-8") + "), o è vuoto, vale l'inglese e " + c("LANGUAGE")
    + " non conta.",
    "Altrimenti si prova prima l'elenco di " + c("LANGUAGE") + " (separato da due punti), poi la lingua del valore "
    "scelto: la parte prima di " + c("_") + ", " + c(".") + ", " + c("@") + ". Vince la prima lingua che ha un "
    "catalogo installato (l'inglese è sempre disponibile); se nessuna, l'inglese.",
    "Un valore che non è un codice di 2 o 3 lettere minuscole (" + c("../../tmp/x") + ", " + c("a/b") + ") non porta "
    "mai a leggere un file: il percorso del catalogo si costruisce solo con un codice valido.",
    "Nove casi sono provati in " + c("tests/prove-unita.c") + " e di nuovo in " + c("tests/engine.sh") + " (gruppo "
    "8): italiano, inglese, lingua senza traduzione, " + c("C") + ", priorità di " + c("LC_ALL") + " e di "
    + c("LC_MESSAGES") + ", elenco di " + c("LANGUAGE") + ", " + c("LANGUAGE") + " con " + c("C") + ", valori strani.",
])

MO = fig(
    box(20, 50, 150, 56, "intestazione", "magico, N, posizioni", "dark", 12)
    + box(190, 50, 170, 56, "tabella originali", "N × (lunghezza, pos.)", "navy", 12)
    + box(380, 50, 170, 56, "tabella traduzioni", "N × (lunghezza, pos.)", "navy", 12)
    + box(570, 50, 310, 56, "stringhe terminate da zero", "originali in ordine: ricerca binaria", "blue", 12)
    + text(450, 140, "ogni posizione è controllata prima di usarla: una voce che esce dal file non esiste", 11.5,
           "#166534", "600")
    + text(450, 160, "contesto: «contesto\\004testo» nell'originale · traduzione vuota = non tradotto", 11,
           "#475569"),
    900, 180, "«FIG» — Com'è fatto un catalogo .mo, e come lo legge AMS", "Il lettore dei cataloghi")

S3 = p("I cataloghi sono nel formato di gettext (" + c(".mo") + "), ma li legge " + c("src/lingua.c") + ", non la "
       "libintl. È una decisione presa con una prova: con la libintl una lingua non installata nel sistema resta "
       "non tradotta anche forzando " + c("LANGUAGE") + " (con " + c("C.UTF-8") + " la libreria ignora "
       + c("LANGUAGE") + "), e root deve poter scrivere a ogni terminale nella lingua del suo utente, diversa dalla "
       "propria.", lead=True) + MO + table(["Funzione", "Che cosa fa"], [
    [c("catalogo_da_memoria"), "controlla il numero magico " + c("0x950412de") + " in entrambi gli ordini dei byte e "
     "che le due tabelle stiano nel file; altrimenti nessun catalogo"],
    [c("catalogo_cerca"), "ricerca binaria fra gli originali; ogni voce deve stare nel file e finire con uno zero; "
     "una traduzione vuota vale «non tradotto»"],
    [c("catalogo(lingua)"), "legge " + c("LOCALEDIR/LINGUA/LC_MESSAGES/ams.mo") + " (al più 4 MiB) la prima volta, "
     "poi lo tiene in memoria (fino a 8 lingue per processo)"],
    [c("T(testo)") + ", " + c("TC(contesto, testo)"), "la traduzione nella lingua di chi usa il processo"],
    [c("tl(lingua, testo)") + ", " + c("tlc(…)"), "la traduzione in una lingua data: così " + c("ams send")
     + " scrive a ogni terminale nella sua lingua"],
], "«TAB» — Il lettore dei cataloghi") + \
    note("i cataloghi sono file di root, ma il lettore li tratta come dati qualunque: il fuzzing prova anche "
         "cataloghi arbitrari (" + cap(21, 7) + ").")

S4 = flow([("src/*.c", "T(\"…\"), TC, tl, tlc", "dark"), ("make pot", "xgettext → ams.pot", "navy"),
           ("po/it.po", "msgmerge, poi tradurre", "blue"), ("make", "msgfmt --check → .mo", "navy"),
           ("check-docs", "catalogo completo?", "green")], "«FIG» — Dai testi nel codice ai cataloghi") + ul([
    "Nel codice i testi per chi usa AMS sono in inglese dentro " + c("T(\"…\")") + " (o " + c("TC(contesto, \"…\")")
    + ", " + c("tl(lingua, \"…\")") + " per una lingua data; " + c("N_(…)") + " per i testi tradotti più tardi). "
    "Nomi, commenti e documentazione sono in italiano.",
    c("make pot") + " li estrae in " + c("po/ams.pot") + " con " + c("xgettext") + " (con i commenti "
    + c("TRADUTTORI") + ") e aggiorna i " + c(".po") + " con " + c("msgmerge") + "; " + c("make") + " li compila "
    "con " + c("msgfmt --check") + ", che controlla anche che ogni traduzione abbia gli stessi " + c("%s") + ".",
    c("tools/check-docs.py") + " fallisce se un catalogo non passa " + c("msgfmt --check") + ", ha traduzioni da "
    "rivedere o non contiene tutti i testi del codice.",
    "Per una lingua nuova basta un " + c("po/XX.po") + " (per esempio con " + c("msginit") + "): il Makefile e "
    + c("install.sh") + " la prendono da soli.",
]) + warn("se l'utente cambia " + c("LANG") + " dentro la shell (per esempio nel " + c(".bashrc") + "), "
          "l'intestazione scritta all'invio segue l'ambiente con cui la shell è partita; domanda e risposte seguono "
          "quello nuovo (" + cap(23) + ").")

CHAPTER = ("Le lingue", [
    ("Ognuno nella sua lingua", S1),
    ("La scelta della lingua", S2),
    ("Il lettore dei cataloghi .mo", S3),
    ("Testi, contesti e cataloghi", S4),
])
