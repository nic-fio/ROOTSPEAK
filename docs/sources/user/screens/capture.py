"""Real screenshots for the user manual, taken in test mode (without root).

They complete those in docs/sources/screens/ (taken in the test machine by
tools/tui-screenshots.sh) with the overlays of the TUI (keys, revocation, purge,
search) and with the built-in help. It prepares a test message store with
three messages for two users of the machine, opens rspeak on a virtual terminal,
presses keys and saves each screen with its colours.

    make
    python3 docs/sources/user/screens/capture.py              TUI (116x30)
    MODE=help python3 docs/sources/user/screens/capture.py    help (78x22)

The users must exist on the machine: change them in USERS.
"""
import fcntl, os, pathlib, pty, select, shutil, struct, subprocess, tempfile, termios, time

OUT = pathlib.Path(__file__).resolve().parent
ROOT = OUT.parents[3]
USERS = ("nicfio", "user")
VAR = tempfile.mkdtemp(prefix="rootspeak-screenshots-")
env = dict(os.environ, RSPEAK_TEST="1", RSPEAK_CONF="/dev/null", RSPEAK_TEST_TTY="", RSPEAK_LIB=f"{ROOT}/build",
           RSPEAK_VAR=f"{VAR}/var", TERM="xterm-256color")
for k in ("LC_ALL", "LC_MESSAGES", "LANGUAGE", "NO_COLOR"):
    env.pop(k, None)
A = f"{ROOT}/build/rspeak"


def sh(*a):
    return subprocess.run([A, *a], env=env, capture_output=True, text=True)


u1, u2 = USERS
sh("send", "--to", f"{u1},{u2}", "--expires", "1d", "--title", "Server update",
   "Tonight at 11 pm the mail server is updated.")
sh("send", "--to", "all", "--title", "Maintenance",
   "On Saturday from 8 am to 12 noon the server will be off for disk maintenance.\nPlease save your work by Friday evening.")
sh("send", "--to", u2, "Your account expires on Friday: please drop by the IT office.")
now = int(time.time())
for u, mid, ch in ((u1, 1, "desktop"), (u2, 1, "terminal pts/1"), (u1, 2, "desktop")):
    d = f"{VAR}/var/users/{u}"
    open(f"{d}/acks/{mid}", "w").write(f"{now} {ch}\n")
    os.rename(f"{d}/inbox/{mid}", f"{d}/read/{mid}")

MODE = os.environ.get("MODE", "tui")
pid, fd = pty.fork()
if pid == 0:
    os.execve(A, ["rspeak"] if MODE == "tui" else ["rspeak", "--help"], env)
rows, cols = (30, 116) if MODE == "tui" else (22, 78)
fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))


def frame(t=1.2):
    out, t0 = b"", time.time()
    while time.time() - t0 < t:
        r, _, _ = select.select([fd], [], [], 0.05)
        if r:
            try:
                out += os.read(fd, 65536)
            except OSError:
                break
    return out.split(b"\x1b[H")[-1]


def save(name, t=1.2):
    (OUT / f"{name}.ans").write_bytes(frame(t).split(b"\x1b[J")[0])


def keys(b, pause=0.4):
    os.write(fd, b)
    time.sleep(pause)


frame(1.5)
if MODE == "tui":
    keys(b"?")
    save("help")
    keys(b"x")
    keys(b"\x1b[B")
    keys(b"r")
    save("revoke")
    keys(b"n")
    keys(b"p")
    save("purge")
    keys(b"\x1b")
    frame(0.5)
    keys(b"/")
    keys(b"server")
    save("search")
    keys(b"\r")
    save("search-results")
    keys(b"q")
else:
    keys(b"2")
    keys(b"1")
    save("guide-info")
    keys(b"3")
    save("guide-options")
    keys(b"q")
frame(0.5)
shutil.rmtree(VAR, ignore_errors=True)
