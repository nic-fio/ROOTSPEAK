#!/usr/bin/env python3
# Copyright (c) 2026 Nicola Fiorillo
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""RootSpeak - Advanced Messaging System for Linux
Real-world test scenarios: runs as root inside the test machine
(tests/container), with RootSpeak installed, real users and real ssh sessions.

Each scenario sends messages from root or from an administrator to the users,
simulates what the users do (log in, answer, postpone, break their own
mailbox), measures the times and records the outcome in results.json and in a
readable report (Markdown).

    python3 scenarios.py RESULTS_FOLDER
"""
import json
import os
import pty
import pwd
import shlex
import re
import select
import signal
import subprocess
import sys
import time

OUT = sys.argv[1] if len(sys.argv) > 1 else "/opt/results"
VAR = "/var/lib/rootspeak"
# installed by install.sh in /usr/local, or by the package in /usr
PREFIX = "/usr" if os.path.exists("/usr/lib/rootspeak/rootspeak-user") else "/usr/local"
RSPEAK = f"{PREFIX}/bin/rspeak"
AGENT = f"{PREFIX}/lib/rootspeak/rootspeak-user agent"
PACKAGE = os.environ.get("RSPEAK_TEST_PACKAGE")   # the folder of tools/release.sh: package tests (P)
PKG = "/opt/rootspeak-src/tests/container/package.sh"
DESK = os.environ.get("RSPEAK_TEST_DESKTOP")   # user with a graphical session (only in the VM)
# (OSC and APC sequences end with BEL or with ESC \: systemd's profile.d/80-systemd-osc-context.sh
# writes OSC 3008 with ESC \ before every command and every prompt)
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]|\x1b[\]_][^\x07\x1b]*(?:\x07|\x1b\\)|\r")
# what RootSpeak writes in the terminal, exactly as the program prints it
QUESTION = r"\[RootSpeak\] Do you confirm you have read the message\? \[y/N\]"
CONFIRMED = r"\[RootSpeak\] Confirmed\."
HEADER = "── RootSpeak · Message from the administrator · "
# the desktop dialog
DLG_TITLE = "RootSpeak · Message from the administrator"
DLG_OK = "I have read it"
DLG_LATER = "Later"
results = []
# the sessions are opened as from a terminal emulator, which always sets TERM
# (without it the ksh93u+m 1.0.8 of Ubuntu 24.04 exits right after the first prompt)
TERMINAL_ENV = {**os.environ, "TERM": "xterm-256color"}
# users with a shell other than bash, and their prompt
TEST_SHELLS = {"zeno": ("zsh", r"% $"), "fabio": ("fish", r"> $"), "kora": ("ksh", r"\$ $"), "dario": ("dash", r"\$ $")}


# ---- tools ----

def sh(cmd, check=False, **kw):
    r = subprocess.run(cmd, shell=True, executable="/bin/bash", capture_output=True, text=True, **kw)
    if check and r.returncode:
        raise RuntimeError(f"{cmd}: {r.stderr}")
    return r


def rspeak(args, as_user="root"):
    """Runs rspeak as root, or as another user (who goes through sudo)."""
    pre = "" if as_user == "root" else f"runuser -u {as_user} -- "
    return sh(f"{pre}{RSPEAK} {args}")


def as_ordinary_user(user, args):
    """Tries to run rspeak as an ordinary user. The system's own error messages
    (runuser, env) are asked for in English: RootSpeak is never reached."""
    return sh(f"LC_ALL=C.UTF-8 runuser -u {user} -- {args}")


def denied(r):
    """The program could not even be started: permission denied."""
    return r.returncode != 0 and "Permission denied" in r.stderr


def reset():
    """Closes the users' sessions and the RootSpeak dialogs left on the desktop, and empties the store.
    The dialogs are closed first: the store starts again from message 1, and an old dialog
    would find a new message with its same number."""
    for u in ("mario", "anna", "luca", "admin", *TEST_SHELLS):
        sh(f"loginctl terminate-user {u}")
    if DESK:
        # the agent stops with its dialogs, and starts again later, with an empty store
        sh(f"pkill -u {DESK} -f '^(/bin/bash )?{AGENT}$'; pkill -u {DESK} -x zenity")
        time.sleep(1)
    time.sleep(0.5)
    sh(f"rm -rf {VAR}/sent/* {VAR}/sent/.seq* {VAR}/users/*")
    if DESK and sh(f"loginctl show-user {DESK} -p Display --value").stdout.strip():
        sh(f"systemd-run --user --machine={DESK}@.host --collect --quiet {AGENT}")
        time.sleep(1)


def state(mid, user):
    out = rspeak(f"status {mid}").stdout
    for line in out.splitlines():
        parts = line.split(None, 1)
        if parts and parts[0] == user:
            return parts[1].strip() if len(parts) > 1 else ""
    return None


class Session:
    """An ssh connection with a terminal for a user, as a person would open it."""

    def __init__(self, user, prompt=r"\$ $", command=None):
        self.user = user
        self.buf = ""
        self.pid, self.fd = pty.fork()
        if self.pid == 0:
            os.execvpe("ssh", ["ssh", "-tt", f"{user}@localhost"] + ([command] if command else []), TERMINAL_ENV)
        self.read_until(prompt, 15)

    def read(self, duration=0.3):
        end = time.time() + duration
        while time.time() < end:
            r, _, _ = select.select([self.fd], [], [], 0.05)
            if r:
                try:
                    data = os.read(self.fd, 65536)
                except OSError:
                    break
                if not data:
                    break
                self.answer(data)
                self.buf += data.decode("utf-8", "replace")
        return self.buf

    def answer(self, data):
        """Answers the questions a shell asks the terminal, as a terminal emulator does:
        fish 4.1 and later ask for the device attributes and wait for them before the prompt."""
        if re.search(rb"\x1b\[0?c", data):
            os.write(self.fd, b"\x1b[?62;22c")
        if b"\x1b[6n" in data:
            os.write(self.fd, b"\x1b[1;1R")

    def read_until(self, pattern, duration=10):
        """Waits until the output (without colours) contains the pattern; returns the seconds waited."""
        t0 = time.time()
        while time.time() - t0 < duration:
            self.read(0.05)
            if re.search(pattern, ANSI.sub("", self.buf), re.M):
                return time.time() - t0
        return None

    def write(self, text):
        os.write(self.fd, text.encode())

    def clear(self):
        self.buf = ""

    def text(self):
        return ANSI.sub("", self.buf)

    def close(self):
        try:
            os.write(self.fd, b"exit\n")
            time.sleep(0.2)
            os.kill(self.pid, signal.SIGKILL)
        except OSError:
            pass
        try:
            os.waitpid(self.pid, 0)
        except ChildProcessError:
            pass


def open_session(user):
    """An ssh session with a terminal, without waiting for the prompt (at login there may be the question)."""
    s = Session.__new__(Session)
    s.user, s.buf = user, ""
    s.pid, s.fd = pty.fork()
    if s.pid == 0:
        os.execvpe("ssh", ["ssh", "-tt", f"{user}@localhost"], TERMINAL_ENV)
    return s


def halfway(p, duration=10):
    """Waits until the sending started in p is halfway (at least 3 deliveries recorded,
    not all): so an interruption really falls during the delivery, however fast
    the sending is. Returns the message ID (None if the sending finished first)."""
    t0 = time.time()
    while time.time() - t0 < duration and p.poll() is None:
        ids = [int(x) for x in os.listdir(f"{VAR}/sent") if x.isdigit()] if os.path.isdir(f"{VAR}/sent") else []
        if ids:
            mid = max(ids)
            try:
                n = len(open(f"{VAR}/sent/{mid}/delivery").read().splitlines())
            except OSError:
                n = 0
            if n >= 3:
                return mid
        time.sleep(0.002)
    return None


def record(code, area, description, expected, ok, details="", **measures):
    """ok: True passed, False failed, None not tested (not counted among the passed)."""
    outcome = "--" if ok is None else "OK" if ok else "NO"
    results.append(dict(code=code, area=area, description=description, expected=expected,
                        outcome=outcome, details=details, measures=measures))
    print(f"  {dict(OK='ok', NO='NO').get(outcome, '--')}  {code}  {description}" + (f"  [{measures}]" if measures else ""))


def scenario(fn):
    """Runs a scenario on an empty store; an exception is a NO outcome."""
    reset()
    try:
        fn()
    except Exception as e:  # noqa: BLE001
        record(fn.__name__, "error", f"exception in {fn.__name__}", "no exception", False, repr(e))


# ---- A. access and permissions ----

def a_access():
    r = rspeak('send --to mario "from root"')
    record("A1", "Access", "root sends a message", "sending succeeds",
           r.returncode == 0 and "Message 1 sent to 1 user." in r.stdout, r.stdout.strip() + r.stderr.strip())
    t0 = time.time()
    r = rspeak('send --to anna "from admin"', "admin")
    dt = time.time() - t0
    frm = sh(f"grep '^from:' {VAR}/sent/2/msg").stdout.strip()
    record("A2", "Access", "an administrator (sudo group) sends: rspeak re-runs itself with sudo",
           "sending succeeds, sender admin", r.returncode == 0 and frm == "from: admin", frm, seconds=round(dt, 3))
    r = as_ordinary_user("mario", f'{RSPEAK} send --to anna "from mario"')
    record("A3", "Access", "an ordinary user cannot run rspeak", "permission denied, no message",
           denied(r) and not os.path.exists(f"{VAR}/sent/3"), r.stderr.strip())
    r = as_ordinary_user("mario", f"{RSPEAK} --help")
    record("A4", "Access", "an ordinary user cannot even open the help", "permission denied",
           denied(r), r.stderr.strip())


# ---- B. recipients ----

def b_recipients():
    def rcpt(mid):
        return sh(f"cat {VAR}/sent/{mid}/recipients").stdout.split()

    rspeak('send --to mario "one"')
    record("B1", "Recipients", "one user", "mario", rcpt(1) == ["mario"], str(rcpt(1)))
    rspeak('send --to mario,anna,mario "list"')
    record("B2", "Recipients", "list with a duplicate", "anna, mario (once)", rcpt(2) == ["anna", "mario"], str(rcpt(2)))
    rspeak('send --to @developers "group"')
    record("B3", "Recipients", "group @developers", "anna, mario", rcpt(3) == ["anna", "mario"], str(rcpt(3)))
    rspeak('send --to all "everyone"')
    shells = [u for u in TEST_SHELLS if sh(f"getent passwd {u}").returncode == 0]   # only in the container
    everyone = sorted(["admin", "anna", "luca", "mario", *shells] + ([DESK] if DESK else []))
    record("B4", "Recipients", "all: human users, except root and whoever has nologin",
           ", ".join(everyone), rcpt(4) == everyone, str(rcpt(4)))
    s = Session("luca")
    rspeak('send --to online "logged in"')
    online = sorted(["luca"] + ([DESK] if DESK else []))
    record("B5", "Recipients", "online: only whoever has an open session", ", ".join(online), rcpt(5) == online, str(rcpt(5)))
    s.close()
    r = rspeak('send --to nobodyhere "x"')
    record("B6", "Recipients", "user that does not exist", "error, no message created",
           r.returncode != 0 and "no such user: nobodyhere" in r.stderr and not os.path.exists(f"{VAR}/sent/6"),
           r.stderr.strip())
    sh("groupadd -f empty")
    r = rspeak('send --to @empty "x"')
    record("B7", "Recipients", "group without members", "error «no recipients»",
           r.returncode != 0 and "no recipients" in r.stderr, r.stderr.strip())


# ---- C. delivery according to the state of the sessions ----

def c_delivery():
    # C1: logged out, then logs in
    rspeak('send --to mario --title Maintenance "Server off on Saturday"')
    st = state(1, "mario")
    record("C1a", "Delivery", "user logged out: the copy waits in the mailbox", "delivered",
           st == "delivered" and os.path.exists(f"{VAR}/users/mario/inbox/1"), st)
    t0 = time.time()
    s = open_session("mario")
    dt = s.read_until(QUESTION, 15)
    record("C1b", "Delivery", "at login the message and the question appear before the first prompt",
           "text and question at login", dt is not None and "Server off on Saturday" in s.text() and HEADER in s.text(),
           seconds_from_login=round(time.time() - t0, 3) if dt else None)
    s.write("y\n")
    s.read_until(r"\$ $", 5)
    record("C1c", "Delivery", "confirmation at login", "confirmed (terminal)",
           (state(1, "mario") or "").startswith("confirmed"), state(1, "mario"))
    s.close()

    # C2: logged in with a terminal: time for the text to appear
    s = Session("anna")
    s.clear()
    t0 = time.time()
    rspeak('send --to anna "Meeting at 11"')
    dt_send = time.time() - t0
    dt = s.read_until(r"Meeting at 11", 5)
    record("C2a", "Delivery", "user logged in: the text appears in their terminal", "text in the terminal",
           dt is not None, seconds_send=round(dt_send, 3),
           seconds_to_terminal=round(dt_send + (dt or 0), 3) if dt is not None else None)
    st = state(2, "anna")
    record("C2b", "Delivery", "state after writing to the terminal", "delivered, written to 1 terminal",
           st == "delivered, written to 1 terminal", st)
    s.clear()
    s.write("\n")
    dt = s.read_until(QUESTION, 5)
    record("C2c", "Delivery", "pressing Enter the question appears", "question at the next prompt", dt is not None,
           seconds=round(dt, 3) if dt else None)
    s.write("y\n")
    s.read_until(CONFIRMED, 5)
    s.close()

    # C3: ssh without a terminal
    p = subprocess.Popen(["ssh", "luca@localhost", "sleep 4"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.5)
    r = rspeak('send --to luca "Mailbox only"')
    p.wait()
    st = state(3, "luca")
    record("C3", "Delivery", "ssh session without a terminal: it is not touched, the copy goes to the mailbox",
           "sending succeeds, delivered, no terminal written", r.returncode == 0 and st == "delivered", st)

    # C4: two sessions of the same user
    s1, s2 = Session("mario"), Session("mario")
    for s in (s1, s2):
        s.clear()
    rspeak('send --to mario "Two sessions"')
    ok1 = s1.read_until("Two sessions", 5) is not None
    ok2 = s2.read_until("Two sessions", 5) is not None
    st = state(4, "mario")
    record("C4a", "Delivery", "two open sessions: the text appears in both", "text in 2 terminals",
           ok1 and ok2 and st == "delivered, written to 2 terminals", st)
    s1.clear(); s2.clear()
    s1.write("\n"); s2.write("\n")
    s1.read_until(QUESTION, 5); s2.read_until(QUESTION, 5)
    t0 = time.time()
    s1.write("y\n")
    dt = s2.read_until(r"Message already confirmed elsewhere", 5)
    record("C4b", "Delivery", "confirming in one session, the question in the other stops",
           "«Message already confirmed elsewhere» in the other", dt is not None, seconds=round(time.time() - t0, 3))
    s1.close(); s2.close()


# ---- D. confirmation, postponement, reminders ----

def d_confirmation():
    s = Session("luca")
    rspeak('send --to luca "Postpone me"')
    s.clear(); s.write("\n")
    s.read_until(QUESTION, 5)
    s.write("n\n")
    s.read_until(r"You will be asked again in", 5)
    st = state(1, "luca")
    record("D1", "Confirmation", "the user postpones", "delivered, postponed on …",
           (st or "").startswith("delivered") and "postponed on" in st, st)
    s.clear(); s.write("true\n")
    s.read_until(r"\$ $", 5)
    record("D2", "Confirmation", "after the postponement, only a reminder at the prompt",
           "«You have 1 message…», no question",
           "You have 1 message from the administrator to confirm." in s.text() and "Do you confirm" not in s.text(),
           s.text()[-160:])
    r = rspeak("remind 1")
    s.clear(); s.write("\n")
    ok = s.read_until(QUESTION, 5) is not None
    record("D5", "Confirmation", "rspeak remind after a postponement: the question comes back at the next prompt",
           "«Message 1: 1 recipient reminded.», question at the prompt",
           ok and "Message 1: 1 recipient reminded." in r.stdout, r.stdout.strip())
    s.write("n\n"); s.read_until(r"You will be asked again in", 5)
    s.close()
    s = open_session("luca")
    ok = s.read_until(QUESTION, 10) is not None
    record("D3", "Confirmation", "at the next login the postponement does not count: the question comes back",
           "question at login", ok)
    s.write("y\n"); s.read_until(r"\$ $", 5)
    ack = sh(f"cat {VAR}/users/luca/acks/1").stdout.strip()
    record("D4", "Confirmation", "confirmation recorded with date and channel", "«EPOCH terminal pts/N»",
           bool(re.fullmatch(r"\d+ terminal pts/\d+", ack)), ack)
    s.close()


# ---- E. expiry and revocation ----

def e_expiry_revocation():
    rspeak('send --to mario --expires 1m "Short-lived notice"')
    sh(f"sed -i 's/^expires: .*/expires: {int(time.time()) - 5}/' {VAR}/sent/1/msg {VAR}/users/mario/inbox/1")
    s = Session("mario")
    record("E1", "Expiry", "an expired message is not shown at login", "no text",
           "Short-lived notice" not in s.text(), "")
    st = state(1, "mario")
    record("E2", "Expiry", "state of an expired message", "delivered, not confirmed (expired)",
           st == "delivered, not confirmed (expired)", st)
    rspeak('send --to mario "To be revoked"')
    s.clear(); s.write("\n")
    s.read_until(QUESTION, 5)
    t0 = time.time()
    rspeak("revoke 2")
    dt = s.read_until(r"The administrator has revoked the message\.", 5)
    record("E3", "Revocation", "revocation with the question waiting: the question stops",
           "«The administrator has revoked the message.»", dt is not None, seconds=round(time.time() - t0, 3))
    st = state(2, "mario")
    record("E4", "Revocation", "state after the revocation", "delivered, not confirmed (revoked)",
           st == "delivered, not confirmed (revoked)", st)
    s.close()
    rspeak('send --to anna "Revoked early"')
    rspeak("revoke 3")
    s = Session("anna")
    record("E5", "Revocation", "a message revoked before the login is not shown", "no text",
           "Revoked early" not in s.text())
    s.close()


# ---- F. faults and recovery ----

def f_faults():
    # the user's primary group, not a group named after the user: SLES 15 (USERGROUPS_ENAB no)
    # puts every new user in «users», and «-g anna» would fail and leave the folder to root
    sh(f"install -d -m 700 -o anna -g \"$(id -gn anna)\" {VAR}/users/anna; "
       f"install -d -m 555 -o root {VAR}/users/anna/inbox")
    r = rspeak('send --to mario,anna "Fault"')
    st = state(1, "anna")
    record("F1", "Faults", "the copy for one user cannot be written: the others receive it",
           "error, anna «sent, not delivered», mario delivered",
           r.returncode != 0 and (st or "").startswith("sent, not delivered") and state(1, "mario") == "delivered",
           f"{r.stderr.strip()} | anna: {st}")
    sh(f"chown anna:\"$(id -gn anna)\" {VAR}/users/anna/inbox; chmod 755 {VAR}/users/anna/inbox")
    r = rspeak("list")
    record("F2", "Faults", "fault fixed: the next command completes the delivery", "anna delivered",
           state(1, "anna") == "delivered" and not os.path.exists(f"{VAR}/sent/1/incomplete"), r.stderr.strip())

    # sending really interrupted: SIGKILL during the delivery to many users
    for i in range(60):
        sh(f"id u{i:02d} >/dev/null 2>&1 || useradd -m -s /bin/bash u{i:02d}")
    # rspeak send itself is killed (not a shell containing it)
    p = subprocess.Popen([RSPEAK, "send", "--to", "all", "Interrupted"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    halfway(p)
    p.kill(); p.wait()
    ids = sorted(int(x) for x in os.listdir(f"{VAR}/sent") if x.isdigit())
    mid = ids[-1]
    n_before = len(sh(f"cat {VAR}/sent/{mid}/delivery 2>/dev/null").stdout.splitlines())
    n_tot = len(sh(f"cat {VAR}/sent/{mid}/recipients 2>/dev/null").stdout.split())
    t0 = time.time()
    r = rspeak("list")
    dt = time.time() - t0
    n_after = len(sh(f"cat {VAR}/sent/{mid}/delivery").stdout.splitlines())
    record("F3", "Faults", "rspeak send killed halfway (SIGKILL): the next command completes",
           "all copies delivered, no sign of an incomplete sending",
           0 < n_before < n_tot and n_after == n_tot and not os.path.exists(f"{VAR}/sent/{mid}/incomplete"),
           f"delivered before {n_before}/{n_tot}, after {n_after}/{n_tot}; {r.stderr.strip()[:120]}",
           delivered_at_kill=n_before, recipients=n_tot, seconds_recovery=round(dt, 3))

    # sending killed between the creation of the user's folder and its chown
    sh(f"rm -rf {VAR}/users/luca && install -d -m 700 {VAR}/users/luca")
    r = rspeak('send --to luca "After the half-made folder"')
    mid = max(int(x) for x in os.listdir(f"{VAR}/sent") if x.isdigit())
    st = state(mid, "luca")
    record("F6", "Faults", "user's folder left owned by root by an interrupted sending: the delivery fixes it",
           "delivered", r.returncode == 0 and st == "delivered", f"{st}; {r.stderr.strip()[:120]}")

    # revocation while the sending to many users is in progress: no copy may stay or come back
    p = subprocess.Popen([RSPEAK, "send", "--to", "all", "To be revoked"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    halfway(p)
    mid = max(int(x) for x in os.listdir(f"{VAR}/sent") if x.isdigit())
    n_before_revoke = len(open(f"{VAR}/sent/{mid}/delivery").read().splitlines())
    t0 = time.time()
    rv = rspeak(f"revoke {mid}")
    dt = time.time() - t0
    out_send = p.communicate()[0]
    copies = [u for u in os.listdir(f"{VAR}/users") if os.path.exists(f"{VAR}/users/{u}/inbox/{mid}")]
    record("F7", "Faults", "rspeak revoke during a sending to many users: the sending stops and no copy stays",
           "no copy in the mailboxes, sending interrupted", rv.returncode == 0 and not copies
           and not os.path.exists(f"{VAR}/sent/{mid}/revoking") and n_before_revoke < len(os.listdir(f"{VAR}/users")),
           f"copies left: {len(copies)}; delivered before the revocation: {n_before_revoke}; {out_send.strip()[:80]}",
           seconds_waiting_revoke=round(dt, 2))
    # sending in progress and, at the same time, other rspeak commands doing the recovery
    reset()
    p = subprocess.Popen([RSPEAK, "send", "--to", "all", "Concurrent"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    rounds = 0
    while p.poll() is None:
        rspeak("list"); rounds += 1
    rspeak("list")
    lines = sh(f"cut -d' ' -f1 {VAR}/sent/1/delivery").stdout.split()
    n_tot = len(sh(f"cat {VAR}/sent/1/recipients").stdout.split())
    record("F5", "Faults", "rspeak list repeated while rspeak send delivers: the recovery does not interfere",
           "one delivery per recipient, no duplicates, sending complete",
           len(lines) == n_tot == len(set(lines)) and p.returncode == 0 and not os.path.exists(f"{VAR}/sent/1/incomplete"),
           f"{len(lines)} deliveries recorded for {n_tot} recipients, {len(set(lines))} distinct",
           rspeak_list_during_sending=rounds)
    for i in range(60):
        sh(f"userdel -r u{i:02d} 2>/dev/null")

    # confirmation that cannot be written
    reset()
    s = Session("luca")
    rspeak('send --to luca "Confirmation impossible"')
    sh(f"chown root {VAR}/users/luca/acks; chmod 555 {VAR}/users/luca/acks")
    s.clear(); s.write("\n"); s.read_until(QUESTION, 5)
    s.write("y\n")
    ok = s.read_until(r"The confirmation could not be recorded: you will be asked again\.", 5) is not None
    st = state(1, "luca")
    record("F4", "Faults", "the confirmation cannot be written: the message stays and the user is told",
           "notice; state delivered; message still in the mailbox",
           ok and (st or "").startswith("delivered") and os.path.exists(f"{VAR}/users/luca/inbox/1"), st)
    s.close()


# ---- G. security ----

def g_security():
    rspeak('send --to mario "first"')
    sh(f"rm -rf {VAR}/users/mario/inbox; ln -s /etc {VAR}/users/mario/inbox")
    # the link belongs to mario, as if he had made it (lchown: the chown -h of Ubuntu 26.04's
    # coreutils, uutils 0.8, follows the link and would hand /etc itself to mario)
    pw = pwd.getpwnam("mario")
    os.lchown(f"{VAR}/users/mario/inbox", pw.pw_uid, pw.pw_gid)
    r = rspeak('send --to mario "attack"')
    record("G1", "Security", "the mailbox is a link to /etc: root does not write there",
           "no file 2 in /etc; mario «sent, not delivered»",
           not os.path.exists("/etc/2") and not os.path.exists("/etc/2.tmp")
           and (state(2, "mario") or "").startswith("sent, not delivered"), r.stderr.strip()[:160])
    sh(f"rm -f {VAR}/users/mario/inbox")
    s = Session("anna")
    s.clear()
    rspeak("send --to anna $'Text \\e[31mred\\e[0m \\e]0;title\\a \\a end'")
    s.read_until("end", 5)
    record("G2", "Security", "escape sequences in the text: they do not reach the terminal", "no ESC in the text received",
           "Text red" in ANSI.sub("", s.buf) and "\x1b[31m" not in s.buf and "\x1b]0;" not in s.buf and "\x07" not in s.buf.split("Text")[-1],
           repr(s.buf[s.buf.find("Text"):s.buf.find("Text") + 40]))
    s.close()
    rspeak('send --to luca "forged"')
    sh(f"printf '1 \\033[31mfake\\033]0;x\\007%0500d' 0 > {VAR}/users/luca/acks/4; chown luca {VAR}/users/luca/acks/4")
    out = rspeak("status 4").stdout
    record("G3", "Security", "forged confirmation with escapes and 500 bytes: rspeak status stays clean",
           "no ESC in the output, at most 200 bytes read", "\x1b" not in out and len(out) < 1000, out.splitlines()[-1][:120])
    r = as_ordinary_user("mario", f"env RSPEAK_TEST=1 {RSPEAK} list")
    record("G4", "Security", "an ordinary user with RSPEAK_TEST=1 gets nothing", "permission denied",
           denied(r), r.stderr.strip())


# ---- K. shells other than bash ----

def k_shells():
    """zsh and fish: question at login and at every prompt; ksh and dash (which read /etc/profile):
    question at login; for all of them, the text in the terminal when the message is sent."""
    mid = 0
    for user, (shell, prompt) in TEST_SHELLS.items():
        if sh(f"getent passwd {user}").returncode:
            record(f"K-{shell}", "Shells", f"{shell}: test user {user}", "present", None, "user missing")
            continue
        # a login shell that already fails on the distribution's own files (Fedora's
        # /etc/profile.d/lang.sh is not POSIX: dash stops there) does not test RootSpeak
        # (a real login, «-ksh» as its name: openSUSE's ksh is an alternatives wrapper that exits 255 then)
        r = sh(f"runuser -l {user} -c true </dev/null")
        err = r.stderr.strip()
        if r.returncode or (err and "rootspeak" not in err):
            record(f"K-{shell}", "Shells", f"{shell}: the login shell works on this distribution",
                   "no error before RootSpeak", None, (err.splitlines()[0][:150] if err else f"exit {r.returncode}"))
            continue
        mid += 1
        rspeak(f'send --to {user} "At login with {shell}"')
        s = open_session(user)
        dt = s.read_until(QUESTION, 15)
        record(f"K1-{shell}", "Shells", f"{shell}: at login the message and the question", "text and question at login",
               dt is not None and f"At login with {shell}" in s.text(), s.text()[-80:] if dt is None else "")
        s.write("y\n")
        s.read_until(prompt, 8)
        st = state(mid, user) or ""
        record(f"K2-{shell}", "Shells", f"{shell}: confirmation at login", "confirmed (terminal)",
               st.startswith("confirmed"), st)
        mid += 1
        s.clear()
        rspeak(f'send --to {user} "During the {shell} session"')
        dt = s.read_until(f"During the {shell} session", 5)
        record(f"K3-{shell}", "Shells", f"{shell}: user logged in, the text appears in the terminal",
               "text in the terminal", dt is not None, s.text()[-80:] if dt is None else "")
        s.clear()
        s.write("\n")
        if shell in ("zsh", "fish"):
            dt = s.read_until(QUESTION, 5)
            record(f"K4-{shell}", "Shells", f"{shell}: pressing Enter the question appears",
                   "question at the next prompt", dt is not None, s.text()[-80:] if dt is None else "",
                   seconds=round(dt, 3) if dt else None)
            s.write("y\n")
            s.read_until(CONFIRMED, 5)
            st = state(mid, user) or ""
            record(f"K5-{shell}", "Shells", f"{shell}: confirmation at the prompt", "confirmed (terminal)",
                   st.startswith("confirmed"), st)
        else:
            s.read_until(prompt, 3)
            st = state(mid, user) or ""
            record(f"K4-{shell}", "Shells", f"{shell}: no question at the prompt (it comes at the next login)",
                   "no question, delivered", "Do you confirm" not in s.text() and st.startswith("delivered"), st)
        s.close()


# ---- L. language: RootSpeak speaks English to everyone ----

def l_language():
    """The system is in Italian and so is mario's session: RootSpeak still writes English."""
    s = Session("mario", command="LANG=it_IT.UTF-8 LANGUAGE=it exec bash -il")
    s.clear()
    s.write('echo "session language: $LANG"\n')
    italian = s.read_until(r"session language: it_IT", 5) is not None
    s.clear()
    rspeak('send --to mario "Same text for everyone"')
    ok = s.read_until(r"Same text for everyone", 5) is not None and HEADER in s.text()
    s.clear()
    s.write("\n")
    ok = ok and s.read_until(QUESTION, 5) is not None
    s.write("y\n")
    ok = ok and s.read_until(CONFIRMED, 5) is not None
    st = state(1, "mario") or ""
    record("L5", "Language", "a user whose session is in Italian: header, question and answer in English, «y» confirms",
           "«Message from the administrator», «Do you confirm…? [y/N]», «Confirmed.»",
           italian and ok and st.startswith("confirmed"), st if italian else "the session is not in Italian")
    s.close()


