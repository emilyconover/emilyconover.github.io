#!/usr/bin/env python3
"""Save the latest stories from the Science News author feed to articles.json.

Usage:
  python3 scripts/update_articles.py              # download the feed
  python3 scripts/update_articles.py feed.rss     # or read a feed file you downloaded
"""
import html, json, re, sys, urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

FEED_URL = "https://www.sciencenews.org/author/emily-conover/feed"
OUT_FILE = "articles.json"
MAX_ITEMS = 10

try:
    if len(sys.argv) > 1:
        with open(sys.argv[1], "rb") as f:
            data = f.read()
    else:
        req = urllib.request.Request(FEED_URL, headers={"User-Agent": "Mozilla/5.0 (compatible; personal-site-updater)"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
    root = ET.fromstring(data)
except Exception as e:
    sys.exit(f"Could not read or parse the feed: {e}")

items = []
for item in root.iter("item"):
    title = html.unescape(re.sub(r"<[^>]+>", "", item.findtext("title") or "")).strip()
    link = (item.findtext("link") or "").strip()
    if not title or not link:
        continue
    try:
        date = parsedate_to_datetime(item.findtext("pubDate")).date().isoformat()
    except Exception:
        date = ""
    items.append({"title": title, "url": link, "date": date})
    if len(items) >= MAX_ITEMS:
        break

if not items:
    sys.exit("Feed contained no stories; leaving articles.json unchanged.")

with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=2)
    f.write("\n")
print(f"Saved {len(items)} stories to {OUT_FILE}.")
