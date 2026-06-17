import os
import token
from dotenv import load_dotenv
load_dotenv()
import requests
from fastapi import APIRouter, Request, Header, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from database import get_db
import models
import ai_service

router = APIRouter()

FB_VERIFY_TOKEN = os.getenv("FB_VERIFY_TOKEN", "my_secure_token_123")

def send_instagram_message(recipient_id: str, message_text: str, access_token: str):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={access_token}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    response = requests.post(url, json=payload)
    return response.json()

async def process_incoming_message(payload: dict, db: Session):
    try:
        # Extract basic info from Meta payload
        for entry in payload.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                sender_id = messaging_event.get("sender", {}).get("id")
                recipient_id = messaging_event.get("recipient", {}).get("id")
                message = messaging_event.get("message", {})
                message_text = message.get("text")

                if not message_text or not sender_id:
                    continue

                # Find the user associated with this Instagram Page ID
                user = db.query(models.User).filter(models.User.instagram_page_id == recipient_id).first()
                
                if not user or not user.instagram_access_token:
                    continue

                # Check Bot Status
                if user.bot_status == "disabled" or user.bot_status == "human_takeover":
                    continue

                if user.bot_status == "paused":
                    # Optionally notify human or just skip
                    continue

                # Generate AI Response
                ai_reply = ai_service.generate_ai_reply(user, message_text, db)
                
                if ai_reply:
                    send_instagram_message(sender_id, ai_reply, user.instagram_access_token)

    except Exception as e:
        print(f"Error processing webhook: {e}")

@router.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    print("TOKEN RECEIVED =", token)
    print("TOKEN EXPECTED =", FB_VERIFY_TOKEN)
    print("MODE =", mode)
    print("TOKEN =", token)
    print("EXPECTED =", FB_VERIFY_TOKEN)
    print("CHALLENGE =", challenge)
    if mode == "subscribe" and token == FB_VERIFY_TOKEN:
        return int(challenge)
    return {"error": "Verification failed"}

@router.post("/webhook")
async def handle_webhook(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    payload = await request.json()
    
    # Meta requires a 200 OK response quickly
    background_tasks.add_task(process_incoming_message, payload, db)
    
    return {"status": "success"}