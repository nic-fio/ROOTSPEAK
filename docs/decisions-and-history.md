# AMS — decisioni e storia

> Perché AMS è fatto così: il contesto, le decisioni e la storia del progetto.
> Il funzionamento in dettaglio è nel [manuale tecnico](Technical%20Manual.html),
> l'uso nel [manuale utente](User%20Manual.html) (file HTML in inglese: vanno aperti in un browser).
> Stato: **prototipo 0.1.0 funzionante**, provato dal vivo su Debian 13 con GNOME 48 su Wayland (settembre 2026).

---

## 1. Cos'è

**AMS - Advanced Messaging System** è uno strumento con cui gli
amministratori di una macchina Linux mandano messaggi di testo agli utenti e
sanno chi ha confermato di averli letti.

```
amministratore ── sudo ams send ──> casella dell'utente ──> terminali (testo + domanda al prompt)
                                                      ├──> desktop (finestra «Ho letto» / avviso)
                                                      └──> al login, se non è collegato
```

## 2. Contesto e ricerca

- L'esigenza: raggiungere gli utenti di una macchina con avvisi degli
  amministratori, possibilmente con **conferma di lettura**.
- Prima di progettare si è verificato che non esistesse già qualcosa di
  adatto. Esistono solo pezzi separati:
  - `wall` e `write`: scrivono solo sui terminali dei collegati, senza conferma;
  - `notify-send` via `systemd-run --user`: notifiche sul desktop, senza stato;
  - `systembus-notify`: notifiche dal bus di sistema, senza pulsanti né conferme;
  - `/etc/motd`, il `Banner` di sshd, il banner di GDM, i banner di consenso STIG:
    testi fissi al login, senza stato per utente.
- Nessuno tiene uno **stato per messaggio e per utente** né risponde alla
  domanda «chi non ha ancora letto?». AMS mette insieme i pezzi e aggiunge
  proprio questo.

## 3. Le sessioni di un utente

Si è partiti dalla classificazione «testuale/grafica × locale/remota» e la si è
raffinata: pseudo-terminali ssh con e senza pty, terminali dentro il desktop,
tmux staccato, X11 contro Wayland, desktop remoto che condivide la sessione
locale o ne crea una nuova, sessioni non interattive (cron, scp, servizi), `su`.
Conclusione: la domanda utile non è «come è collegato l'utente» ma **«su quali
canali posso raggiungerlo adesso»** (terminale, desktop, nessuno), e la fonte
affidabile è **logind**, non utmp.

## 4. Decisioni

