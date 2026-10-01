# RootSpeak - Advanced Messaging System for Linux
# Aggancio per bash interattiva (richiamato da /etc/profile.d/rootspeak.sh): prima di
# ogni prompt mostra i messaggi dell'amministratore e chiede la conferma di lettura.
if [[ $- == *i* ]] && [ -z "${__RSPEAK_HOOK:-}" ] && [ -x @LIBDIR@/rootspeak-user ]; then
	__RSPEAK_HOOK=1
	__RSPEAK_INBOX=@VARDIR@/users/$(id -un)/inbox
	__rspeak_prompt() {
		local s=$?
		# Controllo senza processi esterni: con la casella vuota non costa nulla.
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
	# Al login la domanda viene fatta subito, anche se era stata rimandata.
	if shopt -q login_shell && compgen -G "$__RSPEAK_INBOX/[0-9]*" >/dev/null; then
		@LIBDIR@/rootspeak-user prompt --login
	fi
fi
