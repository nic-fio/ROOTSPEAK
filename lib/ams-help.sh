# AMS - Advanced Messaging System for linux
# Guida integrata di `ams --help`, sul modello di MTERM:
#   - in un terminale, guida interattiva a schede;
#   - con un terminale più piccolo di 44x10, pagina in stile manuale con un pager;
#   - se l'uscita non è un terminale, testo semplice.
# I testi stanno solo qui: tools/check-docs.py controlla che il riferimento del
# manuale utente riporti ogni voce di comandi e opzioni, con lo stesso testo.

# Voci "etichetta¦descrizione".
AMS_HELP_COMMANDS=(
	"send [opzioni] [TESTO]¦Invia un messaggio ai destinatari indicati con --to. Senza TESTO né --file, il testo viene letto da stdin."
	"list¦Elenca i messaggi inviati, con quanti destinatari hanno confermato (ack) o visto (info) ciascun messaggio."
	"status ID¦Mostra il testo del messaggio e, per ogni destinatario, se ha confermato, quando e da dove."
	"revoke ID¦Ritira un messaggio: chi non l'ha ancora visto non lo vedrà più, e finestre e domande ancora aperte si chiudono da sole."
	"version¦Mostra la versione di AMS."
	"help, --help, -h¦Mostra questa guida. La apre anche «ams» senza argomenti."
)

AMS_HELP_OPTIONS=(
	"--to DEST¦Destinatari, separati da virgole senza spazi: un utente (mario), un gruppo Unix (@sviluppo), all (tutti gli utenti umani) oppure online (solo quelli collegati adesso)."
	"--level info|ack¦ack (predefinito) chiede la conferma di lettura e la ripropone finché l'utente non la dà; info mostra il messaggio una volta, senza domande."
	"--title TITOLO¦Titolo mostrato nell'intestazione del messaggio e nella finestra del desktop."
	"--expires DURATA¦Scadenza, dopo la quale il messaggio non viene più mostrato: 30m, 2h, 3d oppure data e ora (\"2026-10-04 12:00\"; le date a parole vanno in inglese)."
	"--file FILE¦Legge il testo del messaggio da FILE."
)

AMS_HELP_EXAMPLES=(
	"ams send --to mario \"Il tuo account scade venerdì.\"¦Messaggio con conferma di lettura a un solo utente."
	"ams send --to @sviluppo --title Manutenzione --file avviso.txt¦Testo preso da un file, con titolo, a tutti i membri del gruppo sviluppo."
	"ams send --to online --level info \"Riavvio tra 5 minuti.\"¦Avviso senza conferma, solo a chi è collegato adesso."
	"ams send --to all --expires 3d \"Nuova policy password.\"¦A tutti gli utenti; dopo tre giorni smette di essere mostrato."
	"ams list¦Quali messaggi sono stati inviati e quante conferme hanno."
	"ams status 12¦Chi ha confermato il messaggio 12, quando e da dove."
	"ams revoke 12¦Ritira il messaggio 12."
)

AMS_HELP_FILES=(
	"/etc/ams/ams.conf¦Configurazione: livello predefinito, minuti prima di riproporre un messaggio rimandato, intervallo di controllo dell'agente del desktop."
	"/var/lib/ams/¦I messaggi: sent/ (copie di riferimento, solo root) e users/UTENTE/ (la casella di ogni utente, leggibile solo da lui e da root)."
	"sudo journalctl -t ams¦Il registro di sistema: invii, conferme, avvisi mostrati e ritiri."
	"/usr/local/share/doc/ams/AMS_Manuale_Utente.html¦Il manuale utente completo, da aprire in un browser."
)

AMS_HELP_DESCRIPTION="AMS permette agli amministratori di mandare messaggi di testo agli utenti della \
macchina e di sapere chi li ha letti. I messaggi compaiono nei terminali (console, ssh, terminali del \
desktop, tmux) e sul desktop, in una finestra con i pulsanti «Ho letto» e «Più tardi»; chi non è \
collegato li trova al login successivo. Con il livello ack, AMS chiede la conferma di lettura e la \
ripropone finché l'utente non la dà, senza mai bloccare il lavoro. Il comando è riservato agli \
amministratori (gruppo sudo o wheel) e si rilancia da solo con sudo."

AMS_HELP_SYNOPSIS=(
	"ams send --to DEST [opzioni] [TESTO]"
	"ams list"
	"ams status ID"
	"ams revoke ID"
	"ams version"
)

# ---- testo ----

# Colori ANSI, vuoti senza colore.
_help_colors() {
	if [ "$1" = 1 ]; then
		_R=$'\e[0m' _B=$'\e[1m' _D=$'\e[2m' _U=$'\e[4m' _G=$'\e[1;32m' _Y=$'\e[1;33m' _C=$'\e[1;36m' _V=$'\e[7;1m'
	else
		_R='' _B='' _D='' _U='' _G='' _Y='' _C='' _V=''
	fi
}