# ---- T. the administrators' TUI ----

def t_tui():
    """rspeak without arguments, as root, in a terminal: the TUI on the real store."""
    import fcntl, struct, termios
    rspeak('send --to mario,anna --title Test "From the TUI"')
    s = Session.__new__(Session)
    s.user, s.buf = "root", ""
    s.pid, s.fd = pty.fork()
    if s.pid == 0:
        # the size before rspeak starts: set later, rspeak could read 0×0 and open the help in the pager
        fcntl.ioctl(0, termios.TIOCSWINSZ, struct.pack("HHHH", 30, 120, 0, 0))
        os.execvpe(RSPEAK, ["rspeak"], dict(os.environ, TERM="xterm-256color"))
    ok1 = s.read_until(r"2 delivered", 10) is not None and "RootSpeak · sent messages" in s.text()
    record("T1", "TUI", "rspeak without arguments as root: the list with the recipients in the three states",
           "«RootSpeak · sent messages», «2 delivered»", ok1, s.text()[-120:] if not ok1 else "")
    s.clear(); s.write("\r")
    ok2 = s.read_until(r"anna.*delivered", 10) is not None and "mario" in s.text()
    s.clear(); s.write("\t")
    ok3 = s.read_until(r"sent by root", 10) is not None
    record("T2", "TUI", "detail: recipients and history from the log", "anna, mario; «sent by root»", ok2 and ok3)
    s.write("\x1b"); time.sleep(0.5); s.write("q")
    st = 1
    for _ in range(50):   # at most 5 seconds, then it is killed: a stuck TUI must not stop the run
        try:
            pid, st = os.waitpid(s.pid, os.WNOHANG)
        except ChildProcessError:
            break
        if pid:
            break
        time.sleep(0.1)
    else:
        os.kill(s.pid, signal.SIGKILL)
        os.waitpid(s.pid, 0)
        st = 1
    record("T3", "TUI", "q: the TUI exits and gives the terminal back", "exit status 0",
           os.WIFEXITED(st) and os.WEXITSTATUS(st) == 0)


