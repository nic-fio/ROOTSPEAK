# AMS 0.1.0 — Nota per chi fa la revisione

Allegato alla richiesta di revisione del **Manuale Tecnico di AMS**
(`AMS_Manuale_Tecnico.html`). Questa nota non sostituisce il manuale: dice che
cosa vi chiediamo, che cosa è già stato deciso e perché, quali critiche sono già
state esaminate e come è stato verificato il comportamento. Serve a spendere la
revisione sui problemi veri invece che su punti già chiusi.

Le decisioni elencate qui **si possono criticare**: se ne ritenete una
dannosa, ditelo, ma indicate il danno concreto (chi lo subisce, in quale
situazione). Una critica che ripete un punto della sezione 5 senza un
argomento nuovo non ci è utile.

## 1. Che cos'è AMS, in breve

- Uno strumento per **una sola macchina Linux**: gli amministratori mandano
  messaggi di testo agli utenti di quella macchina e sanno chi li ha letti.
- **Ogni messaggio chiede la conferma di lettura.** Per ogni destinatario ci
  sono tre stati: inviato, consegnato (la copia è nella sua casella),
  confermato.
- Il messaggio arriva dove l'utente lavora: nei terminali (console, ssh,
  emulatori, tmux) e sul desktop, in una finestra «Ho letto» / «Più tardi».
  Chi non è collegato lo trova al login successivo.
- **Niente demone**: logind, sudo, un aggancio nella shell e un agente avviato
  con la sessione grafica.
- Prototipo **in bash**, versione 0.1.0: circa 1 900 righe fra codice,
  testi e file di sistema.

## 2. Che cosa vi chiediamo

In ordine di importanza:

1. **Correttezza di consegna e conferma**: casi in cui un messaggio si perde,
   una conferma si perde o viene registrata senza che l'utente l'abbia data,
   uno stato mostrato da `ams status` non corrisponde alla realtà.
2. **Gare e interruzioni**: processi uccisi a metà, comandi concorrenti,
   uscita dalla sessione, orologio spostato, disco pieno.
3. **Confine fra root e utenti** (capitolo 9): modi in cui un utente non
   privilegiato può far fare a root qualcosa che non dovrebbe, leggere messaggi
   altrui, falsificare lo stato di un altro utente o disturbare gli altri.
4. **Coerenza della specifica** (capitolo 14): invarianti che il comportamento
   descritto nei capitoli 4–8 non rispetta, casi mancanti nella tabella delle
   interruzioni.
5. **Chiarezza del manuale**: parti ambigue o che un amministratore
   fraintenderebbe.

Per ogni rilievo, per favore indicate:

- **gravità**: grave (perdita di messaggi o conferme, violazione del confine di
  sicurezza), media, lieve;
- **dove**: capitolo e paragrafo del manuale;
- **scenario**: la sequenza concreta di azioni che porta al problema;
- **base**: *letto nel manuale* oppure *dedotto* (il manuale non lo dice e ne
  ricavate il comportamento). Il codice sorgente completo non è allegato: il
  manuale ne riporta i punti essenziali, ma non tutto. Un rilievo dedotto va
  bene, purché sia dichiarato come tale;
- **tipo**: *difetto* (il comportamento è sbagliato) oppure *scelta
  discutibile* (funziona come previsto, ma lo ritenete sbagliato).

## 3. Che cosa AMS non vuole essere

Queste non sono mancanze, sono fuori dal perimetro:

- **Non è un sistema di messaggistica fra utenti**, né fra macchine: niente
  rete, nessun server centrale.
- **Non è un controllo di sicurezza contro un utente ostile.** La conferma è una
  *dichiarazione* dell'utente («ho letto»), non una prova di lettura. Un utente
  può ignorare la shell di AMS, disattivare l'agente del desktop o rispondere
  senza leggere: AMS lo sollecita, non lo costringe.
- **Non blocca mai il lavoro**: niente schermate bloccanti, niente
  disconnessioni. L'utente può sempre rimandare.
- **Gli utenti non rispondono** agli amministratori: la risposta non è
  prevista.

## 4. Modello di fiducia

- **Fidati**: gli amministratori (gruppo `sudo` o `wheel`). `ams` gira sempre
  come root; chi può usarlo può comunque diventare root.
- **Non fidati**: gli utenti. Ognuno controlla completamente la propria casella
  (`/var/lib/ams/users/UTENTE/`), compresi i file di conferma.
- Tutto ciò che passa fra root e una casella attraversa un confine controllato
  (capitolo 9): root accede alle caselle solo con l'identità dell'utente
  (`runuser`), e ciò che legge da una casella viene ripulito e limitato.
- **Fonte autorevole**: l'archivio di root (`/var/lib/ams/sent/`) per testo,
  destinatari, scadenza e ritiro; la casella dell'utente solo per le sue
  conferme e i suoi rinvii (specifica, «Fonti autorevoli»).
- L'attaccante considerato è un **utente locale** della stessa macchina. Un
  attaccante che è già root, o che ha accesso fisico, è fuori dal modello.

## 5. Decisioni già prese

Ciascuna è stata presa dal responsabile del progetto dopo averne discusso le
alternative.

