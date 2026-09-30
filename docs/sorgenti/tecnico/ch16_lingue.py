from build import arrow, box, c, code, diamond, fig, flow, note, p, path, table, text, ul, warn


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">chapter {n}{"." + str(s) if s else ""}</a>'


LINGUE = fig(
    box(20, 50, 210, 54, "administrator", "their environment, after sudo", "dark")
    + box(20, 130, 210, 54, "user's terminal", "/proc/PID/environ", "dark")
    + box(20, 210, 210, 54, "shell, agent", "their environment", "dark")
    + box(20, 290, 210, 54, "journal", "/etc/default/locale", "dark")
    + box(330, 170, 200, 54, "lingua_scegli", "gettext rules", "navy")
    + box(640, 80, 240, 54, "LINGUA/LC_MESSAGES/ams.mo", "read by lingua.c", "blue", 12)
    + box(640, 170, 240, 54, "English", "the texts in the code", "light")
    + box(640, 260, 240, 54, "message text", "never translated", "soft")
    + arrow(232, 77, 328, 185) + arrow(232, 157, 328, 192) + arrow(232, 237, 328, 204) + arrow(232, 317, 328, 216)
    + arrow(532, 188, 638, 110, "#0050C0", False, "if present", 590, 138) + arrow(532, 200, 638, 198, "#475569", False,
                                                                           "otherwise", 590, 190),
    900, 362, "«FIG» — Where the reader's language comes from, and where the texts are", "Everyone in their own language")

S1 = p("Everyone reads AMS in their own language: the administrator the commands, each user the question, the "
       "dialog and the buttons. The text of the messages is never translated. Today AMS has Italian and English; "
       "English is the language of the texts in the code and the fallback language.", lead=True) + LINGUE + table(["Who reads", "Language",
                                                                                     "Taken from"], [
    ["the administrator: output, errors, help, TUI", "their own", "their environment: sudo usually keeps "
     + c("LANG") + ", " + c("LANGUAGE") + " and " + c("LC_*")],
    ["the user, at sending time: the header in the terminal", "the terminal's", "the environment of the first "
     "process of the terminal, usually the shell; if root cannot read it, the user reads it themselves (" + cap(7, 4) + "); "
     "with no processes, the system language"],
    ["the user, at the prompt: question and answers", "the shell's", "the environment of " + c("ams-user prompt")],
    ["the user, on the desktop: dialog, buttons, notification", "the graphical session's", "the agent's environment"],
    ["the journal (" + c("MESSAGE") + ")", "the system's", c("/etc/default/locale") + " or "
     + c("/etc/locale.conf")],
    [c("ams log") + ", TUI history", "the reader's", "rewritten from the " + c("AMS_*") + " fields (" + cap(18, 4)
     + ")"],
], "«TAB» — Who reads in which language") + ul([
    "What is saved stays <b>language-neutral</b>: the channel of a confirmation is " + c("terminale pts/N") + " or "
    + c("desktop") + " and is translated only when shown (" + c("canale_testo") + "); events are rewritten from "
    "their fields. An administrator using English reads «confirmed on 30/09 17:10 (terminal pts/19)» for the same "
    "confirmation that one using Italian reads as «confermato il … (terminale pts/19)» (scenario L3).",
    "The question accepts " + c("s") + ", " + c("S") + ", " + c("y") + " and " + c("Y") + " in every language (scenario L2).",
])

SCELTA = fig(
    box(20, 40, 230, 56, "LC_ALL › LC_MESSAGES › LANG", "the first one set", "dark", 12)
    + diamond(390, 68, 190, 64, "C or POSIX?", "navy")
    + box(310, 150, 160, 48, "English", "LANGUAGE ignored", "light", 12)
    + box(530, 40, 170, 56, "LANGUAGE list", "de:it → try de, then it", "blue", 12)
    + box(740, 40, 140, 56, "language of LANG", "it_IT.UTF-8 → it", "blue", 12)
    + box(620, 150, 260, 48, "first one with a .mo wins", "otherwise English", "green", 12)
    + arrow(252, 68, 293, 68)
    + arrow(390, 102, 390, 148, "#475569", False, "yes", 404, 126)
    + arrow(487, 68, 528, 68, "#0050C0", False, "no", 507, 58)
    + arrow(702, 68, 738, 68)
    + arrow(810, 98, 810, 148, "#16a34a") + arrow(615, 98, 680, 148, "#16a34a"),
    900, 222, "«FIG» — lingua_scegli, the gettext rules", "Choosing the language")

