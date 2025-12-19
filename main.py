"""
PreSlop Backend - Find Quality Pre-2016 Content
Pure algorithmic quality scoring without AI
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Literal
import httpx
import os
from datetime import datetime
import re

app = FastAPI(title="PreSlop API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str
    content_type: Optional[Literal["all", "text", "video"]] = "all"

class ContentResult(BaseModel):
    title: str
    url: str
    snippet: str
    date: str
    source: str
    quality_score: float
    quality_badges: List[str]
    content_type: str
    view_count: Optional[int] = None
    engagement_count: Optional[int] = None

# Configuration
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = "PreSlop/1.0"
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID", "")

# Check if we have credentials
HAS_REDDIT = bool(REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET)
HAS_YOUTUBE = bool(YOUTUBE_API_KEY)
HAS_GOOGLE = bool(GOOGLE_API_KEY and GOOGLE_CSE_ID)

async def get_reddit_token():
    """Get Reddit OAuth token"""
    if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
        return None
    
    async with httpx.AsyncClient() as client:
        auth = httpx.BasicAuth(REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET)
        data = {"grant_type": "client_credentials"}
        headers = {"User-Agent": REDDIT_USER_AGENT}
        
        try:
            response = await client.post(
                "https://www.reddit.com/api/v1/access_token",
                auth=auth,
                data=data,
                headers=headers
            )
            return response.json().get("access_token")
        except:
            return None

async def search_reddit(query: str, token: Optional[str]) -> List[dict]:
    """Search Reddit for pre-2016 posts"""
    if not token:
        return []
    
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": REDDIT_USER_AGENT
        }
        
        try:
            # Search Reddit
            response = await client.get(
                "https://oauth.reddit.com/search",
                headers=headers,
                params={
                    "q": query,
                    "limit": 100,
                    "sort": "relevance",
                    "t": "all"
                }
            )
            
            posts = response.json().get("data", {}).get("children", [])
            results = []
            
            for post in posts:
                data = post.get("data", {})
                created_utc = data.get("created_utc", 0)
                created_date = datetime.fromtimestamp(created_utc)
                
                # Only pre-2016 content
                if created_date.year >= 2016:
                    continue
                
                # Skip deleted/removed posts
                if data.get("selftext") == "[removed]" or data.get("selftext") == "[deleted]":
                    continue
                
                results.append({
                    "title": data.get("title", ""),
                    "url": f"https://reddit.com{data.get('permalink', '')}",
                    "snippet": data.get("selftext", "")[:300],
                    "date": created_date.strftime("%Y-%m-%d"),
                    "score": data.get("score", 0),
                    "num_comments": data.get("num_comments", 0),
                    "subreddit": data.get("subreddit", ""),
                    "author": data.get("author", ""),
                    "text_length": len(data.get("selftext", ""))
                })
            
            return results
        except Exception as e:
            print(f"Reddit search error: {e}")
            return []

async def search_youtube(query: str) -> List[dict]:
    """Search YouTube for pre-2016 videos"""
    if not YOUTUBE_API_KEY:
        return []
    
    async with httpx.AsyncClient() as client:
        try:
            # Search YouTube
            response = await client.get(
                "https://www.googleapis.com/youtube/v3/search",
                params={
                    "key": YOUTUBE_API_KEY,
                    "q": query,
                    "part": "snippet",
                    "type": "video",
                    "maxResults": 50,
                    "order": "relevance",
                    "publishedBefore": "2016-01-01T00:00:00Z"
                }
            )
            
            videos = response.json().get("items", [])
            video_ids = [v["id"]["videoId"] for v in videos if "videoId" in v["id"]]
            
            if not video_ids:
                return []
            
            # Get video statistics
            stats_response = await client.get(
                "https://www.googleapis.com/youtube/v3/videos",
                params={
                    "key": YOUTUBE_API_KEY,
                    "id": ",".join(video_ids),
                    "part": "snippet,statistics,contentDetails"
                }
            )
            
            results = []
            for video in stats_response.json().get("items", []):
                snippet = video["snippet"]
                stats = video["statistics"]
                
                # Parse duration
                duration = video["contentDetails"]["duration"]
                duration_seconds = parse_duration(duration)
                
                results.append({
                    "title": snippet["title"],
                    "url": f"https://www.youtube.com/watch?v={video['id']}",
                    "snippet": snippet["description"][:300],
                    "date": snippet["publishedAt"][:10],
                    "view_count": int(stats.get("viewCount", 0)),
                    "like_count": int(stats.get("likeCount", 0)),
                    "comment_count": int(stats.get("commentCount", 0)),
                    "channel_title": snippet["channelTitle"],
                    "duration_seconds": duration_seconds
                })
            
            return results
        except Exception as e:
            print(f"YouTube search error: {e}")
            return []

async def search_google(query: str) -> List[dict]:
    """Search Google Custom Search for pre-2016 blogs and articles"""
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        return []
    
    async with httpx.AsyncClient() as client:
        try:
            # Search Google Custom Search
            response = await client.get(
                "https://www.googleapis.com/customsearch/v1",
                params={
                    "key": GOOGLE_API_KEY,
                    "cx": GOOGLE_CSE_ID,
                    "q": query,
                    "num": 10,
                    "dateRestrict": "d5844",  # Approximately before 2016 (16 years from 2000)
                    "sort": "date"
                }
            )
            
            data = response.json()
            items = data.get("items", [])
            
            results = []
            for item in items:
                # Extract date from metadata or snippet
                date_str = "2015-01-01"  # Default
                
                # Try to get publish date from page metadata
                if "pagemap" in item and "metatags" in item["pagemap"]:
                    metatags = item["pagemap"]["metatags"][0]
                    for date_field in ["article:published_time", "datePublished", "publishdate"]:
                        if date_field in metatags:
                            date_str = metatags[date_field][:10]
                            break
                
                # Parse the date
                try:
                    from datetime import datetime
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    
                    # Only include pre-2016 content
                    if date_obj.year >= 2016:
                        continue
                        
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("link", ""),
                        "snippet": item.get("snippet", "")[:300],
                        "date": date_obj.strftime("%Y-%m-%d"),
                        "domain": item.get("displayLink", ""),
                        "text_length": len(item.get("snippet", "")) * 10  # Estimate
                    })
                except:
                    # If date parsing fails, skip this result
                    continue
            
            return results
        except Exception as e:
            print(f"Google search error: {e}")
            return []

def parse_duration(duration_str: str) -> int:
    """Parse ISO 8601 duration to seconds"""
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
    if not match:
        return 0
    
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    
    return hours * 3600 + minutes * 60 + seconds

def calculate_quality_score(item: dict, source: str) -> tuple[float, List[str]]:
    """Calculate quality score and generate badges"""
    score = 0.0
    badges = []
    
    if source == "reddit":
        # Engagement ratio (comments per upvote)
        score_val = item.get("score", 1)
        comments = item.get("num_comments", 0)
        
        if score_val > 0:
            engagement_ratio = comments / score_val
            if engagement_ratio > 0.5:
                score += 30
                badges.append(f"🔥 High engagement: {comments} comments on {score_val} upvotes")
            elif engagement_ratio > 0.2:
                score += 20
        
        # Length bonus (longer = more thoughtful)
        text_length = item.get("text_length", 0)
        if text_length > 2000:
            score += 25
            badges.append(f"📝 In-depth: {text_length} characters")
        elif text_length > 1000:
            score += 15
        
        # Age bonus (older = rarer and more valuable)
        year = int(item["date"][:4])
        if year <= 1999:
            score += 25
            badges.append(f"🏛️ From {year} - Ancient web era!")
        elif year <= 2005:
            score += 20
            badges.append(f"📅 From {year} - Early blog era")
        elif year <= 2010:
            score += 15
            badges.append(f"📅 From {year} - Pre-algorithm era")
        elif year <= 2015:
            score += 10
            badges.append(f"📅 From {year} - Before AI slop")
        
        # Hidden gem bonus (low upvotes but quality)
        if score_val < 500 and comments > 20:
            score += 15
            badges.append(f"💎 Hidden gem: Only {score_val} upvotes but great discussion")
    
    elif source == "google":
        # Domain quality (personal blogs and niche sites)
        domain = item.get("domain", "")
        
        # Bonus for personal/niche domains
        personal_indicators = ["blogspot", "wordpress", "typepad", "livejournal", "tumblr"]
        if any(indicator in domain.lower() for indicator in personal_indicators):
            score += 20
            badges.append(f"✍️ Personal blog: {domain}")
        
        # Avoid content farms and big SEO sites
        content_farms = ["ehow", "buzzfeed", "wikihow", "listverse"]
        if any(farm in domain.lower() for farm in content_farms):
            score -= 20
        
        # Length bonus (estimated from snippet)
        text_length = item.get("text_length", 0)
        if text_length > 5000:
            score += 25
            badges.append(f"📝 Long-form content")
        elif text_length > 2000:
            score += 15
        
        # Age bonus (older = rarer and better)
        year = int(item["date"][:4])
        if year <= 1999:
            score += 25
            badges.append(f"🏛️ From {year} - Ancient web era!")
        elif year <= 2005:
            score += 20
            badges.append(f"📅 From {year} - Early blog era")
        elif year <= 2010:
            score += 15
            badges.append(f"📅 From {year} - Pre-algorithm era")
        elif year <= 2015:
            score += 10
            badges.append(f"📅 From {year} - Before AI slop")
        
        # Hidden gem bonus (niche domain)
        niche_tlds = [".org", ".edu", ".net"]
        if any(domain.endswith(tld) for tld in niche_tlds):
            score += 10
            badges.append(f"💎 Niche site: {domain}")
    
    elif source == "youtube":
        view_count = item.get("view_count", 1)
        like_count = item.get("like_count", 0)
        comment_count = item.get("comment_count", 0)
        duration = item.get("duration_seconds", 0)
        
        # Like ratio
        if view_count > 0:
            like_ratio = like_count / view_count
            if like_ratio > 0.05:  # 5% like rate is excellent
                score += 30
                badges.append(f"👍 Highly liked: {like_ratio*100:.1f}% like rate")
        
        # Hidden gem (low views but quality engagement)
        if view_count < 10000:
            score += 25
            badges.append(f"💎 Hidden gem: Only {view_count:,} views")
            
            if comment_count > 50:
                score += 15
                badges.append(f"💬 Active discussion: {comment_count} comments")
        
        # Length bonus (deep dives)
        if duration > 600:  # 10+ minutes
            score += 20
            mins = duration // 60
            badges.append(f"🎥 Deep dive: {mins} minute video")
        elif duration > 300:
            score += 10
        
        # Age bonus (older = rarer and better)
        year = int(item["date"][:4])
        if year <= 1999:
            score += 25
            badges.append(f"🏛️ From {year} - Ancient YouTube!")
        elif year <= 2005:
            score += 20
            badges.append(f"📅 From {year} - Early YouTube era")
        elif year <= 2010:
            score += 15
            badges.append(f"📅 From {year} - Pre-algorithm era")
        elif year <= 2015:
            score += 10
            badges.append(f"📅 From {year} - Before AI slop")
    
    return score, badges

@app.get("/")
async def root():
    return {
        "message": "PreSlop API - Find quality pre-2016 content",
        "status": {
            "google": "enabled" if HAS_GOOGLE else "disabled (add GOOGLE_API_KEY and GOOGLE_CSE_ID)",
            "youtube": "enabled" if HAS_YOUTUBE else "disabled (optional)",
            "reddit": "enabled" if HAS_REDDIT else "disabled (optional)"
        }
    }

@app.post("/search", response_model=ContentResult)
async def search(request: SearchRequest):
    """Search for best quality content"""
    
    # Check if we have any APIs configured
    if not HAS_YOUTUBE and not HAS_REDDIT and not HAS_GOOGLE:
        raise HTTPException(
            status_code=503, 
            detail="No APIs configured. Please add GOOGLE_API_KEY and GOOGLE_CSE_ID to environment variables."
        )
    
    # Get Reddit token only if configured
    reddit_token = None
    if HAS_REDDIT:
        reddit_token = await get_reddit_token()
    
    # Search all available sources
    reddit_results = []
    youtube_results = []
    google_results = []
    
    if request.content_type in ["all", "text"] and HAS_REDDIT and reddit_token:
        reddit_results = await search_reddit(request.query, reddit_token)
    
    if request.content_type in ["all", "text"] and HAS_GOOGLE:
        google_results = await search_google(request.query)
    
    if request.content_type in ["all", "video"] and HAS_YOUTUBE:
        youtube_results = await search_youtube(request.query)
    
    # Score all results
    all_results = []
    
    for item in reddit_results:
        score, badges = calculate_quality_score(item, "reddit")
        all_results.append({
            "title": item["title"],
            "url": item["url"],
            "snippet": item["snippet"],
            "date": item["date"],
            "source": f"r/{item['subreddit']}",
            "quality_score": score,
            "quality_badges": badges,
            "content_type": "text",
            "view_count": None,
            "engagement_count": item["num_comments"]
        })
    
    for item in google_results:
        score, badges = calculate_quality_score(item, "google")
        all_results.append({
            "title": item["title"],
            "url": item["url"],
            "snippet": item["snippet"],
            "date": item["date"],
            "source": item["domain"],
            "quality_score": score,
            "quality_badges": badges,
            "content_type": "text",
            "view_count": None,
            "engagement_count": None
        })
    
    for item in youtube_results:
        score, badges = calculate_quality_score(item, "youtube")
        all_results.append({
            "title": item["title"],
            "url": item["url"],
            "snippet": item["snippet"],
            "date": item["date"],
            "source": item["channel_title"],
            "quality_score": score,
            "quality_badges": badges,
            "content_type": "video",
            "view_count": item["view_count"],
            "engagement_count": item["comment_count"]
        })
    
    # Sort by quality score
    all_results.sort(key=lambda x: x["quality_score"], reverse=True)
    
    if not all_results:
        raise HTTPException(status_code=404, detail="No quality content found for this topic")
    
    # Return the best result
    return ContentResult(**all_results[0])

@app.get("/surprise")
async def surprise_me():
    """Get a random quality topic"""
    topics = [
        "bread fermentation",
        "quantum mechanics interpretation",
        "ancient roman engineering",
        "tcp ip implementation",
        "jazz improvisation theory",
        "mycology fungi",
        "typography history",
        "game theory economics",
        "neuroplasticity brain",
        "woodworking joinery",
        "cryptography mathematics",
        "astronomy deep space",
        "philosophy consciousness",
        "genetics evolution",
        "architecture brutalism"
    ]
    
    import random
    random_topic = random.choice(topics)
    
    return await search(SearchRequest(query=random_topic, content_type="all"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
