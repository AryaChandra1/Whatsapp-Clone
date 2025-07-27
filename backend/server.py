from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
import openai
import base64

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# OpenAI setup
openai.api_key = os.environ['OPENAI_API_KEY']

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# AI Personalities Configuration
AI_PERSONALITIES = {
    "alex_sarcastic": {
        "name": "Alex",
        "avatar": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
        "description": "Your sarcastic friend who always has a witty comeback",
        "system_prompt": "You are Alex, a sarcastic and witty friend. You love making jokes, using sarcasm, and playful teasing. Keep responses casual, funny, and a bit sassy. Use modern slang and emojis sparingly. Always maintain a friendly tone despite the sarcasm.",
        "last_seen": "online"
    },
    "maya_mentor": {
        "name": "Maya",
        "avatar": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
        "description": "Wise mentor who provides thoughtful guidance",
        "system_prompt": "You are Maya, a wise and caring mentor. You provide thoughtful guidance, ask meaningful questions, and help people grow. Your responses are warm, insightful, and encouraging. You draw from life experience and always see the bigger picture.",
        "last_seen": "2 mins ago"
    },
    "zoe_tech": {
        "name": "Zoe",
        "avatar": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
        "description": "Tech geek who loves coding and gadgets",
        "system_prompt": "You are Zoe, a passionate tech geek and programmer. You love discussing coding, new technologies, gadgets, and programming languages. You're enthusiastic about tech trends and always excited to share knowledge. Use some technical terms but keep it accessible.",
        "last_seen": "5 mins ago"
    },
    "ryan_flirty": {
        "name": "Ryan",
        "avatar": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
        "description": "Your charming and flirty crush",
        "system_prompt": "You are Ryan, a charming and slightly flirty person. You're confident, playful, and know how to make someone feel special. Use subtle compliments, playful teasing, and maintain an air of mystery. Keep it fun and lighthearted.",
        "last_seen": "1 min ago"
    },
    "sage_spiritual": {
        "name": "Sage",
        "avatar": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
        "description": "Spiritual guru who brings peace and wisdom",
        "system_prompt": "You are Sage, a spiritual guide focused on mindfulness, inner peace, and personal growth. You speak with calm wisdom, often sharing insights about life's deeper meanings. Use gentle language and occasional spiritual concepts.",
        "last_seen": "30 mins ago"
    },
    "jake_funny": {
        "name": "Jake",
        "avatar": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
        "description": "The class clown who always makes you laugh",
        "system_prompt": "You are Jake, the ultimate class clown and comedian. You love making people laugh with jokes, puns, funny stories, and silly observations. You're upbeat, energetic, and always looking for the humor in any situation.",
        "last_seen": "15 mins ago"
    },
    "luna_mysterious": {
        "name": "Luna",
        "avatar": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
        "description": "Mysterious friend with deep thoughts",
        "system_prompt": "You are Luna, a mysterious and thoughtful person who speaks in poetic, somewhat cryptic ways. You're introspective, philosophical, and have a unique perspective on life. Your responses are intriguing and make people think.",
        "last_seen": "1 hour ago"
    },
    "max_athlete": {
        "name": "Max",
        "avatar": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
        "description": "Fitness enthusiast and motivational coach",
        "system_prompt": "You are Max, a fitness enthusiast and motivational coach. You're energetic, positive, and always encouraging people to be their best selves. You love talking about sports, workouts, healthy living, and personal achievement.",
        "last_seen": "3 mins ago"
    },
    "aria_artist": {
        "name": "Aria",
        "avatar": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
        "description": "Creative artist with a passionate soul",
        "system_prompt": "You are Aria, a creative and passionate artist. You see beauty in everything and express yourself through art, music, and creative writing. You're emotional, expressive, and always inspired by the world around you.",
        "last_seen": "20 mins ago"
    },
    "noah_chill": {
        "name": "Noah",
        "avatar": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
        "description": "Laid-back friend who goes with the flow",
        "system_prompt": "You are Noah, a super chill and laid-back person. You're easygoing, relaxed, and have a 'go with the flow' attitude. You use casual language, don't stress about things, and help others stay calm too.",
        "last_seen": "10 mins ago"
    }
}

# Data Models
class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    chat_id: str
    sender_type: str  # "user" or "ai"
    sender_name: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    message_status: str = "sent"  # sent, delivered, read
    message_type: str = "text"  # text, image, audio

class MessageCreate(BaseModel):
    chat_id: str
    content: str

