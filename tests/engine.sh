#!/bin/bash
# Copyright (c) 2026 Nicola Fiorillo
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# RootSpeak - Advanced Messaging System for Linux
# Engine tests: sending, mailbox, confirmations, in test mode (no root, on a
# temporary message store). Usage: tests/engine.sh [-v]   (-v shows the output)
# Tests the programs built in build/ (make; RSPEAK_BUILD for another folder,
# for example build-san/ of the sanitizers).
set -uo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
VERBOSE=${1:-}
BASE=$(mktemp -d)
trap 'chmod -R u+w "$BASE" 2>/dev/null; rm -rf "$BASE"' EXIT
export RSPEAK_TEST=1 RSPEAK_CONF=/dev/null RSPEAK_TEST_TTY=
B=${RSPEAK_BUILD:-$ROOT/build}
[ -x "$B/rspeak" ] && [ -x "$B/unit-tests" ] || { echo "$B is missing: run make and make build/unit-tests" >&2; exit 1; }
export RSPEAK_LIB=$B
RSPEAK=$B/rspeak RSPEAK_USER=$B/rootspeak-user
# the internals: the confirmation on its own, the configuration
rspeak_ack() { "$RSPEAK_USER" confirm "$@"; }
read_conf() { RSPEAK_CONF=$1 "$B/unit-tests" conf; }
# RootSpeak speaks English whatever the language of the session
export LANG=it_IT.UTF-8
unset LC_ALL LC_MESSAGES LANGUAGE
U=$(id -un)
fails=0 total=0

# A new message store for each test.
fresh() {
	export RSPEAK_VAR=$BASE/var-$1
	rm -rf "$RSPEAK_VAR"
	D=$RSPEAK_VAR/users/$U
}

send() { "$RSPEAK" send --to "$U" "$@" >/dev/null; }

# Answers «$1» to the question at the prompt, on a pseudo-terminal
# (prompt_login: as in a login shell, where the postponement does not count).
prompt() {
	printf '%s\n' "$1" | script -qec "$RSPEAK_USER prompt" /dev/null 2>&1
}
prompt_login() {
	printf '%s\n' "$1" | script -qec "$RSPEAK_USER prompt --login" /dev/null 2>&1
}

check() { # description, condition (evaluated string)
	total=$((total + 1))
	if eval "$2"; then
		[ -n "$VERBOSE" ] && echo "  ok   $1"
	else
		echo "  NO   $1"
		fails=$((fails + 1))
	fi
}

# ---- 1. confirmations: recorded, never lost silently ----

echo "1. confirmations"
fresh ack-ok
send "test"
out=$(prompt y)
check "normal confirmation: recorded" '[ -s "$D/acks/1" ] && [ ! -e "$D/inbox/1" ] && [[ $out == *"Confirmed."* ]]'

fresh ack-fail
send "test"
chmod 555 "$D/acks"
out=$(prompt y)
chmod 755 "$D/acks"
[ -n "$VERBOSE" ] && echo "$out" | tail -2 | sed 's/^/       /'
check "cannot write: the message stays in the mailbox" '[ -e "$D/inbox/1" ] && [ ! -e "$D/read/1" ]'
check "cannot write: no confirmation recorded" '[ ! -e "$D/acks/1" ]'
check "cannot write: the user is told" '[[ $out == *"The confirmation could not be recorded"* ]]'
check "cannot write: no temporary file left" '[ -z "$(ls -A "$D/acks")" ]'
out=$(prompt y)
check "after the fault the question comes back and the confirmation succeeds" '[ -s "$D/acks/1" ] && [[ $out == *"Confirmed."* ]]'

fresh ack-first
send "test"
echo "1000 desktop" >"$D/acks/1"
rspeak_ack 1 "terminal pts/9"
check "confirmation already there: the first one stays" '[ "$(cat "$D/acks/1")" = "1000 desktop" ] && [ ! -e "$D/inbox/1" ]'

fresh ack-no-move
send "test"
echo "$(date +%s) desktop" >"$D/acks/1"
out=$(prompt y)
check "confirmation recorded but not moved (interruption): not asked again" \
	'[[ $out != *"Do you confirm"* ]] && [ -e "$D/read/1" ] && [ ! -e "$D/inbox/1" ]'

# ---- 2. delivery: tracked per recipient, completed after an interruption ----
# The second recipient is root: in test mode its mailbox is just a folder of
# the test message store.