# ---- J. event log ----

def j_log():
    s = Session("mario")
    rspeak('send --to mario,anna "History"')
    s.clear(); s.write("\n"); s.read_until(QUESTION, 5)
    s.write("n\n"); s.read_until(r"You will be asked again in", 5)
    s.close()
    s = open_session("mario")
    s.read_until(QUESTION, 10); s.write("y\n"); s.read_until(CONFIRMED, 5)
    s.close()
    rspeak("revoke 1")
    time.sleep(1)
    out = rspeak("log 1").stdout
    expected = ["message 1 sent by root", "message 1 delivered to anna", "message 1 delivered to mario",
                "user mario: postponed message 1 (terminal)",
                "user mario: confirmed reading message 1 (terminal pts/", "message 1 revoked by root"]
    missing = [a for a in expected if a not in out]
    record("J1", "Log", "rspeak log: the history of the message", "sending, deliveries, postponement, confirmation, revocation",
           not missing, "missing: " + ", ".join(missing) if missing else f"{len(out.splitlines()) - 1} events")
    uid = pwd.getpwnam("mario").pw_uid
    ev = sh("journalctl -q -o cat --output-fields=_UID RSPEAK_MESSAGE=1 RSPEAK_EVENT=CONFIRMED RSPEAK_USER=mario").stdout.split()
    record("J2", "Log", "the confirmation in the journal carries the user who wrote it (_UID)",
           f"_UID {uid}", str(uid) in ev, " ".join(ev))
    # a user writes into the journal a fake confirmation in the name of another
    sh("runuser -u luca -- sh -c 'printf \"MESSAGE=fake\\nSYSLOG_IDENTIFIER=rspeak\\nRSPEAK_EVENT=CONFIRMED\\n"
       "RSPEAK_MESSAGE=1\\nRSPEAK_USER=anna\\nRSPEAK_CHANNEL=desktop\\n\" | logger --journald'")
    time.sleep(1)
    out = rspeak("log 1").stdout
    luca = pwd.getpwnam("luca").pw_uid
    fake = [r for r in out.splitlines() if "user anna: confirmed" in r]
    record("J3", "Log", "an event written by a user in the name of another: rspeak log flags it",
           f"«[not trustworthy: written by UID {luca}]»",
           bool(fake) and all(f"[not trustworthy: written by UID {luca}]" in r for r in fake)
           and not any("not trustworthy" in r for r in out.splitlines() if r not in fake),
           " / ".join(fake)[:160])


