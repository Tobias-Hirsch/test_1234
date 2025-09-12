import requests
import json
import os

# --- CONFIGURATION ---
# The script will try to get the JWT from an environment variable first.
# If not found, you MUST replace the placeholder value below.
JWT_TOKEN = os.environ.get("ROSTI_JWT_TOKEN", "YOUR_JWT_TOKEN_HERE") 
HOST = "http://localhost:8000"
# This conversation ID is taken from the latest logs you provided.
CONVERSATION_ID = "6885a3ec7ca1780c8704ee2f"

# --- SCRIPT ---

def run_stream_test():
    """
    Connects to the chat streaming endpoint and prints the raw SSE events.
    This bypasses Nginx and the frontend to test the backend stream directly.
    """
    url = f"{HOST}/api/chat/conversations/{CONVERSATION_ID}/messages/"
    
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
    }

    # This payload mimics a typical request from the frontend.
    payload = {
        "content": "Tell me about Bush",
        "attachments": [],
        "search_ai_active": True,
        "search_rosti_active": True,
        "search_online_active": False,
        "show_think_process": True
    }

    print(f"--- Connecting to: {url} ---")
    
    try:
        with requests.post(url, headers=headers, json=payload, stream=True, timeout=180) as response:
            response.raise_for_status()
            
            print(f"--- Successfully connected (Status: {response.status_code}). Waiting for stream data... ---")
            
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    print(decoded_line)
            
            print("\n--- Stream finished. ---")

    except requests.exceptions.RequestException as e:
        print(f"\n--- !!! An HTTP error occurred: {e} !!! ---")
    except Exception as e:
        print(f"\n--- !!! A general error occurred: {e} !!! ---")

if __name__ == "__main__":
    if "YOUR_JWT_TOKEN_HERE" in JWT_TOKEN:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!! ERROR: JWT Token not found.                                            !!!")
        print("!!! Please get a valid token from your browser's developer tools           !!!")
        print("!!! (Network tab, look for a request to /api/...). Then run this command:  !!!")
        print("!!!                                                                        !!!")
        print("!!!   ROSTI_JWT_TOKEN='your_token_here' python diagnose_stream.py          !!!")
        print("!!!                                                                        !!!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    else:
        run_stream_test()