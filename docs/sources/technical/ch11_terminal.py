from build import arrow, box, c, code, diamond, fig, flow, note, p, seq, table, term, text, ul


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">chapter {n}{"." + str(s) if s else ""}</a>'


S1 = p("Each shell has its own hook, installed where that shell reads it. They all do the same thing: if the "
       "mailbox contains messages, they run " + c("rootspeak-user prompt") + ", right at login and then before every "
       "prompt.", lead=True) + table(["Shell", "Installed file", "Read by", "When it asks"], [
    ["bash", c("/usr/local/lib/rootspeak/rootspeak.bash"), c("/etc/profile.d/rootspeak.sh") + " (login shells) and "
     + c("/etc/bash.bashrc") + " (the others)", "at login and at every prompt (" + c("PROMPT_COMMAND") + ")"],
    ["zsh", c("/usr/local/lib/rootspeak/rootspeak.zsh"), "a line in " + c("/etc/zsh/zshrc") + " (or " + c("/etc/zshrc") + ")",
     "at login and at every prompt (" + c("precmd") + ")"],
    ["fish", c("/etc/fish/conf.d/rootspeak.fish"), "fish itself, at startup", "at login and at every prompt ("
     + c("fish_prompt") + " event)"],
    ["sh, dash, ksh…", c("/etc/profile.d/rootspeak.sh"), c("/etc/profile") + ", in login shells", "only at login"],
], "«TAB» — The shell hooks") + \
    p("The message text reaches the terminal at send time whatever the shell: root writes it, not the shell "
      "(" + cap(8, 4) + "). dash, ksh and similar shells have no place to hook into before the prompt: the "
      "question arrives at the next login, or through the desktop dialog (scenarios K of the test machine). "
      + c("profile.d/rootspeak.sh") + " is written in plain sh because every shell reads it: it hands bash over to "
      + c("rootspeak.bash") + ", leaves zsh to its own hook and asks the others at login.") + \
    note("zsh reads the system-wide zshrc: if it is installed after RootSpeak, just run " + c("install.sh")
         + " again to add the line. fish reads " + c("conf.d") + " even if it arrives later.")

S2 = flow([("interactive bash", "$- contains i", "dark"), ("profile.d/rootspeak.sh", "→ rootspeak.bash, once", "blue"),
           ("PROMPT_COMMAND", "+ __rspeak_prompt", "blue"), ("mailbox empty?", "compgen -G", "navy"),
           ("rootspeak-user", "prompt, only if needed", "light")], "«FIG» — From the hook to the question, in bash") + \
    code("""__rspeak_prompt() {
	local s=$?
	# A check without external processes: with an empty mailbox it costs nothing.
	if compgen -G "$__RSPEAK_INBOX/[0-9]*" >/dev/null; then
		@LIBDIR@/rootspeak-user prompt
	fi
	return $s
}""", "bash", "etc/rootspeak.bash (excerpt)") + ul([
    "The hook acts only in an interactive shell, if " + c("rootspeak-user") + " exists, and once per shell "
    "(variable " + c("__RSPEAK_HOOK") + ", in fish " + c("__rspeak_hook") + ").",
    "It adds " + c("__rspeak_prompt") + " to " + c("PROMPT_COMMAND") + ": as an element if it is an array (bash 5.1 and "
    "later), at the front if it is a string. It preserves " + c("$?") + ": the user's prompt sees the result of their "
    "last command.",
    "The mailbox check uses " + c("compgen -G") + ", a bash builtin that starts no processes: "
    "with an empty mailbox the prompt costs nothing. zsh does the same with the " + c("(N)") + " glob, fish with "
    + c("string match") + " on the names (fish globs have no " + c("[0-9]") + ").",
    "In a login shell it calls " + c("rootspeak-user prompt --login") + " straight away: the message appears before the "
    "first prompt (scenario C1b: about 0.3 s after login).",
    "On Debian, interactive non-login shells (the desktop terminals) do not read " + c("/etc/profile.d")
    + ": the hook is also called from " + c("/etc/bash.bashrc") + " (" + cap(3, 3) + ").",
])

ROUND = fig(
    box(20, 40, 170, 56, "pending_n", "inbox in numeric order", "dark")
    + diamond(360, 68, 240, 72, "recently postponed?", "amber")
    + box(570, 40, 160, 56, "reminder", "counted, not asked", "soft")
    + box(270, 160, 180, 56, "shows and asks", "text, then [y/N]", "blue")
    + box(560, 160, 170, 56, "result", "confirm · postpone · …", "green")
    + arrow(192, 68, 238, 68) + arrow(482, 68, 568, 68, "#d97706", False, "yes, not at login", 525, 58)
    + arrow(360, 106, 360, 158, "#475569", False, "no", 376, 134)
    + arrow(452, 188, 558, 188)
    + text(815, 60, "at the end, if there are any:", 11, "#475569")
    + text(815, 78, "“You have N messages", 11, "#92400e", "600")
    + text(815, 94, "from the administrator", 11, "#92400e", "600")
    + text(815, 110, "to confirm.”", 11, "#92400e", "600")
    + text(105, 130, "confirmed and expired", 11, "#475569")
    + text(105, 146, "move to read/", 11, "#475569"),
    900, 236, "«FIG» — rootspeak-user prompt, for each message in the mailbox", "The rootspeak-user prompt loop")

