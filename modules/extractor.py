# AI extractor: pakai Gemini/Groq buat extract info API
import json
import requests
from config import Config

PROMPT = (
    "Extract API info dari search results ini. Return JSON array SAJA:\n"
    "[{\"name\":\"...\",\"url\":\"...\",\"category\":\"...\","
    "\"auth_type\":\"...\",\"free_tier\":\"...\"}]\n\n"
    "Results:\n{results}\n\nReturn [] kalau nggak ada API."
)

def _parse(text):
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]) if len(lines) > 2 else text
    try:
        return json.loads(text)
    except:
        import re
        m = re.search(r"\[.*\]", text, re.DOTALL)
        if m:
            try: return json.loads(m.group(0))
            except: pass
        return []

def extract(query, results):
    if not results: return []
    text = "\n".join(
        f"- {r['title']}\n  {r['url']}\n  {r['snippet'][:150]}"
        for r in results[:10]
    )
    prompt = PROMPT.format(results=text)

    if Config.GEMINI_API_KEY:
        try:
            r = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
                params={"key": Config.GEMINI_API_KEY},
                json={"contents": [{"parts": [{"text": prompt}]}],
                      "generationConfig": {"maxOutputTokens": 2000, "temperature": 0.3}},
                timeout=60)
            if r.ok:
                return _parse(r.json()["candidates"][0]["content"]["parts"][0]["text"])
        except Exception as e:
            print("[extractor-gemini]", e)

    if Config.GROQ_API_KEY:
        try:
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {Config.GROQ_API_KEY}",
                         "Content-Type": "application/json"},
                json={"model": "llama-3.3-70b-versatile",
                      "messages": [{"role": "user", "content": prompt}],
                      "max_tokens": 2000, "temperature": 0.3},
                timeout=60)
            if r.ok:
                return _parse(r.json()["choices"][0]["message"]["content"])
        except Exception as e:
            print("[extractor-groq]", e)

    return []
