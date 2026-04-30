import requests
import os
import subprocess
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- CONFIGURATION ---
API_KEY = "PMAK-69f39960ece114000194e985-6089819acaee87b0bd687a994eb2ad0ef1"
REPO_URL = "https://github.com/manishrnl/Postman-API-Key.git"
BACKUP_DIR = "postman_backups"

# Setup a robust session with retries
session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))
session.headers.update({"X-Api-Key": API_KEY})

def run_command(command):
    subprocess.run(command, shell=True)

def sync():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    try:
        print("Step 1: Fetching all collections...")
        # Get all collections directly (Faster than nesting by workspace)
        response = session.get("https://api.getpostman.com/collections", timeout=15)
        collections = response.json().get('collections', [])

        for col in collections:
            uid = col['uid']
            name = col['name'].replace(" ", "_").replace("/", "-")
            print(f"Downloading: {name}")

            try:
                # Fetch full collection data
                col_response = session.get(f"https://api.getpostman.com/collections/{uid}", timeout=15)
                if col_response.status_code == 200:
                    with open(f"{BACKUP_DIR}/{name}.json", "w", encoding="utf-8") as f:
                        json.dump(col_response.json(), f, indent=4)
            except Exception as e:
                print(f"Failed to download {name}: {e}")

        print("\nStep 2: Pushing to GitHub...")
        if not os.path.exists(".git"):
            run_command("git init")
            run_command(f"git remote add origin {REPO_URL}")
        
        run_command("git add .")
        run_command('git commit -m "Auto-sync"')
        run_command("git branch -m main")
        run_command("git push origin main --force")
        print("\nSuccess!")

    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Connection timed out. Please check your internet or VPN.")

if __name__ == "__main__":
    sync()