| Decisione | Perché |
|---|---|
| **Una sola macchina, inviano solo gli amministratori** | Lo strumento deve restare «semplice»: niente rete, niente messaggi tra utenti. |
| **Ogni messaggio chiede la conferma; tre stati** | All'inizio c'erano due livelli, `ack` (con conferma) e `info` (solo avviso). Il 30 settembre, lavorando sulla revisione avversariale, l'utente ha deciso: «TUTTI i messaggi hanno 3 stati: inviato, consegnato, confermato. L'utente destinatario deve SEMPRE confermare la lettura», scegliendo di semplificare l'architettura. Sparisce lo stato «mostrato», che confondeva consegna e lettura (revisione, punto 6). Per gli avvisi brevi si usa `--expires`: dopo la scadenza il messaggio non viene più mostrato né sollecitato. |
| **Nessun blocco** | Proposto e scartato un livello `block` (sessione chiusa se l'utente non conferma entro un tempo di grazia): «butta fuori gli utenti dal sistema, troppo estremo». Scartato anche il blocco a schermo intero: invasivo e non realizzabile su GNOME Wayland. Il blocco peggiorerebbe proprio il messaggio più comune («riavvio tra 10 minuti, salvate il lavoro») e romperebbe gli script. |
| **Ricezione automatica** | L'utente non deve conoscere né digitare comandi: finestra sul desktop, testo e domanda nel terminale, tutto da solo. |
| **Gli utenti non hanno il comando `ams`** | Ricevono e confermano soltanto. Il codice che gira come utente è l'aiutante interno `ams-user`, fuori dal PATH. Conseguenza accettata: dopo la conferma un messaggio non si può rileggere. |
| **Nessuna classe di permessi in AMS** | Proposte e scartate: un gruppo `ams-admin`, poi un gruppo `ams` popolato con i membri dei gruppi root e admin. Duplicherebbero il gruppo degli amministratori e invecchierebbero. `ams` è installato `root:sudo` (o `wheel`) con permessi `750`. |
| **`ams` gira sempre come root, senza eccezioni** | Si rilancia da solo con sudo prima di qualunque comando, **compresi la guida e la versione**: regola scelta dall'utente, a costo di chiedere la password anche per l'aiuto. |
| **Nessun demone** | Senza il livello `block` non serve: `ams send` consegna subito, l'aggancio della shell e l'agente del desktop fanno il resto. |
| **La prima conferma vale per tutti i canali** | Emerso da una prova: l'utente doveva confermare due volte (finestra e terminale). Ora la domanda nel terminale si accorge della conferma dal desktop, e la conferma è scritta in modo esclusivo (`set -C`). |
| **Agente del desktop svegliato da un segnale** | Emerso da una prova: la finestra arrivava dopo 3-4 secondi (controllo ogni 10 s). `ams send` manda `SIGUSR1` all'agente: la finestra compare subito, e il controllo periodico passa a 60 s per risparmiare batteria. |
| **Avvisi `info` prima delle finestre di conferma** | Emerso da una prova: al login un avviso restava in coda dietro una finestra e sembrava una seconda richiesta. Superata dalla decisione di chiedere sempre la conferma. |
| **zenity per la finestra** | Pacchetto standard e piccolo; una finestra che resta aperta finché l'utente non sceglie. Le notifiche di GNOME possono essere ignorate o sparire da sole: inaffidabili per la conferma. |
| **Prototipo in bash** | Per validare il flusso con gli strumenti del sistema. Una riscrittura in un linguaggio compilato si farà solo se emergeranno limiti concreti. Superata il 30 settembre: vedi la riga seguente. |
| **Riscrittura in C** | Decisione dell'utente (30 settembre), dopo la seconda revisione: i difetti trovati nascevano quasi tutti dal bash (gare fra controllo e uso, tempi massimi, un processo per operazione). Proposto Rust per evitare la corruzione della memoria in un programma di root che legge file degli utenti; l'utente ha scelto il C, con difese obbligatorie (avvisi, analisi statica, sanitizer, fuzzing). Tutto viene riscritto; restano script gli agganci delle shell. |
| **TUI per gli amministratori** | Decisione dell'utente (30 settembre): per gli amministratori, aperta da `ams` senza argomenti, per consultare, agire, scrivere e inviare, con aggiornamento automatico. Discutendo le anteprime l'utente ha notato che erano comparsi stati inventati («in attesa», «completo», poi «invio incompleto» e «annullato», che erano segni tecnici del recupero finiti nella specifica senza passare da lui): gli stati sono solo i tre decisi, ritirato e scaduto sono proprietà, e un messaggio si riassume con i conteggi dei destinatari nei tre stati, a parole e con una barra. La specifica è stata corretta di conseguenza. |
| **Lingue con gettext** | Decisione dell'utente (30 settembre): formato e strumenti standard. La lettura dei `.mo` è di AMS e non della libintl, perché con la libintl una lingua non installata nel sistema resta non tradotta anche forzando `LANGUAGE` (provato), mentre root deve poter scrivere a ogni terminale nella lingua del suo utente. |
| **Guida integrata come quella di MTERM, niente man page** | «Non voglio un sistema man, ma un sistema molto più evoluto»: guida a schede in un terminale, pagina in stile manuale con un pager se il terminale è piccolo, testo semplice in una pipe. Un controllo (`tools/check-docs.py`) tiene allineati guida e manuale. |
| **Manuali sul modello di IR_Service** | Una prima versione copiata dai manuali di NESH è stata bocciata dall'utente su tutto (grafici, aspetto, testi, apertura): «Ancora una volta i manuali html fanno schifo». Il riferimento indicato è il Manuale Tecnico di IR_Service: i manuali sono generati da sorgenti Python (un file per capitolo) in due file HTML autosufficienti, con copertina, indice laterale, schemi SVG e tabelle numerate, senza script. Il riferimento dei comandi è generato dai testi della guida integrata. |
| **Manuali in inglese** | Decisione dell'utente (30 settembre): i due manuali e i loro sorgenti sono tradotti in inglese e si chiamano `User Manual.html` e `Technical Manual.html`; struttura, colori e stile restano quelli di prima. Tutto il resto (codice, commenti, messaggi, questo documento) resta com'è. Il riferimento dei comandi del manuale utente viene quindi dai testi di partenza inglesi della guida, e `tools/check-docs.py` lo confronta con quelli. |
| **Domanda di conferma in tutte le shell** | Decisione dell'utente (30 settembre): «sì, per tutte le shell». Proposta accolta in pratica: domanda a ogni prompt per bash, zsh e fish; al login per ogni shell che legge `/etc/profile`; testo all'invio per qualunque shell (alcune shell, come `dash` e `tcsh`, non hanno un aggancio prima del prompt). Fatto il 30 settembre: `ams.bash`, `ams.zsh`, `ams.fish` e il ramo sh di `profile.d/ams.sh`, provati nella macchina di prova (scenari K). |
| **Gli utenti non rispondono** | Decisione dell'utente (30 settembre): «non è previsto al momento» che gli utenti rispondano ai messaggi. |
| **Lingua dell'utente** | Decisione dell'utente (30 settembre): domanda, finestra, pulsanti e avvisi nella lingua di ciascun destinatario (`LANG`); i comandi dell'amministratore nella sua lingua; il testo del messaggio resta com'è. Fatto il 30 settembre: italiano e inglese in `lib/lingue/`, inglese come lingua di ripiego; il registro di sistema nella lingua della macchina, riscritto da `ams log` in quella di chi legge. |
| **Nessuna licenza** | Repository privato, copyright nic-fio. |

## 5. Scelte tecniche nate dalle prove

- **Comando in `/usr/local/bin`, non in `sbin`**: su Debian gli utenti non root
  non hanno `sbin` nel PATH, e `ams` risultava «comando non trovato».
- **Prove di ssh con `ssh utente@localhost`, non con `su`**: con `su` il
  terminale resta di chi l'ha aperto, e `ams send` non lo trova.
- **Due finestre uguali** in una prova erano un messaggio inviato due volte
  (due ID in `ams list`), non un difetto: nessuna correzione.
- **Esempio di `--expires` corretto**: `date -d` non capisce `"sabato 12:00"`;
  la guida usa il formato ISO.
- **Ritiro con finestra o domanda aperte**: si chiudono da sole e non
  registrano la conferma di un messaggio ritirato.

## 6. Storia

| Quando | Cosa |
|---|---|
| 29 settembre 2026, sera | Classificazione delle sessioni, scopo, ricerca di strumenti esistenti, lista delle funzionalità, decisioni su livelli, blocco, comandi degli utenti e permessi. Prototipo in bash e installazione; prime prove dal vivo (finestra, terminale, conferma unica, sveglia dell'agente). Repository privato su GitHub. |
| 29 settembre 2026, notte | Prove con un secondo utente: consegna al login grafico, avvisi `info`, terminale via ssh. Manuale utente in HTML sullo stile di NESH; versione 0.1.0. |
| 30 settembre 2026 | Guida integrata interattiva sul modello di MTERM, sempre come root; `tools/check-docs.py` e `tests/help-tui.py`. Manuale tecnico, questo documento e `CLAUDE.md`. Manuali rifatti da capo sul modello di IR_Service, con generatore in `docs/sorgenti/`. Revisione avversariale di due modelli e lavoro punto per punto: conferme mai perse, consegna verificata con recupero, tre stati per ogni messaggio (niente più livelli), suite dal vero in container e in VM con desktop sul server delle prove, eventi strutturati e `ams log`, `ams purge`, configurazione come dati, capitolo «Specifica». Domanda di conferma in tutte le shell (bash, zsh, fish; sh, dash, ksh al login) e AMS nella lingua di ciascuno (italiano, inglese). |
| 30 settembre 2026, pomeriggio | Seconda revisione (due revisori) e correzioni: ritiro serializzato con l'invio, conferme successive al ritiro, terminale controllato dopo l'apertura, durata dopo un'interruzione di corrente, cancellazione in un colpo solo, caselle anomale. Riscrittura in C (versione 0.2.0) con gettext: stesse prove, tutte superate (motore, container, VM in italiano e in inglese, guida), più sanitizer, analisi statica e fuzzing; tolto il prototipo in bash. |
| 30 settembre 2026, sera | TUI per gli amministratori (`ams` da solo), dopo anteprime discusse con l'utente: correzione degli stati inventati e della specifica; `ams remind`; `ams list` con i destinatari nei tre stati. Prove: `tests/tui.py`, scenari D5, T1-T3, I11; la VM ha trovato un sollecito perso se arrivava entro un secondo da «Più tardi» (l'agente ora registra la risposta appena zenity si chiude). |
| 30 settembre 2026, notte | Struttura standard comune ai 7 progetti, decisa dal proprietario: nomi di file e cartelle in inglese (`docs/sources/`, `tests/results/`, `tests/unit-tests.c`, `tools/fingerprint.sh`, `run.sh` al posto di `esegui.sh`; questo documento si chiamava `decisioni-e-storia.md`), con il contenuto invariato; `NOTICE.md`, `docs/index.html`, `tools/setup-dev.sh`, `tools/backup.sh`, `make test`, `make docs`, `make docs-check`, CI su GitHub, il logo in `logos/`. |
