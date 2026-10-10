# Copyright (c) 2026 Nicola Fiorillo
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0

# RootSpeak - Advanced Messaging System for Linux
# Hook for the shells. bash asks for the confirmation at every prompt
# (rootspeak.bash); zsh and fish have their own hook (rootspeak.zsh from zshrc,
# rootspeak.fish from fish/conf.d); the other shells that read /etc/profile (sh,
# dash, ksh…) get the question at login. The file is plain sh: they all read it.
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
