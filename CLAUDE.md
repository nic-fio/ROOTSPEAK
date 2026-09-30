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
  finché i manuali non la descrivono.
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
| **Livelli `info` e `ack`, nessun blocco** | Niente livello `block`, niente disconnessioni, niente blocco a schermo intero: l'utente può sempre rimandare. |
| **Ricezione automatica, nessun comando per gli utenti** | Gli utenti non hanno `ams`; il codice che gira come utente è `ams-user`, fuori dal PATH. |
| **`ams` sempre come root, senza eccezioni** | Si rilancia con sudo prima di tutto, anche per `--help` e `version`. |
| **Nessun gruppo di AMS** | Si usa il gruppo admin esistente (`sudo`/`wheel`): `ams` è `root:<gruppo>` `750`. |
| **Nessun demone** | logind, sudo, aggancio della shell, avvio automatico del desktop. |
| **Root non tocca le caselle come root** | Ogni accesso a `/var/lib/ams/users/U` passa da `as_user` (`runuser`). |
| **zenity e notify-send** per il desktop | Finestra «Ho letto» / «Più tardi»; notifiche per `info`. |
| **Guida integrata come MTERM, niente man page** | Schede in un terminale, pagina con pager sotto 44×10, testo in una pipe; testi solo in `lib/ams-help.sh`. |
| **Manuali HTML in italiano, tema chiaro** | Stile e palette di NESH, impianto di MTERM. |
| **Prototipo in bash** | Riscrittura in un linguaggio compilato solo per limiti concreti. |
| **Nessuna licenza** | Repository privato, copyright nic-fio. |

## Il repository

| Dove | Cosa |
|---|---|
| `bin/ams` | Il comando degli amministratori. |
| `lib/` | `ams-common.sh` (comune), `ams-user` (aiutante come utente), `ams-help.sh` (guida integrata). |
| `etc/` | Aggancio della shell, avvio automatico dell'agente, configurazione predefinita. |
| `install.sh` | Installazione, aggiornamento, `--uninstall`, `--purge`. |
| `docs/` | `manuale-utente.html`, `manuale-tecnico.html`, `decisioni-e-storia.md`, `assets/`. |
| `tests/` | `help-tui.py`: la guida interattiva su un terminale virtuale. |
| `tools/` | `check-docs.py`: coerenza tra codice, guida e manuali. |

## Prima di registrare una modifica

1. `bash -n` su tutti gli script.
2. `tools/check-docs.py`: fallisce se guida integrata e riferimento del manuale
   utente divergono, se la mappa dei file del manuale tecnico non è aggiornata
   (file mancanti o righe oltre il 10%), se la versione non coincide o se un
   link interno è rotto. **Fallisce se i manuali non sono aggiornati.**
3. `tests/help-tui.py` se è cambiata la guida.
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
avvisi `info`, testo e domanda nel terminale anche via ssh, conferma unica fra
i canali, `list` e `status`. `revoke`, scadenze, errori e pulizia del testo
provati in modalità di prova. Aperti: le voci [2] del README e la decisione
sulla risposta dell'utente all'amministratore.
