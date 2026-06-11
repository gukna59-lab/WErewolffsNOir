from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_start_kb(bot_username: str = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Мой профиль 👤", callback_data="my_profile"))
    if bot_username:
        builder.row(InlineKeyboardButton(text="Добавить в группу ➕", url=f"https://t.me/{bot_username}?startgroup=true"))
    builder.row(InlineKeyboardButton(text="Магазин 🛒", callback_data="shop"))
    return builder.as_markup()

def get_new_lobby_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔄 Создать новое лобби", callback_data="create_new_lobby"))
    return builder.as_markup()

def get_lobby_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Присоединиться ✅", callback_data="join_lobby"))
    builder.row(InlineKeyboardButton(text="Выйти ❌", callback_data="leave_lobby"))
    builder.row(InlineKeyboardButton(text="▶ Старт", callback_data="start_game"))
    return builder.as_markup()

def get_profile_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔄 Обновить", callback_data="my_profile"))
    builder.row(InlineKeyboardButton(text="🏪 Магазин", callback_data="shop"))
    return builder.as_markup()

def get_shop_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🎫 Купить обычный (100) 💰", callback_data="buy_ticket_normal"))
    builder.row(InlineKeyboardButton(text="🎫 Купить редкий (300) 💰", callback_data="buy_ticket_rare"))
    builder.row(InlineKeyboardButton(text="🎫 Купить легендарный (800) 💰", callback_data="buy_ticket_legendary"))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu"))
    return builder.as_markup()

def get_player_selection_kb(players: list, callback_prefix: str, exclude_ids: list = None) -> InlineKeyboardMarkup:
    if exclude_ids is None: exclude_ids = []
    builder = InlineKeyboardBuilder()
    for player in players:
        if player.user_id not in exclude_ids:
            builder.button(text=player.username, callback_data=f"{callback_prefix}:{player.user_id}")
    builder.adjust(2)
    return builder.as_markup()

def get_witch_action_kb(can_heal: bool, can_poison: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if can_heal:
        builder.row(InlineKeyboardButton(text="🧪 Слепое исцеление", callback_data="witch_action:heal"))
    if can_poison:
        builder.row(InlineKeyboardButton(text="☠️ Отравить", callback_data="witch_action:poison"))
    builder.row(InlineKeyboardButton(text="💤 Пропустить", callback_data="witch_action:skip"))
    return builder.as_markup()

def get_little_girl_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="👀 Подсмотреть", callback_data="girl_look")
    builder.button(text="😴 Спать", callback_data="girl_sleep")
    builder.adjust(1)
    return builder.as_markup()

def get_passive_night_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💤 Уснуть", callback_data="sleep_passive")
    return builder.as_markup()

def get_confirm_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Применить", callback_data="confirm_action")
    return builder.as_markup()
