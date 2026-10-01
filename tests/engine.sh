#!/bin/bash
# RootSpeak - Advanced Messaging System for Linux
# Test del motore: invio, casella, conferme, in modalità di prova (senza root,
# su un archivio temporaneo). Uso: tests/engine.sh [-v]   (-v mostra gli output)
# Prova i programmi compilati in build/ (make; RSPEAK_BUILD per un'altra
# cartella, per esempio build-san/ dei sanitizer).
set -uo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
VERBOSE=${1:-}
BASE=$(mktemp -d)
trap 'chmod -R u+w "$BASE" 2>/dev/null; rm -rf "$BASE"' EXIT
export RSPEAK_TEST=1 RSPEAK_CONF=/dev/null RSPEAK_TEST_TTY=
B=${RSPEAK_BUILD:-$ROOT/build}
[ -x "$B/rspeak" ] && [ -x "$B/unit-tests" ] || { echo "manca $B: lanciare make e make build/unit-tests" >&2; exit 1; }
export RSPEAK_LIB=$B RSPEAK_LOCALEDIR=$B/locale
RSPEAK=$B/rspeak RSPEAK_USER=$B/rootspeak-user
# le parti interne: la conferma da sola, la configurazione, la scelta della lingua
rspeak_ack() { "$RSPEAK_USER" conferma "$@"; }
leggi_conf() { RSPEAK_CONF=$1 "$B/unit-tests" conf; }
lingua() { "$B/unit-tests" lingua "$@"; }
# i test controllano i testi italiani; il gruppo 8 prova le altre lingue
export LANG=it_IT.UTF-8
unset LC_ALL LC_MESSAGES LANGUAGE
U=$(id -un)
fails=0 total=0

# Archivio nuovo per ogni test.
fresh() {
	export RSPEAK_VAR=$BASE/var-$1
	rm -rf "$RSPEAK_VAR"
	D=$RSPEAK_VAR/users/$U
}

send() { "$RSPEAK" send --to "$U" "$@" >/dev/null; }

