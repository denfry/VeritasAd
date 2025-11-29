from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
import httpx
from config import settings

router = Router()

@router.message(Command("analyze"))
async def cmd_analyze(message: Message):
    await message.answer(
        "Send me a video URL or upload a video file to analyze."
    )

@router.message(F.text.startswith("http"))
async def analyze_url(message: Message):
    url = message.text
    user_id = message.from_user.id
    api_key = f"tg_{user_id}"
    
    status_msg = await message.answer("Starting analysis...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Submit analysis
            response = await client.post(
                f"{settings.API_URL}/api/v1/analyze/check",
                data={"url": url},
                headers={"X-API-Key": api_key}
            )
            result = response.json()
            task_id = result.get("task_id")
            
            if not task_id:
                await status_msg.edit_text("Error: No task ID returned")
                return
            
            # Poll for progress
            for i in range(60):
                await asyncio.sleep(2)
                
                progress_response = await client.get(
                    f"{settings.API_URL}/api/v1/analysis/{task_id}/status",
                    headers={"X-API-Key": api_key}
                )
                progress = progress_response.json()
                
                status = progress.get("status")
                percent = progress.get("progress", 0)
                
                # Update message
                await status_msg.edit_text(
                    f"Analysis: {percent}%\nStatus: {status}"
                )
                
                if status == "completed":
                    # Get full results
                    await status_msg.edit_text(
                        f"Analysis completed!\n"
                        f"Advertising detected: {result.get('has_advertising', 'Unknown')}\n"
                        f"Confidence: {result.get('confidence_score', 0):.2%}"
                    )
                    break
                elif status == "failed":
                    await status_msg.edit_text(f"Analysis failed: {progress.get('message')}")
                    break
        except Exception as e:
            await status_msg.edit_text(f"Error: {str(e)}")

import asyncio
from aiogram import F
