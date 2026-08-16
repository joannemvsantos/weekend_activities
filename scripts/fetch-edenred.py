#!/usr/bin/env python3
"""Fetch Virike-accepting merchants near Oulu from Edenred and write data/edenred.json.

Unlike Menox, this is a plain public JSON search endpoint (search.edenred.fi)
backing edenred.fi/en/merchant-search — no auth/key required, confirmed with a
bare request during the JOA-306 research spike.

Usage: python3 scripts/fetch-edenred.py > data/edenred.json
"""
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

SEARCH_URL = "https://search.edenred.fi/affiliates"
# Oulu city-center coordinates, used to sort/filter merchants by proximity.
OULU_LOCATION = "65.0121:25.4651"
# Service-type category ids the site's own "Virike" filter sends (captured
# from a live merchant-search request in the browser).
VIRIKE_CATEGORIES = (
    "48,47,53,33,34,137,30,131,54,37,38,32,123,52,50,133,128,51,135,43,45,117,"
    "31,36,115,35,49,41,39,126,119,44,46,40,121,42,55,61,62,63,56,67,68,60,59,"
    "69,64,95,57,66,58,130,65"
)


def fetch_merchants(count=30):
    params = {
        "count": str(count),
        "query": "",
        "type": "Virike",
        "city": "",
        "postcode": "",
        "address": "",
        "accepts": "",
        "categories": VIRIKE_CATEGORIES,
        "category": "",
        "location": OULU_LOCATION,
        "sortBy": "relevance",
        "page": "0",
    }
    url = f"{SEARCH_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=20) as res:
        if res.status != 200:
            raise RuntimeError(f"Edenred fetch failed: HTTP {res.status}")
        return json.loads(res.read().decode("utf-8"))


def main():
    try:
        result = fetch_merchants()
    except Exception as exc:  # noqa: BLE001 - top-level CLI error boundary
        print(f"Failed to fetch Edenred merchants: {exc}", file=sys.stderr)
        sys.exit(1)

    items = result.get("items", [])
    # Belt-and-suspenders: keep only merchants that actually accept the Virike
    # voucher, even though the query already filters type=Virike server-side.
    virike_items = [i for i in items if i.get("accepts", {}).get("voucher")]

    output = {
        "source": "edenred",
        "filter": "virike",
        "city": "Oulu",
        "fetchedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "merchants": [
            {
                "id": m.get("id"),
                "name": m.get("name"),
                "type": m.get("type"),
                "categories": [c.get("en") for c in m.get("categories", []) if c.get("en")],
                "address": m.get("addresses", {}).get("visiting", {}).get("addressLine"),
                "city": m.get("addresses", {}).get("visiting", {}).get("city"),
                "postcode": m.get("addresses", {}).get("visiting", {}).get("postcode"),
                "website": m.get("website"),
                "acceptsVoucher": m.get("accepts", {}).get("voucher", False),
                "acceptsCard": m.get("accepts", {}).get("card", False),
                "acceptsMobile": m.get("accepts", {}).get("mobile", False),
            }
            for m in virike_items
        ],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
