from build import c, p, table

S1 = table(["Tema", "Regola"], [
    ["lingua", "codice, commenti e documentazione in italiano; ciò che leggono amministratori e utenti sta in "
     + c("lib/lingue/") + ", in ogni lingua (capitolo 10.4)"],
    [c("bin/ams"), c("set -euo pipefail") + "; niente " + c("((…))") + " come comando isolato: un risultato 0 farebbe uscire lo script"],
    [c("lib/ams-user"), c("set -uo pipefail") + " senza " + c("-e") + ": gira dentro il prompt dell'utente e non deve interromperlo"],
    ["guida", "disattiva " + c("-e") + " e " + c("-u") + " all'ingresso"],
    ["errori", c("ams_die") + ": stampa " + c("ams: …") + " ed esce con 1"],
    ["registro", c("ams_log") + ": " + c("logger -t ams")],
    ["accessi alle caselle", "sempre con " + c("as_user")],
    ["manuali", "si modificano i sorgenti in " + c("docs/sorgenti/") + " e si rigenerano; mai a mano i file HTML"],
    ["commit", "identità locale del repository (noreply di GitHub), messaggi in italiano"],
], "«TAB» — Le convenzioni") + \
    p("La versione è " + c("AMS_VERSION") + " in " + c("lib/ams-common.sh") + ": i manuali la leggono da lì.")

CHAPTER = ("Convenzioni", [
    ("Regole di scrittura", S1),
])
