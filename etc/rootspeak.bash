# RootSpeak - Advanced Messaging System for Linux
# Hook for interactive bash (called from /etc/profile.d/rootspeak.sh): before
# every prompt it shows the administrator's messages and asks for the read confirmation.
if [[ $- == *i* ]] && [ -z "${__RSPEAK_HOOK:-}" ] && [ -x @LIBDIR@/rootspeak-user ]; then
	__RSPEAK_HOOK=1
	__RSPEAK_INBOX=@VARDIR@/users/$(id -un)/inbox
	__rspeak_prompt() {
		local s=$?
		# A check without external processes: with an empty mailbox it costs nothing.
		if compgen -G "$__RSPEAK_INBOX/[0-9]*" >/dev/null; then
			@LIBDIR@/rootspeak-user prompt
		fi
		return $s
	}
	if [[ "$(declare -p PROMPT_COMMAND 2>/dev/null)" == "declare -a"* ]]; then
		PROMPT_COMMAND+=(__rspeak_prompt)
	else
		PROMPT_COMMAND="__rspeak_prompt${PROMPT_COMMAND:+; $PROMPT_COMMAND}"
	fi
	# At login the question is asked at once, even if it had been postponed.
	if shopt -q login_shell && compgen -G "$__RSPEAK_INBOX/[0-9]*" >/dev/null; then
		@LIBDIR@/rootspeak-user prompt --login
	fi
fi
