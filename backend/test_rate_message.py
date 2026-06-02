import sys
import os

# Set console output encoding to UTF-8 to correctly display emojis on Windows
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

# Add the parent directory to sys.path so we can import from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.exchange_rate import get_exchange_rate_message

def test_message():
    print("Generating daily exchange rate message...")
    try:
        message = get_exchange_rate_message()
        print("\n=== GENERATED MESSAGE ===")
        print(message)
        print("=========================\n")
    except Exception as e:
        print(f"Error generating message: {e}")

if __name__ == "__main__":
    test_message()
