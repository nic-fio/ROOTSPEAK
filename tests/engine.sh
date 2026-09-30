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

# Risponde «$1» alla domanda del prompt, su uno pseudo-terminale
# (prompt_login: come in una shell di login, dove il rinvio non vale).
prompt() {
	printf '%s\n' "$1" | script -qec "$ROOT/lib/ams-user prompt" /dev/null 2>&1
}
prompt_login() {
	printf '%s\n' "$1" | script -qec "$ROOT/lib/ams-user prompt --login" /dev/null 2>&1
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
(source <(sed -e "s|^AMS_LIB=.*|AMS_LIB=$ROOT/lib|" -e '/^case \${1:-} in/,$d' "$ROOT/lib/ams-user"); ack 1 "terminale pts/9")
check "conferma già presente: resta la prima" '[ "$(cat "$D/acks/1")" = "1000 desktop" ] && [ ! -e "$D/inbox/1" ]'

# ---- 2. consegna: tracciata per destinatario, completata dopo un'interruzione ----
# Il secondo destinatario è root: in modalità di prova la sua casella è una
# cartella qualunque dell'archivio di prova.

echo "2. consegna"
state_of() { "$ROOT/bin/ams" status "$1" 2>/dev/null | awk -v u="$2" '$1 == u { $1 = ""; sub(/^ +/, ""); print }'; }
R=$AMS_VAR/users/root

fresh send-ok
"$ROOT/bin/ams" send --to "$U,root" "prova" >/dev/null
R=$AMS_VAR/users/root
check "invio normale: due consegne registrate, nessun segno di invio incompleto" \
	'[ "$(wc -l <"$AMS_VAR/sent/1/delivery")" = 2 ] && [ ! -e "$AMS_VAR/sent/1/incomplete" ]'
check "invio normale: stato «consegnato»" '[ "$(state_of 1 root)" = "consegnato" ]'

fresh send-fail
R=$AMS_VAR/users/root
mkdir -p "$R/inbox" && chmod 555 "$R/inbox"
out=$("$ROOT/bin/ams" send --to "$U,root" "prova" 2>&1)
rc=$?
[ -n "$VERBOSE" ] && echo "$out" | sed 's/^/       /'
check "copia non scrivibile: ams send termina con errore" '[ $rc -ne 0 ] && [[ $out == *"non consegnato a: root"* ]]'
check "copia non scrivibile: l'altro destinatario la riceve" '[ -e "$D/inbox/1" ] && delivered_u=$(awk "{print \$1}" "$AMS_VAR/sent/1/delivery") && [ "$delivered_u" = "$U" ]'
check "copia non scrivibile: resta il segno di invio incompleto" '[ -e "$AMS_VAR/sent/1/incomplete" ]'
check "copia non scrivibile: stato «inviato, non consegnato»" '[[ $(state_of 1 root) == "inviato, non consegnato"* ]]'
chmod 755 "$R/inbox"
"$ROOT/bin/ams" list >/dev/null 2>&1
check "guasto risolto: il comando successivo completa la consegna" \
	'[ -e "$R/inbox/1" ] && [ ! -e "$AMS_VAR/sent/1/incomplete" ] && [ "$(state_of 1 root)" = "consegnato" ]'

fresh crash
R=$AMS_VAR/users/root
"$ROOT/bin/ams" send --to "$U,root" "prova" >/dev/null
# interruzione simulata dopo il primo destinatario
rm -f "$R/inbox/1"; sed -i '/^root /d' "$AMS_VAR/sent/1/delivery"; : >"$AMS_VAR/sent/1/incomplete"
"$ROOT/bin/ams" status 1 >/dev/null 2>&1
check "invio interrotto: il comando successivo consegna chi mancava" '[ -e "$R/inbox/1" ] && [ ! -e "$AMS_VAR/sent/1/incomplete" ]'

fresh crash-acked
"$ROOT/bin/ams" send --to "$U" "prova" >/dev/null
prompt s >/dev/null
sed -i "/^$U /d" "$AMS_VAR/sent/1/delivery"; : >"$AMS_VAR/sent/1/incomplete"
"$ROOT/bin/ams" list >/dev/null 2>&1
check "recupero: non ripropone un messaggio già confermato" '[ ! -e "$D/inbox/1" ] && [[ $(state_of 1 "$U") == confermato* ]]'

fresh unsaved
mkdir -p "$AMS_VAR/sent/7" "$AMS_VAR/users"; : >"$AMS_VAR/sent/7/incomplete"
out=$("$ROOT/bin/ams" list 2>&1)
check "invio interrotto prima del salvataggio: annullato e segnalato" \
	'[ -e "$AMS_VAR/sent/7/failed" ] && [ ! -e "$AMS_VAR/sent/7/incomplete" ] && [[ $out == *"annullato"* ]]'

fresh in-progress
R=$AMS_VAR/users/root
"$ROOT/bin/ams" send --to "$U,root" "prova" >/dev/null
rm -f "$R/inbox/1"; sed -i '/^root /d' "$AMS_VAR/sent/1/delivery"; : >"$AMS_VAR/sent/1/incomplete"
flock "$AMS_VAR/sent/1/lock" sleep 2 &
sleep 0.3
"$ROOT/bin/ams" list >/dev/null 2>&1
check "invio in corso (lock occupato): il recupero non lo tocca" '[ ! -e "$R/inbox/1" ] && [ -e "$AMS_VAR/sent/1/incomplete" ]'
wait
"$ROOT/bin/ams" list >/dev/null 2>&1
check "lock rilasciato: il recupero completa, senza doppioni" \
	'[ -e "$R/inbox/1" ] && [ "$(wc -l <"$AMS_VAR/sent/1/delivery")" = 2 ]'

fresh just-started
mkdir -p "$AMS_VAR/sent/7" "$AMS_VAR/users"; : >"$AMS_VAR/sent/7/incomplete"
flock "$AMS_VAR/sent/7/lock" sleep 1 &
sleep 0.3
"$ROOT/bin/ams" list >/dev/null 2>&1
check "invio appena iniziato (ancora senza messaggio): non viene annullato" '[ ! -e "$AMS_VAR/sent/7/failed" ]'
wait

# ---- 3. stati: inviato, consegnato, confermato; ogni messaggio chiede conferma ----

echo "3. stati"
fresh states
out=$("$ROOT/bin/ams" send --to "$U" --level info "prova" 2>&1)
check "--level non esiste più" '[[ $out == *"opzione sconosciuta: --level"* ]] && [ ! -d "$AMS_VAR/sent/1" ]'
send "prova"
check "dopo l'invio: consegnato" '[ "$(state_of 1 "$U")" = "consegnato" ]'
check "il messaggio non ha più un livello" '! grep -q "^level:" "$AMS_VAR/sent/1/msg"'
prompt n >/dev/null
check "rimandato: resta consegnato, con l'ora del rinvio" '[[ $(state_of 1 "$U") == "consegnato, rimandato il "* ]]'
prompt s >/dev/null
check "rimandato: al prompt successivo non viene richiesto subito" '[[ $(state_of 1 "$U") == "consegnato, rimandato il "* ]]'
prompt_login s >/dev/null
check "confermato (nuovo login)" '[[ $(state_of 1 "$U") == "confermato il "* ]]'
list=$("$ROOT/bin/ams" list)
check "ams list: colonne senza livello, conferme 1/1" '[[ $list == *"ID    DATA         CONFERME  TESTO"* ]] && [[ $list == *" 1/1 "* ]]'

fresh expired
send --expires 1m "prova"
sed -i "s/^expires: .*/expires: $(( $(date +%s) - 5 ))/" "$AMS_VAR/sent/1/msg"
check "scaduto: consegnato, non confermato" '[ "$(state_of 1 "$U")" = "consegnato, non confermato (scaduto)" ]'

echo
if [ $fails -eq 0 ]; then echo "OK: $total controlli"; else echo "FALLITI: $fails su $total"; fi
[ $fails -eq 0 ]
