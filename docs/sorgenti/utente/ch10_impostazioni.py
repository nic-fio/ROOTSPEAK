import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import arrow, box, c, code, fig, note, p, steps, table, term, text, tip, warn  # noqa: E402
from _aiuti import rif  # noqa: E402

S1 = p("AMS has two settings, and they live in a single file, " + c("/etc/ams/ams.conf") + ". They are fine as "
       "installed; change them only for particular needs.", lead=True) + \
    code("""# AMS - Advanced Messaging System: configurazione
# File di dati, non uno script: righe CHIAVE=valore con numeri interi positivi.
# Chiavi sconosciute e valori non validi sono ignorati.

# Dopo quanti minuti riproporre un messaggio rimandato dall'utente
AMS_REMIND_MINUTES=30

# Ogni quanti secondi l'agente del desktop ricontrolla i messaggi
# (i nuovi messaggi lo svegliano comunque subito)
AMS_AGENT_POLL=60""", "conf", "/etc/ams/ams.conf, as AMS installs it") + \
    table(["Setting", "Default", "What it decides"], [
        [c("AMS_REMIND_MINUTES"), c("30"), "after how many minutes a postponed message is asked again, in the "
         "terminal and on the desktop; it is also the number written in «La domanda verrà riproposta tra 30 "
         "minuti» (“You will be asked again in 30 minutes”)"],
        [c("AMS_AGENT_POLL"), c("60"), "how often, in seconds, the desktop agent checks the messages again as a "
         "safeguard. New messages and reminders arrive at once anyway. Lower values use slightly more "
         "battery"],
    ], "«TAB» — The settings") + \
    table(["File rule", "Example"], [
        ["one line per setting, " + c("CHIAVE=valore"), c("AMS_REMIND_MINUTES=15")],
        ["only integers greater than zero, at most six digits", c("AMS_AGENT_POLL=120")],
        ["spaces do not matter", c("AMS_REMIND_MINUTES = 15")],
        ["anything after " + c("#") + " is a comment", c("AMS_AGENT_POLL=30  # laptops on charge")],
        ["invalid lines, unknown keys and wrong values are ignored: the default applies",
         c("AMS_REMIND_MINUTES=half-an-hour") + " → 30"],
    ], "«TAB» — How the file is written") + \
    note("the file contains only data: it is not a script and is never executed. A typing mistake does not stop "
         "AMS, it only makes it use the default value.", "Data only.")

EFFETTO = fig(
    '<line x1="60" y1="120" x2="860" y2="120" stroke="#94a3b8" stroke-width="2"/>'
    + text(60, 146, "postponed", 11.5, "#475569", "600") + text(620, 146, "+ AMS_REMIND_MINUTES", 11.5, "#92400e", "700")
    + '<path d="M62 100 H 618" stroke="#d97706" stroke-width="2" stroke-dasharray="5 4"/>'
    + box(630, 76, 230, 40, "the message comes back", "at the next prompt, or in the dialog", "amber", 12)
    + '<line x1="60" y1="240" x2="860" y2="240" stroke="#94a3b8" stroke-width="2"/>'
    + "".join(f'<line x1="{x}" y1="232" x2="{x}" y2="248" stroke="#0050C0" stroke-width="2"/>' for x in (100, 300, 500, 700))
    + text(400, 272, "desktop agent checks, every AMS_AGENT_POLL seconds", 11.5, "#1e40af", "600")
    + box(360, 176, 180, 40, "ams send or remind", "wakes it at once", "green", 12)
    + arrow(450, 218, 450, 238, "#16a34a"),
    900, 292, "«FIG» — What the two settings control", "Postponement and checks")

S2 = EFFETTO + steps([
    "Open the file with administrator rights:" + term("admin@server:~$ sudo nano /etc/ams/ams.conf"),
    "Change the value, for example " + c("AMS_REMIND_MINUTES=15") + ", save and exit.",
    "There is nothing to restart: the value applies at once to terminals (from the next prompt) and to the desktop "
    "from the agent's next check.",
]) + table(["Need", "Setting"], [
    ["urgent notices: ask again more often", c("AMS_REMIND_MINUTES=10")],
    ["users complaining about the requests", c("AMS_REMIND_MINUTES=60") + " or more"],
    ["battery-powered laptops", c("AMS_AGENT_POLL=300") + ": new messages still arrive at once"],
], "«TAB» — Recommended values") + \
    warn("the file must remain owned by root and writable only by root, as the installation leaves it: all users "
         "read it, to know when to ask the messages again.", "Permissions.") + \
    note("an AMS upgrade does not overwrite " + c("/etc/ams/ams.conf") + "; " + c("./install.sh --purge")
         + " deletes it.", "Upgrades.")

S3 = p("A few environment variables change the behaviour of " + c("ams") + " for the administrator who sets them. "
       "Since " + c("ams") + " always re-runs itself with sudo, they only get through if sudo keeps them.",
       lead=True) + \
    table(["Variable", "Effect", "Default"], [
        [c("NO_COLOR"), "if set, TUI and built-in help without colours", "colours"],
        [c("PAGER"), "the program that pages the built-in help in small terminals (" + rif(9, 3) + ")", c("less")],
        [c("VISUAL") + ", " + c("EDITOR"), "the editor opened with " + "Ctrl+E" + " in the new message (" + rif(5, 5)
         + ")", c("nano") + ", then " + c("vi")],
        [c("LANG") + " and similar", "the language of " + c("ams") + " and of the TUI", "kept by sudo in the "
         "usual configurations"],
    ], "«TAB» — Environment variables") + \
    p("To have sudo keep them, add a line to its settings, always with " + c("visudo") + ":") + \
    term('admin@server:~$ sudo visudo -f /etc/sudoers.d/ams\n'
         '# in the file:\n'
         'Defaults env_keep += "NO_COLOR PAGER VISUAL EDITOR"', "Keeping the variables through sudo") + \
    warn("this line applies to every command run with sudo, not just " + c("ams") + ". Add only the variables you "
         "need.", "For all of sudo.") + \
    tip("the editor opened by " + c("ams") + " runs with the administrator's identity, not as root: keeping "
        + c("EDITOR") + " does not give it extra powers.", "Editor and security.")

CHAPTER = ("Settings", [
    ("The settings file", S1),
    ("Changing a setting", S2),
    ("Colours, pager and editor", S3),
])
