from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
import httpx
from config import settings

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "User"
    
    # Generate API key for user
    async with httpx.AsyncClient() as client:
        try:
            # Auto-generate API key by first request
            api_key = f"tg_{user_id}"
            response = await client.get(
                f"{settings.API_URL}/health",
                headers={"X-API-Key": api_key}
            )
            
            welcome_text = f"""
<b>Welcome to VeritasAd Bot, {username}!</b>

I can help you analyze videos for advertising content.

<b>Your API Key:</b> <code>{api_key}</code>

<b>Commands:</b>
/analyze - Analyze a video
/history - View your analysis history
/profile - View your profile
/help - Show help

Send me a video link or file to start!
"""
            await message.answer(welcome_text)
        except Exception as e:
            await message.answer(f"Error: {str(e)}")

@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = """
<b>VeritasAd Bot - Help</b>

<b>How to use:</b>
1. Send me a video URL (YouTube, Telegram, etc.)
2. Or send me a video file
3. Wait for analysis to complete
4. Get detailed report

<b>Supported platforms:</b>
• YouTube
• Telegram
• Direct video links

<b>Commands:</b>
/start - Start bot
/analyze - Analyze video
/history - View history
/profile - View profile
/help - This message
"""
    await message.answer(help_text)
