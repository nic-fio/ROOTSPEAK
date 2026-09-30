# AMS - Advanced Messaging System for linux
# Libreria condivisa da `ams` (amministratore, root) e `ams-user` (utente).

AMS_VERSION=0.1.0

AMS_CONF=${AMS_CONF:-/etc/ams/ams.conf}

# La configurazione è un file di dati, non uno script: righe CHIAVE=valore,
# commenti con #. Si accettano solo le chiavi note, con valori interi
# positivi; il resto è ignorato e i valori mancanti restano quelli predefiniti.
ams_load_conf() {
	local riga k v
	AMS_REMIND_MINUTES=30
	AMS_AGENT_POLL=60
	[ -r "$AMS_CONF" ] || return 0
	while IFS= read -r riga || [ -n "$riga" ]; do
		riga=${riga%%#*}
		riga=${riga//[[:space:]]/}
		[ -n "$riga" ] || continue
		k=${riga%%=*}
		v=${riga#*=}
		[[ $v =~ ^[0-9]{1,6}$ ]] && [ "$v" -gt 0 ] || continue
		case $k in
		AMS_REMIND_MINUTES) AMS_REMIND_MINUTES=$v ;;
		AMS_AGENT_POLL) AMS_AGENT_POLL=$v ;;
		esac
	done <"$AMS_CONF"
	return 0
}
ams_load_conf
AMS_VAR=${AMS_VAR:-/var/lib/ams}

ams_die() { printf 'ams: %s\n' "$*" >&2; exit 1; }

# ---- lingua ----
# Ogni persona legge AMS nella sua lingua: l'amministratore quella del suo
# ambiente (sudo conserva LANG e LC_*), l'utente quella della sua sessione. Il
# testo dei messaggi non si traduce. Le lingue sono i file lib/lingue/XX.sh;
# senza una lingua nota vale l'inglese.

# Lingua dai valori di LANGUAGE, LC_ALL, LC_MESSAGES e LANG, con le regole di
# gettext: conta il primo impostato fra LC_ALL, LC_MESSAGES e LANG; se è C o
# POSIX vale l'inglese, altrimenti si prova prima l'elenco di LANGUAGE. Vince
# la prima lingua che AMS conosce. Risultato in _LINGUA. I valori possono
# venire dall'ambiente di un altro utente: si accettano solo codici di lettere.
ams_pick_lang() {
	local language=$1 loc=${2:-${3:-$4}} l
	_LINGUA=en
	case ${loc%%[.@]*} in '' | C | POSIX) return 0 ;; esac
	for l in ${language//:/ } "$loc"; do
		l=${l%%[_.@]*}
		if [[ $l =~ ^[a-z]{2,3}$ ]] && [ -r "$AMS_LIB/lingue/$l.sh" ]; then
			_LINGUA=$l
			return 0
		fi
	done
}

# Lingua da un ambiente in formato /proc/PID/environ, letto da stdin. Esito 1
# se l'ambiente è vuoto o illeggibile.
ams_env_lang() {
	local riga language='' lc_all='' lc_messages='' lang='' n=0
	while IFS= read -r -d '' riga; do
		n=$((n + 1))
		case $riga in
		LANGUAGE=*) language=${riga#*=} ;;
		LC_ALL=*) lc_all=${riga#*=} ;;
		LC_MESSAGES=*) lc_messages=${riga#*=} ;;
		LANG=*) lang=${riga#*=} ;;
		esac
	done
	[ $n -gt 0 ] || return 1
	ams_pick_lang "$language" "$lc_all" "$lc_messages" "$lang"
}

# Lingua del sistema (/etc/default/locale o /etc/locale.conf): quella del
# registro, che è di tutti. Calcolata una volta, in AMS_LINGUA_SISTEMA.
ams_sys_lang() {
	[ -z "${AMS_LINGUA_SISTEMA:-}" ] || return 0
	local f riga k v language='' lc_all='' lc_messages='' lang=''
	for f in /etc/default/locale /etc/locale.conf; do
		[ -r "$f" ] || continue
		while IFS= read -r riga || [ -n "$riga" ]; do
			k=${riga%%=*} v=${riga#*=} v=${v//[\"\']/}
			case $k in
			LANGUAGE) language=$v ;;
			LC_ALL) lc_all=$v ;;
			LC_MESSAGES) lc_messages=$v ;;
			LANG) lang=$v ;;
			esac
		done <"$f"
		break
	done
	ams_pick_lang "$language" "$lc_all" "$lc_messages" "$lang"
	AMS_LINGUA_SISTEMA=$_LINGUA
}

ams_load_lang() {
	declare -p "AMS_T_$1" >/dev/null 2>&1 || . "$AMS_LIB/lingue/$1.sh"
}

