# RootSpeak - Advanced Messaging System for Linux
# Aggancio per fish interattiva (/etc/fish/conf.d/rootspeak.fish): prima di ogni
# prompt mostra i messaggi dell'amministratore e chiede la conferma di lettura.
if status is-interactive; and not set -q __rspeak_hook; and test -x @LIBDIR@/rootspeak-user
	set -g __rspeak_hook 1
	set -g __rspeak_inbox @VARDIR@/users/(id -un)/inbox
	function __rspeak_prompt --on-event fish_prompt
		# con la casella vuota non si lancia nulla (set ammette glob senza
		# risultati; fish non ha [0-9] nei glob, da qui string match)
		set -l f $__rspeak_inbox/*
		if string match -rq '/[0-9][^/]*$' -- $f
			@LIBDIR@/rootspeak-user prompt
		end
	end
	# Al login la domanda viene fatta subito, anche se era stata rimandata.
	if status is-login
		set -l f $__rspeak_inbox/*
		if string match -rq '/[0-9][^/]*$' -- $f
			@LIBDIR@/rootspeak-user prompt --login
		end
	end
end
