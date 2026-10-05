# RootSpeak landing page

Mockup **19 «Night sky»**, chosen by the owner on 1 October 2026 among 20 mockups
(same content, twenty visual directions): deep navy, subtle stars, the logo's orbit
as a planetary path and its orange dot as the planet. On 5 October 2026, when
RootSpeak became freeware, the trial and the prices were replaced by the
download, and the page got its search-engine tags.

- `index.html` — the page, self-contained, without JavaScript (fonts embedded and
  subset to Basic Latin plus a few signs: `© « · » × – — ’ “ ” … ← ↑ → ↓`, the
  box-drawing characters; other characters fall back to system fonts). In the
  head: description, canonical address, link preview (`../og.jpg`), the
  `SoftwareApplication` data for search engines (version, download, price 0).
- `preview.png` — the top of the mockup as chosen, at 1440 × 900.
- `BRIEF.md` — the brief the 20 mockups followed (only true statements, program
  texts quoted exactly). Its trial and pricing parts are superseded by the
  freeware decision.

The page names the version and the archive
(`download/rootspeak-VERSION-linux-x86_64.tar.gz`, «about 360 KB»): at a new
version update them; `site/publish.sh` refuses to publish if the link does not
match the current version. The site is built and published by
`site/publish.sh` (see the technical manual, «The downloadable archive and the
website»).
