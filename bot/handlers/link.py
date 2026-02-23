"""Telegram account linking handlers."""
import logging
import re
import httpx
from aiogram import Router, F, types
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from services.auth_service import BotAuthService
from config import settings

router = Router()
logger = logging.getLogger(__name__)

# Pattern to extract link token from /start command
LINK_TOKEN_PATTERN = re.compile(r"^start_(\w+)$")


def get_link_keyboard(link_token: str) -> InlineKeyboardMarkup:
    """Create keyboard with link button."""
    buttons = [
        [
            InlineKeyboardButton(
                text="Привязать аккаунт",
                callback_data=f"link_{link_token}",
            )
        ],
        [
            InlineKeyboardButton(
                text="Отмена",
                callback_data="link_cancel",
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_linked_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for linked account."""
    buttons = [
        [
            InlineKeyboardButton(
                text="Профиль",
                callback_data="profile",
            ),
            InlineKeyboardButton(
                text="Анализ",
                callback_data="analyze",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Отвязать аккаунт",
                callback_data="unlink_confirm",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_main_keyboard() -> InlineKeyboardMarkup:
    """Create main menu keyboard."""
    buttons = [
        [
            InlineKeyboardButton(text="Анализировать", callback_data="analyze"),
            InlineKeyboardButton(text="Профиль", callback_data="profile"),
        ],
        [
            InlineKeyboardButton(text="История", callback_data="history"),
            InlineKeyboardButton(text="Привязать аккаунт", callback_data="link_start"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(Command("link"))
async def cmd_link(message: Message):
    """Handle /link command - start account linking process."""
    telegram_id = message.from_user.id
    auth_service = BotAuthService()

    try:
        # Check if already linked
        status = await auth_service.check_account_status(telegram_id)
        if status.get("is_linked"):
            await message.answer(
                "Your Telegram account is already linked!\n\n"
                "You can now:\n"
                "- Analyze videos via the bot\n"
                "- Receive readiness notifications\n"
                "- Log in to the website via Telegram",
                reply_markup=get_linked_keyboard(),
            )
            return

        # Generate link token from backend
        api_key = f"tg_{telegram_id}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{settings.API_URL}/api/v1/telegram/link-token",
                    headers={"X-API-Key": api_key},
                )
                if response.status_code == 200:
                    data = response.json()
                    link_token = data.get("token")

                    bot_url = f"https://t.me/{(await message.bot.get_me()).username}?start={link_token}"

                    await message.answer(
                        "<b>Account Linking</b>\n\n"
                        f"1. Open this link:\n{bot_url}\n\n"
                        "2. Or click the button below",
                        reply_markup=get_link_keyboard(link_token),
                        parse_mode="HTML",
                    )
                    return
            except Exception as e:
                logger.error(f"Error generating link token: {e}")

        await message.answer(
            "Failed to generate link token.\n"
            "Please try again later or contact support.",
        )

    finally:
        await auth_service.close()


@router.callback_query(F.data == "link_start")
async def callback_link_start(callback_query: CallbackQuery):
    """Handle 'Link account' callback."""
    telegram_id = callback_query.from_user.id
    auth_service = BotAuthService()

    try:
        status = await auth_service.check_account_status(telegram_id)
        if status.get("is_linked"):
            await callback_query.message.answer(
                "Your account is already linked!",
                reply_markup=get_linked_keyboard(),
            )
            return

        await callback_query.message.answer(
            "<b>Account Linking</b>\n\n"
            "To link your account:\n\n"
            "1. Go to the website <b>Account → Telegram</b>\n"
            "2. Click <b>'Generate Token'</b>\n"
            "3. Copy the token and send it to me as a message\n\n"
            "Or use the /link command",
            parse_mode="HTML",
        )

    finally:
        await auth_service.close()

    await callback_query.answer()


@router.callback_query(F.data.startswith("link_"))
async def callback_link_execute(callback_query: CallbackQuery):
    """Handle link execution callback."""
    telegram_id = callback_query.from_user.id
    link_token = callback_query.data.split("_", 1)[1]
    username = callback_query.from_user.username

    auth_service = BotAuthService()

    try:
        await callback_query.message.answer("Linking account...")

        success, error = await auth_service.link_account(
            telegram_id=telegram_id,
            link_token=link_token,
            username=username,
        )

        if success:
            await callback_query.message.answer(
                "<b>Account successfully linked!</b>\n\n"
                "You can now:\n"
                "- Log in to the website via Telegram Login Widget\n"
                "- Analyze videos via the bot\n"
                "- Receive readiness notifications\n\n"
                "Use /help for available commands.",
                reply_markup=get_main_keyboard(),
                parse_mode="HTML",
            )
        else:
            await callback_query.message.answer(
                f"<b>Linking Error</b>\n\n{error}",
                parse_mode="HTML",
            )

    finally:
        await auth_service.close()

    await callback_query.answer()


@router.callback_query(F.data == "link_cancel")
async def callback_link_cancel(callback_query: CallbackQuery):
    """Handle link cancellation."""
    await callback_query.message.answer(
        "Linking cancelled.\n\n"
        "You can link your account later with /link",
    )
    await callback_query.answer()


@router.callback_query(F.data == "unlink_confirm")
async def callback_unlink_confirm(callback_query: CallbackQuery):
    """Confirm unlink account."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Yes, unlink",
                    callback_data="unlink_execute",
                ),
                InlineKeyboardButton(
                    text="Cancel",
                    callback_data="unlink_cancel",
                ),
            ],
        ]
    )

    await callback_query.message.answer(
        "<b>Unlink Account</b>\n\n"
        "Are you sure you want to unlink your Telegram account?\n\n"
        "After this:\n"
        "- You won't be able to log in via Telegram\n"
        "- Analysis history will remain on the website\n"
        "- You can link again later",
        reply_markup=keyboard,
        parse_mode="HTML",
    )
    await callback_query.answer()


