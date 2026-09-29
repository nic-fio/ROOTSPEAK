# AMS - Advanced Messaging System for linux
# Libreria condivisa da `ams` (amministratore, root) e `ams-user` (utente).

AMS_DEFAULT_LEVEL=ack
AMS_REMIND_MINUTES=30
AMS_AGENT_POLL=60
AMS_CONF=${AMS_CONF:-/etc/ams/ams.conf}
[ -r "$AMS_CONF" ] && . "$AMS_CONF"
AMS_VAR=${AMS_VAR:-/var/lib/ams}

ams_die() { printf 'ams: %s\n' "$*" >&2; exit 1; }

ams_log() { logger -t ams -- "$*" 2>/dev/null || true; }

# Toglie le sequenze di escape ANSI e i caratteri di controllo (C0 tranne tab e a capo, DEL, C1 in UTF-8),
# così un messaggio non può iniettare sequenze di escape nei terminali.
ams_sanitize() {
	LC_ALL=C sed 's/\x1b\[[0-9;?]*[@-~]//g; s/\x1b\][^\x07]*\x07//g' |
		LC_ALL=C tr -d '\000-\010\013-\037\177' | LC_ALL=C sed 's/\xc2[\x80-\x9f]//g'
}

# Formato di un messaggio: intestazione "chiave: valore", riga vuota, testo.
ams_msg_get() { sed -n "/^\$/q; s/^$2: //p" "$1"; }
ams_msg_body() { sed '1,/^$/d' "$1"; }

# Vero se il messaggio ha una scadenza già passata.
ams_msg_expired() {
	local exp
	exp=$(ams_msg_get "$1" expires)
	[ -n "$exp" ] && [ "$exp" -le "$(date +%s)" ]
}

# Intestazione leggibile: "Titolo · 29/09 22:15" oppure solo la data.
ams_msg_heading() {
	local title date
	title=$(ams_msg_get "$1" title)
	date=$(date -d "@$(ams_msg_get "$1" date)" '+%d/%m %H:%M')
	printf '%s%s' "${title:+$title · }" "$date"
}

# Messaggio formattato per il terminale.
ams_msg_term() {
	printf '\n── AMS · Messaggio dall'\''amministratore · %s ──\n' "$(ams_msg_heading "$1")"
	ams_msg_body "$1"
	printf '────────────────────────────────────────\n'
}
