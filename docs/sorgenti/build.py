"""Generatore dei manuali di AMS, sul modello dei manuali di IR_Service.

Produce due file HTML autosufficienti (nessuno script, nessun file esterno):
  docs/AMS_Manuale_Utente.html   dai capitoli in utente/chNN_*.py
  docs/AMS_Manuale_Tecnico.html  dai capitoli in tecnico/chNN_*.py

Ogni capitolo espone CHAPTER = (titolo, [(titolo_sezione, html), ...]).
I segnaposto «FIG» e «TAB» nelle didascalie diventano «Figura N.M» e
«Tabella N.M», numerati per capitolo. Lo stile è in stile.css.

    python3 docs/sorgenti/build.py            rigenera i due manuali
    python3 docs/sorgenti/build.py CARTELLA   li scrive in CARTELLA (usato da tools/check-docs.py)

Serve la libreria pygments (pacchetto python3-pygments).
"""
import html
import importlib.util
import math
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
DATE = "Settembre 2026"
VERSION = re.search(r"^AMS_VERSION=(\S+)", (ROOT / "lib/ams-common.sh").read_text(), re.M).group(1)

MANUALS = {
    "utente": dict(file="AMS_Manuale_Utente.html", title="Manuale Utente — AMS", kicker="Documentazione utente",
                   h1="Manuale Utente",
                   sub="AMS — Advanced Messaging System for linux · Messaggi dagli amministratori agli utenti, "
                       "con conferma di lettura"),
    "tecnico": dict(file="AMS_Manuale_Tecnico.html", title="Manuale Tecnico — AMS", kicker="Documentazione tecnica",
                    h1="Manuale Tecnico",
                    sub="AMS — Advanced Messaging System for linux · Architettura, archivio dei messaggi, "
                        "consegna, conferme e sicurezza"),
}

