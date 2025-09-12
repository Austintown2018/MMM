import subprocess
import os

# ======== 0. Use current folder as local repo ========
LOCAL_FOLDER = "."  # Current directory

# Verify folder exists
if not os.path.exists(LOCAL_FOLDER):
    print(f"Error: Folder '{LOCAL_FOLDER}' not found.")
    exit(1)

os.chdir(LOCAL_FOLDER)

# ======== 1. Stage all files ========
print("Staging all files...")
subprocess.run(["git", "add", "."])

# ======== 2. Commit changes ========
commit_message = "Add MMM skeleton with starter modules"
print(f"Committing with message: '{commit_message}'")
subprocess.run(["git", "commit", "-m", commit_message])

# ======== 3. Push to GitHub ========
print("Pushing to GitHub...")
result = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)

if result.returncode == 0:
    print("Push successful! Your online repo is now updated.")
else:
    print("Push failed. Output:")
    print(result.stdout)
    print(result.stderr)
