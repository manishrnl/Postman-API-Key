import requests
import os
import subprocess
from dotenv import load_dotenv
import json
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- CONFIGURATION ---
load_dotenv() # Add this line BEFORE accessing variables

API_KEY = os.getenv('API_KEY')
REPO_URL = os.getenv('REPO_URL')
BACKUP_DIR = "postman_backups"

# Debugging: Check if keys are loaded
if not API_KEY or not REPO_URL:
    print("Error: API_KEY or REPO_URL not found in .env file!")
    exit()
session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))
session.headers.update({"X-Api-Key": API_KEY})

def run_command(command):
    subprocess.run(command, shell=True)

def sync():
    try:
        # 1. Get all Workspaces first
        print("Step 1: Fetching Workspaces...")
        ws_response = session.get("https://api.getpostman.com/workspaces", timeout=15)
        workspaces = ws_response.json().get('workspaces', [])

        for ws in workspaces:
            ws_id = ws['id']
            ws_name = ws['name'].replace(" ", "_").replace("/", "-")
            ws_path = os.path.join(BACKUP_DIR, ws_name)
            
            # Create the Workspace folder
            os.makedirs(ws_path, exist_ok=True)
            print(f"\nCreated folder for Workspace: {ws_name}")

            # 2. Get specific details for this workspace (Collections & Envs)
            ws_detail = session.get(f"https://api.getpostman.com/workspaces/{ws_id}", timeout=15).json().get('workspace', {})
            
            # Sync Collections
            collections = ws_detail.get('collections', [])
            for col in collections:
                col_id = col['id']
                col_name = col['name'].replace(" ", "_").replace("/", "-")
                print(f"  --> Syncing Collection: {col_name}")
                
                c_data = session.get(f"https://api.getpostman.com/collections/{col_id}", timeout=15).json()
                with open(os.path.join(ws_path, f"{col_name}.json"), "w", encoding="utf-8") as f:
                    json.dump(c_data, f, indent=4)

            # Sync Environments
            environments = ws_detail.get('environments', [])
            for env in environments:
                env_id = env['id']
                env_name = env['name'].replace(" ", "_").replace("/", "-")
                print(f"  --> Syncing Environment: {env_name}")
                
                e_data = session.get(f"https://api.getpostman.com/environments/{env_id}", timeout=15).json()
                with open(os.path.join(ws_path, f"ENV_{env_name}.json"), "w", encoding="utf-8") as f:
                    json.dump(e_data, f, indent=4)

        # 3. Pushing to GitHub
        # Formatting to: Month Day, Year Hour:Minute
        # %b = Abbreviated month, %d = day, %y = 2-digit year, %H:%M = 24hr time
        # 3. Pushing to GitHub
        # %b = Month (May), %d = Day (01), %y = Year (26), %H:%M = Time (18:30)
        timestamp = datetime.now().strftime("%b %d, %y %H:%M") 
        print(f"\nStep 2: Pushing to GitHub with timestamp {timestamp}...")
        
        if not os.path.exists(".git"):
            run_command("git init")
            run_command(f"git remote add origin {REPO_URL}")
        
        run_command("git add .")
        # Use double quotes for the commit message to handle the timestamp correctly in CMD
        run_command(f'git commit -m "Auto-Sync: {timestamp}"')
        run_command("git branch -m main")
        run_command("git push origin main --force")
        
        print("\nSuccess! All collections are now organized by workspace.")

    except Exception as e:
        print(f"Error during sync: {e}")

if __name__ == "__main__":
    sync()