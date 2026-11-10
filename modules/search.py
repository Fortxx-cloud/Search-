"""Search orchestrator: filter, dedupe, timeout, cache."""
import time
import re
import base64
import logging
import threading
import requests
from urllib.parse import urlparse

from config import Config
from modules.scraper_extra import ALL_EXTRA_SCRAPERS
from modules.public_api import ALL_PUBLIC_APIS
from modules.api_extra import ALL_EXTRA_APIS
from modules.api import tavily, exa, jina, serper, firecrawl, brave_api
from modules.searxng import searxng
from modules.engine_ddgs import ddgs
from modules.engine_whoogle import whoogle
from modules.engine_slopsearx import slopsearx
from modules.engine_webless import webless
from modules.engine_googlesearch import googlesearch
from modules.engine_pypi import pypi
from modules.engine_reddit import reddit

logger = logging.getLogger(__name__)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# ============ CACHE (5 menit) ============
_CACHE = {}
_CACHE_LOCK = threading.Lock()
_CACHE_TTL = 300

def _cache_get(key):
    with _CACHE_LOCK:
        e = _CACHE.get(key)
        if e and time.time() - e["t"] < _CACHE_TTL:
            return e["v"]
        if e:
            _CACHE.pop(key, None)
    return None

def _cache_set(key, val):
    with _CACHE_LOCK:
        _CACHE[key] = {"t": time.time(), "v": val}

# ============ PER-ENGINE TIMEOUT WRAPPER ============
def _run_with_timeout(fn, query, limit, timeout=8):
    """Run fn di thread, timeout 8s. Kalau hang, return []."""
    result = {"v": []}
    def worker():
        try:
            result["v"] = fn(query, limit) or []
        except Exception as e:
            logger.debug(f"{fn.__name__}: {e}")
    t = threading.Thread(target=worker, daemon=True)
    t.start()
    t.join(timeout)
    return result["v"] if not t.is_alive() else []

# ============ RELEVANCE FILTER ============
RELEVANCE_KEYWORDS = [
    "api", "developer", "documentation", "docs", "endpoint",
    "sdk", "rest", "json", "oauth", "integration", "reference",
    "developer portal", "get started", "quickstart",
]

def _is_relevant(item, query_keywords):
    """Skip hasil yang totally nggak relevan — strict."""
    text = ((item.get("title") or "") + " " + (item.get("url") or "") + " "
            + (item.get("snippet") or "")).lower()
    # Skip domain obvious non-API (weather.com, accuweather, dll) — kecuali query = weather
    BLACKLIST_DOMAINS = ["weather.com", "accuweather", "bbc.com/weather",
                         "meteoblue", "weather-forecast", "météo", "meteo",
                         "wunderground", "weatherbug"]
    q_has_weather = any(k in " ".join(query_keywords) for k in ["weather", "forecast", "météo"])
    if not q_has_weather:
        for bl in BLACKLIST_DOMAINS:
            if bl in text:
                return False
    # Wajib ada minimal 1 keyword relevansi (api, docs, developer, dll)
    has_relevance = any(k in text for k in RELEVANCE_KEYWORDS)
    return has_relevance

# ============ DOMAIN DEDUPE ============
def _domain(url):
    try:
        d = urlparse(url).netloc.lower()
        return d.replace("www.", "")
    except Exception:
        return ""

# ============ BING ============
def bing(query, limit):
    # Enhance query: tambah "developer" atau "documentation" kalau belum ada
    q_lower = query.lower()
    if not any(k in q_lower for k in ["documentation", "docs", "api", "developer"]):
        enhanced = query + " API documentation"
    else:
        enhanced = query
    try:
        r = requests.get("https://www.bing.com/search",
            params={"q": enhanced, "count": limit, "setlang": "en-US", "cc": "US"},
            headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"},
            timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, "lxml")
        out = []
        for li in soup.select("li.b_algo")[:limit]:
            a = li.select_one("h2 a")
            p = li.select_one("p")
            if not a: continue
            href = a.get("href", "")
            m = re.search(r"[?&]u=a1([^&]+)", href)
            if m:
                try:
                    enc = m.group(1)
                    enc += "=" * (4 - len(enc) % 4)
                    href = base64.urlsafe_b64decode(enc).decode("utf-8", "ignore")
                except: pass
            out.append({"title": a.get_text(strip=True), "url": href,
                        "snippet": p.get_text(strip=True) if p else "",
                        "source": "bing"})
        return out
    except Exception as e:
        logger.debug(f"bing: {e}"); return []

# ============ ALL ENGINES ============
ALL_ENGINES = ([bing, searxng, ddgs, whoogle, slopsearx, webless, googlesearch, pypi, reddit]
               + ALL_EXTRA_SCRAPERS
               + ALL_PUBLIC_APIS
               + [tavily, exa, jina, serper, firecrawl, brave_api]
               + ALL_EXTRA_APIS)

# ============ MAIN SEARCH ============
def search(query, limit=20):
    """Full search: parallel-ish, timeout, filter, dedupe, cache."""
    cache_key = f"{query}|{limit}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached[0], cached[1]

    q_keywords = [k.lower() for k in re.findall(r"\w+", query) if len(k) > 2]
    results = []
    stats = {}

    for fn in ALL_ENGINES:
        name = fn.__name__
        r = _run_with_timeout(fn, query, limit, timeout=8)
        if r:
            stats[name] = len(r)
            results.extend(r)
            logger.info(f"[OK] {name}: {len(r)}")
        else:
            logger.debug(f"[EMPTY] {name}")

    # Dedupe by URL
    seen_url = set()
    deduped = []
    for r in results:
        u = r.get("url", "")
        if u and u not in seen_url:
            seen_url.add(u)
            deduped.append(r)

    # Relevance filter
    filtered = [r for r in deduped if _is_relevant(r, q_keywords)]

    # Domain dedupe (max 3 per domain)
    domain_count = {}
    final = []
    for r in filtered:
        d = _domain(r.get("url", ""))
        if domain_count.get(d, 0) >= 3:
            continue
        domain_count[d] = domain_count.get(d, 0) + 1
        final.append(r)

    final = final[:limit]
    _cache_set(cache_key, (final, stats))
    return final, stats

def search_legacy(query, limit=20):
    r, _ = search(query, limit)
    return r

def cache_stats():
    with _CACHE_LOCK:
        now = time.time()
        fresh = sum(1 for e in _CACHE.values() if now - e["t"] < _CACHE_TTL)
        return {"entries": len(_CACHE), "fresh": fresh, "ttl_sec": _CACHE_TTL}
