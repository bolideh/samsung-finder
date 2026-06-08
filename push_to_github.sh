#!/bin/bash
# ─────────────────────────────────────────────
#  Samsung Finder — GitHub Push Script
#  Usage: bash push_to_github.sh YOUR_GITHUB_USERNAME
# ─────────────────────────────────────────────

USERNAME=$1

if [ -z "$USERNAME" ]; then
  echo "❌  Usage: bash push_to_github.sh YOUR_GITHUB_USERNAME"
  exit 1
fi

REPO="samsung-finder"

echo ""
echo "🚀  Setting up Git and pushing to GitHub..."
echo ""

# Init git
git init
git add .
git commit -m "🚀 Initial commit: Samsung Device Finder"

# Create repo on GitHub using CLI (if installed)
if command -v gh &> /dev/null; then
  echo "✅  GitHub CLI detected — creating repo automatically..."
  gh repo create "$REPO" --public --description "Scan your local network to find Samsung devices" --push --source=.
  echo ""
  echo "✅  Done! Your repo is live at: https://github.com/$USERNAME/$REPO"
else
  echo "⚠️   GitHub CLI not found. Creating repo manually..."
  echo ""
  echo "1️⃣   Go to: https://github.com/new"
  echo "2️⃣   Repository name: $REPO"
  echo "3️⃣   Set to Public, do NOT initialize with README"
  echo "4️⃣   Click 'Create repository'"
  echo ""
  echo "Then run:"
  echo ""
  echo "   git remote add origin https://github.com/$USERNAME/$REPO.git"
  echo "   git branch -M main"
  echo "   git push -u origin main"
  echo ""
fi
