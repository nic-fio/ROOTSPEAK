#!/usr/bin/env python3
"""Controlla che il manuale utente sia allineato al codice, come in MTERM.

Fallisce se:
  - un comando o un'opzione della guida integrata (AMS_HELP_COMMANDS e
    AMS_HELP_OPTIONS in lib/ams-help.sh) non ha la sua voce nel riferimento del
    manuale utente (attributo data-help identico all'etichetta della guida), o
    la descrizione del manuale è diversa da quella della guida, o il manuale
    documenta una voce che non esiste;
  - un file della mappa dei file del manuale tecnico manca o non esiste, o il
    numero di righe indicato si scosta di oltre il 10% da quello vero;
  - la versione di lib/ams-common.sh non è quella dei due manuali;
  - un link interno #ancora di uno dei due manuali punta a un id inesistente.
"""
import html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANUAL = ROOT / "docs" / "manuale-utente.html"
TECH = ROOT / "docs" / "manuale-tecnico.html"
HELP = ROOT / "lib" / "ams-help.sh"
COMMON = ROOT / "lib" / "ams-common.sh"

errors = []


def plain(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()


def help_items(name, src):
    body = src[src.index(name + "=("):]
    body = body[:body.index("\n)")]
    items = {}
    for raw in re.findall(r'^\t"((?:[^"\\]|\\.)*)"$', body, re.M):
        flag, desc = raw.replace('\\"', '"').split("¦", 1)
        items[flag] = re.sub(r"\s+", " ", desc).strip()
    return items


help_src = HELP.read_text()
manual = MANUAL.read_text()

wanted = {**help_items("AMS_HELP_COMMANDS", help_src), **help_items("AMS_HELP_OPTIONS", help_src)}
ref = manual[manual.index('id="reference"'):manual.index('id="messaggi-errore"')]
documented = {}
for flag, desc in re.findall(r'<dt[^>]*\bdata-help="([^"]+)"[^>]*>.*?</dt>\s*<dd>(.*?)</dd>', ref, re.S):
    documented[html.unescape(flag)] = plain(desc)

for flag in sorted(set(wanted) - set(documented)):
    errors.append(f"manuale: manca «{flag}» nel riferimento")
for flag in sorted(set(documented) - set(wanted)):
    errors.append(f"manuale: «{flag}» non esiste nella guida integrata")
for flag in sorted(set(wanted) & set(documented)):
    if wanted[flag] != documented[flag]:
        errors.append(f"manuale: la descrizione di «{flag}» è diversa da quella della guida")

tech = TECH.read_text()

# ---- mappa dei file ----
fmap = tech[tech.index('id="file-map"'):]
fmap = fmap[:fmap.index("</table>")]
rows = dict(re.findall(r"<tr><td><code>([\w./-]+)</code></td><td>(\d+)</td>", fmap))
code_files = ["bin/ams", "install.sh", *sorted(str(p.relative_to(ROOT)) for d in ("lib", "etc", "tests", "tools")
                                          for p in (ROOT / d).rglob("*") if p.is_file())]
for f in code_files:
    real = len((ROOT / f).read_text().splitlines())
    if f not in rows:
        errors.append(f"manuale tecnico: {f} ({real} righe) manca dalla mappa dei file")
    elif abs(real - int(rows[f])) > max(2, int(rows[f]) // 10):
        errors.append(f"manuale tecnico: {f} ha {real} righe, la mappa ne indica {rows[f]}")
for f in sorted(set(rows) - set(code_files)):
    errors.append(f"manuale tecnico: {f} è nella mappa dei file ma non esiste")

# ---- versione e link ----
version = re.search(r"^AMS_VERSION=(\S+)", COMMON.read_text(), re.M).group(1)
for where, text in (("manuale utente", manual), ("manuale tecnico", tech)):
    if version not in text:
        errors.append(f"{where}: manca la versione {version}")
    for other in sorted(set(re.findall(r"\b0\.\d+\.\d+\b", text)) - {version}):
        errors.append(f"{where}: versione {other} diversa da {version}")
    ids = set(re.findall(r'\bid="([^"]+)"', text))
    for anchor in sorted(set(re.findall(r'href="#([^"]+)"', text))):
        if anchor not in ids:
            errors.append(f"{where}: il link #{anchor} non porta da nessuna parte")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"documentazione allineata: {len(wanted)} voci della guida, {len(rows)} file nella mappa, versione {version}")
