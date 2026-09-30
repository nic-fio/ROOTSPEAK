import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import arrow, box, c, dl, fig, text, zone  # noqa: E402

MAPPA = fig(
    box(30, 60, 190, 60, "Messaggio", "numero, titolo, testo", "navy")
    + box(30, 170, 190, 60, "Proprietà", "scadenza, ritiro", "grey")
    + box(300, 60, 190, 60, "Destinatari", "nomi, @gruppo, all, online", "dark")
    + zone(560, 40, 320, 206, "Stato di ogni destinatario")
    + box(590, 76, 260, 44, "inviato", "", "grey", 13)
    + box(590, 130, 260, 44, "consegnato", "", "amber", 13)
    + box(590, 184, 260, 44, "confermato", "", "green", 13)
    + arrow(222, 90, 298, 90) + arrow(125, 122, 125, 168, "#475569")
    + arrow(492, 90, 556, 98)
    + box(300, 260, 190, 56, "Eventi", "nel registro e nella storia", "light")
    + arrow(395, 122, 395, 258, "#475569", True)
    + text(720, 276, "sessioni: desktop, terminali, accesso", 11.5, "#334155", "600")
    + text(720, 296, "canale della conferma: desktop o terminale", 11.5, "#334155", "600"),
    900, 330, "«FIG» — Le parole di AMS e come stanno insieme", "Mappa dei termini")

S1 = MAPPA + dl([
    ("agente del desktop", "Il piccolo programma di AMS che parte a ogni accesso grafico e mostra le finestre di "
     "conferma. Non è un comando: parte da solo."),
    ("all", "Destinatario speciale: tutti gli utenti della macchina con UID da 1000 in su e una shell vera."),
    ("archivio", "La cartella " + c("/var/lib/ams/") + ": le copie di riferimento dei messaggi e le caselle degli "
     "utenti."),
    ("canale", "Da dove è arrivata una conferma: " + c("desktop") + " oppure " + c("terminale pts/N") + " o "
     + c("terminale ttyN") + "."),
    ("casella", "Lo spazio in cui AMS tiene i messaggi di un utente, le sue conferme e i suoi rinvii. La può aprire "
     "solo lui (e root)."),
    ("conferma", "La dichiarazione dell'utente di aver letto un messaggio: un clic su «Ho letto» o la risposta «s». "
     "È definitiva e vale per tutte le sue sessioni."),
    ("confermato", "Terzo stato di un destinatario: ha dichiarato di aver letto il messaggio. È la sua dichiarazione, "
     "non una prova che l'abbia letto davvero."),
    ("consegnato", "Secondo stato: la copia del messaggio è nella casella dell'utente, che non ha ancora confermato. "
     "Chi rimanda resta consegnato."),
    ("destinatari", "Gli utenti che ricevono un messaggio: nomi, " + c("@gruppo") + ", " + c("all") + ", "
     + c("online") + "."),
    ("evento", "Un fatto nella storia di un messaggio (invio, consegna, rinvio, sollecito, conferma, ritiro, "
     "cancellazione), scritto nel registro di sistema."),
    ("guida integrata", "La guida a schede che si apre con " + c("ams --help") + "."),
    ("inviato", "Primo stato: il messaggio è partito, ma la copia non è ancora nella casella dell'utente."),
    ("online", "Destinatario speciale: fra gli utenti di " + c("all") + ", chi è collegato al momento dell'invio."),
    ("pulizia", "La cancellazione dei messaggi più vecchi di una durata: " + c("ams purge") + " o il tasto " + c("p")
     + " della TUI."),
    ("recupero", "Il completamento automatico di un invio rimasto a metà, al primo uso successivo di " + c("ams") + "."),
    ("registro di sistema", "Il registro della macchina (journal), dove AMS scrive i suoi eventi con l'etichetta "
     + c("ams") + "."),
    ("rimandare", "Premere «Più tardi» o rispondere «n»: il messaggio viene riproposto dopo 30 minuti. Non è uno stato."),
    ("ritirare", "Togliere un messaggio con " + c("ams revoke") + " o il tasto " + c("r") + ": chi non l'ha visto non "
     "lo vedrà più. Ritirato è una proprietà del messaggio, non uno stato dei destinatari."),
    ("scadenza", "Il momento dopo il quale un messaggio non viene più mostrato (" + c("--expires") + "). Scaduto è "
     "una proprietà del messaggio, non uno stato dei destinatari."),
    ("sessione", "Un accesso di un utente alla macchina: il desktop, una console, una connessione ssh."),
    ("sollecitare", "Chiedere di nuovo, subito, la conferma a chi è ancora consegnato: " + c("ams remind") + " o il "
     "tasto " + c("s") + " della TUI."),
    ("TUI", "L'interfaccia a tutto schermo, dentro il terminale, che si apre scrivendo " + c("ams") + " da solo."),
], cls="gloss")

CHAPTER = ("Glossario", [
    ("Termini", S1),
])
