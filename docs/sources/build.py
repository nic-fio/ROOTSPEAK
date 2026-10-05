"""Generator of the RootSpeak manuals, in the common style of the 7 projects' manuals.

It produces two self-contained HTML files (no external files: style, logo and
script are embedded):
  "docs/User Manual.html"       from the chapters in user/chNN_*.py
  "docs/Technical Manual.html"  from the chapters in technical/chNN_*.py

The manuals are in English: chapter texts, captions and the labels below.

Each chapter exposes CHAPTER = (title, [(section_title, html), ...]).
The placeholders «FIG» and «TAB» in the captions become «Figure N.M» and
«Table N.M», numbered per chapter.

Common style (the same in all the manuals of the 7 projects, not to be changed here):
  style.css       the style, embedded first and identical byte for byte;
  manual.js       sidebar search, index, Copy button;
  cover-logo.png  the logo with a transparent background, for the cover.
The rules of RootSpeak alone live in RSPEAK_CSS, below.

    python3 docs/sources/build.py            regenerates the two manuals
    python3 docs/sources/build.py FOLDER     writes them into FOLDER (used by tools/check-docs.py)

It needs the pygments library (package python3-pygments).
"""
import base64
import html
import importlib.util
import math
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
DATE = "October 2026"
VERSION = re.search(r'^#define RSPEAK_VERSION "([^"]+)"', (ROOT / "src/common.h").read_text(), re.M).group(1)

MANUALS = {
    "user": dict(file="User Manual.html", title="User Manual — RootSpeak", h1="User Manual", index=False),
    "technical": dict(file="Technical Manual.html", title="Technical Manual — RootSpeak", h1="Technical Manual",
                      index=True),
}

# The common footer, with the licence.
FOOTER = "RootSpeak · {manual} · Version {version} · {date} · © 2026 Nicola Fiorillo · Licence: free, source available"

# Index words to show as code (window.MANUAL_CODE_TERMS of manual.js).
CODE_TERMS = ["zenity"]

# RootSpeak only: rules for elements that exist only in the RootSpeak manuals, after style.css.
RSPEAK_CSS = """
/* RootSpeak only: real TUI screenshots, keys, terminals, sample dialogs, tree, states, glossary */
.code.tui-screen{background:#111827;color:#e5e7eb;line-height:1.15;font-size:10.2px;overflow-x:auto;font-family:"DejaVu Sans Mono",ui-monospace,Menlo,Consolas,monospace}
.tui-screen .a-b{font-weight:700;color:#fff}.tui-screen .a-d{color:#6b7280}.tui-screen .a-v{background:#e5e7eb;color:#111827;font-weight:700}
.tui-screen .a-32{color:#4ade80}.tui-screen .a-33{color:#facc15}.tui-screen .a-31{color:#f87171}.tui-screen .a-36{color:#22d3ee}
.tui-screen .a-90{color:#9ca3af}.tui-screen .a-b.a-32{color:#86efac}.tui-screen .a-b.a-33{color:#fde047}.tui-screen .a-b.a-36{color:#67e8f9}
.key{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.85em;font-weight:700;color:#0f172a;background:#fff;border:1px solid #cbd5e1;border-bottom-width:2px;border-radius:5px;padding:.05em .42em;white-space:nowrap}
.steps .code,.steps .code-w{margin:10px 0 4px} .steps .code-w>.code{margin:0}
.code .pr{color:#93c5fd} .code .cmd{color:#fff;font-weight:700} .code .am{color:#fdba74;font-weight:600}
.code .er{color:#fca5a5} .code .bx{color:#7dd3fc} .code .dim{color:#94a3b8}
.code.tui{line-height:1.12;font-size:12.5px;font-family:"DejaVu Sans Mono",ui-monospace,Menlo,Consolas,monospace}
.code-t{display:block;font-family:Outfit,Segoe UI,Arial,sans-serif;font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#64748b;margin:16px 0 -8px}
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
.tree{background:transparent;border:0;padding:4px 8px;font-family:ui-monospace,Menlo,Consolas,monospace;font-size:13px;line-height:1.6;color:#0f172a;overflow-x:auto;margin:0;text-align:left}
.tree .d{color:#0050C0;font-weight:700} .tree .m{color:#64748b}
.pill{display:inline-block;font-size:12px;font-weight:700;border-radius:999px;padding:.1em .65em;white-space:nowrap}
.p-ok{background:#dcfce7;color:#166534} .p-wait{background:#dbeafe;color:#1e40af} .p-snooze{background:#fef3c7;color:#92400e}
.p-off{background:#e2e8f0;color:#475569} .p-info{background:#f1f5f9;color:#334155;border:1px solid #cbd5e1}
.gloss{margin:12px 0} .gloss dt{font-weight:700;color:#003a90;font-size:15px;margin-top:12px} .gloss dd{margin:2px 0 0;color:#334155;font-size:14px}
.gloss dt[id]{scroll-margin-top:16px}
"""

