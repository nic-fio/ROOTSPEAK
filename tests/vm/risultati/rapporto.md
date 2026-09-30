# Prove di AMS nella VM con desktop

- Data: 2026-09-30 12:12:50 UTC
- AMS - Advanced Messaging System for linux 0.1.0
- Sistema: Debian GNU/Linux 13 (trixie), VM con GNOME, desktop di sara
- Codice: commit c3eed4f872-modificato, impronta 0aff1a9e1aa5
- Esito: **61 riusciti, 0 falliti, 4 non provati** su 65 scenari

| Codice | Area | Scenario | Atteso | Esito | Misure / dettagli |
|---|---|---|---|---|---|
| A1 | Accesso | root invia un messaggio | invio riuscito | OK | Messaggio 1 inviato a 1 utente. |
| A2 | Accesso | un amministratore (gruppo sudo) invia: ams si rilancia con sudo | invio riuscito, mittente admin | OK | secondi 0.307; from: admin |
| A3 | Accesso | un utente normale non può eseguire ams | permesso negato, nessun messaggio | OK | runuser: failed to execute /usr/local/bin/ams: Permesso negato |
| A4 | Accesso | un utente normale non può aprire nemmeno la guida | permesso negato | OK | runuser: failed to execute /usr/local/bin/ams: Permesso negato |
| B1 | Destinatari | un utente | mario | OK | ['mario'] |
| B2 | Destinatari | lista con un doppione | anna, mario (una volta) | OK | ['anna', 'mario'] |
| B3 | Destinatari | gruppo @sviluppo | anna, mario | OK | ['anna', 'mario'] |
| B4 | Destinatari | all: utenti umani, esclusi root e chi ha nologin | admin, anna, luca, mario, sara | OK | ['admin', 'anna', 'luca', 'mario', 'sara'] |
| B5 | Destinatari | online: solo chi ha una sessione aperta | luca, sara | OK | ['luca', 'sara'] |
| B6 | Destinatari | utente inesistente | errore, nessun messaggio creato | OK | ams: utente inesistente: pippo |
| B7 | Destinatari | gruppo senza membri | errore «nessun destinatario» | OK | ams: nessun destinatario |
| C1a | Consegna | utente scollegato: la copia aspetta nella casella | consegnato | OK | consegnato |
| C1b | Consegna | al login il messaggio e la domanda compaiono prima del primo prompt | testo e domanda al login | OK | secondi_dal_login 0.481 |
| C1c | Consegna | conferma al login | confermato (terminale) | OK | confermato il 30/09 12:09 (terminale pts/2) |
| C2a | Consegna | utente collegato: il testo compare nel suo terminale | testo nel terminale | OK | secondi_invio 0.327, secondi_al_terminale 0.377 |
| C2b | Consegna | stato dopo la scrittura nel terminale | consegnato, scritto su 1 terminale | OK | consegnato, scritto su 1 terminale |
| C2c | Consegna | premendo Invio compare la domanda | domanda al prompt successivo | OK | secondi 0.052 |
| C3 | Consegna | sessione ssh senza terminale: non viene toccata, la copia va nella casella | invio riuscito, consegnato, nessun terminale scritto | OK | consegnato |
| C4a | Consegna | due sessioni aperte: il testo compare in entrambe | testo in 2 terminali | OK | consegnato, scritto su 2 terminali |
| C4b | Consegna | confermando in una sessione, la domanda nell'altra si ferma | «già confermato altrove» nell'altra | OK | secondi 0.909 |
| D1 | Conferma | l'utente rimanda | consegnato, rimandato il … | OK | consegnato, scritto su 1 terminale, rimandato il 30/09 12:09 |
| D2 | Conferma | dopo il rinvio, al prompt solo un promemoria | «Hai 1 messaggio…», nessuna domanda | OK | true [AMS] Hai 1 messaggio dell'amministratore da confermare. luca@ams-desktop:~$  |
| D3 | Conferma | al login successivo il rinvio non vale: la domanda torna | domanda al login | OK |  |
| D4 | Conferma | conferma registrata con data e canale | «EPOCH terminale pts/N» | OK | 1790770160 terminale pts/7 |
| E1 | Scadenza | un messaggio scaduto non viene mostrato al login | nessun testo | OK |  |
| E2 | Scadenza | stato di un messaggio scaduto | consegnato, non confermato (scaduto) | OK | consegnato, non confermato (scaduto) |
| E3 | Ritiro | ritiro con la domanda in attesa: la domanda si interrompe | «L'amministratore ha ritirato il messaggio» | OK | secondi 1.004 |
| E4 | Ritiro | stato dopo il ritiro | consegnato, non confermato (ritirato) | OK | consegnato, non confermato (ritirato) |
| E5 | Ritiro | un messaggio ritirato prima del login non viene mostrato | nessun testo | OK |  |
| F1 | Guasti | la copia per un utente non si può scrivere: gli altri la ricevono | errore, anna «inviato, non consegnato», mario consegnato | OK | ams: messaggio 1 non consegnato a: anna (vedi il registro; il prossimo comando ams riproverà) ¦ anna: inviato, non consegnato: la copia non è stata scritta (vedi il registro; il prossimo comando ams r |
| F2 | Guasti | guasto risolto: il comando successivo completa la consegna | anna consegnato | OK | ams: completata la consegna del messaggio 1 a 1 destinatari |
| F3 | Guasti | ams send ucciso a metà (SIGKILL): il comando successivo completa | tutte le copie consegnate, nessun segno di invio incompleto | OK | consegnati_al_kill 22, destinatari 65, secondi_recupero 3.675; consegnati prima 22/65, dopo 65/65; ams: completata la consegna del messaggio 2 a 43 destinatari |
| F6 | Guasti | cartella dell'utente rimasta di root da un invio interrotto: la consegna la sistema | consegnato | OK | consegnato;  |
| F7 | Guasti | ams revoke durante un invio a molti utenti: l'invio si ferma e nessuna copia resta | nessuna copia nelle caselle, invio interrotto | OK | secondi_attesa_revoke 0.38; copie rimaste: 0; Messaggio 4 ritirato durante l'invio: consegna interrotta. |
| F5 | Guasti | ams list ripetuto mentre ams send consegna: il recupero non interferisce | una consegna per destinatario, nessun doppione, invio completo | OK | ams_list_durante_invio 23; 65 consegne annotate per 65 destinatari, 65 distinte |
| F4 | Guasti | la conferma non si può scrivere: il messaggio resta e l'utente è avvisato | avviso; stato consegnato; messaggio ancora nella casella | OK | consegnato, scritto su 1 terminale |
| G1 | Sicurezza | la casella è un collegamento a /etc: root non ci scrive | nessun file 2 in /etc; mario «inviato, non consegnato» | OK | ams: messaggio 2 non consegnato a: mario (vedi il registro; il prossimo comando ams riproverà) |
| G2 | Sicurezza | sequenze di escape nel testo: non arrivano al terminale | nessun ESC nel testo ricevuto | OK | 'Testo rosso   fine\r\r\n───────────────────' |
| G3 | Sicurezza | conferma fabbricata con escape e 500 byte: ams status resta pulito | nessun ESC nell'uscita, al massimo 200 byte letti | OK | luca             confermato il 01/01 00:00 (finto00000000000000000000000000000000000000000000000000000000000000000000000 |
| G4 | Sicurezza | un utente normale con AMS_TEST=1 non ottiene nulla | permesso negato | OK | env: ‘/usr/local/bin/ams’: Permesso negato |
| J1 | Registro | ams log: la storia del messaggio | invio, consegne, rinvio, conferma, ritiro | OK | 6 eventi |
| J2 | Registro | la conferma nel journal porta l'utente che l'ha scritta (_UID) | _UID 1001 | OK | 1001 1001 |
| J3 | Registro | un evento scritto da un utente a nome di un altro: ams log lo segnala | «non attendibile: scritto da UID 1003» | OK | 2026-09-30 12:10:18  [non attendibile: scritto da UID 1003] utente anna: confermata la lettura del messaggio 1 (desktop) |
| K-zsh | Shell | zsh: utente di prova zeno | presente | NON PROVATO | utente assente |
| K-fish | Shell | fish: utente di prova fabio | presente | NON PROVATO | utente assente |
| K-ksh | Shell | ksh: utente di prova kora | presente | NON PROVATO | utente assente |
| K-dash | Shell | dash: utente di prova dario | presente | NON PROVATO | utente assente |
| L1 | Lingua | all'invio ciascun terminale riceve l'intestazione nella lingua del suo utente | luca in inglese, mario in italiano, testo non tradotto | OK |  |
| L2 | Lingua | la domanda e la conferma nella lingua dell'utente | domanda in inglese, «y» conferma | OK | confermato il 30/09 12:10 (terminale pts/14) |
| L3 | Lingua | un amministratore in inglese legge ams status in inglese | USER STATE, confirmed on … (terminal …) | OK | luca             confirmed on 30/09 12:10 (terminal pts/14) / mario            delivered, written to 1 terminal |
| L4 | Lingua | il registro è nella lingua del sistema; ams log lo riscrive in quella di chi legge | journal in italiano; ams log in inglese e in italiano | OK | 2026-09-30 12:10:26  user luca: confirmed reading message 1 (terminal pts/14) |
| H1 | Prestazioni | invio a tutti (55 destinatari) | misura | OK | secondi 5.03, ms_per_destinatario 91.4 |
| H2 | Prestazioni | ams list con 10 messaggi × 55 destinatari | misura (punto 15 della revisione) | OK | secondi 0.95 |
| H3 | Prestazioni | ams status di un messaggio con 55 destinatari | misura | OK | secondi 1.21 |
| I0 | Desktop | sara ha una sessione grafica con l'agente di AMS attivo (l'avvio dal login automatico lo verifica esegui.sh prima degli scenari) | sessione grafica, agente attivo | OK | sessione 8 |
| I1 | Desktop | la finestra compare da sola dopo l'invio, nella lingua della sessione | finestra «AMS · Messaggio dall'amministratore» (it) con titolo e testo | OK | secondi_alla_finestra 0.69; AMS · Messaggio dall'amministratore ¦ AMS · Messaggio dall'amministratore ¦ Manutenzione · 30/09 12:11  Server spento sabato dalle 8 alle 12. ¦ Più tardi ¦ Ho |
| I2 | Desktop | «Ho letto»: la finestra si chiude e la conferma è registrata | confermato (desktop) | OK | confermato il 30/09 12:11 (desktop) |
| I8 | Desktop | agente assente: ams send lo avvia (systemd-run) e la finestra compare | agente attivo, finestra | OK | secondi_alla_finestra 0.7 |
| I3 | Desktop | «Più tardi»: la finestra si chiude, il messaggio resta consegnato | consegnato, rimandato il … | OK | consegnato, rimandato il 30/09 12:11 |
| I4 | Desktop | dopo il rinvio (1 minuto per la prova) la finestra ricompare | finestra di nuovo, dopo circa 60 s | OK | secondi_alla_ricomparsa 60.38 |
| I5 | Desktop | conferma da un terminale con la finestra aperta: la finestra si chiude da sola | finestra chiusa, confermato (terminale) | OK | secondi_alla_chiusura 0.42; confermato il 30/09 12:12 (terminale pts/16) |
| I6 | Desktop | ritiro con la finestra aperta: la finestra si chiude da sola | finestra chiusa | OK | secondi_alla_chiusura 0.71 |
| I7 | Desktop | due messaggi: le finestre compaiono una dopo l'altra, dal più vecchio | «Primo di due», poi «Secondo di due», entrambi confermati | OK |  di due ¦ Più tardi ¦ Ho letto →  di due ¦ Più tardi ¦ Ho letto; confermato il 30/09 12:12 (desktop) |
| I10 | Desktop | «Ho letto» e subito fuori dalla sessione (0,1 s): la conferma resta | confermato (desktop) | OK | confermato il 30/09 12:12 (desktop) |
| I9 | Desktop | messaggio mandato a desktop chiuso: la finestra compare al login grafico | finestra dopo il login automatico | OK | secondi_dal_riavvio_del_login 2.91; re ¦ 30/09 12:12  In attesa del login ¦ Più tardi ¦ Ho letto |
