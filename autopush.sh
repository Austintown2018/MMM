#!/data/data/com.termux/files/usr/bin/bash
# === Super Pro-Max Auto Push Script ===
# Location: ~/.../MMM/MMM/autopush.sh

# Go to repo directory
cd "$(dirname "$0")" || exit

echo "🚀 Staging all changes..."
git add -A

# Commit with timestamp so it’s always unique
COMMIT_MSG="Auto-push on $(date '+%Y-%m-%d %H:%M:%S')"
echo "📝 Committing with message: $COMMIT_MSG"
git commit -m "$COMMIT_MSG" || echo "⚠️ Nothing to commit."

echo "⬆️ Pushing to GitHub..."
git push origin main

echo "✅ Auto-push completed."
