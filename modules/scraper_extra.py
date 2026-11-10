"""Extra scrapers that MAY work from cloud (permissive ones only)."""
import requests
from bs4 import BeautifulSoup
from config import Config

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

def _r(t, u, s, src):
    return {"title": t, "url": u, "snippet": s, "source": src}

def mojeek(query, limit):
    """Mojeek - smaller, often permissive to cloud."""
    try:
        r = requests.get("https://www.mojeek.com/search",
            params={"q": query}, headers={"User-Agent": UA},
            timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        soup = BeautifulSoup(r.text, "lxml")
        out = []
        for li in soup.select("ul.results-standard li")[:limit]:
            a = li.select_one("a.title")
            p = li.select_one("p.s")
            if not a: continue
            out.append(_r(a.get_text(strip=True), a.get("href", ""),
                p.get_text(strip=True) if p else "", "mojeek"))
        return out
    except Exception as e:
        print("[mojeek]", e); return []

def marginalia(query, limit):
    """Marginalia - small independent, permissive."""
    try:
        r = requests.get("https://search.marginalia.nu/search",
            params={"query": query}, headers={"User-Agent": UA},
            timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        soup = BeautifulSoup(r.text, "lxml")
        out = []
        for a in soup.select("a.href")[:limit]:
            out.append(_r(a.get_text(strip=True), a.get("href", ""), "", "marginalia"))
        return out
    except Exception as e:
        print("[marginalia]", e); return []

ALL_EXTRA_SCRAPERS = [mojeek, marginalia]
