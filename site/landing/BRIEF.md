# RootSpeak landing page — brief for the mockups

Twenty mockups of the same landing page, **same content, twenty visual directions**.
They are for choosing a direction: the chosen one becomes the real page later.

## Rules (all mockups)

- One **self-contained HTML file** per mockup: `site/mockups/NN-slug.html`. No JavaScript,
  no external requests (no CDN, no Google Fonts, no remote images): CSS in a `<style>`,
  images inline (SVG, or `data:` URIs), fonts embedded as `data:` URIs from
  `/usr/share/fonts` if used (the mockup may also use only system font stacks).
  Local fonts available: Cantarell, Quicksand, URW Gothic, P052 (Palatino-like),
  C059 (Century-like), URW Bookman, Nimbus Sans, DejaVu Sans/Serif/Sans Mono,
  Liberation Sans/Serif/Mono, Noto Mono. They are for exploring only: the real site will
  use fonts licensed for commercial use.
- English only. Elegant, professional, appealing. Responsive: it must look right at 1440 px
  and at 390 px (phone), with no horizontal scrolling.
- The logo: the mark in `_shared/logo-mark.svg` (inline it), next to the word **RootSpeak**
  written in the page's font, «Root» and «Speak» in two tones (on light backgrounds the
  original colours are #14306b and #1f6fd1; on dark backgrounds use light tones). Subtitle,
  where it fits: «Advanced Messaging System for Linux». The palette of the page is free.
- **Only true statements.** Use the facts below; do not invent features, customers,
  testimonials, numbers, prices or certifications. Where something is not decided yet
  (prices, licence terms, download links) write a visible placeholder, e.g. «Price to be
  announced», links to `#`.
- Program texts are quoted **exactly** as below (they are English, verbatim from the program).
- The real TUI screens are in `_shared/tui-list.html` and `_shared/tui-detail.html`
  (HTML with classes `a-b` bold, `a-d` dim, `a-v` reverse, `a-31` red, `a-32` green,
  `a-33` yellow, `a-36` cyan, `a-90` grey): use them as they are, with your own CSS for
  the classes, in a terminal-window frame. They are 116 columns wide: scale the font down,
  and on phones let the screen scroll inside its own frame or show a crop.

## What RootSpeak is

The administrators of a Linux machine send text messages to its users and **know who has
confirmed reading them**. For administrators of shared Linux machines: servers with many
accounts, labs, university and research machines, workstations of a team, companies.

Tagline ideas (choose or adapt, keep them true): «Tell every user. Know who read it.» —
«Messages from root that people actually see.» — «Read receipts for your Linux users.»

## The problem

`wall` and `write` reach only who is logged in at that moment, in a terminal, and leave no
trace. E-mails get lost. Before a reboot, a maintenance window, a policy change or a
security notice, the administrator has no way to know who has seen the message.

## How it works (three steps)

1. **Send.** `rspeak send --to @developers --title "Server update" "Tonight at 11 pm the mail server is updated."`
   Recipients: a user, a list, a Unix group (`@group`), `all` (every human user) or
   `online` (only those logged in now). Optional `--expires 2h`.
2. **It reaches them wherever they are.** In every open terminal (tty, ssh, tmux) and on the
   desktop (X11 and Wayland) at once; whoever is logged out finds it at the next login.
3. **See who confirmed.** For each recipient: **sent**, **delivered** or **confirmed**, with
   date, time and channel. `rspeak status 1`, `rspeak list`, or the TUI.

## Exact program texts

- In the terminal, the message appears framed:
  `── RootSpeak · Message from the administrator · 01/10 15:13 ──` then the text, then a line
  `────────────────────────────────────────`, then the question
  `[RootSpeak] Do you confirm you have read the message? [y/N]` — after `y`:
  `[RootSpeak] Confirmed.`
- On the desktop: a dialog titled `RootSpeak · Message from the administrator`, with the
  message title and date (e.g. `Maintenance · 01/10 15:13`), the text (e.g. `Server off on
  Saturday from 8 to 12.`) and two buttons: `Later` and `I have read it`.
- Sending: `Message 1 sent to 14 users.` (the form is «Message N sent to N users.»)
- States in `rspeak status`: `delivered`, `confirmed on 01/10 11:37 (terminal pts/2)`,
  `confirmed on 01/10 15:14 (desktop)`, `delivered, postponed on 01/10 15:20`.
