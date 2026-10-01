#!/usr/bin/env python3
"""Controlla che i manuali siano allineati al codice.

Fallisce se:
  - i manuali in docs/ non coincidono con quelli rigenerati dai sorgenti
    (docs/sources/build.py): i file HTML non si modificano a mano;
  - un comando o un'opzione della guida integrata (contesti guida-comandi e
    guida-opzioni in src/guida.c) manca dal riferimento del manuale utente
    (attributo data-help), vi ha una descrizione diversa dal testo di partenza
    inglese estratto ora dal codice con xgettext (i manuali sono in inglese, come
    i testi di partenza), o il manuale documenta una voce che non esiste;
  - un file di codice manca dalla mappa dei file del manuale tecnico, o la
    mappa cita un file che non esiste;
  - la versione di src/comune.h non compare nella copertina e nel piè di pagina
    dei due manuali;
  - un manuale non incorpora lo stile e lo script comuni (docs/sources/style.css
    in testa al blocco <style>, docs/sources/manual.js) così come sono;
  - un link interno #ancora di uno dei due manuali non porta a nessun id;
  - un catalogo po/*.po non passa msgfmt --check (stessi %s dell'originale),
    ha traduzioni da rivedere, o manca di testi presenti nei sorgenti;
  - l'ultima esecuzione di tests/engine.sh non ha l'impronta del codice
    attuale (tools/fingerprint.sh) o ha controlli falliti;
  - il vecchio nome del prodotto (AMS, ams) ricompare in un file del
    repository, nel contenuto o nel nome, fuori dalla storia delle decisioni.
"""
import html
import importlib.util
import pathlib
import re
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
USER = DOCS / "User Manual.html"
TECH = DOCS / "Technical Manual.html"

errors = []


def plain(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()


# ---- manuali rigenerati ----
spec = importlib.util.spec_from_file_location("build", DOCS / "sources" / "build.py")
build = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(DOCS / "sources"))
spec.loader.exec_module(build)
with tempfile.TemporaryDirectory() as tmp:
    for kind in build.MANUALS:
        fresh, _ = build.build(kind, tmp)
        current = DOCS / fresh.name
        if not current.exists() or current.read_text() != fresh.read_text():
            errors.append(f"{current.name}: non corrisponde ai sorgenti, rigenerare con python3 docs/sources/build.py")

user = USER.read_text()
tech = TECH.read_text()

# ---- testi di partenza, estratti ora dal codice ----
import subprocess
with tempfile.TemporaryDirectory() as tmp:
    pot = pathlib.Path(tmp) / "rootspeak.pot"
    subprocess.run(["xgettext", "--from-code=UTF-8", "-k", "-kT", "-kN_", "-kTC:1c,2", "-kNC_:1c,2", "-ktl:2",
                    "-ktlc:2c,3", "-o", str(pot)] + sorted(str(p) for p in (ROOT / "src").glob("*.c")),
                   check=True, capture_output=True)
    estratte = build.po_voci(pot)
sorgenti = {(c, m) for c, m, _ in estratte if m}

# ---- riferimento ----
# Il manuale utente è in inglese: le sue voci si confrontano con i testi di partenza
# inglesi della guida così come sono ora in src/guida.c, non con po/rootspeak.pot da cui il
# generatore le legge (un rootspeak.pot vecchio fa quindi fallire il controllo: make pot).
wanted = {}
for name in ("RSPEAK_HELP_COMMANDS", "RSPEAK_HELP_OPTIONS"):
    for c, m, _ in estratte:
        if c == build.GUIDA_CONTESTI[name]:
            f, d = m.split("¦", 1)
            wanted[f] = re.sub(r"\s+", " ", d).strip()
if not wanted:
    errors.append("guida: nessuna voce di comandi e opzioni estratta da src/guida.c")
documented = {html.unescape(f): plain(d)
              for f, d in re.findall(r'<dt[^>]*\bdata-help="([^"]+)"[^>]*>.*?</dt><dd>(.*?)</dd>', user, re.S)}
for f in sorted(set(wanted) - set(documented)):
    errors.append(f"manuale utente: manca «{f}» nel riferimento")
for f in sorted(set(documented) - set(wanted)):
    errors.append(f"manuale utente: «{f}» non esiste nella guida integrata")
for f in sorted(set(wanted) & set(documented)):
    if wanted[f] != documented[f]:
        errors.append(f"manuale utente: la descrizione di «{f}» è diversa da quella della guida in src/guida.c "
                      f"(make pot, poi rigenerare i manuali)")