# Aggiunte allo stile di IR: procedure, etichette, terminali, finestre di esempio.
EXTRA_CSS = """
/* AMS: etichette di finestre e pulsanti, procedure a passi */
.ui{font-weight:600;color:#003a90;background:#eff6ff;border:1px solid #bfdbfe;border-radius:5px;padding:.02em .4em;font-size:.93em;white-space:nowrap}
.key{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.85em;font-weight:700;color:#0f172a;background:#fff;border:1px solid #cbd5e1;border-bottom-width:2px;border-radius:5px;padding:.05em .42em;white-space:nowrap}
.steps{counter-reset:st;list-style:none;margin:14px 0;padding:0}
.steps>li{counter-increment:st;position:relative;padding:8px 0 8px 44px;margin:0;border-left:2px solid #dbeafe;margin-left:15px}
.steps>li:before{content:counter(st);position:absolute;left:-16px;top:6px;width:30px;height:30px;border-radius:50%;background:#0050C0;color:#fff;font-weight:800;text-align:center;line-height:30px;font-size:14px}
.steps>li:last-child{border-left-color:transparent}
.steps .code{margin:10px 0 4px}
/* terminali: prompt, righe di AMS, errori, cornici */
.code .pr{color:#93c5fd} .code .cmd{color:#fff;font-weight:700} .code .am{color:#fdba74;font-weight:600}
.code .er{color:#fca5a5} .code .bx{color:#7dd3fc} .code .dim{color:#94a3b8}
.code.tui{line-height:1.12;font-size:12.5px;font-family:"DejaVu Sans Mono",ui-monospace,Menlo,Consolas,monospace}
.code-t{display:block;font-family:Outfit,Segoe UI,Arial,sans-serif;font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#64748b;margin:16px 0 -8px}
/* finestra di conferma e notifica, disegnate come su GNOME */
.shot{display:flex;flex-wrap:wrap;gap:28px;justify-content:center;align-items:flex-start;padding:10px 0 4px}
.dlg{width:410px;max-width:100%;background:#fafafa;border-radius:16px;box-shadow:0 2px 6px rgba(0,0,0,.14),0 12px 30px rgba(0,0,0,.16);padding:20px 20px 18px;color:#2e3436;text-align:left;font-family:Cantarell,Outfit,Segoe UI,Arial,sans-serif}
.dlg-t{text-align:center;font-weight:700;font-size:15.5px;margin-bottom:16px}
.dlg-b{display:flex;gap:18px;align-items:center;padding:0 6px}
.dlg-i{flex:none;width:30px;height:30px;transform:rotate(45deg);background:#2e3436;border-radius:6px;display:flex;align-items:center;justify-content:center}
.dlg-i span{transform:rotate(-45deg);color:#fafafa;font-weight:800}
.dlg-x{font-size:14px} .dlg-x div{margin:0 0 7px}
.dlg-k{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin-top:16px}
.dlg-k span{background:#e3e3e3;border-radius:9px;padding:8px;text-align:center;font-weight:700;font-size:14px}
.ntf{width:360px;max-width:100%;background:#fafafa;border-radius:14px;box-shadow:0 2px 6px rgba(0,0,0,.12),0 8px 22px rgba(0,0,0,.14);padding:12px 16px;color:#2e3436;text-align:left;font-family:Cantarell,Outfit,Segoe UI,Arial,sans-serif;font-size:14px}
.ntf-a{font-size:11.5px;color:#6b7785;margin-bottom:3px} .ntf b{display:block}
.shot-c{font-size:12px;color:#64748b;text-align:center;margin-top:10px}
/* archivio a albero */
.tree{background:transparent;border:0;padding:4px 8px;font-family:ui-monospace,Menlo,Consolas,monospace;font-size:13px;line-height:1.6;color:#0f172a;overflow-x:auto;margin:0;text-align:left}
.tree .d{color:#0050C0;font-weight:700} .tree .m{color:#64748b}
/* stati: pastiglie colorate */
.pill{display:inline-block;font-size:12px;font-weight:700;border-radius:999px;padding:.1em .65em;white-space:nowrap}
.p-ok{background:#dcfce7;color:#166534} .p-wait{background:#dbeafe;color:#1e40af} .p-snooze{background:#fef3c7;color:#92400e}
.p-off{background:#e2e8f0;color:#475569} .p-info{background:#f1f5f9;color:#334155;border:1px solid #cbd5e1}
.main{max-width:1030px}
.gloss{margin:12px 0} .gloss dt{font-weight:700;color:#003a90;font-size:15px;margin-top:12px} .gloss dd{margin:2px 0 0;color:#334155;font-size:14px}
"""

# ── Testo ───────────────────────────────────────────────────────────────
def esc(t):
    return html.escape(t, quote=False)


def c(t):
    return f"<code>{esc(t)}</code>"


def ui(label):
    """Etichetta esatta di una finestra o di un pulsante."""
    return f'<span class="ui">{esc(label)}</span>'


def key(*keys):
    return "+".join(f'<span class="key">{esc(k)}</span>' for k in keys)


def pill(text, kind):
    return f'<span class="pill p-{kind}">{esc(text)}</span>'


def p(t, lead=False):
    return f'<p class="lead">{t}</p>' if lead else f"<p>{t}</p>"


def h4(t):
    return f"<h4>{t}</h4>"


def ul(items):
    return '<ul class="ul">' + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def ol(items):
    return '<ol class="ol">' + "".join(f"<li>{i}</li>" for i in items) + "</ol>"


def steps(items):
    return '<ol class="steps">' + "".join(f"<li>{i}</li>" for i in items) + "</ol>"


def note(t, title="Nota."):
    return f'<div class="callout c-info"><div class="callout-i">i</div><div><b>{title}</b> {t}</div></div>'


def warn(t, title="Attenzione."):
    return f'<div class="callout c-warn"><div class="callout-i">!</div><div><b>{title}</b> {t}</div></div>'


def tip(t, title="Consiglio."):
    return f'<div class="callout c-ok"><div class="callout-i">+</div><div><b>{title}</b> {t}</div></div>'