| Decisione | Perché |
|---|---|
| Ogni messaggio chiede la conferma; nessun livello (tolto il livello «solo informazione») | Architettura più semplice e un solo significato per «consegnato». Per gli avvisi brevi c'è la scadenza (`--expires`). |
| Nessun blocco, mai | Bloccare o disconnettere un utente è stato giudicato troppo invasivo per uno strumento di comunicazione. |
| Nessun comando per gli utenti | La ricezione è automatica; gli utenti non devono imparare nulla. Il codice che gira come utente (`ams-user`) è fuori dal `PATH`. |
| `ams` sempre come root, anche per `--help` e `version` | Un solo modo di funzionare; nessun ramo di codice per utenti non privilegiati. |
| Nessun gruppo proprio di AMS | Si usa il gruppo di amministratori esistente: `ams` è `root:<gruppo>` con permessi `750`. |
| Nessun demone | Meno parti in esecuzione, niente servizio da mantenere; logind e sudo fanno già il lavoro. |
| Guida integrata a schede invece di una man page | Scelta di usabilità del responsabile del progetto. |
| Prototipo in bash | Per validare il flusso con gli strumenti del sistema. Una riscrittura si farà solo se il prototipo mostrerà limiti concreti. |
| Domanda di conferma in tutte le shell | A ogni prompt per bash, zsh e fish; al login per sh, dash, ksh e le altre shell che leggono `/etc/profile`; il testo arriva nel terminale all'invio con qualunque shell. |
| Ognuno legge AMS nella sua lingua | Italiano e inglese; per le altre lingue, l'inglese. Il testo del messaggio non si traduce. Il registro di sistema è nella lingua della macchina. |

## 6. Critiche già esaminate (prima revisione, 30 settembre 2026)

Due revisori hanno già esaminato la versione precedente del manuale. Per i
punti accolti vi chiediamo di **verificare la correzione** descritta nel
manuale, non di riproporre il difetto originale.

**Accolti e corretti**

| Difetto | Correzione | Dove nel manuale |
|---|---|---|
| Una conferma non scrivibile (disco pieno, permessi) veniva trattata come «già confermata» | Conferma pubblicata con `ln` esclusivo; se fallisce, il messaggio resta e l'utente è avvisato | cap. 8 |
| Un `ams send` interrotto lasciava destinatari senza copia | Consegna verificata per destinatario; `sent/ID/incomplete` e recupero al comando successivo; lock per l'invio in corso | cap. 5, 14 |
| L'agente del desktop moriva se svegliato mentre partiva | Segnale preparato come prima istruzione; sveglia solo all'agente pronto (`ams-agent.pronto`) | cap. 5.6, 7 |
| Una finestra o una domanda aperte accettavano la conferma dopo la scadenza | Chiusura alla scadenza; `ack` rifiuta; `ams status` confronta con la scadenza della copia di root | cap. 8, 14 |
| Mancava una specifica formale | Capitolo 14: stati, transizioni, invarianti, interruzioni, formato dell'archivio | cap. 14 |
| Mancava un registro per messaggio | Eventi strutturati nel journal e `ams log ID` | cap. 5.8 |
| Configurazione letta come script da root | File di dati: solo chiavi note, interi positivi | cap. 9 |
| Nessuna pulizia dell'archivio | `ams purge DURATA` | cap. 5.9 |
| `list` e `status` lenti | Una lettura per casella e per messaggio (`list` da circa 6 s a circa 0,7 s) | cap. 5.9 |
| Nessun test automatico | Test del motore, macchina di prova, VM con desktop | cap. 11 |
| Lock dell'agente ereditato dai processi figli | I figli non ricevono il descrittore del lock | cap. 7 |
| Domanda di conferma solo in bash | Agganci per zsh, fish e le shell POSIX | cap. 6 |

**Non accolti**

| Critica | Perché |
|---|---|
| L'aggancio della shell si può aggirare; la conferma non prova la lettura | Vero e voluto: vedi sezione 3. |
| Con il terminale bloccato il messaggio non arriva | Inesatto: la copia è nella casella e la domanda arriva al prompt successivo o al login; la scrittura nel terminale ha un limite di 3 secondi. |
| Riscrivere subito in un linguaggio compilato | Vedi sezione 5. |
| `ams` sempre come root è un rischio | Vedi sezioni 4 e 5: chi può usare `ams` può già diventare root. |

## 7. Come è verificato il comportamento

Ogni comportamento descritto nel manuale viene da un'esecuzione, non da una
dichiarazione (capitolo 11).

| Suite | Dove gira | Esito al 30 settembre 2026 |
|---|---|---|
| `tests/engine.sh` | modalità di prova, senza root | 62 controlli su 62 |
| `tests/container/` | Debian 13 con systemd, utenti e sessioni ssh vere, come root | 66 scenari su 66 |
| `tests/vm/` | VM Debian 13 con GNOME 48 su Wayland, finestre usate con l'accessibilità | 59 scenari su 59 (desktop in italiano); scenari del desktop anche in inglese |

**Non provato**: distribuzioni diverse da Debian 13, X11, desktop diversi da
GNOME, sistemi senza systemd (non supportati).

## 8. Limiti già noti

Il capitolo 13 elenca i limiti noti con le loro conseguenze. Segnalateli solo
se ritenete che la conseguenza sia peggiore di quella descritta. In breve:

- sh, dash e ksh ricevono la domanda solo al login;
- se zsh viene installata dopo AMS, bisogna rilanciare l'installazione;
- l'intestazione scritta nel terminale all'invio usa la lingua con cui è
  partita la shell;
- un utente entrato con `su` non riceve il testo all'invio in quel terminale
  (lo riceve al prompt successivo);
- se l'agente del desktop muore con una finestra aperta, quella finestra non
  registra più nulla e il nuovo agente ne apre un'altra.
