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

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/search")
def search():
    q = request.args.get("q", "").strip()
    if not q: return jsonify({"error": "q required"}), 400
    limit = int(request.args.get("limit", "20"))
    results = search_mod.search(q, limit=limit)
    return jsonify({"query": q, "count": len(results), "results": results})

@app.route("/discover")
def discover():
    q = request.args.get("q", "").strip()
    if not q: return jsonify({"error": "q required"}), 400
    results = search_mod.search(q, limit=20)
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
