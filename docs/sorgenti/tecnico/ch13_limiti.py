from build import c, table

S1 = table(["Limite", "Conseguenza"], [
    ["la domanda al prompt esiste solo in bash", "zsh e fish ricevono il testo all'invio, non la domanda"],
    ["date di " + c("--expires") + " a parole in inglese", "le interpreta " + c("date -d") + "; il formato ISO funziona sempre"],
    [c("ams list") + " usa un " + c("runuser") + " per destinatario e messaggio", "lento: circa 6 s per 10 messaggi a 54 "
     "destinatari (misura della suite dal vero)"],
    ["le caselle crescono", "i messaggi letti restano in " + c("read/")],
    ["l'agente legge " + c("ams.conf") + " solo all'avvio", "le modifiche valgono sul desktop dal login successivo"],
    [c("su") + " non cambia il proprietario del terminale", c("ams send") + " non scrive in quel terminale all'invio"],
], "«TAB» — Limiti noti")

S2 = table(["Punto", "Stato"], [
    ["invio programmato (" + c("--at") + ")", "previsto, seconda versione"],
    ["modelli di messaggio riutilizzabili", "previsto, seconda versione"],
    [c("ams remind") + ": sollecito manuale", "previsto, seconda versione"],
    ["esportazione CSV o JSON per audit", "previsto, seconda versione"],
    ["interfaccia a schede per l'amministratore", "previsto, seconda versione"],
    ["pacchetti deb e rpm", "previsto, seconda versione"],
    ["interfaccia in inglese", "previsto, seconda versione"],
    ["risposta dell'utente all'amministratore", "da decidere"],
    ["riscrittura in un linguaggio compilato", "solo se il prototipo mostrerà limiti concreti"],
], "«TAB» — Punti aperti")

CHAPTER = ("Limiti noti e punti aperti", [
    ("Limiti noti", S1),
    ("Punti aperti", S2),
])
