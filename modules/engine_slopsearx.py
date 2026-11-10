"""SlopSearX - SearXNG-compatible JSON API (self-hosted instance)."""
import os
import requests
from config import Config

def _r(t, u, s, src):
    return {"title": t, "url": u, "snippet": s, "source": src}

def slopsearx(query, limit=10):
    base = os.getenv("SLOPSEARX_URL", "").rstrip("/")
    if not base:
        return []
    try:
        r = requests.get(
            f"{base}/search",
            params={"q": query, "format": "json"},
            headers={"User-Agent": "PUSAT-SEARCH/1.0"},
            timeout=Config.SEARCH_TIMEOUT,
        )
        if not r.ok:
            return []
        data = r.json()
        out = []
        for x in data.get("results", [])[:limit]:
            out.append(_r(
                x.get("title", ""),
                x.get("url", ""),
                (x.get("content") or "")[:200],
                "slopsearx",
            ))
        return out
    except Exception as e:
        print(f"[slopsearx] {e}")
        return []