echo "2. delivery"
state_of() { "$RSPEAK" status "$1" 2>/dev/null | awk -v u="$2" '$1 == u { $1 = ""; sub(/^ +/, ""); print }'; }
R=$RSPEAK_VAR/users/root

fresh send-ok
"$RSPEAK" send --to "$U,root" "test" >/dev/null
R=$RSPEAK_VAR/users/root
check "normal send: two deliveries recorded, no incomplete-send mark" \
	'[ "$(wc -l <"$RSPEAK_VAR/sent/1/delivery")" = 2 ] && [ ! -e "$RSPEAK_VAR/sent/1/incomplete" ]'
check "normal send: state «delivered»" '[ "$(state_of 1 root)" = "delivered" ]'

fresh send-fail
R=$RSPEAK_VAR/users/root
mkdir -p "$R/inbox" && chmod 555 "$R/inbox"
out=$("$RSPEAK" send --to "$U,root" "test" 2>&1)
rc=$?
[ -n "$VERBOSE" ] && echo "$out" | sed 's/^/       /'
check "copy cannot be written: rspeak send ends with an error" '[ $rc -ne 0 ] && [[ $out == *"not delivered to: root"* ]]'
check "copy cannot be written: the other recipient gets it" '[ -e "$D/inbox/1" ] && delivered_u=$(awk "{print \$1}" "$RSPEAK_VAR/sent/1/delivery") && [ "$delivered_u" = "$U" ]'
check "copy cannot be written: the incomplete-send mark stays" '[ -e "$RSPEAK_VAR/sent/1/incomplete" ]'
check "copy cannot be written: state «sent, not delivered»" '[[ $(state_of 1 root) == "sent, not delivered"* ]]'
chmod 755 "$R/inbox"
"$RSPEAK" list >/dev/null 2>&1
check "fault fixed: the next command completes the delivery" \
	'[ -e "$R/inbox/1" ] && [ ! -e "$RSPEAK_VAR/sent/1/incomplete" ] && [ "$(state_of 1 root)" = "delivered" ]'

fresh crash
R=$RSPEAK_VAR/users/root
"$RSPEAK" send --to "$U,root" "test" >/dev/null
# interruption simulated after the first recipient
rm -f "$R/inbox/1"; sed -i '/^root /d' "$RSPEAK_VAR/sent/1/delivery"; : >"$RSPEAK_VAR/sent/1/incomplete"
"$RSPEAK" status 1 >/dev/null 2>&1
check "interrupted send: the next command delivers to whoever was missing" '[ -e "$R/inbox/1" ] && [ ! -e "$RSPEAK_VAR/sent/1/incomplete" ]'

fresh crash-acked
"$RSPEAK" send --to "$U" "test" >/dev/null
prompt y >/dev/null
sed -i "/^$U /d" "$RSPEAK_VAR/sent/1/delivery"; : >"$RSPEAK_VAR/sent/1/incomplete"
"$RSPEAK" list >/dev/null 2>&1
check "recovery: does not show again a message already confirmed" '[ ! -e "$D/inbox/1" ] && [[ $(state_of 1 "$U") == confirmed* ]]'

fresh unsaved
mkdir -p "$RSPEAK_VAR/sent/7" "$RSPEAK_VAR/users"; : >"$RSPEAK_VAR/sent/7/incomplete"
out=$("$RSPEAK" list 2>&1)
check "send interrupted before saving: cancelled and reported" \
	'[ -e "$RSPEAK_VAR/sent/7/failed" ] && [ ! -e "$RSPEAK_VAR/sent/7/incomplete" ] && [[ $out == *"cancelled"* ]]'

fresh in-progress
R=$RSPEAK_VAR/users/root
"$RSPEAK" send --to "$U,root" "test" >/dev/null
rm -f "$R/inbox/1"; sed -i '/^root /d' "$RSPEAK_VAR/sent/1/delivery"; : >"$RSPEAK_VAR/sent/1/incomplete"
flock "$RSPEAK_VAR/sent/1/lock" sleep 2 &
sleep 0.3
"$RSPEAK" list >/dev/null 2>&1
check "send in progress (lock held): recovery leaves it alone" '[ ! -e "$R/inbox/1" ] && [ -e "$RSPEAK_VAR/sent/1/incomplete" ]'
wait
"$RSPEAK" list >/dev/null 2>&1
check "lock released: recovery completes, without duplicates" \
	'[ -e "$R/inbox/1" ] && [ "$(wc -l <"$RSPEAK_VAR/sent/1/delivery")" = 2 ]'

