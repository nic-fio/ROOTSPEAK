#!/usr/bin/env python3
"""AMS - Advanced Messaging System for linux
Gira dentro la VM di prova, con l'identità dell'utente del desktop e il suo bus
di sessione: guarda e usa le finestre di AMS attraverso l'accessibilità di GNOME
(AT-SPI), come farebbe una persona, anche su Wayland.

    desktop.py finestre             numero di finestre di AMS aperte
    desktop.py titolo               titolo della prima finestra
    desktop.py testo                testo della prima finestra
    desktop.py clicca ETICHETTA     preme il pulsante ETICHETTA nella prima finestra
"""
import sys

import pyatspi

# il titolo cambia con la lingua della sessione, ma comincia sempre così
TITOLO = "AMS · "


def finestre():
    """Le finestre di dialogo di AMS: applicazioni zenity con il titolo di AMS (in ogni lingua)."""
    out = []
    desktop = pyatspi.Registry.getDesktop(0)
    for app in desktop:
        if app is None or (app.name or "").lower() != "zenity":
            continue
        for win in app:
            if win is not None and (win.name or "").startswith(TITOLO):
                out.append(win)
    return out


def cerca(nodo, ruolo, nome=None):
    if nodo is None:
        return None
    if nodo.getRoleName() == ruolo and (nome is None or nodo.name == nome):
        return nodo
    for figlio in nodo:
        trovato = cerca(figlio, ruolo, nome)
        if trovato is not None:
            return trovato
    return None


def testi(nodo, out):
    if nodo is None:
        return out
    if nodo.getRoleName() in ("label", "text", "static") and nodo.name:
        out.append(nodo.name)
    for figlio in nodo:
        testi(figlio, out)
    return out


if __name__ == "__main__":
    cmd = sys.argv[1]
    wins = finestre()
    if cmd == "finestre":
        print(len(wins))
    elif cmd == "titolo":
        print(wins[0].name if wins else "")
    elif cmd == "testo":
        print(" | ".join(testi(wins[0], [])) if wins else "")
    elif cmd == "clicca":
        if not wins:
            sys.exit("nessuna finestra di AMS")
        bottone = cerca(wins[0], "push button", sys.argv[2]) or cerca(wins[0], "button", sys.argv[2])
        if bottone is None:
            sys.exit(f"pulsante «{sys.argv[2]}» non trovato")
        azioni = bottone.queryAction()
        for i in range(azioni.nActions):
            if azioni.getName(i) in ("click", "press", "activate"):
                azioni.doAction(i)
                break
        else:
            azioni.doAction(0)
        print("premuto")
