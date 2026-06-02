import httpx
from backend.core.config import settings
 
class WahaClient:
    def __init__(self):
        self.base_url = settings.waha_api_url
        self.session_name = settings.waha_session_name
        self._headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Api-Key": settings.waha_api_key,
        }
 
    async def send_message(self, chat_id: str, text: str):
        """
        Sends a text message using WAHA API.
        chat_id examples:
          Individual: '573001234567@c.us'
          Group:      '120363xxxxxxx@g.us'
        """
        url = f"{self.base_url}/api/sendText"
        payload = {
            "session": self.session_name,
            "chatId": chat_id,
            "text": text,
        }
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(url, json=payload, headers=self._headers)
            response.raise_for_status()
            return response.json()
 
    async def get_groups(self):
        url = f"{self.base_url}/api/{self.session_name}/groups"
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(url, headers=self._headers)
            response.raise_for_status()
            return response.json()
 
    async def get_chats(self):
        url = f"{self.base_url}/api/{self.session_name}/chats"
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(url, headers=self._headers)
            response.raise_for_status()
            return response.json()