# Manda a capo "testo" a "larghezza" con "rientro": righe in _W.
_help_wrap() {
	local width=$2 ind=$3 pad avail cur='' w
	local -a words
	printf -v pad '%*s' "$ind" ''
	avail=$((width - ind))
	if [ $avail -lt 24 ]; then avail=24; fi
	read -ra words <<<"$1"
	_W=()
	for w in "${words[@]}"; do
		if [ -z "$cur" ]; then
			cur=$w
		elif [ $((${#cur} + 1 + ${#w})) -le $avail ]; then
			cur+=" $w"
		else
			_W+=("$pad$cur")
			cur=$w
		fi
	done
	if [ -n "$cur" ]; then _W+=("$pad$cur"); fi
}

_help_repeat() { # carattere, volte → _X
	printf -v _X '%*s' "$2" ''
	_X=${_X// /$1}
}

# ---- pagina in stile manuale (pager e testo semplice) ----

_help_page() { # colore, larghezza
	local color=$1 width=$2 e left mid right gap l r
	if [ "$width" -lt 60 ]; then width=60; fi
	if [ "$width" -gt 100 ]; then width=100; fi
	_help_colors "$color"
	local ti='       ' di=14

	three() {
		left=$1 mid=$2 right=$3
		gap=$((width - ${#left} - ${#mid} - ${#right}))
		if [ $gap -lt 2 ]; then gap=2; fi
		l=$((gap / 2)) r=$((gap - l))
		printf '%s%s%*s%s%*s%s%s\n' "$_B" "$left" "$l" '' "$mid" "$r" '' "$right" "$_R"
	}
	hdr() { printf '\n%s%s%s\n' "$_B" "$1" "$_R"; }
	para() {
		_help_wrap "$1" "$width" "$2"
		printf '%s\n' "${_W[@]}"
	}
	entries() { # nome dell'array
		local -n arr=$1
		for e in "${arr[@]}"; do
			printf '%s%s%s%s\n' "$ti" "$_G" "${e%%¦*}" "$_R"
			para "${e#*¦}" "$di"
		done
	}

	three "AMS(1)" "Manuale di ams" "AMS(1)"
	hdr NOME
	para "ams — invia messaggi agli utenti della macchina e ne segue la conferma di lettura" 7
	hdr SINTASSI
	for e in "${AMS_HELP_SYNOPSIS[@]}"; do printf '%s%s%s%s %s\n' "$ti" "$_B" "${e%% *}" "$_R" "${e#* }"; done
	hdr DESCRIZIONE
	para "$AMS_HELP_DESCRIPTION" 7
	hdr COMANDI
	entries AMS_HELP_COMMANDS
	hdr "OPZIONI DI SEND"
	entries AMS_HELP_OPTIONS
	hdr ESEMPI
	entries AMS_HELP_EXAMPLES
	hdr FILE
	entries AMS_HELP_FILES
	hdr AMBIENTE
	printf '%s%sPAGER%s\n' "$ti" "$_G" "$_R"
	para "Pager usato per impaginare questa guida quando il terminale è troppo piccolo per quella interattiva (predefinito: less). Come NO_COLOR, arriva ad ams solo se sudo la conserva (env_keep in sudoers)." "$di"
	printf '%s%sNO_COLOR%s\n' "$ti" "$_G" "$_R"
	para "Se impostata, disabilita i colori." "$di"
	hdr "STATO DI USCITA"
	printf '%s%s0%s\n' "$ti" "$_G" "$_R"
	para "Completato con successo." "$di"
	printf '%s%s1%s\n' "$ti" "$_G" "$_R"
	para "Errore: il messaggio d'errore, che inizia con «ams:», dice quale." "$di"
	hdr "VEDERE ANCHE"
	para "wall(1), write(1), e il manuale utente in /usr/local/share/doc/ams/AMS_Manuale_Utente.html" 7
	echo
	three "ams $AMS_VERSION" "" "AMS(1)"
}

# ---- guida interattiva a schede ----

_HELP_TABS=(Info Comandi Opzioni Esempi File)

# Righe della scheda $1 larga $2: tipo in _LT (H titolo, F voce, T testo), testo in _LS.
_help_tab_lines() {
	local tab=$1 inner=$2 e w first=1
	_LT=() _LS=()
	add() { _LT+=("$1"); _LS+=("$2"); }
	items() {
		local -n arr=$1
		for e in "${arr[@]}"; do
			if [ $first = 0 ]; then add T ''; fi
			first=0
			add F " ${e%%¦*}"
			_help_wrap "${e#*¦}" "$inner" 4
			for w in "${_W[@]}"; do add T "$w"; done
		done
	}
	case $tab in
	0)
		add H NOME
		add T "   ams — messaggi agli utenti con conferma di lettura"
		add T ''
		add H SINTASSI
		for e in "${AMS_HELP_SYNOPSIS[@]}"; do add T "   $e"; done
		add T ''
		add H DESCRIZIONE
		_help_wrap "$AMS_HELP_DESCRIPTION" "$inner" 3
		for w in "${_W[@]}"; do add T "$w"; done
		add T ''
		add T "   AMS $AMS_VERSION · manuale completo: /usr/local/share/doc/ams/AMS_Manuale_Utente.html"
		;;
	1) add H Comandi; add T ''; items AMS_HELP_COMMANDS ;;
	2) add H "Opzioni di send"; add T ''; items AMS_HELP_OPTIONS ;;
	3) add H Esempi; add T ''; items AMS_HELP_EXAMPLES ;;
	4) add H "File e registro"; add T ''; items AMS_HELP_FILES ;;
	esac
}

_help_row() { # tipo, testo → riga incorniciata in _ROW
	local inner=$((_TW - 4)) s=$2 pad
	s=${s:0:$inner}
	printf -v pad '%*s' $((inner - ${#s})) ''
	case $1 in
	H) s="$_Y$s$_R" ;;
	F) s="$_G$s$_R" ;;
	esac
	_ROW="$_D│$_R $s$pad $_D│$_R"
}

_help_border() { # sinistra, destra, titolo → _ROW
	local inner=$((_TW - 2)) t
	if [ -n "$3" ]; then
		t="─ $3 "
		_help_repeat ─ $((inner - ${#t}))
		_ROW="$_D$1$_R$_C$t$_R$_D$_X$2$_R"
	else
		_help_repeat ─ "$inner"
		_ROW="$_D$1$_X$2$_R"
	fi
}

_help_draw() {
	local ch=$((_TH - 6)) i n=0 label bar='' total off bottom pos hint status gap inner=$((_TW - 4))
	local -a rows=()
	_help_tab_lines "$_TAB" "$inner"
	total=${#_LS[@]}
	_MAX=$((total - ch))
	if [ $_MAX -lt 0 ]; then _MAX=0; fi
	if [ "${_SCROLL[_TAB]}" -gt $_MAX ]; then _SCROLL[_TAB]=$_MAX; fi
	if [ "${_SCROLL[_TAB]}" -lt 0 ]; then _SCROLL[_TAB]=0; fi
	off=${_SCROLL[_TAB]}

	_help_border ┌ ┐ "ams — guida"; rows+=("$_ROW")
	for i in "${!_HELP_TABS[@]}"; do
		label=" ${_HELP_TABS[i]} "
		if [ "$i" = "$_TAB" ]; then
			if [ -n "$_V" ]; then bar+="$_V$label$_R"; else bar+=">${_HELP_TABS[i]}<"; fi
		else
			bar+="$_D$label$_R"
		fi
		n=$((n + ${#label}))
	done
	local pad
	printf -v pad '%*s' $((inner - n > 0 ? inner - n : 0)) ''
	rows+=("$_D│$_R $bar$pad $_D│$_R")
	_help_border ├ ┤ ''; rows+=("$_ROW")
	for ((i = 0; i < ch; i++)); do
		if [ $((off + i)) -lt $total ]; then
			_help_row "${_LT[off + i]}" "${_LS[off + i]}"
		else
			_help_row T ''
		fi
		rows+=("$_ROW")
	done
	_help_border ├ ┤ ''; rows+=("$_ROW")
	bottom=$((off + ch))
	if [ $bottom -gt $total ]; then bottom=$total; fi
	pos="righe $((off + 1))-$bottom/$total"
	hint="←/→ schede · ↑/↓ scorri · PgUp/PgDn · g/G · q esci"
	status=$hint
	if [ $((${#hint} + ${#pos} + 3)) -le $inner ]; then
		printf -v gap '%*s' $((inner - ${#hint} - ${#pos})) ''
		status="$hint$gap$pos"
	fi
	printf -v pad '%*s' $((inner - ${#status} > 0 ? inner - ${#status} : 0)) ''
	rows+=("$_D│ $status$pad │$_R")
	_help_border └ ┘ ''; rows+=("$_ROW")

	local IFS=$'\n'
	printf '\e[H%s\e[J' "${rows[*]}"
}

# Legge un tasto dal terminale: nome in _K (timeout se non arriva nulla).
_help_key() {
	local k rest c rc
	_K=none
	IFS= read -rsn1 -t 0.3 k </dev/tty
	rc=$?
	if [ $rc -gt 128 ]; then _K=timeout; return; fi
	if [ $rc -ne 0 ]; then _K=quit; return; fi
	case $k in
	$'\e')
		rest=''
		IFS= read -rsn2 -t 0.05 rest </dev/tty
		case $rest in
		'[A' | OA) _K=up ;;
		'[B' | OB) _K=down ;;
		'[C' | OC) _K=right ;;
		'[D' | OD) _K=left ;;
		'[H' | OH) _K=home ;;
		'[F' | OF) _K=end ;;
		'[Z') _K=stab ;;
		'') _K=quit ;;
		'['[0-9])
			# sequenze "ESC [ n ~": 5 PgUp, 6 PgDn, 1/7 Home, 4/8 End
			c=''
			while IFS= read -rsn1 -t 0.05 c </dev/tty && [ "$c" != '~' ]; do :; done
			case ${rest:1:1} in
			5) _K=pgup ;;
			6) _K=pgdn ;;
			1 | 7) _K=home ;;
			4 | 8) _K=end ;;
			esac
			;;
		esac
		;;
	q | Q) _K=quit ;;
	$'\t') _K=tab ;;
	h) _K=left ;;
	l | '') _K=right ;;
	j) _K=down ;;
	k) _K=up ;;
	' ') _K=pgdn ;;
	b) _K=pgup ;;
	g) _K=home ;;
	G) _K=end ;;
	[1-9]) _K=digit$k ;;
	esac
}