# tl LINGUA CHIAVE [dati]: stampa il testo nella lingua data; t CHIAVE [dati]
# nella lingua di chi usa AMS; tv VARIABILE CHIAVE [dati] lo mette in una
# variabile, senza sottoprocessi.
tl() {
	local _l=$1 _k=$2
	shift 2
	ams_load_lang "$_l"
	local -n _cat=AMS_T_$_l
	# shellcheck disable=SC2059
	printf -- "${_cat[$_k]:-$_k}" "$@"
}
t() { tl "$AMS_LINGUA" "$@"; }
tv() {
	local _v=$1 _k=$2
	shift 2
	ams_load_lang "$AMS_LINGUA"
	local -n _cat=AMS_T_$AMS_LINGUA
	# shellcheck disable=SC2059
	printf -v "$_v" -- "${_cat[$_k]:-$_k}" "$@"
}

ams_pick_lang "${LANGUAGE:-}" "${LC_ALL:-}" "${LC_MESSAGES:-}" "${LANG:-}"
AMS_LINGUA=$_LINGUA

# Canale registrato («terminale pts/3», «desktop») nella lingua data.
ams_channel() {
	case $2 in
	terminale*) printf '%s%s' "$(tl "$1" channel_term)" "${2#terminale}" ;;
	desktop) tl "$1" channel_desktop ;;
	*) printf '%s' "$2" ;;
	esac
}

# Testo di un evento nella lingua data: LINGUA EVENTO MESSAGGIO UTENTE CANALE DETTAGLI AUTORE.
ams_event_text() {
	local l=$1 ev=$2 id=$3 u=$4 ch=$5 det=$6 aut=$7
	case $ev in
	INVIATO) tl "$l" ev_INVIATO "$id" "$aut" "$det" ;;
	CONSEGNATO)
		if [ -n "$det" ]; then tl "$l" ev_CONSEGNATO "$id" "$u" "$det"; else tl "$l" ev_CONSEGNATO_recupero "$id" "$u"; fi ;;
	NON_CONSEGNATO) tl "$l" ev_NON_CONSEGNATO "$id" "$u" ;;
	ANNULLATO) tl "$l" ev_ANNULLATO "$id" ;;
	RECUPERATO) tl "$l" ev_RECUPERATO "$id" "$det" ;;
	CANCELLATO) tl "$l" ev_CANCELLATO "$id" "$aut" "$det" ;;
	RITIRATO) tl "$l" ev_RITIRATO "$id" "$aut" ;;
	RINVIATO) tl "$l" ev_RINVIATO "$u" "$id" "$(ams_channel "$l" "$ch")" ;;
	CONFERMATO) tl "$l" ev_CONFERMATO "$u" "$id" "$(ams_channel "$l" "$ch")" ;;
	CONFERMA_FALLITA) tl "$l" ev_CONFERMA_FALLITA "$u" "$id" "$(ams_channel "$l" "$ch")" "${det:-$(tl "$l" ev_unknown_error)}" ;;
	*) return 1 ;;
	esac
}

ams_log() { logger -t ams -- "$*" 2>/dev/null || true; }

# Evento strutturato nel journal: EVENTO MESSAGGIO UTENTE CANALE [DETTAGLI [AUTORE]].
# Il testo leggibile (journalctl -t ams) è nella lingua del sistema, uguale per
# tutti; i campi AMS_* permettono di ricostruire la storia di un messaggio
# (journalctl AMS_MESSAGGIO=12) e ad ams log di riscriverla nella lingua di chi
# la legge. Il journal aggiunge _UID, l'utente che ha scritto l'evento, non falsificabile.
ams_event() {
	local det=${5:-} aut=${6:-} testo
	det=${det//$'\n'/ }
	ams_sys_lang
	testo=$(ams_event_text "$AMS_LINGUA_SISTEMA" "$1" "$2" "$3" "$4" "$det" "$aut")
	printf 'MESSAGE=%s\nSYSLOG_IDENTIFIER=ams\nPRIORITY=6\nAMS_EVENTO=%s\nAMS_MESSAGGIO=%s\nAMS_UTENTE=%s\nAMS_CANALE=%s\nAMS_DETTAGLI=%s\nAMS_AUTORE=%s\n' \
		"$testo" "$1" "$2" "$3" "$4" "$det" "$aut" | logger --journald 2>/dev/null || ams_log "$testo"
}

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

# Messaggio formattato per il terminale, nella lingua data (predefinita: AMS_LINGUA).
ams_msg_term() {
	printf '\n%s\n' "$(tl "${2:-$AMS_LINGUA}" term_header "$(ams_msg_heading "$1")")"
	ams_msg_body "$1"
	printf '────────────────────────────────────────\n'
}
