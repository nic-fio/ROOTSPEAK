# Lavorare ad AMS

Come si sviluppa questo progetto: gli accordi, le decisioni già prese e cosa
controllare prima di registrare una modifica. Un clone più questo file sono
tutto il contesto di lavoro: niente di ciò che serve per continuare sta fuori
dal repository.

Il nome è **AMS - Advanced Messaging System** (non «Message System», senza «for linux»).

## Come si lavora

- **Si parla con l'utente in italiano, sempre**, senza frasi in inglese.
  Codice, commenti, messaggi del programma e il resto della documentazione
  sono in italiano, come prima.
- **I manuali sono in inglese**: `docs/User Manual.html` e
  `docs/Technical Manual.html` e i loro sorgenti in `docs/sources/` (testi dei
  capitoli, didascalie, etichette di `build.py`). Comandi, percorsi, uscite del
  programma e schermate restano come sono.
- **Quando l'utente propone qualcosa**, prima si dice se migliora o peggiora il
  risultato e perché, poi lo si esegue o si fa una controproposta.
- **Testi per l'utente senza gergo da programmatori**: guida integrata,
  messaggi e manuale utente sono scritti per chi usa AMS.
- **Verificare, non dichiarare.** Ogni affermazione sul comportamento viene da
  un'esecuzione: modalità di prova, `tests/`, o una prova dal vivo dopo
  `./install.sh`. «Dovrebbe funzionare» non è un risultato.
- **La documentazione conta quanto il codice.** Una funzione non è finita
  finché i manuali non la descrivono. I manuali si giudicano come un lavoro di
  grafica: schemi in ogni capitolo, testi pratici, e ogni pagina guardata con
  uno screenshot prima di consegnarla.
- **Claude non ha la password di sudo**: l'installazione e le prove come root
  le lancia l'utente (`! ./install.sh`, `! ams …`). Attenzione: se le
  credenziali di sudo dell'utente sono ancora valide, `build/ams` senza
  `AMS_TEST=1` parte come root senza chiedere nulla. Nelle prove impostare
  sempre la modalità di prova (manuale tecnico, «Provare senza root»).

## Decisioni prese: non riaprirle

Il perché di ciascuna è in [docs/decisions-and-history.md](docs/decisions-and-history.md).

