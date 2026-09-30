import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import arrow, box, c, code, fig, note, p, steps, table, term, text, tip, warn  # noqa: E402
from _aiuti import rif  # noqa: E402

S1 = p("Le impostazioni di AMS sono due e stanno in un solo file, " + c("/etc/ams/ams.conf") + ". Vanno bene così "
       "come sono installate; si cambiano solo per esigenze particolari.", lead=True) + \
    code("""# AMS - Advanced Messaging System for linux: configurazione
# File di dati, non uno script: righe CHIAVE=valore con numeri interi positivi.
# Chiavi sconosciute e valori non validi sono ignorati.

# Dopo quanti minuti riproporre un messaggio rimandato dall'utente
AMS_REMIND_MINUTES=30

# Ogni quanti secondi l'agente del desktop ricontrolla i messaggi
# (i nuovi messaggi lo svegliano comunque subito)
AMS_AGENT_POLL=60""", "conf", "/etc/ams/ams.conf, come lo installa AMS") + \
    table(["Impostazione", "Predefinito", "Cosa decide"], [
        [c("AMS_REMIND_MINUTES"), c("30"), "dopo quanti minuti un messaggio rimandato viene riproposto, nel terminale "
         "e sul desktop; è anche il numero scritto in «La domanda verrà riproposta tra 30 minuti»"],
        [c("AMS_AGENT_POLL"), c("60"), "ogni quanti secondi l'agente del desktop ricontrolla i messaggi per "
         "sicurezza. I messaggi nuovi e i solleciti arrivano comunque subito. Valori più bassi consumano un po' più "
         "di batteria"],
    ], "«TAB» — Le impostazioni") + \
    table(["Regola del file", "Esempio"], [
        ["una riga per impostazione, " + c("CHIAVE=valore"), c("AMS_REMIND_MINUTES=15")],
        ["solo numeri interi maggiori di zero, al massimo sei cifre", c("AMS_AGENT_POLL=120")],
        ["gli spazi non contano", c("AMS_REMIND_MINUTES = 15")],
        ["dopo " + c("#") + " è un commento", c("AMS_AGENT_POLL=30  # portatili in carica")],
        ["righe non valide, chiavi sconosciute e valori sbagliati sono ignorati: vale il predefinito",
         c("AMS_REMIND_MINUTES=mezz'ora") + " → 30"],
    ], "«TAB» — Come si scrive il file") + \
    note("il file contiene solo dati: non è uno script e non viene eseguito. Un errore di scrittura non blocca AMS, "
         "fa solo usare il valore predefinito.", "Solo dati.")

EFFETTO = fig(
    '<line x1="60" y1="120" x2="860" y2="120" stroke="#94a3b8" stroke-width="2"/>'
    + text(60, 146, "rinvio", 11.5, "#475569", "600") + text(620, 146, "+ AMS_REMIND_MINUTES", 11.5, "#92400e", "700")
    + '<path d="M62 100 H 618" stroke="#d97706" stroke-width="2" stroke-dasharray="5 4"/>'
    + box(630, 76, 230, 40, "il messaggio torna", "al prompt dopo, o alla finestra", "amber", 12)
    + '<line x1="60" y1="240" x2="860" y2="240" stroke="#94a3b8" stroke-width="2"/>'
    + "".join(f'<line x1="{x}" y1="232" x2="{x}" y2="248" stroke="#0050C0" stroke-width="2"/>' for x in (100, 300, 500, 700))
    + text(400, 272, "controlli dell'agente del desktop, ogni AMS_AGENT_POLL secondi", 11.5, "#1e40af", "600")
    + box(360, 176, 180, 40, "ams send o remind", "sveglia subito", "green", 12)
    + arrow(450, 218, 450, 238, "#16a34a"),
    900, 292, "«FIG» — Che cosa regolano le due impostazioni", "Rinvio e controlli")

S2 = EFFETTO + steps([
    "Aprire il file con i permessi di amministratore:" + term("admin@server:~$ sudo nano /etc/ams/ams.conf"),
    "Cambiare il valore, per esempio " + c("AMS_REMIND_MINUTES=15") + ", salvare e uscire.",
    "Non serve riavviare nulla: il valore vale subito per i terminali (dal prompt successivo) e per il desktop "
    "dal controllo successivo dell'agente.",
]) + table(["Esigenza", "Impostazione"], [
    ["avvisi urgenti: riproporre più spesso", c("AMS_REMIND_MINUTES=10")],
    ["utenti che si lamentano delle richieste", c("AMS_REMIND_MINUTES=60") + " o più"],
    ["portatili a batteria", c("AMS_AGENT_POLL=300") + ": i messaggi nuovi arrivano comunque subito"],
], "«TAB» — Valori consigliati") + \
    warn("il file deve restare di proprietà di root e modificabile solo da root, come lo lascia l'installazione: "
         "lo leggono tutti gli utenti, per sapere quando riproporre i messaggi.", "Permessi.") + \
    note("un aggiornamento di AMS non sovrascrive " + c("/etc/ams/ams.conf") + "; " + c("./install.sh --purge")
         + " invece lo cancella.", "Aggiornamenti.")

S3 = p("Alcune variabili d'ambiente cambiano il comportamento di " + c("ams") + " per l'amministratore che le "
       "imposta. Poiché " + c("ams") + " si rilancia sempre con sudo, arrivano solo se sudo le conserva.", lead=True) + \
    table(["Variabile", "Effetto", "Predefinito"], [
        [c("NO_COLOR"), "se impostata, TUI e guida senza colori", "colori"],
        [c("PAGER"), "il programma che impagina la guida nei terminali piccoli (" + rif(9, 3) + ")", c("less")],
        [c("VISUAL") + ", " + c("EDITOR"), "l'editor aperto con " + "Ctrl+E" + " nel nuovo messaggio (" + rif(5, 5)
         + ")", c("nano") + ", poi " + c("vi")],
        [c("LANG") + " e simili", "la lingua di " + c("ams") + " e della TUI", "conservate da sudo nelle "
         "configurazioni abituali"],
    ], "«TAB» — Le variabili d'ambiente") + \
    p("Per farle conservare da sudo si aggiunge una riga alle sue impostazioni, sempre con " + c("visudo") + ":") + \
    term('admin@server:~$ sudo visudo -f /etc/sudoers.d/ams\n'
         '# nel file:\n'
         'Defaults env_keep += "NO_COLOR PAGER VISUAL EDITOR"', "Conservare le variabili attraverso sudo") + \
    warn("questa riga vale per tutti i comandi lanciati con sudo, non solo per " + c("ams") + ". Aggiungere solo le "
         "variabili che servono.", "Per tutto sudo.") + \
    tip("l'editor aperto da " + c("ams") + " gira con l'identità dell'amministratore, non come root: tenere "
        + c("EDITOR") + " non gli dà poteri in più.", "Editor e sicurezza.")

CHAPTER = ("Impostazioni", [
    ("Il file delle impostazioni", S1),
    ("Cambiare un'impostazione", S2),
    ("Colori, pager ed editor", S3),
])
