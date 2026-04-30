import os
import json
import requests
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

API_KEY = os.getenv('API_KEY') 
BACKUP_DIR = "postman_backups"
headers = {"X-Api-Key": API_KEY}

def upload_file(file_path, file_name, ws_id):
    """Uploads a single collection or environment file to a workspace."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = json.load(f)

    if file_name.startswith("ENV_"):
        url = f"https://api.getpostman.com/environments?workspace={ws_id}"
        item_type = "Environment"
    else:
        url = f"https://api.getpostman.com/collections?workspace={ws_id}"
        item_type = "Collection"

    response = requests.post(url, json=content, headers=headers)
    if response.status_code in [200, 201]:
        print(f"    Successfully uploaded {item_type}: {file_name}")
    else:
        print(f"    Failed to upload {file_name}: {response.status_code} - {response.text}")

def process_workspace(ws_name):
    """Handles the creation and population of a single workspace."""
    ws_path = os.path.join(BACKUP_DIR, ws_name)
    if not os.path.isdir(ws_path):
        return

    print(f"Starting Workspace: {ws_name}")
    
    # 1. Create Workspace
    ws_data = {
        "workspace": {
            "name": ws_name.replace("_", " "),
            "type": "personal",
            "description": "Restored via Threaded Script"
        }
    }
    res = requests.post("https://api.getpostman.com/workspaces", json=ws_data, headers=headers)
    
    if res.status_code in [200, 201]:
        new_ws_id = res.json()['workspace']['id']
        files = os.listdir(ws_path)
        
        # 2. Upload files within this workspace in parallel
        # max_workers=3 inside here to avoid overwhelming the API for one workspace
        with ThreadPoolExecutor(max_workers=3) as file_executor:
            for file_name in files:
                file_path = os.path.join(ws_path, file_name)
                file_executor.submit(upload_file, file_path, file_name, new_ws_id)
    else:
        print(f"Error creating workspace {ws_name}: {res.text}")

def restore():
    if not os.path.exists(BACKUP_DIR):
        print(f"Source directory {BACKUP_DIR} not found.")
        return

    workspaces = [d for d in os.listdir(BACKUP_DIR) if os.path.isdir(os.path.join(BACKUP_DIR, d))]
    
    # Process multiple workspaces at once
    # We use a smaller worker count (e.g., 4) to stay within Postman API rate limits
    print(f"Found {len(workspaces)} workspaces. Beginning threaded import...")
    with ThreadPoolExecutor(max_workers=4) as ws_executor:
        ws_executor.map(process_workspace, workspaces)

if __name__ == "__main__":
    restore()