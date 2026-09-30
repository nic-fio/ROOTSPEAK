# Revisione avversariale del 30 settembre 2026

Il progetto è stato sottoposto a due revisioni critiche indipendenti, fatte da
due modelli linguistici di frontiera sul manuale tecnico della versione 0.1.0:

- **Revisione A** — «Relazione critica su AMS 0.1.0» (24 punti e piano di risanamento);
- **Revisione B** — «Relazione critica senza sconti — AMS v0.1.0» (file ricevuto
  troncato: si interrompe al punto 5.1).

I punti sulla lingua dell'interfaccia sono esclusi da questo elenco: sono stati
trattati a parte (decisione del 30 settembre, fatta: italiano e inglese). Ogni affermazione concreta è stata verificata sul codice
prima di essere accolta. Le voci [2] del README restano congelate finché i
gruppi A–D non sono chiusi (revisione A, punto 23).

Stato: **aperto**, **fatto**, **non accolto**.

**Al 30 settembre 2026 tutti i punti accolti sono fatti, compresi l'aggancio per tutte le shell e la lingua di ciascun utente decisi il 30 settembre; la risposta dell'utente all'amministratore non è prevista (decisione dell'utente).** Le suite dal vero hanno trovato altri difetti, corretti e descritti qui sotto e nel manuale tecnico (capitoli 5, 7 e 14).

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
| 5 | Macchina a stati formale, invarianti, comportamento dopo un crash, formato dell'archivio: capitolo «Specifica» del manuale tecnico (stati e transizioni con precondizioni, operazioni atomiche ed eventi; 11 invarianti; tabella delle interruzioni e delle riparazioni; formato 1 dell'archivio). Scrivendola è emerso e si è corretto un caso: conferma scritta ma messaggio non ancora spostato, che veniva ripresentato. | A 2, 4, 13, 22; B 3.4 | fatto |
| 6 | Distinguere consegnato, mostrato e confermato. Risolto semplificando, per decisione dell'utente: ogni messaggio chiede la conferma e ogni destinatario ha tre stati, inviato, consegnato (copia nella casella), confermato; lo stato «mostrato» e il livello `info` spariscono. Test: `tests/engine.sh`, gruppo 3. | A 3; B 4.1 | fatto |
| 7 | Registro degli eventi per messaggio: eventi strutturati nel journal (`AMS_EVENTO`, `AMS_MESSAGGIO`, `AMS_UTENTE`, `AMS_CANALE`, più `_UID` messo dal journal) per invio, consegna, mancata consegna, recupero, annullamento, rinvio, conferma, conferma fallita, ritiro; nuovo comando `ams log ID`. Scenari J1 e J2. | A 5 | fatto |
| 8 | La casella dell'utente non è la fonte autorevole: specifica, «Fonti autorevoli»; applicato anche alla scadenza (punto 4). | A 7 | fatto |
| 9 | Semantica di ritiro, scadenza e orologio: specifica, «Tempo, ritiro e scadenza». | A 14, 15, 16 | fatto |
| 10 | Versione del formato dei messaggi: ogni messaggio inizia con `format: 1`. Test: `tests/engine.sh`, gruppo 5. | B 3.3 | fatto |

## C. Robustezza e configurazione

