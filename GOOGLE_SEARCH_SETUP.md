# 📝 Google Custom Search Setup - Find Pre-2016 Blogs!

Complete guide to set up Google Custom Search to find amazing old blogs and articles from across the entire web.

## What You'll Find

With Google Custom Search, you can discover pre-2016 content on **ANY topic**:
- ✅ Personal blogs from 1990s-2015
- ✅ Niche websites and articles  
- ✅ Old forums and discussions
- ✅ Hidden gems from the ancient web
- ✅ Content from 1995, 2005, 2010, any year pre-2016!

---

## Step 1: Get Google API Key (5 minutes)

### A. Go to Google Cloud Console
1. Visit: **https://console.cloud.google.com/**
2. Sign in with your Google account

### B. Create Project (if you don't have one)
1. Click **project dropdown** at top (says "Select a project")
2. Click **"NEW PROJECT"**
3. Name: `PreSlop`
4. Click **"CREATE"**
5. Wait 10 seconds

### C. Enable Custom Search API
1. Click **☰ Menu** → **"APIs & Services"** → **"Library"**
2. Search for: `Custom Search API`
3. Click on **"Custom Search API"**
4. Click **"ENABLE"** button
5. Wait a few seconds

### D. Create API Key
1. Click **☰ Menu** → **"APIs & Services"** → **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"**
3. Select **"API key"**
4. **COPY THE KEY IMMEDIATELY!**

Example key:
```
AIzaSyD9xK3mN7pQ2rS4tU6vW8xY0zA1bC2dE3f
```

### E. Restrict the Key (Optional but Recommended)
1. Click **"Restrict Key"**
2. Under "API restrictions":
   - Select **"Restrict key"**
   - Check **"Custom Search API"**
3. Click **"Save"**

✅ **You now have your GOOGLE_API_KEY!**

---

## Step 2: Create Custom Search Engine (5 minutes)

This is the special part that makes it work!

### A. Go to Programmable Search Engine
1. Visit: **https://programmablesearchengine.google.com/controlpanel/create**
2. Sign in with same Google account

### B. Create Search Engine

Fill in the form:

**Search engine name:**
```
PreSlop Web Search
```

**What to search:**
- Select: **"Search the entire web"**
- This lets you search everything, not just specific sites!

**Search settings:**
- ✅ Check "Search the entire web"
- Leave other options as default

Click **"CREATE"** button

### C. Get Your Search Engine ID

After creating, you'll see a confirmation page.

1. Click **"Customize"** button
2. In the left sidebar, find **"Basic"** tab
3. Look for **"Search engine ID"**
4. Copy this ID (looks like: `a1b2c3d4e5f6g7h8i`)

Example:
```
017576662512468239146:omuauf_lfve
```

✅ **You now have your GOOGLE_CSE_ID!**

---

## Step 3: Configure Search Engine

### A. Enable Image Search (Optional)
1. In "Basics" tab
2. Toggle **"Image search"** to ON