def table(head, rows, cap, tid=None):
    th = "".join(f"<th>{h}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f"<td>{x}</td>" for x in r) + "</tr>" for r in rows)
    idattr = f' id="{tid}"' if tid else ""
    return (f'<figure class="tbl-wrap"><table class="tbl"{idattr}><thead><tr>{th}</tr></thead>'
            f'<tbody>{tr}</tbody></table><figcaption class="cap">{cap}</figcaption></figure>')


def dl(pairs, attrs=None, cls="deflist"):
    out = []
    for i, (a, b) in enumerate(pairs):
        extra = attrs[i] if attrs else ""
        out.append(f"<dt{extra}>{a}</dt><dd>{b}</dd>")
    return f'<dl class="{cls}">' + "".join(out) + "</dl>"


def code(text, lang="bash", title=""):
    from pygments import lex
    from pygments.lexers import BashLexer, IniLexer, PythonLexer, TextLexer
    from pygments.token import Comment, Keyword, Name, String
    lx = {"bash": BashLexer, "conf": IniLexer, "python": PythonLexer, "text": TextLexer}[lang]()
    out = []
    for tok, val in lex(text.strip("\n"), lx):
        e = html.escape(val, quote=True)
        cls = ("cm" if tok in Comment else "st" if tok in String else
               "k" if tok in Keyword or (lang == "conf" and tok in Name.Attribute) else None)
        if cls and val.strip():
            e = "\n".join(f'<span class="{cls}">{x}</span>' if x else x for x in e.split("\n"))
        out.append(e)
    head = f'<span class="code-t">{esc(title)}</span>' if title else ""
    return head + '<pre class="code"><code>' + "".join(out).rstrip("\n") + "</code></pre>"


PROMPT = re.compile(r"^((?:[\w.-]+@[\w.-]+:[^$#\n]*[$#]|[$#])(?: |$))(.*)$")


def term(text, title="", tui=False):
    """Una sessione di terminale: prompt, comandi, righe di AMS, errori."""
    lines = []
    for line in text.strip("\n").split("\n"):
        m = PROMPT.match(line)
        if m:
            lines.append(f'<span class="pr">{esc(m.group(1))}</span><span class="cmd">{esc(m.group(2))}</span>')
        elif line.startswith("ams: ") or "Permesso negato" in line:
            lines.append(f'<span class="er">{esc(line)}</span>')
        elif line.startswith("[AMS]"):
            lines.append(f'<span class="am">{esc(line)}</span>')
        elif line.startswith("──") or (tui and line[:1] in "┌├└"):
            lines.append(f'<span class="bx">{esc(line)}</span>')
        else:
            lines.append(esc(line))
    cls = "code tui" if tui else "code"
    head = f'<span class="code-t">{esc(title)}</span>' if title else ""
    return head + f'<pre class="{cls}"><code>' + "\n".join(lines) + "</code></pre>"


def tree(lines, cap):
    """Albero di cartelle: righe 'percorso  # commento'."""
    out = []
    for line in lines:
        path, _, comment = line.partition("  #")
        m = re.match(r"^([\s│├└─]*)(.*)$", path)
        pre, name = m.group(1), m.group(2)
        cls = "d" if name.rstrip().endswith("/") else ""
        out.append(esc(pre) + (f'<span class="{cls}">{esc(name)}</span>' if cls else esc(name))
                   + (f'<span class="m">  #{esc(comment)}</span>' if comment else ""))
    return f'<figure class="fig"><pre class="tree">' + "\n".join(out) + f'</pre><figcaption class="cap">{cap}</figcaption></figure>'


def dialog(title, heading, body, cap):
    return (f'<figure class="fig"><div class="shot"><div class="dlg" role="img" aria-label="{esc(title)}">'
            f'<div class="dlg-t">{esc(title)}</div><div class="dlg-b"><div class="dlg-i"><span>?</span></div>'
            f'<div class="dlg-x"><div>{esc(heading)}</div><div>{esc(body)}</div></div></div>'
            f'<div class="dlg-k"><span>Più tardi</span><span>Ho letto</span></div></div></div>'
            f'<figcaption class="cap">{cap}</figcaption></figure>')


def notification(title, body, cap):
    return (f'<figure class="fig"><div class="shot"><div class="ntf" role="img" aria-label="Notifica">'
            f'<div class="ntf-a">AMS</div><b>{esc(title)}</b>{esc(body)}</div></div>'
            f'<figcaption class="cap">{cap}</figcaption></figure>')


# ── Figure SVG nello stile di IR_Service ───────────────────────────────
COL = {"dark": "#475569", "blue": "#0050C0", "light": "#3b82f6", "navy": "#003a90", "soft": "#eef2f7",
       "green": "#16a34a", "amber": "#d97706", "grey": "#94a3b8", "white": "#ffffff"}
FONT = 'font-family="Outfit,Segoe UI,Arial,sans-serif"'


def box(x, y, w, h, title, sub="", color="blue", size=13):
    fill = COL[color]
    light = color in ("soft", "white")
    fg = "#334155" if light else "#fff"
    stroke = ' stroke="#cbd5e1"' if light else ""
    cy = y + h / 2
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{fill}"{stroke}/>'
    if sub:
        s += (f'<text x="{x + w / 2}" y="{cy - 7}" text-anchor="middle" dominant-baseline="middle" '
              f'font-size="{size}" font-weight="700" fill="{fg}">{esc(title)}</text>'
              f'<text x="{x + w / 2}" y="{cy + 12}" text-anchor="middle" font-size="10.5" fill="{fg}" opacity="0.88">{esc(sub)}</text>')
    else:
        s += (f'<text x="{x + w / 2}" y="{cy}" text-anchor="middle" dominant-baseline="middle" '
              f'font-size="{size}" font-weight="700" fill="{fg}">{esc(title)}</text>')
    return s


def diamond(cx, cy, w, h, text, color="amber"):
    pts = f"{cx},{cy - h / 2} {cx + w / 2},{cy} {cx},{cy + h / 2} {cx - w / 2},{cy}"
    return (f'<polygon points="{pts}" fill="{COL[color]}"/>'
            f'<text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="middle" font-size="12.5" '
            f'font-weight="700" fill="#fff">{esc(text)}</text>')


def _head(x2, y2, ang, color):
    a1 = (x2 - 8 * math.cos(ang) + 5 * math.sin(ang), y2 - 8 * math.sin(ang) - 5 * math.cos(ang))
    a2 = (x2 - 8 * math.cos(ang) - 5 * math.sin(ang), y2 - 8 * math.sin(ang) + 5 * math.cos(ang))
    return f'<path d="M{a1[0]:.1f} {a1[1]:.1f} L{x2} {y2} L{a2[0]:.1f} {a2[1]:.1f} Z" fill="{color}"/>'


def arrow(x1, y1, x2, y2, color="#0050C0", dash=False, label="", lx=None, ly=None):
    ang = math.atan2(y2 - y1, x2 - x1)
    d = ' stroke-dasharray="5 4"' if dash else ""
    s = (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2.2"{d}/>'
         + _head(x2, y2, ang, color))
    if label:
        s += text((x1 + x2) / 2 if lx is None else lx, (y1 + y2) / 2 - 7 if ly is None else ly, label, 11, "#334155")
    return s


def path(points, color="#0050C0", dash=False, label="", lx=0, ly=0):
    """Spezzata con freccia finale: points = [(x, y), ...]."""
    d = " ".join(("M" if i == 0 else "L") + f"{x} {y}" for i, (x, y) in enumerate(points))
    dd = ' stroke-dasharray="5 4"' if dash else ""
    (xa, ya), (xb, yb) = points[-2], points[-1]
    s = (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2.2"{dd}/>'
         + _head(xb, yb, math.atan2(yb - ya, xb - xa), color))
    if label:
        s += text(lx, ly, label, 11, "#334155")
    return s


def text(x, y, t, size=12, color="#334155", weight="400", anchor="middle", halo=True):
    """Etichetta; il contorno chiaro la stacca dalle linee che attraversa."""
    h = ' stroke="#f8fafc" stroke-width="4" stroke-linejoin="round" paint-order="stroke"' if halo else ""
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" font-weight="{weight}" '
            f'fill="{color}"{h}>{esc(t)}</text>')


