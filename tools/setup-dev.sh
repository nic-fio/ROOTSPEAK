#!/bin/sh
# Copyright (c) 2026 Nicola Fiorillo
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Prepares a freshly cloned copy on a Debian or Ubuntu machine.
#
# A clone brings sources, tests, documentation and the whole history, but not
# two things: the packages needed to build and test RootSpeak, and the git
# identity of this repository (it lives in .git/config, which is not cloned).
# This script says what is missing and, with --install, installs the packages
# with apt. The optional ones are needed only for the real-world tests and for
# the desktop: they are installed separately, if needed.
#
#     tools/setup-dev.sh            # says what is missing
#     tools/setup-dev.sh --install  # installs it (asks for sudo)
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

# package : a command that shows it is there (- = ask dpkg) : what it is for
PACKAGES="
gcc:gcc:the compiler (make)
make:make:make, make unit, make test
pkg-config:pkg-config:finds the systemd library
libsystemd-dev:-:journal and logind sessions (rspeak and rootspeak-user)
python3:python3:manuals, manual checks, tests/tui.py and tests/help-tui.py
python3-pygments:-:code highlighting in the manuals (make docs, make docs-check)
bsdutils:script:tests/engine.sh (fake terminal for the confirmation questions)
util-linux:flock:tests/engine.sh
git:git:the repository and the code fingerprint (tools/fingerprint.sh)
"

# optional: the desktop and the real-world tests (container, fuzzing, VM)
OPTIONAL="
zenity:zenity:the confirmation dialog on the desktop
libnotify-bin:notify-send:the notice of a confirmation not recorded on the desktop
podman:podman:tests/container/run.sh, tests/fuzz/run.sh, tools/tui-screenshots.sh
"

NAME=${RSPEAK_GIT_NAME:-nic-fio}
EMAIL=${RSPEAK_GIT_EMAIL:-315794250+nic-fio@users.noreply.github.com}

has() {
    if [ "$2" = "-" ]; then
        dpkg-query -W -f='${Status}' "$1" 2>/dev/null | grep -q "ok installed"
    else
        command -v "$2" >/dev/null 2>&1
    fi
}

missing=
echo "Packages:"
while IFS=: read -r pkg cmd why; do
    [ -z "$pkg" ] && continue
    if has "$pkg" "$cmd"; then ok=yes; else ok=no; missing="$missing $pkg"; fi
    printf '  [%s] %-18s %s\n' "$([ "$ok" = yes ] && echo ' ok ' || echo MISS)" "$pkg" "$why"
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
    echo "  nothing is missing"
fi

echo
echo "Optional (desktop and real-world tests):"
optional=
while IFS=: read -r pkg cmd why; do
    [ -z "$pkg" ] && continue
    if has "$pkg" "$cmd"; then ok=yes; else ok=no; optional="$optional $pkg"; fi
    printf '  [%s] %-18s %s\n' "$([ "$ok" = yes ] && echo ' ok ' || echo MISS)" "$pkg" "$why"
done <<LIST
$OPTIONAL
LIST
[ -n "$optional" ] && echo "  (if needed: sudo apt-get install -y$optional)"
echo "  The VM with a desktop runs on the test server (tests/vm/run.sh): it needs"
echo "  ssh access with a key to 192.168.0.2."

echo
echo "Git identity of this copy:"
if git -C "$ROOT" rev-parse --git-dir >/dev/null 2>&1; then
    if [ -z "$(git -C "$ROOT" config --local --get user.email || true)" ]; then
        git -C "$ROOT" config --local user.name "$NAME"
        git -C "$ROOT" config --local user.email "$EMAIL"
        echo "  set to $NAME <$EMAIL>"
        echo "  (it keeps the personal address out of the history;"
        echo "   RSPEAK_GIT_NAME and RSPEAK_GIT_EMAIL change it)"
    else
        echo "  already set: $(git -C "$ROOT" config --local --get user.name) <$(git -C "$ROOT" config --local --get user.email)>"
    fi
    git -C "$ROOT" config --local core.hooksPath .githooks
    echo "  pre-commit hook enabled: checks the manuals before every commit"
else
    echo "  not a git copy, skipped"
fi

cat <<'END'

Then check that everything really works:

    make            # builds rspeak and rootspeak-user in build/
    make test       # unit tests, manual checks, tests/engine.sh
    python3 tests/tui.py && python3 tests/help-tui.py   # TUI and help on a virtual terminal
END
