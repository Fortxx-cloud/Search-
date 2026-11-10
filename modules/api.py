"""API cloud with key (Tavily, Exa, Jina, Serper, Firecrawl, Brave)."""
import requests
from config import Config


def _r(t, u, s, src):
    return {"title": t, "url": u, "snippet": s, "source": src}


def tavily(query, limit=10):
    if not Config.TAVILY_API_KEY:
        return []
    try:
        r = requests.post(
            "https://api.tavily.com/search",
            json={"api_key": Config.TAVILY_API_KEY, "query": query,
                  "max_results": limit, "include_answer": False},
            timeout=Config.SEARCH_TIMEOUT)
        if not r.ok:
            return []
        return [_r(x.get("title", ""), x.get("url", ""),
                   (x.get("content") or "")[:200], "tavily")
                for x in r.json().get("results", [])]
    except Exception as e:
        print("[tavily]", e); return []


def exa(query, limit=10):
    if not Config.EXA_API_KEY:
        return []
    try:
        r = requests.post(
            "https://api.exa.ai/search",
            headers={"x-api-key": Config.EXA_API_KEY,
                     "Content-Type": "application/json"},
            json={"query": query, "numResults": limit,
                  "contents": {"text": {"maxCharacters": 300}}},
            timeout=Config.SEARCH_TIMEOUT)
        if not r.ok:
            return []
        return [_r(x.get("title") or "", x.get("url", ""),
                   (x.get("text") or "")[:200], "exa")
                for x in r.json().get("results", [])]
    except Exception as e:
        print("[exa]", e); return []


def jina(query, limit=10):
    if not Config.JINA_API_KEY:
        return []
    try:
        r = requests.get(
            f"https://s.jina.ai/{query}",
            headers={"Authorization": f"Bearer {Config.JINA_API_KEY}",
                     "Accept": "application/json"},
            timeout=Config.SEARCH_TIMEOUT)
        if not r.ok:
            return []
        ct = r.headers.get("content-type", "")
        data = r.json() if "json" in ct else {}
        return [_r(x.get("title", ""), x.get("url", ""),
                   (x.get("content") or "")[:200], "jina")
                for x in (data.get("data") or [])[:limit]]
    except Exception as e:
        print("[jina]", e); return []


def serper(query, limit=10):
    if not Config.SERPER_API_KEY:
        return []
    try:
        r = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": Config.SERPER_API_KEY,
                     "Content-Type": "application/json"},
            json={"q": query, "num": limit},
            timeout=Config.SEARCH_TIMEOUT)
        if not r.ok:
            return []
        return [_r(x.get("title", ""), x.get("link", ""),
                   x.get("snippet", ""), "serper")
                for x in r.json().get("organic", [])]
    except Exception as e:
        print("[serper]", e); return []


def firecrawl(query, limit=10):
    if not Config.FIRECRAWL_API_KEY:
        return []
    try:
        r = requests.post(
            "https://api.firecrawl.dev/v1/search",
            headers={"Authorization": f"Bearer {Config.FIRECRAWL_API_KEY}",
                     "Content-Type": "application/json"},
            json={"query": query, "limit": limit},
            timeout=Config.SEARCH_TIMEOUT)
        if not r.ok:
            return []
        return [_r(x.get("title") or "", x.get("url", ""),
                   (x.get("markdown") or x.get("description") or "")[:200],
                   "firecrawl")
                for x in r.json().get("data", [])]
    except Exception as e:
        print("[firecrawl]", e); return []


def brave_api(query, limit=10):
    if not Config.BRAVE_API_KEY:
        return []
    try:
        r = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={"X-Subscription-Token": Config.BRAVE_API_KEY,
                     "Accept": "application/json"},
            params={"q": query, "count": limit},
            timeout=Config.SEARCH_TIMEOUT)
        if not r.ok:
            return []
        return [_r(x.get("title", ""), x.get("url", ""),
                   x.get("description", ""), "brave")
                for x in r.json().get("web", {}).get("results", [])]
    except Exception as e:
        print("[brave]", e); return []
