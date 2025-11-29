from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
import httpx
from config import settings

router = Router()

@router.message(Command("profile"))
async def cmd_profile(message: Message):
    user_id = message.from_user.id
    api_key = f"tg_{user_id}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.API_URL}/api/v1/user/profile",
                headers={"X-API-Key": api_key}
            )
            
            if response.status_code == 200:
                data = response.json()
                profile_text = f"""
<b>Your Profile</b>

<b>Plan:</b> {data.get('plan', 'free')}
<b>Daily Limit:</b> {data.get('daily_limit', 0)}
<b>Used Today:</b> {data.get('daily_used', 0)}
<b>Total Analyses:</b> {data.get('total_analyses', 0)}

<b>API Key:</b> <code>{api_key}</code>
"""
                await message.answer(profile_text)
            else:
                await message.answer("Could not fetch profile.")
        except Exception as e:
            await message.answer(f"Error: {str(e)}")

@router.message(Command("history"))
async def cmd_history(message: Message):
    await message.answer("History feature coming soon!")
