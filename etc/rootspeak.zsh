# RootSpeak - Advanced Messaging System for Linux
# Aggancio per zsh interattiva (richiamato da /etc/zsh/zshrc): prima di ogni
# prompt mostra i messaggi dell'amministratore e chiede la conferma di lettura.
if [[ -o interactive ]] && [[ -z ${__RSPEAK_HOOK:-} ]] && [[ -x @LIBDIR@/rootspeak-user ]]; then
	__RSPEAK_HOOK=1
	__RSPEAK_INBOX=@VARDIR@/users/$(id -un)/inbox
	__rspeak_prompt() {
		local s=$? f
		# Controllo senza processi esterni: con la casella vuota non costa nulla.
		f=($__RSPEAK_INBOX/[0-9]*(N))
		if (( ${#f} )); then
			@LIBDIR@/rootspeak-user prompt
		fi
		return $s
	}
	autoload -Uz add-zsh-hook
	add-zsh-hook precmd __rspeak_prompt
	# Al login la domanda viene fatta subito, anche se era stata rimandata.
	if [[ -o login ]]; then
		() {
			local f=($__RSPEAK_INBOX/[0-9]*(N))
			if (( ${#f} )); then @LIBDIR@/rootspeak-user prompt --login; fi
		}
	fi
fi
