from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import requests
import random
from datetime import datetime

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get API keys from environment
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

class SearchRequest(BaseModel):
    query: str
    content_type: str = "all"

@app.get("/")
async def root():
    return {"status": "PreSlop API Running", "version": "1.0"}

@app.post("/search")
async def search(request: SearchRequest):
    query = request.query
    
    # Search Google for pre-2016 content
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "q": f"{query} before:2016-01-01",
        "num": 10
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "items" not in data or len(data["items"]) == 0:
            return {
                "content_type": "text",
                "title": "No results found",
                "url": "#",
                "snippet": "Try a different search term",
                "source": "PreSlop",
                "date": "N/A",
                "quality_badges": []
            }
        
        # Get best result
        best = data["items"][0]
        
        return {
            "content_type": "text",
            "title": best.get("title", "Untitled"),
            "url": best.get("link", "#"),
            "snippet": best.get("snippet", "No description available"),
            "source": best.get("displayLink", "Unknown"),
            "date": "Pre-2016",
            "quality_badges": [
                "📚 Pre-2016 Content",
                "🎯 High Quality",
                "💎 Classic Article",
                "⭐ Top Result"
            ]
        }
    except Exception as e:
        return {
            "content_type": "text",
            "title": "Search Error",
            "url": "#",
            "snippet": str(e),
            "source": "Error",
            "date": "N/A",
            "quality_badges": []
        }

@app.get("/surprise")
async def surprise():
    topics = [
        "timeless philosophy",
        "classic productivity advice",
        "deep thinking frameworks",
        "forgotten wisdom",
        "vintage tutorials",
        "timeless life lessons",
        "old internet gems",
        "classic essays"
    ]
    topic = random.choice(topics)
    return await search(SearchRequest(query=topic, content_type="all"))
