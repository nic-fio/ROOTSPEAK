#!/usr/bin/env python3
"""RootSpeak - Advanced Messaging System for Linux
Runs inside the test VM, with the identity of the desktop user and their session
bus: looks at and uses the RootSpeak dialogs through GNOME's accessibility
(AT-SPI), as a person would, on Wayland too.

    desktop.py windows            number of RootSpeak dialogs open
    desktop.py title              title of the first dialog
    desktop.py text               text of the first dialog
    desktop.py click LABEL        presses the LABEL button in the first dialog
"""
import sys

import pyatspi

# the dialogs are found by the start of their title, so that a wrong title
# is still found and reported by the scenarios
TITLE = "RootSpeak · "


def windows():
    """The RootSpeak dialogs: zenity applications with the RootSpeak title."""
    out = []
    desktop = pyatspi.Registry.getDesktop(0)
    for app in desktop:
        if app is None or (app.name or "").lower() != "zenity":
            continue
        for win in app:
            if win is not None and (win.name or "").startswith(TITLE):
                out.append(win)
    return out


def find(node, role, name=None):
    if node is None:
        return None
    if node.getRoleName() == role and (name is None or node.name == name):
        return node
    for child in node:
        found = find(child, role, name)
        if found is not None:
            return found
    return None


def texts(node, out):
    if node is None:
        return out
    if node.getRoleName() in ("label", "text", "static") and node.name:
        out.append(node.name)
    for child in node:
        texts(child, out)
    return out


if __name__ == "__main__":
    cmd = sys.argv[1]
    wins = windows()
    if cmd == "windows":
        print(len(wins))
    elif cmd == "title":
        print(wins[0].name if wins else "")
    elif cmd == "text":
        print(" | ".join(texts(wins[0], [])) if wins else "")
    elif cmd == "click":
        if not wins:
            sys.exit("no RootSpeak dialog")
        button = find(wins[0], "push button", sys.argv[2]) or find(wins[0], "button", sys.argv[2])
        if button is None:
            sys.exit(f"button «{sys.argv[2]}» not found")
        actions = button.queryAction()
        for i in range(actions.nActions):
            if actions.getName(i) in ("click", "press", "activate"):
                actions.doAction(i)
                break
        else:
            actions.doAction(0)
        print("pressed")
