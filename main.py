from fastapi import FastAPI, HTTPException
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from scrapegraphai.graphs import SmartScraperGraph
import json

app = FastAPI()

# --- STEP 1: Enable CORS ---
# This allows your website to talk to this API even if they are on different domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace "*" with your website's URL
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- STEP 2: Configure Scraper ---
# Note: On a server (Render/Railway), we MUST use headless: True
graph_config = {
    "llm": {
        "api_key": "AIzaSyBE7WkkvyEe3Uosp2CuKlN0a_X2dWMTWH8",
        "model": "google_genai/gemini-2.5-flash",
    },
    "verbose": True,
    "headless": False, 
}

def run_static_scraper():
    """
    Scraper logic with a HARDCODED URL.
    """
    # Change this URL to exactly what you want to scrape every time
    STATIC_URL = "https://www.expatriates.com/scripts/search/search.epl?page=2&category_id=50&region_id=49"
    
    smart_scraper_graph = SmartScraperGraph(
        prompt="Extract all the text from the page and find the title, description, price, location, and link for each item for sale. Return the result as a list of dictionaries with keys: title, description, price, location, link. Make sure the data is all clean and well formatted",
        source=STATIC_URL,
        config=graph_config
    )
    return smart_scraper_graph.run()

@app.get("/get-listings")
async def get_listings():
    try:
        # We use to_thread to prevent the 'NoEventLoopError'
        result = await asyncio.to_thread(run_static_scraper)
        print(json.dumps(result, indent=4))
        return result
    
    except Exception as e:
        print(f"Scraper Error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)