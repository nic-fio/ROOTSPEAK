# Copyright (c) 2026 Nicola Fiorillo
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0

# RootSpeak - Advanced Messaging System for Linux
# Hook for interactive fish (/etc/fish/conf.d/rootspeak.fish): before every
# prompt it shows the administrator's messages and asks for the read confirmation.
if status is-interactive; and not set -q __rspeak_hook; and test -x @LIBDIR@/rootspeak-user
	set -g __rspeak_hook 1
	set -g __rspeak_inbox @VARDIR@/users/(id -un)/inbox
	function __rspeak_prompt --on-event fish_prompt
		# with an empty mailbox nothing is run (set accepts globs without
		# results; fish has no [0-9] in globs, hence string match)
		set -l f $__rspeak_inbox/*
		if string match -rq '/[0-9][^/]*$' -- $f
			@LIBDIR@/rootspeak-user prompt
		end
	end
	# At login the question is asked at once, even if it had been postponed.
	if status is-login
		set -l f $__rspeak_inbox/*
		if string match -rq '/[0-9][^/]*$' -- $f
			@LIBDIR@/rootspeak-user prompt --login
		end
	end
end