| Decisione | |
|---|---|
| **Una sola macchina, inviano solo gli amministratori** | Niente rete, niente messaggi tra utenti. |
| **Ogni messaggio chiede la conferma; tre stati** | Per ogni destinatario: inviato, consegnato (copia nella casella), confermato. Niente livelli (`info` è stato tolto il 30 settembre: scelta di semplificare l'architettura); per gli avvisi brevi si usa `--expires`. Scadenza e ritiro sono proprietà del messaggio. |
| **Nessun blocco** | Niente livello `block`, niente disconnessioni, niente blocco a schermo intero: l'utente può sempre rimandare. |
| **Ricezione automatica, nessun comando per gli utenti** | Gli utenti non hanno `ams`; il codice che gira come utente è `ams-user`, fuori dal PATH. |
| **`ams` sempre come root, senza eccezioni** | Si rilancia con sudo prima di tutto, anche per `--help` e `version`. |
| **Nessun gruppo di AMS** | Si usa il gruppo admin esistente (`sudo`/`wheel`): `ams` è `root:<gruppo>` `750`. |
| **Nessun demone** | logind, sudo, aggancio della shell, avvio automatico del desktop. |
| **Root non tocca le caselle come root** | Ogni accesso a `/var/lib/ams/users/U` avviene in un processo figlio con l'identità dell'utente (`come_utente`), con un tempo massimo. |
| **zenity** per il desktop | Finestra «Ho letto» / «Più tardi»; `notify-send`, se c'è, solo per segnalare una conferma non registrata. |
| **Guida integrata come MTERM, niente man page** | Schede in un terminale, pagina con pager sotto 44×10, testo in una pipe; testi in `src/guida.c` (inglese) e nei cataloghi `po/`. |
| **Manuali nello stile comune dei 7 progetti (1° ottobre 2026)** | Generati da `docs/sources/` (un file per capitolo) in due file HTML autosufficienti in inglese (`User Manual.html`, `Technical Manual.html`), con lo stile comune dei manuali dei 7 progetti, approvato dal proprietario: incorporato in ogni manuale e identico in tutti. `docs/sources/style.css` è il canone (nato da questo file) e `docs/sources/manual.js` lo script comune (ricerca nella barra laterale, indice analitico, pulsante Copy): si copiano alla lettera, mai modificati in un solo progetto; le regole solo di AMS stanno in `AMS_CSS`/`AMS_JS` di `build.py`. Copertina: logo (`docs/sources/cover-logo.png`, copia trasparente di `logos/ams-logo.png`), «User Manual»/«Technical Manual», versione e data. Piè di pagina: `AMS · User Manual · Version X · Month YYYY · © 2026 Nicola Fiorillo` (niente licenza). Indice analitico solo nel manuale tecnico, dai termini del glossario. L'utente ha bocciato i manuali in stile NESH ("fanno schifo"). |
| **Riscrittura in C (30 settembre)** | Tutto: `ams` e `ams-user`; gli agganci delle shell restano script, la finestra resta zenity. Fatta: versione 0.2.0; il prototipo in bash è stato tolto quando il C ha passato tutte le prove (resta nella storia di git). Difese obbligatorie: tutti gli avvisi, `-fanalyzer`, sanitizer nei test, fuzzing di ciò che legge file degli utenti. |
| **Lingue con gettext (30 settembre)** | Formato e strumenti di gettext (`po/*.po`, `.mo`, `msgfmt --check`), testi di partenza in inglese; i `.mo` li legge un lettore di AMS, non la libintl: con la libintl una lingua non installata nel sistema non funziona (provato: `C.UTF-8` ignora `LANGUAGE`), e root deve scrivere a ogni terminale nella sua lingua. |
| **TUI per gli amministratori (30 settembre)** | `ams` senza argomenti in un terminale apre la TUI (`--help` resta la guida; in una pipe `ams` mostra la guida). Consultare, agire (ritiro, pulizia, sollecito) con conferma, scrivere e inviare (Ctrl+E apre `$EDITOR`), aggiornamento automatico. Niente ncurses. La TUI usa le stesse funzioni dei comandi e **non inventa stati**: solo inviato, consegnato, confermato; ritirato e scaduto come proprietà. Un messaggio si riassume con i suoi destinatari: barra a tre colori e «14 confermato · 5 consegnato · 2 inviato». |
| **Nessuna licenza** | Repository privato, copyright nic-fio. |

## Il repository

La struttura segue quella standard comune ai 7 progetti (AMS, EFI_PARTITION_MANAGER, HOSTER,
MTERM, NESH, PHONESTRA, SCRAPER), decisa dal proprietario il 30 settembre 2026: nomi di file e
cartelle in inglese (tranne i file `.c`/`.h` di `src/`, che coincidono con i nomi del codice),
`README.md`, `CLAUDE.md`, `NOTICE.md`, `Makefile` con `make`, `make test`, `make docs-check`,
`make clean`, `.github/workflows/ci.yml`, `logos/`, `src/`, `tests/`, `tools/` e `docs/` con `index.html`, i
due manuali, `README.md`, `decisions-and-history.md`, `.nojekyll`, `sources/`. Il contenuto dei
documenti resta nella sua lingua.

| Dove | Cosa |
|---|---|
| `src/` | Il codice in C: `ams.c` (comando degli amministratori), `ams-user.c` (aiutante come utente), `archivio.c`, `utente.c`, `sessioni.c`, `testo.c`, `lingua.c`, `evento.c`, `guida.c`, `comune.c`. |
| `po/` | Cataloghi gettext: `ams.pot` e le traduzioni (`it.po`). |
| `Makefile` | `make`, `make prove`, `make test` (prove, controlli dei manuali, `tests/engine.sh`), `make docs`, `make docs-check`, `make sanitizer`, `make analizza`, `make pot`, `make clean`. |
| `etc/` | Aggancio della shell, avvio automatico dell'agente, configurazione predefinita. |
| `install.sh` | Installazione, aggiornamento, `--uninstall`, `--purge`. |
| `docs/` | `User Manual.html` e `Technical Manual.html` (in inglese, generati, mai a mano), `index.html` (pagina iniziale), `README.md` (cosa c'è e come si rigenera), `.nojekyll`, `decisions-and-history.md`, `adversarial-review.md`. |
| `docs/sources/` | `build.py` (generatore e funzioni per figure e tabelle), `style.css` e `manual.js` (stile e script comuni ai 7 progetti, da non modificare qui), `cover-logo.png` (il logo della copertina), capitoli in `user/` e `technical/` (in inglese), schermate vere della TUI in `screens/` e `user/screens/`. Il riferimento dei comandi del manuale utente viene dai testi di partenza inglesi di `po/ams.pot`. |
| `tests/` | `engine.sh`: il motore in modalità di prova; `help-tui.py`: la guida interattiva su un terminale virtuale; `container/`: la macchina di prova e gli scenari dal vero; `vm/`: la VM con desktop sul server delle prove; `unit-tests.c`: le parti interne (`make prove`). Risultati in `results/` e `*/results/`. |
| `tools/` | `check-docs.py`: coerenza tra codice, guida e manuali; `fingerprint.sh`: impronta del codice registrata con i risultati; `tui-screenshots.sh`: schermate vere della TUI per i manuali; `setup-dev.sh`: cosa manca per lavorare su una copia appena clonata; `backup.sh`: tutto il repository in un git bundle. |
| `logos/` | Il logo del progetto (`ams-logo.png`, PNG 2172×724 fornito dal proprietario, da non modificare): nelle copertine dei manuali va la sua copia trasparente `docs/sources/cover-logo.png`; non va in `docs/index.html`. |
| `NOTICE.md` | Copyright e componenti di terzi (nessuno incorporato). |
| `.github/workflows/ci.yml` | Su GitHub a ogni push: `make`, `make prove`, `tests/engine.sh`, `make docs-check` (niente container né VM). |

**Server delle prove** (192.168.0.2, accesso ssh con chiave): la VM vive in
`/media/AMS` sull'SSD (il `/` del server è in RAM). QEMU con KVM come utente
normale, senza libvirt né sudo. Il disco base si prepara una volta
(`tests/vm/run.sh --prepara`, circa 10 minuti); ogni esecuzione parte da una
copia pulita e spegne la VM alla fine.

## Prima di registrare una modifica

1. `make` (avvisi come errori) e `make prove`; `make pot` se sono cambiati
   testi da tradurre, poi la traduzione in `po/it.po`.
2. `make docs` (`python3 docs/sources/build.py`), poi `make docs-check` (`tools/check-docs.py`): fallisce se i
   manuali in `docs/` non corrispondono ai sorgenti, se guida integrata e
   riferimento del manuale utente divergono, se un file di codice manca dalla
   mappa dei file, se la versione non coincide, se un link interno è rotto,
   se un catalogo è incompleto o se `tests/engine.sh` non è stato eseguito
   sul codice attuale.
   **Fallisce se i manuali non sono aggiornati.**
3. `tests/engine.sh` sempre; `tests/help-tui.py` se è cambiata la guida;
   `make sanitizer` con `AMS_BUILD=build-san tests/engine.sh`, `make analizza`
   e `tests/fuzz/run.sh` se è cambiato il codice che legge dati;
   `tests/container/run.sh` (prove dal vero come root in un container) se
   sono cambiati invio, consegna, conferme o permessi; `tests/vm/run.sh`
   (VM con GNOME sul server delle prove, 192.168.0.2) se è cambiato il desktop.
   I risultati vanno registrati insieme alla modifica.
4. Prova del flusso toccato in modalità di prova; per desktop, sudo e altri
   utenti, prova dal vivo dopo `./install.sh`, fatta dall'utente.
5. I commit usano l'identità locale del repository (nome `nic-fio`, indirizzo
   noreply di GitHub), che tiene fuori l'indirizzo personale. Messaggi in
   italiano. Mai `git add -A` senza guardare `git status`.

Il capitolo **«Specifica»** del manuale tecnico è il contratto di AMS (fonti
autorevoli, stati, invarianti, interruzioni, tempo, formato dell'archivio):
ogni modifica lo rispetta o lo aggiorna esplicitamente.

Versione: `AMS_VERSION` in `src/comune.h`, e la stessa nei due manuali
(controllata da `tools/check-docs.py`).

## A che punto è

Versione 0.2.0 in C (30 settembre 2026), che sostituisce il prototipo in bash 0.1.0.
Suite (numeri aggiornati nel manuale tecnico, capitolo 11, letti dai risultati): `tests/engine.sh` 82 controlli, `tests/tui.py`, container 72 scenari
(più il desktop, non provabile lì), VM con desktop in italiano 66 scenari, tutti riusciti (le shell si provano solo nel container; `AMS_PROVA_LINGUA=en` per il desktop in inglese, 11 su 11)
(30 settembre 2026), anche con AddressSanitizer e UBSan; fuzzing 30 minuti senza
difetti. Il prototipo in bash è stato provato anche dal vivo su Debian 13 con GNOME 48 su
Wayland, con due account (`nicfio`, `user`): finestra immediata e al login,
testo e domanda nel terminale anche via ssh, conferma unica fra
i canali, `list` e `status`. `revoke`, scadenze, errori e pulizia del testo
provati in modalità di prova. La revisione avversariale del 30 settembre 2026
([docs/adversarial-review.md](docs/adversarial-review.md)) è chiusa:
le due decisioni rimaste sono state prese il 30 settembre: domanda di
conferma in tutte le shell (bash, zsh, fish a ogni prompt; al login per le
shell che leggono `/etc/profile`), nessuna risposta degli utenti, interfaccia
nella lingua di ciascun utente. Shell e lingue sono fatte (scenari K ed L; cataloghi gettext in `po/`, inglese di ripiego). La versione in C non è ancora stata provata dal vivo sul PC dell'utente. Le voci [2] del README erano congelate fino
alla chiusura della revisione; ripartire da lì solo su indicazione
dell'utente.