fresh just-started
mkdir -p "$RSPEAK_VAR/sent/7" "$RSPEAK_VAR/users"; : >"$RSPEAK_VAR/sent/7/incomplete"
flock "$RSPEAK_VAR/sent/7/lock" sleep 1 &
sleep 0.3
"$RSPEAK" list >/dev/null 2>&1
check "send just started (no message yet): not cancelled" '[ ! -e "$RSPEAK_VAR/sent/7/failed" ]'
wait

# ---- 3. states: sent, delivered, confirmed; every message asks for confirmation ----

echo "3. states"
fresh states
out=$("$RSPEAK" send --to "$U" --level info "test" 2>&1)
check "--level no longer exists" '[[ $out == *"unknown option: --level"* ]] && [ ! -d "$RSPEAK_VAR/sent/1" ]'
send "test"
check "after sending: delivered" '[ "$(state_of 1 "$U")" = "delivered" ]'
check "the message no longer has a level" '! grep -q "^level:" "$RSPEAK_VAR/sent/1/msg"'
prompt n >/dev/null
check "postponed: stays delivered, with the time of the postponement" '[[ $(state_of 1 "$U") == "delivered, postponed on "* ]]'
prompt y >/dev/null
check "postponed: not asked again at the next prompt" '[[ $(state_of 1 "$U") == "delivered, postponed on "* ]]'
prompt_login y >/dev/null
check "confirmed (new login)" '[[ $(state_of 1 "$U") == "confirmed on "* ]]'
list=$("$RSPEAK" list)
check "rspeak list: recipients in the three states, in words" '[[ $list == *"RECIPIENTS"* ]] && [[ $list == *"all confirmed (1)"* ]]'
check "rspeak list: no invented state" '! grep -qiE "pending|complete|cancelled|waiting" <<<"$list"'

fresh expired
send --expires 1m "test"
sed -i "s/^expires: .*/expires: $(( $(date +%s) - 5 ))/" "$RSPEAK_VAR/sent/1/msg"
check "expired: delivered, not confirmed" '[ "$(state_of 1 "$U")" = "delivered, not confirmed (expired)" ]'

# ---- 4. expiry: questions and dialogs close, a late confirmation does not count ----

echo "4. expiry"
fresh expire-during
send --expires 1m "expires during the question"
exp=$(( $(date +%s) + 2 ))
sed -i "s/^expires: .*/expires: $exp/" "$RSPEAK_VAR/sent/1/msg" "$D/inbox/1"
out=$( (sleep 4; echo y) | script -qec "$RSPEAK_USER prompt" /dev/null 2>&1)
check "expiry during the question: the question stops" '[[ $out == *"The message has expired."* ]]'
check "expiry during the question: no confirmation recorded" '[ ! -e "$D/acks/1" ] && [ -e "$D/read/1" ]'
check "expiry during the question: state «not confirmed (expired)»" '[ "$(state_of 1 "$U")" = "delivered, not confirmed (expired)" ]'

fresh late-ack
send --expires 1m "late confirmation"
exp=$(( $(date +%s) - 10 ))
sed -i "s/^expires: .*/expires: $exp/" "$RSPEAK_VAR/sent/1/msg"
echo "$(date +%s) desktop" >"$D/acks/1"
check "confirmation timed after the expiry (reference copy): does not count" \
	'[ "$(state_of 1 "$U")" = "delivered, not confirmed (expired; confirmation arrived after the expiry)" ]'
check "rspeak list does not count it" '[[ $("$RSPEAK" list) == *"[expired]"*"1 delivered"* ]]'

# ---- 5. configuration and format ----

