from build import arrow, box, c, code, dl, fig, note, p, table, text


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">capitolo {n}{"." + str(s) if s else ""}</a>'


MAPPA = fig(
    box(20, 40, 170, 56, "msg_t", "sent/ID/msg letto", "navy")
    + box(250, 40, 190, 56, "riassunto_t", "msg_t + tre conteggi", "blue")
    + box(500, 40, 170, 56, "elenco_t (TUI)", "i riassunti, in ordine", "soft")
    + box(250, 130, 190, 56, "stato_e", "INVIATO · CONSEGNATO · …", "green", 12)
    + box(500, 130, 170, 56, "destinatario_t", "utente, stato, riga", "blue")
    + box(20, 130, 170, 56, "consegne_t", "sent/ID/delivery", "dark")
    + box(20, 220, 170, 56, "casella_t", "voci lette come U", "dark")
    + box(250, 220, 190, 56, "stato_t", "stato, data, canale", "light")
    + box(720, 40, 160, 56, "utente_t", "nome, uid, gid", "dark")
    + box(720, 130, 160, 56, "op_t", "casella, ID", "soft")
    + box(720, 220, 160, 56, "conf_t", "rinvio, controllo", "soft")
    + arrow(192, 68, 248, 68) + arrow(442, 68, 498, 68)
    + arrow(192, 158, 248, 238) + arrow(192, 248, 248, 250)
    + arrow(345, 218, 345, 188) + arrow(442, 158, 498, 158)
    + arrow(345, 128, 345, 98, "#16a34a")
    + arrow(800, 98, 800, 128, "#475569", True)
    + text(450, 300, "lo stato si calcola ogni volta: nessuna di queste strutture viene salvata", 11.5, "#475569",
           "600"),
    900, 316, "«FIG» — Le strutture dati e come si compongono", "Strutture")

S1 = p("Questa appendice raccoglie le strutture dati di AMS con il file che le definisce e il capitolo di "
       "approfondimento. Sono i «contratti» che attraversano il codice. Nessuna viene scritta su disco così com'è: "
       "sui file vanno solo i formati di testo del " + cap(20, 8) + ".", lead=True) + MAPPA + table(
    ["Struttura", "Definita in", "Ruolo", "Capitolo"], [
        [c("msg_t"), c("src/testo.h"), "un messaggio letto o da scrivere", cap(5, 2)],
        [c("conf_t"), c("src/testo.h"), "la configurazione", cap(4, 5)],
        [c("stato_e"), c("src/ams.h"), "i tre stati di un destinatario", cap(10, 1)],
        [c("riassunto_t"), c("src/ams.h"), "un messaggio con i destinatari contati nei tre stati", cap(10, 3)],
        [c("destinatario_t") + ", " + c("destinatari_t"), c("src/ams.h"), "i destinatari con la riga di "
         + c("ams status"), cap(10, 4)],
        [c("voce_casella_t") + ", " + c("casella_t"), c("src/archivio.h"), "conferme e rinvii letti da una casella",
         cap(10, 2)],
        [c("utente_t"), c("src/utente.h"), "un utente: nome, UID, gruppo principale", cap(7, 2)],
        [c("come_utente_fn"), c("src/utente.h"), "la funzione eseguita nel figlio", cap(7, 2)],
        [c("op_t"), c("src/archivio.c"), "argomento delle operazioni sulle caselle", cap(7, 4)],
        [c("consegne_t"), c("src/ams.c"), "le righe di " + c("delivery") + " di un messaggio", cap(10, 1)],
        [c("stato_t"), c("src/ams.c"), "lo stato di un destinatario, con data e canale della conferma", cap(10, 1)],
        [c("catalogo_t"), c("src/lingua.c"), "un catalogo " + c(".mo") + " in memoria", cap(16, 3)],
        [c("buf_t") + ", " + c("strv_t"), c("src/comune.h"), "testi che crescono ed elenchi di stringhe", cap(5, 5)],
        [c("schermo_t") + ", " + c("elenco_t") + ", " + c("modulo_t") + ", " + c("lancio_t"), c("src/tui.c"),
         "schermata, lista, modulo e comando da eseguire nella TUI", cap(14)],
    ], "«TAB» — Indice delle strutture dati")

