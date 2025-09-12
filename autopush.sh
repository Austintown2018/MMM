#!/data/data/com.termux/files/usr/bin/bash

# Navigate to your repository
cd ~/MMM/MMM || exit

# Stage all changes
git add .

# Commit with timestamp
git commit -m "Auto-push on $(date '+%Y-%m-%d %H:%M:%S')"

# Push to GitHub
git push origin main
