# PreSlop - Rediscover the Old Internet

Find high-quality, underrated content from before 2016 - when the internet was still made by humans, for humans.

## What It Does

PreSlop searches Reddit, YouTube, and blogs for pre-2016 content and uses a smart algorithm to find:
- Hidden gems (low views but high engagement)
- Deep, thoughtful content (long posts/videos)
- Content from the "golden age" (2010-2015)
- Genuine human discussions (no AI slop)

**No AI APIs needed** - uses pure algorithmic scoring based on engagement ratios, content length, date, and view counts.

## Setup Instructions

### Step 1: Get API Keys

#### Reddit API (Required)
1. Go to https://www.reddit.com/prefs/apps
2. Click "create another app..." at the bottom
3. Fill in:
   - **Name**: PreSlop
   - **App type**: Select "script"
   - **Description**: Personal content discovery tool
   - **About URL**: (leave blank)
   - **Redirect URI**: http://localhost:8000
4. Click "create app"
5. Copy the **client ID** (under your app name) and **client secret**

#### YouTube API (Required)
1. Go to https://console.cloud.google.com/
2. Create a new project or select existing one
3. Enable "YouTube Data API v3":
   - Go to "APIs & Services" > "Library"
   - Search for "YouTube Data API v3"
   - Click "Enable"
4. Create credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - Copy the API key
5. (Optional) Restrict the key to YouTube Data API v3 for security

### Step 2: Install Backend

```bash
# Navigate to backend folder
cd preslop-backend

# Install Python dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use any text editor
```

Your `.env` file should look like:
```
REDDIT_CLIENT_ID=your_actual_client_id
REDDIT_CLIENT_SECRET=your_actual_client_secret
YOUTUBE_API_KEY=your_actual_youtube_key
```

### Step 3: Run Backend

```bash
# Start the backend server
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Keep this terminal window open!

### Step 4: Run Frontend

Open a new terminal:

```bash
# Navigate to frontend folder
cd preslop-frontend

# Serve the HTML file (multiple options)

# Option 1: Python HTTP server
python -m http.server 3000

# Option 2: Node.js http-server (if you have node)
npx http-server -p 3000

# Option 3: Just open the HTML file directly
# Double-click index.html in your file manager
```

### Step 5: Use the App

Open your browser and go to:
```
http://localhost:3000
```

**Try it out:**
1. Search for a topic like "quantum mechanics" or "bread making"
2. Click "Surprise Me" for a random quality topic
3. View the best pre-2016 content!

## How the Quality Algorithm Works

### For Reddit Posts:
- **Engagement Ratio** (30 points): High comments relative to upvotes
- **Length Bonus** (25 points): Posts over 2000 characters
- **Age Bonus** (20 points): Older posts (2010-2013 era)
- **Hidden Gem** (15 points): Low upvotes but great discussion

### For YouTube Videos:
- **Like Ratio** (30 points): High percentage of likes
- **Hidden Gem** (25 points): Under 10k views
- **Length Bonus** (20 points): Videos over 10 minutes
- **Age Bonus** (20 points): Older videos (2010-2013 era)
- **Active Discussion** (15 points): Many comments relative to views

## Troubleshooting

### Backend won't start
```bash
# Make sure you're in the right directory
cd preslop-backend

# Check if Python dependencies are installed
pip list | grep fastapi

# Reinstall if needed
pip install -r requirements.txt
```

### "No quality content found"
- The APIs might not have found relevant pre-2016 content
- Try different search terms
- Make sure your API keys are correct in `.env`

### API rate limits
- Reddit: 60 requests per minute (should be plenty)
- YouTube: 10,000 quota units per day (≈100-200 searches)

### CORS errors in browser
Make sure:
1. Backend is running on port 8000
2. Frontend is accessing `http://localhost:8000` (check the API_URL in index.html)
3. Try accessing frontend via `http://localhost:3000` not `file://`

## Deployment - Make It Public! 🌐

Want to access PreSlop from anywhere and share it with others?

### 📖 Full Deployment Guide

See **DEPLOYMENT_GUIDE.md** for complete step-by-step instructions to deploy on:
- **Backend**: Render.com (free tier)
- **Frontend**: Vercel (free tier)
- **Cost**: $0/month forever

### ⚡ Quick Deploy Steps

1. Push code to GitHub
2. Deploy backend on Render (10 min)
3. Deploy frontend on Vercel (5 min)
4. Share your URL with the world!

**Total time**: ~20 minutes to go from local to live website.

See **DEPLOYMENT_CHECKLIST.md** for a quick checklist to follow along.

## Customization

### Add More Topics to "Surprise Me"
Edit `main.py` line 230 - add topics to the list

### Change Quality Scoring Weights
Edit the `calculate_quality_score()` function in `main.py`

### Modify UI Colors/Fonts
Edit the CSS variables in `index.html` (lines 9-18)

### Add More Content Sources
The backend is designed to be extensible - you can add:
- Hacker News archives
- Stack Overflow questions
- Blog aggregators
- Forum posts

## API Endpoints

### POST /search
Search for content by topic
```json
{
  "query": "quantum mechanics",
  "content_type": "all"  // or "text" or "video"
}
```

### GET /surprise
Get random quality content

## Tech Stack

- **Backend**: Python FastAPI
- **Frontend**: Vanilla HTML/CSS/JS (no framework needed!)
- **APIs**: Reddit OAuth, YouTube Data API v3
- **No AI Runtime Costs**: Pure algorithmic scoring

## Future Enhancements

Ideas for v2:
- [ ] Save favorite finds
- [ ] User accounts
- [ ] Topic recommendations
- [ ] Browser extension
- [ ] Weekly digest email
- [ ] Community submissions
- [ ] Pre-computed quality database (faster searches)

## License

Built for personal use. Feel free to modify and extend!

---

**Questions?** The code is thoroughly commented - check `main.py` for the backend logic and `index.html` for the frontend.

Enjoy rediscovering the old internet! 🌐✨
