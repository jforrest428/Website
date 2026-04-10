#!/usr/bin/env bash
# Forrest Analytics Group — Chatbot Deploy Script
# Usage: ./deploy.sh [railway|render|fly]

set -e

PLATFORM=${1:-railway}
BACKEND_DIR="$(cd "$(dirname "$0")/backend" && pwd)"

echo "=== Forrest Analytics Chatbot Deploy ==="
echo "Platform: $PLATFORM"
echo "Backend:  $BACKEND_DIR"
echo ""

check_env() {
  if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "ERROR: ANTHROPIC_API_KEY is not set."
    echo "Run: export ANTHROPIC_API_KEY=sk-ant-..."
    exit 1
  fi
}

deploy_railway() {
  if ! command -v railway &>/dev/null; then
    echo "Railway CLI not found. Installing..."
    npm install -g @railway/cli
  fi

  check_env

  cd "$BACKEND_DIR"

  echo "Logging in to Railway..."
  railway login

  echo "Initializing Railway project..."
  railway init

  echo "Setting environment variables..."
  railway variables set ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY"

  if [ -n "$ZOHO_EMAIL" ]; then
    railway variables set ZOHO_EMAIL="$ZOHO_EMAIL"
  fi
  if [ -n "$ZOHO_APP_PASSWORD" ]; then
    railway variables set ZOHO_APP_PASSWORD="$ZOHO_APP_PASSWORD"
  fi

  echo "Deploying to Railway..."
  railway up --detach

  echo ""
  echo "=== Deploy complete ==="
  echo "Get your URL: railway open"
  echo "Then update widget.js backendUrl with your Railway URL."
}

deploy_render() {
  echo "Render deployment is best done via the web UI."
  echo ""
  echo "Steps:"
  echo "1. Go to render.com → New → Web Service"
  echo "2. Connect your GitHub repo"
  echo "3. Root Directory: chatbot/backend"
  echo "4. Build Command: pip install -r requirements.txt"
  echo "5. Start Command: uvicorn main:app --host 0.0.0.0 --port \$PORT"
  echo "6. Add env vars: ANTHROPIC_API_KEY, ZOHO_EMAIL, ZOHO_APP_PASSWORD"
  echo "7. Deploy"
}

deploy_fly() {
  if ! command -v fly &>/dev/null; then
    echo "Fly CLI not found. Install from: fly.io/docs/hands-on/install-flyctl/"
    exit 1
  fi

  check_env

  cd "$BACKEND_DIR"

  echo "Launching Fly app..."
  fly launch --name fag-chatbot --region ewr --no-deploy

  echo "Setting secrets..."
  fly secrets set ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY"

  if [ -n "$ZOHO_EMAIL" ]; then
    fly secrets set ZOHO_EMAIL="$ZOHO_EMAIL"
  fi
  if [ -n "$ZOHO_APP_PASSWORD" ]; then
    fly secrets set ZOHO_APP_PASSWORD="$ZOHO_APP_PASSWORD"
  fi

  echo "Deploying..."
  fly deploy

  echo ""
  echo "=== Deploy complete ==="
  fly status
}

case "$PLATFORM" in
  railway) deploy_railway ;;
  render)  deploy_render  ;;
  fly)     deploy_fly     ;;
  *)
    echo "Unknown platform: $PLATFORM"
    echo "Usage: ./deploy.sh [railway|render|fly]"
    exit 1
    ;;
esac