# ── Text ────────────────────────────────────────────────────────────────
def esc(t):
    return html.escape(t, quote=False)


def c(t):
    return f"<code>{esc(t)}</code>"


def ui(label):
    """The exact label of a dialog or of a button."""
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


def note(t, title="Note."):
    return f'<div class="callout c-info"><div class="callout-i">i</div><div><b>{title}</b> {t}</div></div>'


def warn(t, title="Warning."):
    return f'<div class="callout c-warn"><div class="callout-i">!</div><div><b>{title}</b> {t}</div></div>'


def tip(t, title="Tip."):
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
    from pygments.lexers import CLexer, BashLexer, IniLexer, PythonLexer, TextLexer
    from pygments.token import Comment, Keyword, Name, String
    lx = {"c": CLexer, "bash": BashLexer, "conf": IniLexer, "python": PythonLexer, "text": TextLexer}[lang]()
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
    """A terminal session: prompts, commands, RootSpeak lines, errors."""
    lines = []
    for line in text.strip("\n").split("\n"):
        m = PROMPT.match(line)
        if m:
            lines.append(f'<span class="pr">{esc(m.group(1))}</span><span class="cmd">{esc(m.group(2))}</span>')
        elif line.startswith("rspeak: ") or "Permission denied" in line:
            lines.append(f'<span class="er">{esc(line)}</span>')
        elif line.startswith("[RootSpeak]"):
            lines.append(f'<span class="am">{esc(line)}</span>')
        elif line.startswith("──") or (tui and line[:1] in "┌├└"):
            lines.append(f'<span class="bx">{esc(line)}</span>')
        else:
            lines.append(esc(line))
    cls = "code tui" if tui else "code"
    head = f'<span class="code-t">{esc(title)}</span>' if title else ""
    return head + f'<pre class="{cls}"><code>' + "\n".join(lines) + "</code></pre>"


def tree(lines, cap):
    """A folder tree: lines 'path  # comment'."""
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
            f'<div class="dlg-k"><span>Later</span><span>I have read it</span></div></div></div>'
            f'<figcaption class="cap">{cap}</figcaption></figure>')


def notification(title, body, cap):
    return (f'<figure class="fig"><div class="shot"><div class="ntf" role="img" aria-label="Notification">'
            f'<div class="ntf-a">RootSpeak</div><b>{esc(title)}</b>{esc(body)}</div></div>'
            f'<figcaption class="cap">{cap}</figcaption></figure>')


# ── SVG figures in the style of IR_Service ─────────────────────────────
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
    """A polyline with an arrowhead at the end: points = [(x, y), ...]."""
    d = " ".join(("M" if i == 0 else "L") + f"{x} {y}" for i, (x, y) in enumerate(points))
    dd = ' stroke-dasharray="5 4"' if dash else ""
    (xa, ya), (xb, yb) = points[-2], points[-1]
    s = (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2.2"{dd}/>'
         + _head(xb, yb, math.atan2(yb - ya, xb - xa), color))
    if label:
        s += text(lx, ly, label, 11, "#334155")
    return s


def text(x, y, t, size=12, color="#334155", weight="400", anchor="middle", halo=True):
    """A label; the light outline sets it apart from the lines it crosses."""
    h = ' stroke="#f8fafc" stroke-width="4" stroke-linejoin="round" paint-order="stroke"' if halo else ""
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" font-weight="{weight}" '
            f'fill="{color}"{h}>{esc(t)}</text>')


