import sys
import os

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.exchange_rate import get_exchange_rate_message
from backend.services.waha import WahaClient
from backend.core.config import settings


def test_send_rate():
    if not settings.test_chat_id:
        print("Error: TEST_CHAT_ID is not set in the environment variables.")
        print("Please configure it in your .env file.")
        return

    print("Generating daily exchange rate message...")
    try:
        message = get_exchange_rate_message()
    except Exception as e:
        print(f"Error generating message: {e}")
        return

    print("\n=== MESSAGE TO SEND ===")
    print(message)
    print("======================\n")

    client = WahaClient()
    print(f"Sending to {settings.test_chat_id} via WAHA at {client.base_url}...")
    try:
        response = client.send_message(chat_id=settings.test_chat_id, text=message)
        print("Message sent successfully!")
        print("Response:", response)
    except Exception as e:
        print(f"Failed to send message: {e}")


if __name__ == "__main__":
    test_send_rate()
