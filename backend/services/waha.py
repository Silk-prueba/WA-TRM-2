import requests
from backend.core.config import settings

class WahaClient:
    def __init__(self):
        self.base_url = settings.waha_api_url
        self.session_name = settings.waha_session_name

    def send_message(self, chat_id: str, text: str):
        """
        Sends a text message using WAHA API.
        :param chat_id: The WhatsApp number with country code and @c.us suffix (e.g., '1234567890@c.us')
        :param text: The text message to send
        """
        url = f"{self.base_url}/api/sendText"
        payload = {
            "session": self.session_name,
            "chatId": chat_id,
            "text": text
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Api-Key": "123"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_groups(self):
        """
        Retrieves a list of all groups the connected number is a part of.
        """
        url = f"{self.base_url}/api/{self.session_name}/groups"
        headers = {
            "Accept": "application/json",
            "X-Api-Key": "123"
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_chats(self):
        """
        Retrieves a list of all recent chats.
        """
        url = f"{self.base_url}/api/{self.session_name}/chats"
        headers = {
            "Accept": "application/json",
            "X-Api-Key": "123"
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
