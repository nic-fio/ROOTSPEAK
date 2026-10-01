# Adversarial review of 30 September 2026

The project went through two independent critical reviews, made by two
frontier language models on the technical manual of version 0.1.0:

- **Revisione A** — «Relazione critica su AMS 0.1.0» (AMS was RootSpeak's former name) [Critical report on AMS 0.1.0] (24 points and a remediation plan);
- **Revisione B** — «Relazione critica senza sconti — AMS v0.1.0» [Critical report with no discounts — AMS v0.1.0] (the file was received truncated: it stops at point 5.1).

The points about the interface language are left out of this list: they were
handled separately (decision of 30 September, done: Italian and English; on
1 October 2026 the translations were removed and RootSpeak now speaks English
only). Every concrete statement was checked against the code before being
accepted. The [2] items of the README stay frozen until groups A–D are closed
(review A, point 23).

Status: **open**, **done**, **not accepted**.

**As of 30 September 2026 every accepted point is done, including the hook for all shells and each user's own language decided on 30 September (the languages were later removed, on 1 October); replies from users to the administrator are not planned (the user's decision).** The live suites found further defects, fixed and described below and in the technical manual (chapters «The message store», «Receiving in the terminal» and the specification).

## A. Real defects, checked in the code

| # | Point | Source | Status |
|---|---|---|---|
| 1 | If the confirmation could not be written (full disk, permissions), RootSpeak treated it as «already confirmed»: the message moved among the read ones without a confirmation and the user read «Confirmed». Now the confirmation is published with `ln` (exclusive); a failure leaves the message in the mailbox, warns the user and goes into the log. Test: `tests/engine.sh`, group 1 (fails with the previous code). | B 3.1, A 20 | done |
| 2 | An `rspeak send` interrupted halfway left recipients without a copy, never recovered. Now every delivery is checked and noted per recipient; `sent/ID/incomplete` stays as long as a copy is missing and the next `rspeak` command completes the sending; a failure for one recipient does not stop the others; new state «not delivered», distinct from «to be confirmed»; a sending interrupted before it is saved is cancelled. Test: `tests/engine.sh`, group 2 (6 checks fail with the previous code). The live suite then found that the recovery, started during a sending still in progress, delivered in parallel and noted duplicates: now `rspeak send` holds a lock (`sent/ID/lock`) and the recovery skips the sendings in progress (scenarios F3 and F5; 2 checks of `tests/engine.sh`). | A 4 | done |
| 3 | A desktop agent that had just started died if woken while starting (20 out of 20 in one test). Now it sets up the reception of the signal as its first instruction and, when it is ready, writes its PID in `rootspeak-agent.ready`; `rspeak send` wakes only that PID (with `pkill -F` and the exact command line, as the user) and otherwise starts an agent. Test: `tests/engine.sh`, group 5. | A 11 | done |
| 4 | A dialog or a question opened before the expiry accepted the confirmation after it. Now they close at the expiry; `ack` refuses an expired message; `rspeak status` does not count a confirmation with a time later than the expiry of the reference copy (`sent/`), even if the user altered their own copy. Test: `tests/engine.sh`, group 4. | A 15 | done |

## B. Specification and model

| # | Point | Source | Status |
|---|---|---|---|
| 5 | Formal state machine, invariants, behaviour after a crash, store format: the «Specification» chapter of the technical manual (states and transitions with preconditions, atomic operations and events; 11 invariants; table of interruptions and repairs; store format 1). Writing it brought out, and fixed, one case: a confirmation written but a message not yet moved, which was shown again. | A 2, 4, 13, 22; B 3.4 | done |
| 6 | Tell delivered, shown and confirmed apart. Solved by simplifying, by the user's decision: every message asks for confirmation and every recipient has three states, sent, delivered (copy in the mailbox), confirmed; the «shown» state and the `info` level are gone. Test: `tests/engine.sh`, group 3. | A 3; B 4.1 | done |
| 7 | Per-message event log: structured events in the journal (`RSPEAK_EVENT`, `RSPEAK_MESSAGE`, `RSPEAK_USER`, `RSPEAK_CHANNEL`, plus `_UID` set by the journal) for sending, delivery, failed delivery, recovery, cancellation, postponement, confirmation, failed confirmation, revocation; new command `rspeak log ID`. Scenarios J1 and J2. | A 5 | done |
| 8 | The user's mailbox is not the authoritative source: specification, «Authoritative sources»; applied to the expiry too (point 4). | A 7 | done |
| 9 | Semantics of revocation, expiry and the clock: specification, «Time, revocation and expiry». | A 14, 15, 16 | done |
| 10 | Version of the message format: every message starts with `format: 1`. Test: `tests/engine.sh`, group 5. | B 3.3 | done |