# ---- H. performance ----

def h_performance():
    n_users = 50
    for i in range(n_users):
        sh(f"id p{i:02d} >/dev/null 2>&1 || useradd -m -s /bin/bash p{i:02d}")
    t0 = time.time()
    rspeak('send --to all "Measure"')
    t_send = time.time() - t0
    for k in range(9):
        rspeak(f'send --to all "Measure {k}"')
    n_rcpt = len(sh(f"cat {VAR}/sent/1/recipients").stdout.split())
    t0 = time.time()
    rspeak("list")
    t_list = time.time() - t0
    t0 = time.time()
    rspeak("status 1")
    t_status = time.time() - t0
    record("H1", "Performance", f"sending to all ({n_rcpt} recipients)", "measure", True,
           seconds=round(t_send, 2), ms_per_recipient=round(1000 * t_send / n_rcpt, 1))
    record("H2", "Performance", f"rspeak list with 10 messages × {n_rcpt} recipients", "measure (item 15 of the review)", True,
           seconds=round(t_list, 2))
    record("H3", "Performance", f"rspeak status of a message with {n_rcpt} recipients", "measure", True,
           seconds=round(t_status, 2))
    for i in range(n_users):
        sh(f"userdel -r p{i:02d} 2>/dev/null")


# ---- I. desktop ----

