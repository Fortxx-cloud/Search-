import time
import logging
import base64
import re
from urllib.parse import unquote

from config import Config
from modules.scraper_extra import ALL_EXTRA_SCRAPERS
from modules.public_api import ALL_PUBLIC_APIS
from modules.api_extra import ALL_EXTRA_APIS
from modules.searxng import searxng
from modules.engine_ddgs import ddgs
from modules.engine_whoogle import whoogle
from modules.engine_slopsearx import slopsearx
from modules.api import tavily, exa, jina, serper, firecrawl, brave_api

logger = logging.getLogger(__name__)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

def _r(t, u, s, src):
    return {"title": t, "url": u, "snippet": s, "source": src}

def bing(query, limit):
    """Bing HTML with URL decode."""
    try:
        r = requests.get("https://www.bing.com/search",
            params={"q": query, "count": limit},
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
            out.append(_r(a.get_text(strip=True), href,
                p.get_text(strip=True) if p else "", "bing"))
        return out
    except Exception as e:
        logger.debug(f"bing: {e}"); return []

import requests

BASE_SCRAPERS = [bing, searxng, ddgs, whoogle, slopsearx]
ALL_ENGINES = BASE_SCRAPERS + ALL_EXTRA_SCRAPERS + ALL_PUBLIC_APIS + [tavily, exa, jina, serper, firecrawl, brave_api] + ALL_EXTRA_APIS

def search(query, limit=20):
    """Run all engines, dedupe, log status."""
    results = []
    stats = {}
    for fn in ALL_ENGINES:
        name = fn.__name__
        try:
            r = fn(query, limit)
            if r:
                stats[name] = len(r)
                results.extend(r)
                logger.info(f"[OK] {name}: {len(r)}")
            else:
                logger.debug(f"[EMPTY] {name}")
        except Exception as e:
            logger.warning(f"[ERR] {name}: {str(e)[:80]}")

    seen = set()
    unique = []
    for r in results:
        url = r.get("url", "")
        if url and url not in seen:
            seen.add(url)
            unique.append(r)
    return unique[:limit], stats

def search_legacy(query, limit=20):
    """Backward compat - return only results."""
    r, _ = search(query, limit)
    return r
