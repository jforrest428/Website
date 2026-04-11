# Forrest Analytics Group — AI Chat Widget

A consultative AI chatbot for `forrestanalyticsgroup.com/small-business/` that greets visitors, answers product questions, qualifies leads, and books discovery calls — powered by Claude.

---

## Directory Structure

```
chatbot/
├── backend/
│   ├── main.py              # FastAPI app (all logic here)
│   ├── system_prompt.py     # Claude system prompt (edit this to tune personality)
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── Procfile             # For Railway / Render
│   ├── railway.toml         # Railway-specific config
│   ├── .env.example         # Copy to .env and fill in
│   └── conversations/       # Auto-created; stores JSON conversation logs
└── widget/
    └── widget.js            # Self-contained embeddable widget
```

---

## Step 1: Local Setup & Testing

### Prerequisites
- Python 3.11+
- An Anthropic API key (console.anthropic.com)

### Install & run

```bash
cd chatbot/backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy and fill in env vars
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY (and optionally ZOHO_EMAIL + ZOHO_APP_PASSWORD)

# Start the server
uvicorn main:app --reload --port 8000
```

The API will be live at `http://localhost:8000`.

### Test with curl

```bash
# Health check
curl http://localhost:8000/health

# Send a message
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hi, I run a plumbing company and miss a lot of calls"}'

# Stats
curl http://localhost:8000/stats
```

### Test the widget locally
Open `chatbot/widget/widget.js`, find this line near the top:
```js
backendUrl: "https://your-api-url.railway.app",
```
Change it to:
```js
backendUrl: "http://localhost:8000",
```
Then open any local HTML file and paste the widget script tag in.

---

## Step 2: Deploy the Backend

### Option A: Railway (recommended — easiest)

1. Push the repo to GitHub (if not already there)
2. Go to railway.app → New Project → Deploy from GitHub
3. Select your repo, set the **Root Directory** to `chatbot/backend`
4. Add environment variables in the Railway dashboard:
   - `ANTHROPIC_API_KEY` = your key
   - `ZOHO_EMAIL` = josh@forrestanalytics.com
   - `ZOHO_APP_PASSWORD` = your Zoho app password
5. Railway auto-detects the Dockerfile and deploys. You'll get a URL like:
   `https://forrest-analytics-chatbot.up.railway.app`

Or use the deploy script (requires Railway CLI):
```bash
cd chatbot
chmod +x deploy.sh
./deploy.sh railway
```

### Option B: Render

1. Go to render.com → New → Web Service
2. Connect your GitHub repo
3. Root directory: `chatbot/backend`
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add the same 3 environment variables
7. Deploy → get your URL like `https://fag-chatbot.onrender.com`

### Option C: Fly.io

```bash
cd chatbot/backend
fly launch --name fag-chatbot
fly secrets set ANTHROPIC_API_KEY=sk-ant-...
fly secrets set ZOHO_EMAIL=josh@forrestanalytics.com
fly secrets set ZOHO_APP_PASSWORD=your-password
fly deploy
```

---

## Step 3: Update the Widget URL

Once deployed, open `chatbot/widget/widget.js` and update:

```js
backendUrl: "https://YOUR-ACTUAL-URL.railway.app",
```

---

## Step 4: Embed in Squarespace

Paste this into **Settings → Advanced → Code Injection → Footer**:

```html
<script>
// Optional: override config before loading
window.FAG_CHAT_CONFIG = {
  backendUrl: "https://YOUR-DEPLOYED-URL.railway.app"
};
</script>
<script src="https://cdn.jsdelivr.net/gh/YOUR-GITHUB-USERNAME/YOUR-REPO/chatbot/widget/widget.js"></script>
```

**OR** (simpler — paste the entire widget.js inline):

1. Open `chatbot/widget/widget.js`
2. Copy the entire file contents
3. Wrap in `<script>...</script>` tags
4. Update `backendUrl` inside the pasted code
5. Paste into Squarespace Code Injection → Footer → Save

The inline approach means no external CDN dependency — recommended.

---

## Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Your Claude API key from console.anthropic.com |
| `ZOHO_EMAIL` | No* | Your Zoho email address for sending lead notifications |
| `ZOHO_APP_PASSWORD` | No* | Zoho App Password (not your account password) |
| `PORT` | No | Injected automatically by Railway/Render |

*If Zoho vars are missing, lead emails are skipped but conversations are still logged to disk.

### Getting a Zoho App Password
1. Log in to Zoho Mail → Settings → Security
2. Under "App Passwords," create a new password for "Chatbot"
3. Use that password (not your login password) as `ZOHO_APP_PASSWORD`

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/stats` | Today's conversation stats |
| POST | `/chat` | Send a message, get a reply |

### POST /chat Request
```json
{
  "conversation_id": "optional-existing-id",
  "message": "Hi, I run a plumbing company"
}
```

### POST /chat Response
```json
{
  "conversation_id": "uuid",
  "reply": "Hey! Plumbing — perfect...",
  "message_count": 1,
  "lead_captured": false,
  "booking_requested": false
}
```

---

## Tuning the Chatbot

The personality, product knowledge, objection handling, and tone all live in:
**`chatbot/backend/system_prompt.py`**

Edit `SYSTEM_PROMPT` to:
- Add new products or update pricing
- Adjust tone
- Add new objection-handling scripts
- Add new verticals

No code changes needed in `main.py` for prompt tuning.

---

## Conversation Logs

Every conversation is saved to `chatbot/backend/conversations/` as a JSON file:
```json
{
  "conversation_id": "uuid",
  "timestamp": "2026-04-10T...",
  "meta": {
    "lead_captured": true,
    "booking_requested": true,
    "recommended_products": "..."
  },
  "messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

On Railway/Render, these are ephemeral (reset on redeploy). For persistence, add a volume mount or pipe to a database.

---

## Rate Limits

- Max 30 messages per conversation
- Max 100 new conversations per hour (across all visitors)
- Jailbreak detection on every user message

---

## Customization Quick Reference

In `widget.js`, the `defaultConfig` object controls:
- `backendUrl` — your deployed API URL
- `accentColor` — chat bubble + send button color (`#2563EB`)
- `headerName` — name shown in chat header
- `headerSubtitle` — subtitle in chat header
- `greeting` — first message shown when chat opens
- `quickReplies` — the 3 clickable starter buttons
