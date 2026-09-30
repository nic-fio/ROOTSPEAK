# AMS - Advanced Messaging System for linux
# Texts of the built-in guide (ams --help) in English. Every language has the
# same entries (tools/check-docs.py checks it).
# shellcheck disable=SC2034

# Entries "label¦description".
AMS_HELP_COMMANDS=(
	"send [options] [TEXT]¦Sends a message to the recipients given with --to. Without TEXT or --file, the text is read from stdin."
	"list¦Lists the messages sent, with how many recipients have confirmed each one."
	"status ID¦Shows the text of the message and the state of each recipient: sent, delivered (in their mailbox) or confirmed, with date, time and channel."
	"revoke ID¦Revokes a message: whoever has not seen it yet will not see it, and dialogs and questions still open close by themselves."
	"log ID¦Shows the history of the message from the system log: sending, deliveries, postponements, confirmations and revocation, with date and time."
	"purge DURATION¦Deletes the messages sent more than DURATION ago (for example 90d), with the copies and confirmations in the users' mailboxes; the events stay in the system log."
	"version¦Shows the AMS version."
	"help, --help, -h¦Shows this guide. «ams» without arguments opens it too."
)

AMS_HELP_OPTIONS=(
	"--to DEST¦Recipients, separated by commas without spaces: a user (mario), a Unix group (@developers), all (every human user) or online (only those logged in now)."
	"--title TITLE¦Title shown in the message header and in the desktop dialog."
	"--expires DURATION¦Expiry, after which the message is no longer shown: 30m, 2h, 3d or a date and time (\"2026-10-04 12:00\")."
	"--file FILE¦Reads the message text from FILE."
)

AMS_HELP_EXAMPLES=(
	"ams send --to mario \"Your account expires on Friday.\"¦Message with read confirmation to a single user."
	"ams send --to @developers --title Maintenance --file notice.txt¦Text taken from a file, with a title, to every member of the developers group."
	"ams send --to online --expires 15m \"Reboot at 13:00.\"¦Urgent notice to whoever is logged in now; after 15 minutes it is no longer shown or asked about."
	"ams send --to all --expires 3d \"New password policy.\"¦To every user; after three days it stops being shown."
	"ams list¦Which messages were sent and how many confirmations they have."
	"ams status 12¦Who confirmed message 12, when and from where."
	"ams log 12¦The history of message 12: sending, deliveries, postponements, confirmations."
	"ams purge 90d¦Deletes the messages older than 90 days, with copies and confirmations."
	"ams revoke 12¦Revokes message 12."
)

AMS_HELP_FILES=(
	"/etc/ams/ams.conf¦Configuration: minutes before a postponed message is asked about again, check interval of the desktop agent."
	"/var/lib/ams/¦The messages: sent/ (reference copies, root only) and users/USER/ (each user's mailbox, readable only by them and by root)."
	"sudo journalctl -t ams¦The system log: sending, deliveries, confirmations and revocations."
	"/usr/local/share/doc/ams/AMS_Manuale_Utente.html¦The complete user manual (in Italian), to open in a browser."
)

AMS_HELP_DESCRIPTION="AMS lets administrators send text messages to the users of the machine and know \
who has read them. Messages appear in terminals (console, ssh, desktop terminals, tmux) and on the \
desktop, in a dialog with the buttons «I have read it» and «Later»; whoever is not logged in finds \
them at the next login. Every message asks for a read confirmation and AMS asks again until the user \
gives it, without ever blocking their work. Each user sees AMS in their own language. The command is \
reserved to administrators (sudo or wheel group) and re-runs itself with sudo."

AMS_HELP_SYNOPSIS=(
	"ams send --to DEST [options] [TEXT]"
	"ams list"
	"ams status ID"
	"ams revoke ID"
	"ams log ID"
	"ams purge DURATION"
	"ams version"
)

declare -gA AMS_HELP_L=(
	[title]="ams manual"
	[name]="ams — sends messages to the users of the machine and tracks their read confirmation"
	[short]="ams — messages to users with read confirmation"
	[h_name]="NAME"
	[h_synopsis]="SYNOPSIS"
	[h_description]="DESCRIPTION"
	[h_commands]="COMMANDS"
	[h_options]="SEND OPTIONS"
	[h_examples]="EXAMPLES"
	[h_files]="FILES"
	[h_environment]="ENVIRONMENT"
	[h_exit]="EXIT STATUS"
	[h_see]="SEE ALSO"
	[pager]="Pager used to page this guide when the terminal is too small for the interactive one (default: less). Like NO_COLOR, it reaches ams only if sudo keeps it (env_keep in sudoers)."
	[no_color]="If set, disables colours."
	[exit0]="Completed successfully."
	[exit1]="Error: the error message, starting with «ams:», says which."
	[see]="wall(1), write(1), and the user manual (in Italian) in /usr/local/share/doc/ams/AMS_Manuale_Utente.html"
	[manual]="AMS %s · complete manual (in Italian): /usr/local/share/doc/ams/AMS_Manuale_Utente.html"
	[tabs]="Info Commands Options Examples Files"
	[t_commands]="Commands"
	[t_options]="Send options"
	[t_examples]="Examples"
	[t_files]="Files and log"
	[frame]="ams — guide"
	[lines]="lines %s-%s/%s"
	[hint]="←/→ tabs · ↑/↓ scroll · PgUp/PgDn · g/G · q quit"
)
