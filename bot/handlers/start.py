from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
import logging
from config import settings
from services.api_client import VeritasAdApiClient
from services.auth_service import BotAuthService
from keyboards import main_menu_keyboard

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Handle /start command with optional link token."""
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name or "User"
    
    # Check for link token in start parameters
    args = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
    link_token = None
    
    if args and len(args) > 20:  # Likely a link token
        link_token = args

    # Generate API key for this user
    api_key = f"tg_{user_id}"

    # Try to check backend health (optional)
    try:
        api_client = VeritasAdApiClient(settings.API_URL)
        health = await api_client.health_check(api_key=api_key)
        await api_client.close()
        api_status = "Online" if health else "Offline"
    except Exception:
        api_status = "Offline"

    # If link token provided, try to link account
    if link_token:
        auth_service = BotAuthService()
        try:
            success, error = await auth_service.link_account(
                telegram_id=user_id,
                link_token=link_token,
                username=username,
            )
            
            if success:
                await message.answer(
                    f"""
<b>Account successfully linked!</b>

<b>Welcome, {username}!</b>

Your Telegram account is now linked to your website account.
You can now log in via Telegram Login Widget.

<b>Available commands:</b>
/analyze - Analyze video
/profile - My profile
/history - Analysis history
/help - Help

<b>How to use:</b>
Simply send me a link to a video (YouTube, Telegram, TikTok)
or upload a video file, and I'll analyze it for advertising!
""",
                    reply_markup=main_menu_keyboard(),
                    parse_mode="HTML",
                )
                await auth_service.close()
                return
            else:
                logger.warning(f"Auto-link failed: {error}")
        finally:
            await auth_service.close()

    welcome_text = f"""
<b>Welcome, {username}!</b>

I am <b>VeritasAd Bot</b>, helping you analyze videos for hidden advertising.

<b>Your API Key:</b>
<code>{api_key}</code>

<b>API Status:</b> {api_status}

<b>Available commands:</b>
/analyze - Analyze video
/profile - My profile
/history - Analysis history
/link - Link account to website
/help - Help

<b>How to use:</b>
Simply send me a link to a video (YouTube, Telegram, TikTok)
or upload a video file, and I'll analyze it for advertising!

<b>Tip:</b> Link your account with /link to log in to the website via Telegram!
"""

    await message.answer(
        welcome_text,
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command."""
    help_text = """
<b>VeritasAd Bot - Help</b>

<b>How it works:</b>
1. Send a link to a video (YouTube, Telegram, TikTok, etc.)
2. Or upload a video file directly
3. Wait for analysis to complete
4. Receive a detailed report

<b>Supported platforms:</b>
- YouTube (youtube.com, youtu.be)
- Telegram (t.me)
- TikTok (tiktok.com)
- Instagram (instagram.com)
- Direct video links

<b>Commands:</b>
/start - Start the bot
/analyze - Start analysis
/profile - Profile information
/history - Analysis history
/help - This help message

<b>Security:</b>
All videos are processed confidentially.
API key is used for identification and rate limiting.
"""
    await message.answer(help_text, parse_mode="HTML")


@router.callback_query(F.data == "analyze")
async def callback_analyze(callback_query):
    """Handle 'Analyze' callback."""
    await callback_query.message.answer(
        "<b>Video Analysis</b>\n\n"
        "Send a video link or upload a file.",
        parse_mode="HTML",
    )
    await callback_query.answer()


@router.callback_query(F.data == "profile")
async def callback_profile(callback_query):
    """Handle 'Profile' callback."""
    await callback_query.message.answer(
        "Use the /profile command to view your profile information.",
        parse_mode="HTML",
    )
    await callback_query.answer()


@router.callback_query(F.data == "history")
async def callback_history(callback_query):
    """Handle 'History' callback."""
    await callback_query.message.answer(
        "<b>Analysis History</b>\n\n"
        "Feature coming soon. Stay tuned!",
        parse_mode="HTML",
    )
    await callback_query.answer()
