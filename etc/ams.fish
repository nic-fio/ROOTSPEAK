# AMS - Advanced Messaging System for linux
# Aggancio per fish interattiva (/etc/fish/conf.d/ams.fish): prima di ogni
# prompt mostra i messaggi dell'amministratore e chiede la conferma di lettura.
if status is-interactive; and not set -q __ams_hook; and test -x @LIBDIR@/ams-user
	set -g __ams_hook 1
	set -g __ams_inbox @VARDIR@/users/(id -un)/inbox
	function __ams_prompt --on-event fish_prompt
		# con la casella vuota non si lancia nulla (set ammette glob senza
		# risultati; fish non ha [0-9] nei glob, da qui string match)
		set -l f $__ams_inbox/*
		if string match -rq '/[0-9][^/]*$' -- $f
			@LIBDIR@/ams-user prompt
		end
	end
	# Al login la domanda viene fatta subito, anche se era stata rimandata.
	if status is-login
		set -l f $__ams_inbox/*
		if string match -rq '/[0-9][^/]*$' -- $f
			@LIBDIR@/ams-user prompt --login
		end
	end
end