def zone(x, y, w, h, title, color="#e8eef7"):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{color}" stroke="#d5deea"/>'
            + text(x + 14, y + 20, title, 11.5, "#003a90", "700", "start", False))


def fig(body, width, height, cap, title=""):
    t = text(20, 28, title, 12, "#003a90", "700", "start") if title else ""
    return (f'<figure class="fig"><svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" {FONT} '
            f'role="img"><rect width="{width}" height="{height}" fill="#f8fafc" rx="12"/>{t}{body}</svg>'
            f'<figcaption class="cap">{cap}</figcaption></figure>')


def flow(nodes, cap, title="", width=900):
    """Flusso orizzontale: nodes = [(titolo, sottotitolo, colore)]."""
    n = len(nodes)
    gap = 36
    w = (width - 40 - gap * (n - 1)) / n
    top = 50 if title else 26
    h = 64
    s = []
    for i, (t, sub, col) in enumerate(nodes):
        x = 20 + i * (w + gap)
        s.append(box(x, top, w, h, t, sub, col))
        if i < n - 1:
            s.append(arrow(x + w + 2, top + h / 2, x + w + gap - 2, top + h / 2))
    return fig("".join(s), width, top + h + 26, cap, title)


def seq(actors, events, cap, title="", width=900):
    """Diagramma di sequenza.
    actors = [(nome, sottotitolo, colore)];
    events = (da, a, testo[, tratteggio]) per un messaggio, ("nota", i, testo) per una nota,
             ("sep", testo) per una separazione con testo."""
    n = len(actors)
    top = 50 if title else 22
    colw = (width - 40) / n
    xs = [20 + colw * i + colw / 2 for i in range(n)]
    bw, bh = min(colw - 24, 190), 50
    y = top + bh + 34
    body = []
    for ev in events:
        if ev[0] == "nota":
            _, i, t = ev
            tw = max(len(t) * 6.6 + 24, 90)
            body.append(f'<rect x="{xs[i] - tw / 2}" y="{y - 15}" width="{tw}" height="26" rx="6" fill="#fff7ed" stroke="#fdba74"/>')
            body.append(text(xs[i], y + 3, t, 11, "#9a3412", "600", "middle", False))
            y += 40
        elif ev[0] == "sep":
            body.append(f'<line x1="24" y1="{y - 4}" x2="{width - 24}" y2="{y - 4}" stroke="#cbd5e1" stroke-dasharray="2 4"/>')
            tw = len(ev[1]) * 6.4 + 22
            body.append(f'<rect x="{width / 2 - tw / 2}" y="{y - 15}" width="{tw}" height="22" rx="11" fill="#f8fafc" stroke="#cbd5e1"/>')
            body.append(text(width / 2, y + 0, ev[1], 11, "#475569", "600", "middle", False))
            y += 36
        else:
            a, b, t = ev[0], ev[1], ev[2]
            dash = len(ev) > 3 and ev[3]
            color = "#475569" if dash else "#0050C0"
            if a == b:
                x = xs[a]
                body.append(f'<path d="M{x} {y - 8} h34 v18 h-30" fill="none" stroke="{color}" stroke-width="2"/>'
                            + _head(x + 2, y + 10, math.pi, color))
                body.append(text(x + 42, y + 5, t, 11, "#334155", "400", "start"))
                y += 42
            else:
                x1, x2 = xs[a], xs[b]
                off = 5 if x2 > x1 else -5
                body.append(arrow(x1 + off, y, x2 - off, y, color, dash))
                body.append(text((x1 + x2) / 2, y - 8, t, 11, "#334155"))
                y += 42
    height = y + 10
    head = []
    for i, (name, sub, color) in enumerate(actors):
        head.append(f'<line x1="{xs[i]}" y1="{top + bh}" x2="{xs[i]}" y2="{height - 14}" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="4 4"/>')
        head.append(box(xs[i] - bw / 2, top, bw, bh, name, sub, color))
    return fig("".join(head + body), width, height, cap, title)