def desk(*args):
    """Looks at or uses the RootSpeak dialogs in DESK's graphical session (tests/vm/desktop.py)."""
    uid = pwd.getpwnam(DESK).pw_uid
    env = f"DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/{uid}/bus XDG_RUNTIME_DIR=/run/user/{uid}"
    return sh(f"runuser -u {DESK} -- env {env} python3 /opt/rootspeak-src/tests/vm/desktop.py "
              + " ".join(shlex.quote(a) for a in args)).stdout.strip()


def n_windows():
    try:
        return int(desk("windows") or 0)
    except ValueError:
        return 0


def wait_windows(n, duration):
    """Waits until the open RootSpeak dialogs are n; returns the seconds, or None."""
    t0 = time.time()
    while time.time() - t0 < duration:
        if n_windows() == n:
            return round(time.time() - t0, 2)
        time.sleep(0.2)
    return None


def window_text(duration=6):
    """The text of the first RootSpeak dialog; just after a login the desktop's accessibility
    may expose the window before its content, so it tries again."""
    t0 = time.time()
    t = ""
    while time.time() - t0 < duration:
        t = desk("text")
        if "|" in t:
            break
        time.sleep(0.3)
    return t


def wait_state(mid, user, test, duration=8):
    """Waits until the recipient's state satisfies test(state): the agent records
    confirmations and postponements a moment after the dialog closes."""
    t0 = time.time()
    st = ""
    while time.time() - t0 < duration:
        st = state(mid, user) or ""
        if test(st):
            break
        time.sleep(0.2)
    return st


