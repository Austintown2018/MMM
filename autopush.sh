#!/data/data/com.termux/files/usr/bin/bash
# 🚀 Pro-Max Auto Push Script with Retry + Summary

MAX_RETRIES=3
RETRY_DELAY=5
SUCCESS=false

# Navigate to your repository
cd ~/MMM/MMM || exit

for i in $(seq 1 $MAX_RETRIES); do
    echo "🚀 Staging all changes..."
    git add -A

    # Commit only if there are changes
    if ! git diff --cached --quiet; then
        echo "📝 Committing with message: Auto-push on $(date '+%Y-%m-%d %H:%M:%S')"
        git commit -m "Auto-push on $(date '+%Y-%m-%d %H:%M:%S')"
    else
        echo "⚠️ Nothing to commit."
    fi

    echo "⬆️ Attempt $i of $MAX_RETRIES: Pushing to GitHub..."
    if git push origin main; then
        echo "✅ Auto-push completed successfully!"
        SUCCESS=true
        break
    else
        echo "❌ Push failed. Retrying in $RETRY_DELAY seconds..."
        sleep $RETRY_DELAY
    fi
done

if [ "$SUCCESS" = false ]; then
    echo "❌ All push attempts failed. Check your network or credentials."
fi