def file_map(rows, cap):
    """Mappa dei file: rows = [(percorso, ruolo)]; le righe si contano a ogni generazione."""
    out = []
    for f, role in rows:
        n = len((ROOT / f).read_text().splitlines())
        out.append([c(f), str(n), role])
    return table(["File", "Righe", "Ruolo"], out, cap, "file-map")


# ── I risultati delle prove, letti dai file che le prove scrivono ────────
def impronta_attuale():
    import subprocess
    return subprocess.run([str(ROOT / "tools/impronta.sh")], capture_output=True, text=True).stdout.strip()


def risultati_prove():
    """Una riga per suite: esito, data, commit, impronta e se l'impronta è quella del codice attuale."""
    import json
    attuale = impronta_attuale()
    righe = []
    for nome, f, unita in (("tests/engine.sh", "tests/risultati/engine.json", "controlli"),
                           ("tests/container/esegui.sh", "tests/container/risultati/risultati.json", "scenari"),
                           ("tests/vm/esegui.sh", "tests/vm/risultati/risultati.json", "scenari")):
        path = ROOT / f
        if not path.exists():
            righe.append([c(nome), "mai eseguita", "", "", "", ""])
            continue
        d = json.loads(path.read_text())
        m = d.get("meta", d)
        esito = f"{m['ok']} riusciti su {m['totale']} {unita}"
        if m.get("no"):
            esito += f", <b>{m['no']} falliti</b>"
        if m.get("non_provati"):
            esito += f", {m['non_provati']} non provati"
        if m.get("solo"):
            esito += f" (solo {m['solo']})"
        imp = m.get("impronta", "sconosciuta")
        righe.append([c(nome), esito, m.get("data", ""), c(m.get("commit", "sconosciuto")), c(imp),
                      "sì" if imp == attuale else "<b>no</b>: codice cambiato dopo la prova"])
    return table(["Suite", "Esito", "Data", "Commit", "Impronta", "Vale per il codice attuale"], righe,
                 "«TAB» — L'ultima esecuzione di ogni suite (" + c("tests/*/risultati/") + "); impronta del codice "
                 "attuale: " + c(attuale))


