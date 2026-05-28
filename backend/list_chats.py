import sys
import os
import datetime

# Add the parent directory to sys.path so we can import from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.waha import WahaClient

def list_chats(debug=False):
    client = WahaClient()

    print(f"Fetching recent chats for session '{client.session_name}'...")

    try:
        chats = client.get_chats()

        if not chats:
            print("\nNo recent chats found for this session.")
            return

        if debug:
            print(f"\n[DEBUG] Total items returned by API: {len(chats)}")
            print("[DEBUG] First 3 raw items:")
            import json
            for item in chats[:3]:
                print(json.dumps(item, indent=2, default=str))
            print()

        print("\n=== Recent WhatsApp Chats ===")
        print(f"{'Type':<6} | {'Chat Name':<30} | {'Chat ID'}")
        print("-" * 75)

        count = 0
        skipped = 0
        for chat in chats:
            if count >= 30:
                break

            chat_id_raw = chat.get('id', {})

            # WAHA sometimes returns id as an object with '_serialized'
            if isinstance(chat_id_raw, dict):
                chat_id = chat_id_raw.get('_serialized', '')
            else:
                chat_id = str(chat_id_raw)

            name = chat.get('name', '') or chat.get('title', '') or ''
            if not name:
                name = "Unknown Contact"

            # Skip status broadcast and empty IDs
            if not chat_id or chat_id == 'status@broadcast':
                skipped += 1
                continue

            # Determine chat type
            if chat_id.endswith('@g.us'):
                chat_type = "group"
            elif chat_id.endswith('@c.us') or chat_id.endswith('@lid'):
                chat_type = "dm"
            elif chat_id.endswith('@newsletter'):
                skipped += 1
                continue
            else:
                if debug:
                    print(f"[DEBUG] Unknown ID format: {chat_id}")
                chat_type = "other"

            display_name = name[:27] + "..." if len(name) > 30 else name
            print(f"{chat_type:<6} | {display_name:<30} | {chat_id}")
            count += 1

        print("-" * 75)
        if skipped:
            print(f"({skipped} non-chat items like status/newsletters were hidden)")
        print("Copy the ID of the person or group you want to message and put it in .env as TEST_CHAT_ID.")
    except Exception as e:
        print("\n[!] Failed to fetch chats.")
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_mode = "--debug" in sys.argv
    list_chats(debug=debug_mode)
