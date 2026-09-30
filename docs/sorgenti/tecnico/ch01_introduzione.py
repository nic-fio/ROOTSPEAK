from build import arrow, box, c, fig, p, path, table, text, zone

OVERVIEW = fig(
    zone(20, 44, 250, 250, "Amministratore · root")
    + box(44, 78, 202, 58, "ams", "bin/ams, via sudo", "navy")
    + box(44, 150, 202, 50, "ams-common.sh", "libreria comune", "soft")
    + box(44, 214, 202, 50, "ams-help.sh", "guida integrata", "soft")
    + zone(318, 44, 240, 250, "Archivio · /var/lib/ams")
    + box(340, 78, 196, 58, "sent/", "copie di riferimento · root", "dark")
    + box(340, 172, 196, 58, "users/U/", "casella di ogni utente · U", "blue")
    + zone(606, 44, 274, 250, "Utente · U")
    + box(628, 78, 230, 58, "ams-user prompt", "aggancio della shell bash", "light")
    + box(628, 172, 230, 58, "ams-user agent", "avvio automatico del desktop", "light")
    + text(743, 262, "terminali /dev/pts/N · finestra zenity", 11, "#475569")
    + arrow(248, 104, 338, 104)
    + path([(248, 118), (294, 118), (294, 200), (338, 200)], "#0050C0", False, "come U", 300, 190)
    + arrow(538, 190, 626, 106, "#16a34a", True)
    + arrow(538, 204, 626, 200, "#16a34a", True)
    + text(582, 236, "legge, conferma", 11, "#166534", "600"),
    900, 312, "«FIG» — I tre ambiti di AMS: il comando di root, l'archivio, l'aiutante che gira come utente",
    "Chi fa cosa")

S1 = p("AMS è uno strumento con cui gli amministratori di una macchina Linux mandano messaggi di testo agli utenti e "
       "ne seguono la conferma di lettura. La versione 0.1.0 è un prototipo in bash: niente demone, niente database, "
       "solo file e strumenti già presenti nel sistema.", lead=True) + OVERVIEW + \
    p("Il comando " + c("ams") + " gira sempre come root e scrive nell'archivio. Dalla parte dell'utente, due ingressi "
      "dello stesso aiutante, " + c("ams-user") + ", leggono la casella e registrano la conferma: uno nel prompt di bash, "
      "l'altro nella sessione grafica.")

S2 = table(["Principio", "Cosa comporta nel codice"], [
    ["<b>Nessun demone</b>", "La consegna la fa " + c("ams send") + " nel momento dell'invio; il resto lo fanno l'aggancio "
     "della shell e l'agente del desktop, che partono con le sessioni dell'utente."],
    ["<b>" + c("ams") + " sempre come root</b>", "Il comando si rilancia con " + c("sudo") + " prima di qualunque cosa, "
     "compresi " + c("--help") + " e " + c("version") + "."],
    ["<b>Mai bloccare</b>", "Nessun livello bloccante: " + c("ack") + " insiste con i solleciti, ma l'utente può sempre "
     "rimandare. Le sessioni senza terminale non vengono toccate."],
    ["<b>Gli utenti non hanno comandi</b>", c("ams-user") + " è un aiutante interno fuori dal PATH; la ricezione è "
     "automatica."],
    ["<b>Root non si fida delle caselle</b>", "Ogni accesso di root a " + c("users/U") + " passa da " + c("runuser -u U")
     + " (capitolo 5.3)."],
    ["<b>Strumenti del sistema</b>", c("loginctl") + ", " + c("runuser") + ", " + c("flock") + ", " + c("zenity") + ", "
     + c("notify-send") + ", " + c("systemd-run") + ", " + c("logger") + "."],
], "«TAB» — I principi del progetto")

S3 = table(["Componente", "Chi lo esegue", "Quando"], [
    [c("ams"), "root, rilanciato con sudo", "quando un amministratore lo invoca"],
    [c("ams-user prompt"), "l'utente, nella sua shell bash", "prima di ogni prompt, se la casella non è vuota; subito al login"],
    [c("ams-user agent"), "l'utente, nella sessione grafica", "dal login grafico alla fine della sessione; " + c("ams send")
     + " lo avvia se manca"],
    [c("/etc/profile.d/ams.sh"), "la shell dell'utente", "a ogni shell interattiva (anche da " + c("/etc/bash.bashrc") + ")"],
    [c("install.sh"), "root", "installazione, aggiornamento, rimozione"],
], "«TAB» — I componenti e chi li esegue")

CHAPTER = ("Introduzione e concetti", [
    ("Che cos'è AMS", S1),
    ("Principi", S2),
    ("I componenti in breve", S3),
])
