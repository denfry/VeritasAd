from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Create main menu inline keyboard."""
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


def back_keyboard() -> InlineKeyboardMarkup:
    """Create back button keyboard."""
    buttons = [
        [InlineKeyboardButton(text="Назад", callback_data="back")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def cancel_keyboard() -> InlineKeyboardMarkup:
    """Create cancel button keyboard."""
    buttons = [
        [InlineKeyboardButton(text="Отмена", callback_data="cancel")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def link_account_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for account linking."""
    buttons = [
        [
            InlineKeyboardButton(text="Привязать аккаунт", callback_data="link_start"),
        ],
        [
            InlineKeyboardButton(text="Отмена", callback_data="link_cancel"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def linked_account_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for linked account."""
    buttons = [
        [
            InlineKeyboardButton(text="Профиль", callback_data="profile"),
            InlineKeyboardButton(text="Анализ", callback_data="analyze"),
        ],
        [
            InlineKeyboardButton(text="Отвязать аккаунт", callback_data="unlink_confirm"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
