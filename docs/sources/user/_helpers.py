# Copyright (c) 2026 Nicola Fiorillo
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0

"""Helpers shared by the chapters of the user manual (not a chapter: the generator
loads only the chNN_*.py files).

The chapters import them with:
    import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
    from _helpers import ...
"""
import re

import build
from build import COL, esc, pill, tui_screen, text


def ref(chapter, section=None):
    """Internal reference: «chapter 5» or «chapter 5.3», with the link."""
    if section is None:
        return f'<a href="#ch{chapter}">chapter {chapter}</a>'
    return f'<a href="#ch{chapter}s{section}">chapter {chapter}.{section}</a>'


def screen(name, caption):
    """A real screenshot taken for this manual (user/screens/NAME.ans,
    captured in test mode by user/screens/capture.py)."""
    return tui_screen(f"../user/screens/{name}", caption)


def dialog(title, heading, body, caption):
    """The desktop dialog, with the buttons RootSpeak really shows."""
    return re.sub(r'<div class="dlg-k">.*?</div>',
                  '<div class="dlg-k"><span>Later</span><span>I have read it</span></div>',
                  build.dialog(title, heading, body, caption), count=1)


# The pills of the three states of a recipient and of the two properties of a message.
SENT = '<span class="pill" style="background:#fee2e2;color:#991b1b">sent</span>'
DELIVERED = pill("delivered", "snooze")
CONFIRMED = pill("confirmed", "ok")
REVOKED = pill("revoked", "off")
EXPIRED = pill("expired", "off")


def badge(x, y, n, color="#d97706"):
    """A small numbered circle, for annotated figures."""
    return (f'<circle cx="{x}" cy="{y}" r="11" fill="{color}"/>'
            f'<text x="{x}" y="{y + 4.5}" text-anchor="middle" font-size="12" font-weight="800" fill="#fff">{n}</text>')


def bar(x, y, confirmed, delivered, sent, w=12, seg=14, h=14):
    """The three-colour bar of the TUI, drawn as in a row of the list:
    confirmed █ green, delivered ▒ amber, sent ░ red."""
    out = []
    colours = ["#16a34a"] * confirmed + ["#d97706"] * delivered + ["#dc2626"] * sent
    for i, c in enumerate(colours[:w]):
        op = "1" if c == "#16a34a" else "0.75" if c == "#d97706" else "0.55"
        out.append(f'<rect x="{x + i * seg}" y="{y}" width="{seg - 2}" height="{h}" rx="2" fill="{c}" fill-opacity="{op}"/>')
    return "".join(out)


def frame(x, y, w, h, fill="#ffffff", stroke="#cbd5e1", rx=10, dash=False):
    d = ' stroke-dasharray="5 4"' if dash else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.4"{d}/>'


def text_left(x, y, t, size=12, color="#334155", weight="400"):
    return text(x, y, t, size, color, weight, "start", False)


def mono(x, y, t, size=12, color="#0f172a", weight="400", anchor="start"):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" font-weight="{weight}" fill="{color}" '
            f'font-family="DejaVu Sans Mono,ui-monospace,Menlo,Consolas,monospace" xml:space="preserve" style="white-space:pre">{esc(t)}</text>')


__all__ = ["ref", "screen", "dialog", "SENT", "DELIVERED", "CONFIRMED", "REVOKED", "EXPIRED", "badge", "bar",
           "frame", "text_left", "mono", "COL"]