S3 = p(c("rootspeak-user prompt") + " in " + c("src/rootspeak-user.c") + " takes the messages in the mailbox in numeric "
       "order. If stdin is not a terminal it does nothing; the confirmation channel is the terminal name ("
       + c("terminal pts/3") + ").", lead=True) + ROUND + ul([
    c("pending_n") + " lists " + c("inbox/") + " (only names made of digits, and regular files). A message whose "
    "confirmation is already present, because of an interruption between the confirmation and the move, goes to "
    + c("read/") + " without asking; an expired one goes to " + c("read/") + " without a confirmation.",
    "A message postponed less than " + c("RSPEAK_REMIND_MINUTES") + " minutes ago (modification time of "
    + c("state/ID.term") + ") is not asked about: it is counted, and at the end the one-line reminder appears. With "
    + c("--login") + " the postponement does not apply.",
]) + table(["Result of ask", "What it does", "Prints"], [
    ["0 · “y” or “Y”", c("confirm(ID, \"terminal pts/N\")"), "“[RootSpeak] Confirmed.”; or “[RootSpeak] The message has "
     "expired: the confirmation was not recorded.”, “[RootSpeak] The administrator has revoked the message.”, "
     "“[RootSpeak] The confirmation could not be recorded: you will be asked again.”"],
    ["1 · anything else, or just Enter", c("postpone(ID, \"term\")") + ": touches " + c("state/ID.term") + ", event "
     + c("POSTPONED"), "“[RootSpeak] You will be asked again in 30 minutes.”"],
    ["2 · confirmed elsewhere", "moves to " + c("read/"), "“[RootSpeak] Message already confirmed elsewhere (for example "
     "on the desktop).”"],
    ["3 · revoked", "nothing", "“[RootSpeak] The administrator has revoked the message.”"],
    ["4 · expired while the question was open", "moves to " + c("read/"), "“[RootSpeak] The message has expired.”"],
], "«TAB» — The results of the question") + term(
    "mario@server:~$ \n"
    "── RootSpeak · Message from the administrator · Maintenance · 01/10 10:49 ──\n"
    "On Saturday from 8 am to 12 noon the server will be off for disk maintenance.\n"
    "────────────────────────────────────────\n"
    "[RootSpeak] Do you confirm you have read the message? [y/N] y\n"
    "[RootSpeak] Confirmed.\n"
    "mario@server:~$ ", "The question at the prompt, answered with y") + \
    note(c("rootspeak-user") + " runs inside the user's prompt: it never ends with an error that would disrupt the "
         "shell, and any problem it meets (unreadable mailbox, no terminal) turns into doing nothing.")

ASK = seq([("User", "keyboard", "dark"), ("ask", "poll 1 s on /dev/tty", "blue"),
           ("Mailbox", "users/U", "soft")], [
    (1, 0, "[RootSpeak] Do you confirm…? [y/N]"),
    ("note", 1, "waits at most 1 second".ljust(24)),
    (1, 2, "acks/ID? inbox/ID? expired?"),
    ("note", 1, "nothing new: starts over".ljust(27)),
    ("sep", "meanwhile: user confirms on desktop".ljust(37)),
    (1, 2, "acks/ID exists"),
    (1, 0, "result 2: “confirmed elsewhere”", True),
], "«FIG» — The question notices what happens elsewhere", "A question that checks every second")

S4 = p(c("ask") + " waits for the answer on " + c("/dev/tty") + " with " + c("poll") + ", one second at a time, "
       "then reads it with " + c("read") + ". At every second without an answer it checks the mailbox: if the "
       "confirmation has appeared, the user confirmed elsewhere; if the message has disappeared, it was revoked; if "
       "it has expired, the question stops.", lead=True) + ASK + ul([
    "The terminal stays in canonical mode: whatever the user is typing stays in the terminal's buffer and is not "
    "lost from one second to the next.",
    "The question closes within about a second: confirmation from another session (scenario C4b, 0.95 s), "
    "revocation (scenario E3, 1.0 s), expiry (" + c("tests/engine.sh") + ", group 4).",
    "Without " + c("/dev/tty") + " (no controlling terminal) the answer counts as “no”: the message stays and comes "
    "back later.",
    "Only the first character of the answer is checked: only " + c("y") + " and " + c("Y") + " mean yes. RootSpeak "
    "speaks English, whatever the language of the session.",
])

CHAPTER = ("Receiving in the terminal", [
    ("The shell hooks", S1),
    ("From the hook to the question", S2),
    ("rootspeak-user prompt", S3),
    ("The question and the wait", S4),
])
