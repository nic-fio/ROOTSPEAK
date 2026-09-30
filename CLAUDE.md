# Lavorare ad AMS

Come si sviluppa questo progetto: gli accordi, le decisioni già prese e cosa
controllare prima di registrare una modifica. Un clone più questo file sono
tutto il contesto di lavoro: niente di ciò che serve per continuare sta fuori
dal repository.

Il nome è **AMS - Advanced Messaging System for linux** (non «Message System»).

## Come si lavora

- **Si parla con l'utente in italiano, sempre**, senza frasi in inglese.
  Codice, commenti, messaggi del programma e documentazione sono in italiano.
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
  credenziali di sudo dell'utente sono ancora valide, `bin/ams` senza
  `AMS_TEST=1` parte come root senza chiedere nulla. Nelle prove impostare
  sempre la modalità di prova (manuale tecnico, «Provare senza root»).

## Decisioni prese: non riaprirle

Il perché di ciascuna è in [docs/decisioni-e-storia.md](docs/decisioni-e-storia.md).

| Decisione | |
|---|---|
| **Una sola macchina, inviano solo gli amministratori** | Niente rete, niente messaggi tra utenti. |
| **Ogni messaggio chiede la conferma; tre stati** | Per ogni destinatario: inviato, consegnato (copia nella casella), confermato. Niente livelli (`info` è stato tolto il 30 settembre: scelta di semplificare l'architettura); per gli avvisi brevi si usa `--expires`. Scadenza e ritiro sono proprietà del messaggio. |
| **Nessun blocco** | Niente livello `block`, niente disconnessioni, niente blocco a schermo intero: l'utente può sempre rimandare. |
| **Ricezione automatica, nessun comando per gli utenti** | Gli utenti non hanno `ams`; il codice che gira come utente è `ams-user`, fuori dal PATH. |
| **`ams` sempre come root, senza eccezioni** | Si rilancia con sudo prima di tutto, anche per `--help` e `version`. |
| **Nessun gruppo di AMS** | Si usa il gruppo admin esistente (`sudo`/`wheel`): `ams` è `root:<gruppo>` `750`. |
| **Nessun demone** | logind, sudo, aggancio della shell, avvio automatico del desktop. |
| **Root non tocca le caselle come root** | Ogni accesso a `/var/lib/ams/users/U` passa da `as_user` (`runuser`). |
| **zenity** per il desktop | Finestra «Ho letto» / «Più tardi»; `notify-send`, se c'è, solo per segnalare una conferma non registrata. |
| **Guida integrata come MTERM, niente man page** | Schede in un terminale, pagina con pager sotto 44×10, testo in una pipe; testi solo in `lib/ams-help.sh`. |
| **Manuali sul modello di IR_Service** | Generati da `docs/sorgenti/` (un file per capitolo) in due file HTML autosufficienti, con lo stile del Manuale Tecnico di IR_Service: copertina, indice laterale, figure SVG e tabelle numerate. L'utente ha bocciato i manuali in stile NESH ("fanno schifo"). |
| **Prototipo in bash** | Riscrittura in un linguaggio compilato solo per limiti concreti. |
| **Nessuna licenza** | Repository privato, copyright nic-fio. |

## Il repository

| Dove | Cosa |
|---|---|
| `bin/ams` | Il comando degli amministratori. |
| `lib/` | `ams-common.sh` (comune), `ams-user` (aiutante come utente), `ams-help.sh` (guida integrata). |
| `etc/` | Aggancio della shell, avvio automatico dell'agente, configurazione predefinita. |
| `install.sh` | Installazione, aggiornamento, `--uninstall`, `--purge`. |
| `docs/` | `AMS_Manuale_Utente.html` e `AMS_Manuale_Tecnico.html` (generati, mai a mano), `decisioni-e-storia.md`. |
| `docs/sorgenti/` | `build.py` (generatore e funzioni per figure e tabelle), `stile.css`, capitoli in `utente/` e `tecnico/`. |
| `tests/` | `engine.sh`: il motore in modalità di prova; `help-tui.py`: la guida interattiva su un terminale virtuale; `container/`: la macchina di prova e gli scenari dal vero; `vm/`: la VM con desktop sul server delle prove. Risultati in `*/risultati/`. |

**Server delle prove** (192.168.0.2, accesso ssh con chiave): la VM vive in
`/media/AMS` sull'SSD (il `/` del server è in RAM). QEMU con KVM come utente
normale, senza libvirt né sudo. Il disco base si prepara una volta
(`tests/vm/esegui.sh --prepara`, circa 10 minuti); ogni esecuzione parte da una
copia pulita e spegne la VM alla fine.
| `tools/` | `check-docs.py`: coerenza tra codice, guida e manuali. |

## Prima di registrare una modifica

1. `bash -n` su tutti gli script.
2. `python3 docs/sorgenti/build.py`, poi `tools/check-docs.py`: fallisce se i
   manuali in `docs/` non corrispondono ai sorgenti, se guida integrata e
   riferimento del manuale utente divergono, se un file di codice manca dalla
   mappa dei file, se la versione non coincide o se un link interno è rotto.
   **Fallisce se i manuali non sono aggiornati.**
3. `tests/engine.sh` sempre; `tests/help-tui.py` se è cambiata la guida;
   `tests/container/esegui.sh` (prove dal vero come root in un container) se
   sono cambiati invio, consegna, conferme o permessi; `tests/vm/esegui.sh`
   (VM con GNOME sul server delle prove, 192.168.0.2) se è cambiato il desktop.
   I risultati vanno registrati insieme alla modifica.
4. Prova del flusso toccato in modalità di prova; per desktop, sudo e altri
   utenti, prova dal vivo dopo `./install.sh`, fatta dall'utente.
5. I commit usano l'identità locale del repository (nome `nic-fio`, indirizzo
   noreply di GitHub), che tiene fuori l'indirizzo personale. Messaggi in
   italiano. Mai `git add -A` senza guardare `git status`.

Versione: `AMS_VERSION` in `lib/ams-common.sh`, e la stessa nei due manuali
(controllata da `tools/check-docs.py`).

## A che punto è

Prototipo 0.1.0 installato e provato dal vivo su Debian 13 con GNOME 48 su
Wayland, con due account (`nicfio`, `user`): finestra immediata e al login,
testo e domanda nel terminale anche via ssh, conferma unica fra
i canali, `list` e `status`. `revoke`, scadenze, errori e pulizia del testo
provati in modalità di prova. Aperti: i punti della revisione avversariale del 30 settembre 2026
([docs/revisione-avversariale.md](docs/revisione-avversariale.md)), da chiudere
prima delle voci [2] del README, che restano congelate.