# ── La guida integrata come fonte del riferimento ───────────────────────
def help_items(name):
    """Le voci «etichetta¦descrizione» di un array della guida in italiano (lib/lingue/aiuto-it.sh)."""
    src = (ROOT / "lib/lingue/aiuto-it.sh").read_text()
    block = src[src.index(name + "=("):]
    block = block[:block.index("\n)")]
    items = []
    for raw in re.findall(r'^\t"((?:[^"\\]|\\.)*)"$', block, re.M):
        flag, desc = raw.replace('\\"', '"').split("¦", 1)
        items.append((flag, desc))
    return items


def help_reference(name, kind):
    items = help_items(name)
    pairs = [(esc(f), esc(d)) for f, d in items]
    attrs = [f' data-help="{html.escape(f)}" data-kind="{kind}"' for f, _ in items]
    return dl(pairs, attrs)


# ── Copertina ──────────────────────────────────────────────────────────
LOGO = """<div class="cover-logo"><svg viewBox="0 0 520 100" width="270" height="52" xmlns="http://www.w3.org/2000/svg" aria-label="AMS">
<defs><linearGradient id="lg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#8fb6ff"/><stop offset="1" stop-color="#ffffff"/></linearGradient></defs>
<rect x="8" y="22" width="92" height="62" rx="10" fill="url(#lg)"/>
<path d="M12 28 L54 58 L96 28" fill="none" stroke="#0050C0" stroke-width="6" stroke-linejoin="round"/>
<path d="M66 72 l9 9 l16 -18" fill="none" stroke="#0050C0" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M80 72 l9 9 l16 -18" fill="none" stroke="#cfe0ff" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
<text x="124" y="78" font-size="70" font-weight="800" fill="#ffffff">AMS</text>
<text x="290" y="78" font-size="38" font-weight="500" fill="#cfe0ff">Messaging</text></svg></div>"""


