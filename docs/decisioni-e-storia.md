# AMS — decisioni e storia

> Perché AMS è fatto così: il contesto, le decisioni e la storia del progetto.
> Il funzionamento in dettaglio è nel [manuale tecnico](manuale-tecnico.html),
> l'uso nel [manuale utente](manuale-utente.html) (file HTML: vanno aperti in un browser).
> Stato: **prototipo 0.1.0 funzionante**, provato dal vivo su Debian 13 con GNOME 48 su Wayland (settembre 2026).

---

## 1. Cos'è

**AMS - Advanced Messaging System for linux** è uno strumento con cui gli
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
| **Due livelli: `info` e `ack`** | `ack` chiede la conferma e insiste; `info` avvisa e basta. |
| **Nessun blocco** | Proposto e scartato un livello `block` (sessione chiusa se l'utente non conferma entro un tempo di grazia): «butta fuori gli utenti dal sistema, troppo estremo». Scartato anche il blocco a schermo intero: invasivo e non realizzabile su GNOME Wayland. Il blocco peggiorerebbe proprio il messaggio più comune («riavvio tra 10 minuti, salvate il lavoro») e romperebbe gli script. |
| **Ricezione automatica** | L'utente non deve conoscere né digitare comandi: finestra sul desktop, testo e domanda nel terminale, tutto da solo. |
| **Gli utenti non hanno il comando `ams`** | Ricevono e confermano soltanto. Il codice che gira come utente è l'aiutante interno `ams-user`, fuori dal PATH. Conseguenza accettata: dopo la conferma un messaggio non si può rileggere. |
| **Nessuna classe di permessi in AMS** | Proposte e scartate: un gruppo `ams-admin`, poi un gruppo `ams` popolato con i membri dei gruppi root e admin. Duplicherebbero il gruppo degli amministratori e invecchierebbero. `ams` è installato `root:sudo` (o `wheel`) con permessi `750`. |
| **`ams` gira sempre come root, senza eccezioni** | Si rilancia da solo con sudo prima di qualunque comando, **compresi la guida e la versione**: regola scelta dall'utente, a costo di chiedere la password anche per l'aiuto. |
| **Nessun demone** | Senza il livello `block` non serve: `ams send` consegna subito, l'aggancio della shell e l'agente del desktop fanno il resto. |
| **La prima conferma vale per tutti i canali** | Emerso da una prova: l'utente doveva confermare due volte (finestra e terminale). Ora la domanda nel terminale si accorge della conferma dal desktop, e la conferma è scritta in modo esclusivo (`set -C`). |
| **Agente del desktop svegliato da un segnale** | Emerso da una prova: la finestra arrivava dopo 3-4 secondi (controllo ogni 10 s). `ams send` manda `SIGUSR1` all'agente: la finestra compare subito, e il controllo periodico passa a 60 s per risparmiare batteria. |
| **Avvisi `info` prima delle finestre di conferma** | Emerso da una prova: al login un avviso restava in coda dietro una finestra e sembrava una seconda richiesta. |
| **zenity per la finestra** | Pacchetto standard e piccolo; una finestra che resta aperta finché l'utente non sceglie. Le notifiche di GNOME possono essere ignorate o sparire da sole: inaffidabili per la conferma. |
| **Prototipo in bash** | Per validare il flusso con gli strumenti del sistema. Una riscrittura in un linguaggio compilato si farà solo se emergeranno limiti concreti. |
| **Guida integrata come quella di MTERM, niente man page** | «Non voglio un sistema man, ma un sistema molto più evoluto»: guida a schede in un terminale, pagina in stile manuale con un pager se il terminale è piccolo, testo semplice in una pipe. Un controllo (`tools/check-docs.py`) tiene allineati guida e manuale. |
| **Manuali HTML in italiano, tema chiaro** | Stessa struttura, stile e palette dei manuali di NESH; nomi dei file e impianto (manuale utente, manuale tecnico, decisioni e storia, `CLAUDE.md`) come in MTERM. |
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
| 30 settembre 2026 | Guida integrata interattiva sul modello di MTERM, sempre come root; `tools/check-docs.py` e `tests/help-tui.py`. Manuale tecnico, questo documento e `CLAUDE.md`. |