def zone(x, y, w, h, title, color="#e8eef7"):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{color}" stroke="#d5deea"/>'
            + text(x + 14, y + 20, title, 11.5, "#003a90", "700", "start", False))


def tui_screen(name, cap):
    """A real TUI screenshot (docs/sources/screens/NAME.ans, captured by
    tools/tui-screenshots.sh), with its colours, exactly as on the screen."""
    raw = (HERE / "screens" / f"{name}.ans").read_bytes().decode("utf-8", "replace")
    raw = re.sub(r"\x1b\[\?[0-9;]*[a-zA-Z]|\x1b\[[0-9]*;[0-9]*H|\x1b\[J|\r", "", raw)
    classes, out = set(), []
    for piece in re.split(r"(\x1b\[[0-9;]*m)", raw):
        m = re.fullmatch(r"\x1b\[([0-9;]*)m", piece)
        if m:
            for sgr in (m.group(1) or "0").split(";"):
                if sgr in ("0", ""):
                    classes = set()
                elif sgr == "1":
                    classes.add("a-b")
                elif sgr == "2":
                    classes.add("a-d")
                elif sgr == "7":
                    classes.add("a-v")
                elif sgr in ("31", "32", "33", "36", "90"):
                    classes = {x for x in classes if not x.startswith("a-3") and x != "a-90"} | {f"a-{sgr}"}
            continue
        if piece:
            out.append(f'<span class="{" ".join(sorted(classes))}">{esc(piece)}</span>' if classes else esc(piece))
    return (f'<figure class="fig"><pre class="code tui-screen"><code>{"".join(out)}</code></pre>'
            f'<figcaption class="cap">{cap}</figcaption></figure>')


def fig(body, width, height, cap, title=""):
    t = text(20, 28, title, 12, "#003a90", "700", "start") if title else ""
    return (f'<figure class="fig"><svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" {FONT} '
            f'role="img"><rect width="{width}" height="{height}" fill="#f8fafc" rx="12"/>{t}{body}</svg>'
            f'<figcaption class="cap">{cap}</figcaption></figure>')


def flow(nodes, cap, title="", width=900):
    """A horizontal flow: nodes = [(title, subtitle, colour)]."""
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
    """A sequence diagram.
    actors = [(name, subtitle, colour)];
    events = (from, to, text[, dashed]) for a message, ("note", i, text) for a note,
             ("sep", text) for a separator with a text."""
    n = len(actors)
    top = 50 if title else 22
    colw = (width - 40) / n
    xs = [20 + colw * i + colw / 2 for i in range(n)]
    bw, bh = min(colw - 24, 190), 50
    y = top + bh + 34
    body = []
    for ev in events:
        if ev[0] == "note":
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
                # a light background, so that the lifelines it crosses do not run through the label
                tw = len(t) * 6.0 + 10
                body.append(f'<rect x="{(x1 + x2) / 2 - tw / 2}" y="{y - 21}" width="{tw}" height="17" rx="3" fill="#f8fafc"/>')
                body.append(text((x1 + x2) / 2, y - 8, t, 11, "#334155"))
                y += 42
    height = y + 10
    head = []
    for i, (name, sub, color) in enumerate(actors):
        head.append(f'<line x1="{xs[i]}" y1="{top + bh}" x2="{xs[i]}" y2="{height - 14}" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="4 4"/>')
        head.append(box(xs[i] - bw / 2, top, bw, bh, name, sub, color))
    return fig("".join(head + body), width, height, cap, title)


def file_map(rows, cap):
    """The file map: rows = [(path, role)]; the lines are counted at every generation."""
    out = []
    for f, role in rows:
        n = len((ROOT / f).read_text().splitlines())
        out.append([c(f), str(n), role])
    return table(["File", "Lines", "Role"], out, cap, "file-map")


# ── Test results, read from the files the tests write ──────────────────
def current_fingerprint():
    import subprocess
    return subprocess.run([str(ROOT / "tools/fingerprint.sh")], capture_output=True, text=True).stdout.strip()


