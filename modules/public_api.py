"""Public APIs that work from cloud IPs. No key needed."""
import requests
from bs4 import BeautifulSoup
from config import Config

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
        t = d[1] if len(d) > 1 else []
        ds = d[2] if len(d) > 2 else []
        u = d[3] if len(d) > 3 else []
        return [_r(a, c, b, "wikipedia") for a, b, c in zip(t, ds, u)]
    except Exception as e:
        print("[wikipedia]", e); return []

def publicapis(query, limit):
    """api.publicapis.org - directory of free APIs. DIRECT for discovery."""
    try:
        r = requests.get("https://api.publicapis.org/entries",
            params={"title": query}, headers={"User-Agent": UA},
            timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        data = r.json()
        entries = (data.get("entries") or [])[:limit]
        out = []
        for e in entries:
            out.append(_r(
                e.get("API", ""),
                e.get("Link", ""),
                f"{e.get('Description', '')[:150]} | Auth: {e.get('Auth', '')} | HTTPS: {e.get('HTTPS', False)}",
                "publicapis"
            ))
        return out
    except Exception as e:
        print("[publicapis]", e); return []

def apisguru(query, limit):
    """apis.guru - OpenAPI directory."""
    try:
        r = requests.get("https://api.apis.guru/v2/list.json",
            headers={"User-Agent": UA}, timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        data = r.json()
        q_lower = query.lower()
        out = []
        for name, info in data.items():
            if q_lower in name.lower() or any(q_lower in str(v).lower() for v in info.get("versions", {}).values()):
                preferred = info.get("preferred", "")
                version_data = info.get("versions", {}).get(preferred, {})
                out.append(_r(
                    version_data.get("info", {}).get("title", name),
                    version_data.get("link", "") or version_data.get("info", {}).get("contact", {}).get("url", ""),
                    version_data.get("info", {}).get("description", "")[:150],
                    "apisguru"
                ))
                if len(out) >= limit: break
        return out
    except Exception as e:
        print("[apisguru]", e); return []

def hackernews(query, limit):
    try:
        r = requests.get("https://hn.algolia.com/api/v1/search",
            params={"query": query, "hitsPerPage": limit},
            headers={"User-Agent": UA}, timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        return [_r(
            x.get("title") or x.get("story_title") or "",
            x.get("url") or f"https://news.ycombinator.com/item?id={x.get('objectID', '')}",
            (x.get("comment_text") or "")[:150],
            "hackernews"
        ) for x in r.json().get("hits", [])]
    except Exception as e:
        print("[hackernews]", e); return []

def github(query, limit):
    import os
    headers = {"User-Agent": UA, "Accept": "application/vnd.github+json"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        r = requests.get("https://api.github.com/search/repositories",
            params={"q": query, "per_page": limit},
            headers=headers, timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        return [_r(x.get("full_name", ""), x.get("html_url", ""),
            (x.get("description") or "")[:150], "github")
            for x in r.json().get("items", [])]
    except Exception as e:
        print("[github]", e); return []

def stackoverflow(query, limit):
    try:
        r = requests.get("https://api.stackexchange.com/2.3/search/advanced",
            params={"order": "desc", "sort": "relevance", "q": query,
                    "site": "stackoverflow", "pagesize": limit},
            headers={"User-Agent": UA}, timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        return [_r(x.get("title", ""), x.get("link", ""),
            x.get("tags", []) and ", ".join(x["tags"]) or "", "stackoverflow")
            for x in r.json().get("items", [])]
    except Exception as e:
        print("[stackoverflow]", e); return []

def npm(query, limit):
    try:
        r = requests.get("https://registry.npmjs.org/-/v1/search",
            params={"text": query, "size": limit},
            headers={"User-Agent": UA}, timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        return [_r(x["package"].get("name", ""),
            x["package"].get("links", {}).get("npm", ""),
            x["package"].get("description", "")[:150], "npm")
            for x in r.json().get("objects", [])]
    except Exception as e:
        print("[npm]", e); return []

def arxiv(query, limit):
    try:
        r = requests.get("http://export.arxiv.org/api/query",
            params={"search_query": f"all:{query}", "max_results": limit},
            headers={"User-Agent": UA}, timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        soup = BeautifulSoup(r.text, "xml")
        out = []
        for entry in soup.find_all("entry")[:limit]:
            t = entry.find("title")
            l = entry.find("id")
            s = entry.find("summary")
            out.append(_r(t.text.strip() if t else "", l.text if l else "",
                (s.text.strip()[:150] if s else ""), "arxiv"))
        return out
    except Exception as e:
        print("[arxiv]", e); return []

def crossref(query, limit):
    try:
        r = requests.get("https://api.crossref.org/works",
            params={"query": query, "rows": limit},
            headers={"User-Agent": UA}, timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        return [_r((x.get("title") or [""])[0], x.get("URL", ""),
            (x.get("abstract") or "")[:150], "crossref")
            for x in r.json().get("message", {}).get("items", [])]
    except Exception as e:
        print("[crossref]", e); return []

def openalex(query, limit):
    try:
        r = requests.get("https://api.openalex.org/works",
            params={"search": query, "per-page": limit},
            headers={"User-Agent": UA}, timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        out = []
        for x in r.json().get("results", []):
            url = x.get("doi") or x.get("id", "")
            out.append(_r(x.get("display_name", "") or "", url, "", "openalex"))
        return out
    except Exception as e:
        print("[openalex]", e); return []

def mdn(query, limit):
    try:
        r = requests.get("https://developer.mozilla.org/api/v1/search",
            params={"q": query, "size": limit},
            headers={"User-Agent": UA}, timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        return [_r(x.get("title", ""),
            "https://developer.mozilla.org" + x.get("mdn_url", ""),
            x.get("summary", "")[:150], "mdn")
            for x in r.json().get("documents", [])]
    except Exception as e:
        print("[mdn]", e); return []

def openlibrary(query, limit):
    try:
        r = requests.get("https://openlibrary.org/search.json",
            params={"q": query, "limit": limit},
            headers={"User-Agent": UA}, timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        return [_r(x.get("title", ""),
            f"https://openlibrary.org{x.get('key', '')}",
            (x.get("author_name") or [""])[0], "openlibrary")
            for x in r.json().get("docs", [])]
    except Exception as e:
        print("[openlibrary]", e); return []

ALL_PUBLIC_APIS = [wikipedia, publicapis, apisguru, hackernews, github,
                   stackoverflow, npm, arxiv, crossref, openalex, mdn, openlibrary]
