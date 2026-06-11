from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from database import get_user, update_user_coins, set_next_role
from keyboards import get_start_kb, get_lobby_kb, get_profile_kb, get_shop_kb
from game_engine import ACTIVE_GAMES, GameSession, GamePlayer
import random
import asyncio
from game_flow import start_game_flow

router = Router()

@router.message(Command("start"))
async def start_handler(message: Message):
    if message.chat.type == "private":
        get_user(message.from_user.id, message.from_user.full_name) # Ensure user in DB
        await message.answer(
            "Привет! Я бот для игры в 'Оборотней' (Мафию). \n"
            "Добавь меня в группу, чтобы создать лобби, или используй меню ниже.",
            reply_markup=get_start_kb()
        )
    else:
        await message.answer("Я работаю через кнопки! Нажми /create_lobby чтобы начать.")

@router.message(Command("create_lobby"))
async def create_lobby_handler(message: Message):
    if message.chat.type == "private":
         return await message.answer("Лобби нужно создавать в группе!")
    
    chat_id = message.chat.id
    if chat_id in ACTIVE_GAMES and ACTIVE_GAMES[chat_id].state != "FINISHED":
        return await message.answer("Игра здесь уже идёт или лобби создано.")
        
    game = GameSession(chat_id)
    game.creator_id = message.from_user.id
    player = GamePlayer(message.from_user.id, message.from_user.full_name)
    game.players[player.user_id] = player
    ACTIVE_GAMES[chat_id] = game
    
    text = f"🐺 ЛОББИ СОЗДАНО (1/12)\n\nСоздатель: {message.from_user.full_name}\n\nУчастники:\n1. {message.from_user.full_name}"
    await message.answer(text, reply_markup=get_lobby_kb(is_creator=False)) # Only creator sees start but we show it on update

