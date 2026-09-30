from build import arrow, box, c, fig, note, p, path, table, text, ul, zone


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">chapter {n}{"." + str(s) if s else ""}</a>'


RISOLVI = fig(
    box(20, 110, 180, 56, "--to DEST", "mario,@sviluppo,online", "dark")
    + box(250, 110, 130, 56, "strtok_r", "splits on commas", "navy")
    + box(440, 20, 200, 44, "all", "utenti_umani", "blue", 12)
    + box(440, 74, 200, 44, "online", "utenti_online", "blue", 12)
    + box(440, 128, 200, 44, "@group", "membri_gruppo", "blue", 12)
    + box(440, 182, 200, 44, "name", "getpwnam: must exist", "blue", 12)
    + box(700, 110, 180, 56, "list", "no duplicates, sorted", "green")
    + arrow(202, 138, 248, 138)
    + arrow(382, 130, 438, 42) + arrow(382, 134, 438, 96) + arrow(382, 142, 438, 150) + arrow(382, 146, 438, 204)
    + arrow(642, 42, 698, 128) + arrow(642, 96, 698, 134) + arrow(642, 150, 698, 142) + arrow(642, 204, 698, 150)
    + text(540, 250, "unknown group or user: die, no message created", 11, "#b91c1c", "600"),
    900, 266, "«FIG» — From --to to the list of recipients (risolvi_destinatari)", "Resolving the recipients")

S1 = p(c("risolvi_destinatari") + " in " + c("src/ams.c") + " turns the value of " + c("--to") + " into the list "
       "of recipients. It does so <b>before</b> taking a number and before writing anything: an error here leaves "
       "no trace in the message store.", lead=True) + RISOLVI + ul([
    "The value is split on commas; each part is one of the four forms in the figure. Empty parts (two commas in a "
    "row) are skipped; a space, on the other hand, becomes part of the name, which therefore does not exist: this is "
    "why the help asks for names separated by commas without spaces.",
    "An unknown user or group ends with " + c("die") + " («utente inesistente: pippo» (“no such user: pippo”), «gruppo "
    "inesistente: x» (“no such group: x”)); for the user this is scenario B6 on the test machine.",
    "Duplicates are removed along the way (scenario B2) and the final list is in alphabetical order: this is the "
    "order of the deliveries and of " + c("sent/ID/recipients") + ".",
    "An empty list (for example a group with no members) ends with «nessun destinatario» (“no recipients”) (scenario B7).",
    "An explicit name may also be a system account or root: the filter on human users applies only to "
    + c("all") + " and " + c("online") + ".",
])

S2 = table(["Function (src/sessioni.c)", "What it returns", "Source"], [
    [c("utenti_umani"), "the users with a UID between " + c("UID_MIN") + " and " + c("UID_MAX") + " and a shell "
     "that does not end in " + c("nologin") + " or " + c("false"), c("/etc/login.defs") + " (defaults 1000 and 60000), "
     + c("getpwent")],
    [c("utenti_online"), "the human users with at least one logind session of class " + c("user"),
     c("sd_get_sessions") + ", " + c("sd_session_get_class") + ", " + c("sd_session_get_uid")],
    [c("membri_gruppo G"), "the members listed in the group plus the users whose primary group is G; false "
     "if the group does not exist", c("getgrnam") + ", " + c("getpwent")],
    [c("terminali_utente U"), "U's pseudo-terminals and the consoles of U's text sessions", "see " + cap(6, 3)],
    [c("sessione_grafica U"), "true if U has a session of type " + c("x11") + " or " + c("wayland"),
     c("sd_session_get_type")],
], "«TAB» — Recipients and sessions") + \
    p("Everything goes through the system interfaces (" + c("getpwent") + ", " + c("getgrnam") + ", libsystemd's "
      + c("sd-login") + " library): LDAP users or users from other name services work if the system exposes them "
      "this way. " + c("all") + " excludes root and system accounts because they have a UID below " + c("UID_MIN")
      + " or a non-login shell (scenario B4).") + \
    note("<b>online</b> counts the sessions of class " + c("user") + " and then filters them against the human "
         "users: the test VM showed that root and logged-in system accounts (for example the graphical login "
         "manager) ended up among the recipients (scenario B5). They are now excluded even when logged in.")

