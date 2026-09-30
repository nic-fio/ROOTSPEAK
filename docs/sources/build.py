"""Generatore dei manuali di AMS, sul modello dei manuali di IR_Service.

Produce due file HTML autosufficienti (nessuno script, nessun file esterno):
  "docs/User Manual.html"       dai capitoli in user/chNN_*.py
  "docs/Technical Manual.html"  dai capitoli in technical/chNN_*.py

I manuali sono in inglese: testi dei capitoli, didascalie ed etichette qui sotto.

Ogni capitolo espone CHAPTER = (titolo, [(titolo_sezione, html), ...]).
I segnaposto «FIG» e «TAB» nelle didascalie diventano «Figure N.M» e
«Table N.M», numerati per capitolo. Lo stile è in style.css.

    python3 docs/sources/build.py            rigenera i due manuali
    python3 docs/sources/build.py CARTELLA   li scrive in CARTELLA (usato da tools/check-docs.py)

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
DATE = "September 2026"
VERSION = re.search(r'^#define AMS_VERSION "([^"]+)"', (ROOT / "src/comune.h").read_text(), re.M).group(1)

MANUALS = {
    "user": dict(file="User Manual.html", title="User Manual — AMS", kicker="User documentation",
                   h1="User Manual",
                   sub="AMS — Advanced Messaging System · Messages from administrators to users, "
                       "with read confirmation"),
    "technical": dict(file="Technical Manual.html", title="Technical Manual — AMS", kicker="Technical documentation",
                    h1="Technical Manual",
                    sub="AMS — Advanced Messaging System · Architecture, message store, "
                        "delivery, confirmations and security"),
}

# Aggiunte allo stile di IR: procedure, etichette, terminali, finestre di esempio.
EXTRA_CSS = """
/* AMS: schermate vere della TUI, con i loro colori */
.code.schermo{background:#111827;color:#e5e7eb;line-height:1.15;font-size:10.2px;overflow-x:auto;font-family:"DejaVu Sans Mono",ui-monospace,Menlo,Consolas,monospace}
.schermo .a-b{font-weight:700;color:#fff}.schermo .a-d{color:#6b7280}.schermo .a-v{background:#e5e7eb;color:#111827;font-weight:700}
.schermo .a-32{color:#4ade80}.schermo .a-33{color:#facc15}.schermo .a-31{color:#f87171}.schermo .a-36{color:#22d3ee}
.schermo .a-90{color:#9ca3af}.schermo .a-b.a-32{color:#86efac}.schermo .a-b.a-33{color:#fde047}.schermo .a-b.a-36{color:#67e8f9}
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
    return (f'<figure class="fig"><div class="shot"><div class="ntf" role="img" aria-label="Notification">'
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


# Le scritte italiane delle schermate, con la traduzione inglese (quella di po/ams.pot quando
# esiste): schermata() le aggiunge alla didascalia, perché il contenuto resta uguale allo schermo.
_DISTESO = ("the text: «Sabato dalle 8 alle 12 il server sarà spento per la manutenzione dei dischi. Salvate il lavoro "
            "entro venerdì sera.» (“On Saturday from 8 to 12 the server will be switched off for disk maintenance. "
            "Save your work by Friday evening.”)")
_MESSAGGIO = ("«Messaggio 2 · Manutenzione» (“Message 2 · Maintenance”), «aggiornato alle» (“updated at”), «da root» "
              "(“from root”); " + _DISTESO + "; tabs «Destinatari (8)» (“Recipients (8)”) and «Storia» (“History”); "
              "«4 confermato · 3 consegnato · 1 inviato» (“4 confirmed · 3 delivered · 1 sent”)")
_TASTI_MESSAGGIO = ("keys «Tab destinatari/storia» (“recipients/history”), «↑/↓ scorri» (“scroll”), «s sollecita» "
                    "(“remind”), «r ritira» (“revoke”), «Esc indietro» (“back”)")
_CONFERMA = "«s Conferma» (“Confirm”), «n Annulla» (“Cancel”); key line «s conferma · n o Esc annulla» (“confirm · n or Esc cancel”)"
_INVIO_ESC = "key line «Invio conferma» (“Enter confirm”), «Esc annulla» (“cancel”)"
TRADUZIONI_SCHERMATE = {
    "list": "«AMS · messaggi inviati» (“AMS · sent messages”), «aggiornato alle» (“updated at”); columns «DATA» "
             "(“DATE”), «MESSAGGIO» (“MESSAGE”), «DESTINATARI» (“RECIPIENTS”); the example titles «Riavvio» "
             "(“Reboot”), «Il tuo account scade venerdì» (“Your account expires on Friday”), «Manutenzione» "
             "(“Maintenance”), «Aggiornamento del server · Stanotte» (“Server update · Tonight”); «[ritirato]» "
             "(“[revoked]”); «4 confermato · 3 consegnato · 1 inviato» (“4 confirmed · 3 delivered · 1 sent”), "
             "«tutti confermato (3)» (“all confirmed (3)”); keys «Invio apri» (“Enter open”), «n nuovo» (“new”), "
             "«r ritira» (“revoke”), «s sollecita» (“remind”), «p pulizia» (“purge”), «/ cerca» (“search”), "
             "«? tasti» (“keys”), «q esci» (“quit”)",
    "detail": _MESSAGGIO + "; columns «UTENTE» (“USER”) and «STATO» (“STATE”); «confermato il 30/09 18:58 "
                 "(terminale pts/0)» (“confirmed on 30/09 18:58 (terminal pts/0)”), «inviato, non consegnato» (“sent, "
                 "not delivered”), «consegnato, rimandato il 30/09 18:58» (“delivered, postponed on 30/09 18:58”); "
                 + _TASTI_MESSAGGIO,
    "history": _MESSAGGIO + "; the events «messaggio 2 consegnato a admin (terminali scritti: 0)» (“message 2 delivered "
              "to admin (terminals written: 0)”) and «messaggio 2 inviato da root a: …» (“message 2 sent by root to: "
              "…”); " + _TASTI_MESSAGGIO,
    "new": "«Nuovo messaggio» (“New message”); fields «A» (“To”), «Titolo» (“Title”), «Scadenza» (“Expires”), «Testo» "
             "(“Text”); hints «2 destinatari» (“2 recipients”), «facoltativo, una riga» (“optional, one line”), "
             "«facoltativa: 30m, 2h,» (“optional: 30m, 2h,”); the text: «Sabato dalle 8 alle 12 il server sarà spento. "
             "Salvate il lavoro entro venerdì sera.» (“On Saturday from 8 to 12 the server will be switched off. Save "
             "your work by Friday evening.”); «85 di 65536 byte» (“85 of 65536 bytes”); keys «Tab campo successivo» "
             "(“next field”), «Ctrl+E apri nell'editor» (“open in the editor”), «Ctrl+S invia» (“send”), «Esc "
             "annulla» (“cancel”)",
    "send": "over the new message, «Inviare il messaggio?» (“Send the message?”) with «A: @sviluppo (2 destinatari)» "
             "(“To: @sviluppo (2 recipients)”), «Titolo» (“Title”), «Scadenza» (“Expires”), «Testo: 85 byte» (“Text: "
             "85 bytes”); " + _CONFERMA,
    "reminder": "over the list, «Sollecitare il messaggio 2?» (“Remind message 2?”), «3 destinatari non hanno ancora "
                 "confermato.» (“3 recipients have not confirmed yet.”), «La domanda torna subito: al prompt successivo "
                 "e con la finestra sul desktop.» (“They are asked again now: at the next prompt and with the dialog on "
                 "the desktop.”); " + _CONFERMA,
    "../user/screens/help": "over the list, «Tasti» (“Keys”): «scorre la lista» (“move through the list”), «Invio» "
                                 "(Enter) «apre il messaggio: destinatari e storia» (“open the message: recipients and "
                                 "history”), «scrive e invia un messaggio nuovo» (“write and send a new message”), «ritira "
                                 "il messaggio scelto» (“revoke the selected message”), «sollecita chi non ha confermato» "
                                 "(“remind whoever has not confirmed”), «cancella i messaggi vecchi» (“delete old "
                                 "messages”), «cerca i messaggi per testo o titolo» (“search the messages by text or "
                                 "title”), «esci» (“quit”); «La lista si aggiorna da sola ogni 3 secondi.» (“The list "
                                 "updates by itself every 3 seconds.”), «La guida completa: ams --help.» (“The complete "
                                 "guide: ams --help.”), «un tasto per continuare» (“any key to continue”)",
    "../user/screens/search": "over the list, «Cerca» (“Search”), «Mostra solo i messaggi che contengono:» (“Show only "
                                 "the messages containing:”); " + _INVIO_ESC,
    "../user/screens/search-results": "at the bottom, «ricerca: «server» (Esc per toglierla)» (“search: «server» (Esc to "
                                   "clear)”)",
    "../user/screens/purge": "over the list, «Cancellare i messaggi vecchi» (“Delete old messages”), «Cancellare i "
                                   "messaggi inviati da più di (per esempio 90d, 12h):» (“Delete the messages sent more "
                                   "than (for example 90d, 12h):”); " + _INVIO_ESC,
    "../user/screens/revoke": "over the list, «Ritirare il messaggio 2?» (“Revoke message 2?”), ««Manutenzione» · 1 "
                                  "confermato · 1 consegnato» (“«Maintenance» · 1 confirmed · 1 delivered”), «Chi non "
                                  "l'ha ancora visto non lo vedrà più; finestre e domande aperte si chiudono da sole.» "
                                  "(“Whoever has not seen it yet will not see it; open dialogs and questions close by "
                                  "themselves.”); " + _CONFERMA,
    "../user/screens/guide-info": "«ams — guida» (“ams — guide”); tabs «Comandi» (“Commands”), «Opzioni» "
                                      "(“Options”), «Esempi» (“Examples”), «File» (“Files”); «NOME» (“NAME”): «ams — "
                                      "messaggi agli utenti con conferma di lettura» (“ams — messages to users with read "
                                      "confirmation”); «SINTASSI» (“SYNOPSIS”), with «[opzioni] [TESTO]» (“[options] "
                                      "[TEXT]”) and «DURATA» (“DURATION”); «DESCRIZIONE» (“DESCRIPTION”): «AMS permette "
                                      "agli amministratori di mandare messaggi di testo agli…» (“AMS lets administrators "
                                      "send text messages to the…”); «←/→ schede · ↑/↓ scorri · … · q esci» (“←/→ tabs · "
                                      "↑/↓ scroll · … · q quit”), «righe 1-16/26» (“lines 1-16/26”)",
    "../user/screens/guide-options": "«Opzioni di send» (“Send options”); «--to DEST: Destinatari, separati da "
                                         "virgole senza spazi: un utente (mario), un gruppo Unix (@sviluppo), all (tutti "
                                         "gli utenti umani) oppure online (solo quelli collegati adesso).» (“Recipients, "
                                         "separated by commas without spaces: a user (mario), a Unix group, all (every "
                                         "human user) or online (only those logged in now).”); «--title TITOLO: Titolo "
                                         "mostrato nell'intestazione del messaggio e nella finestra del desktop.» (“TITLE: "
                                         "Title shown in the message header and in the desktop dialog.”); «--expires "
                                         "DURATA: Scadenza, dopo la quale il messaggio non viene più mostrato: 30m, 2h, "
                                         "3d oppure data e ora (\"2026-10-04 12:00\"; le date a parole vanno in "
                                         "inglese).» (“DURATION: Expiry, after which the message is no longer shown: "
                                         "30m, 2h, 3d or a date and time; dates in words must be in English.”)",
}


def schermata(nome, cap):
    """Una schermata vera della TUI (docs/sources/screens/NOME.ans, catturata da
    tools/tui-screenshots.sh), con i suoi colori. Il contenuto resta uguale allo schermo;
    la traduzione delle scritte (TRADUZIONI_SCHERMATE) va nella didascalia."""
    if nome in TRADUZIONI_SCHERMATE:
        cap = cap.rstrip(".") + ". On screen: " + TRADUZIONI_SCHERMATE[nome] + "."
    raw = (HERE / "screens" / f"{nome}.ans").read_bytes().decode("utf-8", "replace")
    raw = re.sub(r"\x1b\[\?[0-9;]*[a-zA-Z]|\x1b\[[0-9]*;[0-9]*H|\x1b\[J|\r", "", raw)
    stato, out = set(), []
    for pezzo in re.split(r"(\x1b\[[0-9;]*m)", raw):
        m = re.fullmatch(r"\x1b\[([0-9;]*)m", pezzo)
        if m:
            for cod in (m.group(1) or "0").split(";"):
                if cod in ("0", ""):
                    stato = set()
                elif cod == "1":
                    stato.add("a-b")
                elif cod == "2":
                    stato.add("a-d")
                elif cod == "7":
                    stato.add("a-v")
                elif cod in ("31", "32", "33", "36", "90"):
                    stato = {x for x in stato if not x.startswith("a-3") and x != "a-90"} | {f"a-{cod}"}
            continue
        if pezzo:
            out.append(f'<span class="{" ".join(sorted(stato))}">{esc(pezzo)}</span>' if stato else esc(pezzo))
    assert nome in TRADUZIONI_SCHERMATE, f"schermata {nome}: manca la traduzione delle scritte"
    return (f'<figure class="fig"><pre class="code schermo"><code>{"".join(out)}</code></pre>'
            f'<figcaption class="cap">{cap}</figcaption></figure>')


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
    return table(["File", "Lines", "Role"], out, cap, "file-map")


# ── I risultati delle prove, letti dai file che le prove scrivono ────────
def impronta_attuale():
    import subprocess
    return subprocess.run([str(ROOT / "tools/fingerprint.sh")], capture_output=True, text=True).stdout.strip()


def risultati_prove():
    """Una riga per suite: esito, data, commit, impronta e se l'impronta è quella del codice attuale."""
    import json
    attuale = impronta_attuale()
    righe = []
    for nome, f, unita in (("tests/engine.sh", "tests/results/engine.json", "checks"),
                           ("tests/container/run.sh", "tests/container/results/results.json", "scenarios"),
                           ("tests/vm/run.sh", "tests/vm/results/results.json", "scenarios")):
        path = ROOT / f
        if not path.exists():
            righe.append([c(nome), "never run", "", "", "", ""])
            continue
        d = json.loads(path.read_text())
        m = d.get("meta", d)
        esito = f"{m['ok']} of {m['totale']} {unita} passed"
        if m.get("no"):
            esito += f", <b>{m['no']} failed</b>"
        if m.get("non_provati"):
            esito += f", {m['non_provati']} not tested"
        if m.get("solo"):
            esito += f" (only {m['solo']})"
        imp = m.get("impronta", "unknown")
        righe.append([c(nome), esito, m.get("data", ""), c(m.get("commit", "unknown")), c(imp),
                      "yes" if imp == attuale else "<b>no</b>: code changed after the run"])
    return table(["Suite", "Result", "Date", "Commit", "Fingerprint", "Valid for the current code"], righe,
                 "«TAB» — The last run of each suite (" + c("tests/*/results/") + "); fingerprint of the current "
                 "code: " + c(attuale))


# ── La guida integrata come fonte del riferimento ───────────────────────
def po_voci(path):
    """Le voci di un catalogo gettext: (contesto, testo di partenza, traduzione), nell'ordine."""
    def testo(parti):
        return re.sub(r'\\(.)', lambda m: {"n": "\n", "t": "\t"}.get(m.group(1), m.group(1)), "".join(parti))
    voci = []
    for blocco in path.read_text().split("\n\n"):
        parti, cur = {"msgctxt": [], "msgid": [], "msgstr": []}, None
        for riga in blocco.splitlines():
            m = re.match(r'^(msgctxt|msgid|msgstr) "(.*)"$', riga)
            if m:
                cur = m.group(1)
                parti[cur].append(m.group(2))
            elif riga.startswith('"') and cur:
                parti[cur].append(riga[1:-1])
        if parti["msgid"]:
            voci.append((testo(parti["msgctxt"]), testo(parti["msgid"]), testo(parti["msgstr"])))
    return voci


GUIDA_CONTESTI = {"AMS_HELP_COMMANDS": "guida-comandi", "AMS_HELP_OPTIONS": "guida-opzioni",
                  "AMS_HELP_EXAMPLES": "guida-esempi", "AMS_HELP_FILES": "guida-file"}


def help_items(name):
    """Le voci «etichetta¦descrizione» di un gruppo della guida, in inglese come i
    manuali: i testi di partenza di po/ams.pot (estratti da src/guida.c con make pot)
    con il contesto del gruppo, nell'ordine di src/guida.c. tools/check-docs.py li
    confronta con quelli estratti in quel momento dal codice."""
    ctx = GUIDA_CONTESTI[name]
    return [tuple(mid.split("¦", 1)) for c, mid, _ in po_voci(ROOT / "po/ams.pot") if c == ctx]


def help_reference(name, kind):
    items = help_items(name)
    pairs = [(esc(f), esc(d)) for f, d in items]
    attrs = [f' data-help="{html.escape(f)}" data-kind="{kind}"' for f, _ in items]
    return dl(pairs, attrs)


# ── Copertina ──────────────────────────────────────────────────────────
LOGO = """<div class="cover-logo"><svg viewBox="0 0 700 100" width="364" height="52" xmlns="http://www.w3.org/2000/svg" aria-label="AMS - Advanced Messaging System">
<text x="8" y="78" font-size="70" font-weight="800" fill="#ffffff">AMS</text>
<text x="176" y="78" font-size="38" font-weight="500" fill="#cfe0ff">Advanced Messaging System</text></svg></div>"""


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
            return f'{"Figure" if k == "FIG" else "Table"} {cur}.{counters[k]}'
        out.append(re.sub(r"«(FIG|TAB)»", num, part) if counters else part)
    return "".join(out)


def build(kind, outdir):
    meta = MANUALS[kind]
    css = (HERE / "style.css").read_text() + EXTRA_CSS
    toc, body = [], []
    for ci, (ctitle, sections) in enumerate(load_chapters(kind), 1):
        toc.append(f'<li class="toc-ch"><a href="#ch{ci}"><span class="toc-n">{ci}</span><span class="toc-t">{esc(ctitle)}</span></a></li>')
        body.append(f'<section class="chapter" id="ch{ci}"><div class="ch-head"><span class="ch-kick">Chapter {ci}</span>'
                    f'<h2 class="h-ch">{esc(ctitle)}</h2></div>')
        for si, (stitle, shtml) in enumerate(sections, 1):
            sid = f"ch{ci}s{si}"
            toc.append(f'<li class="toc-se"><a href="#{sid}"><span class="toc-n">{ci}.{si}</span><span class="toc-t">{esc(stitle)}</span></a></li>')
            body.append(f'<section class="sec" id="{sid}"><h3 class="h-sec">{ci}.{si} · {esc(stitle)}</h3>{shtml}</section>')
        body.append("</section>")
    doc = number("".join(body))
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
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
      <div><span>Version</span><b>{VERSION}</b></div>
      <div><span>Date</span><b>{DATE}</b></div>
      <div><span>Status</span><b>Confidential</b></div>
    </div>
    <div class="cover-swoosh"></div>
  </section>
  <div class="with-side">
    <aside class="side"><div class="side-inner"><h2 class="toc-head">Contents</h2><ul class="toc-list">{"".join(toc)}</ul></div></aside>
    <main class="main">{doc}</main>
  </div>
  <footer class="doc-foot">AMS — Advanced Messaging System · {meta["h1"]} v{VERSION} · {DATE} · Confidential document · Copyright (c) 2026 nic-fio</footer>
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
