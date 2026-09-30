from build import arrow, box, c, code, diamond, fig, note, p, path, seq, table, term, text, ul


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">capitolo {n}{"." + str(s) if s else ""}</a>'


DECIDE = fig(
    diamond(120, 70, 200, 64, "riga in delivery?", "navy")
    + box(40, 150, 160, 50, "INVIATO", "", "light")
    + diamond(355, 70, 220, 64, "conferma in acks/ID?", "navy")
    + box(275, 150, 160, 50, "CONSEGNATO", "nessuna conferma", "blue", 12)
    + diamond(585, 70, 200, 64, "data ≤ scadenza?", "navy")
    + box(705, 45, 185, 50, "CONSEGNATO", "conferma tardiva", "blue", 12)
    + diamond(585, 190, 200, 64, "data ≤ ritiro?", "navy")
    + box(705, 165, 185, 50, "CONSEGNATO", "conferma dopo il ritiro", "blue", 12)
    + box(505, 260, 160, 50, "CONFERMATO", "data e canale", "green", 12)
    + arrow(220, 70, 243, 70, "#0050C0", False, "sì", 232, 60)
    + arrow(120, 104, 120, 148, "#475569", False, "no", 136, 128)
    + arrow(465, 70, 483, 70, "#0050C0", False, "sì", 474, 60)
    + arrow(355, 104, 355, 148, "#475569", False, "no", 371, 128)
    + arrow(685, 70, 703, 70, "#475569", False, "no", 694, 60)
    + arrow(585, 104, 585, 156, "#0050C0", False, "sì", 601, 132)
    + arrow(685, 190, 703, 190, "#475569", False, "no", 694, 180)
    + arrow(585, 224, 585, 258, "#16a34a", False, "sì", 601, 244),
    900, 330, "«FIG» — stato_destinatario: lo stato di un destinatario, dedotto dai file", "Come si decide lo stato")

S1 = p("Lo stato di un destinatario non è scritto da nessuna parte: " + c("stato_destinatario") + " di "
       + c("src/ams.c") + " lo deduce ogni volta da " + c("sent/ID/delivery") + ", dalla conferma nella casella e "
       "dalla copia di riferimento. La scadenza e il ritiro che contano sono <b>quelli di root</b>, non quelli della "
       "copia che l'utente potrebbe aver alterato.", lead=True) + DECIDE + table(["Condizione", "Stato",
                                                                                 "Riga di ams status"], [
    ["nessuna riga per U in " + c("delivery"), "inviato", "«inviato, non consegnato»; se c'è " + c("incomplete")
     + ": «…: la copia non è stata scritta (vedi il registro; il prossimo comando ams riproverà)»"],
    ["riga in " + c("delivery") + ", nessuna conferma", "consegnato", "«consegnato», più i dettagli: «scritto su N "
     "terminali», «rimandato il …»; oppure «non confermato (ritirato)» o «(scaduto)»"],
    ["conferma con data dopo la scadenza di " + c("sent/ID/msg"), "consegnato", "«consegnato, non confermato "
     "(scaduto; conferma arrivata dopo la scadenza)»"],
    ["conferma con data dopo " + c("sent/ID/revoked"), "consegnato", "«consegnato, non confermato (ritirato)»"],
    ["conferma valida", "confermato", "«confermato il 30/09 17:10 (terminale pts/2)»"],
], "«TAB» — Lo stato dedotto dai file") + ul([
    "La data della conferma è il numero prima dello spazio in " + c("acks/ID") + " (0 se non è un numero); il resto "
    "della riga è il canale, tradotto solo quando si mostra (" + c("canale_testo") + ").",
    "Una conferma con la stessa data del ritiro vale; una del secondo dopo no (" + c("tests/engine.sh")
    + ", gruppo 9).",
    "Un destinatario è in <b>uno solo</b> dei tre stati: la funzione restituisce un valore di " + c("stato_e")
    + " (" + c("INVIATO") + ", " + c("CONSEGNATO") + ", " + c("CONFERMATO") + ") più, a parte, se la conferma era "
    "tardiva, la sua data e il suo canale.",
])

LETTURA = seq([("ams (root)", "list, status, TUI", "navy"), ("figlio come U", "op_leggi, 20 s", "dark"),
               ("Casella U", "users/U", "blue")], [
    (0, 1, "ID di sent/, uno per riga"),
    (1, 2, "acks/ID: al più 200 byte"),
    (1, 2, "stat di state/ID.term e .gui"),
    (1, 0, "«A ID riga» · «S ID data»", True),
    ("nota", 0, "pulisci, poi casella_da_testo"),
], "«FIG» — Una casella si legge una volta, come l'utente", "Lettura delle caselle")

S2 = p(c("ams status") + " e " + c("ams list") + " leggono le conferme dalle caselle, che gli utenti controllano. "
       + c("leggi_casella") + " di " + c("src/archivio.c") + " le tratta come <b>dati non fidati</b> e le legge "
       "<b>una volta per utente</b>, in un solo processo figlio.", lead=True) + LETTURA + ul([
    "Il figlio riceve su stdin i numeri dei messaggi che esistono in " + c("sent/") + " e cerca solo quelli: "
    "migliaia di file finti in " + c("acks/") + " non contano (5000 file: " + c("ams list") + " sotto il secondo, "
    + c("tests/engine.sh") + " gruppo 9; prima della correzione, 3,9 s).",
    "Di " + c("acks/ID") + " legge al più 200 byte, solo se è un file normale aperto senza bloccarsi: una pipe al "
    "posto della conferma non blocca " + c("ams status") + " (gruppo 9).",
    "Di " + c("state/ID.*") + " legge la data di modifica più recente: è l'ora del rinvio.",
    "L'uscita del figlio (al più 4 MiB) passa da " + c("pulisci") + " prima di essere interpretata: una conferma "
    "fabbricata con sequenze di escape non arriva al terminale dell'amministratore (scenario G3).",
    "Le caselle lette restano in memoria per tutto il comando; la TUI le dimentica a ogni aggiornamento ("
    + c("caselle_svuota") + "). Le consegne si leggono una volta per messaggio (" + c("leggi_consegne") + ").",
])

