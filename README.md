# AMS - Advanced Messaging System

Strumento con cui gli amministratori di una macchina Linux inviano messaggi
testuali agli utenti e sanno chi ha confermato di averli letti.

A differenza di `wall` e `write`, AMS:

- raggiunge sia i terminali (tty, ssh, tmux) sia le sessioni grafiche (X11 e Wayland);
- conserva i messaggi per gli utenti non collegati e li mostra al login successivo;
- registra la conferma di lettura di ogni utente, con data e ora;
- sollecita chi non ha confermato, **senza mai bloccare il lavoro né disconnettere nessuno**.

> Nota: la conferma registra che l'utente *dichiara* di aver letto il messaggio,
> come le spunte di lettura di un'app di messaggistica. Non prova la lettura effettiva.

## Perimetro

- Una sola macchina: niente rete, niente invio tra host.
- Il comando `ams` è riservato agli amministratori, cioè ai membri del gruppo admin già esistente
  (`sudo` su Debian/Ubuntu, `wheel` su Fedora/RHEL/Arch). AMS non crea gruppi né ha permessi propri.
- Gli utenti non hanno alcun comando: ricevono e confermano soltanto, in modo automatico.
- Le sessioni non interattive (cron, scp, rsync, ssh senza terminale, servizi) non vengono mai toccate.

## Conferma e stati

Ogni messaggio chiede la conferma di lettura e insiste finché l'utente non conferma: finestra sul
desktop, domanda nel terminale e al login, solleciti ogni 30 minuti. Non blocca mai. Per ogni
destinatario un messaggio è **inviato** (la copia non è ancora nella sua casella), **consegnato**
(la copia è nella casella) o **confermato**. Scadenza e ritiro sono proprietà del messaggio: per gli
avvisi che valgono solo per poco si usa `--expires`.

## Interfacce

| Ruolo | Interfaccia |
|---|---|
| Amministratore | `ams`: comandi e, da solo in un terminale, la TUI (solo gruppo admin) |
| Utente nel terminale | Nessun comando: messaggio e domanda di conferma automatici |
| Utente nel desktop | Finestra minima con il pulsante "Ho letto" |

## Funzionalità

Legenda: **[1]** prima versione · **[2]** seconda versione · **[?]** da decidere

### Invio (amministratore)
- [1] Destinatari: utente, lista di utenti, gruppo Unix (`@gruppo`), `all` (tutti gli utenti umani), `online` (solo i collegati)
- [1] Conferma sempre richiesta; tre stati per destinatario: inviato, consegnato, confermato
- [1] Testo da argomento, file o stdin; titolo opzionale
- [1] Scadenza (`--expires 2h`)
- [2] Invio programmato (`--at "sabato 08:00"`)
- [2] Modelli di messaggio riutilizzabili
- [?] Risposta dell'utente all'amministratore

### Gestione e controllo (amministratore)
- [1] `ams list`: messaggi inviati con il conteggio delle conferme
- [1] `ams status <id>`: stato per utente (consegnato / confermato, data e ora, tipo di sessione)
- [1] `ams revoke <id>`: ritiro di un messaggio
- [1] `ams remind <id>`: sollecito a chi non ha confermato (la domanda e la finestra tornano subito)
- [2] Esportazione in CSV o JSON per audit
- [1] TUI per l'amministratore: `ams` da solo apre la lista dei messaggi con i destinatari nei tre stati, dettaglio e storia, scrittura e invio, ritiro, sollecito e pulizia con conferma, aggiornamento automatico

### Consegna
- [1] Terminale: scrittura su tutte le tty e pts attive, individuate tramite logind (non utmp)
- [1] Hook della shell (bash, zsh, fish; sh, dash, ksh al login): messaggi in sospeso al login e domanda di conferma automatica al prompt
- [1] Desktop: finestra con il pulsante "Ho letto" (X11 e Wayland)
- [1] Coda per gli utenti non collegati, con consegna al login successivo
- [1] Finestra ripetuta ogni N minuti sul desktop finché l'utente non conferma

