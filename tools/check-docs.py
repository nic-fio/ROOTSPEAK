#!/usr/bin/env python3
"""Controlla che i manuali siano allineati al codice.

Fallisce se:
  - i manuali in docs/ non coincidono con quelli rigenerati dai sorgenti
    (docs/sorgenti/build.py): i file HTML non si modificano a mano;
  - un comando o un'opzione della guida integrata (AMS_HELP_COMMANDS e
    AMS_HELP_OPTIONS in lib/ams-help.sh) manca dal riferimento del manuale
    utente (attributo data-help), vi ha una descrizione diversa, o il manuale
    documenta una voce che non esiste;
  - un file di codice manca dalla mappa dei file del manuale tecnico, o la
    mappa cita un file che non esiste;
  - la versione di lib/ams-common.sh non compare nei due manuali;
  - un link interno #ancora di uno dei due manuali non porta a nessun id.
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
code_files = {"bin/ams", "install.sh", "docs/sorgenti/build.py", "docs/sorgenti/stile.css"}
code_files |= {str(p.relative_to(ROOT)) for d in ("lib", "etc", "tests", "tools")
               for p in (ROOT / d).rglob("*") if p.is_file()}
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

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"documentazione allineata: 2 manuali, {len(wanted)} voci della guida, {len(rows)} file nella mappa, "
      f"versione {version}")