S3 = p("Nella lista dei messaggi, in " + c("ams list") + " e nella TUI, un messaggio si riassume <b>con i suoi "
       "destinatari</b>: quanti sono in ciascuno dei tre stati, a parole e con una barra, più le proprietà ritirato "
       "e scaduto. Nessun'altra parola descrive lo stato di un messaggio (" + cap(20, 3) + ").", lead=True) + \
    code("""typedef struct {
	long long id;
	msg_t m;                              /* il messaggio letto da sent/ID/msg */
	int confermato, consegnato, inviato;  /* i destinatari nei tre stati */
	bool ritirato, scaduto;               /* proprietà del messaggio */
} riassunto_t;""", "c", "src/ams.h") + table(["Funzione", "Che cosa fa"], [
    [c("riassumi(id, r)"), "legge messaggio, destinatari, consegne e data del ritiro <b>prima</b> di contare; "
     "falso se il messaggio non c'è più, se non ha destinatari o se l'invio è stato annullato (" + c("failed") + ")"],
    [c("riassunto_frase(r, out)"), "«14 confermato · 5 consegnato · 2 inviato», omettendo i conteggi a zero; "
     "«tutti confermato (58)» se nessuno manca"],
    ["barra della TUI", "12 segni: " + c("█") + " confermato (verde), " + c("▒") + " consegnato (giallo), "
     + c("░") + " inviato (rosso); un solo destinatario inviato ha comunque almeno un segno"],
], "«TAB» — Riassumere un messaggio") + \
    note("la frase usa sempre il nome dello stato («5 consegnato»), non un aggettivo accordato: è la stessa parola "
         "della colonna STATO di " + c("ams status") + ", in ogni lingua.")

LIST = ("admin@server:~$ sudo ams list\n"
        "ID    DATA         TESTO                                     DESTINATARI\n"
        "1     30/09 16:55  Stanotte alle 23 il server di posta vien  tutti confermato (3)\n"
        "2     30/09 16:55  Sabato dalle 8 alle 12 il server sarà sp  4 confermato · 3 consegnato · 1 inviato\n"
        "3     30/09 16:55  Il tuo account scade venerdì: passa dall  1 consegnato\n"
        "4     30/09 16:55  [ritirato] Riavvio alle 13:00.            2 consegnato")

STATUS = ("admin@server:~$ sudo ams status 2\n"
          "Messaggio 2 · Manutenzione · 30/09 16:55 · da root\n"
          "  │ Sabato dalle 8 alle 12 il server sarà spento per la manutenzione dei dischi.\n"
          "  │ Salvate il lavoro entro venerdì sera.\n"
          "\n"
          "UTENTE           STATO\n"
          "admin            confermato il 30/09 16:55 (terminale pts/0)\n"
          "anna             confermato il 30/09 16:55 (desktop)\n"
          "dario            inviato, non consegnato\n"
          "fabio            confermato il 30/09 16:55 (desktop)\n"
          "kora             consegnato, rimandato il 30/09 16:55\n"
          "luca             consegnato\n"
          "mario            consegnato, rimandato il 30/09 16:55\n"
          "zeno             confermato il 30/09 16:55 (terminale pts/2)")

S4 = p("I due comandi di consultazione mostrano lo stesso stato a due livelli: la lista dei messaggi e il dettaglio "
       "di uno. Entrambi eseguono prima il recupero; poi solo letture, senza lock.", lead=True) + \
    term(LIST, "ams list: un messaggio per riga (i messaggi delle schermate del capitolo 14)") + ul([
    "Colonne: ID, data d'invio («30/09 16:55»), le prime 40 colonne della prima riga del testo (con "
    + c("[ritirato]") + " e " + c("[scaduto]") + " davanti), la frase del riassunto.",
    "Un invio annullato compare come «[invio annullato: interrotto prima del salvataggio]»: è l'avviso di un "
    "segno interno, non uno stato.",
]) + term(STATUS, "ams status: un destinatario per riga") + ul([
    "Intestazione: numero, titolo e data, mittente; poi «RITIRATO il …» e «SCADUTO» se valgono; poi il testo, "
    "rientrato.",
    "Una riga per destinatario, nell'ordine di " + c("recipients") + " (alfabetico), con la riga di stato della "
    "tabella precedente; le stesse righe compaiono nel dettaglio della TUI.",
    "Un messaggio inesistente o annullato termina con errore: «messaggio inesistente: 99», «il messaggio N è stato "
    "annullato: l'invio si era interrotto prima del salvataggio».",
]) + p("I tempi misurati nell'ultima esecuzione registrata (scenari H2 e H3, 10 messaggi a 58 destinatari "
       "nella macchina di prova): " + c("ams list") + " 0,24 s, " + c("ams status") + " 0,28 s. Nel prototipo, "
       "prima della lettura per utente, " + c("ams list") + " impiegava circa 6 s.")

CHAPTER = ("Lo stato: list, status e il riassunto", [
    ("Lo stato dedotto dai file", S1),
    ("La lettura delle caselle", S2),
    ("Il riassunto di un messaggio", S3),
    ("ams list e ams status", S4),
])
