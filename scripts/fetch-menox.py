#!/usr/bin/env python3
"""Fetch upcoming Oulu events from Menox and write data/menox.json.

Menox (app.menox.fi) is a client-rendered app with no published/documented
API. Its frontend calls a Supabase PostgREST endpoint directly using a public
"anon" key baked into its JS bundle (frydokrgdtihhknrbwgz.supabase.co) — this
is the same request the site itself makes, not an authenticated/internal
endpoint, but it is undocumented and could change without notice. See
JOA-306 for the research spike that found this.

Usage: python3 scripts/fetch-menox.py > data/menox.json
"""
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

SUPABASE_URL = "https://frydokrgdtihhknrbwgz.supabase.co/rest/v1/events"
# Public "anon" role key shipped in app.menox.fi's own JS bundle — not a secret,
# but not a published API contract either. May need updating if Menox rotates it.
SUPABASE_ANON_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZyeWRva3JnZHRpaGhrbnJid2d6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY4MjQ0NDksImV4cCI6MjA3MjQwMDQ0OX0."
    "r8YSo-Rw9cbLnaey85C8zIqUQRiQsV67NfS1eELkzgc"
)

FIELDS = (
    "id,title,slug,start_date,end_date,start_time,end_time,"
    "location,city,city_slug,category,categories,tags,is_free,is_sold_out"
)


def fetch_events(city_slug="oulu", limit=40):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    params = {
        "select": FIELDS,
        "is_published": "eq.true",
        "city_slug": f"eq.{city_slug}",
        "start_date": f"gte.{today}",
        "order": "start_date.asc",
        "limit": str(limit),
    }
    url = f"{SUPABASE_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        url,
        headers={
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as res:
        if res.status != 200:
            raise RuntimeError(f"Menox fetch failed: HTTP {res.status}")
        return json.loads(res.read().decode("utf-8"))


def main():
    try:
        events = fetch_events()
    except Exception as exc:  # noqa: BLE001 - top-level CLI error boundary
        print(f"Failed to fetch Menox events: {exc}", file=sys.stderr)
        sys.exit(1)

    output = {
        "source": "menox",
        "city": "Oulu",
        "fetchedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "events": [
            {
                "id": e.get("id"),
                "title": e.get("title"),
                "slug": e.get("slug"),
                "startDate": e.get("start_date"),
                "endDate": e.get("end_date"),
                "startTime": e.get("start_time"),
                "endTime": e.get("end_time"),
                "location": e.get("location"),
                "city": e.get("city"),
                "category": e.get("category"),
                "isFree": e.get("is_free"),
                "isSoldOut": e.get("is_sold_out"),
            }
            for e in events
        ],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