### Ricezione (utente)

La ricezione è automatica: l'utente non deve conoscere né digitare alcun comando.

- [1] **Desktop**: compare da sola una finestra con il testo e i pulsanti **[Più tardi]** e **[Ho letto]**;
  con "Più tardi" la finestra ricompare dopo N minuti, finché l'utente non conferma.
- [1] **Terminale**: il testo completo compare nel terminale nel momento dell'invio; al prompt
  successivo AMS chiede da solo «Confermi di averlo letto? [s/N]». Se l'utente risponde no,
  vede una riga di promemoria a ogni prompt e la domanda viene riproposta dopo N minuti.
- [1] **Utente non collegato**: messaggio e domanda compaiono da soli al login successivo.
- [1] Basta confermare una volta, in una qualsiasi sessione, perché il messaggio sparisca ovunque.
- L'utente non ha comandi: una volta confermato, il messaggio non si può rileggere
  (il testo completo è visibile nel momento della conferma).

### Sicurezza (tutto [1])
- `ams` è installato come `root:<gruppo admin>` con permessi `750`: gli altri utenti non possono eseguirlo.
- Se lanciato da un amministratore non root, `ams` si rilancia da solo con sudo (password come per ogni
  operazione amministrativa). Chi entra o esce dal gruppo admin ottiene o perde subito l'accesso.
- Ogni utente vede e conferma solo i propri messaggi, grazie ai permessi della sua cartella.
- Il testo viene ripulito dai caratteri di controllo, per impedire l'iniezione di sequenze di escape nei terminali.
- Ogni operazione viene registrata nel journal di sistema.

### Configurazione e distribuzione
- [1] `/etc/ams/ams.conf`: intervallo dei solleciti, controllo dell'agente del desktop
- [1] Script di installazione
- [1] Manuale utente e manuale tecnico in HTML (un file ciascuno, in inglese), generati da `docs/sorgenti/` con lo stile dei manuali di IR_Service
- [1] Guida integrata interattiva (`ams --help`), sul modello di MTERM: schede, pagina in stile manuale
  se il terminale è piccolo, testo semplice in una pipe. Niente man page.
- [1] `tools/check-docs.py`: fallisce se guida integrata e manuale divergono; `tests/help-tui.py` prova la guida
- [2] Pacchetti deb e rpm
- [1] Ognuno nella sua lingua: interfaccia per utenti e amministratori in italiano e inglese (cataloghi gettext in `po/`), inglese di ripiego; il testo dei messaggi non si traduce

## Scelte escluse

- **Blocco a schermo intero** delle sessioni grafiche: troppo invasivo e non realizzabile su GNOME Wayland.
- **Blocco al login** con disconnessione forzata di chi non conferma: troppo estremo.
- **GUI per l'amministratore**: gli amministratori lavorano da terminale.
- **Gruppo `ams` dedicato**: duplicherebbe il gruppo admin e andrebbe tenuto allineato. Da riconsiderare solo
  se servirà far inviare messaggi a chi non è amministratore.
- **Comandi per l'utente** (`ams read`, `ams ack`, `ams history`): la ricezione è automatica e il comando resta riservato a root.

## Architettura

Nessun demone: ogni pezzo usa strumenti già presenti nel sistema. I dettagli sono nel
[manuale tecnico](docs/Technical%20Manual.html) (in inglese).