def capture(name):
    """Asks tests/vm/run.sh (outside the VM) for a screenshot, and leaves it the time to take it."""
    print(f"@@CAPTURE {name}", flush=True)
    time.sleep(2.5)


def agent_pids():
    return sh(f"pgrep -u {DESK} -f '^(/bin/bash )?{AGENT}$'").stdout.split()


def agent_running():
    return bool(agent_pids())


def agent_language():
    """The locale of the graphical session, read from the agent's environment."""
    pids = agent_pids()
    if not pids:
        return ""
    try:
        env = open(f"/proc/{pids[0]}/environ", "rb").read().decode("utf-8", "replace")
    except OSError:
        return ""
    v = dict(x.split("=", 1) for x in env.split("\0") if "=" in x)
    return v.get("LC_ALL") or v.get("LC_MESSAGES") or v.get("LANG") or ""


def session_type():
    """The kind of graphical session logind gives the desktop user: Wayland or X11, as it really is."""
    sid = sh(f"loginctl show-user {DESK} -p Display --value").stdout.strip()
    t = sh(f"loginctl show-session {sid} -p Type --value").stdout.strip() if sid else ""
    return {"wayland": "Wayland", "x11": "X11"}.get(t, t or "an unknown session type")


def i_desktop():
    if not DESK:
        record("I1", "Desktop", "confirmation dialog in the graphical session", f"dialog «{DLG_OK}»",
               None, "the container has no graphical session: the dialog is tested in the VM (tests/vm)")
        return
    graphical = sh(f"loginctl show-user {DESK} -p Display --value").stdout.strip()
    desktop_lang = agent_language()
    record("I0", "Desktop", f"{DESK} has a graphical session with the RootSpeak agent running "
           "(run.sh checks the start from the automatic login before the scenarios)",
           "graphical session, agent running", bool(graphical) and agent_running(), f"session {graphical}")

    t0 = time.time()
    rspeak(f'send --to {DESK} --title Maintenance "Server off on Saturday from 8 to 12."')
    dt = wait_windows(1, 20)
    text = window_text()
    title = desk("title")
    record("I1", "Desktop", "the dialog appears by itself after the sending",
           f"dialog «{DLG_TITLE}» with title and text",
           dt is not None and "Server off on Saturday" in text and title == DLG_TITLE,
           f"{title} | {text[:120]}",
           seconds_to_dialog=round(time.time() - t0, 2) if dt is not None else None)
    capture("I1-window")
    clicked = desk("click", DLG_OK) == "pressed"
    closed = wait_windows(0, 10)
    st = wait_state(1, DESK, lambda x: x.startswith("confirmed"))
    record("I2", "Desktop", f"«{DLG_OK}»: the dialog closes and the confirmation is recorded",
           "confirmed (desktop)", closed is not None and st.startswith("confirmed") and st.endswith("(desktop)"), st)
    record("I12", "Desktop", "desktop session in Italian: the dialog is in English",
           f"session it_IT; title «{DLG_TITLE}», button «{DLG_OK}»",
           desktop_lang.startswith("it") and title == DLG_TITLE and clicked,
           f"session language {desktop_lang or 'unknown'}; title «{title}»")

    # quick reminders for the test; the agent restarts and reads the configuration again
    sh("printf 'RSPEAK_REMIND_MINUTES=1\nRSPEAK_AGENT_POLL=5\n' > /etc/rootspeak/rootspeak.conf")
    sh(f"pkill -u {DESK} -f '^(/bin/bash )?{AGENT}$'")
    time.sleep(1)
    t0 = time.time()
    rspeak(f'send --to {DESK} "Second message"')
    dt = wait_windows(1, 30)
    record("I8", "Desktop", "agent not running: rspeak send starts it (systemd-run) and the dialog appears",
           "agent running, dialog", dt is not None and agent_running(),
           seconds_to_dialog=round(time.time() - t0, 2) if dt is not None else None)
    desk("click", DLG_LATER)
    wait_windows(0, 10)
    st = wait_state(2, DESK, lambda x: "postponed on" in x)
    record("I3", "Desktop", f"«{DLG_LATER}»: the dialog closes, the message stays delivered",
           "delivered, postponed on …", st.startswith("delivered") and "postponed on" in st, st)
    t0 = time.time()
    dt = wait_windows(1, 120)
    record("I4", "Desktop", "after the postponement (1 minute for the test) the dialog comes back",
           "dialog again, after about 60 s", dt is not None, seconds_to_reappearance=dt)
    desk("click", DLG_LATER)
    wait_windows(0, 10)
    # the reminder comes after the postponement, as when an administrator asks for it
    wait_state(2, DESK, lambda x: "postponed on" in x)
    t0 = time.time()
    rspeak("remind 2")
    dt = wait_windows(1, 20)
    diag = "" if dt is not None else " | ".join([
        sh(f"{RSPEAK} remind 2").stdout.strip(), state(2, DESK) or "", sh(f"ls -la {VAR}/users/{DESK}/state {VAR}/users/{DESK}/inbox").stdout.replace("\n", " "),
        sh(f"pgrep -a -u {DESK} rootspeak-user").stdout.replace("\n", " "), sh(f"pgrep -a -u {DESK} zenity").stdout.replace("\n", " "),
        sh(f"cat /run/user/$(id -u {DESK})/rootspeak-agent.ready").stdout.strip()])
    record("I11", "Desktop", f"rspeak remind after «{DLG_LATER}»: the dialog comes back at once", "dialog within a few seconds",
           dt is not None, diag, seconds_to_reappearance=round(time.time() - t0, 2) if dt is not None else None)
    desk("click", DLG_OK)
    wait_windows(0, 10)

    rspeak(f'send --to {DESK} "Confirmed from the terminal"')
    wait_windows(1, 20)
    s = open_session(DESK)
    s.read_until(QUESTION, 15)
    t0 = time.time()
    s.write("y\n")
    dt = wait_windows(0, 10)
    st = wait_state(3, DESK, lambda x: x.startswith("confirmed"))
    record("I5", "Desktop", "confirmation from a terminal with the dialog open: the dialog closes by itself",
           "dialog closed, confirmed (terminal)", dt is not None and "(terminal" in st, st,
           seconds_to_closing=round(time.time() - t0, 2) if dt is not None else None)
    s.close()

    rspeak(f'send --to {DESK} "To be revoked"')
    wait_windows(1, 20)
    t0 = time.time()
    rspeak("revoke 4")
    dt = wait_windows(0, 10)
    record("I6", "Desktop", "revocation with the dialog open: the dialog closes by itself", "dialog closed",
           dt is not None, seconds_to_closing=round(time.time() - t0, 2) if dt is not None else None)

    rspeak(f'send --to {DESK} "First of two"')
    rspeak(f'send --to {DESK} "Second of two"')
    wait_windows(1, 20)
    t1 = window_text()
    desk("click", DLG_OK)
    time.sleep(1)
    dt = wait_windows(1, 15)
    t2 = window_text()
    desk("click", DLG_OK)
    st = wait_state(6, DESK, lambda x: x.startswith("confirmed"))
    record("I7", "Desktop", "two messages: the dialogs appear one after the other, oldest first",
           "«First of two», then «Second of two», both confirmed",
           "First of two" in t1 and dt is not None and "Second of two" in t2 and st.startswith("confirmed"),
           f"{t1[-30:]} → {t2[-30:]}; {st}")
    wait_windows(0, 10)

    # «I have read it» and leaving the session at once: the confirmation must not get lost.
    # Through AT-SPI the press reaches zenity some hundred milliseconds after doAction returns
    # (a real key press: about 40 ms); the session is closed as soon as zenity has the answer
    # and has exited, which is sooner than any person can log out.
    rspeak(f'send --to {DESK} "Click and go"')
    wait_windows(1, 20)
    t0 = time.time()
    desk("click", DLG_OK)
    answered = None
    while time.time() - t0 < 5:
        if not sh(f"pgrep -u {DESK} -x zenity").stdout.strip():
            answered = round(time.time() - t0, 2)
            break
        time.sleep(0.01)
    sh(f"loginctl terminate-user {DESK}")
    time.sleep(2)
    st = state(7, DESK) or ""
    record("I10", "Desktop", f"«{DLG_OK}» and out of the session as soon as the dialog has the answer: the confirmation stays",
           "confirmed (desktop)", answered is not None and st.startswith("confirmed"), st, seconds_click_to_answer=answered)

    # leaving the session with the dialog open: not a postponement, the dialog comes back at the login
    time.sleep(1)
    sh("systemctl restart display-manager")
    wait_windows(0, 90)
    t0 = time.time()
    while time.time() - t0 < 90 and not agent_running():
        time.sleep(0.5)
    rspeak(f'send --to {DESK} "Left open"')
    wait_windows(1, 20)
    sh(f"loginctl terminate-user {DESK}")
    time.sleep(2)
    st13 = state(8, DESK) or ""

    # message waiting, then graphical login
    time.sleep(1)
    rspeak(f'send --to {DESK} "Waiting for the login"')
    t0 = time.time()
    sh("systemctl restart display-manager")   # gdm, sddm or lightdm
    dt = wait_windows(1, 90)
    t13 = window_text()
    record("I13", "Desktop", "session ended with the dialog open: no postponement, the dialog comes back at the login",
           "delivered without postponement; «Left open» first at the login",
           st13.startswith("delivered") and "postponed" not in st13 and "Left open" in t13, f"{st13}; {t13[-40:]}")
    if "Left open" in t13:
        desk("click", DLG_OK)
        wait_windows(0, 10)
        dt2 = wait_windows(1, 20)
        dt = dt if dt2 is not None else None
    t9 = window_text()
    record("I9", "Desktop", "message sent while the desktop was closed: the dialog appears at the graphical login",
           "dialog after the automatic login", dt is not None and "Waiting for the login" in t9, t9[-60:],
           seconds_from_login_restart=round(time.time() - t0, 2) if dt is not None else None)
    capture("I9-login")
    desk("click", DLG_OK)
    wait_windows(0, 10)
    sh("printf 'RSPEAK_REMIND_MINUTES=30\nRSPEAK_AGENT_POLL=60\n' > /etc/rootspeak/rootspeak.conf")


