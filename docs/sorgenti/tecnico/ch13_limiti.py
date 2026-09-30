from build import c, table

S1 = table(["Limite", "Conseguenza"], [
    ["sh, dash, ksh e simili non hanno un aggancio prima del prompt", "la domanda arriva al login (e dal desktop); "
     "durante la sessione arriva solo il testo, all'invio"],
    ["zsh installata dopo AMS", "serve rilanciare " + c("install.sh") + " per la riga nello zshrc"],
    ["l'intestazione scritta all'invio usa la lingua con cui è partita la shell", "se l'utente cambia " + c("LANG")
     + " dentro la shell (per esempio nel " + c(".bashrc") + "), l'intestazione resta nella lingua del login; domanda "
     "e risposte seguono quella nuova"],
    ["lingue: italiano e inglese", "le altre lingue vedono l'inglese; i manuali sono solo in italiano"],
    ["date di " + c("--expires") + " a parole in inglese", "le interpreta " + c("date -d") + "; il formato ISO funziona sempre"],
    [c("su") + " non cambia il proprietario del terminale", c("ams send") + " non scrive in quel terminale all'invio"],
    ["se l'agente del desktop muore, la sua finestra resta aperta", "l'agente che lo sostituisce apre una seconda "
     "finestra per lo stesso messaggio; la prima non registra più nulla"],
], "«TAB» — Limiti noti")

S2 = table(["Punto", "Stato"], [
    ["invio programmato (" + c("--at") + ")", "previsto, seconda versione"],
    ["modelli di messaggio riutilizzabili", "previsto, seconda versione"],
    [c("ams remind") + ": sollecito manuale", "previsto, seconda versione"],
    ["esportazione CSV o JSON per audit", "previsto, seconda versione"],
    ["interfaccia a schede per l'amministratore", "previsto, seconda versione"],
    ["pacchetti deb e rpm", "previsto, seconda versione"],
    ["risposta dell'utente all'amministratore", "non prevista (decisione del 30 settembre)"],
    ["riscrittura in un linguaggio compilato", "solo se il prototipo mostrerà limiti concreti"],
], "«TAB» — Punti aperti")

CHAPTER = ("Limiti noti e punti aperti", [
    ("Limiti noti", S1),
    ("Punti aperti", S2),
])