class Chat(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ai_personality: str
    last_message: Optional[str] = None
    last_message_time: Optional[datetime] = None
    unread_count: int = 0

class ChatResponse(BaseModel):
    id: str
    ai_personality: str
    name: str
    avatar: str
    description: str
    last_message: Optional[str] = None
    last_message_time: Optional[datetime] = None
    last_seen: str
    unread_count: int = 0

class AIResponse(BaseModel):
    message: str
    typing_duration: int  # milliseconds to simulate typing

# Routes
@api_router.get("/")
async def root():
    return {"message": "WhatsApp AI Clone API"}

@api_router.get("/chats", response_model=List[ChatResponse])
async def get_chats():
    """Get all AI personality chats"""
    chats = []
    
    # Get existing chats from database
    db_chats = await db.chats.find().to_list(1000)
    existing_chat_personalities = {chat["ai_personality"] for chat in db_chats}
    
    # Create chats for all personalities
    for personality_id, personality_data in AI_PERSONALITIES.items():
        db_chat = next((chat for chat in db_chats if chat["ai_personality"] == personality_id), None)
        
        if db_chat:
            chat_response = ChatResponse(
                id=db_chat["id"],
                ai_personality=personality_id,
                name=personality_data["name"],
                avatar=personality_data["avatar"],
                description=personality_data["description"],
                last_message=db_chat.get("last_message"),
                last_message_time=db_chat.get("last_message_time"),
                last_seen=personality_data["last_seen"],
                unread_count=db_chat.get("unread_count", 0)
            )
        else:
            # Create new chat for this personality
            new_chat = Chat(ai_personality=personality_id)
            await db.chats.insert_one(new_chat.dict())
            
            chat_response = ChatResponse(
                id=new_chat.id,
                ai_personality=personality_id,
                name=personality_data["name"],
                avatar=personality_data["avatar"],
                description=personality_data["description"],
                last_seen=personality_data["last_seen"],
                unread_count=0
            )
        
        chats.append(chat_response)
    
    # Sort by last message time (most recent first)
    chats.sort(key=lambda x: x.last_message_time or datetime.min, reverse=True)
    return chats

@api_router.get("/chats/{chat_id}/messages", response_model=List[Message])
async def get_chat_messages(chat_id: str):
    """Get all messages for a specific chat"""
    messages = await db.messages.find({"chat_id": chat_id}).sort("timestamp", 1).to_list(1000)
    return [Message(**msg) for msg in messages]

@api_router.post("/chats/{chat_id}/messages", response_model=Message)
async def send_message(chat_id: str, message_data: MessageCreate):
    """Send a message to an AI personality"""
    
    # Get the chat to find the AI personality
    chat = await db.chats.find_one({"id": chat_id})
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    personality_id = chat["ai_personality"]
    personality_data = AI_PERSONALITIES.get(personality_id)
    
    if not personality_data:
        raise HTTPException(status_code=404, detail="AI personality not found")
    
    # Save user message
    user_message = Message(
        chat_id=chat_id,
        sender_type="user",
        sender_name="You",
        content=message_data.content,
        message_status="sent"
    )
    await db.messages.insert_one(user_message.dict())
    
    # Generate AI response using OpenAI
    try:
        # Get recent conversation context (last 10 messages)
        recent_messages = await db.messages.find(
            {"chat_id": chat_id}
        ).sort("timestamp", -1).limit(10).to_list(10)
        recent_messages.reverse()  # Oldest first
        
        # Build conversation context
        conversation_context = []
        conversation_context.append({
            "role": "system", 
            "content": personality_data["system_prompt"]
        })
        
        # Add recent conversation history
        for msg in recent_messages[:-1]:  # Exclude the message we just added
            if msg["sender_type"] == "user":
                conversation_context.append({
                    "role": "user",
                    "content": msg["content"]
                })
            else:
                conversation_context.append({
                    "role": "assistant", 
                    "content": msg["content"]
                })
        
        # Add current user message
        conversation_context.append({
            "role": "user",
            "content": message_data.content
        })
        
        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # Using latest model
            messages=conversation_context,
            max_tokens=150,
            temperature=0.9
        )
        
        ai_response_content = response.choices[0].message.content
        
        # Save AI response
        ai_message = Message(
            chat_id=chat_id,
            sender_type="ai",
            sender_name=personality_data["name"],
            content=ai_response_content,
            message_status="delivered"
        )
        await db.messages.insert_one(ai_message.dict())
        
        # Update chat with last message
        await db.chats.update_one(
            {"id": chat_id},
            {
                "$set": {
                    "last_message": ai_response_content,
                    "last_message_time": ai_message.timestamp
                }
            }
        )
        
        return ai_message
        
    except Exception as e:
        logging.error(f"Error generating AI response: {str(e)}")
        # Return a fallback response
        fallback_message = Message(
            chat_id=chat_id,
            sender_type="ai", 
            sender_name=personality_data["name"],
            content="Sorry, I'm having trouble responding right now. Try again in a moment!",
            message_status="delivered"
        )
        await db.messages.insert_one(fallback_message.dict())
        return fallback_message

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()