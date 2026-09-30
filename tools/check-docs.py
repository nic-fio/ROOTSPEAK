#!/usr/bin/env python3
"""Controlla che i manuali siano allineati al codice.

Fallisce se:
  - i manuali in docs/ non coincidono con quelli rigenerati dai sorgenti
    (docs/sorgenti/build.py): i file HTML non si modificano a mano;
  - un comando o un'opzione della guida integrata (AMS_HELP_COMMANDS e
    AMS_HELP_OPTIONS in lib/lingue/aiuto-it.sh) manca dal riferimento del manuale
    utente (attributo data-help), vi ha una descrizione diversa, o il manuale
    documenta una voce che non esiste;
  - un file di codice manca dalla mappa dei file del manuale tecnico, o la
    mappa cita un file che non esiste;
  - la versione di src/comune.h non compare nei due manuali;
  - un link interno #ancora di uno dei due manuali non porta a nessun id;
  - un catalogo po/*.po non passa msgfmt --check (stessi %s dell'originale),
    ha traduzioni da rivedere, o manca di testi presenti nei sorgenti;
  - l'ultima esecuzione di tests/engine.sh non ha l'impronta del codice
    attuale (tools/impronta.sh) o ha controlli falliti.
"""
import html
import importlib.util
import pathlib
import re
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
USER = DOCS / "AMS_Manuale_Utente.html"
TECH = DOCS / "AMS_Manuale_Tecnico.html"

errors = []


def plain(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()


# ---- manuali rigenerati ----
spec = importlib.util.spec_from_file_location("build", DOCS / "sorgenti" / "build.py")
build = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(DOCS / "sorgenti"))
spec.loader.exec_module(build)
with tempfile.TemporaryDirectory() as tmp:
    for kind in build.MANUALS:
        fresh, _ = build.build(kind, tmp)
        current = DOCS / fresh.name
        if not current.exists() or current.read_text() != fresh.read_text():
            errors.append(f"{current.name}: non corrisponde ai sorgenti, rigenerare con python3 docs/sorgenti/build.py")

user = USER.read_text()
tech = TECH.read_text()

# ---- riferimento ----
wanted = {f: re.sub(r"\s+", " ", d).strip()
          for name in ("AMS_HELP_COMMANDS", "AMS_HELP_OPTIONS") for f, d in build.help_items(name)}
documented = {html.unescape(f): plain(d)
              for f, d in re.findall(r'<dt[^>]*\bdata-help="([^"]+)"[^>]*>.*?</dt><dd>(.*?)</dd>', user, re.S)}
for f in sorted(set(wanted) - set(documented)):
    errors.append(f"manuale utente: manca «{f}» nel riferimento")
for f in sorted(set(documented) - set(wanted)):
    errors.append(f"manuale utente: «{f}» non esiste nella guida integrata")
for f in sorted(set(wanted) & set(documented)):
    if wanted[f] != documented[f]:
        errors.append(f"manuale utente: la descrizione di «{f}» è diversa da quella della guida")

# ---- mappa dei file ----
fmap = tech[tech.index('id="file-map"'):]
fmap = fmap[:fmap.index("</table>")]
rows = set(re.findall(r"<tr><td><code>([\w./-]+)</code></td><td>\d+</td>", fmap))
code_files = {"install.sh", "Makefile", "docs/sorgenti/build.py", "docs/sorgenti/stile.css"}
code_files |= {str(p.relative_to(ROOT)) for d in ("src", "po", "etc", "tests", "tools")
               for p in (ROOT / d).rglob("*") if p.is_file() and "risultati" not in p.parts
               and "__pycache__" not in p.parts}
for f in sorted(code_files - rows):
    errors.append(f"manuale tecnico: {f} manca dalla mappa dei file")
for f in sorted(rows - code_files):
    errors.append(f"manuale tecnico: {f} è nella mappa dei file ma non esiste")

# ---- versione e link ----
version = build.VERSION
for where, text in (("manuale utente", user), ("manuale tecnico", tech)):
    if version not in text:
        errors.append(f"{where}: manca la versione {version}")
    ids = set(re.findall(r'\bid="([^"]+)"', text))
    for anchor in sorted(set(re.findall(r'href="#([^"]+)"', text))):
        if anchor not in ids:
            errors.append(f"{where}: il link #{anchor} non porta da nessuna parte")

# ---- lingue ----
import subprocess
with tempfile.TemporaryDirectory() as tmp:
    pot = pathlib.Path(tmp) / "ams.pot"
    subprocess.run(["xgettext", "--from-code=UTF-8", "-k", "-kT", "-kN_", "-kTC:1c,2", "-kNC_:1c,2", "-ktl:2",
                    "-ktlc:2c,3", "-o", str(pot)] + sorted(str(p) for p in (ROOT / "src").glob("*.c")),
                   check=True, capture_output=True)
    sorgenti = {(c, m) for c, m, _ in build.po_voci(pot) if m}
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
eng = ROOT / "tests" / "risultati" / "engine.json"
if not eng.exists() or json.loads(eng.read_text()).get("impronta") != build.impronta_attuale():
    errors.append("prove: tests/engine.sh non è stato eseguito sul codice attuale (impronta diversa): lanciarlo")
elif json.loads(eng.read_text()).get("no"):
    errors.append("prove: l'ultima esecuzione di tests/engine.sh ha controlli falliti")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"documentazione allineata: 2 manuali, {len(wanted)} voci della guida, {len(rows)} file nella mappa, "
      f"versione {version}, lingue {', '.join(langs)} ({len(base)} testi)")
