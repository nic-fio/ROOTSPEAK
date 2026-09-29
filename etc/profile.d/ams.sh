# AMS - Advanced Messaging System for linux
# Hook per le shell bash interattive: prima di ogni prompt mostra i messaggi
# dell'amministratore e chiede la conferma di lettura.
if [ -n "${BASH_VERSION:-}" ] && [[ $- == *i* ]] && [ -z "${__AMS_HOOK:-}" ] && [ -x @LIBDIR@/ams-user ]; then
	__AMS_HOOK=1
	__AMS_INBOX=@VARDIR@/users/$(id -un)/inbox
	__ams_prompt() {
		local s=$?
		# Controllo senza processi esterni: con la casella vuota non costa nulla.
		if compgen -G "$__AMS_INBOX/[0-9]*" >/dev/null; then
			@LIBDIR@/ams-user prompt
		fi
		return $s
	}
	if [[ "$(declare -p PROMPT_COMMAND 2>/dev/null)" == "declare -a"* ]]; then
		PROMPT_COMMAND+=(__ams_prompt)
	else
		PROMPT_COMMAND="__ams_prompt${PROMPT_COMMAND:+; $PROMPT_COMMAND}"
	fi
	# Al login la domanda viene fatta subito, anche se era stata rimandata.
	if shopt -q login_shell && compgen -G "$__AMS_INBOX/[0-9]*" >/dev/null; then
		@LIBDIR@/ams-user prompt --login
	fi
fi
