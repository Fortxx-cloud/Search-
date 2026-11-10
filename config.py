import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
    EXA_API_KEY = os.getenv("EXA_API_KEY", "")
    JINA_API_KEY = os.getenv("JINA_API_KEY", "")
    SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")
    FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "")
    BRAVE_API_KEY = os.getenv("BRAVE_API_KEY", "")
    GOOGLE_CSE_KEY = os.getenv("GOOGLE_CSE_KEY", "")
    GOOGLE_CSE_CX = os.getenv("GOOGLE_CSE_CX", "")
    YEP_API_KEY = os.getenv("YEP_API_KEY", "")
    YOU_API_KEY = os.getenv("YOU_API_KEY", "")
    SEARCH_TIMEOUT = int(os.getenv("SEARCH_TIMEOUT", "20"))
    SEARCH_MAX_RESULTS = int(os.getenv("SEARCH_MAX_RESULTS", "20"))
    SEARXNG_URL = os.getenv("SEARXNG_URL", "")
    FLASK_PORT = int(os.getenv("SERVER_PORT", os.getenv("PORT", os.getenv("FLASK_PORT", "8080"))))
