from fastapi import FastAPI, HTTPException
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from scrapegraphai.graphs import SmartScraperGraph
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration for Cloudflare Bypass
# We use Playwright with Chromium and specifically enable 'stealth'
graph_config = {
    "llm": {
        "api_key": os.getenv("GEMINI_API_KEY", "AIzaSyD8hWUE0EgJ32LyuenYtQVWENRJSUNJr1g"),
        "model": "google_genai/gemini-2.5-flash",
    },
    "headless": True,
   "library": "playwright"
   
}

def run_static_scraper():
    STATIC_URL = "https://www.expatriates.com/scripts/search/search.epl?page=2&category_id=50&region_id=49"
    
    # SmartScraperGraph will now use Playwright under the hood
    smart_scraper_graph = SmartScraperGraph(
        prompt="Extract all listings. For each item, find the title, description, price, location, and link. Return a list of clean dictionaries.",
        source=STATIC_URL,
        config=graph_config
    )
    return smart_scraper_graph.run()

@app.get("/get-listings")
async def get_listings():
    try:
        # Running in a thread to keep the FastAPI event loop free
        result = await asyncio.to_thread(run_static_scraper)
        return result
    except Exception as e:
        print(f"Scraper Error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 

if __name__ == "__main__":
    import uvicorn
    # Render uses the PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)