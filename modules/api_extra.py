import requests
from config import Config

def _r(t, u, s, src):
    return {"title": t, "url": u, "snippet": s, "source": src}

def google_cse(query, limit):
    if not Config.GOOGLE_CSE_KEY or not Config.GOOGLE_CSE_CX: return []
    try:
        r = requests.get("https://www.googleapis.com/customsearch/v1",
            params={"key": Config.GOOGLE_CSE_KEY, "cx": Config.GOOGLE_CSE_CX, "q": query, "num": min(limit, 10)},
            timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        return [_r(x.get("title",""), x.get("link",""), x.get("snippet",""), "google-cse")
                for x in r.json().get("items", [])]
    except Exception as e:
        print("[google-cse]", e); return []

def yep(query, limit):
    if not Config.YEP_API_KEY: return []
    try:
        r = requests.get("https://api.yep.com/fs/2/search",
            params={"client": "web", "gl": "US", "limit": limit, "no_correct": "false", "q": query, "safeSearch": "off", "type": "web"},
            headers={"Authorization": "Bearer " + Config.YEP_API_KEY}, timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        out = []
        for group in r.json():
            if isinstance(group, list):
                for x in group[:limit]:
                    if isinstance(x, dict) and x.get("url"):
                        out.append(_r(x.get("title",""), x.get("url",""), x.get("snippet",""), "yep"))
        return out[:limit]
    except Exception as e:
        print("[yep]", e); return []

def you(query, limit):
    if not Config.YOU_API_KEY: return []
    try:
        r = requests.get("https://api.ydc-index.io/search",
            params={"query": query, "num_web_results": limit},
            headers={"X-API-Key": Config.YOU_API_KEY}, timeout=Config.SEARCH_TIMEOUT)
        if not r.ok: return []
        return [_r(x.get("title",""), x.get("url",""), (x.get("description") or "")[:200], "you")
                for x in r.json().get("hits", [])]
    except Exception as e:
        print("[you]", e); return []

ALL_EXTRA_APIS = [google_cse, yep, you]
