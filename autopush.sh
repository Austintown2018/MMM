#!/bin/bash
# 🚀 Pro-Max Auto Push Script with Retry + Summary

MAX_RETRIES=3
RETRY_DELAY=5
SUCCESS=false

echo "🚀 Staging all changes..."
git add -A

# Create commit only if there are changes
if ! git diff --cached --quiet; then
    COMMIT_MSG="Auto-push on $(date '+%Y-%m-%d %H:%M:%S')"
    echo "📝 Committing with message: $COMMIT_MSG"
    git commit -m "$COMMIT_MSG"
else
    echo "⚠️ Nothing to commit."
fi

# Retry loop for git push
for ((i=1; i<=MAX_RETRIES; i++)); do
    echo "⬆️ Attempt $i of $MAX_RETRIES: Pushing to GitHub..."
    if git push origin main; then
        SUCCESS=true
        break
    else
        echo "❌ Push failed. Retrying in $RETRY_DELAY seconds..."
        sleep $RETRY_DELAY
    fi
done

if [ "$SUCCESS" = true ]; then
    echo "✅ Auto-push completed successfully!"
    git status -s
else
    echo "🚨 Auto-push failed after $MAX_RETRIES attempts."
fi