### B. Adjust Settings
1. Click **"Look and feel"** in sidebar
2. Choose your preferences (doesn't matter for API)

### C. That's It!
Your search engine is ready to use!

---

## Step 4: Add to Your .env File

In `preslop-backend/.env`:

```env
# Google Custom Search for blogs/articles
GOOGLE_API_KEY=AIzaSyD9xK3mN7pQ2rS4tU6vW8xY0zA1bC2dE3f
GOOGLE_CSE_ID=017576662512468239146:omuauf_lfve

# YouTube is optional now!
# YOUTUBE_API_KEY=your_key_here

# Reddit is optional!
# REDDIT_CLIENT_ID=your_id
# REDDIT_CLIENT_SECRET=your_secret
```

Replace with your actual keys!

---

## Step 5: Test It!

### Start Backend
```bash
cd preslop-backend
python main.py
```

### Check Status
Visit: http://localhost:8000

Should see:
```json
{
  "message": "PreSlop API - Find quality pre-2016 content",
  "status": {
    "google": "enabled",
    "youtube": "disabled (optional)",
    "reddit": "disabled (optional)"
  }
}
```

✅ Google is enabled!

### Start Frontend
```bash
cd preslop-frontend
python -m http.server 3000
```

### Search for Something!
Go to: http://localhost:3000

Try searching:
- "sourdough bread recipe"
- "javascript closures explained"
- "ancient roman architecture"
- "jazz improvisation techniques"

🎉 **You're finding pre-2016 blogs from across the web!**

---

## What You'll Discover

### Content Types:
- 📝 Personal blogs (blogspot, wordpress, etc.)
- 🌐 Niche websites
- 📰 Old articles
- 💬 Forum posts
- 🎓 Educational content
- 🏛️ Ancient web pages from 1990s!

### Quality Scoring:
The algorithm prioritizes:
1. **Age** - 1990s content gets highest score!
2. **Personal blogs** - Over corporate sites
3. **Length** - Long-form, thoughtful content
4. **Domain quality** - .org, .edu, personal domains
5. **Avoids SEO spam** - Filters out content farms

---

## API Limits & Costs

### Google Custom Search Free Tier:
- **100 searches per day** - FREE
- Resets daily
- Perfect for personal use!

### If You Need More:
- Paid tier: $5 per 1,000 queries
- Or create multiple Custom Search Engines with different Google accounts
- Each account gets 100 free searches/day

---

## Troubleshooting

### "Google API key not valid"
- Your API key is wrong
- Make sure Custom Search API is enabled
- Check for typos

### "Search engine ID not valid"
- CSE_ID is wrong
- Go back to programmablesearchengine.google.com
- Copy the ID from "Basics" tab

### "No results found"
- Try broader search terms
- Pre-2016 content might not exist for very niche topics
- Google's date filtering isn't perfect

### "Quota exceeded"
- You've used 100 searches today
- Wait until tomorrow (resets at midnight)
- Or create another Custom Search Engine

### Getting modern results (post-2016)
- Date filtering isn't perfect in Google
- Our algorithm still scores older content higher
- Quality badges show the actual date

---

## Advanced: Search Specific Domains

Want to search only certain types of sites?

### A. Edit Your Search Engine
1. Go to: https://programmablesearchengine.google.com/controlpanel/all
2. Click your search engine
3. Click **"Setup"** → **"Basics"**

### B. Add Sites to Search
Under "Sites to search", add domains like:
```
blogspot.com/*
wordpress.com/*
typepad.com/*
livejournal.com/*
```

This will only search blog platforms (more focused results!)

### C. Or Keep "Search entire web"
For maximum coverage, keep searching everything!

---

## What's Next?

### Current Setup:
✅ Google Custom Search (blogs/articles)
❌ YouTube (videos) - Optional
❌ Reddit (discussions) - Optional

### Want to Add Videos?
Follow **YOUTUBE_ONLY_SETUP.md** to add YouTube

### Want All Three?
Get all API keys and add them all to `.env`:
- Google finds blogs
- YouTube finds videos
- Reddit finds discussions
- Algorithm picks THE BEST result!

---

## Example Searches to Try

**Tech:**
- "javascript prototypes explained"
- "python decorators tutorial"
- "unix philosophy"

**Hobbies:**
- "bread fermentation science"
- "darkroom photography techniques"
- "jazz chord voicings"

**Academic:**
- "quantum entanglement explained"
- "roman engineering techniques"
- "renaissance art techniques"

**Random:**
- "coffee roasting at home"
- "knife sharpening guide"
- "typography history"

---

## Cost Summary

**Google Custom Search**: FREE
- 100 searches/day
- No credit card needed
- Perfect for personal use

**Total cost**: **$0/month** ✅

---

## Deployment

To make it public (accessible from anywhere):

1. Follow **DEPLOYMENT_GUIDE.md**
2. Add these environment variables on Render:
   - `GOOGLE_API_KEY`
   - `GOOGLE_CSE_ID`
3. Deploy!

Your friends can now discover pre-2016 gems too! 🌐

---

**You're all set!** 

Now you can search for ANY topic and find amazing pre-2016 blogs, articles, and hidden web gems from 1995-2015! 🎉

The algorithm will surface:
- 🏛️ Ancient 1990s web pages
- 📝 Early 2000s blog posts  
- 💎 Hidden gems from 2010-2015
- ✍️ Personal sites over corporate SEO

**Enjoy rediscovering the old internet!** 🌐✨
