"""PyPI - search Python packages (API resmi, stabil)."""
import requests
from config import Config

def _r(t, u, s, src):
    return {"title": t, "url": u, "snippet": s, "source": src}

def pypi(query, limit=10):
    try:
        r = requests.get("https://pypi.org/search/",
            params={"q": query}, headers={"User-Agent": "PUSAT-SEARCH/1.0"},
            timeout=Config.SEARCH_TIMEOUT)
        if not r.ok:
            return []
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, "lxml")
        out = []
        for pkg in soup.select(".package-snippet")[:limit]:
            name = pkg.select_one(".package-snippet__name")
            ver = pkg.select_one(".package-snippet__version")
            desc = pkg.select_one(".package-snippet__description")
            if not name:
                continue
            n = name.get_text(strip=True)
            out.append(_r(
                f"{n} {ver.get_text(strip=True) if ver else ''}",
                f"https://pypi.org/project/{n}/",
                (desc.get_text(strip=True) if desc else "")[:150],
                "pypi"
            ))
        return out
    except Exception:
        return []