# Rimette il terminale com'era: modo, schermo principale, cursore.
_help_restore() {
	stty "$_HELP_STTY" </dev/tty 2>/dev/null
	printf '\e[?25h\e[?1049l'
}

_help_tui() {
	local size ch
	size=$(stty size </dev/tty 2>/dev/null) || return 1
	read -r _TH _TW <<<"$size"
	if [ "${_TW:-0}" -lt 44 ] || [ "${_TH:-0}" -lt 10 ]; then return 1; fi
	_HELP_STTY=$(stty -g </dev/tty) || return 1
	_help_colors "$([ -z "${NO_COLOR:-}" ] && echo 1 || echo 0)"
	_TAB=0
	_SCROLL=(0 0 0 0 0)

	trap '_help_restore; exit 0' INT TERM HUP
	stty -echo -icanon min 1 time 0 </dev/tty
	printf '\e[?1049h\e[?25l'
	_help_draw
	while true; do
		_help_key
		ch=$((_TH - 7))
		case $_K in
		quit) break ;;
		timeout)
			# ridisegna se la finestra ha cambiato dimensione
			size=$(stty size </dev/tty 2>/dev/null) || continue
			if [ "$size" != "$_TH $_TW" ]; then
				read -r _TH _TW <<<"$size"
				if [ "$_TW" -lt 44 ] || [ "$_TH" -lt 10 ]; then break; fi
				_help_draw
			fi
			continue
			;;
		left | stab) _TAB=$(((_TAB - 1 + ${#_HELP_TABS[@]}) % ${#_HELP_TABS[@]})) ;;
		right | tab) _TAB=$(((_TAB + 1) % ${#_HELP_TABS[@]})) ;;
		up) _SCROLL[_TAB]=$((_SCROLL[_TAB] - 1)) ;;
		down) _SCROLL[_TAB]=$((_SCROLL[_TAB] + 1)) ;;
		pgup) _SCROLL[_TAB]=$((_SCROLL[_TAB] - ch)) ;;
		pgdn) _SCROLL[_TAB]=$((_SCROLL[_TAB] + ch)) ;;
		home) _SCROLL[_TAB]=0 ;;
		end) _SCROLL[_TAB]=999999 ;;
		digit*)
			if [ "${_K#digit}" -le ${#_HELP_TABS[@]} ]; then _TAB=$((${_K#digit} - 1)); fi
			;;
		*) continue ;;
		esac
		_help_draw
	done
	trap - INT TERM HUP
	_help_restore
	return 0
}

# Mostra la guida nel modo adatto a dove va l'uscita.
ams_help() {
	set +eu
	if [ ! -t 0 ] || [ ! -t 1 ]; then
		_help_page 0 80
		return
	fi
	if _help_tui; then return; fi
	local color=1 width
	if [ -n "${NO_COLOR:-}" ]; then color=0; fi
	width=$(stty size </dev/tty 2>/dev/null | cut -d' ' -f2)
	if [ -n "${PAGER:-}" ]; then
		_help_page "$color" "${width:-80}" | sh -c "$PAGER"
	elif command -v less >/dev/null; then
		_help_page "$color" "${width:-80}" | less -R -F -X
	else
		_help_page "$color" "${width:-80}"
	fi
}