echo "5. configuration"
conf=$BASE/rootspeak.conf
readc() { read_conf "$conf"; }
printf 'RSPEAK_REMIND_MINUTES=$(touch %s/executed)\nRSPEAK_AGENT_POLL=`touch %s/executed`\n' "$BASE" "$BASE" >"$conf"
check "the configuration is not run as code" '[ "$(readc)" = "30 60" ] && [ ! -e "$BASE/executed" ]'
printf '# comment\n RSPEAK_REMIND_MINUTES = 15  # on the right\nRSPEAK_AGENT_POLL=abc\nRSPEAK_DEFAULT_LEVEL=info\nOTHER=5\n' >"$conf"
check "valid values read, invalid and unknown ones ignored" '[ "$(readc)" = "15 60" ]'
printf 'RSPEAK_REMIND_MINUTES=0\nRSPEAK_AGENT_POLL=-3\n' >"$conf"
check "zero and negative values ignored" '[ "$(readc)" = "30 60" ]'
fresh format
send "test"
check "the message declares the format version" '[ "$(head -1 "$RSPEAK_VAR/sent/1/msg")" = "format: 1" ]'

# ---- 6. purge ----

echo "6. purge"
fresh purge
send "old"; send "recent"
sed -i "s/^date: .*/date: $(( $(date +%s) - 10 * 86400 ))/" "$RSPEAK_VAR/sent/1/msg"
prompt_login y >/dev/null
out=$("$RSPEAK" purge 7d)
check "rspeak purge 7d: deletes the message from 10 days ago" '[[ $out == "Deleted 1 message"* ]] && [ ! -d "$RSPEAK_VAR/sent/1" ]'
check "rspeak purge: copies and confirmations removed from the mailbox" \
	'[ ! -e "$D/inbox/1" ] && [ ! -e "$D/read/1" ] && [ ! -e "$D/acks/1" ]'
check "rspeak purge: the recent message stays" '[ -d "$RSPEAK_VAR/sent/2" ] && [ -e "$D/inbox/2" -o -e "$D/read/2" ]'
: >"$RSPEAK_VAR/sent/2/incomplete"
sed -i "s/^date: .*/date: $(( $(date +%s) - 10 * 86400 ))/" "$RSPEAK_VAR/sent/2/msg"
flock "$RSPEAK_VAR/sent/2/lock" sleep 1 &
sleep 0.2
"$RSPEAK" purge 7d >/dev/null 2>&1
check "rspeak purge: an incomplete or running send is not touched" '[ -d "$RSPEAK_VAR/sent/2" ]'
wait
out=$("$RSPEAK" purge 7x 2>&1)
check "rspeak purge: invalid duration refused" '[[ $out == *"invalid duration"* ]]'

# ---- 7. desktop agent: woken only when it is ready ----
# Needs a graphical session of the user running the tests (without one the
# agent exits at once); otherwise the group is skipped.

echo "7. agent"
if [ -n "$(loginctl show-user "$U" -p Display --value 2>/dev/null)" ]; then
	fresh agent
	mkdir -p "$RSPEAK_VAR/users" "$BASE/run-agent"
	alive=0 ready=0
	for i in 1 2 3 4 5 6 7 8 9 10; do
		rm -f "$BASE/run-agent/rootspeak-agent.ready"
		XDG_RUNTIME_DIR=$BASE/run-agent "$RSPEAK_USER" agent &
		p=$!
		for k in $(seq 1 200); do [ -s "$BASE/run-agent/rootspeak-agent.ready" ] && break; sleep 0.01; done
		[ "$(cat "$BASE/run-agent/rootspeak-agent.ready" 2>/dev/null)" = "$p" ] && ready=$((ready + 1))
		for k in 1 2 3 4 5; do pkill -USR1 -F "$BASE/run-agent/rootspeak-agent.ready" -f 'rootspeak-user agent$' 2>/dev/null; done
		sleep 0.2
		kill -0 $p 2>/dev/null && alive=$((alive + 1))
		kill $p 2>/dev/null; wait $p 2>/dev/null
	done
	check "the agent writes its PID in rootspeak-agent.ready when ready (10 of 10)" '[ $ready = 10 ]'
	check "waking the ready PID does not kill it (10 of 10)" '[ $alive = 10 ]'
	check "on exit rootspeak-agent.ready disappears" '[ ! -e "$BASE/run-agent/rootspeak-agent.ready" ]'
else
	echo "  --   skipped: no graphical session"
fi

# ---- 8. English only: whatever the language of the session ----

echo "8. English only"
fresh english
send "Text written by the administrator"
out=$(prompt s)
check "an Italian session: header and question in English, text untouched" \
	'[[ $out == *"Message from the administrator"* && $out == *"Do you confirm"* && $out == *"Text written by the administrator"* ]]'
