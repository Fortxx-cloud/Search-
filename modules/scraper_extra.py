import requests
from bs4 import BeautifulSoup
from config import Config

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

def _r(t, u, s, src):
    return {"title": t, "url": u, "snippet": s, "source": src}

def ecosia(query, limit):
    try:
        r = requests.get("https://www.ecosia.org/search", params={"q": query}, headers={"User-Agent": UA}, timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        soup = BeautifulSoup(r.text, "lxml")
        out = []
        for a in soup.select("a.result__link")[:limit]:
            out.append(_r(a.get_text(strip=True), a.get("href",""), "", "ecosia"))
        return out
    except Exception as e:
        print("[ecosia]", e); return []

def qwant(query, limit):
    try:
        r = requests.get("https://api.qwant.com/v3/search/web", params={"q": query, "count": limit, "locale": "en_US", "offset": 0, "device": "desktop"}, headers={"User-Agent": UA}, timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        data = r.json()
        items = data.get("data",{}).get("result",{}).get("items",[]) or []
        return [_r(x.get("title",""), x.get("url",""), x.get("desc",""), "qwant") for x in items[:limit]]
    except Exception as e:
        print("[qwant]", e); return []

def yandex(query, limit):
    try:
        r = requests.get("https://yandex.com/search/", params={"text": query}, headers={"User-Agent": UA}, timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        soup = BeautifulSoup(r.text, "lxml")
        out = []
        for a in soup.select("a.Link_theme_normal")[:limit]:
            href = a.get("href","")
            if "yandex" in href: continue
            out.append(_r(a.get_text(strip=True), href, "", "yandex"))
        return out
    except Exception as e:
        print("[yandex]", e); return []

def marginalia(query, limit):
    try:
        r = requests.get("https://search.marginalia.nu/search", params={"query": query}, headers={"User-Agent": UA}, timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        soup = BeautifulSoup(r.text, "lxml")
        out = []
        for a in soup.select("a.href")[:limit]:
            out.append(_r(a.get_text(strip=True), a.get("href",""), "", "marginalia"))
        return out
    except Exception as e:
        print("[marginalia]", e); return []

def presearch(query, limit):
    try:
        r = requests.get("https://presearch.com/search", params={"q": query}, headers={"User-Agent": UA}, timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        soup = BeautifulSoup(r.text, "lxml")
        out = []
        for a in soup.select("a.title")[:limit]:
            out.append(_r(a.get_text(strip=True), a.get("href",""), "", "presearch"))
        return out
    except Exception as e:
        print("[presearch]", e); return []

def ask(query, limit):
    try:
        r = requests.get("https://www.ask.com/web", params={"q": query}, headers={"User-Agent": UA}, timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        soup = BeautifulSoup(r.text, "lxml")
        out = []
        for div in soup.select(".PartialSearchResults-item")[:limit]:
            a = div.select_one(".PartialSearchResults-item-title a")
            p = div.select_one(".PartialSearchResults-item-abstract")
            if not a: continue
            out.append(_r(a.get_text(strip=True), a.get("href",""), p.get_text(strip=True) if p else "", "ask"))
        return out
    except Exception as e:
        print("[ask]", e); return []

def searx_public(query, limit):
    for base in ["https://searx.be", "https://search.bus-hit.me"]:
        try:
            r = requests.get(base + "/search", params={"q": query, "format": "json"}, headers={"User-Agent": UA}, timeout=15)
            if not r.ok: continue
            return [_r(x.get("title",""), x.get("url",""), x.get("content",""), "searx") for x in r.json().get("results",[])[:limit]]
        except: continue
    return []

ALL_EXTRA_SCRAPERS = [ecosia, qwant, yandex, marginalia, presearch, ask, searx_public]