## C. Robustness and configuration

| # | Point | Source | Status |
|---|---|---|---|
| 11 | Configuration as data: the configuration reader (`rspeak_load_conf` in the prototype, `conf_read` in C) accepts only the known keys with positive whole numbers and runs nothing. Test: group 5 (a file with `$(…)` is not run). | A 18 | done |
| 12 | The desktop agent reads the configuration again at every round. | A 19 | done |
| 13 | Supported scope: specification, «Supported and verified scope», and user manual, «Requirements». | A 9 | done |
| 14 | Cleanup: new command `rspeak purge DURATION`, which deletes the older messages with their copies, confirmations and postponements in the mailboxes (as the user) and leaves the event in the log; it skips incomplete sendings and those in progress. Test: `tests/engine.sh`, group 6. | B 2 | done |
| 15 | `list` and `status` slow. Measured (scenarios H), then fixed by reading each mailbox only once per user (a single `runuser` for all their confirmations and postponements) and the deliveries once per message: `list` from about 6 s to about 0.7 s for 10 messages to 54 recipients, `status` from about 1.3 s to about 0.7 s. Copying the confirmations on the root side was not needed. | A 8 | done |

## D. Tests

| # | Point | Source | Status |
|---|---|---|---|
| 16 | Automatic tests of the engine: `tests/engine.sh` plus the live suites in the container and in the VM (the current numbers are in the technical manual, chapter «Tests and checks», read from the results). Covered: concurrency, races, interruptions, altered files and mailboxes, failing tools, security. | A 20 | done |
| 17 | A reproducible environment for the live tests. (The VM then found a third defect: leaving the session right after «I have read it» could lose the confirmation; scenario I10.) Done in two forms: a Debian 13 container with systemd (`tests/container/run.sh`) and a VM with GNOME on Wayland on the test server (`tests/vm/run.sh`, including the desktop dialog scenarios). Outcomes and measures in `tests/*/results/`. The VM found two defects: `online` included root and the system accounts; the agent's lock passed to its child processes (see below). | A 21 | done |

## E. Criticisms not accepted

| Point | Source | Why |
|---|---|---|
| The shell hook can be bypassed; the confirmation is no proof of reading. | B 4.2 | An intended consequence of the decision «never block»: the confirmation is, by design, a statement by the user. |
| If the terminal is busy the message does not arrive. | B 4.1 | Inaccurate: the mailbox acts as a queue, the message arrives at the next prompt or at login. |
| Locks left stuck. | B 4.3 | **Rejected by mistake, then accepted.** The kernel releases the lock when the process dies, but the test VM showed that the agent's lock passed to its children (`sleep`, `zenity`): an orphan child held it for up to 60 s and the new agent exited at once. Fixed (`9>&-`). |
| Bash only. | A 10; B 4.2 | The user's decision of 30 September: the confirmation question must reach every shell (bash, zsh, fish at every prompt; at login for the shells that read `/etc/profile`). Done: hooks for bash, zsh, fish and sh; scenarios K on the test machine. |
| Rewrite at once in a compiled language. | B 3 | Review A is followed: first the specification, then a possible rewrite (done later: version 0.2.0 is in C). |
| `rspeak` always root. | B 5.1 | An explicit decision of the user. |

# Second review (30 September 2026)

Two reviewers examined the technical manual with its covering note (without
the code): **review C** (12 findings, G-01…L-03) and **review D** (7 findings
plus 2 notes on clarity). Every finding was checked against the code or with a
test before being accepted; for every fix there is a test that fails with the
previous code (group 9 of `tests/engine.sh`, scenarios F7 and J3), except where
stated.

