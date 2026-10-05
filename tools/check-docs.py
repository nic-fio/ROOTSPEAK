#!/usr/bin/env python3
"""Checks that the manuals are aligned with the code.

Fails if:
  - the manuals in docs/ do not match the ones regenerated from the sources
    (docs/sources/build.py): the HTML files are never edited by hand;
  - a command or an option of the built-in help (the COMMANDS and OPTIONS
    arrays in src/help.c) is missing from the reference of the user manual
    (data-help attribute), has a different description there, or the manual
    documents an item that does not exist;
  - a code file is missing from the file map of the technical manual, or the
    map names a file that does not exist;
  - the version in src/common.h is not on the cover and in the footer of the
    two manuals;
  - a manual does not embed the common style and script (docs/sources/style.css
    at the top of the <style> block, docs/sources/manual.js) as they are;
  - an internal #anchor link of one of the two manuals leads nowhere;
  - the last run of tests/engine.sh does not have the fingerprint of the
    current code (tools/fingerprint.sh) or has failed checks;
  - the old name of the product (AMS, ams) reappears in a file of the
    repository, in its content or in its name, outside the decision history;
  - Italian reappears in a file of the repository: RootSpeak, its messages,
    its code and its documents are in English only (decision of 1 October 2026).
"""
import html
import importlib.util
import json
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
USER = DOCS / "User Manual.html"
TECH = DOCS / "Technical Manual.html"

errors = []


def plain(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()


# ---- regenerated manuals ----
spec = importlib.util.spec_from_file_location("build", DOCS / "sources" / "build.py")
build = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(DOCS / "sources"))
spec.loader.exec_module(build)
with tempfile.TemporaryDirectory() as tmp:
    for kind in build.MANUALS:
        fresh, _ = build.build(kind, tmp)
        current = DOCS / fresh.name
        if not current.exists() or current.read_text() != fresh.read_text():
            errors.append(f"{current.name}: does not match the sources, regenerate with python3 docs/sources/build.py")

user = USER.read_text()
tech = TECH.read_text()

# ---- reference ----
wanted = {}
for name in ("RSPEAK_HELP_COMMANDS", "RSPEAK_HELP_OPTIONS"):
    for f, d in build.help_items(name):
        wanted[f] = re.sub(r"\s+", " ", d).strip()
if not wanted:
    errors.append("help: no command or option read from src/help.c")
documented = {html.unescape(f): plain(d)
              for f, d in re.findall(r'<dt[^>]*\bdata-help="([^"]+)"[^>]*>.*?</dt><dd>(.*?)</dd>', user, re.S)}
for f in sorted(set(wanted) - set(documented)):
    errors.append(f"user manual: «{f}» is missing from the reference")
for f in sorted(set(documented) - set(wanted)):
    errors.append(f"user manual: «{f}» does not exist in the built-in help")
for f in sorted(set(wanted) & set(documented)):
    if wanted[f] != documented[f]:
        errors.append(f"user manual: the description of «{f}» differs from the one in src/help.c "
                      f"(regenerate the manuals)")

# ---- file map ----
fmap = tech[tech.index('id="file-map"'):]
fmap = fmap[:fmap.index("</table>")]
rows = set(re.findall(r"<tr><td><code>([\w./-]+)</code></td><td>\d+</td>", fmap))
code_files = {"install.sh", "Makefile", "docs/sources/build.py", "docs/sources/style.css", "docs/sources/manual.js"}
code_files |= {str(p.relative_to(ROOT)) for d in ("src", "etc", "tests", "tools")
               for p in (ROOT / d).rglob("*") if p.is_file() and "results" not in p.parts
               and "__pycache__" not in p.parts}
code_files |= {str(p.relative_to(ROOT)) for p in (ROOT / "site").glob("*") if p.suffix in (".sh", ".py")}
for f in sorted(code_files - rows):
    errors.append(f"technical manual: {f} is missing from the file map")
for f in sorted(rows - code_files):
    errors.append(f"technical manual: {f} is in the file map but does not exist")