S2 = code("""typedef struct {
	long long id;
	char *from;         /* l'amministratore */
	long long date;     /* secondi dall'epoca Unix; obbligatoria */
	char *title;        /* una riga, eventualmente vuota */
	long long expires;  /* 0: nessuna scadenza */
	char *body;         /* il testo, con l'a capo finale */
} msg_t;""", "c", "src/testo.h") + table(["Campo", "Tipo", "Descrizione"], [
    [c("id"), c("long long"), "il numero del messaggio (" + c("id:") + ")"],
    [c("from"), c("char *"), "mai nullo dopo la lettura (vuoto se manca)"],
    [c("date"), c("long long"), "un messaggio senza " + c("date") + " valida non si legge"],
    [c("title"), c("char *"), "mai nullo dopo la lettura"],
    [c("expires"), c("long long"), c("msg_scaduto") + " è vero se è diverso da 0 e minore o uguale all'ora data"],
    [c("body"), c("char *"), "tutto ciò che segue la prima riga vuota"],
], "«TAB» — I campi di msg_t") + \
    p(c("msg_libera") + " libera i tre testi e azzera la struttura: una " + c("msg_t") + " azzerata si può liberare "
      "senza danni.")

S3 = code("""/* Gli stati di un destinatario: gli unici tre (capitolo «Specifica»). */
typedef enum { INVIATO, CONSEGNATO, CONFERMATO } stato_e;

typedef struct {
	long long id;
	msg_t m;
	int confermato, consegnato, inviato;
	bool ritirato, scaduto;
} riassunto_t;

typedef struct {
	char *utente;
	stato_e stato;
	char *riga;        /* la riga di ams status, nella lingua di chi legge */
} destinatario_t;""", "c", "src/ams.h") + dl([
    (c("stato_e"), "l'unico posto del codice in cui gli stati sono enumerati. Ritirato e scaduto non ci sono: sono "
     "i due " + c("bool") + " di " + c("riassunto_t") + "."),
    (c("riassunto_t"), "prodotto da " + c("riassumi") + "; " + c("confermato + consegnato + inviato") + " è il numero "
     "dei destinatari. " + c("riassunto_libera") + " libera il messaggio contenuto."),
    (c("destinatario_t"), "prodotto da " + c("destinatari") + " per " + c("ams status") + ", per la TUI e per "
     + c("ams remind") + ", che sollecita chi ha " + c("stato == CONSEGNATO") + "."),
])

S4 = code("""typedef struct {
	long long id;
	char *conferma;     /* prima riga di acks/ID, o NULL */
	long long rinvio;   /* data di modifica più recente di state/ID.*, o 0 */
} voce_casella_t;

typedef struct {
	voce_casella_t *v;
	size_t n;
} casella_t;""", "c", "src/archivio.h") + \
    p("Una " + c("casella_t") + " nasce da " + c("casella_da_testo") + ", che interpreta l'uscita del figlio ("
      + c("A ID riga") + " per le conferme, " + c("S ID data") + " per i rinvii) già ripulita; righe malformate si "
      "scartano, e per ogni ID conta la prima conferma e il rinvio più recente. " + c("casella_da_testo")
      + " è esposta anche per le prove e per il fuzzing.")

S5 = code("""typedef struct { char *nome; uid_t uid; gid_t gid; } utente_t;
typedef int (*come_utente_fn)(void *arg);
typedef struct { long remind_minutes; long agent_poll; } conf_t;   /* 30, 60 */
typedef struct { char *s; size_t n, cap; } buf_t;    /* s sempre terminato da '\\0' */
typedef struct { char **v; size_t n, cap; } strv_t;""", "c", "src/utente.h, src/testo.h, src/comune.h (in breve)") + dl([
    (c("utente_t"), "da " + c("utente_cerca") + " (per nome) o " + c("utente_da_uid") + "; il nome è copiato."),
    (c("conf_t"), "riempita da " + c("conf_leggi") + " con i valori predefiniti e le chiavi valide del file."),
    (c("buf_t"), "ogni testo che viene da fuori finisce qui: " + c("buf_add") + " controlla il trabocco delle "
     "dimensioni, e la memoria cresce raddoppiando. " + c("buf_free") + " lo riporta a vuoto."),
    (c("strv_t"), "elenchi di destinatari, di ID, di terminali; " + c("strv_sort") + " in ordine alfabetico, "
     + c("elenca_numeri") + " in ordine numerico."),
]) + note("tutte le strutture si inizializzano a zero (" + c("{0}") + ") e hanno una funzione che le libera; il "
          "fuzzing ha trovato proprio una funzione che presupponeva una struttura già azzerata (" + cap(21, 7) + ").")

CHAPTER = ("Appendice A — Strutture dati", [
    ("Indice delle strutture dati", S1),
    ("msg_t: un messaggio", S2),
    ("stato_e, riassunto_t, destinatario_t", S3),
    ("voce_casella_t e casella_t", S4),
    ("utente_t, conf_t, buf_t, strv_t", S5),
])
