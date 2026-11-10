"""webless - multi-engine (DDG, Mojeek, Bing, Wikipedia)."""
import asyncio
from config import Config

def _r(t, u, s, src):
    return {"title": t, "url": u, "snippet": s, "source": src}

def webless(query, limit=10):
    try:
        from webless import search as webless_search
    except ImportError:
        return []
    async def _run():
        try:
            result = await webless_search(query, limit=limit, wide=False,
                timeout=Config.SEARCH_TIMEOUT)
            return result.hits if hasattr(result, "hits") else []
        except Exception:
            return []
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        hits = loop.run_until_complete(_run())
        loop.close()
    except Exception:
        return []
    return [_r(h.title, h.url, (h.snippet or "")[:200], "webless")
            for h in hits[:limit]]
