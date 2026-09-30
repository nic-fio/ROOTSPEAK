from build import c, p, table

S1 = table(["Tema", "Regola"], [
    ["lingua", "nomi, commenti e documentazione in italiano; i testi per chi usa AMS sono in inglese nel codice, "
     "dentro " + c("T(\"…\")") + ", e tradotti in " + c("po/") + " (capitolo 10.4)"],
    ["C", "C17 con " + c("_GNU_SOURCE") + "; tutti gli avvisi sono errori; niente array a lunghezza variabile; ogni "
     "descrittore con " + c("O_CLOEXEC") + "; memoria con " + c("xmalloc") + " e testi con " + c("buf_t")
     + " (niente buffer di lunghezza fissa per dati che vengono da fuori)"],
    ["file", c("leggi_file") + " legge solo file normali, fino a una misura massima, e senza seguire collegamenti dove "
     "conta; " + c("scrivi_atomico") + " scrive, porta su disco e rinomina"],
    ["errori", c("die") + ": stampa " + c("ams: …") + " ed esce con 1; " + c("avviso") + " per gli avvertimenti"],
    ["registro", c("evento") + ": " + c("sd_journal_send") + " con i campi " + c("AMS_*")],
    ["accessi alle caselle", "sempre con " + c("come_utente")],
    [c("ams-user"), "gira dentro il prompt dell'utente: non esce mai con un errore che interrompa la shell"],
    ["manuali", "si modificano i sorgenti in " + c("docs/sorgenti/") + " e si rigenerano; mai a mano i file HTML"],
    ["commit", "identità locale del repository (noreply di GitHub), messaggi in italiano"],
], "«TAB» — Le convenzioni") + \
    p("La versione è " + c("AMS_VERSION") + " in " + c("src/comune.h") + ": i manuali la leggono da lì.")

CHAPTER = ("Convenzioni", [
    ("Regole di scrittura", S1),
])
