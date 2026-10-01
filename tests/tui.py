#!/usr/bin/env python3
"""RootSpeak - Advanced Messaging System for Linux
Tests the administrators' TUI (rspeak without arguments) on a virtual
terminal, in test mode on a temporary message store: it opens it, presses keys
as a person would and checks the screen and the store after each one.
    tests/tui.py [-v]        (-v prints the screens)
Uses the programs in build/ (RSPEAK_BUILD for another folder)."""
import fcntl, os, pty, re, select, shutil, struct, subprocess, sys, tempfile, termios, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.environ.get("RSPEAK_BUILD", os.path.join(ROOT, "build"))
VERBOSE = "-v" in sys.argv
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
U = subprocess.run(["id", "-un"], capture_output=True, text=True).stdout.strip()
TMP = tempfile.mkdtemp()
ENV = dict(os.environ, RSPEAK_TEST="1", RSPEAK_VAR=f"{TMP}/var", RSPEAK_LIB=B,
           RSPEAK_CONF="/dev/null", RSPEAK_TEST_TTY="", LANG="en_US.UTF-8", TERM="xterm-256color",
           EDITOR="sed -i s/second/SECOND/")
ENV.pop("LANGUAGE", None), ENV.pop("LC_ALL", None), ENV.pop("LC_MESSAGES", None)
failed = []


def rspeak(*args, stdin=None):
    return subprocess.run([f"{B}/rspeak", *args], env=ENV, input=stdin, capture_output=True, text=True)


def start(rows, cols):
    pid, fd = pty.fork()
    if pid == 0:
        os.execvpe(f"{B}/rspeak", ["rspeak"], ENV)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))
    return pid, fd


def read_bytes(fd, t=1.0):
    out, t0 = b"", time.time()
    while time.time() - t0 < t:
        r, _, _ = select.select([fd], [], [], 0.05)
        if r:
            try:
                out += os.read(fd, 65536)
            except OSError:
                break
    return out


def read(fd, t=1.0):
    """What arrives in t seconds."""
    return read_bytes(fd, t).decode("utf-8", "replace")


def read_screen(fd, t=1.0, limit=6.0):
    """Reads until the last drawing is complete (it has the bottom right corner)."""
    raw, t0 = read_bytes(fd, t), time.time()
    while not (b"\x1b[H" in raw and "┘".encode() in raw.split(b"\x1b[H")[-1]) and time.time() - t0 < limit:
        raw += read_bytes(fd, 0.3)
    return raw.decode("utf-8", "replace")


def screen(raw):
    fr = raw.split("\x1b[H")[-1]
    return [ANSI.sub("", l).rstrip("\r") for l in fr.split("\n")]


def check(name, ok, lines):
    if VERBOSE or not ok:
        print(f"--- {name}")
        print("\n".join(l for l in lines if l.strip("│ ")))
    if not ok:
        failed.append(name)


def text(lines):
    return "\n".join(lines)


