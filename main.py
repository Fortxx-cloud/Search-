import os, sys
from flask import Flask, jsonify, request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Config
from modules import search as search_mod
from modules import extractor, database

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"service": "pusat-search", "version": "1.0.0",
                    "endpoints": ["/health", "/search?q=", "/discover?q="]})

@app.route("/engines")
def engines_health():
    import time
    from modules.search import ALL_ENGINES
    out = {}
    for fn in ALL_ENGINES:
        name = fn.__name__
        t0 = time.time()
        try:
            r = fn("test", 3)
            out[name] = {"status": "ok" if r else "empty",
                         "count": len(r), "ms": int((time.time()-t0)*1000)}
        except Exception as e:
            out[name] = {"status": "error", "error": str(e)[:80],
                         "ms": int((time.time()-t0)*1000)}
    alive = sum(1 for v in out.values() if v["status"] == "ok")
    return jsonify({"alive": alive, "total": len(out), "engines": out})

@app.route("/cache")
def cache_info():
    from modules.search import cache_stats
    return jsonify(cache_stats())

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/search")
def search():
    q = request.args.get("q", "").strip()
    if not q: return jsonify({"error": "q required"}), 400
    limit = int(request.args.get("limit", "20"))
    results, stats = search_mod.search(q, limit=limit)
    return jsonify({"query": q, "count": len(results), "sources": stats, "results": results})

@app.route("/discover")
def discover():
    q = request.args.get("q", "").strip()
    if not q: return jsonify({"error": "q required"}), 400
    results, _ = search_mod.search(q, limit=20)
    apis = extractor.extract(q, results)
    database.init_db()
    saved = 0
    for api in apis:
        try:
            database.save(q, api)
            saved += 1
        except: pass
    return jsonify({"query": q, "search_results": len(results),
                    "apis_extracted": len(apis), "apis_saved": saved, "apis": apis})

if __name__ == "__main__":
    database.init_db()
    port = Config.FLASK_PORT
    print(f"[PUSAT-SEARCH] port={port} ai={'gemini' if Config.GEMINI_API_KEY else 'groq' if Config.GROQ_API_KEY else 'none'}")
    app.run(host="0.0.0.0", port=port, debug=False)
