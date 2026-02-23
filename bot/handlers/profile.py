from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
import logging
from config import settings
from services.api_client import VeritasAdApiClient
from services.auth_service import BotAuthService
from keyboards import main_menu_keyboard

router = Router()
logger = logging.getLogger(__name__)


def get_profile_keyboard(is_linked: bool) -> InlineKeyboardMarkup:
    """Create profile keyboard based on link status."""
    buttons = [
        [
            InlineKeyboardButton(text="Analyze", callback_data="analyze"),
            InlineKeyboardButton(text="History", callback_data="history"),
        ],
    ]

    if is_linked:
        buttons.append(
            [InlineKeyboardButton(text="Unlink Account", callback_data="unlink_confirm")]
        )
    else:
        buttons.append(
            [InlineKeyboardButton(text="Link Account", callback_data="link_start")]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(Command("profile"))
async def cmd_profile(message: Message):
    """Handle /profile command with Telegram link status."""
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name or "User"
    api_key = f"tg_{user_id}"

    # Get profile and link status
    auth_service = BotAuthService()
    profile_data = None
    link_status = None
    
    try:
        profile_data = await auth_service.get_user_profile(user_id)
        link_status = await auth_service.check_account_status(user_id)
    except Exception as exc:
        logger.warning(f"Failed to get profile: {exc}")
    finally:
        await auth_service.close()

    is_linked = link_status.get("is_linked", False) if link_status else False
    telegram_username = link_status.get("telegram_username") if link_status else None

    profile_text = f"""
<b>Your Profile</b>

<b>Telegram ID:</b> <code>{user_id}</code>
<b>Username:</b> @{message.from_user.username or 'not specified'}

<b>Link Status:</b> {"Linked" if is_linked else "Not linked"}
"""

    if is_linked and telegram_username:
        profile_text += f"\n<b>Telegram:</b> @{telegram_username}"

    if profile_data:
        profile_text += f"""

<b>Statistics:</b>
- Plan: {profile_data.get('plan', 'Free').capitalize()}
- Daily limit: {profile_data.get('daily_limit', 100)}
- Used today: {profile_data.get('daily_used', 0)}
- Total analyses: {profile_data.get('total_analyses', 0)}
"""
    else:
        profile_text += f"""

<b>Statistics:</b>
- Plan: Free
- Daily limit: 100 analyses
"""

    if not is_linked:
        profile_text += """
Tip: Link your account to log in to the website via Telegram!
Use /link or the button below.
"""

    await message.answer(
        profile_text,
        reply_markup=get_profile_keyboard(is_linked),
        parse_mode="HTML",
    )


@router.message(Command("history"))
async def cmd_history(message: Message):
    """Handle /history command."""
    history_text = """
<b>Analysis History</b>

This feature is under development.

Coming soon:
- View all your analyses
- Filter by date and status
- Download PDF reports
- Repeat previous analyses

Stay tuned!
"""
    await message.answer(history_text, parse_mode="HTML")
