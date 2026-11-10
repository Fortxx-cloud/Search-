"""Whoogle Search - proxy Google (self-hosted instance via HTTP)."""
import os
import requests
from config import Config

def _r(t, u, s, src):
    return {"title": t, "url": u, "snippet": s, "source": src}

def whoogle(query, limit=10):
    base = os.getenv("WHOOGLE_URL", "").rstrip("/")
    if not base:
        return []
    try:
        r = requests.get(
            f"{base}/search",
            params={"q": query},
            headers={"User-Agent": "PUSAT-SEARCH/1.0"},
            timeout=Config.SEARCH_TIMEOUT,
        )
        if not r.ok:
            return []
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, "lxml")
        out = []
        for a in soup.select("a.result")[:limit]:
            href = a.get("href", "")
            title = a.get_text(strip=True)
            if href:
                out.append(_r(title, href, "", "whoogle"))
        return out
    except Exception as e:
        print(f"[whoogle] {e}")
        return []