@router.callback_query(F.data == "join_lobby")
async def join_lobby(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    if chat_id not in ACTIVE_GAMES:
        return await callback.answer("Лобби не существует.", show_alert=True)
    
    game = ACTIVE_GAMES[chat_id]
    user_id = callback.from_user.id
    if user_id in game.players:
        return await callback.answer("Ты уже в лобби!", show_alert=True)
        
    if len(game.players) >= 12:
        return await callback.answer("Лобби полно!", show_alert=True)
        
    user = get_user(user_id, callback.from_user.full_name)
    if user['coins'] < 50:
         return await callback.answer("Недостаточно монет для участия (нужно 50)!", show_alert=True)
         
    get_user(user_id, callback.from_user.full_name)
    player = GamePlayer(user_id, callback.from_user.full_name)
    game.players[user_id] = player
    
    players_text = "\n".join([f"{i+1}. {p.username}" for i, p in enumerate(game.players.values())])
    
    is_creator = callback.from_user.id == game.creator_id
    kb = get_lobby_kb(is_creator=True) # Usually creator will be the one controlling via their message view
    
    await callback.message.edit_text(
        f"🐺 ЛОББИ ({len(game.players)}/12)\n\nСоздатель: {game.players[game.creator_id].username}\n\nУчастники:\n{players_text}",
        reply_markup=get_lobby_kb(is_creator=False) # Wait, need to update inline kb dynamically. 
    )
    # Creator start button should be handled. Simplified here.
    
@router.callback_query(F.data == "my_profile")
async def my_profile(callback: CallbackQuery):
    user = get_user(callback.from_user.id, callback.from_user.full_name)
    text = (f"📊 Профиль: {user['username']}\n"
            f"🏆 Побед: {user['wins']}\n"
            f"💀 Поражений: {user['losses']}\n"
            f"💰 Монет: {user['coins']}\n"
            f"🎭 Любимая роль: {user['favorite_role']}\n"
            f"📈 Рейтинг: {user['rating']}\n")
    if callback.message.text != text:
        try:
             await callback.message.edit_text(text, reply_markup=get_profile_kb())
        except:
             pass
    await callback.answer()

@router.callback_query(F.data == "shop")
async def shop(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    text = (f"🛒 ДОБРО ПОЖАЛОВАТЬ В МАГАЗИН 🛒\n\n"
            f"💰 Твой баланс: {user['coins']} монет\n\n"
            f"【 ОБЫЧНЫЙ БИЛЕТ 】 100💰\nШансы: 50% обыватель, 30% активная, 20% оборотень\n\n"
            f"【 РЕДКИЙ БИЛЕТ 】 300💰\nШансы: 70% активная, 30% оборотень\n\n"
            f"【 ЛЕГЕНДАРНЫЙ БИЛЕТ 】 800💰\n100% активная роль")
    await callback.message.edit_text(text, reply_markup=get_shop_kb())

@router.callback_query(F.data.startswith("buy_ticket_"))
async def buy_ticket(callback: CallbackQuery):
    ticket_type = callback.data.split("_")[2]
    prices = {"normal": 100, "rare": 300, "legendary": 800}
    price = prices[ticket_type]
    
    user = get_user(callback.from_user.id)
    if user['coins'] < price:
        return await callback.answer("Недостаточно монет!", show_alert=True)
        
    update_user_coins(callback.from_user.id, -price)
    
    active_roles = ["Предсказатель", "Ведьма", "Купидон", "Охотник"]
    
    if ticket_type == "normal":
        outcome = random.choices(["Обыватель", "Active", "Оборотень"], weights=[50, 30, 20])[0]
    elif ticket_type == "rare":
        outcome = random.choices(["Active", "Оборотень"], weights=[70, 30])[0]
    else:
        outcome = "Active"
        
    if outcome == "Active":
         role = random.choice(active_roles)
    else:
         role = outcome
         
    set_next_role(callback.from_user.id, role)
    
    await callback.answer(f"Ты купил билет! Следующая роль: {role} (сохранено в профиль)", show_alert=True)
    await shop(callback)

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    await start_handler(callback.message)

@router.callback_query(F.data == "start_game")
async def start_game_btn(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    game = ACTIVE_GAMES.get(chat_id)
    if not game:
        return await callback.answer("Лобби не найдено.", show_alert=True)
    if callback.from_user.id != game.creator_id:
        return await callback.answer("Только создатель может начать!", show_alert=True)
    if len(game.players) < 2:
        return await callback.answer("Нужно хотя бы 2 игрока (в идеале 5+).", show_alert=True)
        
    await callback.message.delete()
    asyncio.create_task(start_game_flow(callback.bot, chat_id))
    await callback.answer("Запускаем игру...")

def get_game_for_user(user_id: int):
    for g in ACTIVE_GAMES.values():
        if user_id in g.players and g.state != "FINISHED":
            return g
    return None

@router.callback_query(F.data == "sleep_passive")
async def sleep_passive(callback: CallbackQuery):
    game = get_game_for_user(callback.from_user.id)
    if game and game.state == "NIGHT":
        game.night_actions[callback.from_user.id] = "sleep"
        await callback.message.edit_text("Вы уснули 💤. Ничего не произойдет до утра.")
    await callback.answer()

@router.callback_query(F.data.startswith("ww_vote:"))
async def ww_vote(callback: CallbackQuery):
    game = get_game_for_user(callback.from_user.id)
    if game and game.state == "NIGHT":
        target_id = int(callback.data.split(":")[1])
        game.night_actions[callback.from_user.id] = target_id
        await update_ww_votes(callback.bot, game)
    await callback.answer()

@router.callback_query(F.data.startswith("seer_look:"))
async def seer_look(callback: CallbackQuery):
    game = get_game_for_user(callback.from_user.id)
    if game and game.state == "NIGHT":
        target_id = int(callback.data.split(":")[1])
        game.night_actions[callback.from_user.id] = "looked"
        role = game.players[target_id].role_name
        name = game.players[target_id].username
        await callback.message.edit_text(f"🔮 Ясновидение: {name} имеет роль [{role}]")
    await callback.answer()

@router.callback_query(F.data.startswith("day_vote:"))
async def day_vote(callback: CallbackQuery):
    game = get_game_for_user(callback.from_user.id)
    if game and game.state == "VOTING":
        target_id = int(callback.data.split(":")[1])
        game.day_votes[callback.from_user.id] = target_id
        await update_day_votes(callback.bot, game)
    await callback.answer()

async def update_ww_votes(bot: Bot, game: GameSession):
    alive_wws = game.get_alive_werewolves()
    votes_text = ""
    for ww in alive_wws:
        target_id = game.night_actions.get(ww.user_id)
        if target_id and isinstance(target_id, int):
            target_name = game.players[target_id].username
            votes_text += f"\n🐺 {ww.username} ➡ 🩸 {target_name}"
        else:
            votes_text += f"\n🐺 {ww.username} ➡ ⏳ думает..."
            
    base_text = "🐺 Выберите жертву:\n" + votes_text
    
    for ww in alive_wws:
        msg_id = game.ww_msg_ids.get(ww.user_id)
        if msg_id:
            others = [x for x in game.get_alive_players() if x.role_name != "Оборотень"]
            kb = get_player_selection_kb(others, "ww_vote")
            try:
                await bot.edit_message_text(base_text, chat_id=ww.user_id, message_id=msg_id, reply_markup=kb)
            except Exception:
                pass

async def update_day_votes(bot: Bot, game: GameSession):
    alive = game.get_alive_players()
    votes_text = ""
    for p in alive:
        target_id = game.day_votes.get(p.user_id)
        if target_id:
            target_name = game.players[target_id].username
            votes_text += f"\n👤 {p.username} ➡ 🪢 {target_name}"
        else:
            votes_text += f"\n👤 {p.username} ➡ ⏳ думает..."
            
    base_text = "⚖️ Кого отправим на виселицу?\n" + votes_text
    
    for p in alive:
        msg_id = game.day_vote_msg_ids.get(p.user_id)
        if msg_id:
            kb = get_player_selection_kb(alive, "day_vote", p.user_id)
            try:
                await bot.edit_message_text(base_text, chat_id=p.user_id, message_id=msg_id, reply_markup=kb)
            except Exception:
                pass