| # | Punto | Fonte | Stato |
|---|---|---|---|
| 11 | Configurazione come dati: `ams_load_conf` accetta solo le chiavi note con interi positivi e non esegue nulla. Test: gruppo 5 (un file con `$(…)` non viene eseguito). | A 18 | fatto |
| 12 | L'agente rilegge la configurazione a ogni giro. | A 19 | fatto |
| 13 | Perimetro supportato: specifica, «Perimetro supportato», e manuale utente, «Cosa serve». | A 9 | fatto |
| 14 | Pulizia: nuovo comando `ams purge DURATA`, che cancella i messaggi più vecchi con copie, conferme e rinvii nelle caselle (come l'utente) e lascia l'evento nel registro; salta gli invii incompleti o in corso. Test: `tests/engine.sh`, gruppo 6. | B 2 | fatto |
| 15 | `list` e `status` lenti. Misurato (scenari H), poi corretto leggendo ogni casella una volta sola per utente (un solo `runuser` per tutte le sue conferme e i suoi rinvii) e le consegne una volta per messaggio: `list` da circa 6 s a circa 0,7 s per 10 messaggi a 54 destinatari, `status` da circa 1,3 s a circa 0,7 s. Non è servito copiare le conferme lato root. | A 8 | fatto |

## D. Test

| # | Punto | Fonte | Stato |
|---|---|---|---|
| 16 | Test automatici del motore: `tests/engine.sh` più le suite dal vero nel container e nella VM (i numeri aggiornati sono nel manuale tecnico, capitolo 11, letti dai risultati). Coperti concorrenza, gare, interruzioni, file e caselle alterati, strumenti che falliscono, sicurezza. | A 20 | fatto |
| 17 | Ambiente riproducibile per le prove dal vivo. (La VM ha poi trovato un terzo difetto: un'uscita dalla sessione subito dopo «Ho letto» poteva perdere la conferma; scenario I10.) Fatto in due forme: un container Debian 13 con systemd (`tests/container/run.sh`) e una VM con GNOME su Wayland sul server delle prove (`tests/vm/run.sh` compresi quelli della finestra sul desktop). Esiti e misure in `tests/*/risultati/`. La VM ha trovato due difetti: `online` includeva root e gli account di sistema; il lock dell'agente passava ai processi figli (vedi sotto). | A 21 | fatto |

## E. Critiche non accolte

| Punto | Fonte | Perché |
|---|---|---|
| L'aggancio della shell si aggira; la conferma non prova la lettura. | B 4.2 | Conseguenza voluta della decisione «mai bloccare»: la conferma è dichiaratamente una dichiarazione dell'utente. |
| Se il terminale è bloccato il messaggio non arriva. | B 4.1 | Inesatto: la casella fa da coda, il messaggio arriva al prompt successivo o al login. |
| Lock rimasti bloccati. | B 4.3 | **Respinta per errore, poi accolta.** Il kernel rilascia il lock alla morte del processo, ma la VM di prova ha mostrato che il lock dell'agente passava ai suoi figli (`sleep`, `zenity`): un figlio orfano lo teneva fino a 60 s e il nuovo agente usciva subito. Corretto (`9>&-`). |
| Solo bash. | A 10; B 4.2 | Decisione dell'utente del 30 settembre: la domanda di conferma va portata in tutte le shell (bash, zsh, fish a ogni prompt; al login per le shell che leggono `/etc/profile`). Fatto: agganci per bash, zsh, fish e sh; scenari K nella macchina di prova. |
| Riscrivere subito in un linguaggio compilato. | B 3 | Si segue la revisione A: prima la specifica, poi un'eventuale riscrittura. |
| `ams` sempre root. | B 5.1 | Decisione esplicita dell'utente. |

# Seconda revisione (30 settembre 2026)

Due revisori hanno esaminato il manuale tecnico con la nota di accompagnamento
(senza il codice): **revisione C** (12 rilievi, G-01…L-03) e **revisione D**
(7 rilievi più 2 note di chiarezza). Ogni rilievo è stato verificato sul codice
o con una prova prima di essere accolto; per ogni correzione c'è una prova che
fallisce con il codice precedente (gruppo 9 di `tests/engine.sh`, scenari F7 e
J3), salvo dove indicato.

| # | Rilievo | Fonte | Verifica | Stato |
|---|---|---|---|---|
| 18 | `ams revoke` non aspettava un `ams send` in corso: una copia poteva arrivare dopo il ritiro. Ora il ritiro scrive `revoked` (su disco), attende il lock dell'invio, che si ferma al destinatario successivo, poi toglie le copie; `sent/ID/ritiro` resta finché non sono tolte tutte e il comando successivo completa. | C G-01, C M-03 | fondato (codice) | fatto |
| 19 | Conferma e ritiro senza un ordine: una conferma poteva nascere dopo il ritiro. Ora `ack` non conferma senza copia nella casella (esito 3) e `ams status` non conta una conferma con data successiva a `sent/ID/revoked` (stesso secondo: vale). La prova sulla domanda interrotta passa anche con il codice precedente, che se ne accorgeva già: la correzione riguarda la finestra fra controllo e `ln`, provata con la regola della data. | C G-02 | fondato (codice) | fatto |
| 20 | Terminale riassegnato fra la ricerca e la scrittura: il testo poteva finire sul terminale di un altro utente. Ora `write_term` apre il terminale e controlla il proprietario del terminale aperto (`/dev/fd/5`), non del nome. | C G-03 | fondato (gara reale, finestra breve) | fatto |
| 21 | Nessuna garanzia dopo un'interruzione di corrente. Ora `sync` di messaggio, destinatari e segno prima delle consegne, `syncfs` prima di togliere `incomplete`, conferma su disco prima di «Confermato», ritiro su disco prima di toccare le caselle; il recupero ricontrolla anche le copie già annotate. Un'interruzione di corrente vera non è provata; la copia sparita è simulata. | C G-04, C L-03 | fondato | fatto |
| 22 | Numeri delle prove nel manuale vecchi e non collegati al codice. Ora ogni suite registra commit e impronta del codice (`tools/fingerprint.sh`); il capitolo 11 legge i risultati e dice se valgono per il codice attuale; `tools/check-docs.py` fallisce se `tests/engine.sh` non è stato eseguito sul codice attuale. | C M-01, C L-01 | fondato | fatto |
| 23 | Perimetro «supportato» confuso con «verificato». Ora la specifica li separa. | C M-02 | fondato (documento) | fatto |
| 24 | `_UID` presentato come «non falsificabile»: dice chi ha scritto un evento, non che sia vero. Testo corretto; `ams log` segnala come non attendibile un evento scritto dall'utente sbagliato (scenario J3). | C M-04 | fondato | fatto |
| 25 | «Confermato» va letto come dichiarazione dell'utente, anche negli audit: scritto nella specifica e nel glossario. | C M-05 | fondato (documento) | fatto |
| 26 | Punti di linearizzazione non definiti: nuovo paragrafo «Operazioni concorrenti» nella specifica. | C L-02 | fondato (documento) | fatto |
| 27 | `ams purge` insieme a `ams list`: un messaggio poteva sparire a metà lettura. Ora `purge` rinomina `sent/ID` in `sent/.cancella-ID` (un colpo solo) e `list` legge prima ciò che gli serve; una cancellazione interrotta la completa il comando successivo. | D 1.2, C M-03 | fondato | fatto |
| 28 | Migliaia di file finti in `acks/` rallentavano `ams list` (5000 file: 3,9 s). Ora si leggono solo i messaggi esistenti in `sent/`, con un tempo massimo: 25 ms. | D 1.4 | fondato (misurato) | fatto |
| 29 | Testi oltre 128 KiB: zenity non può riceverli come argomento. Ora `ams send` rifiuta oltre 65536 byte. | D 1.6 | fondato | fatto |
| 30 | Messaggio che scade durante l'invio: comportamento scritto nella specifica (le copie successive si consegnano, nessuno le vede). | D 1.7 | fondato (documento) | fatto |
| 31 | Chiarezza: costo del controllo al prompt (capitolo 6.1) e formato dei campi dell'archivio (capitolo 14). | D, note | fondato | fatto |

**Non accolti**

| Rilievo | Fonte | Perché |
|---|---|---|
| Una pipe al posto di `acks/ID` blocca `ams status` | D 1.1 | Inesatto: si leggono solo file normali; provato, `ams status` risponde in 0,03 s. Resta una prova nel gruppo 9. |
| Un commento a fine riga in `ams.conf` invalida il valore | D 1.5 | Inesatto: commenti e spazi sono gestiti; provato, resta una prova nel gruppo 9. |
| Collegamento simbolico `/var/lib/ams` creato prima dell'installazione | D 1.3 | Fuori dal modello: in `/var/lib` scrive solo root, che è già fidato. |
