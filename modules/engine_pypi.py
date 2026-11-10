"""PyPI via libraries.io API (reliable, works from cloud)."""
import requests
from config import Config

def _r(t, u, s, src):
    return {"title": t, "url": u, "snippet": s, "source": src}

def pypi(query, limit=10):
    try:
        r = requests.get("https://libraries.io/api/search",
            params={"q": query, "platforms": "Pypi", "per_page": min(limit, 10)},
            headers={"User-Agent": "PUSAT-SEARCH/1.0"},
            timeout=Config.SEARCH_TIMEOUT)
        if not r.ok:
            return []
        data = r.json()
        if not isinstance(data, list):
            return []
        return [_r(
            x.get("name", ""),
            x.get("repository_url") or x.get("homepage") or f"https://pypi.org/project/{x.get('name','')}/",
            (x.get("description") or "")[:150],
            "pypi"
        ) for x in data[:limit]]
    except Exception:
        return []
