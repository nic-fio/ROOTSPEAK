# RootSpeak tests in the test machine

- Date: 2026-10-01 18:25:19 UTC
- RootSpeak - Advanced Messaging System for Linux 0.2.0
- System: Red Hat Enterprise Linux 10.2 (Coughlan), container with systemd
- Code: commit 81199e69f0-modified, fingerprint 3368c39af24d
- Outcome: **56 passed, 0 failed, 4 not tested** out of 60 scenarios

| Code | Area | Scenario | Expected | Outcome | Measures / details |
|---|---|---|---|---|---|
| A1 | Access | root sends a message | sending succeeds | OK | Message 1 sent to 1 user. |
| A2 | Access | an administrator (sudo group) sends: rspeak re-runs itself with sudo | sending succeeds, sender admin | OK | seconds 0.156; from: admin |
| A3 | Access | an ordinary user cannot run rspeak | permission denied, no message | OK | runuser: failed to execute /usr/local/bin/rspeak: Permission denied |
| A4 | Access | an ordinary user cannot even open the help | permission denied | OK | runuser: failed to execute /usr/local/bin/rspeak: Permission denied |
| B1 | Recipients | one user | mario | OK | ['mario'] |
| B2 | Recipients | list with a duplicate | anna, mario (once) | OK | ['anna', 'mario'] |
| B3 | Recipients | group @developers | anna, mario | OK | ['anna', 'mario'] |
| B4 | Recipients | all: human users, except root and whoever has nologin | admin, anna, luca, mario, zeno | OK | ['admin', 'anna', 'luca', 'mario', 'zeno'] |
| B5 | Recipients | online: only whoever has an open session | luca | OK | ['luca'] |
| B6 | Recipients | user that does not exist | error, no message created | OK | rspeak: no such user: nobodyhere |
| B7 | Recipients | group without members | error «no recipients» | OK | rspeak: no recipients |
| C1a | Delivery | user logged out: the copy waits in the mailbox | delivered | OK | delivered |
| C1b | Delivery | at login the message and the question appear before the first prompt | text and question at login | OK | seconds_from_login 0.279 |
| C1c | Delivery | confirmation at login | confirmed (terminal) | OK | confirmed on 01/10 18:23 (terminal pts/2) |
| C2a | Delivery | user logged in: the text appears in their terminal | text in the terminal | OK | seconds_send 0.057, seconds_to_terminal 0.108 |
| C2b | Delivery | state after writing to the terminal | delivered, written to 1 terminal | OK | delivered, written to 1 terminal |
| C2c | Delivery | pressing Enter the question appears | question at the next prompt | OK | seconds 0.051 |
| C3 | Delivery | ssh session without a terminal: it is not touched, the copy goes to the mailbox | sending succeeds, delivered, no terminal written | OK | delivered |
| C4a | Delivery | two open sessions: the text appears in both | text in 2 terminals | OK | delivered, written to 2 terminals |
| C4b | Delivery | confirming in one session, the question in the other stops | «Message already confirmed elsewhere» in the other | OK | seconds 0.95 |
| D1 | Confirmation | the user postpones | delivered, postponed on … | OK | delivered, written to 1 terminal, postponed on 01/10 18:24 |
| D2 | Confirmation | after the postponement, only a reminder at the prompt | «You have 1 message…», no question | OK | true [RootSpeak] You have 1 message from the administrator to confirm. [luca@26b3c51311ae ~]$  |
| D5 | Confirmation | rspeak remind after a postponement: the question comes back at the next prompt | «Message 1: 1 recipient reminded.», question at the prompt | OK | Message 1: 1 recipient reminded. |
| D3 | Confirmation | at the next login the postponement does not count: the question comes back | question at login | OK |  |
| D4 | Confirmation | confirmation recorded with date and channel | «EPOCH terminal pts/N» | OK | 1790879047 terminal pts/7 |
| E1 | Expiry | an expired message is not shown at login | no text | OK |  |
| E2 | Expiry | state of an expired message | delivered, not confirmed (expired) | OK | delivered, not confirmed (expired) |
| E3 | Revocation | revocation with the question waiting: the question stops | «The administrator has revoked the message.» | OK | seconds 1.001 |
| E4 | Revocation | state after the revocation | delivered, not confirmed (revoked) | OK | delivered, not confirmed (revoked) |
| E5 | Revocation | a message revoked before the login is not shown | no text | OK |  |
| F1 | Faults | the copy for one user cannot be written: the others receive it | error, anna «sent, not delivered», mario delivered | OK | rspeak: message 1 not delivered to: anna (see the log; the next rspeak command will retry) ¦ anna: sent, not delivered: the copy could not be written (see the log; the next rspeak command will retry) |
| F2 | Faults | fault fixed: the next command completes the delivery | anna delivered | OK | rspeak: completed delivery of message 1 to 1 recipients |
| F3 | Faults | rspeak send killed halfway (SIGKILL): the next command completes | all copies delivered, no sign of an incomplete sending | OK | delivered_at_kill 4, recipients 65, seconds_recovery 1.147; delivered before 4/65, after 65/65; rspeak: completed delivery of message 2 to 61 recipients |
| F6 | Faults | user's folder left owned by root by an interrupted sending: the delivery fixes it | delivered | OK | delivered;  |
| F7 | Faults | rspeak revoke during a sending to many users: the sending stops and no copy stays | no copy in the mailboxes, sending interrupted | OK | seconds_waiting_revoke 0.3; copies left: 0; delivered before the revocation: 3; Message 4 revoked while sending: delivery stopped. |
| F5 | Faults | rspeak list repeated while rspeak send delivers: the recovery does not interfere | one delivery per recipient, no duplicates, sending complete | OK | rspeak_list_during_sending 37; 65 deliveries recorded for 65 recipients, 65 distinct |
| F4 | Faults | the confirmation cannot be written: the message stays and the user is told | notice; state delivered; message still in the mailbox | OK | delivered, written to 1 terminal |
| G1 | Security | the mailbox is a link to /etc: root does not write there | no file 2 in /etc; mario «sent, not delivered» | OK | rspeak: message 2 not delivered to: mario (see the log; the next rspeak command will retry) |
| G2 | Security | escape sequences in the text: they do not reach the terminal | no ESC in the text received | OK | 'Text red   end\r\r\n───────────────────────' |
| G3 | Security | forged confirmation with escapes and 500 bytes: rspeak status stays clean | no ESC in the output, at most 200 bytes read | OK | luca             confirmed on 01/01 00:00 (fake0000000000000000000000000000000000000000000000000000000000000000000000000 |
| G4 | Security | an ordinary user with RSPEAK_TEST=1 gets nothing | permission denied | OK | env: ‘/usr/local/bin/rspeak’: Permission denied |
| J1 | Log | rspeak log: the history of the message | sending, deliveries, postponement, confirmation, revocation | OK | 6 events |
| J2 | Log | the confirmation in the journal carries the user who wrote it (_UID) | _UID 1001 | OK | 1001 1001 |
| J3 | Log | an event written by a user in the name of another: rspeak log flags it | «[not trustworthy: written by UID 1003]» | OK | 2026-10-01 18:24:46  [not trustworthy: written by UID 1003] user anna: confirmed reading message 1 (desktop) |
| T1 | TUI | rspeak without arguments as root: the list with the recipients in the three states | «RootSpeak · sent messages», «2 delivered» | OK |  |
| T2 | TUI | detail: recipients and history from the log | anna, mario; «sent by root» | OK |  |
| T3 | TUI | q: the TUI exits and gives the terminal back | exit status 0 | OK |  |
| K1-zsh | Shells | zsh: at login the message and the question | text and question at login | OK |  |
| K2-zsh | Shells | zsh: confirmation at login | confirmed (terminal) | OK | confirmed on 01/10 18:24 (terminal pts/15) |
| K3-zsh | Shells | zsh: user logged in, the text appears in the terminal | text in the terminal | OK |  |
| K4-zsh | Shells | zsh: pressing Enter the question appears | question at the next prompt | OK | seconds 0.066 |
| K5-zsh | Shells | zsh: confirmation at the prompt | confirmed (terminal) | OK | confirmed on 01/10 18:24 (terminal pts/15) |
| K-fish | Shells | fish: test user fabio | present | -- | user missing |
| K-ksh | Shells | ksh: test user kora | present | -- | user missing |
| K-dash | Shells | dash: test user dario | present | -- | user missing |
| L5 | Language | a user whose session is in Italian: header, question and answer in English, «y» confirms | «Message from the administrator», «Do you confirm…? [y/N]», «Confirmed.» | OK | confirmed on 01/10 18:24 (terminal pts/16) |
| H1 | Performance | sending to all (55 recipients) | measure | OK | seconds 0.66, ms_per_recipient 12.1 |
| H2 | Performance | rspeak list with 10 messages × 55 recipients | measure (item 15 of the review) | OK | seconds 0.38 |
| H3 | Performance | rspeak status of a message with 55 recipients | measure | OK | seconds 0.27 |
| I1 | Desktop | confirmation dialog in the graphical session | dialog «I have read it» | -- | the container has no graphical session: the dialog is tested in the VM (tests/vm) |