check "«s» (an Italian yes) is not a yes: no confirmation, the message is postponed" \
	'[ ! -e "$D/acks/1" ] && [[ $(state_of 1 "$U") == "delivered, postponed on "* ]]'
out=$(prompt_login Y)
check "«Y» confirms" '[[ $out == *"Confirmed."* ]] && [ -s "$D/acks/1" ]'
send "Second"
out=$("$RSPEAK" status 2)
check "rspeak status in English" '[[ $out == *"USER"*"STATE"* && $out == *"delivered"* ]]'
out=$("$RSPEAK" status 1)
check "confirmation given from a terminal: shown as «terminal»" '[[ $out == *"confirmed on"*"(terminal "* ]]'
out=$("$RSPEAK" send "x" 2>&1)
check "error in English" '[[ $out == "rspeak: missing --to" ]]'
out=$("$RSPEAK" --help </dev/null | cat)
check "help in English" '[[ $out == *"SYNOPSIS"* && $out == *"SEND OPTIONS"* ]]'

# ---- 9. second review: revocation, terminals, interruptions, odd mailboxes ----

echo "9. second review"
fresh rev-wait
send "long send"
( flock "$RSPEAK_VAR/sent/1/lock" sleep 2 ) &
sleep 0.3
t0=$(date +%s%N)
"$RSPEAK" revoke 1 >/dev/null
dt=$((($(date +%s%N) - t0) / 1000000))
wait
check "rspeak revoke waits for a running send (lock), then removes the copy" '[ $dt -ge 1200 ] && [ ! -e "$D/inbox/1" ] && [ ! -e "$RSPEAK_VAR/sent/1/revoking" ]'

fresh rev-ack
send "revoked"
"$RSPEAK" revoke 1 >/dev/null
rev=$(cat "$RSPEAK_VAR/sent/1/revoked")
echo "$((rev + 5)) terminal pts/9" >"$D/acks/1"
check "confirmation timed after the revocation: does not count" '[[ "$(state_of 1 "$U")" == "delivered, not confirmed (revoked)" ]]'
echo "$rev terminal pts/9" >"$D/acks/1"
check "confirmation in the same second as the revocation: counts" '[[ "$(state_of 1 "$U")" == confirmed* ]]'

fresh rev-answer
send "revoked before the answer"
cp "$D/inbox/1" "$BASE/copy"
out=$(printf 'y\n' | script -qec "bash -c '$RSPEAK_USER prompt & sleep 0.5; rm -f $D/inbox/1; wait'" /dev/null 2>&1)
check "copy removed while the user answers: no confirmation written" '[ ! -e "$D/acks/1" ]'

fresh term-other
RSPEAK_TEST_TTY=/dev/null "$RSPEAK" send --to "$U" "someone else's terminal" >/dev/null
check "terminal of another user (here /dev/null, root's): not written" '[ "$(state_of 1 "$U")" = delivered ]'
: >"$BASE/tty-mine"
RSPEAK_TEST_TTY=$BASE/tty-mine "$RSPEAK" send --to "$U" "my terminal" >/dev/null
check "terminal of the user: written" 'grep -q "my terminal" "$BASE/tty-mine"'

fresh power
send "lost after a power cut"
rm -f "$D/inbox/1"
: >"$RSPEAK_VAR/sent/1/incomplete"
"$RSPEAK" list >/dev/null 2>&1
check "copy recorded but gone (incomplete send): recovery writes it again" '[ -s "$D/inbox/1" ] && [ ! -e "$RSPEAK_VAR/sent/1/incomplete" ] && [ "$(wc -l <"$RSPEAK_VAR/sent/1/delivery")" = 1 ]'

fresh rev-half
send "revocation interrupted"
date +%s >"$RSPEAK_VAR/sent/1/revoked"
: >"$RSPEAK_VAR/sent/1/revoking"
"$RSPEAK" list >/dev/null 2>&1
check "revocation interrupted: the next command removes the copy" '[ ! -e "$D/inbox/1" ] && [ ! -e "$RSPEAK_VAR/sent/1/revoking" ]'

fresh del-half
send "deletion interrupted"
mv "$RSPEAK_VAR/sent/1" "$RSPEAK_VAR/sent/.deleting-1"
out=$("$RSPEAK" list 2>&1)
check "deletion interrupted: rspeak list does not show it and recovery completes it" \
	'[[ $out != *"deletion interrupted"* ]] && [ ! -e "$RSPEAK_VAR/sent/.deleting-1" ] && [ ! -e "$D/inbox/1" ]'