def test_results():
    """One row per suite: outcome, date, commit, fingerprint and whether the fingerprint is the current code's."""
    import json
    current = current_fingerprint()
    rows = []
    for name, f, unit in (("tests/engine.sh", "tests/results/engine.json", "checks"),
                          ("tests/container/run.sh", "tests/container/results/results.json", "scenarios"),
                          ("tests/vm/run.sh", "tests/vm/results/results.json", "scenarios"),
                          ("tests/distros/run.sh", "tests/distros/results/summary.json", "distributions")):
        path = ROOT / f
        if not path.exists():
            rows.append([c(name), "never run", "", "", "", ""])
            continue
        d = json.loads(path.read_text())
        m = d.get("meta", d)
        outcome = f"{m['ok']} of {m['total']} {unit} passed"
        if m.get("failed"):
            outcome += f", <b>{m['failed']} failed</b>"
        if m.get("not_tested"):
            outcome += f", {m['not_tested']} not tested"
        if m.get("only"):
            outcome += f" (only {m['only']})"
        fp = m.get("fingerprint", "unknown")
        rows.append([c(name), outcome, m.get("date", ""), c(m.get("commit", "unknown")), c(fp),
                     "yes" if fp == current else "<b>no</b>: code changed after the run"])
    return table(["Suite", "Result", "Date", "Commit", "Fingerprint", "Valid for the current code"], rows,
                 "«TAB» — The last run of each suite (" + c("tests/*/results/") + "); fingerprint of the current "
                 "code: " + c(current))


def distro_results():
    """One row per distribution of the last tests/distros/run.sh: outcome and what was not tested, with the reason."""
    import json
    path = ROOT / "tests/distros/results/summary.json"
    if not path.exists():
        return p("The distributions have not been tested yet.")
    current = current_fingerprint()
    summary = json.loads(path.read_text())
    rows = []
    for d in summary["distributions"]:
        if d.get("not_run"):
            rows.append([c(d["name"]), "—", "<b>not run</b>: " + esc(d["not_run"]), ""])
            continue
        res = json.loads((ROOT / "tests/distros/results" / d["name"] / "results.json").read_text())["results"]
        why = []
        for r in res:
            if r["outcome"] != "--" or r["code"] == "I1":
                continue
            shell = r["code"].removeprefix("K-")
            why.append(f"{shell}: not in the distribution's packages" if r["details"] == "user missing"
                       else f"{shell}: the login shell already fails on the distribution's own files ("
                       + esc(r["details"][:80]) + ")" if r["code"].startswith("K-") else f"{r['code']}: {esc(r['details'][:80])}")
        outcome = f"{d['ok']} of {d['total']} passed" + (f", <b>{d['failed']} failed</b> ({', '.join(d['failed_codes'])})"
                                                        if d["failed"] else "")
        if d.get("fingerprint") != current:
            outcome += " — <b>older code</b>"
        rows.append([c(d["name"]), esc(d["system"]), outcome, "; ".join(why) or "—"])
    return table(["Name", "System", "Scenarios", "Not tested, and why"], rows,
                 "«TAB» — RootSpeak on each distribution: the last run of " + c("tests/distros/run.sh")
                 + " (the desktop scenario is never tested in a container); RootSpeak installed from "
                 + esc(summary["meta"].get("installed", "source, built on each distribution")))


def desktop_results():
    """One row per desktop profile of tests/vm: system, desktop, outcome of its last run."""
    import json
    current = current_fingerprint()
    rows = []
    for prof in sorted((ROOT / "tests/vm/desktops").glob("*.yaml")):
        name = prof.stem
        label = re.search(r"^# desktop: (.*)$", prof.read_text(), re.M).group(1)
        res = ROOT / ("tests/vm/results" if name == "debian-gnome" else f"tests/vm/desktops/results/{name}") / "results.json"
        if not res.exists():
            rows.append([c(name), "—", esc(label), "never run"])
            continue
        d = json.loads(res.read_text())
        m = d["meta"]
        failed = [r["code"] for r in d["results"] if r["outcome"] == "NO"]
        outcome = f"{m['ok']} of {m['total']} passed" + (f", <b>{m['failed']} failed</b> ({', '.join(failed)})"
                                                        if failed else "")
        if m.get("fingerprint") != current:
            outcome += " — <b>older code</b>"
        system, _, rest = m["system"].partition(", VM with ")
        # the desktop and the kind of session (Wayland or X11) as measured in the run
        rows.append([c(name), esc(system), esc(rest.split(", desktop of")[0] or label), outcome])
    return table(["Profile", "System", "Desktop", "Scenarios"], rows,
                 "«TAB» — RootSpeak on each desktop: the last run of " + c("tests/vm/run.sh PROFILE")
                 + " (the four shells other than bash are tested in the containers)")


