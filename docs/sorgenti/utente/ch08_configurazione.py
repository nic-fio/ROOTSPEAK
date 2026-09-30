from build import c, code, p, steps, table, term, warn

S1 = p("Le impostazioni di AMS sono tre e stanno in un solo file, " + c("/etc/ams/ams.conf") + ". Vanno bene così "
       "come sono installate; si cambiano solo per esigenze particolari.", lead=True) + \
    code("""# Livello predefinito dei messaggi: info oppure ack
AMS_DEFAULT_LEVEL=ack

# Dopo quanti minuti riproporre un messaggio rimandato dall'utente
AMS_REMIND_MINUTES=30

# Ogni quanti secondi l'agente del desktop ricontrolla i messaggi
# (i nuovi messaggi lo svegliano comunque subito)
AMS_AGENT_POLL=60""", "conf", "/etc/ams/ams.conf") + \
    table(["Impostazione", "Predefinito", "Cosa decide"], [
        [c("AMS_DEFAULT_LEVEL"), c("ack"), "il livello dei messaggi mandati senza " + c("--level")],
        [c("AMS_REMIND_MINUTES"), c("30"), "dopo quanti minuti un messaggio rimandato viene riproposto, nel terminale e sul desktop"],
        [c("AMS_AGENT_POLL"), c("60"), "ogni quanti secondi il desktop ricontrolla i messaggi per sicurezza; i messaggi nuovi arrivano comunque subito. Valori più bassi consumano un po' più di batteria"],
    ], "«TAB» — Le impostazioni")

S2 = steps([
    "Aprire il file con i permessi di amministratore:" + term("admin@server:~$ sudo nano /etc/ams/ams.conf", ""),
    "Cambiare il valore, per esempio " + c("AMS_REMIND_MINUTES=15") + ", e salvare.",
    "Non serve riavviare nulla: il valore vale subito per " + c("ams send") + " e per i terminali. Sul desktop vale "
    "dal prossimo accesso dell'utente.",
]) + warn("il file viene letto da AMS anche per conto degli utenti: deve restare di proprietà di root e modificabile "
          "solo da root, come lo lascia l'installazione.")

CHAPTER = ("Impostazioni", [
    ("Il file delle impostazioni", S1),
    ("Cambiare un'impostazione", S2),
])
