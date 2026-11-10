# PUSAT-SEARCH

Discovery API gratis. Python murni, no Docker, no VPS.

## Deploy BotHosting

1. Upload ZIP ke panel
2. Extract
3. Set ENV:
   - GEMINI_API_KEY / GROQ_API_KEY (AI extractor)
   - DATABASE_URL (Neon)
   - JINA_API_KEY, EXA_API_KEY, TAVILY_API_KEY (opsional)
4. Start: `python main.py`

## Endpoints

- GET /health
- GET /search?q=free+api+weather&limit=10
- GET /discover?q=free+api+weather (search + AI extract + save DB)

## Scraper (no key)
DuckDuckGo, Bing, Yahoo, Mojeek, Brave-html, Startpage

## API (key optional)
Tavily, Exa, Jina, Serper, Firecrawl, Brave

## Free tier semua
Tavily 1000/mo, Exa $10/mo, Jina 10M token, Serper 2500 once, Firecrawl 1000/mo, Brave 2000/mo
