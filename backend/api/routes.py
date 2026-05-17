from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/webhook")
async def receive_webhook(request: Request):
    """
    Webhook endpoint to receive events from WAHA.
    """
    payload = await request.json()
    print("Received Webhook payload:")
    print(payload)
    
    # Example logic: if it's a message, print the text
    if payload.get('event') == 'message':
        message_data = payload.get('payload', {})
        sender = message_data.get('from')
        body = message_data.get('body')
        print(f"Message from {sender}: {body}")
        
        # Here you could call your business logic to process the message and reply
        
    return {"status": "ok"}
