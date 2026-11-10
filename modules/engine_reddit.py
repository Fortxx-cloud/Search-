"""Reddit JSON search (public, no auth)."""
import requests
from config import Config

def _r(t, u, s, src):
    return {"title": t, "url": u, "snippet": s, "source": src}

def reddit(query, limit=10):
    try:
        r = requests.get("https://www.reddit.com/search.json",
            params={"q": query, "limit": limit, "sort": "relevance"},
            headers={"User-Agent": "PUSAT-SEARCH/1.0"}, timeout=Config.SEARCH_TIMEOUT)
        if not r.ok:
            return []
        return [_r(
            x["data"].get("title", ""),
            "https://reddit.com" + x["data"].get("permalink", ""),
            (x["data"].get("selftext") or "")[:150],
            "reddit"
        ) for x in r.json().get("data", {}).get("children", [])]
    except Exception:
        return []