fresh many-acks
send "one"
(cd "$D/acks" && seq 1000 6000 | xargs touch)
t0=$(date +%s%N)
"$RSPEAK" list >/dev/null
dt=$((($(date +%s%N) - t0) / 1000000))
[ -n "$VERBOSE" ] && echo "       rspeak list with 5000 fake files in acks/: $dt ms"
check "5000 fake files in acks/: rspeak list does not slow down (under 1 s)" '[ $dt -lt 1000 ]'

fresh fifo
send "one"
mkfifo "$D/acks/1"
check "acks/ID is a pipe: rspeak status does not hang" 'timeout 5 "$RSPEAK" status 1 >/dev/null'

fresh long
out=$(head -c 70000 /dev/zero | tr '\0' a | "$RSPEAK" send --to "$U" 2>&1)
check "text over 65536 bytes: refused with a clear error" '[[ $out == *"message too long: 70000 bytes"* ]] && [ ! -e "$RSPEAK_VAR/sent/1" ]'
out=$(head -c 65536 /dev/zero | tr '\0' a | "$RSPEAK" send --to "$U" 2>&1)
check "text of 65536 bytes: accepted" '[ -e "$RSPEAK_VAR/sent/1/msg" ]'

printf 'RSPEAK_REMIND_MINUTES=45 # minutes of postponement\n  RSPEAK_AGENT_POLL = 20  \n' >"$BASE/conf"
out=$(read_conf "$BASE/conf")
check "rootspeak.conf: comment at the end of the line and spaces" '[ "$out" = "45 20" ]'

# ---- 10. reminder ----

echo "10. reminder"
fresh remind
send "to confirm"
prompt n >/dev/null
out=$(prompt y)
check "postponed: the question does not come back at once at the prompt" '[[ $out != *"Do you confirm"* ]]'
out=$("$RSPEAK" remind 1)
check "rspeak remind: reminds whoever has not confirmed" '[[ $out == "Message 1: 1 recipient reminded." ]] && [ ! -e "$D/state/1.term" ]'
out=$(prompt y)
check "after the reminder the question comes back at the next prompt" '[[ $out == *"Do you confirm"* ]] && [[ "$(state_of 1 "$U")" == confirmed* ]]'
out=$("$RSPEAK" remind 1)
check "rspeak remind: whoever has confirmed is not reminded, and the command says so" '[[ $out == "Message 1: everyone has already confirmed, nobody to remind." ]]'
send "to revoke"
"$RSPEAK" revoke 2 >/dev/null
out=$("$RSPEAK" remind 2 2>&1)
check "rspeak remind of a revoked message: error" '[[ $out == *"has been revoked: nobody to remind"* ]]'

# ---- 11. arguments ----

echo "11. arguments"
fresh args
send "one"
out=$("$RSPEAK" remind 1 1 2>&1); rc=$?
check "an extra argument is an error, and nothing is done" \
	'[ $rc -ne 0 ] && [[ $out == "rspeak: too many arguments for remind: 1 (rspeak --help for the guide)" ]] && [ ! -e "$D/state/1.term" ]'
out=$("$RSPEAK" list extra 2>&1); rc=$?
check "list takes no argument" '[ $rc -ne 0 ] && [[ $out == *"too many arguments for list: extra"* ]]'
out=$("$RSPEAK" revoke 1 2 2>&1); rc=$?
check "revoke with two numbers: refused, the message is not revoked" '[ $rc -ne 0 ] && [ ! -e "$RSPEAK_VAR/sent/1/revoked" ]'

echo
if [ $fails -eq 0 ]; then echo "OK: $total checks"; else echo "FAILED: $fails of $total"; fi
# result, with commit and fingerprint of the code tested (read by the technical manual, chapter 11)
mkdir -p "$ROOT/tests/results"
printf '{"date": "%s", "commit": "%s", "fingerprint": "%s", "ok": %d, "failed": %d, "total": %d}\n' \
	"$(date '+%Y-%m-%d %H:%M:%S %Z')" "$("$ROOT/tools/fingerprint.sh" --commit)" "$("$ROOT/tools/fingerprint.sh")" \
	$((total - fails)) "$fails" "$total" >"$ROOT/tests/results/engine.json"
[ $fails -eq 0 ]