TERM = fig(
    zone(20, 44, 400, 200, "Pseudo-terminals · /dev/pts")
    + box(44, 84, 170, 56, "/dev/pts/N", "owner = U?", "blue")
    + box(230, 84, 170, 56, "ssh, emulators", "tmux, desktop terminals", "soft", 12)
    + text(220, 180, "lstat: character device owned by U", 11, "#475569")
    + text(220, 198, "names made only of digits", 11, "#475569")
    + zone(480, 44, 400, 200, "Consoles · logind")
    + box(504, 84, 170, 56, "U's session", "type tty", "navy")
    + box(690, 84, 170, 56, "/dev/ttyN", "sd_session_get_tty", "blue")
    + text(680, 180, "only names «tty» + digits", 11, "#475569")
    + arrow(676, 112, 688, 112)
    + box(300, 262, 300, 48, "terminali_utente(U)", "no duplicates, sorted", "green", 12)
    + arrow(220, 216, 380, 260, "#16a34a") + arrow(680, 216, 520, 260, "#16a34a"),
    900, 326, "«FIG» — The two sources of a user's terminals", "Where the terminals are")

S3 = p(c("terminali_utente") + " collects the terminals to which " + c("ams send") + " writes the text when "
       "sending. There are two sources, because neither is enough on its own.", lead=True) + TERM + table(["Source", "What it finds",
                                                                                         "What it does not find"], [
    [c("/dev/pts/N") + " owned by U", "ssh with a terminal, desktop terminal emulators, tmux and screen",
     "text consoles; terminals opened with " + c("su") + " (they stay owned by whoever opened them)"],
    ["U's logind sessions of type " + c("tty"), "text consoles (" + c("tty1") + "…" + c("tty6") + ")",
     "pseudo-terminals that are not a session (tmux, emulators)"],
], "«TAB» — The sources of terminals") + ul([
    "Here the owner of " + c("/dev/pts/N") + " serves only to <b>find</b> the candidates: at the moment of writing, "
    + c("scrivi_terminale") + " reopens the terminal and checks the owner of the opened terminal (" + cap(8, 4)
    + "). The name " + c("/dev/pts/N") + " does not identify a session: between the search and the write it might "
    "pass to another user.",
    "In test mode there is a single «terminal»: the file " + c("AMS_TEST_TTY") + ", if set.",
    "An ssh session without a terminal (" + c("scp") + ", remote commands) and services have no terminals: they are "
    "not touched (scenario C3).",
])

S4 = p(c("sessione_grafica") + " tells whether a user has an X11 or Wayland session open. It is needed in two "
       "places, with the same code.", lead=True) + table(["Who calls it", "Why"], [
    [c("ams send") + ", through " + c("sveglia_agente"), "only users with an open desktop receive the wake-up or a "
     "new agent (" + cap(8, 5) + ")"],
    [c("ams-user agent"), "the agent stays alive as long as the user has a graphical session, then exits (" + cap(12, 1) + ")"],
], "«TAB» — Who uses sessione_grafica") + \
    p("A user with several graphical sessions (for example a local desktop and a remote one that creates a new "
      "session) still has a single agent: the lock " + c("ams-agent.lock") + " lives in " + c("$XDG_RUNTIME_DIR")
      + ", which is unique per user (" + cap(12, 1) + "). The behaviour with several simultaneous desktops of the "
      "same user has not been tested.")

CHAPTER = ("Recipients and sessions", [
    ("From --to to the list", S1),
    ("Human users, logged-in users, groups", S2),
    ("A user's terminals", S3),
    ("The graphical session", S4),
])
