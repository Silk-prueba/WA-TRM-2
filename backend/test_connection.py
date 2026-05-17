import sys
import os

# Add the parent directory to sys.path so we can import from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.waha import WahaClient
from backend.core.config import settings

def test_connection():
    client = WahaClient()
    
    # Get the test number from the environment variables
    test_number = settings.test_chat_id
    
    if not test_number:
        print("Error: TEST_CHAT_ID is not set in the environment variables.")
        print("Please configure it in your .env file.")
        return
    
    print(f"Testing connection to WAHA at {client.base_url} with session '{client.session_name}'")
    
    try:
        response = client.send_message(
            chat_id=test_number,
            text="Hello everyone! This is an automated test message from our FastAPI + WAHA prototype! 🚀"
        )
        print("Message sent successfully!")
        print("Response:", response)
    except Exception as e:
        print("Failed to send message.")
        print(f"Error: {e}")

if __name__ == "__main__":
    test_connection()
