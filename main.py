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
    'youtube.com/watch',  # avoid individual videos
]

class SearchRequest(BaseModel):
    query: str
    content_type: str = "all"

def extract_year_from_text(text):
    """Extract year from snippet or title"""
    if not text:
        return None
    
    # Look for patterns like "2012", "Jan 2015", "2010-01-01"
    year_patterns = [
        r'\b(20\d{2})\b',  # Match 2000-2099
        r'\b(19\d{2})\b',  # Match 1900-1999
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
        
        # Check if it's a quality domain
        if domain in QUALITY_DOMAINS:
            return QUALITY_DOMAINS[domain]
        
        # Check if .edu domain
        if domain.endswith('.edu'):
            return 25
        
        # Check if it's a domain to avoid
        for avoid in AVOID_PATTERNS:
            if avoid in domain:
                return 0
        
        # Default score for unknown domains
        return 10
    except:
        return 10

def calculate_quality_score(item):
    """Calculate overall quality score for a search result"""
    score = 0
    badges = []
    
    # 1. Domain Authority (0-35 points)
    url = item.get('link', '')
    domain_score = get_domain_score(url)
    score += domain_score
    
    if domain_score >= 25:
        badges.append("⭐ Trusted Source")
    
    # 2. Content Length (0-25 points)
    snippet = item.get('snippet', '')
    title = item.get('title', '')
    
    # Estimate content depth from snippet length and richness
    snippet_length = len(snippet)
    if snippet_length > 200:
        score += 25
        badges.append("📚 Long-form Content")
    elif snippet_length > 150:
        score += 15
    elif snippet_length > 100:
        score += 10
    else:
        score += 5
    
    # 3. Date/Era Score (0-20 points)
    # Try to extract year from snippet or title
    year = extract_year_from_text(snippet + " " + title)
    
    if year:
        if 2010 <= year <= 2015:
            score += 20
            badges.append(f"🕰️ Golden Era ({year})")
        elif 2005 <= year <= 2009:
            score += 15
            badges.append(f"📅 Classic ({year})")
        elif 2000 <= year <= 2004:
            score += 10
    else:
        # No year found, assume it's pre-2016 due to our search filter
        score += 12
        badges.append("📅 Pre-2016")
    
    # 4. Content Type (0-15 points)
    # Check URL and title for content type indicators
    content_indicators = {
        'essay': 15,
        'article': 12,
        'guide': 12,
        'tutorial': 10,
        'analysis': 12,
        'introduction': 10,
        'primer': 10,
        'overview': 8,
    }
    
    text_to_check = (url + " " + title).lower()
    content_type_found = False
    
    for indicator, points in content_indicators.items():
        if indicator in text_to_check:
            score += points
            content_type_found = True
            break
    
    if not content_type_found:
        score += 5
    
    # 5. Title Quality (0-5 points)
    # Longer, more descriptive titles tend to be better content
    title_length = len(title)
    if title_length > 60:
        score += 5
    elif title_length > 40:
        score += 3
    
    # Add quality badge based on final score
    if score >= 70:
        badges.insert(0, "💎 Exceptional Quality")
    elif score >= 60:
        badges.insert(0, "✨ High Quality")
    elif score >= 50:
        badges.insert(0, "👍 Good Quality")
    
    return score, badges

@app.get("/")
async def root():
    return {"status": "PreSlop API Running", "version": "2.0"}

@app.post("/search")
async def search(request: SearchRequest):
    query = request.query
    
    # Enhanced search query for better results
    # Add terms that help find essay-style content
    enhanced_query = f"{query} (essay OR article OR guide OR analysis) before:2016-01-01"
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "q": enhanced_query,
        "num": 10,  # Get 10 results to choose from
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
                "snippet": "Try a different search term or topic",
                "source": "Search",
                "date": "N/A",
                "quality_badges": [],
                "quality_score": 0
            }
        
        # Score all results
        scored_results = []
        for item in data["items"]:
            score, badges = calculate_quality_score(item)
            
            # Filter out low quality results (score < 40)
            if score >= 40:
                scored_results.append({
                    "item": item,
                    "score": score,
                    "badges": badges
                })
        
        # If no results passed the quality threshold, lower it
        if not scored_results:
            for item in data["items"]:
                score, badges = calculate_quality_score(item)
                if score >= 30:
                    scored_results.append({
                        "item": item,
                        "score": score,
                        "badges": badges
                    })
        
        # Still no results? Just take the best of what we have
        if not scored_results:
            for item in data["items"]:
                score, badges = calculate_quality_score(item)
                scored_results.append({
                    "item": item,
                    "score": score,
                    "badges": badges
                })
        
        # Sort by score (highest first)
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        
        # Get the best result
        best = scored_results[0]
        item = best["item"]
        
        # Extract domain for display
        try:
            domain = urlparse(item.get("link", "")).netloc.replace('www.', '')
        except:
            domain = item.get("displayLink", "Unknown")
        
        return {
            "content_type": "text",
            "title": item.get("title", "Untitled"),
            "url": item.get("link", "#"),
            "snippet": item.get("snippet", "No description available"),
            "source": domain,
            "date": "Pre-2016",
            "quality_badges": best["badges"],
            "quality_score": best["score"]
        }
        
    except Exception as e:
        return {
            "content_type": "text",
            "title": "Search Error",
            "url": "#",
            "snippet": f"Error searching: {str(e)}",
            "source": "Error",
            "date": "N/A",
            "quality_badges": [],
            "quality_score": 0
        }

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