# ---- P. packages ----

def p_packages():
    """The package of the distribution, installed by run.sh with the package
    manager: what it installed, reinstalling, install.sh refusing, removing,
    purging (apt), and moving from the archive to the package. Last: it removes RootSpeak."""
    mgr = sh(f"{PKG} manager").stdout.strip()
    admins = sh("getent group sudo >/dev/null && echo sudo || echo wheel").stdout.strip()
    hooks = lambda: int(sh("cat /etc/bash.bashrc /etc/zsh/zshrc /etc/zshrc 2>/dev/null | grep -c '# RootSpeak hook'").stdout.strip() or 0)
    want_hooks = sum(os.path.exists(f) for f in ("/etc/bash.bashrc",)) + (1 if sh("command -v zsh").returncode == 0 else 0)
    known = {"apt": "dpkg -s rootspeak", "dnf": "rpm -q rootspeak", "zypper": "rpm -q rootspeak",
             "pacman": "pacman -Q rootspeak"}[mgr]
    perm = sh("stat -c '%U:%G %a' /usr/bin/rspeak").stdout.strip()
    record("P1", "Packages", f"the package installed with {mgr}: the command in /usr/bin, of root and the administrators",
           f"package known, root:{admins} 750, {want_hooks} hook lines",
           sh(known).returncode == 0 and perm == f"root:{admins} 750" and hooks() == want_hooks
           and not os.path.exists("/usr/local/bin/rspeak"), f"{perm}, {hooks()} hook lines")
    # what the package manager checks: only the group of rspeak differs (set at installation)
    verify = {"apt": "dpkg --verify rootspeak", "dnf": "rpm -V rootspeak", "zypper": "rpm -V rootspeak",
              "pacman": "pacman -Qkk rootspeak 2>&1"}[mgr]
    # (the Arch image and Ubuntu's minimized ones do not extract /usr/share/doc:
    # NoExtract in pacman.conf, path-exclude in dpkg.cfg.d)
    noextract = sh("grep -s '^NoExtract' /etc/pacman.conf; grep -hs '^path-exclude' /etc/dpkg/dpkg.cfg.d/*").stdout
    out = [l for l in sh(verify).stdout.splitlines() if l.strip() and "/usr/bin/rspeak" not in l
           and "rootspeak.conf" not in l and "altered files" not in l
           and not ("usr/share/doc" in noextract and "/usr/share/doc" in l)]
    record("P2", "Packages", "the package manager finds the files as the package installed them",
           "no difference but the group of rspeak", not out, "; ".join(out)[:200])
    sh("echo 'RSPEAK_REMIND_MINUTES=45' >> /etc/rootspeak/rootspeak.conf")
    rspeak('send --to mario "before reinstalling"')
    r = sh(f"{PKG} reinstall")
    perm = sh("stat -c '%U:%G %a' /usr/bin/rspeak").stdout.strip()
    record("P3", "Packages", "reinstalling (as an upgrade does): messages, configuration and hooks stay as they were",
           f"message 1 still there, edited configuration kept, root:{admins} 750, {want_hooks} hook lines",
           r.returncode == 0 and state(1, "mario") is not None and "=45" in open("/etc/rootspeak/rootspeak.conf").read()
           and perm == f"root:{admins} 750" and hooks() == want_hooks, (r.stderr.strip() or perm)[:200])
    sh("rm -rf /opt/archive && mkdir /opt/archive && tar -C /opt/archive --strip-components=1 -xzf /opt/release/rootspeak-*-linux-x86_64.tar.gz")
    r = sh("/opt/archive/install.sh")
    record("P4", "Packages", "install.sh with the package installed: it refuses and says to use the package manager",
           "exit 1, the message, nothing in /usr/local",
           r.returncode == 1 and "installed from a package" in r.stderr and not os.path.exists("/usr/local/bin/rspeak"),
           r.stderr.strip()[:200])
    r = sh(f"{PKG} remove")
    left = [f for f in ("/usr/bin/rspeak", "/usr/lib/rootspeak", "/etc/profile.d/rootspeak.sh",
                        "/etc/xdg/autostart/rootspeak-agent.desktop", "/etc/fish/conf.d/rootspeak.fish") if os.path.exists(f)]
    record("P5", "Packages", "removing the package: programs and hooks go, messages stay",
           "no files of RootSpeak, no hook lines, message 1 in the store",
           r.returncode == 0 and not left and hooks() == 0 and os.path.exists(f"{VAR}/sent/1"),
           ", ".join(left) or r.stderr.strip()[:200])
    # from the archive to the package: the archive's programs go, the messages and its
    # settings stay, without questions (dpkg must not know RootSpeak, as on a machine that
    # never had the package: after apt remove it still knows the settings, hence the purge)
    if mgr == "apt":
        sh("dpkg --purge rootspeak")
    r = sh("/opt/archive/install.sh")
    ok = r.returncode == 0 and os.path.exists("/usr/local/bin/rspeak")
    sh("echo 'RSPEAK_REMIND_MINUTES=50' >> /etc/rootspeak/rootspeak.conf")
    rspeak_old = sh('/usr/local/bin/rspeak send --to anna "from the archive"')
    # (its number: 1 after the purge above, 2 otherwise)
    m = re.search(r"Message (\d+) sent", rspeak_old.stdout)
    mid = int(m.group(1)) if m else 0
    if mgr == "pacman":
        # pacman does not install over files it does not know (those of install.sh in /etc):
        # it refuses without touching anything, and the archive is removed first
        r = sh(f"{PKG} install")
        ok = ok and r.returncode != 0 and "exists in filesystem" in r.stderr + r.stdout \
            and os.path.exists("/usr/local/bin/rspeak")
        ok = ok and sh("/opt/archive/install.sh --uninstall").returncode == 0
    r = sh(f"{PKG} install")
    zline = sh("grep -h '# RootSpeak hook' /etc/zsh/zshrc /etc/zshrc 2>/dev/null").stdout
    # (dpkg asks about a configuration file it does not know: without a terminal it prints the question)
    asked = "Configuration file" in r.stdout + r.stderr
    kept = "=50" in open("/etc/rootspeak/rootspeak.conf").read()
    record("P6", "Packages", "the package over an installation from the archive: it takes its place, "
           "keeps its settings and asks nothing (pacman: it refuses, and takes it after install.sh --uninstall)",
           "nothing left in /usr/local, the archive's message still there, settings kept, no question, hooks pointing to /usr",
           ok and rspeak_old.returncode == 0 and r.returncode == 0 and not os.path.exists("/usr/local/bin/rspeak")
           and not os.path.exists("/usr/local/lib/rootspeak") and state(mid, "anna") is not None
           and hooks() == want_hooks and "/usr/local" not in zline and kept and not asked,
           ("asked about the configuration file; " if asked else "") + ("settings lost; " if not kept else "")
           + (r.stdout + r.stderr).strip()[-160:])
    if mgr == "apt":
        r = sh(f"{PKG} purge")
        record("P7", "Packages", "apt purge: also messages and configuration go",
               "no /var/lib/rootspeak, no /etc/rootspeak",
               r.returncode == 0 and not os.path.exists(VAR) and not os.path.exists("/etc/rootspeak"), r.stderr.strip()[:200])
    else:
        r = sh(f"{PKG} remove")
        record("P7", "Packages", f"removing with {mgr}: the messages stay (only apt has purge)",
               f"{VAR} kept", r.returncode == 0 and os.path.exists(f"{VAR}/sent/{mid}"), r.stderr.strip()[:200])


