from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
import logging
from config import settings
from services.api_client import VeritasAdApiClient
from services.auth_service import BotAuthService
from keyboards import main_menu_keyboard

router = Router()
logger = logging.getLogger(__name__)

HISTORY_PAGE_SIZE = 5

user_history_pages = {}  # user_id -> current page


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
            [
                InlineKeyboardButton(
                    text="Unlink Account", callback_data="unlink_confirm"
                )
            ]
        )
    else:
        buttons.append(
            [InlineKeyboardButton(text="Link Account", callback_data="link_start")]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_history_keyboard(
    user_id: int, page: int, has_more: bool
) -> InlineKeyboardMarkup:
    """Create pagination keyboard for history."""
    buttons = []

    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                text="← Prev", callback_data=f"history_page_{page - 1}"
            )
        )
    if has_more:
        nav_buttons.append(
            InlineKeyboardButton(
                text="Next →", callback_data=f"history_page_{page + 1}"
            )
        )

    if nav_buttons:
        buttons.append(nav_buttons)

    buttons.append(
        [
            InlineKeyboardButton(
                text="← Back to Profile", callback_data="back_to_profile"
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def format_history_item(item: dict, index: int) -> str:
    """Format a single history item for display."""
    task_id = item.get("task_id", "N/A")[:8]
    status = item.get("status", "unknown")
    source = item.get("source_type", "unknown")
    created = item.get("created_at", "")

    # Format date
    date_str = ""
    if created:
        try:
            from datetime import datetime

            dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            date_str = dt.strftime("%d.%m.%Y %H:%M")
        except:
            date_str = created[:10]

    # Status emoji
    status_emoji = {
        "completed": "✅",
        "failed": "❌",
        "processing": "⏳",
        "queued": "⏳",
    }.get(status, "❓")

    # Confidence score
    confidence = item.get("confidence_score")
    confidence_str = ""
    if confidence is not None:
        confidence_str = f" ({(confidence * 100):.0f}% confidence)"

    # Result
    has_ads = item.get("has_advertising")
    result = ""
    if status == "completed":
        result = "📢 Advertising" if has_ads else "✅ Clean"

    return f"{index + 1}. {status_emoji} {source.upper()}{confidence_str}\n   📅 {date_str} | {result}\n   🔹 ID: {task_id}"


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
<b>Username:</b> @{message.from_user.username or "not specified"}

<b>Link Status:</b> {"Linked" if is_linked else "Not linked"}
"""

    if is_linked and telegram_username:
        profile_text += f"\n<b>Telegram:</b> @{telegram_username}"

    if profile_data:
        profile_text += f"""

<b>Statistics:</b>
- Plan: {profile_data.get("plan", "Free").capitalize()}
- Daily limit: {profile_data.get("daily_limit", 100)}
- Used today: {profile_data.get("daily_used", 0)}
- Total analyses: {profile_data.get("total_analyses", 0)}
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
    """Handle /history command - show analysis history."""
    user_id = message.from_user.id
    api_key = f"tg_{user_id}"

    # Reset page for new command
    user_history_pages[user_id] = 0

    await show_history(message, user_id, api_key, page=0)


async def show_history(message_or_callback, user_id: int, api_key: str, page: int = 0):
    """Show history page."""
    client = VeritasAdApiClient(settings.API_URL)
    user_history_pages[user_id] = page

    try:
        history = await client.get_analysis_history(
            api_key=api_key, limit=HISTORY_PAGE_SIZE, offset=page * HISTORY_PAGE_SIZE
        )

        if not history:
            text = """
<b>Analysis History</b>

📭 No analyses found yet.

Start your first analysis with /analyze or send a video URL!
"""
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="← Back to Profile", callback_data="back_to_profile"
                        )
                    ]
                ]
            )

            if hasattr(message_or_callback, "message"):
                await message_or_callback.message.edit_text(
                    text, reply_markup=keyboard, parse_mode="HTML"
                )
            else:
                await message_or_callback.answer(
                    text, reply_markup=keyboard, parse_mode="HTML"
                )
            return

        # Check if there's more
        has_more = len(history) == HISTORY_PAGE_SIZE

        # Format history
        text = f"<b>Analysis History</b> (Page {page + 1})\n\n"

        for i, item in enumerate(history):
            text += format_history_item(item, i) + "\n\n"

        if has_more:
            text += "<i>More results available...</i>"

        keyboard = get_history_keyboard(user_id, page, has_more)

        if hasattr(message_or_callback, "message"):
            await message_or_callback.message.edit_text(
                text, reply_markup=keyboard, parse_mode="HTML"
            )
        else:
            await message_or_callback.message.answer(
                text, reply_markup=keyboard, parse_mode="HTML"
            )

    except Exception as e:
        logger.error(f"Error loading history: {e}")
        error_text = """
<b>Analysis History</b>

❌ Failed to load history.

Please try again later or link your account.
"""
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="← Back to Profile", callback_data="back_to_profile"
                    )
                ]
            ]
        )

        if hasattr(message_or_callback, "message"):
            await message_or_callback.message.edit_text(
                error_text, reply_markup=keyboard, parse_mode="HTML"
            )
        else:
            await message_or_callback.message.answer(
                error_text, reply_markup=keyboard, parse_mode="HTML"
            )
    finally:
        await client.close()


@router.callback_query(F.data.startswith("history_page_"))
async def callback_history_page(callback: CallbackQuery):
    """Handle history pagination."""
    user_id = callback.from_user.id
    api_key = f"tg_{user_id}"

    page = int(callback.data.split("_")[-1])

    await callback.answer()
    await show_history(callback, user_id, api_key, page=page)


@router.callback_query(F.data == "history")
async def callback_history(callback: CallbackQuery):
    """Handle History button press."""
    user_id = callback.from_user.id
    api_key = f"tg_{user_id}"

    await callback.answer()
    user_history_pages[user_id] = 0
    await show_history(callback, user_id, api_key, page=0)


@router.callback_query(F.data == "back_to_profile")
async def callback_back_to_profile(callback: CallbackQuery):
    """Handle back to profile button."""
    await callback.answer()
    await cmd_profile(callback.message)
