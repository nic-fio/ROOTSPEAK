#!/usr/bin/env bash
# publish.sh - builds the site of RootSpeak in site/public/ and publishes it to
# https://rootspeak.nicfio.it (the owner's VPS, user "progetti",
# /srv/www/rootspeak.nicfio.it).
#
#   site/publish.sh            build and publish
#   site/publish.sh --build    build only (look at site/public/ first)
#
# The site: the landing page (site/landing/index.html), the two manuals
# (self-contained), the licence as a page, and the download of the current
# version (download/: the archive built by tools/release.sh, SHA256SUMS, the
# licence). Run tools/release.sh first.
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
OUT=$ROOT/site/public
HOST=progetti@57.131.27.241
DEST=/srv/www/rootspeak.nicfio.it
VERSION=$(sed -n 's/^#define RSPEAK_VERSION "\(.*\)"/\1/p' "$ROOT/src/common.h")
URL=https://rootspeak.nicfio.it
ARCHIVE=rootspeak-$VERSION-linux-x86_64.tar.gz
REL=$ROOT/build/release

[ -f "$REL/$ARCHIVE" ] || { echo "missing $REL/$ARCHIVE: run tools/release.sh first" >&2; exit 1; }
(cd "$REL" && sha256sum -c SHA256SUMS >/dev/null)
# the landing page names the version and the archive: they must be the current ones
grep -q "download/$ARCHIVE" "$ROOT/site/landing/index.html" ||
	{ echo "site/landing/index.html does not link download/$ARCHIVE" >&2; exit 1; }

rm -rf "$OUT"
mkdir -p "$OUT/download"

cp "$ROOT/site/landing/index.html" "$OUT/index.html"
cp "$ROOT/docs/User Manual.html" "$ROOT/docs/Technical Manual.html" "$OUT/"
python3 "$ROOT/site/licence-page.py" "$ROOT/LICENSE" > "$OUT/licence.html"

# canonical URL, link preview and a search-friendly title for each page
SEO=$ROOT/site/seo-head.py
python3 "$SEO" "$OUT/User Manual.html" "$URL/User%20Manual.html" \
    "RootSpeak User Manual — messages to Linux users with read confirmation" \
    "How to use RootSpeak: install it, send messages to the users of a Linux machine, follow who confirmed, remind, revoke, the full-screen interface and every command."
python3 "$SEO" "$OUT/Technical Manual.html" "$URL/Technical%20Manual.html" \
    "RootSpeak Technical Manual — architecture, message store and security" \
    "How RootSpeak works: the message store, delivery to terminals and desktops, confirmations, security, the specification and how it is tested on 22 distributions."
python3 "$SEO" "$OUT/licence.html" "$URL/licence.html" \
    "RootSpeak Freeware Licence" \
    "RootSpeak is freeware: free to use, also at work, and to give away unchanged; not to sell, modify or include in commercial products."

# the download, with the licence in a form every system opens
DL=$OUT/download
cp "$REL/$ARCHIVE" "$REL/SHA256SUMS" "$DL/"
sed 's/$/\r/' "$ROOT/LICENSE" > "$DL/LICENSE.txt"
sed 's/$/\r/' "$ROOT/NOTICE.md" > "$DL/NOTICE.txt"

cp "$ROOT/site/og.jpg" "$OUT/og.jpg"
cp "$ROOT"/site/google*.html "$OUT/" 2>/dev/null || true
cat > "$OUT/robots.txt" <<EOR
User-agent: *
Allow: /
Sitemap: $URL/sitemap.xml
EOR
TODAY=$(date +%F)
{
    echo '<?xml version="1.0" encoding="UTF-8"?>'
    echo '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    for p in "" "User%20Manual.html" "Technical%20Manual.html" "licence.html"; do
        echo "  <url><loc>$URL/$p</loc><lastmod>$TODAY</lastmod></url>"
    done
    echo '</urlset>'
} > "$OUT/sitemap.xml"

echo "built $OUT (version $VERSION):"
(cd "$OUT" && find . -type f -printf '  %p  %s bytes\n' | sort)

[ "${1:-}" = --build ] && exit 0

# the server ends up identical to site/public (no rsync on either side)
tar -C "$OUT" -cf - --mode=u=rwX,go=rX . | ssh "$HOST" "find '$DEST' -mindepth 1 -delete && tar -C '$DEST' -xf - --no-same-owner"
echo "published to $URL"
