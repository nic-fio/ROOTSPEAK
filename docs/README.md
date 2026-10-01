# RootSpeak documentation

GitHub shows `.html` files as source code: it does not display the web pages
saved in a repository. The repository is private, so GitHub Pages does not
publish the documentation: read it from the local copy. Clone the repository
and open `docs/index.html` (or `docs/User Manual.html` directly) in the
browser, for example with `xdg-open docs/index.html`. Each manual is a single
file that contains its style, figures and logo, so it works without a network
too, can be attached to an email and printed. After `./install.sh` the two
manuals are also in `/usr/local/share/doc/rootspeak/`.

GitHub already shows the Markdown files (`decisions-and-history.md`,
`adversarial-review.md`) formatted.

Inside the program, `rspeak --help` shows the built-in help, in tabs.

## Files

| File | What |
|---|---|
| `index.html` | Home page of the documentation. |
| `User Manual.html` | User manual: installing and using RootSpeak; reference of every command and option. |
| `Technical Manual.html` | Technical manual: architecture, message store, delivery, confirmations, security, specification, tests, limits. |
| `decisions-and-history.md` | Why RootSpeak is the way it is, and its history. |
| `adversarial-review.md` | The two external reviews and what was done for each point. |
| `.nojekyll` | Tells GitHub Pages to serve the files as they are (if the documentation is ever published). |
| `sources/` | The sources of the two manuals: see below. |

## How to regenerate the manuals

The two manuals are generated: they are never edited by hand.

| Where | What |
|---|---|
| `sources/build.py` | The generator, with the functions for figures and tables. |
| `sources/style.css` | The common style of the 7 projects' manuals, embedded as it is in every manual: not to be changed here. |
| `sources/manual.js` | The common script of the manuals (search, index, Copy button), embedded as it is. |
| `sources/cover-logo.png` | The cover logo: a transparent copy of the logo in `logos/`. |
| `sources/user/` | The chapters of the user manual, one file per chapter (`_helpers.py` holds the shared functions). |
| `sources/technical/` | The chapters of the technical manual, one file per chapter. |
| `sources/screens/` | Real TUI screenshots, taken on the test machine by `tools/tui-screenshots.sh`. |
| `sources/user/screens/` | Other real screenshots for the user manual, taken in test mode by `capture.py`. |

```
make docs         # python3 docs/sources/build.py: regenerates the two manuals (needs python3-pygments)
make docs-check   # tools/check-docs.py: fails if the manuals are not aligned with the code
```

`tools/check-docs.py` (also run by `make test` and by the CI) checks that the
manuals in `docs/` match the ones regenerated from the sources, that the
reference of the user manual matches the built-in help, that every code file
is in the file map of the technical manual, the version, the internal links,
that `tests/engine.sh` was run on the current code, and that the old name and
Italian do not reappear. The technical manual reports the last run of each
test suite, read from their results (the container, `tests/distros` with one row per
distribution, `tests/vm` with one row per desktop): after running any of them it must be regenerated.