- A message summary in the list: a three-colour bar and `14 confirmed · 5 delivered · 2 sent`.

## Features (all true today, version 0.2.0)

- Recipients by user, list, Unix group, `all`, `online`; text from an argument, a file or stdin;
  optional title; expiry (`--expires`).
- Three states per recipient: sent, delivered, confirmed — with date, time and channel
  (desktop or terminal).
- Reminders until confirmed, every 30 minutes by default; `rspeak remind` brings the question
  back at once; `rspeak revoke` withdraws a message; `rspeak purge` deletes old ones.
- A full-screen terminal interface (TUI) for administrators: browse, read who confirmed,
  write and send, remind, revoke. No ncurses.
- History in the system journal: `rspeak log` (`journalctl -t rspeak`).
- **Never blocks anyone**: no lock screen, no logout; users can always choose «Later».
  Non-interactive sessions (cron, scp, rsync, ssh without a terminal, services) are never touched.
- Users install nothing and have no command: they just receive and confirm.
- Honest note (keep it somewhere, small): the confirmation records that the user *states*
  they have read the message, like read receipts in a messaging app.

## Security and design

- One machine, no network, no daemon: it uses what the system already has (logind, sudo,
  the shell, desktop autostart).
- The `rspeak` command is for the administrators' group that already exists (`sudo` or
  `wheel`) and always runs as root; users cannot run it.
- Root never writes into users' mailboxes as root: every access happens in a child process
  with the user's identity, with a time limit.
- Written in C, built with every warning as an error and compiler hardening; tested with
  AddressSanitizer and UBSan, static analysis and fuzzing of everything that reads users' files.
- Escape sequences in messages are cleaned: a message cannot take over a terminal.

## Compatibility (tested, not just claimed)

- Tested automatically, as root with real users and sessions, on **22 distributions** with
  systemd: Debian 12 and 13, Ubuntu 22.04, 24.04 and 26.04, Fedora 44 and 45, CentOS Stream 9
  and 10, RHEL 9 and 10, Rocky Linux 9 and 10, AlmaLinux 9 and 10, Oracle Linux 9 and 10,
  openSUSE Leap 16 and Tumbleweed, SLES 15 and 16, Arch Linux.
- Desktops tested: GNOME (Debian, Ubuntu, Rocky Linux with SELinux enforcing), KDE Plasma
  (Fedora), Cinnamon — on Wayland and on X11.
- Shells: bash, zsh, fish (question at every prompt); ksh, dash, sh (at login).
- Requires systemd. Packages: `.deb` and `.rpm` (coming — say «coming soon» if shown).

## Trial and purchase (placeholders — not decided yet)

- **Free trial**: full features for 7 days. Button «Start the 7-day free trial» → `#`.
- **Licence**: unlimited, for those who buy. «Price to be announced». Button «Buy» → `#`.
- Do not state licence terms (per machine, per organisation…): not decided.

## Sections of the page (in this order, adapt the layout)

1. Header: logo, links (Features, How it works, Compatibility, Pricing, Docs), a button for the trial.
2. Hero: tagline, one-sentence description, two buttons (trial; «See how it works»), a visual
   showing the terminal question and/or the desktop dialog (built in HTML/CSS/SVG, faithful to
   the exact texts above).
3. The problem (short).
4. How it works: the three steps.
5. Features.
6. The TUI (a real screen from `_shared/`).
7. Respectful by design (never blocks) and security.
8. Compatibility: the 22 distributions, desktops, shells.
9. Pricing: trial and licence (placeholders).
10. FAQ (3–5 true answers, e.g. «Does it need a server or a network?» — no, one machine;
    «Do users need to install anything?» — no; «What if a user is not logged in?» — they get
    it at the next login; «Can it lock the screen until they confirm?» — no, by design).
11. Footer: «RootSpeak — Advanced Messaging System for Linux · © 2026 Nicola Fiorillo», links
    to the User Manual and the Technical Manual (`#`).

## Checking your work

Render each page with Chrome headless and look at the images before delivering:
`google-chrome --headless=new --disable-gpu --hide-scrollbars --window-size=1440,6000 --screenshot=OUT.png file:///path/NN-slug.html`
and at `--window-size=390,9000`. Fix anything broken (overflow, overlaps, unreadable
contrast, empty areas). Save a preview for the gallery: `site/mockups/previews/NN-slug.png`
(1440 px wide, first 900 px tall: `--window-size=1440,900`).
