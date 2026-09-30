# AMS - Advanced Messaging System for linux
# Aggancio per le shell. bash chiede la conferma a ogni prompt (ams.bash); zsh
# e fish hanno il loro aggancio (ams.zsh da zshrc, ams.fish da fish/conf.d);
# le altre shell che leggono /etc/profile (sh, dash, ksh…) ricevono la domanda
# al login. Il file è in sh semplice: lo leggono tutte.
if [ -n "${BASH_VERSION:-}" ]; then
	[ -r @LIBDIR@/ams.bash ] && . @LIBDIR@/ams.bash
elif [ -z "${ZSH_VERSION:-}" ]; then
	case $- in
	*i*)
		if [ -z "${__AMS_HOOK:-}" ] && [ -x @LIBDIR@/ams-user ]; then
			__AMS_HOOK=1
			for __ams_f in @VARDIR@/users/$(id -un)/inbox/[0-9]*; do
				if [ -e "$__ams_f" ]; then
					@LIBDIR@/ams-user prompt --login
					break
				fi
			done
			unset __ams_f
		fi
		;;
	esac
fi
