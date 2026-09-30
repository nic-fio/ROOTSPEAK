"""Aiuti comuni ai capitoli del manuale utente (non è un capitolo: il generatore
carica solo i file chNN_*.py).

Si importa dai capitoli con:
    import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
    from _aiuti import ...
"""
from build import COL, esc, pill, schermata, text


def rif(cap, sez=None):
    """Rimando interno: «chapter 5» o «chapter 5.3», con il link."""
    if sez is None:
        return f'<a href="#ch{cap}">chapter {cap}</a>'
    return f'<a href="#ch{cap}s{sez}">chapter {cap}.{sez}</a>'


def schermata_u(nome, cap):
    """Una schermata vera presa per questo manuale (utente/schermate/NOME.ans,
    catturata in modalità di prova da utente/schermate/cattura.py)."""
    return schermata(f"../utente/schermate/{nome}", cap)


# Le pastiglie dei tre stati di un destinatario e delle due proprietà del messaggio.
INVIATO = '<span class="pill" style="background:#fee2e2;color:#991b1b">sent</span>'
CONSEGNATO = pill("delivered", "snooze")
CONFERMATO = pill("confirmed", "ok")
RITIRATO = pill("revoked", "off")
SCADUTO = pill("expired", "off")


def numero(x, y, n, color="#d97706"):
    """Un cerchietto numerato, per le figure annotate."""
    return (f'<circle cx="{x}" cy="{y}" r="11" fill="{color}"/>'
            f'<text x="{x}" y="{y + 4.5}" text-anchor="middle" font-size="12" font-weight="800" fill="#fff">{n}</text>')


def barra(x, y, conf, cons, inv, w=12, seg=14, h=14):
    """La barra a tre colori della TUI, disegnata come in una riga della lista:
    confermato █ verde, consegnato ▒ giallo, inviato ░ rosso."""
    out = []
    colori = ["#16a34a"] * conf + ["#d97706"] * cons + ["#dc2626"] * inv
    for i, c in enumerate(colori[:w]):
        op = "1" if c == "#16a34a" else "0.75" if c == "#d97706" else "0.55"
        out.append(f'<rect x="{x + i * seg}" y="{y}" width="{seg - 2}" height="{h}" rx="2" fill="{c}" fill-opacity="{op}"/>')
    return "".join(out)


def riquadro(x, y, w, h, fill="#ffffff", stroke="#cbd5e1", rx=10, dash=False):
    d = ' stroke-dasharray="5 4"' if dash else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.4"{d}/>'


def testo_sx(x, y, t, size=12, color="#334155", weight="400"):
    return text(x, y, t, size, color, weight, "start", False)


def mono(x, y, t, size=12, color="#0f172a", weight="400", anchor="start"):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" font-weight="{weight}" fill="{color}" '
            f'font-family="DejaVu Sans Mono,ui-monospace,Menlo,Consolas,monospace" xml:space="preserve" style="white-space:pre">{esc(t)}</text>')


__all__ = ["rif", "schermata_u", "INVIATO", "CONSEGNATO", "CONFERMATO", "RITIRATO", "SCADUTO", "numero", "barra",
           "riquadro", "testo_sx", "mono", "COL"]
