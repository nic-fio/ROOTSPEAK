# RootSpeak - Advanced Messaging System for Linux
# Hook for interactive zsh (called from /etc/zsh/zshrc): before every prompt it
# shows the administrator's messages and asks for the read confirmation.
if [[ -o interactive ]] && [[ -z ${__RSPEAK_HOOK:-} ]] && [[ -x @LIBDIR@/rootspeak-user ]]; then
	__RSPEAK_HOOK=1
	__RSPEAK_INBOX=@VARDIR@/users/$(id -un)/inbox
	__rspeak_prompt() {
		local s=$? f
		# A check without external processes: with an empty mailbox it costs nothing.
		f=($__RSPEAK_INBOX/[0-9]*(N))
		if (( ${#f} )); then
			@LIBDIR@/rootspeak-user prompt
		fi
		return $s
	}
	autoload -Uz add-zsh-hook
	add-zsh-hook precmd __rspeak_prompt
	# At login the question is asked at once, even if it had been postponed.
	if [[ -o login ]]; then
		() {
			local f=($__RSPEAK_INBOX/[0-9]*(N))
			if (( ${#f} )); then @LIBDIR@/rootspeak-user prompt --login; fi
		}
	fi
fi
