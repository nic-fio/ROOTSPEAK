# Prove di AMS nella macchina di prova

- Data: 2026-09-30 09:44:19 UTC
- AMS - Advanced Messaging System for linux 0.1.0
- Sistema: Debian GNU/Linux 13 (trixie), container con systemd
- Esito: **41 riusciti, 0 falliti, 1 non provati** su 42 scenari

| Codice | Area | Scenario | Atteso | Esito | Misure / dettagli |
|---|---|---|---|---|---|
| A1 | Accesso | root invia un messaggio | invio riuscito | OK | Messaggio 1 inviato a 1 utente. |
| A2 | Accesso | un amministratore (gruppo sudo) invia: ams si rilancia con sudo | invio riuscito, mittente admin | OK | secondi 0.101; from: admin |
| A3 | Accesso | un utente normale non può eseguire ams | permesso negato, nessun messaggio | OK | runuser: failed to execute /usr/local/bin/ams: Permission denied |
| A4 | Accesso | un utente normale non può aprire nemmeno la guida | permesso negato | OK | runuser: failed to execute /usr/local/bin/ams: Permission denied |
| B1 | Destinatari | un utente | mario | OK | ['mario'] |
| B2 | Destinatari | lista con un doppione | anna, mario (una volta) | OK | ['anna', 'mario'] |
| B3 | Destinatari | gruppo @sviluppo | anna, mario | OK | ['anna', 'mario'] |
| B4 | Destinatari | all: utenti umani, esclusi root e chi ha nologin | admin, anna, luca, mario | OK | ['admin', 'anna', 'luca', 'mario'] |
| B5 | Destinatari | online: solo chi ha una sessione aperta | luca | OK | ['luca'] |
| B6 | Destinatari | utente inesistente | errore, nessun messaggio creato | OK | ams: utente inesistente: pippo |
| B7 | Destinatari | gruppo senza membri | errore «nessun destinatario» | OK | ams: nessun destinatario |
| C1a | Consegna | utente scollegato: la copia aspetta nella casella | consegnato | OK | consegnato |
| C1b | Consegna | al login il messaggio e la domanda compaiono prima del primo prompt | testo e domanda al login | OK | secondi_dal_login 0.367 |
| C1c | Consegna | conferma al login | confermato (terminale) | OK | confermato il 30/09 09:43 (terminale pts/2) |
| C2a | Consegna | utente collegato: il testo compare nel suo terminale | testo nel terminale | OK | secondi_invio 0.09, secondi_al_terminale 0.14 |
| C2b | Consegna | stato dopo la scrittura nel terminale | consegnato, scritto su 1 terminale | OK | consegnato, scritto su 1 terminale |
| C2c | Consegna | premendo Invio compare la domanda | domanda al prompt successivo | OK | secondi 0.063 |
| C3 | Consegna | sessione ssh senza terminale: non viene toccata, la copia va nella casella | invio riuscito, consegnato, nessun terminale scritto | OK | consegnato |
| C4a | Consegna | due sessioni aperte: il testo compare in entrambe | testo in 2 terminali | OK | consegnato, scritto su 2 terminali |
| C4b | Consegna | confermando in una sessione, la domanda nell'altra si ferma | «già confermato altrove» nell'altra | OK | secondi 0.905 |
| D1 | Conferma | l'utente rimanda | consegnato, rimandato il … | OK | consegnato, scritto su 1 terminale, rimandato il 30/09 09:43 |
| D2 | Conferma | dopo il rinvio, al prompt solo un promemoria | «Hai 1 messaggio…», nessuna domanda | OK | true [AMS] Hai 1 messaggio dell'amministratore da confermare. luca@e26a25679be4:~$  |
| D3 | Conferma | al login successivo il rinvio non vale: la domanda torna | domanda al login | OK |  |
| D4 | Conferma | conferma registrata con data e canale | «EPOCH terminale pts/N» | OK | 1790761408 terminale pts/7 |
| E1 | Scadenza | un messaggio scaduto non viene mostrato al login | nessun testo | OK |  |
| E2 | Scadenza | stato di un messaggio scaduto | consegnato, non confermato (scaduto) | OK | consegnato, non confermato (scaduto) |
| E3 | Ritiro | ritiro con la domanda in attesa: la domanda si interrompe | «L'amministratore ha ritirato il messaggio» | OK | secondi 1.002 |
| E4 | Ritiro | stato dopo il ritiro | consegnato, non confermato (ritirato) | OK | consegnato, non confermato (ritirato) |
| E5 | Ritiro | un messaggio ritirato prima del login non viene mostrato | nessun testo | OK |  |
| F1 | Guasti | la copia per un utente non si può scrivere: gli altri la ricevono | errore, anna «inviato, non consegnato», mario consegnato | OK | ams: messaggio 1 non consegnato a: anna (vedi il registro; il prossimo comando ams riproverà) ¦ anna: inviato, non consegnato: la copia non è stata scritta (vedi il registro; il prossimo comando ams r |
| F2 | Guasti | guasto risolto: il comando successivo completa la consegna | anna consegnato | OK | ams: completata la consegna del messaggio 1 a 1 destinatari |
| F3 | Guasti | ams send ucciso a metà (SIGKILL): il comando successivo completa | tutte le copie consegnate, nessun segno di invio incompleto | OK | consegnati_al_kill 15, destinatari 64, secondi_recupero 2.538; consegnati prima 15/64, dopo 64/64; ams: completata la consegna del messaggio 2 a 49 destinatari |
| F5 | Guasti | ams list ripetuto mentre ams send consegna: il recupero non interferisce | una consegna per destinatario, nessun doppione, invio completo | OK | ams_list_durante_invio 25; 64 consegne annotate per 64 destinatari, 64 distinte |
| F4 | Guasti | la conferma non si può scrivere: il messaggio resta e l'utente è avvisato | avviso; stato consegnato; messaggio ancora nella casella | OK | consegnato, scritto su 1 terminale |
| G1 | Sicurezza | la casella è un collegamento a /etc: root non ci scrive | nessun file 2 in /etc; mario «inviato, non consegnato» | OK | ams: messaggio 2 non consegnato a: mario (vedi il registro; il prossimo comando ams riproverà) |
| G2 | Sicurezza | sequenze di escape nel testo: non arrivano al terminale | nessun ESC nel testo ricevuto | OK | 'Testo rosso   fine\r\r\n───────────────────' |
| G3 | Sicurezza | conferma fabbricata con escape e 500 byte: ams status resta pulito | nessun ESC nell'uscita, al massimo 200 byte letti | OK | luca             confermato il 01/01 00:00 (finto00000000000000000000000000000000000000000000000000000000000000000000000 |
| G4 | Sicurezza | un utente normale con AMS_TEST=1 non ottiene nulla | permesso negato | OK | env: ‘/usr/local/bin/ams’: Permission denied |
| H1 | Prestazioni | invio a tutti (54 destinatari) | misura | OK | secondi 2.76, ms_per_destinatario 51.1 |
| H2 | Prestazioni | ams list con 10 messaggi × 54 destinatari | misura (punto 15 della revisione) | OK | secondi 0.69 |
| H3 | Prestazioni | ams status di un messaggio con 54 destinatari | misura | OK | secondi 0.73 |
| I1 | Desktop | finestra di conferma nella sessione grafica | finestra «Ho letto» | NON PROVATO | il container non ha una sessione grafica: la finestra si prova nella VM (tests/vm) |
