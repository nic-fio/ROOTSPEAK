# Revisione avversariale del 30 settembre 2026

Il progetto è stato sottoposto a due revisioni critiche indipendenti, fatte da
due modelli linguistici di frontiera sul manuale tecnico della versione 0.1.0:

- **Revisione A** — «Relazione critica su AMS 0.1.0» (24 punti e piano di risanamento);
- **Revisione B** — «Relazione critica senza sconti — AMS v0.1.0» (file ricevuto
  troncato: si interrompe al punto 5.1).

I punti sulla lingua dell'interfaccia sono esclusi da questo elenco: verranno
trattati a parte. Ogni affermazione concreta è stata verificata sul codice
prima di essere accolta. Le voci [2] del README restano congelate finché i
gruppi A–D non sono chiusi (revisione A, punto 23).

Stato: **aperto**, **fatto**, **non accolto**.

## A. Difetti reali, verificati nel codice

| # | Punto | Fonte | Stato |
|---|---|---|---|
| 1 | Se la conferma non si poteva scrivere (disco pieno, permessi), AMS la trattava come «già confermata»: il messaggio passava tra i letti senza conferma e l'utente leggeva «Confermato». Ora la conferma è pubblicata con `ln` (esclusivo), un fallimento lascia il messaggio nella casella, avvisa l'utente e va nel registro. Test: `tests/engine.sh`, gruppo 1 (fallisce con il codice precedente). | B 3.1, A 20 | fatto |
| 2 | Un `ams send` interrotto a metà lasciava destinatari senza copia, mai recuperati. Ora ogni consegna è verificata e annotata per destinatario; `sent/ID/incomplete` resta finché manca una copia e il comando `ams` successivo completa l'invio; un guasto per un destinatario non ferma gli altri; nuovo stato «non consegnato», distinto da «da confermare»; un invio interrotto prima del salvataggio viene annullato. Test: `tests/engine.sh`, gruppo 2 (6 controlli falliscono con il codice precedente). La suite dal vero ha poi trovato che il recupero, lanciato durante un invio ancora in corso, consegnava in parallelo e annotava doppioni: ora `ams send` tiene un lock (`sent/ID/lock`) e il recupero salta gli invii in corso (scenari F3 e F5; 2 controlli di `tests/engine.sh`). | A 4 | fatto |
| 3 | Un agente appena partito moriva se svegliato mentre partiva (20 su 20 in una prova). Ora prepara la ricezione del segnale come prima istruzione e, quando è pronto, scrive il suo PID in `ams-agent.pronto`; `ams send` sveglia solo quel PID (con `pkill -F` e la riga di comando esatta, come l'utente) e altrimenti avvia un agente. Test: `tests/engine.sh`, gruppo 5. | A 11 | fatto |
| 4 | Una finestra o una domanda aperte prima della scadenza accettavano la conferma dopo. Ora alla scadenza si chiudono; `ack` rifiuta un messaggio scaduto; `ams status` non conta una conferma con ora successiva alla scadenza della copia di riferimento (`sent/`), anche se l'utente ha alterato la propria copia. Test: `tests/engine.sh`, gruppo 4. | A 15 | fatto |

## B. Specifica e modello

| # | Punto | Fonte | Stato |
|---|---|---|---|
| 5 | Macchina a stati formale, invarianti, comportamento dopo un crash, formato dell'archivio. | A 2, 4, 13, 22; B 3.4 | aperto |
| 6 | Distinguere consegnato, mostrato e confermato. Risolto semplificando, per decisione dell'utente: ogni messaggio chiede la conferma e ogni destinatario ha tre stati, inviato, consegnato (copia nella casella), confermato; lo stato «mostrato» e il livello `info` spariscono. Test: `tests/engine.sh`, gruppo 3. | A 3; B 4.1 | fatto |
| 7 | Registro degli eventi per messaggio (il journal registra già l'UID di chi scrive, non falsificabile). | A 5 | aperto |
| 8 | Dichiarare che la casella dell'utente non è la fonte autorevole. | A 7 | aperto |
| 9 | Semantica rigorosa di ritiro, scadenza e orologio. | A 14, 15, 16 | aperto |
| 10 | Versione del formato dei messaggi: ogni messaggio inizia con `format: 1`. Test: `tests/engine.sh`, gruppo 5. | B 3.3 | fatto |

## C. Robustezza e configurazione

| # | Punto | Fonte | Stato |
|---|---|---|---|
| 11 | Configurazione come dati: `ams_load_conf` accetta solo le chiavi note con interi positivi e non esegue nulla. Test: gruppo 5 (un file con `$(…)` non viene eseguito). | A 18 | fatto |
| 12 | L'agente rilegge la configurazione a ogni giro. | A 19 | fatto |
| 13 | Perimetro supportato dichiarato. | A 9 | aperto |
| 14 | Pulizia delle caselle (i messaggi letti si accumulano). | B 2 | aperto |
| 15 | `list` e `status` lenti. Misurato (scenari H), poi corretto leggendo ogni casella una volta sola per utente (un solo `runuser` per tutte le sue conferme e i suoi rinvii) e le consegne una volta per messaggio: `list` da circa 6 s a circa 0,7 s per 10 messaggi a 54 destinatari, `status` da circa 1,3 s a circa 0,7 s. Non è servito copiare le conferme lato root. | A 8 | fatto |

## D. Test

| # | Punto | Fonte | Stato |
|---|---|---|---|
| 16 | Test automatici del motore: concorrenza, gare, file corrotti, Unicode, testi grandi, strumenti che falliscono. Avviata con `tests/engine.sh`; ogni correzione aggiunge i suoi casi. | A 20 | in corso |
| 17 | Ambiente riproducibile per le prove dal vivo. Fatto in due forme: un container Debian 13 con systemd (`tests/container/esegui.sh`, 42 scenari) e una VM con GNOME su Wayland sul server delle prove (`tests/vm/esegui.sh`, 51 scenari compresi quelli della finestra sul desktop). Esiti e misure in `tests/*/risultati/`. La VM ha trovato due difetti: `online` includeva root e gli account di sistema; il lock dell'agente passava ai processi figli (vedi sotto). | A 21 | fatto |

## E. Critiche non accolte

| Punto | Fonte | Perché |
|---|---|---|
| L'aggancio della shell si aggira; la conferma non prova la lettura. | B 4.2 | Conseguenza voluta della decisione «mai bloccare»: la conferma è dichiaratamente una dichiarazione dell'utente. |
| Se il terminale è bloccato il messaggio non arriva. | B 4.1 | Inesatto: la casella fa da coda, il messaggio arriva al prompt successivo o al login. |
| Lock rimasti bloccati. | B 4.3 | **Respinta per errore, poi accolta.** Il kernel rilascia il lock alla morte del processo, ma la VM di prova ha mostrato che il lock dell'agente passava ai suoi figli (`sleep`, `zenity`): un figlio orfano lo teneva fino a 60 s e il nuovo agente usciva subito. Corretto (`9>&-`). |
| Solo bash. | A 10; B 4.2 | Vincolo dichiarato; un aggancio per zsh è una voce separata, da decidere. |
| Riscrivere subito in un linguaggio compilato. | B 3 | Si segue la revisione A: prima la specifica, poi un'eventuale riscrittura. |
| `ams` sempre root. | B 5.1 | Decisione esplicita dell'utente. |
