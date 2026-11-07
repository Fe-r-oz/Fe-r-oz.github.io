"""Fetch Google Scholar profile stats and per-paper citation counts.

Writes _data/scholar.json, which the site renders. Run by
.github/workflows/scholar.yml once a day. If Google Scholar blocks the
request or the page layout changes, the script leaves the existing file
untouched and exits successfully, so the site keeps the last good numbers.

Usage: python _scripts/update_scholar.py [--html saved_profile.html]
"""
import datetime
import html
import json
import os
import sys
import urllib.request
from html.parser import HTMLParser

USER = "xdGGmiUAAAAJ"
PROFILE = f"https://scholar.google.com/citations?user={USER}&hl=en&cstart=0&pagesize=100"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "_data", "scholar.json")


class ProfileParser(HTMLParser):
    """Collects the stats table and the per-article rows."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stats = []          # numbers from td.gsc_rsb_std, in page order
        self.papers = {}         # citation_for_view id -> {"title", "cited", "cites_url"}
        self._in_std = False
        self._buf = ""
        self._row_id = None
        self._in_title = False
        self._in_cited = False
        self._cites_url = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class", "") or ""
        if tag == "td" and "gsc_rsb_std" in cls.split():
            self._in_std, self._buf = True, ""
        elif tag == "a" and "gsc_a_at" in cls.split():
            href = html.unescape(a.get("href", "") or a.get("data-href", "") or "")
            key = "citation_for_view="
            self._row_id = href.split(key, 1)[1].split("&", 1)[0] if key in href else None
            self._in_title, self._buf = True, ""
        elif tag == "a" and "gsc_a_ac" in cls.split():
            self._in_cited, self._buf = True, ""
            self._cites_url = html.unescape(a.get("href", "") or "")

    def handle_endtag(self, tag):
        if tag == "td" and self._in_std:
            self._in_std = False
            self.stats.append(self._buf.strip())
        elif tag == "a" and self._in_title:
            self._in_title = False
            if self._row_id:
                self.papers[self._row_id] = {"title": " ".join(self._buf.split()), "cited": 0, "cites_url": ""}
        elif tag == "a" and self._in_cited:
            self._in_cited = False
            if self._row_id and self._row_id in self.papers:
                text = self._buf.strip()
                self.papers[self._row_id]["cited"] = int(text) if text.isdigit() else 0
                self.papers[self._row_id]["cites_url"] = self._cites_url

    def handle_data(self, data):
        if self._in_std or self._in_title or self._in_cited:
            self._buf += data


def parse(page):
    p = ProfileParser()
    p.feed(page)
    # stats table: Citations(all, recent), h-index(all, recent), i10(all, recent)
    if len(p.stats) < 6 or not all(s.isdigit() for s in p.stats[:6]) or not p.papers:
        return None
    return {
        "profile": f"https://scholar.google.com/citations?user={USER}&hl=en",
        "citations": int(p.stats[0]),
        "h_index": int(p.stats[2]),
        "i10_index": int(p.stats[4]),
        "papers": p.papers,
    }


def fetch():
    req = urllib.request.Request(PROFILE, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--html":
        page = open(sys.argv[2], encoding="utf-8").read()
    else:
        try:
            page = fetch()
        except Exception as e:  # blocked, rate-limited or offline
            print(f"Could not reach Google Scholar ({e}); keeping existing numbers.")
            return 0
    data = parse(page)
    if data is None:
        print("Profile page did not parse (possibly a CAPTCHA); keeping existing numbers.")
        return 0
    old = {}
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            old = json.load(f)
    if {k: v for k, v in old.items() if k != "updated"} == data:
        print("No change in Google Scholar numbers.")
        return 0
    data["updated"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Updated: {data['citations']} citations, h-index {data['h_index']}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
