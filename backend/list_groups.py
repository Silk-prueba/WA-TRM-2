import sys
import os

# Add the parent directory to sys.path so we can import from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.waha import WahaClient

def list_groups():
    client = WahaClient()
    
    print(f"Fetching groups for session '{client.session_name}'...")
    
    try:
        groups = client.get_groups()
        
        if not groups:
            print("\nNo groups found for this session.")
            return
            
        print("\n=== Your WhatsApp Groups ===")
        print(f"{'Group Name':<30} | {'Group ID'}")
        print("-" * 65)
        
        for group in groups:
            # Safely get the ID and Name
            group_id_raw = group.get('id', {})
            if isinstance(group_id_raw, dict):
                group_id = group_id_raw.get('_serialized', '')
            else:
                group_id = str(group_id_raw)
                
            name = group.get('name', 'Unnamed Group')
            
            if not group_id or not group_id.endswith('@g.us'):
                continue
                
            display_name = name[:27] + "..." if len(name) > 30 else name
            print(f"{display_name:<30} | {group_id}")
            
        print("-" * 65)
        print("To send a message to a group, copy its ID and put it in .env as TEST_CHAT_ID.")
    except Exception as e:
        print("\n[!] Failed to fetch groups.")
        print(f"Error: {e}")

if __name__ == "__main__":
    list_groups()
