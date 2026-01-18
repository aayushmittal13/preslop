from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import requests
import random
import re
from datetime import datetime
from urllib.parse import urlparse

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

# Quality domains - known for timeless content
QUALITY_DOMAINS = {
    'paulgraham.com': 35,
    'waitbutwhy.com': 35,
    'lesswrong.com': 30,
    'fs.blog': 30,
    'gwern.net': 30,
    'slatestarcodex.com': 30,
    'jamesclear.com': 30,
    'aeon.co': 25,
    'nautil.us': 25,
    'longform.org': 25,
    'theatlantic.com': 20,
    'newyorker.com': 20,
    'harpers.org': 20,
    'nplusonemag.com': 20,
    'edge.org': 20,
}

# Low quality patterns to avoid
AVOID_PATTERNS = [
    'reddit.com',
    'quora.com',
    'answers.yahoo.com',
    'stackoverflow.com',
    'pinterest.com',
    'facebook.com',
    'twitter.com',
    'instagram.com',
    'youtube.com/watch',
]

class SearchRequest(BaseModel):
    query: str
    content_type: str = "all"

def extract_year_from_text(text):
    """Extract year from snippet or title"""
    if not text:
        return None
    
    year_patterns = [
        r'\b(20\d{2})\b',
        r'\b(19\d{2})\b',
    ]
    
    for pattern in year_patterns:
        match = re.search(pattern, text)
        if match:
            year = int(match.group(1))
            if 2000 <= year <= 2015:
                return year
    
    return None

def get_domain_score(url):
    """Calculate score based on domain quality"""
    try:
        domain = urlparse(url).netloc.lower()
        domain = domain.replace('www.', '')
        
        if domain in QUALITY_DOMAINS:
            return QUALITY_DOMAINS[domain]
        
        if domain.endswith('.edu'):
            return 25
        
        for avoid in AVOID_PATTERNS:
            if avoid in domain:
                return 0
        
        return 10
    except:
        return 10

def calculate_quality_score(item):
    """Calculate overall quality score for a search result"""
    score = 0
    
    # 1. Domain Authority (0-35 points)
    url = item.get('link', '')
    domain_score = get_domain_score(url)
    score += domain_score
    
    # 2. Content Length (0-25 points)
    snippet = item.get('snippet', '')
    snippet_length = len(snippet)
    if snippet_length > 200:
        score += 25
    elif snippet_length > 150:
        score += 15
    elif snippet_length > 100:
        score += 10
    else:
        score += 5
    
    # 3. Date/Era Score (0-20 points)
    title = item.get('title', '')
    year = extract_year_from_text(snippet + " " + title)
    
    if year:
        if 2010 <= year <= 2015:
            score += 20
        elif 2005 <= year <= 2009:
            score += 15
        elif 2000 <= year <= 2004:
            score += 10
    else:
        score += 12
    
    # 4. Content Type (0-15 points)
    content_indicators = {
        'essay': 15,
        'article': 12,
        'guide': 12,
        'tutorial': 10,
        'analysis': 12,
        'introduction': 10,
    }
    
    text_to_check = (url + " " + title).lower()
    
    for indicator, points in content_indicators.items():
        if indicator in text_to_check:
            score += points
            break
    else:
        score += 5
    
    # 5. Title Quality (0-5 points)
    title_length = len(title)
    if title_length > 60:
        score += 5
    elif title_length > 40:
        score += 3
    
    return score

@app.get("/")
async def root():
    return {"status": "PreSlop API Running", "version": "2.0"}

@app.post("/search")
async def search(request: SearchRequest):
    query = request.query
    
    # Enhanced search query
    enhanced_query = f"{query} (essay OR article OR guide OR analysis) before:2016-01-01"
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "q": enhanced_query,
        "num": 10,
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "items" not in data or len(data["items"]) == 0:
            return []
        
        # Score all results
        scored_results = []
        for item in data["items"]:
            score = calculate_quality_score(item)
            
            # Filter out very low quality (score < 35)
            if score >= 35:
                scored_results.append({
                    "item": item,
                    "score": score
                })
        
        # If we filtered out everything, lower the threshold
        if not scored_results:
            for item in data["items"]:
                score = calculate_quality_score(item)
                if score >= 25:
                    scored_results.append({
                        "item": item,
                        "score": score
                    })
        
        # Still nothing? Take whatever we have
        if not scored_results:
            for item in data["items"]:
                score = calculate_quality_score(item)
                scored_results.append({
                    "item": item,
                    "score": score
                })
        
        # Sort by score (highest first)
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        
        # Return top 3-4 results
        top_results = scored_results[:4]
        
        results = []
        for result in top_results:
            item = result["item"]
            
            # Extract domain for display
            try:
                domain = urlparse(item.get("link", "")).netloc.replace('www.', '')
            except:
                domain = item.get("displayLink", "Unknown")
            
            # Extract year if available
            year = extract_year_from_text(item.get("snippet", "") + " " + item.get("title", ""))
            date_str = str(year) if year else "Pre-2016"
            
            # Create better gist/summary
            snippet = item.get("snippet", "")
            
            # Try to get meta description from pagemap (often better than snippet)
            if "pagemap" in item and "metatags" in item["pagemap"]:
                metatags = item["pagemap"]["metatags"]
                if metatags and len(metatags) > 0:
                    meta_desc = metatags[0].get("og:description") or metatags[0].get("description") or metatags[0].get("twitter:description")
                    if meta_desc and len(meta_desc) > len(snippet):
                        snippet = meta_desc
            
            # If still no good snippet
            if not snippet:
                snippet = "No description available."
            
            # Clean up the snippet
            # Remove date patterns at the beginning
            snippet = re.sub(r'^[A-Z][a-z]{2}\s+\d{1,2},\s+\d{4}\s*[-—\.]\s*', '', snippet)
            snippet = re.sub(r'^\d{4}\s*[-—\.]\s*', '', snippet)
            
            # Remove "Read more" type endings
            snippet = re.sub(r'\s*\.\.\.\s*(read more|continue reading|more).*$', '...', snippet, flags=re.IGNORECASE)
            
            # Limit length but keep it meaningful (200-300 chars is good)
            if len(snippet) > 300:
                # Find last sentence ending before 300 chars
                last_period = snippet[:300].rfind('.')
                if last_period > 150:  # Make sure we have enough content
                    snippet = snippet[:last_period + 1]
                else:
                    snippet = snippet[:300] + '...'
            
            # Ensure it ends properly
            if not snippet.endswith(('...', '.', '!', '?')):
                snippet = snippet + '...'
            
            results.append({
                "title": item.get("title", "Untitled"),
                "url": item.get("link", "#"),
                "snippet": snippet,
                "source": domain,
                "date": date_str,
                "quality_score": result["score"]
            })
        
        return results
        
    except Exception as e:
        return []

@app.get("/surprise")
async def surprise():
    """Get a random timeless topic"""
    topics = [
        "philosophy of time",
        "cognitive biases",
        "systems thinking",
        "decision making frameworks",
        "the nature of consciousness",
        "productivity and deep work",
        "writing and storytelling",
        "learning and memory",
        "human psychology",
        "game theory",
        "probability and statistics",
        "evolution and biology",
        "physics and reality",
        "mathematics and logic",
        "economics and incentives",
        "history and civilization",
        "technology and society",
        "art and creativity",
        "meditation and mindfulness",
        "stoic philosophy",
    ]
    topic = random.choice(topics)
    return await search(SearchRequest(query=topic, content_type="all"))
