"""googlesearch-python - scrape Google tanpa API key."""
from config import Config

def _r(t, u, s, src):
    return {"title": t, "url": u, "snippet": s, "source": src}

def googlesearch(query, limit=10):
    try:
        from googlesearch import search as g_search
    except ImportError:
        return []
    out = []
    try:
        for url in g_search(query, num_results=min(limit, 8),
                            lang="en", sleep_interval=0.5, timeout=8):
            out.append(_r(url[:60], url, "", "google-scrape"))
            if len(out) >= limit:
                break
    except Exception:
        pass
    return out
