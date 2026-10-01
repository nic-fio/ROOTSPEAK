# Documentazione di RootSpeak

GitHub mostra i file `.html` come codice sorgente: non visualizza le pagine web
salvate in un repository. Il repository è privato, quindi GitHub Pages non
pubblica la documentazione: si legge dalla copia locale. Si clona il
repository e si apre `docs/index.html` (o direttamente `docs/User Manual.html`)
nel browser, per esempio con `xdg-open docs/index.html`. Ogni manuale è un file
unico che contiene stile, figure e logo, quindi funziona anche senza rete, si allega
a una email e si stampa. Dopo `./install.sh` i due manuali sono anche in
`/usr/local/share/doc/rootspeak/`.

I file Markdown (`decisions-and-history.md`, `adversarial-review.md`) GitHub li
mostra già formattati.

Dentro il programma, `rspeak --help` mostra la guida integrata a schede.

## File

| File | Cosa |
|---|---|
| `index.html` | Pagina iniziale della documentazione. |
| `User Manual.html` | Manuale utente, in inglese: installare e usare RootSpeak; riferimento di tutti i comandi e le opzioni. |
| `Technical Manual.html` | Manuale tecnico, in inglese: architettura, archivio, consegna, conferme, sicurezza, specifica, test, limiti. |
| `decisions-and-history.md` | Perché RootSpeak è fatto così, e la sua storia. |
| `adversarial-review.md` | Le due revisioni esterne e cosa è stato fatto per ogni punto. |
| `.nojekyll` | Dice a GitHub Pages di servire i file così come sono (se un giorno la documentazione verrà pubblicata). |
| `sources/` | I sorgenti dei due manuali: vedi sotto. |

## Come si rigenerano i manuali

I due manuali sono generati: non si modificano mai a mano.

| Dove | Cosa |
|---|---|
| `sources/build.py` | Il generatore, con le funzioni per figure e tabelle. |
| `sources/style.css` | Lo stile comune dei manuali dei 7 progetti, incorporato così com'è in ogni manuale: non si modifica qui. |
| `sources/manual.js` | Lo script comune dei manuali (ricerca, indice analitico, pulsante Copy), incorporato così com'è. |
| `sources/cover-logo.png` | Il logo della copertina: copia trasparente di `logos/rootspeak-logo.png`. |
| `sources/user/` | I capitoli del manuale utente, un file per capitolo (`_helpers.py` contiene le funzioni comuni). |
| `sources/technical/` | I capitoli del manuale tecnico, un file per capitolo. |
| `sources/screens/` | Schermate vere della TUI, prese nella macchina di prova da `tools/tui-screenshots.sh`. |
| `sources/user/screens/` | Altre schermate vere per il manuale utente, prese in modalità di prova da `capture.py`. |

```
make docs         # python3 docs/sources/build.py: rigenera i due manuali (serve python3-pygments)
make docs-check   # tools/check-docs.py: fallisce se i manuali non sono allineati al codice
```

`tools/check-docs.py` (eseguito anche da `make test` e dalla CI) controlla che i
manuali in `docs/` coincidano con quelli rigenerati dai sorgenti, che il
riferimento del manuale utente coincida con la guida integrata, che ogni file
del codice sia nella mappa dei file del manuale tecnico, la versione, i link
interni, i cataloghi delle lingue e che `tests/engine.sh` sia stato eseguito
sul codice attuale. Il manuale tecnico riporta l'ultima esecuzione di ogni suite
di prove: dopo `tests/engine.sh` va rigenerato.
