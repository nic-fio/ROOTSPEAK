import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import arrow, box, c, code, fig, note, p, steps, table, term, text, tip, warn  # noqa: E402
from _helpers import ref  # noqa: E402

S1 = p("RootSpeak has two settings, and they live in a single file, " + c("/etc/rootspeak/rootspeak.conf") + ". They are fine as "
       "installed; change them only for particular needs.", lead=True) + \
    code("""# RootSpeak - Advanced Messaging System for Linux: configuration
# A data file, not a script: KEY=value lines with positive whole numbers.
# Unknown keys and invalid values are ignored.

# After how many minutes a message postponed by the user is shown again
RSPEAK_REMIND_MINUTES=30

# Every how many seconds the desktop agent checks the messages again
# (new messages wake it at once anyway)
RSPEAK_AGENT_POLL=60""", "conf", "/etc/rootspeak/rootspeak.conf, as RootSpeak installs it") + \
    table(["Setting", "Default", "What it decides"], [
        [c("RSPEAK_REMIND_MINUTES"), c("30"), "after how many minutes a postponed message is asked again, in the "
         "terminal and on the desktop; it is also the number written in “You will be "
         "asked again in 30 minutes”"],
        [c("RSPEAK_AGENT_POLL"), c("60"), "how often, in seconds, the desktop agent checks the messages again as a "
         "safeguard. New messages and reminders arrive at once anyway. Lower values use slightly more "
         "battery"],
    ], "«TAB» — The settings") + \
    table(["File rule", "Example"], [
        ["one line per setting, " + c("KEY=value"), c("RSPEAK_REMIND_MINUTES=15")],
        ["only whole numbers greater than zero, at most six digits", c("RSPEAK_AGENT_POLL=120")],
        ["spaces do not matter", c("RSPEAK_REMIND_MINUTES = 15")],
        ["anything after " + c("#") + " is a comment", c("RSPEAK_AGENT_POLL=30  # laptops on charge")],
        ["invalid lines, unknown keys and wrong values are ignored: the default applies",
         c("RSPEAK_REMIND_MINUTES=half-an-hour") + " → 30"],
    ], "«TAB» — How the file is written") + \
    note("the file contains only data: it is not a script and is never executed. A typing mistake does not stop "
         "RootSpeak, it only makes it use the default value.", "Data only.")

EFFETTO = fig(
    '<line x1="60" y1="120" x2="860" y2="120" stroke="#94a3b8" stroke-width="2"/>'
    + text(60, 146, "postponed", 11.5, "#475569", "600") + text(620, 146, "+ RSPEAK_REMIND_MINUTES", 11.5, "#92400e", "700")
    + '<path d="M62 100 H 618" stroke="#d97706" stroke-width="2" stroke-dasharray="5 4"/>'
    + box(630, 76, 230, 40, "the message comes back", "at the next prompt, or in the dialog", "amber", 12)
    + '<line x1="60" y1="240" x2="860" y2="240" stroke="#94a3b8" stroke-width="2"/>'
    + "".join(f'<line x1="{x}" y1="232" x2="{x}" y2="248" stroke="#0050C0" stroke-width="2"/>' for x in (100, 300, 500, 700))
    + text(400, 272, "desktop agent checks, every RSPEAK_AGENT_POLL seconds", 11.5, "#1e40af", "600")
    + box(360, 176, 180, 40, "rspeak send or remind", "wakes it at once", "green", 12)
    + arrow(450, 218, 450, 238, "#16a34a"),
    900, 292, "«FIG» — What the two settings control", "Postponement and checks")

S2 = EFFETTO + steps([
    "Open the file with administrator rights:" + term("admin@server:~$ sudo nano /etc/rootspeak/rootspeak.conf"),
    "Change the value, for example " + c("RSPEAK_REMIND_MINUTES=15") + ", save and exit.",
    "There is nothing to restart: the value applies at once to terminals (from the next prompt) and to the desktop "
    "from the agent's next check.",
]) + table(["Need", "Setting"], [
    ["urgent notices: ask again more often", c("RSPEAK_REMIND_MINUTES=10")],
    ["users complaining about the requests", c("RSPEAK_REMIND_MINUTES=60") + " or more"],
    ["battery-powered laptops", c("RSPEAK_AGENT_POLL=300") + ": new messages still arrive at once"],
], "«TAB» — Recommended values") + \
    warn("the file must remain owned by root and writable only by root, as the installation leaves it: all users "
         "read it, to know when to ask the messages again.", "Permissions.") + \
    note("a RootSpeak upgrade does not overwrite " + c("/etc/rootspeak/rootspeak.conf") + "; " + c("./install.sh --purge")
         + " deletes it.", "Upgrades.")

S3 = p("A few environment variables change the behaviour of " + c("rspeak") + " for the administrator who sets them. "
       "Since " + c("rspeak") + " always re-runs itself with sudo, they only get through if sudo keeps them.",
       lead=True) + \
    table(["Variable", "Effect", "Default"], [
        [c("NO_COLOR"), "if set, TUI and built-in help without colours", "colours"],
        [c("PAGER"), "the program that pages the built-in help in small terminals (" + ref(9, 3) + ")", c("less")],
        [c("VISUAL") + ", " + c("EDITOR"), "the editor opened with " + "Ctrl+E" + " in the new message (" + ref(5, 5)
         + ")", c("nano") + ", then " + c("vi")],
    ], "«TAB» — Environment variables") + \
    p("To have sudo keep them, add a line to its settings, always with " + c("visudo") + ":") + \
    term('admin@server:~$ sudo visudo -f /etc/sudoers.d/rootspeak\n'
         '# in the file:\n'
         'Defaults env_keep += "NO_COLOR PAGER VISUAL EDITOR"', "Keeping the variables through sudo") + \
    warn("this line applies to every command run with sudo, not just " + c("rspeak") + ". Add only the variables you "
         "need.", "For all of sudo.") + \
    tip("the editor opened by " + c("rspeak") + " runs with the administrator's identity, not as root: keeping "
        + c("EDITOR") + " does not give it extra powers.", "Editor and security.")

CHAPTER = ("Settings", [
    ("The settings file", S1),
    ("Changing a setting", S2),
    ("Colours, pager and editor", S3),
])