| # | Finding | Source | Check | Status |
|---|---|---|---|---|
| 18 | `rspeak revoke` did not wait for an `rspeak send` in progress: a copy could arrive after the revocation. Now the revocation writes `revoked` (on disk), waits for the sending's lock, which stops at the next recipient, then removes the copies; `sent/ID/revoking` stays until they are all removed and the next command completes the job. | C G-01, C M-03 | founded (code) | done |
| 19 | Confirmation and revocation without an order: a confirmation could appear after the revocation. Now `ack` does not confirm without a copy in the mailbox (exit code 3) and `rspeak status` does not count a confirmation dated after `sent/ID/revoked` (same second: it counts). The test on the interrupted question passes with the previous code too, which already noticed it: the fix concerns the window between the check and `ln`, tested with the date rule. | C G-02 | founded (code) | done |
| 20 | A terminal reassigned between the lookup and the writing: the text could end up on another user's terminal. Now the terminal is opened first and the owner of the opened terminal is checked, not the owner of the name (`write_term` with `/dev/fd/5` in the prototype, `write_terminal` in C). | C G-03 | founded (real race, short window) | done |
| 21 | No guarantee after a power cut. Now `sync` of message, recipients and marker before the deliveries, `syncfs` before removing `incomplete`, the confirmation on disk before «Confirmed», the revocation on disk before touching the mailboxes; the recovery checks the copies already noted too. A real power cut is not tested; the vanished copy is simulated. | C G-04, C L-03 | founded | done |
| 22 | Test numbers in the manual old and not tied to the code. Now every suite records the commit and the fingerprint of the code (`tools/fingerprint.sh`); the chapter «Tests and checks» reads the results and says whether they apply to the current code; `tools/check-docs.py` fails if `tests/engine.sh` was not run on the current code. | C M-01, C L-01 | founded | done |
| 23 | «Supported» scope confused with «verified». Now the specification keeps them apart («Supported and verified scope»). | C M-02 | founded (document) | done |
| 24 | `_UID` presented as «unforgeable»: it says who wrote an event, not that the event is true. Text corrected; `rspeak log` flags as unreliable an event written by the wrong user (scenario J3). | C M-04 | founded | done |
| 25 | «Confirmed» must be read as a statement by the user, in audits too: written in the specification and in the glossary. | C M-05 | founded (document) | done |
| 26 | Linearisation points not defined: new paragraph «Concurrent operations» in the specification. | C L-02 | founded (document) | done |
| 27 | `rspeak purge` together with `rspeak list`: a message could vanish halfway through the reading. Now `purge` renames `sent/ID` to `sent/.deleting-ID` (in one step) and `list` first reads what it needs; an interrupted deletion is completed by the next command. | D 1.2, C M-03 | founded | done |
| 28 | Thousands of fake files in `acks/` slowed down `rspeak list` (5000 files: 3.9 s). Now only the messages that exist in `sent/` are read, with a time limit: 25 ms. | D 1.4 | founded (measured) | done |
| 29 | Texts over 128 KiB: zenity cannot receive them as an argument. Now `rspeak send` refuses texts over 65536 bytes. | D 1.6 | founded | done |
| 30 | A message that expires during the sending: the behaviour is written in the specification (the later copies are delivered, nobody sees them). | D 1.7 | founded (document) | done |
| 31 | Clarity: cost of the check at the prompt (chapter «Receiving in the terminal») and format of the store fields (chapter «The message store»). | D, notes | founded | done |

**Not accepted**

| Finding | Source | Why |
|---|---|---|
| A pipe in place of `acks/ID` blocks `rspeak status` | D 1.1 | Inaccurate: only regular files are read; tested, `rspeak status` answers in 0.03 s. A test remains in group 9. |
| A comment at the end of a line in `rootspeak.conf` invalidates the value | D 1.5 | Inaccurate: comments and spaces are handled; tested, a test remains in group 9. |
| A symbolic link `/var/lib/rootspeak` created before the installation | D 1.3 | Outside the model: only root writes in `/var/lib`, and root is already trusted. |