@router.callback_query(F.data == "unlink_execute")
async def callback_unlink_execute(callback_query: CallbackQuery):
    """Execute unlink account."""
    telegram_id = callback_query.from_user.id
    auth_service = BotAuthService()

    try:
        success, error = await auth_service.unlink_account(telegram_id)

        if success:
            await callback_query.message.answer(
                "Account unlinked.\n\n"
                "You can link it again with /link",
                reply_markup=get_main_keyboard(),
            )
        else:
            await callback_query.message.answer(
                f"Error: {error}",
            )

    finally:
        await auth_service.close()

    await callback_query.answer()


@router.callback_query(F.data == "unlink_cancel")
async def callback_unlink_cancel(callback_query: CallbackQuery):
    """Cancel unlink."""
    await callback_query.message.answer(
        "Unlink cancelled.\n"
        "Your account remains linked.",
        reply_markup=get_linked_keyboard(),
    )
    await callback_query.answer()


@router.message(F.text)
async def handle_link_token(message: Message):
    """Handle link token sent as message."""
    telegram_id = message.from_user.id
    link_token = message.text.strip()
    username = message.from_user.username

    # Check if it looks like a token
    if len(link_token) < 20 or len(link_token) > 100:
        return  # Not a token, ignore

    auth_service = BotAuthService()

    try:
        # Check if already linked
        status = await auth_service.check_account_status(telegram_id)
        if status.get("is_linked"):
            await message.answer(
                "Your account is already linked!\n"
                "Use /unlink to unlink.",
            )
            return

        status_msg = await message.answer("Linking account...")

        success, error = await auth_service.link_account(
            telegram_id=telegram_id,
            link_token=link_token,
            username=username,
        )

        if success:
            await status_msg.edit_text(
                "<b>Account successfully linked!</b>\n\n"
                "You can now log in to the website via Telegram.",
                reply_markup=get_main_keyboard(),
                parse_mode="HTML",
            )
        else:
            await status_msg.edit_text(
                f"<b>Linking Error</b>\n\n{error}\n\n"
                "Please check the token and try again.",
                parse_mode="HTML",
            )

    finally:
        await auth_service.close()
