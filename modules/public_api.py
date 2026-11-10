"""Public APIs that work from cloud IPs."""
import requests
import base64
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
        return [_r(a, c, b, "wikipedia")
                for a, b, c in zip(d[1], d[2], d[3])]
    except Exception as e:
        print("[wikipedia]", e); return []

def publicapis_gh(query, limit):
    """GitHub public-apis list — replacement for dead api.publicapis.org.
    Reads README.md dari repo public-apis/public-apis, filter query."""
    try:
        r = requests.get(
            "https://raw.githubusercontent.com/public-apis/public-apis/master/README.md",
            headers={"User-Agent": UA}, timeout=15)
        if not r.ok: return []
        text = r.text
        q = query.lower()
        out = []
        # Format baris: | [API Name](https://...) | Description | Auth | HTTPS | CORS |
        for line in text.split("\n"):
            if not line.startswith("|") or "[!--" in line: continue
            if q not in line.lower(): continue
            # Extract: [Name](URL)
            m = re.search(r"\[([^\]]+)\]\(([^)]+)\)", line)
            if not m: continue
            name, url = m.group(1), m.group(2)
            # Skip header rows
            if name.lower() in ("api", "name", "---"): continue
            # Extract description (column 2)
            parts = [p.strip() for p in line.split("|")]
            desc = parts[2] if len(parts) > 2 else ""
            auth = parts[3] if len(parts) > 3 else ""
            out.append(_r(f"{name} (Auth: {auth})", url,
                         desc[:150], "publicapis-gh"))
            if len(out) >= limit: break
        return out
    except Exception as e:
        print("[publicapis-gh]", e); return []

# alias buat backward compat
def publicapis(query, limit):
    return publicapis_gh(query, limit)

def apisguru(query, limit):
    try:
        r = requests.get("https://api.apis.guru/v2/list.json",
            headers={"User-Agent": UA}, timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        data = r.json()
        q = query.lower()
        out = []
        for name, info in data.items():
            if q not in name.lower(): continue
            preferred = info.get("preferred", "")
            vd = info.get("versions", {}).get(preferred, {})
            out.append(_r(vd.get("info", {}).get("title", name),
                         vd.get("link", ""),
                         vd.get("info", {}).get("description", "")[:150],
                         "apisguru"))
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
        return [_r(x.get("title") or x.get("story_title") or "",
                   x.get("url") or f"https://news.ycombinator.com/item?id={x.get('objectID','')}",
                   (x.get("comment_text") or "")[:150], "hackernews")
                for x in r.json().get("hits", [])]
    except Exception as e:
        print("[hackernews]", e); return []

def github(query, limit):
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
                   ", ".join(x.get("tags", [])) or "", "stackoverflow")
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
            t = entry.find("title"); l = entry.find("id"); s = entry.find("summary")
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
        return [_r(x.get("display_name", "") or "",
                   x.get("doi") or x.get("id", ""), "", "openalex")
                for x in r.json().get("results", [])]
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

ALL_PUBLIC_APIS = [wikipedia, publicapis_gh, apisguru, hackernews, github,
                   stackoverflow, npm, arxiv, crossref, openalex, mdn, openlibrary]
