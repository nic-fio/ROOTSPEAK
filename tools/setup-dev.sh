#!/bin/sh
# Prepara una copia appena clonata su una macchina Debian o Ubuntu.
#
# Un clone porta con sé sorgenti, prove, documentazione e tutta la storia, ma
# non due cose: i pacchetti che servono per compilare e provare AMS, e
# l'identità git di questo repository (sta in .git/config, che non viene
# clonato). Questo script dice cosa manca e, con --install, installa i
# pacchetti con apt. Quelli facoltativi servono solo per le prove dal vero
# e per il desktop: si installano a parte, se servono.
#
#     tools/setup-dev.sh            # dice cosa manca
#     tools/setup-dev.sh --install  # lo installa (chiede sudo)
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

# pacchetto : un comando che lo prova (- = chiedere a dpkg) : a cosa serve
PACKAGES="
gcc:gcc:il compilatore (make)
make:make:make, make prove, make test
pkg-config:pkg-config:trova la libreria di systemd
libsystemd-dev:-:journal e sessioni di logind (ams e ams-user)
gettext:msgfmt:cataloghi delle lingue (make, make pot, tools/check-docs.py)
python3:python3:manuali, controlli dei manuali, tests/tui.py e tests/help-tui.py
python3-pygments:-:evidenziazione del codice nei manuali (make docs, make docs-check)
bsdutils:script:tests/engine.sh (terminale finto per le domande di conferma)
util-linux:flock:tests/engine.sh
git:git:il repository e l'impronta del codice (tools/fingerprint.sh)
"

# facoltativi: il desktop e le prove dal vero (container, fuzzing, VM)
OPTIONAL="
zenity:zenity:la finestra di conferma sul desktop
libnotify-bin:notify-send:l'avviso di una conferma non registrata sul desktop
podman:podman:tests/container/run.sh, tests/fuzz/run.sh, tools/tui-screenshots.sh
"

NAME=${AMS_GIT_NAME:-nic-fio}
EMAIL=${AMS_GIT_EMAIL:-315794250+nic-fio@users.noreply.github.com}

has() {
    if [ "$2" = "-" ]; then
        dpkg-query -W -f='${Status}' "$1" 2>/dev/null | grep -q "ok installed"
    else
        command -v "$2" >/dev/null 2>&1
    fi
}

missing=
echo "Pacchetti:"
while IFS=: read -r pkg cmd why; do
    [ -z "$pkg" ] && continue
    if has "$pkg" "$cmd"; then ok=yes; else ok=no; missing="$missing $pkg"; fi
    printf '  [%s] %-18s %s\n' "$([ "$ok" = yes ] && echo ' ok ' || echo MANC)" "$pkg" "$why"
done <<LIST
$PACKAGES
LIST

if [ -n "$missing" ]; then
    if [ "${1:-}" = "--install" ]; then
        sudo apt-get update
        # shellcheck disable=SC2086
        sudo apt-get install -y --no-install-recommends $missing
    else
        echo
        echo "  sudo apt-get install -y --no-install-recommends$missing"
    fi
else
    echo "  non manca niente"
fi

echo
echo "Facoltativi (desktop e prove dal vero):"
optional=
while IFS=: read -r pkg cmd why; do
    [ -z "$pkg" ] && continue
    if has "$pkg" "$cmd"; then ok=yes; else ok=no; optional="$optional $pkg"; fi
    printf '  [%s] %-18s %s\n' "$([ "$ok" = yes ] && echo ' ok ' || echo MANC)" "$pkg" "$why"
done <<LIST
$OPTIONAL
LIST
[ -n "$optional" ] && echo "  (se servono: sudo apt-get install -y$optional)"
echo "  La VM con desktop gira sul server delle prove (tests/vm/run.sh): serve"
echo "  l'accesso ssh con chiave a 192.168.0.2."

echo
echo "Identità git di questa copia:"
if git -C "$ROOT" rev-parse --git-dir >/dev/null 2>&1; then
    if [ -z "$(git -C "$ROOT" config --local --get user.email || true)" ]; then
        git -C "$ROOT" config --local user.name "$NAME"
        git -C "$ROOT" config --local user.email "$EMAIL"
        echo "  impostata a $NAME <$EMAIL>"
        echo "  (tiene l'indirizzo personale fuori dalla storia;"
        echo "   AMS_GIT_NAME e AMS_GIT_EMAIL la cambiano)"
    else
        echo "  già impostata: $(git -C "$ROOT" config --local --get user.name) <$(git -C "$ROOT" config --local --get user.email)>"
    fi
else
    echo "  non è una copia git, saltata"
fi

cat <<'END'

Poi verifica che tutto funzioni davvero:

    make            # compila ams, ams-user e le lingue in build/
    make test       # prove delle parti interne, controlli dei manuali, tests/engine.sh
    python3 tests/tui.py && python3 tests/help-tui.py   # TUI e guida su un terminale virtuale
END