# Risponde «$1» alla domanda del prompt, su uno pseudo-terminale
# (prompt_login: come in una shell di login, dove il rinvio non vale).
prompt() {
	printf '%s\n' "$1" | script -qec "$RSPEAK_USER prompt" /dev/null 2>&1
}
prompt_login() {
	printf '%s\n' "$1" | script -qec "$RSPEAK_USER prompt --login" /dev/null 2>&1
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
rspeak_ack 1 "terminale pts/9"
check "conferma già presente: resta la prima" '[ "$(cat "$D/acks/1")" = "1000 desktop" ] && [ ! -e "$D/inbox/1" ]'

fresh ack-no-move
send "prova"
echo "$(date +%s) desktop" >"$D/acks/1"
out=$(prompt s)
check "conferma registrata ma non spostata (interruzione): non viene richiesta di nuovo" \
	'[[ $out != *"Confermi"* ]] && [ -e "$D/read/1" ] && [ ! -e "$D/inbox/1" ]'

# ---- 2. consegna: tracciata per destinatario, completata dopo un'interruzione ----
# Il secondo destinatario è root: in modalità di prova la sua casella è una
# cartella qualunque dell'archivio di prova.

echo "2. consegna"
state_of() { "$RSPEAK" status "$1" 2>/dev/null | awk -v u="$2" '$1 == u { $1 = ""; sub(/^ +/, ""); print }'; }
R=$RSPEAK_VAR/users/root

fresh send-ok
"$RSPEAK" send --to "$U,root" "prova" >/dev/null
R=$RSPEAK_VAR/users/root
check "invio normale: due consegne registrate, nessun segno di invio incompleto" \
	'[ "$(wc -l <"$RSPEAK_VAR/sent/1/delivery")" = 2 ] && [ ! -e "$RSPEAK_VAR/sent/1/incomplete" ]'
check "invio normale: stato «consegnato»" '[ "$(state_of 1 root)" = "consegnato" ]'

fresh send-fail
R=$RSPEAK_VAR/users/root
mkdir -p "$R/inbox" && chmod 555 "$R/inbox"
out=$("$RSPEAK" send --to "$U,root" "prova" 2>&1)
rc=$?
[ -n "$VERBOSE" ] && echo "$out" | sed 's/^/       /'
check "copia non scrivibile: rspeak send termina con errore" '[ $rc -ne 0 ] && [[ $out == *"non consegnato a: root"* ]]'
check "copia non scrivibile: l'altro destinatario la riceve" '[ -e "$D/inbox/1" ] && delivered_u=$(awk "{print \$1}" "$RSPEAK_VAR/sent/1/delivery") && [ "$delivered_u" = "$U" ]'
check "copia non scrivibile: resta il segno di invio incompleto" '[ -e "$RSPEAK_VAR/sent/1/incomplete" ]'
check "copia non scrivibile: stato «inviato, non consegnato»" '[[ $(state_of 1 root) == "inviato, non consegnato"* ]]'
chmod 755 "$R/inbox"
"$RSPEAK" list >/dev/null 2>&1
check "guasto risolto: il comando successivo completa la consegna" \
	'[ -e "$R/inbox/1" ] && [ ! -e "$RSPEAK_VAR/sent/1/incomplete" ] && [ "$(state_of 1 root)" = "consegnato" ]'

fresh crash
R=$RSPEAK_VAR/users/root
"$RSPEAK" send --to "$U,root" "prova" >/dev/null
# interruzione simulata dopo il primo destinatario
rm -f "$R/inbox/1"; sed -i '/^root /d' "$RSPEAK_VAR/sent/1/delivery"; : >"$RSPEAK_VAR/sent/1/incomplete"
"$RSPEAK" status 1 >/dev/null 2>&1
check "invio interrotto: il comando successivo consegna chi mancava" '[ -e "$R/inbox/1" ] && [ ! -e "$RSPEAK_VAR/sent/1/incomplete" ]'

fresh crash-acked
"$RSPEAK" send --to "$U" "prova" >/dev/null
prompt s >/dev/null
sed -i "/^$U /d" "$RSPEAK_VAR/sent/1/delivery"; : >"$RSPEAK_VAR/sent/1/incomplete"
"$RSPEAK" list >/dev/null 2>&1
check "recupero: non ripropone un messaggio già confermato" '[ ! -e "$D/inbox/1" ] && [[ $(state_of 1 "$U") == confermato* ]]'

fresh unsaved
mkdir -p "$RSPEAK_VAR/sent/7" "$RSPEAK_VAR/users"; : >"$RSPEAK_VAR/sent/7/incomplete"
out=$("$RSPEAK" list 2>&1)
check "invio interrotto prima del salvataggio: annullato e segnalato" \
	'[ -e "$RSPEAK_VAR/sent/7/failed" ] && [ ! -e "$RSPEAK_VAR/sent/7/incomplete" ] && [[ $out == *"annullato"* ]]'

fresh in-progress
R=$RSPEAK_VAR/users/root
"$RSPEAK" send --to "$U,root" "prova" >/dev/null
rm -f "$R/inbox/1"; sed -i '/^root /d' "$RSPEAK_VAR/sent/1/delivery"; : >"$RSPEAK_VAR/sent/1/incomplete"
flock "$RSPEAK_VAR/sent/1/lock" sleep 2 &
sleep 0.3
"$RSPEAK" list >/dev/null 2>&1
check "invio in corso (lock occupato): il recupero non lo tocca" '[ ! -e "$R/inbox/1" ] && [ -e "$RSPEAK_VAR/sent/1/incomplete" ]'
wait
"$RSPEAK" list >/dev/null 2>&1
check "lock rilasciato: il recupero completa, senza doppioni" \
	'[ -e "$R/inbox/1" ] && [ "$(wc -l <"$RSPEAK_VAR/sent/1/delivery")" = 2 ]'

fresh just-started
mkdir -p "$RSPEAK_VAR/sent/7" "$RSPEAK_VAR/users"; : >"$RSPEAK_VAR/sent/7/incomplete"
flock "$RSPEAK_VAR/sent/7/lock" sleep 1 &
sleep 0.3
"$RSPEAK" list >/dev/null 2>&1
check "invio appena iniziato (ancora senza messaggio): non viene annullato" '[ ! -e "$RSPEAK_VAR/sent/7/failed" ]'
wait

# ---- 3. stati: inviato, consegnato, confermato; ogni messaggio chiede conferma ----

echo "3. stati"
fresh states
out=$("$RSPEAK" send --to "$U" --level info "prova" 2>&1)
check "--level non esiste più" '[[ $out == *"opzione sconosciuta: --level"* ]] && [ ! -d "$RSPEAK_VAR/sent/1" ]'
send "prova"
check "dopo l'invio: consegnato" '[ "$(state_of 1 "$U")" = "consegnato" ]'
check "il messaggio non ha più un livello" '! grep -q "^level:" "$RSPEAK_VAR/sent/1/msg"'
prompt n >/dev/null
check "rimandato: resta consegnato, con l'ora del rinvio" '[[ $(state_of 1 "$U") == "consegnato, rimandato il "* ]]'
prompt s >/dev/null
check "rimandato: al prompt successivo non viene richiesto subito" '[[ $(state_of 1 "$U") == "consegnato, rimandato il "* ]]'
prompt_login s >/dev/null
check "confermato (nuovo login)" '[[ $(state_of 1 "$U") == "confermato il "* ]]'
list=$("$RSPEAK" list)
check "rspeak list: destinatari nei tre stati, a parole" '[[ $list == *"DESTINATARI"* ]] && [[ $list == *"tutti confermato (1)"* ]]'
check "rspeak list: nessuno stato inventato" '! grep -qiE "in attesa|completo|annullato|incompleto" <<<"$list"'

fresh expired
send --expires 1m "prova"
sed -i "s/^expires: .*/expires: $(( $(date +%s) - 5 ))/" "$RSPEAK_VAR/sent/1/msg"
check "scaduto: consegnato, non confermato" '[ "$(state_of 1 "$U")" = "consegnato, non confermato (scaduto)" ]'

# ---- 4. scadenza: domande e finestre si chiudono, una conferma tardiva non vale ----

echo "4. scadenza"
fresh expire-during
send --expires 1m "scade durante la domanda"
exp=$(( $(date +%s) + 2 ))
sed -i "s/^expires: .*/expires: $exp/" "$RSPEAK_VAR/sent/1/msg" "$D/inbox/1"
out=$( (sleep 4; echo s) | script -qec "$RSPEAK_USER prompt" /dev/null 2>&1)
check "scadenza durante la domanda: la domanda si ferma" '[[ $out == *"Il messaggio è scaduto."* ]]'
check "scadenza durante la domanda: nessuna conferma registrata" '[ ! -e "$D/acks/1" ] && [ -e "$D/read/1" ]'
check "scadenza durante la domanda: stato «non confermato (scaduto)»" '[ "$(state_of 1 "$U")" = "consegnato, non confermato (scaduto)" ]'

fresh late-ack
send --expires 1m "conferma fuori tempo"
exp=$(( $(date +%s) - 10 ))
sed -i "s/^expires: .*/expires: $exp/" "$RSPEAK_VAR/sent/1/msg"
echo "$(date +%s) desktop" >"$D/acks/1"
check "conferma con ora dopo la scadenza (copia di riferimento): non vale" \
	'[ "$(state_of 1 "$U")" = "consegnato, non confermato (scaduto; conferma arrivata dopo la scadenza)" ]'
check "rspeak list non la conta" '[[ $("$RSPEAK" list) == *"[scaduto]"*"1 consegnato"* ]]'

# ---- 5. configurazione e formato ----

echo "5. configurazione"
conf=$BASE/rootspeak.conf
leggi() { leggi_conf "$conf"; }
printf 'RSPEAK_REMIND_MINUTES=$(touch %s/eseguito)\nRSPEAK_AGENT_POLL=`touch %s/eseguito`\n' "$BASE" "$BASE" >"$conf"
check "la configurazione non viene eseguita come codice" '[ "$(leggi)" = "30 60" ] && [ ! -e "$BASE/eseguito" ]'
printf '# commento\n RSPEAK_REMIND_MINUTES = 15  # a destra\nRSPEAK_AGENT_POLL=abc\nRSPEAK_DEFAULT_LEVEL=info\nALTRO=5\n' >"$conf"
check "valori validi letti, non validi e sconosciuti ignorati" '[ "$(leggi)" = "15 60" ]'
printf 'RSPEAK_REMIND_MINUTES=0\nRSPEAK_AGENT_POLL=-3\n' >"$conf"
check "zero e negativi ignorati" '[ "$(leggi)" = "30 60" ]'
fresh format
send "prova"
check "il messaggio dichiara la versione del formato" '[ "$(head -1 "$RSPEAK_VAR/sent/1/msg")" = "format: 1" ]'

# ---- 6. pulizia ----

echo "6. pulizia"
fresh purge
send "vecchio"; send "recente"
sed -i "s/^date: .*/date: $(( $(date +%s) - 10 * 86400 ))/" "$RSPEAK_VAR/sent/1/msg"
prompt_login s >/dev/null
out=$("$RSPEAK" purge 7d)
check "rspeak purge 7d: cancella il messaggio di 10 giorni fa" '[[ $out == "Cancellato 1 messaggio"* ]] && [ ! -d "$RSPEAK_VAR/sent/1" ]'
check "rspeak purge: copie e conferme nella casella tolte" \
	'[ ! -e "$D/inbox/1" ] && [ ! -e "$D/read/1" ] && [ ! -e "$D/acks/1" ]'
check "rspeak purge: il messaggio recente resta" '[ -d "$RSPEAK_VAR/sent/2" ] && [ -e "$D/inbox/2" -o -e "$D/read/2" ]'
: >"$RSPEAK_VAR/sent/2/incomplete"
sed -i "s/^date: .*/date: $(( $(date +%s) - 10 * 86400 ))/" "$RSPEAK_VAR/sent/2/msg"
flock "$RSPEAK_VAR/sent/2/lock" sleep 1 &
sleep 0.2
"$RSPEAK" purge 7d >/dev/null 2>&1
check "rspeak purge: un invio incompleto o in corso non viene toccato" '[ -d "$RSPEAK_VAR/sent/2" ]'
wait
out=$("$RSPEAK" purge 7x 2>&1)
check "rspeak purge: durata non valida rifiutata" '[[ $out == *"durata non valida"* ]]'

# ---- 7. agente del desktop: sveglia solo quando è pronto ----
# Richiede una sessione grafica dell'utente che esegue i test (l'agente esce
# subito senza); altrimenti il gruppo è saltato.

echo "7. agente"
if [ -n "$(loginctl show-user "$U" -p Display --value 2>/dev/null)" ]; then
	fresh agent
	mkdir -p "$RSPEAK_VAR/users" "$BASE/run-agent"
	vivi=0 pronti=0
	for i in 1 2 3 4 5 6 7 8 9 10; do
		rm -f "$BASE/run-agent/rootspeak-agent.pronto"
		XDG_RUNTIME_DIR=$BASE/run-agent "$RSPEAK_USER" agent &
		p=$!
		for k in $(seq 1 200); do [ -s "$BASE/run-agent/rootspeak-agent.pronto" ] && break; sleep 0.01; done
		[ "$(cat "$BASE/run-agent/rootspeak-agent.pronto" 2>/dev/null)" = "$p" ] && pronti=$((pronti + 1))
		for k in 1 2 3 4 5; do pkill -USR1 -F "$BASE/run-agent/rootspeak-agent.pronto" -f 'rootspeak-user agent$' 2>/dev/null; done
		sleep 0.2
		kill -0 $p 2>/dev/null && vivi=$((vivi + 1))
		kill $p 2>/dev/null; wait $p 2>/dev/null
	done
	check "l'agente scrive il suo PID in rootspeak-agent.pronto quando è pronto (10 su 10)" '[ $pronti = 10 ]'
	check "la sveglia al PID pronto non lo uccide (10 su 10)" '[ $vivi = 10 ]'
	check "all'uscita rootspeak-agent.pronto sparisce" '[ ! -e "$BASE/run-agent/rootspeak-agent.pronto" ]'
else
	echo "  --   saltato: nessuna sessione grafica"
fi

# ---- 8. lingua: ognuno legge RootSpeak nella sua ----

echo "8. lingua"
# lingua LANGUAGE LC_ALL LC_MESSAGES LANG → lingua scelta (definita in alto)
check "LANG=it_IT.UTF-8: italiano" '[ "$(lingua "" "" "" it_IT.UTF-8)" = it ]'
check "LANG=en_GB.UTF-8: inglese" '[ "$(lingua "" "" "" en_GB.UTF-8)" = en ]'
check "lingua senza traduzione (de_DE): inglese" '[ "$(lingua "" "" "" de_DE.UTF-8)" = en ]'
check "LANG=C o assente: inglese" '[ "$(lingua "" "" "" C.UTF-8)" = en ] && [ "$(lingua "" "" "" "")" = en ]'
check "LC_ALL=C vince su LANG=it: inglese" '[ "$(lingua "" C "" it_IT.UTF-8)" = en ]'
check "LC_MESSAGES=it vince su LANG=en: italiano" '[ "$(lingua "" "" it_IT.UTF-8 en_US.UTF-8)" = it ]'
check "LANGUAGE=de:it con LANG=en: italiano (primo noto dell'elenco)" '[ "$(lingua de:it "" "" en_US.UTF-8)" = it ]'
check "LANGUAGE ignorata con LANG=C: inglese" '[ "$(lingua it "" "" C)" = en ]'
check "valori strani (../, /): inglese, nessun file letto" '[ "$(lingua "../../tmp/x" "" "" "a/b")" = en ]'

fresh lingua
send "Testo non tradotto"
out=$(printf 'y\n' | LANG=en_US.UTF-8 script -qec "$RSPEAK_USER prompt" /dev/null 2>&1)
check "utente in inglese: intestazione, domanda e conferma in inglese, testo intatto" \
	'[[ $out == *"Message from the administrator"* && $out == *"Do you confirm"* && $out == *"Confirmed."* && $out == *"Testo non tradotto"* ]] && [ -s "$D/acks/1" ]'
send "Secondo"
out=$(LANG=en_US.UTF-8 "$RSPEAK" status 2)
check "amministratore in inglese: rspeak status" '[[ $out == *"USER"*"STATE"* && $out == *"delivered"* ]]'
out=$(LANG=en_US.UTF-8 "$RSPEAK" status 1)
check "conferma data da terminale, letta in inglese: canale tradotto" '[[ $out == *"confirmed on"*"(terminal "* ]]'
out=$("$RSPEAK" status 1)
check "la stessa conferma letta in italiano" '[[ $out == *"confermato il"*"(terminale "* ]]'
out=$(LANG=en_US.UTF-8 "$RSPEAK" send "x" 2>&1)
check "errore in inglese" '[[ $out == "rspeak: missing --to" ]]'
out=$(LANG=en_US.UTF-8 "$RSPEAK" --help </dev/null | cat)
check "guida in inglese" '[[ $out == *"SYNOPSIS"* && $out == *"SEND OPTIONS"* ]]'
out=$("$RSPEAK" --help </dev/null | cat)
check "guida in italiano" '[[ $out == *"SINTASSI"* && $out == *"OPZIONI DI SEND"* ]]'

# ---- 9. seconda revisione: ritiro, terminali, interruzioni, caselle anomale ----

echo "9. seconda revisione"
S=$RSPEAK_VAR
fresh rit-attesa
send "lungo invio"
( flock "$RSPEAK_VAR/sent/1/lock" sleep 2 ) &
sleep 0.3
t0=$(date +%s%N)
"$RSPEAK" revoke 1 >/dev/null
dt=$((($(date +%s%N) - t0) / 1000000))
wait
check "rspeak revoke aspetta un invio in corso (lock), poi toglie la copia" '[ $dt -ge 1200 ] && [ ! -e "$D/inbox/1" ] && [ ! -e "$RSPEAK_VAR/sent/1/ritiro" ]'

fresh rit-conferma
send "ritirato"
"$RSPEAK" revoke 1 >/dev/null
rev=$(cat "$RSPEAK_VAR/sent/1/revoked")
echo "$((rev + 5)) terminale pts/9" >"$D/acks/1"
check "conferma con ora successiva al ritiro: non vale" '[[ "$(state_of 1 "$U")" == "consegnato, non confermato (ritirato)" ]]'
echo "$rev terminale pts/9" >"$D/acks/1"
check "conferma dello stesso secondo del ritiro: vale" '[[ "$(state_of 1 "$U")" == confermato* ]]'

fresh rit-ack
send "ritirato prima della risposta"
cp "$D/inbox/1" "$BASE/copia"
out=$(printf 's\n' | script -qec "bash -c '$RSPEAK_USER prompt & sleep 0.5; rm -f $D/inbox/1; wait'" /dev/null 2>&1)
check "copia tolta mentre l'utente risponde: nessuna conferma scritta" '[ ! -e "$D/acks/1" ]'

fresh term-altro
RSPEAK_TEST_TTY=/dev/null "$RSPEAK" send --to "$U" "terminale d'altri" >/dev/null
check "terminale di un altro utente (qui /dev/null, di root): non si scrive" '[ "$(state_of 1 "$U")" = consegnato ]'
: >"$BASE/tty-mio"
RSPEAK_TEST_TTY=$BASE/tty-mio "$RSPEAK" send --to "$U" "terminale mio" >/dev/null
check "terminale dell'utente: si scrive" 'grep -q "terminale mio" "$BASE/tty-mio"'

fresh corrente
send "persa dopo un'interruzione di corrente"
rm -f "$D/inbox/1"
: >"$RSPEAK_VAR/sent/1/incomplete"
"$RSPEAK" list >/dev/null 2>&1
check "copia annotata ma sparita (invio incompleto): il recupero la riscrive" '[ -s "$D/inbox/1" ] && [ ! -e "$RSPEAK_VAR/sent/1/incomplete" ] && [ "$(wc -l <"$RSPEAK_VAR/sent/1/delivery")" = 1 ]'

fresh rit-meta
send "ritiro interrotto"
date +%s >"$RSPEAK_VAR/sent/1/revoked"
: >"$RSPEAK_VAR/sent/1/ritiro"
"$RSPEAK" list >/dev/null 2>&1
check "ritiro interrotto: il comando successivo toglie la copia" '[ ! -e "$D/inbox/1" ] && [ ! -e "$RSPEAK_VAR/sent/1/ritiro" ]'

fresh canc-meta
send "cancellazione interrotta"
mv "$RSPEAK_VAR/sent/1" "$RSPEAK_VAR/sent/.cancella-1"
out=$("$RSPEAK" list 2>&1)
check "cancellazione interrotta: rspeak list non la mostra e il recupero la completa" \
	'[[ $out != *"cancellazione interrotta"* ]] && [ ! -e "$RSPEAK_VAR/sent/.cancella-1" ] && [ ! -e "$D/inbox/1" ]'

fresh molti-acks
send "uno"
(cd "$D/acks" && seq 1000 6000 | xargs touch)
t0=$(date +%s%N)
"$RSPEAK" list >/dev/null
dt=$((($(date +%s%N) - t0) / 1000000))
[ -n "$VERBOSE" ] && echo "       rspeak list con 5000 file finti in acks/: $dt ms"
check "5000 file finti in acks/: rspeak list non rallenta (meno di 1 s)" '[ $dt -lt 1000 ]'

fresh fifo
send "uno"
mkfifo "$D/acks/1"
check "acks/ID è una pipe: rspeak status non si blocca" 'timeout 5 "$RSPEAK" status 1 >/dev/null'

fresh lungo
out=$(head -c 70000 /dev/zero | tr '\0' a | "$RSPEAK" send --to "$U" 2>&1)
check "testo oltre 65536 byte: rifiutato con un errore chiaro" '[[ $out == *"messaggio troppo lungo: 70000 byte"* ]] && [ ! -e "$RSPEAK_VAR/sent/1" ]'
out=$(head -c 65536 /dev/zero | tr '\0' a | "$RSPEAK" send --to "$U" 2>&1)
check "testo di 65536 byte: accettato" '[ -e "$RSPEAK_VAR/sent/1/msg" ]'

printf 'RSPEAK_REMIND_MINUTES=45 # minuti di rinvio\n  RSPEAK_AGENT_POLL = 20  \n' >"$BASE/conf"
out=$(leggi_conf "$BASE/conf")
check "rootspeak.conf: commento a fine riga e spazi" '[ "$out" = "45 20" ]'

# ---- 10. sollecito ----

echo "10. sollecito"
fresh sollecito
send "da confermare"
prompt n >/dev/null
out=$(prompt s)
check "rimandato: al prompt la domanda non torna subito" '[[ $out != *"Confermi"* ]]'
out=$("$RSPEAK" remind 1)
check "rspeak remind: sollecita chi non ha confermato" '[[ $out == "Messaggio 1: sollecitato 1 destinatario." ]] && [ ! -e "$D/state/1.term" ]'
out=$(prompt s)
check "dopo il sollecito la domanda torna al prompt successivo" '[[ $out == *"Confermi"* ]] && [[ "$(state_of 1 "$U")" == confermato* ]]'
out=$("$RSPEAK" remind 1)
check "rspeak remind: chi ha confermato non viene sollecitato" '[[ $out == "Messaggio 1: sollecitati 0 destinatari." ]]'
send "da ritirare"
"$RSPEAK" revoke 2 >/dev/null
out=$("$RSPEAK" remind 2 2>&1)
check "rspeak remind di un messaggio ritirato: errore" '[[ $out == *"è stato ritirato: nessuno da sollecitare"* ]]'

echo
if [ $fails -eq 0 ]; then echo "OK: $total controlli"; else echo "FALLITI: $fails su $total"; fi
# risultato, con commit e impronta del codice provato (letti dal manuale tecnico, capitolo 11)
mkdir -p "$ROOT/tests/results"
printf '{"data": "%s", "commit": "%s", "impronta": "%s", "ok": %d, "no": %d, "totale": %d}\n' \
	"$(date '+%Y-%m-%d %H:%M:%S %Z')" "$("$ROOT/tools/fingerprint.sh" --commit)" "$("$ROOT/tools/fingerprint.sh")" \
	$((total - fails)) "$fails" "$total" >"$ROOT/tests/results/engine.json"
[ $fails -eq 0 ]
