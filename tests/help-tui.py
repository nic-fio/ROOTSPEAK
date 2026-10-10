#!/usr/bin/env python3
# Copyright (c) 2026 Nicola Fiorillo
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Tests the interactive guide of `rspeak --help` on a virtual terminal: it opens
it, presses keys and checks the screen after each one. Usage: tests/help-tui.py [-v]
(-v prints the screens). Exits with 1 if a check fails.
Runs without root thanks to RSPEAK_TEST=1: installed, rspeak always goes through sudo."""
import fcntl, os, pty, re, select, struct, sys, termios, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERBOSE = "-v" in sys.argv
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
failures = []


def spawn(rows, cols):
    pid, fd = pty.fork()
    if pid == 0:
        env = dict(os.environ, RSPEAK_LIB=os.path.join(ROOT, "build"), RSPEAK_TEST="1", TERM="xterm-256color")
        os.execvpe(os.environ.get("RSPEAK_BIN", os.path.join(ROOT, "build/rspeak")), ["rspeak", "--help"], env)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))
    return pid, fd


def read_all(fd, wait=0.6, limit=5.0):
    """Reads until something arrives and then everything stays still for «wait»
    seconds (at most «limit»): on a busy machine the drawing can be late."""
    out, start, last = b"", time.time(), time.time()
    while time.time() - start < limit:
        r, _, _ = select.select([fd], [], [], 0.05)
        if r:
            try:
                data = os.read(fd, 65536)
            except OSError:
                break
            if not data:
                break
            out += data
            last = time.time()
        elif out and time.time() - last >= wait:
            break
        elif not out and time.time() - start >= max(wait, 2.0):
            break
    return out.decode("utf-8", "replace")


def read_frame(fd, limit=8.0):
    """Reads until the last frame drawn is complete (it contains the bottom
    right corner of the frame), then collects what follows."""
    out, start = "", time.time()
    while time.time() - start < limit:
        out += read_all(fd, 0.2, 1.0)
        if "\x1b[H" in out and "┘" in out.split("\x1b[H")[-1]:
            return out + read_all(fd, 0.2, 0.5)
    return out


def screen(raw):
    """The last frame drawn, without colours."""
    frame = raw.split("\x1b[H")[-1]
    return [ANSI.sub("", l).rstrip("\r") for l in frame.split("\n")]


def check(name, cond, shot):
    if VERBOSE or not cond:
        print(f"--- {name}")
        print("\n".join(shot))
    if not cond:
        failures.append(name)


pid, fd = spawn(30, 100)
raw = read_frame(fd)
s = screen(raw)
check("opening: frame and Info tab", "\x1b[?1049h" in raw and s[0].startswith("┌─ rspeak — guide")
      and any("SYNOPSIS" in l for l in s) and len(s) == 30 and all(len(l) == 100 for l in s), s)
os.write(fd, b"\x1b[C")                      # right arrow
s = screen(read_frame(fd))
check("→: Commands tab", any("send [options] [TEXT]" in l for l in s), s)
os.write(fd, b"3")                           # tab 3
s = screen(read_frame(fd))
check("3: Options tab", any("--expires DURATION" in l for l in s), s)
os.write(fd, b"4G")                          # Examples, to the end
s = screen(read_frame(fd))
check("4 G: Examples, end", any("rspeak revoke 12" in l for l in s) and any(re.search(r"lines \d+-(\d+)/\1", l) for l in s), s)
os.write(fd, b"\x1b[5~g")                    # PgUp, g
s = screen(read_frame(fd))
check("PgUp g: start of the tab", any("lines 1-" in l for l in s), s)
fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", 20, 70, 0, 0))
s = screen(read_frame(fd))
check("resize to 70x20", len(s) == 20 and all(len(l) == 70 for l in s), s)
os.write(fd, b"q")
raw = read_all(fd)
_, status = os.waitpid(pid, 0)
check("q: clean exit", "\x1b[?1049l" in raw and os.WEXITSTATUS(status) == 0, [repr(raw[-80:])])

# terminal too small: manual-style page through the pager
pid, fd = spawn(8, 40)
raw = read_all(fd, 1.5)
os.write(fd, b"q")
read_all(fd)
os.waitpid(pid, 0)
check("40x8: manual-style page", "\x1b[?1049h" not in raw and "RSPEAK(1)" in raw, screen(raw)[:6])

print("OK" if not failures else "FAILED: " + ", ".join(failures))
sys.exit(1 if failures else 0)
