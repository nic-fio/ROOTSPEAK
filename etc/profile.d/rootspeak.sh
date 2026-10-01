# RootSpeak - Advanced Messaging System for Linux
# Aggancio per le shell. bash chiede la conferma a ogni prompt (rootspeak.bash); zsh
# e fish hanno il loro aggancio (rootspeak.zsh da zshrc, rootspeak.fish da fish/conf.d);
# le altre shell che leggono /etc/profile (sh, dash, ksh…) ricevono la domanda
# al login. Il file è in sh semplice: lo leggono tutte.
if [ -n "${BASH_VERSION:-}" ]; then
	[ -r @LIBDIR@/rootspeak.bash ] && . @LIBDIR@/rootspeak.bash
elif [ -z "${ZSH_VERSION:-}" ]; then
	case $- in
	*i*)
		if [ -z "${__RSPEAK_HOOK:-}" ] && [ -x @LIBDIR@/rootspeak-user ]; then
			__RSPEAK_HOOK=1
			for __rspeak_f in @VARDIR@/users/$(id -un)/inbox/[0-9]*; do
				if [ -e "$__rspeak_f" ]; then
					@LIBDIR@/rootspeak-user prompt --login
					break
				fi
			done
			unset __rspeak_f
		fi
		;;
	esac
fi
