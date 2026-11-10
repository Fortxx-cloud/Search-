import requests
from config import Config
from bs4 import BeautifulSoup

UA = "PUSAT-SEARCH/1.0"

def _r(t, u, s, src):
    return {"title": t, "url": u, "snippet": s, "source": src}

def wikipedia(query, limit):
    try:
        r = requests.get("https://en.wikipedia.org/w/api.php",
            params={"action": "opensearch", "search": query, "limit": limit, "format": "json"},
            headers={"User-Agent": UA}, timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        d = r.json()
        titles = d[1] if len(d) > 1 else []
        descs = d[2] if len(d) > 2 else []
        urls = d[3] if len(d) > 3 else []
        return [_r(t, u, ds, "wikipedia") for t, ds, u in zip(titles, descs, urls)]
    except Exception as e:
        print("[wikipedia]", e); return []

def hackernews(query, limit):
    try:
        r = requests.get("https://hn.algolia.com/api/v1/search", params={"query": query, "hitsPerPage": limit}, timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        return [_r(x.get("title") or x.get("story_title") or "",
                   x.get("url") or "https://news.ycombinator.com/item?id=" + str(x.get("objectID","")),
                   (x.get("comment_text") or "")[:200], "hackernews")
                for x in r.json().get("hits", [])]
    except Exception as e:
        print("[hackernews]", e); return []

def reddit(query, limit):
    try:
        r = requests.get("https://www.reddit.com/search.json", params={"q": query, "limit": limit}, headers={"User-Agent": UA}, timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        return [_r(x["data"].get("title",""), "https://reddit.com" + x["data"].get("permalink",""),
                   (x["data"].get("selftext") or "")[:200], "reddit")
                for x in r.json().get("data",{}).get("children",[])]
    except Exception as e:
        print("[reddit]", e); return []

def github(query, limit):
    try:
        r = requests.get("https://api.github.com/search/repositories", params={"q": query, "per_page": limit}, headers={"User-Agent": UA}, timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        return [_r(x.get("full_name",""), x.get("html_url",""), (x.get("description") or "")[:200], "github")
                for x in r.json().get("items", [])]
    except Exception as e:
        print("[github]", e); return []

def stackoverflow(query, limit):
    try:
        r = requests.get("https://api.stackexchange.com/2.3/search",
            params={"order": "desc", "sort": "relevance", "intitle": query, "site": "stackoverflow", "pagesize": limit},
            timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        return [_r(x.get("title",""), x.get("link",""), "", "stackoverflow") for x in r.json().get("items", [])]
    except Exception as e:
        print("[stackoverflow]", e); return []

def npm(query, limit):
    try:
        r = requests.get("https://registry.npmjs.org/-/v1/search", params={"text": query, "size": limit}, timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        return [_r(x["package"].get("name",""), x["package"].get("links",{}).get("npm",""),
                   x["package"].get("description",""), "npm")
                for x in r.json().get("objects", [])]
    except Exception as e:
        print("[npm]", e); return []

def arxiv(query, limit):
    try:
        r = requests.get("http://export.arxiv.org/api/query",
            params={"search_query": "all:" + query, "max_results": limit}, timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        soup = BeautifulSoup(r.text, "xml")
        out = []
        for entry in soup.find_all("entry")[:limit]:
            t = entry.find("title"); l = entry.find("id"); s = entry.find("summary")
            out.append(_r(t.text.strip() if t else "", l.text if l else "",
                          (s.text.strip()[:200] if s else ""), "arxiv"))
        return out
    except Exception as e:
        print("[arxiv]", e); return []

def crossref(query, limit):
    try:
        r = requests.get("https://api.crossref.org/works", params={"query": query, "rows": limit}, timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        return [_r((x.get("title") or [""])[0], x.get("URL",""),
                   (x.get("abstract") or "")[:200], "crossref")
                for x in r.json().get("message",{}).get("items",[])]
    except Exception as e:
        print("[crossref]", e); return []

def openalex(query, limit):
    try:
        r = requests.get("https://api.openalex.org/works", params={"search": query, "per-page": limit}, timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        out = []
        for x in r.json().get("results", []):
            oid = x.get("id","")
            url = (x.get("doi") or oid or "")
            out.append(_r(x.get("display_name","") or "", url, "", "openalex"))
        return out
    except Exception as e:
        print("[openalex]", e); return []

def mdn(query, limit):
    try:
        r = requests.get("https://developer.mozilla.org/api/v1/search", params={"q": query, "size": limit}, timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        return [_r(x.get("title",""), "https://developer.mozilla.org" + x.get("mdn_url",""),
                   x.get("summary",""), "mdn")
                for x in r.json().get("documents", [])]
    except Exception as e:
        print("[mdn]", e); return []

ALL_PUBLIC_APIS = [wikipedia, hackernews, reddit, github, stackoverflow, npm, arxiv, crossref, openalex, mdn]
