#!/bin/bash
# AMS - Advanced Messaging System for linux
# Test del motore: invio, casella, conferme, in modalità di prova (senza root,
# su un archivio temporaneo). Uso: tests/engine.sh [-v]   (-v mostra gli output)
set -uo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
VERBOSE=${1:-}
BASE=$(mktemp -d)
trap 'chmod -R u+w "$BASE" 2>/dev/null; rm -rf "$BASE"' EXIT
export AMS_TEST=1 AMS_LIB=$ROOT/lib AMS_CONF=/dev/null AMS_TEST_TTY=
U=$(id -un)
fails=0 total=0

# Archivio nuovo per ogni test.
fresh() {
	export AMS_VAR=$BASE/var-$1
	rm -rf "$AMS_VAR"
	D=$AMS_VAR/users/$U
}

send() { "$ROOT/bin/ams" send --to "$U" "$@" >/dev/null; }

# Risponde «$1» alla domanda del prompt, su uno pseudo-terminale.
prompt() {
	printf '%s\n' "$1" | script -qec "$ROOT/lib/ams-user prompt" /dev/null 2>&1
}

check() { # descrizione, condizione (stringa valutata)
	total=$((total + 1))
	if eval "$2"; then
		[ -n "$VERBOSE" ] && echo "  ok   $1"
	else
		echo "  NO   $1"
		fails=$((fails + 1))
	fi
}

# ---- 1. conferme: registrate, mai perse in silenzio ----

echo "1. conferme"
fresh ack-ok
send "prova"
out=$(prompt s)
check "conferma normale: registrata" '[ -s "$D/acks/1" ] && [ ! -e "$D/inbox/1" ] && [[ $out == *"Confermato."* ]]'

fresh ack-fail
send "prova"
chmod 555 "$D/acks"
out=$(prompt s)
chmod 755 "$D/acks"
[ -n "$VERBOSE" ] && echo "$out" | tail -2 | sed 's/^/       /'
check "scrittura impossibile: il messaggio resta nella casella" '[ -e "$D/inbox/1" ] && [ ! -e "$D/read/1" ]'
check "scrittura impossibile: nessuna conferma registrata" '[ ! -e "$D/acks/1" ]'
check "scrittura impossibile: l'utente è avvisato" '[[ $out == *"Non è stato possibile registrare la conferma"* ]]'
check "scrittura impossibile: nessun file temporaneo rimasto" '[ -z "$(ls -A "$D/acks")" ]'
out=$(prompt s)
check "dopo il guasto la domanda torna e la conferma riesce" '[ -s "$D/acks/1" ] && [[ $out == *"Confermato."* ]]'

fresh ack-first
send "prova"
echo "1000 desktop" >"$D/acks/1"
(. "$ROOT/lib/ams-common.sh"; D=$D U=$U; source <(sed -n '/^mark_read()/,/^}/p;/^ack()/,/^}/p' "$ROOT/lib/ams-user"); ack 1 "terminale pts/9")
check "conferma già presente: resta la prima" '[ "$(cat "$D/acks/1")" = "1000 desktop" ] && [ ! -e "$D/inbox/1" ]'

echo
if [ $fails -eq 0 ]; then echo "OK: $total controlli"; else echo "FALLITI: $fails su $total"; fi
[ $fails -eq 0 ]
