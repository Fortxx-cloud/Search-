"""SearXNG via public instances (no self-host needed)."""
import random
import requests
from config import Config

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Public instances — banyak, biar fallback kalau satu mati
INSTANCES = [
    "https://searx.be",
    "https://search.bus-hit.me",
    "https://searx.tiekoetter.com",
    "https://baresearch.org",
    "https://search.inetol.net",
    "https://priv.au",
    "https://search.sapti.me",
    "https://searxng.site",
    "https://opnxng.com",
    "https://search.hbubli.cc",
    "https://searx.work",
    "https://search.rhscz.eu",
]

def _r(t, u, s, src):
    return {"title": t, "url": u, "snippet": s, "source": src}

def searxng(query, limit=10):
    """Try multiple public SearXNG instances until one works."""
    # Kalau user set SEARXNG_URL di ENV → pakai itu dulu (self-host)
    custom = Config.__dict__.get("SEARXNG_URL", "") if hasattr(Config, "SEARXNG_URL") else ""
    if not custom:
        import os
        custom = os.getenv("SEARXNG_URL", "")

    candidates = ([custom] if custom else []) + random.sample(INSTANCES, len(INSTANCES))

    for base in candidates[:5]:  # coba max 5 instance
        try:
            r = requests.get(
                base.rstrip("/") + "/search",
                params={"q": query, "format": "json", "language": "en"},
                headers={"User-Agent": UA, "Accept": "application/json"},
                timeout=8,
            )
            if not r.ok:
                continue
            ct = r.headers.get("content-type", "")
            if "json" not in ct:
                continue  # instance ini disabled JSON, skip
            data = r.json()
            results = data.get("results", [])
            if not results:
                continue
            out = []
            for x in results[:limit]:
                out.append(_r(
                    x.get("title", ""),
                    x.get("url", ""),
                    x.get("content", "")[:200],
                    "searxng",
                ))
            return out
        except Exception:
            continue
    return []
