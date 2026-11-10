"""DDGS - Dux Distributed Global Search (metasearch library).
Agregasi: bing, brave, duckduckgo, google, mojeek, startpage, yandex, yahoo, wikipedia.
"""
from config import Config

def _r(t, u, s, src):
    return {"title": t, "url": u, "snippet": s, "source": src}

def ddgs(query, limit=10):
    try:
        from ddgs import DDGS
    except ImportError:
        print("[ddgs] package not installed")
        return []

    backends = ["bing", "brave", "duckduckgo", "google", "mojeek",
                "startpage", "yandex", "yahoo", "wikipedia"]
    out = []
    seen = set()

    try:
        with DDGS(timeout=Config.SEARCH_TIMEOUT) as client:
            for backend in backends:
                try:
                    results = client.text(query, backend=backend, max_results=limit)
                    for x in results:
                        url = x.get("href") or x.get("url") or ""
                        if not url or url in seen:
                            continue
                        seen.add(url)
                        out.append(_r(
                            x.get("title", ""),
                            url,
                            (x.get("body") or x.get("snippet") or "")[:200],
                            f"ddgs-{backend}",
                        ))
                        if len(out) >= limit:
                            return out
                except Exception:
                    continue
    except Exception as e:
        print(f"[ddgs] {e}")

    return out[:limit]