S2 = p(c("lingua_scegli") + " in " + c("src/lingua.c") + " follows the gettext rules, with one restriction: only "
       "codes of 2 or 3 lowercase letters are accepted.", lead=True) + SCELTA + ul([
    "What counts is the first one set among " + c("LC_ALL") + ", " + c("LC_MESSAGES") + " and " + c("LANG") + ". If it is "
    + c("C") + " or " + c("POSIX") + " (including " + c("C.UTF-8") + "), or empty, English applies and " + c("LANGUAGE")
    + " does not count.",
    "Otherwise the " + c("LANGUAGE") + " list (colon-separated) is tried first, then the language of the chosen "
    "value: the part before " + c("_") + ", " + c(".") + ", " + c("@") + ". The first language that has an "
    "installed catalog wins (English is always available); if none does, English.",
    "A value that is not a code of 2 or 3 lowercase letters (" + c("../../tmp/x") + ", " + c("a/b") + ") never leads "
    "to reading a file: the catalog path is built only from a valid code.",
    "Nine cases are tested in " + c("tests/prove-unita.c") + " and again in " + c("tests/engine.sh") + " (group "
    "8): Italian, English, a language without a translation, " + c("C") + ", precedence of " + c("LC_ALL") + " and of "
    + c("LC_MESSAGES") + ", a " + c("LANGUAGE") + " list, " + c("LANGUAGE") + " with " + c("C") + ", odd values.",
])

MO = fig(
    box(20, 50, 150, 56, "header", "magic, N, offsets", "dark", 12)
    + box(190, 50, 170, 56, "originals table", "N × (length, offset)", "navy", 12)
    + box(380, 50, 170, 56, "translations table", "N × (length, offset)", "navy", 12)
    + box(570, 50, 310, 56, "null-terminated strings", "originals in order: binary search", "blue", 12)
    + text(450, 140, "every offset is checked before use: an entry that runs past the end of the file does not exist", 11.5,
           "#166534", "600")
    + text(450, 160, "context: «context\\004text» in the original · empty translation = not translated", 11,
           "#475569"),
    900, 180, "«FIG» — What a .mo catalog looks like, and how AMS reads it", "The catalog reader")

S3 = p("The catalogs are in the gettext format (" + c(".mo") + "), but they are read by " + c("src/lingua.c") + ", not by "
       "libintl. This decision was made after a test: with libintl, a language not installed on the system stays "
       "untranslated even when " + c("LANGUAGE") + " is forced (with " + c("C.UTF-8") + " the library ignores "
       + c("LANGUAGE") + "), and root must be able to write to every terminal in the language of its user, which "
       "differs from its own.", lead=True) + MO + table(["Function", "What it does"], [
    [c("catalogo_da_memoria"), "checks the magic number " + c("0x950412de") + " in both byte orders and "
     "that the two tables fit in the file; otherwise no catalog"],
    [c("catalogo_cerca"), "binary search among the originals; every entry must fit in the file and end with a zero; "
     "an empty translation means “not translated”"],
    [c("catalogo(lingua)"), "reads " + c("LOCALEDIR/LINGUA/LC_MESSAGES/ams.mo") + " (at most 4 MiB) the first time, "
     "then keeps it in memory (up to 8 languages per process)"],
    [c("T(testo)") + ", " + c("TC(contesto, testo)"), "the translation in the language of whoever uses the process"],
    [c("tl(lingua, testo)") + ", " + c("tlc(…)"), "the translation in a given language: this is how " + c("ams send")
     + " writes to every terminal in its own language"],
], "«TAB» — The catalog reader") + \
    note("the catalogs are root's files, but the reader treats them as arbitrary data: fuzzing also tries "
         "arbitrary catalogs (" + cap(21, 7) + ").")

S4 = flow([("src/*.c", "T(\"…\"), TC, tl, tlc", "dark"), ("make pot", "xgettext → ams.pot", "navy"),
           ("po/it.po", "msgmerge, then translate", "blue"), ("make", "msgfmt --check → .mo", "navy"),
           ("check-docs", "catalog complete?", "green")], "«FIG» — From the texts in the code to the catalogs") + ul([
    "In the code, the texts for AMS users are in English inside " + c("T(\"…\")") + " (or " + c("TC(contesto, \"…\")")
    + ", " + c("tl(lingua, \"…\")") + " for a given language; " + c("N_(…)") + " for texts translated later). "
    "Names, comments and developer notes are in Italian.",
    c("make pot") + " extracts them into " + c("po/ams.pot") + " with " + c("xgettext") + " (with the "
    + c("TRADUTTORI") + " comments) and updates the " + c(".po") + " files with " + c("msgmerge") + "; " + c("make") + " compiles them "
    "with " + c("msgfmt --check") + ", which also checks that every translation has the same " + c("%s") + ".",
    c("tools/check-docs.py") + " fails if a catalog does not pass " + c("msgfmt --check") + ", has translations to "
    "review, or does not contain all the texts of the code.",
    "For a new language a " + c("po/XX.po") + " is enough (created, for example, with " + c("msginit") + "): the Makefile and "
    + c("install.sh") + " pick it up by themselves.",
]) + warn("if the user changes " + c("LANG") + " inside the shell (for example in " + c(".bashrc") + "), "
          "the header written at sending time follows the environment the shell started with; question and answers follow "
          "the new one (" + cap(23) + ").")

CHAPTER = ("Languages", [
    ("Everyone in their own language", S1),
    ("Choosing the language", S2),
    ("The .mo catalog reader", S3),
    ("Texts, contexts and catalogs", S4),
])