try:
    rspeak("send", "--to", U, "--title", "Maintenance", "On Saturday from 8 to 12 the server will be off.")
    rspeak("send", "--to", U, "Second test")
    subprocess.run(["script", "-qec", f"{B}/rootspeak-user prompt", "/dev/null"], env=ENV, input="y\n",
                   capture_output=True, text=True)

    pid, fd = start(28, 120)
    raw = read_screen(fd, 1.5)
    s = screen(raw)
    check("opening: list with bar and summary, right size",
          "\x1b[?1049h" in raw and s[0].startswith("┌─ RootSpeak · sent messages") and len(s) == 28
          and all(len(l) == 120 for l in s) and "all confirmed (1)" in text(s) and "1 delivered" in text(s)
          and "█ confirmed" in text(s), s)
    check("no invented state", not re.search(r"pending|complete|cancelled|waiting", text(s)), s)

    os.write(fd, b"\r")
    s = screen(read_screen(fd))
    check("Enter: detail with the recipients and the state of rspeak status",
          "Message 2" in s[0] and "Second test" in text(s) and f"{U}" in text(s) and "delivered" in text(s), s)
    os.write(fd, b"\t")
    s = screen(read_screen(fd))
    check("Tab: history from the log (or no events)",
          "delivered to" in text(s) or "No events in the system log" in text(s), s)
    os.write(fd, b"\x1b")
    read(fd, 0.6)

    os.write(fd, b"n")
    read(fd, 0.5)
    os.write(fd, U.encode() + b"\t")
    read(fd, 0.8)
    os.write(fd, "TUI test é ok".encode() + b"\t2h\t")
    read(fd, 0.5)
    os.write(fd, "first line\rsecond line".encode())
    s = screen(read_screen(fd))
    check("form: fields, recipient preview, text on two lines",
          "1 recipient" in text(s) and "TUI test é ok" in text(s) and "first line" in text(s)
          and "second line" in text(s), s)
    os.write(fd, b"\x05")
    s = screen(read_screen(fd, 1.5))
    check("Ctrl+E: the text goes through the editor and comes back", "SECOND line" in text(s), s)
    os.write(fd, b"\x13")
    s = screen(read_screen(fd))
    check("Ctrl+S: confirmation with recipients, title and expiry",
          "Send the message?" in text(s) and "To: " + U in text(s) and "Expires: 2h" in text(s), s)
    os.write(fd, b"y")
    s = screen(read_screen(fd, 1.5))
    check("send: outcome of the command, a single window",
          "Message 3 sent to 1 user." in text(s) and text(s).count("┌─ ") == 2, s)
    st = rspeak("status", "3").stdout
    check("the message sent from the TUI is in the store", "TUI test é ok" in st and "SECOND line" in st, [st])
    os.write(fd, b" ")
    s = screen(read_screen(fd))
    check("after sending the list shows the new message at the top", ">  3" in text(s), s)

    os.write(fd, b"m")
    read(fd, 0.6)
    os.write(fd, b"y")
    s = screen(read_screen(fd, 1.5))
    check("m: reminder done", "1 recipient reminded" in text(s), s)
    os.write(fd, b" ")
    read(fd, 0.6)
    os.write(fd, b"r")
    s = screen(read_screen(fd))
    check("r: confirmation before revoking", "Revoke message 3?" in text(s), s)
    os.write(fd, b"n")
    read(fd, 0.6)
    check("n: revocation cancelled, message untouched", "REVOKED" not in rspeak("status", "3").stdout, [])
    os.write(fd, b"r")
    read(fd, 0.6)
    os.write(fd, b"s")
    read(fd, 0.6)
    check("s (an Italian yes) does not confirm the revocation", "REVOKED" not in rspeak("status", "3").stdout, [])
    os.write(fd, b"y")
    read(fd, 1.5)
    os.write(fd, b" ")
    s = screen(read_screen(fd))
    check("revocation: [revoked] in the list and in the store",
          "[revoked]" in text(s) and "REVOKED" in rspeak("status", "3").stdout, s)

    os.write(fd, b"/Maint\r")
    s = screen(read_screen(fd))
    check("/: search", "Maintenance" in text(s) and "Second test" not in text(s), s)
    os.write(fd, b"\x1b")
    read(fd, 0.6)

    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", 24, 80, 0, 0))
    s = screen(read_screen(fd, 1.5))
    check("80x24: bar and confirmed out of total", len(s) == 24 and all(len(l) == 80 for l in s)
          and "1/1" in text(s), s)

    os.write(fd, b"q")
    raw = read(fd, 1.0)
    _, st = os.waitpid(pid, 0)
    check("q: clean exit", "\x1b[?1049l" in raw and os.WEXITSTATUS(st) == 0, [repr(raw[-60:])])

    # terminal too small: no TUI, the guide
    pid, fd = start(15, 60)
    raw = read(fd, 1.5)
    os.write(fd, b"q")
    read(fd, 0.5)
    os.waitpid(pid, 0)
    check("60x15: no TUI, the guide", "RootSpeak · sent messages" not in raw and ("rspeak — guide" in raw or "RSPEAK(1)" in raw),
          screen(raw)[:5])
    # in a pipe: the guide as plain text
    out = subprocess.run([f"{B}/rspeak"], env=ENV, capture_output=True, text=True, stdin=subprocess.DEVNULL).stdout
    check("in a pipe: the guide", "SYNOPSIS" in out, out.splitlines()[:3])
finally:
    shutil.rmtree(TMP, ignore_errors=True)

print("OK" if not failed else "FAILED: " + ", ".join(failed))
sys.exit(1 if failed else 0)