# ---- mappa dei file ----
fmap = tech[tech.index('id="file-map"'):]
fmap = fmap[:fmap.index("</table>")]
rows = set(re.findall(r"<tr><td><code>([\w./-]+)</code></td><td>\d+</td>", fmap))
code_files = {"install.sh", "Makefile", "docs/sources/build.py", "docs/sources/style.css", "docs/sources/manual.js"}
code_files |= {str(p.relative_to(ROOT)) for d in ("src", "po", "etc", "tests", "tools")
               for p in (ROOT / d).rglob("*") if p.is_file() and "results" not in p.parts
               and "__pycache__" not in p.parts}
for f in sorted(code_files - rows):
    errors.append(f"manuale tecnico: {f} manca dalla mappa dei file")
for f in sorted(rows - code_files):
    errors.append(f"manuale tecnico: {f} è nella mappa dei file ma non esiste")

# ---- versione, stile comune e link ----
version = build.VERSION
css = (DOCS / "sources" / "style.css").read_text()
js = (DOCS / "sources" / "manual.js").read_text()
for where, text, title in (("manuale utente", user, "User Manual"), ("manuale tecnico", tech, "Technical Manual")):
    if f"<span>Version</span><b>{version}</b>" not in text:
        errors.append(f"{where}: la copertina non riporta la versione {version}")
    if f"RootSpeak · {title} · Version {version} · " not in text:
        errors.append(f"{where}: il piè di pagina non riporta la versione {version}")
    if not text.split("<style>", 1)[-1].startswith(css):
        errors.append(f"{where}: il blocco <style> non comincia con docs/sources/style.css")
    if f"<script>\n{js}</script>" not in text:
        errors.append(f"{where}: manca docs/sources/manual.js, incorporato così com'è")
    ids = set(re.findall(r'\bid="([^"]+)"', text))
    for anchor in sorted(set(re.findall(r'href="#([^"]+)"', text))):
        if anchor not in ids:
            errors.append(f"{where}: il link #{anchor} non porta da nessuna parte")

# ---- lingue ----
langs = ["en"]
for po in sorted((ROOT / "po").glob("*.po")):
    langs.append(po.stem)
    r = subprocess.run(["msgfmt", "--check", "-o", "/dev/null", str(po)], capture_output=True, text=True)
    if r.returncode:
        errors.append(f"lingue: {po.name} non passa msgfmt --check: {r.stderr.strip()[:200]}")
    voci = {(c, m): t for c, m, t in build.po_voci(po) if m}
    if "#, fuzzy" in po.read_text().replace('#, fuzzy\nmsgid ""', ""):
        errors.append(f"lingue: {po.name} ha traduzioni da rivedere (fuzzy)")
    for c, m in sorted(sorgenti - set(voci)):
        errors.append(f"lingue: {po.name} non ha «{m[:60]}» ({c or 'senza contesto'}): make pot, poi tradurre")
    for c, m in sorted(k for k in sorgenti & set(voci) if not voci[k]):
        errors.append(f"lingue: {po.name}: «{m[:60]}» non è tradotto")
base = sorgenti

# ---- prove ----
import json
eng = ROOT / "tests" / "results" / "engine.json"
if not eng.exists() or json.loads(eng.read_text()).get("impronta") != build.impronta_attuale():
    errors.append("prove: tests/engine.sh non è stato eseguito sul codice attuale (impronta diversa): lanciarlo")
elif json.loads(eng.read_text()).get("no"):
    errors.append("prove: l'ultima esecuzione di tests/engine.sh ha controlli falliti")

# ---- vecchio nome ----
# Il prodotto si chiamava AMS fino al 1° ottobre 2026: il nome sopravvive solo come
# storia. Ammessi: la storia delle decisioni, CLAUDE.md («formerly AMS»), questo
# controllo, il commento d'origine dello stile comune (identico nei 7 progetti) e i
# titoli delle due revisioni critiche, citati così come sono stati ricevuti.
OLD = re.compile(r"(?<![A-Za-z0-9])(AMS|ams)(?![A-Za-z0-9])")
OLD_FILES = {"docs/decisions-and-history.md", "CLAUDE.md", "tools/check-docs.py"}
OLD_LINES = ("/* Base: style.css di AMS */", "- **Revisione ")
tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.split("\n")
for f in filter(None, tracked):
    if OLD.search(f):
        errors.append(f"vecchio nome: il file {f} va rinominato")
    if f in OLD_FILES:
        continue
    try:
        text = (ROOT / f).read_text()
    except (UnicodeDecodeError, FileNotFoundError):
        continue
    for n, line in enumerate(text.splitlines(), 1):
        line = re.sub(r"base64,[A-Za-z0-9+/=]+", "", line)
        if OLD.search(line) and not line.lstrip().startswith(OLD_LINES):
            errors.append(f"vecchio nome: {f}:{n}: {line.strip()[:80]}")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"documentazione allineata: 2 manuali, {len(wanted)} voci della guida, {len(rows)} file nella mappa, "
      f"versione {version}, lingue {', '.join(langs)} ({len(base)} testi)")
