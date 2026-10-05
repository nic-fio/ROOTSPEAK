#!/bin/bash
# RootSpeak - Advanced Messaging System for Linux
# Compatibility tests on the distributions of tests/distros/list, on the test
# server (so as not to load the PC): for each distribution a test machine
# (tests/container) with its own image, where RootSpeak is built and installed
# and the real-world scenarios run. Several distributions at a time; the results
# come back to tests/distros/results/NAME/ with a summary in
# tests/distros/results/summary.md.
#   tests/distros/run.sh                  all the distributions
#   tests/distros/run.sh fedora-44 arch   only these
#   RSPEAK_PARALLEL=N (default 4), RSPEAK_SERVER and RSPEAK_DIR to change server and folder,
#   RSPEAK_REBUILD=1 to build the images again (they are rebuilt anyway when the
#   preparation of the test machine changes), RSPEAK_TEST_ONLY as in tests/container,
#   RSPEAK_ARCHIVE=FILE to install the downloadable archive (tools/release.sh)
#   instead of building from source, RSPEAK_RELEASE=FOLDER to install the package of
#   each distribution from the folder of tools/release.sh (.deb, .rpm, Arch) with
#   its package manager, and test the packages too (scenarios P).
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../.." && pwd)
SERVER=${RSPEAK_SERVER:-192.168.0.2}
DIR=${RSPEAK_DIR:-/media/ROOTSPEAK}
PARALLEL=${RSPEAK_PARALLEL:-4}
SSHOPT=(-o BatchMode=yes -o LogLevel=ERROR)
# (the server's shell profile prints tput warnings without a terminal: they are dropped)
x() { ssh "${SSHOPT[@]}" "$SERVER" "export TERM=dumb; $*" 2> >(grep -v '^tput:' >&2); }