- `ams` gira sempre come root (si rilancia con sudo): salva il messaggio e lo consegna subito alle
  sessioni attive, scrivendo sui terminali e svegliando l'agente del desktop con un segnale
  (se l'agente manca, lo avvia con `systemd-run --user`).
- `/usr/local/lib/ams/ams-user`: helper interno, fuori dal PATH e non documentato come comando.
  Gira come utente e lo usano solo l'hook e l'agente per mostrare i messaggi e registrare la conferma.
- L'hook in `/etc/profile.d` mostra i messaggi in sospeso e i promemoria nel terminale.
- Un piccolo agente avviato automaticamente nella sessione grafica (`/etc/xdg/autostart`)
  mostra la finestra di conferma e la ripropone finché serve.
- Archivio:
  - `/var/lib/ams/sent/` — copia di riferimento dei messaggi e dei destinatari, accessibile solo a root;
  - `/var/lib/ams/users/<utente>/` — messaggi dell'utente e sue conferme, accessibile solo a lui e a root.
  `ams status` calcola lo stato confrontando le due parti. Se un utente cancella un messaggio
  dalla propria cartella, il messaggio risulta semplicemente non confermato.

Il primo prototipo (0.1.0) era in shell, per validare il flusso; dalla versione 0.2.0 AMS
è scritto in C, con le stesse prove e lo stesso formato dell'archivio.

## Installazione

Servono `gcc make pkg-config libsystemd-dev gettext` per compilare e `zenity` per il desktop.

```
make                      # compila in build/
./install.sh              # installa (chiede la password di sudo)
./install.sh --uninstall  # rimuove, conservando messaggi e configurazione
./install.sh --purge      # rimuove tutto
```

| File | Ruolo |
|---|---|
| `/usr/local/bin/ams` | Comando per gli amministratori (`root:sudo`, permessi 750) |
| `/usr/local/lib/ams/` | Helper interno `ams-user` e agganci di bash e zsh |
| `/usr/local/share/locale/*/LC_MESSAGES/ams.mo` | Traduzioni |
| `/etc/ams/ams.conf` | Configurazione |
| `/etc/profile.d/ams.sh` | Hook delle shell che leggono `/etc/profile` (richiamato anche da `/etc/bash.bashrc`); rimanda bash a `lib/ams/ams.bash` |
| `/usr/local/lib/ams/ams.zsh` | Hook di zsh (richiamato dallo zshrc di sistema) |
| `/etc/fish/conf.d/ams.fish` | Hook di fish |
| `/etc/xdg/autostart/ams-agent.desktop` | Avvio automatico dell'agente del desktop |
| `/var/lib/ams/` | Messaggi inviati (`sent/`) e cartelle degli utenti (`users/`) |
| `/usr/local/share/doc/ams/` | Manuale utente e manuale tecnico (`User Manual.html`, `Technical Manual.html`) |

## Documentazione

| Documento | Per chi |
|---|---|
| [`docs/User Manual.html`](docs/User%20Manual.html) | Gli amministratori che usano AMS (in inglese) |
| [`docs/Technical Manual.html`](docs/Technical%20Manual.html) | Chi sviluppa AMS: architettura, archivio, sicurezza, test (in inglese) |
| [`docs/decisioni-e-storia.md`](docs/decisioni-e-storia.md) | Perché AMS è fatto così |
| [`CLAUDE.md`](CLAUDE.md) | Accordi di lavoro e decisioni da non riaprire |
| `ams --help` | La guida integrata, a schede |

I due manuali sono file HTML autosufficienti: si aprono con un doppio clic o con
`xdg-open "docs/User Manual.html"`, si allegano a una email e si stampano. GitHub non li
mostra impaginati (mostra il codice sorgente): scaricarli o aprirli dalla copia locale.
Dopo l'installazione sono anche in `/usr/local/share/doc/ams/`.

Sono generati: si modificano i capitoli in `docs/sorgenti/utente/` e `docs/sorgenti/tecnico/`
e si rigenerano con `python3 docs/sorgenti/build.py` (serve `python3-pygments`).

Esempi:

```
ams send --to mario "Sabato dalle 8 alle 12 il server sarà spento."
ams send --to @sviluppo --title "Policy" --expires 3d --file policy.txt
ams send --to online --expires 15m "Riavvio del servizio web alle 13:00."
ams list
ams status 12
ams revoke 12
```
