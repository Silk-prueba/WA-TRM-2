import sys
import os
import datetime

# Add the parent directory to sys.path so we can import from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.waha import WahaClient

def list_chats():
    client = WahaClient()
    
    print(f"Fetching recent chats for session '{client.session_name}'...")
    
    try:
        chats = client.get_chats()
        
        if not chats:
            print("\nNo recent chats found for this session.")
            return
            
        print("\n=== Recent WhatsApp Chats ===")
        print(f"{'Chat Name':<30} | {'Chat ID'}")
        print("-" * 65)
        
        # Display up to 30 most recent chats
        count = 0
        for chat in chats:
            if count >= 30:
                break
                
            chat_id_raw = chat.get('id', {})
            
            # WAHA sometimes returns id as an object with '_serialized'
            if isinstance(chat_id_raw, dict):
                chat_id = chat_id_raw.get('_serialized', '')
            else:
                chat_id = str(chat_id_raw)
                
            name = chat.get('name', '')
            if not name:
                name = "Unknown Contact"
            
            # Skip if it's not a direct message or group (e.g. status)
            if not chat_id or (not chat_id.endswith('@c.us') and not chat_id.endswith('@g.us')):
                continue
                
            # Truncate long names for display
            display_name = name[:27] + "..." if len(name) > 30 else name
            print(f"{display_name:<30} | {chat_id}")
            count += 1
            
        print("-" * 65)
        print("Copy the ID of the person or group you want to message and put it in .env as TEST_CHAT_ID.")
    except Exception as e:
        print("\n[!] Failed to fetch chats.")
        print(f"Error: {e}")

if __name__ == "__main__":
    list_chats()