# ---- report ----

def report():
    os.makedirs(OUT, exist_ok=True)
    meta = dict(date=time.strftime("%Y-%m-%d %H:%M:%S %Z"), version=VERSION,
                system=sh(". /etc/os-release; echo $PRETTY_NAME").stdout.strip()
                + (f", VM with {os.environ.get('RSPEAK_TEST_DESKTOP_LABEL') or 'GNOME'} on {session_type()}, desktop of {DESK}"
                   if DESK else ", container with systemd"),
                ok=sum(r["outcome"] == "OK" for r in results), failed=sum(r["outcome"] == "NO" for r in results),
                not_tested=sum(r["outcome"] == "--" for r in results), total=len(results),
                commit=os.environ.get("RSPEAK_TEST_COMMIT", "unknown"),
                fingerprint=os.environ.get("RSPEAK_TEST_FINGERPRINT", "unknown"),
                only=os.environ.get("RSPEAK_TEST_ONLY", ""))
    with open(f"{OUT}/results.json", "w") as f:
        json.dump(dict(meta=meta, results=results), f, ensure_ascii=False, indent=1)
    lines = [f"# RootSpeak tests {'in the VM with a desktop' if DESK else 'in the test machine'}\n",
             f"- Date: {meta['date']}", f"- {meta['version']}", f"- System: {meta['system']}",
             f"- Code: commit {meta['commit']}, fingerprint {meta['fingerprint']}",
             f"- Outcome: **{meta['ok']} passed, {meta['failed']} failed, {meta['not_tested']} not tested** "
             f"out of {meta['total']} scenarios\n",
             "| Code | Area | Scenario | Expected | Outcome | Measures / details |", "|---|---|---|---|---|---|"]
    for r in results:
        mes = ", ".join(f"{k} {v}" for k, v in r["measures"].items() if v is not None)
        det = (mes + ("; " if mes and r["details"] else "") + (r["details"] or "")).replace("|", "¦").replace("\n", " ")
        lines.append(f"| {r['code']} | {r['area']} | {r['description']} | {r['expected']} | {r['outcome']} | {det[:200]} |")
    with open(f"{OUT}/report.md", "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\n{meta['ok']} passed, {meta['failed']} failed, {meta['not_tested']} not tested out of {meta['total']}; "
          f"results in {OUT}")
    return meta["failed"] == 0


if __name__ == "__main__":
    only = os.environ.get("RSPEAK_TEST_ONLY", "").split(",")   # for example i_desktop
    VERSION = sh(f"{RSPEAK} version").stdout.strip()   # (now: the package scenarios remove RootSpeak)
    for fn in (a_access, b_recipients, c_delivery, d_confirmation, e_expiry_revocation, f_faults, g_security,
               j_log, t_tui, k_shells, l_language, h_performance, i_desktop, p_packages):
        if fn is p_packages and not PACKAGE:
            continue
        if only != [""] and fn.__name__ not in only:
            continue
        print(fn.__name__)
        scenario(fn)
    sys.exit(0 if report() else 1)
