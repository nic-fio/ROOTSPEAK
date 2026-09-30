# AMS - Advanced Messaging System
# Aggancio per zsh interattiva (richiamato da /etc/zsh/zshrc): prima di ogni
# prompt mostra i messaggi dell'amministratore e chiede la conferma di lettura.
if [[ -o interactive ]] && [[ -z ${__AMS_HOOK:-} ]] && [[ -x @LIBDIR@/ams-user ]]; then
	__AMS_HOOK=1
	__AMS_INBOX=@VARDIR@/users/$(id -un)/inbox
	__ams_prompt() {
		local s=$? f
		# Controllo senza processi esterni: con la casella vuota non costa nulla.
		f=($__AMS_INBOX/[0-9]*(N))
		if (( ${#f} )); then
			@LIBDIR@/ams-user prompt
		fi
		return $s
	}
	autoload -Uz add-zsh-hook
	add-zsh-hook precmd __ams_prompt
	# Al login la domanda viene fatta subito, anche se era stata rimandata.
	if [[ -o login ]]; then
		() {
			local f=($__AMS_INBOX/[0-9]*(N))
			if (( ${#f} )); then @LIBDIR@/ams-user prompt --login; fi
		}
	fi
fi