# ── The built-in help as the source of the reference ───────────────────
# The groups of the built-in help, as they are named in src/help.c.
# where the packages install the manuals (DOCDIR in the Makefile with PREFIX=/usr)
PACKAGE_DOCDIR = "/usr/share/doc/rootspeak"
HELP_GROUPS = {"RSPEAK_HELP_COMMANDS": "COMMANDS", "RSPEAK_HELP_OPTIONS": "OPTIONS",
               "RSPEAK_HELP_EXAMPLES": "EXAMPLES", "RSPEAK_HELP_FILES": "FILES"}


def help_items(name):
    """The «label¦description» items of a group of the built-in help, read from
    the array of the same group in src/help.c, in its order. The manuals use
    them as they are: tools/check-docs.py checks that they match."""
    src = (ROOT / "src" / "help.c").read_text()
    m = re.search(r"static const char \*const " + HELP_GROUPS[name] + r"\[\] = \{(.*?)\n\};", src, re.S)
    # DOCDIR (the folder of the manuals, from the Makefile) as the packages install it
    body = re.sub(r"\bDOCDIR\b", '"' + PACKAGE_DOCDIR + '"', m.group(1))
    items = []
    for lit in re.findall(r'^\s*((?:"(?:[^"\\]|\\.)*"\s*)+),?\s*$', body, re.M):
        s = "".join(re.findall(r'"((?:[^"\\]|\\.)*)"', lit))
        items.append(re.sub(r"\\(.)", lambda x: {"n": "\n", "t": "\t"}.get(x.group(1), x.group(1)), s))
    return [tuple(i.split("¦", 1)) for i in items]


def help_reference(name, kind):
    items = help_items(name)
    pairs = [(esc(f), esc(d)) for f, d in items]
    attrs = [f' data-help="{html.escape(f)}" data-kind="{kind}"' for f, _ in items]
    return dl(pairs, attrs)


# ── Assembly ─────────────────────────────────────────────────────────────
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
            return f'{"Figure" if k == "FIG" else "Table"} {cur}.{counters[k]}'
        out.append(re.sub(r"«(FIG|TAB)»", num, part) if counters else part)
    return "".join(out)


def glossary_index(doc, gloss_ch):
    """The index of the technical manual comes from the glossary, with no new entries: each
    glossary term (its name, without a trailing note in brackets) points to its definition
    and to the chapters and sections that the definition itself cites. manual.js builds
    the index from the data-index attributes."""
    start = doc.index(f'<section class="chapter" id="{gloss_ch}">')
    end = doc.index('<section class="chapter"', start + 1) if '<section class="chapter"' in doc[start + 1:] else len(doc)
    part, targets, slugs = doc[start:end], {}, set()

    def term(m):
        name = re.sub(r"\s*\(it\. [^)]*\)$", "", html.unescape(re.sub(r"<[^>]+>", "", m.group(1)))).strip()
        slug = "g-" + re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        assert slug not in slugs, f"glossary: two terms with the same id {slug}"
        slugs.add(slug)
        for ref in dict.fromkeys(re.findall(r'href="#(ch\d+(?:s\d+)?)"', m.group(2))):
            targets.setdefault(ref, []).append(name)
        return f'<dt id="{slug}" data-index="{html.escape(name)}">{m.group(1)}</dt><dd>{m.group(2)}</dd>'
    part = re.sub(r"<dt>(.*?)</dt><dd>(.*?)</dd>", term, part, flags=re.S)
    doc = doc[:start] + part + doc[end:]
    for ref, names in targets.items():
        tag = re.search(rf'<section class="(chapter|sec)" id="{ref}">', doc).group(0)
        doc = doc.replace(tag, tag[:-1] + f' data-index="{html.escape(";".join(names))}">', 1)
    return doc