# ---- version, common style and links ----
version = build.VERSION
css = (DOCS / "sources" / "style.css").read_text()
js = (DOCS / "sources" / "manual.js").read_text()
for where, text, title in (("user manual", user, "User Manual"), ("technical manual", tech, "Technical Manual")):
    if f"<span>Version</span><b>{version}</b>" not in text:
        errors.append(f"{where}: the cover does not show version {version}")
    if f"RootSpeak · {title} · Version {version} · " not in text:
        errors.append(f"{where}: the footer does not show version {version}")
    if not text.split("<style>", 1)[-1].startswith(css):
        errors.append(f"{where}: the <style> block does not start with docs/sources/style.css")
    if f"<script>\n{js}</script>" not in text:
        errors.append(f"{where}: docs/sources/manual.js is missing, or not embedded as it is")
    ids = set(re.findall(r'\bid="([^"]+)"', text))
    for anchor in sorted(set(re.findall(r'href="#([^"]+)"', text))):
        if anchor not in ids:
            errors.append(f"{where}: the link #{anchor} leads nowhere")

# ---- tests ----
eng = ROOT / "tests" / "results" / "engine.json"
if not eng.exists() or json.loads(eng.read_text()).get("fingerprint") != build.current_fingerprint():
    errors.append("tests: tests/engine.sh was not run on the current code (different fingerprint): run it")
elif json.loads(eng.read_text()).get("failed"):
    errors.append("tests: the last run of tests/engine.sh has failed checks")

# ---- old name ----
# The product was called AMS until 1 October 2026: the name survives only as
# history. Allowed: the decision history, CLAUDE.md («formerly AMS»), this check,
# the origin comment of the common style (identical in the 7 projects) and the
# titles of the two critical reviews, quoted as they were received.
OLD = re.compile(r"(?<![A-Za-z0-9])(AMS|ams)(?![A-Za-z0-9])")
OLD_FILES = {"docs/decisions-and-history.md", "CLAUDE.md", "tools/check-docs.py"}
OLD_LINES = ("/* Base: the style.css of AMS */", "- **Revisione ")
tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.split("\n")
for f in filter(None, tracked):
    if OLD.search(f):
        errors.append(f"old name: the file {f} must be renamed")
    if f in OLD_FILES:
        continue
    try:
        text = (ROOT / f).read_text()
    except (UnicodeDecodeError, FileNotFoundError):
        continue
    for n, line in enumerate(text.splitlines(), 1):
        line = re.sub(r"base64,[A-Za-z0-9+/=]+", "", line)
        if OLD.search(line) and not line.lstrip().startswith(OLD_LINES):
            errors.append(f"old name: {f}:{n}: {line.strip()[:80]}")

# ---- English only ----
# Accented vowels used by Italian and words that exist only in Italian. Allowed: the
# lines kept for history listed in OLD_LINES (the shared style comment and the
# quoted titles of the two reviews) and this check.
ITALIAN = re.compile(r"[àèìòùÀÈÌÒÙ]|\b(della|delle|degli|dello|nella|nelle|questo|questa|perché|sono|anche|"
                     r"quando|messaggio|messaggi|utente|utenti|conferma|confermato|consegnato|rimandato|"
                     r"ritirato|scaduto|destinatari|destinatario|casella|archivio|prova|guida|lingua|"
                     r"italiano|scheda|righe|finestra|inviato|amministratore|sollecito|scadenza|cartella)\b", re.I)
# Old Italian names inside identifiers (RSPEAK_MESSAGGIO, CONSEGNATO, .cancella-ID…).
ITALIAN_NAMES = re.compile(r"MESSAGGIO|CONSEGNAT|CONFERMAT|RITIRAT|SOLLECITAT|RINVIAT|ANNULLAT|RECUPERAT|EVENTO|"
                           r"UTENTE|CANALE|DETTAGLI|AUTORE|_PROVA|\.cancella|\.pronto|/ritiro|\b(lingua|guida|comune|archivio)\.[ch]\b")
for f in filter(None, tracked):
    if f == "tools/check-docs.py" or f.endswith((".png", ".svg", ".ans")):
        continue
    try:
        text = (ROOT / f).read_text()
    except (UnicodeDecodeError, FileNotFoundError):
        continue
    for n, line in enumerate(text.splitlines(), 1):
        line = re.sub(r"base64,[A-Za-z0-9+/=]+", "", line)
        if (ITALIAN.search(line) or ITALIAN_NAMES.search(line)) and not line.lstrip().startswith(OLD_LINES):
            errors.append(f"Italian: {f}:{n}: {line.strip()[:80]}")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"documentation aligned: 2 manuals, {len(wanted)} help items, {len(rows)} files in the map, version {version}")
