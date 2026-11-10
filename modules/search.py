# 12 search engines: 6 scraper (no key) + 6 API (key optional)
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
from config import Config

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

def _r(title, url, snippet, source):
    return {"title": title, "url": url, "snippet": snippet, "source": source}

def ddg(query, limit):
    try:
        r = requests.post("https://html.duckduckgo.com/html/",
            data={"q": query}, headers={"User-Agent": UA},
            timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        soup = BeautifulSoup(r.text, "lxml")
        out = []
        for res in soup.select(".result")[:limit]:
            a = res.select_one(".result__a")
            s = res.select_one(".result__snippet")
            if not a: continue
            url = a.get("href", "")
            m = re.search(r"uddg=([^&]+)", url)
            if m: url = unquote(m.group(1))
            out.append(_r(a.get_text(strip=True), url,
                s.get_text(strip=True) if s else "", "duckduckgo"))
        return out
    except Exception as e:
        print("[ddg]", e); return []

def bing(query, limit):
    try:
        r = requests.get("https://www.bing.com/search",
            params={"q": query, "count": limit},
            headers={"User-Agent": UA}, timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        soup = BeautifulSoup(r.text, "lxml")
        out = []
        for li in soup.select("li.b_algo")[:limit]:
            a = li.select_one("h2 a")
            p = li.select_one("p")
            if not a: continue
            out.append(_r(a.get_text(strip=True), a.get("href", ""),
                p.get_text(strip=True) if p else "", "bing"))
        return out
    except Exception as e:
        print("[bing]", e); return []

def yahoo(query, limit):
    try:
        r = requests.get("https://search.yahoo.com/search",
            params={"p": query}, headers={"User-Agent": UA},
            timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        soup = BeautifulSoup(r.text, "lxml")
        out = []
        for div in soup.select("div.algo")[:limit]:
            a = div.select_one("h3 a")
            p = div.select_one(".compText")
            if not a: continue
            out.append(_r(a.get_text(strip=True), a.get("href", ""),
                p.get_text(strip=True) if p else "", "yahoo"))
        return out
    except Exception as e:
        print("[yahoo]", e); return []

def mojeek(query, limit):
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

def brave_html(query, limit):
    try:
        r = requests.get("https://search.brave.com/search",
            params={"q": query}, headers={"User-Agent": UA},
            timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        soup = BeautifulSoup(r.text, "lxml")
        out = []
        for div in soup.select("[data-type='web']")[:limit]:
            a = div.select_one("a")
            if not a: continue
            t = div.select_one(".title") or a
            s = div.select_one(".snippet")
            out.append(_r(t.get_text(strip=True), a.get("href", ""),
                s.get_text(strip=True) if s else "", "brave-html"))
        return out
    except Exception as e:
        print("[brave-html]", e); return []

def startpage(query, limit):
    try:
        r = requests.get("https://www.startpage.com/sp/search",
            params={"query": query}, headers={"User-Agent": UA},
            timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        soup = BeautifulSoup(r.text, "lxml")
        out = []
        for div in soup.select(".w-gl__result")[:limit]:
            a = div.select_one(".w-gl__result-title")
            p = div.select_one(".w-gl__description")
            if not a: continue
            out.append(_r(a.get_text(strip=True), a.get("href", ""),
                p.get_text(strip=True) if p else "", "startpage"))
        return out
    except Exception as e:
        print("[startpage]", e); return []

def tavily(query, limit):
    if not Config.TAVILY_API_KEY: return []
    try:
        r = requests.post("https://api.tavily.com/search",
            json={"api_key": Config.TAVILY_API_KEY, "query": query,
                  "max_results": limit}, timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        return [_r(x.get("title",""), x.get("url",""),
            (x.get("content") or "")[:300], "tavily")
            for x in r.json().get("results", [])]
    except Exception as e:
        print("[tavily]", e); return []

def exa(query, limit):
    if not Config.EXA_API_KEY: return []
    try:
        r = requests.post("https://api.exa.ai/search",
            headers={"x-api-key": Config.EXA_API_KEY, "Content-Type": "application/json"},
            json={"query": query, "numResults": limit,
                  "contents": {"text": {"maxCharacters": 300}}},
            timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        return [_r(x.get("title") or "", x.get("url",""),
            (x.get("text") or "")[:300], "exa")
            for x in r.json().get("results", [])]
    except Exception as e:
        print("[exa]", e); return []

def jina(query, limit):
    if not Config.JINA_API_KEY: return []
    try:
        r = requests.get(f"https://s.jina.ai/{query}",
            headers={"Authorization": f"Bearer {Config.JINA_API_KEY}",
                     "Accept": "application/json"},
            timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        data = r.json() if "json" in r.headers.get("content-type","") else {}
        return [_r(x.get("title",""), x.get("url",""),
            (x.get("content") or "")[:300], "jina")
            for x in (data.get("data") or [])[:limit]]
    except Exception as e:
        print("[jina]", e); return []

def serper(query, limit):
    if not Config.SERPER_API_KEY: return []
    try:
        r = requests.post("https://google.serper.dev/search",
            headers={"X-API-KEY": Config.SERPER_API_KEY,
                     "Content-Type": "application/json"},
            json={"q": query, "num": limit},
            timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        return [_r(x.get("title",""), x.get("link",""),
            x.get("snippet",""), "serper")
            for x in r.json().get("organic", [])]
    except Exception as e:
        print("[serper]", e); return []

def firecrawl(query, limit):
    if not Config.FIRECRAWL_API_KEY: return []
    try:
        r = requests.post("https://api.firecrawl.dev/v1/search",
            headers={"Authorization": f"Bearer {Config.FIRECRAWL_API_KEY}",
                     "Content-Type": "application/json"},
            json={"query": query, "limit": limit},
            timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        return [_r(x.get("title") or "", x.get("url",""),
            (x.get("markdown") or x.get("description") or "")[:300], "firecrawl")
            for x in r.json().get("data", [])]
    except Exception as e:
        print("[firecrawl]", e); return []

def brave_api(query, limit):
    if not Config.BRAVE_API_KEY: return []
    try:
        r = requests.get("https://api.search.brave.com/res/v1/web/search",
            headers={"X-Subscription-Token": Config.BRAVE_API_KEY,
                     "Accept": "application/json"},
            params={"q": query, "count": limit},
            timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        return [_r(x.get("title",""), x.get("url",""),
            x.get("description",""), "brave")
            for x in r.json().get("web", {}).get("results", [])]
    except Exception as e:
        print("[brave]", e); return []

SCRAPERS = [ddg, bing, yahoo, mojeek, brave_html, startpage]
APIS = [tavily, exa, jina, serper, firecrawl, brave_api]

def _dedupe(results, limit):
    seen = set()
    unique = []
    for r in results:
        if r.get("url") and r["url"] not in seen:
            seen.add(r["url"])
            unique.append(r)
    return unique[:limit]

def search(query, limit=20):
    results = []
    for fn in SCRAPERS + APIS:
        try: results.extend(fn(query, limit))
        except Exception as e: print(f"[{fn.__name__}]", e)
    return _dedupe(results, limit)

def search_scrapers_only(query, limit=20):
    results = []
    for fn in SCRAPERS:
        try: results.extend(fn(query, limit))
        except Exception as e: print(f"[{fn.__name__}]", e)
    return _dedupe(results, limit)


# === EXTENDED ENGINES ===
from modules.scraper_extra import ALL_EXTRA_SCRAPERS
from modules.public_api import ALL_PUBLIC_APIS
from modules.api_extra import ALL_EXTRA_APIS
SCRAPERS.extend(ALL_EXTRA_SCRAPERS)
APIS.extend(ALL_PUBLIC_APIS + ALL_EXTRA_APIS)