def build(kind, outdir):
    meta = MANUALS[kind]
    css = (HERE / "style.css").read_text() + RSPEAK_CSS
    js = (HERE / "manual.js").read_text()
    logo = base64.b64encode((HERE / "cover-logo.png").read_bytes()).decode()
    toc, body, gloss_ch = [], [], None
    chapters = load_chapters(kind)
    for ci, (ctitle, sections) in enumerate(chapters, 1):
        if ctitle == "Glossary":
            gloss_ch = f"ch{ci}"
        toc.append(f'<li class="toc-ch"><a href="#ch{ci}"><span class="toc-n">{ci}</span><span class="toc-t">{esc(ctitle)}</span></a></li>')
        body.append(f'<section class="chapter" id="ch{ci}"><div class="ch-head"><span class="ch-kick">Chapter {ci}</span>'
                    f'<h2 class="h-ch">{esc(ctitle)}</h2></div>')
        for si, (stitle, shtml) in enumerate(sections, 1):
            sid = f"ch{ci}s{si}"
            toc.append(f'<li class="toc-se"><a href="#{sid}"><span class="toc-n">{ci}.{si}</span><span class="toc-t">{esc(stitle)}</span></a></li>')
            body.append(f'<section class="sec" id="{sid}"><h3 class="h-sec">{ci}.{si} · {esc(stitle)}</h3>{shtml}</section>')
        body.append("</section>")
    doc = number("".join(body))
    if meta["index"]:
        doc = glossary_index(doc, gloss_ch)
        ni = len(chapters) + 1
        toc.append(f'<li class="toc-ch"><a href="#index"><span class="toc-n">{ni}</span><span class="toc-t">Index</span></a></li>')
        doc += (f'<section class="chapter" id="index"><div class="ch-head"><span class="ch-kick">Chapter {ni}</span>'
                f'<h2 class="h-ch">Index</h2></div>'
                f'<p class="lead">The terms of the <a href="#{gloss_ch}">glossary</a>, in alphabetical order, with their '
                f'definition and the chapters that the definition refers to.</p>'
                f'<div id="index-list" class="idx"><noscript><div class="callout c-info"><div class="callout-i">i</div>'
                f'<div><b>Note.</b> The index is built by the browser and requires JavaScript. Without it, use the '
                f'chapter contents and the <a href="#{gloss_ch}">glossary</a>.</div></div></noscript></div></section>')
    search = ('<div class="srch" id="srch" hidden><label class="toc-head" for="srch-q">Search</label>'
              '<input type="search" id="srch-q" class="srch-q" placeholder="A word, an option…  ( / )" '
              'autocomplete="off" spellcheck="false"><div class="srch-info" id="srch-info" aria-live="polite"></div>'
              '<ol class="srch-res" id="srch-res"></ol></div>')
    terms = "[" + ",".join(f'"{t}"' for t in CODE_TERMS) + "]"
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{meta["title"]}</title>
<style>{css}</style></head>
<body>
<div class="doc">
  <section class="cover cover-w">
    <div class="cover-logo"><img src="data:image/png;base64,{logo}" alt="RootSpeak"></div>
    <h1 class="cover-title">{meta["h1"]}</h1>
    <div class="cover-meta">
      <div><span>Version</span><b>{VERSION}</b></div>
      <div><span>Date</span><b>{DATE}</b></div>
    </div>
  </section>
  <div class="with-side">
    <aside class="side"><div class="side-inner">{search}<h2 class="toc-head">Contents</h2><ul class="toc-list" id="toc">{"".join(toc)}</ul></div></aside>
    <main class="main">{doc}</main>
  </div>
  <footer class="doc-foot">{FOOTER.format(manual=meta["h1"], version=VERSION, date=DATE)}</footer>
</div>
<script>window.MANUAL_CODE_TERMS={terms};</script>
<script>
{js}</script>
</body></html>
"""
    out = pathlib.Path(outdir) / meta["file"]
    out.write_text(page, encoding="utf-8")
    return out, len(page)


if __name__ == "__main__":
    outdir = sys.argv[1] if len(sys.argv) > 1 else ROOT / "docs"
    for k in MANUALS:
        f, n = build(k, outdir)
        print("written", f, n, "bytes")