list=$(grep -v '^#' "$HERE/list" | awk 'NF==2')
if [ $# -gt 0 ]; then
	want=" $* "
	list=$(echo "$list" | while read -r n i; do [[ $want == *" $n "* ]] && echo "$n $i"; done)
	[ -n "$list" ] || { echo "no such distribution in tests/distros/list: $*" >&2; exit 2; }
fi
# the images carry the fingerprint of the preparation: a new setup.sh builds new images
tag=$(cat "$ROOT/tests/container/Containerfile" "$ROOT/tests/container/setup.sh" | sha256sum | cut -c1-12)
commit=$("$ROOT/tools/fingerprint.sh" --commit)
fingerprint=$("$ROOT/tools/fingerprint.sh")

# the server's system is rebuilt at every boot (its / is in RAM): the programs the
# tests need may be gone, and only the owner can install them, with sudo
missing=$(x 'for c in podman python3; do command -v $c >/dev/null || printf "%s " $c; done')
if [ -n "$missing" ]; then
	echo "the test server $SERVER lacks: $missing(its system is lost at every reboot). Install with:" >&2
	echo "  ssh -t $SERVER 'sudo apt install -y podman python3'" >&2
	exit 2
fi
echo "code on the server ($SERVER:$DIR/distros/src)…"
tar --exclude=.git --exclude='./build*' --exclude='./tests/*/results' -cf - -C "$ROOT" . |
	x "rm -rf $DIR/distros/src && mkdir -p $DIR/distros/src $DIR/distros/results && tar -xf - -C $DIR/distros/src" || exit 1
ARCH=
if [ -n "${RSPEAK_ARCHIVE:-}" ]; then
	echo "archive on the server: $(basename "$RSPEAK_ARCHIVE")…"
	x "cat > $DIR/distros/rootspeak.tar.gz" <"$RSPEAK_ARCHIVE" || exit 1
	ARCH=$DIR/distros/rootspeak.tar.gz
else
	x "rm -f $DIR/distros/rootspeak.tar.gz"
fi
REL=
x "rm -rf $DIR/distros/release" || exit 1
if [ -n "${RSPEAK_RELEASE:-}" ]; then
	echo "packages on the server: $(cd "$RSPEAK_RELEASE" && ls rootspeak_*.deb rootspeak-*.rpm rootspeak-*.pkg.tar.zst | tr '\n' ' ')…"
	tar -C "$RSPEAK_RELEASE" -cf - --exclude='rootspeak-*-linux-x86_64' . | x "mkdir -p $DIR/distros/release && tar -xf - -C $DIR/distros/release" || exit 1
	REL=$DIR/distros/release
fi
# the images on the SSD: the server's / is in RAM (20 GB of images for all of them)
x "mkdir -p $DIR/distros/storage && rm -f $DIR/distros/storage.conf" || exit 1

echo "$(echo "$list" | wc -l) distributions, $PARALLEL at a time…"
echo "$list" | x "cd $DIR/distros && export RSPEAK_PODMAN_ROOT=$DIR/distros/storage \
	RSPEAK_TEST_COMMIT=$commit RSPEAK_TEST_FINGERPRINT=$fingerprint RSPEAK_TEST_ONLY=${RSPEAK_TEST_ONLY:-} RSPEAK_ARCHIVE=$ARCH RSPEAK_RELEASE=$REL
	xargs -P $PARALLEL -L 1 sh -c '
		n=\$0; r=results/\$n; rm -rf \$r; mkdir -p \$r
		RSPEAK_BASE=\$1 RSPEAK_NAME=rootspeak-test-\$n RSPEAK_IMAGE=rootspeak-test-\$n:$tag RSPEAK_RESULTS=\$PWD/\$r \
			src/tests/container/run.sh ${RSPEAK_REBUILD:+--rebuild} >\$r/run.log 2>&1
		echo \"  \$n: exit \$?\"'"

rm -rf "$HERE/results" && mkdir -p "$HERE/results"
x "tar -cf - -C $DIR/distros/results ." | tar -xf - -C "$HERE/results"
how="built from source on each distribution"
[ -n "${RSPEAK_ARCHIVE:-}" ] && how="the downloadable archive $(basename "$RSPEAK_ARCHIVE"), built on RHEL 9"
[ -n "${RSPEAK_RELEASE:-}" ] && how="the package of each distribution (.deb, .rpm, Arch) from tools/release.sh, installed with its package manager"
python3 - "$HERE/results" "$commit" "$fingerprint" "$how" <<'PY'
import json, pathlib, sys, time
res, commit, fingerprint, how = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]
names = [l.split()[0] for l in (res.parent / "list").read_text().splitlines() if l.strip() and not l.startswith("#")]
rows, bad, dists = [], 0, []
for n in names:
    d = res / n
    if not d.is_dir():
        continue
    j = d / "results.json"
    if j.exists():
        m = json.loads(j.read_text())["meta"]
        failed = [r["code"] for r in json.loads(j.read_text())["results"] if r["outcome"] == "NO"]
        skipped = [r["code"] for r in json.loads(j.read_text())["results"] if r["outcome"] == "--"]
        out = "OK" if not failed else "NO"
        dists.append(dict(name=n, system=m["system"].removesuffix(", container with systemd"), outcome=out,
                          ok=m["ok"], failed=m["failed"], not_tested=m["not_tested"], total=m["total"],
                          failed_codes=failed, not_tested_codes=skipped, fingerprint=m.get("fingerprint")))
        rows.append(f"| {n} | {m['system'].removesuffix(', container with systemd')} | {out} | {m['ok']} / {m['failed']} / {m['not_tested']} "
                    f"| {', '.join(failed) or '—'} | {', '.join(skipped) or '—'} |")
    else:
        log = (d / "run.log").read_text(errors="replace").strip().splitlines() if (d / "run.log").exists() else []
        out = "NO"
        why = (log[-1] if log else "no log").replace("|", "¦")[:120]
        rows.append(f"| {n} | — | NO | not run | {why} (see {n}/run.log) | — |")
        dists.append(dict(name=n, system="", outcome="NO", not_run=why))
    bad += out != "OK"
lines = ["# RootSpeak on the distributions\n", f"- Date: {time.strftime('%Y-%m-%d %H:%M:%S %Z')}",
         f"- Code: commit {commit}, fingerprint {fingerprint}",
         f"- Installed: {how}",
         f"- Outcome: **{len(rows) - bad} of {len(rows)} distributions passed**\n",
         "| Name | System | Outcome | Passed / failed / not tested | Failed | Not tested |", "|---|---|---|---|---|---|", *rows]
(res / "summary.md").write_text("\n".join(lines) + "\n")
meta = dict(date=lines[1][8:], commit=commit, fingerprint=fingerprint, installed=how, ok=len(rows) - bad, failed=bad, total=len(rows))
(res / "summary.json").write_text(json.dumps(dict(meta=meta, distributions=dists), indent=1) + "\n")
print("\n".join(lines[4:]))
sys.exit(1 if bad else 0)
PY