# ── Assemblaggio ─────────────────────────────────────────────────────────
def load_chapters(folder):
    chapters = []
    sys.path.insert(0, str(HERE))
    for f in sorted((HERE / folder).glob("ch[0-9][0-9]_*.py")):
        spec = importlib.util.spec_from_file_location(f"{folder}_{f.stem}", f)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        chapters.append(mod.CHAPTER)
    return chapters


def number(doc):
    out, counters, cur = [], {}, 0
    for part in re.split(r'(<section class="chapter" id="ch\d+">)', doc):
        m = re.match(r'<section class="chapter" id="ch(\d+)">', part)
        if m:
            cur = int(m.group(1))
            counters = {"FIG": 0, "TAB": 0}
            out.append(part)
            continue

        def num(mm):
            k = mm.group(1)
            counters[k] += 1
            return f'{"Figura" if k == "FIG" else "Tabella"} {cur}.{counters[k]}'
        out.append(re.sub(r"«(FIG|TAB)»", num, part) if counters else part)
    return "".join(out)


def build(kind, outdir):
    meta = MANUALS[kind]
    css = (HERE / "stile.css").read_text() + EXTRA_CSS
    toc, body = [], []
    for ci, (ctitle, sections) in enumerate(load_chapters(kind), 1):
        toc.append(f'<li class="toc-ch"><a href="#ch{ci}"><span class="toc-n">{ci}</span><span class="toc-t">{esc(ctitle)}</span></a></li>')
        body.append(f'<section class="chapter" id="ch{ci}"><div class="ch-head"><span class="ch-kick">Capitolo {ci}</span>'
                    f'<h2 class="h-ch">{esc(ctitle)}</h2></div>')
        for si, (stitle, shtml) in enumerate(sections, 1):
            sid = f"ch{ci}s{si}"
            toc.append(f'<li class="toc-se"><a href="#{sid}"><span class="toc-n">{ci}.{si}</span><span class="toc-t">{esc(stitle)}</span></a></li>')
            body.append(f'<section class="sec" id="{sid}"><h3 class="h-sec">{ci}.{si} · {esc(stitle)}</h3>{shtml}</section>')
        body.append("</section>")
    doc = number("".join(body))
    page = f"""<!doctype html><html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{meta["title"]}</title>
<style>{css}</style></head>
<body>
<div class="doc">
  <section class="cover">
    {LOGO}
    <div class="cover-kicker">{meta["kicker"]}</div>
    <h1 class="cover-title">{meta["h1"]}</h1>
    <div class="cover-sub">{meta["sub"]}</div>
    <div class="cover-meta">
      <div><span>Versione</span><b>{VERSION}</b></div>
      <div><span>Data</span><b>{DATE}</b></div>
      <div><span>Stato</span><b>Prototipo · Riservato</b></div>
    </div>
    <div class="cover-swoosh"></div>
  </section>
  <div class="with-side">
    <aside class="side"><div class="side-inner"><h2 class="toc-head">Indice</h2><ul class="toc-list">{"".join(toc)}</ul></div></aside>
    <main class="main">{doc}</main>
  </div>
  <footer class="doc-foot">AMS — Advanced Messaging System for linux · {meta["h1"]} v{VERSION} · {DATE} · Documento riservato · Copyright (c) 2026 nic-fio</footer>
</div></body></html>
"""
    out = pathlib.Path(outdir) / meta["file"]
    out.write_text(page, encoding="utf-8")
    return out, len(page)


if __name__ == "__main__":
    outdir = sys.argv[1] if len(sys.argv) > 1 else ROOT / "docs"
    for k in MANUALS:
        f, n = build(k, outdir)
        print("scritto", f, n, "byte")
