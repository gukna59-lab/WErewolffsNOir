import asyncio
import random
from aiogram import Bot
from game_engine import ACTIVE_GAMES, GameSession
from keyboards import get_player_selection_kb, get_passive_night_kb, get_start_kb, get_witch_action_kb, get_little_girl_kb
from database import update_user_coins, get_user, update_user_stats

GIFS = {
    "NIGHT": "https://i.pinimg.com/originals/79/72/f1/7972f147519d7d5cf6b32204662c13d2.gif",
    "DAY": "https://i.pinimg.com/originals/93/0f/22/930f22d2e9a376232cc5d42bc5b4cc90.gif",
    "EXECUTION": "https://i.pinimg.com/originals/fe/7a/ef/fe7aef331608c8ea3a9e9131e24eabc7.gif",
    "WEREWOLVES_WIN": "https://i.pinimg.com/originals/79/72/f1/7972f147519d7d5cf6b32204662c13d2.gif",
    "VILLAGERS_WIN": "https://i.pinimg.com/originals/93/0f/22/930f22d2e9a376232cc5d42bc5b4cc90.gif",
    "DRAW": "https://i.pinimg.com/originals/fe/7a/ef/fe7aef331608c8ea3a9e9131e24eabc7.gif",
    "VOTE": "https://i.pinimg.com/originals/fe/7a/ef/fe7aef331608c8ea3a9e9131e24eabc7.gif"
}

async def broadcast(bot: Bot, game: GameSession, text: str, reply_markup=None, animation: str = None):
    try:
        if animation:
            try:
                await bot.send_animation(game.chat_id, animation, caption=text, reply_markup=reply_markup)
                return
            except Exception as e:
                print(f"Animation error: {e}. Falling back to text.")
        await bot.send_message(game.chat_id, text, reply_markup=reply_markup)
    except Exception as e:
        print(f"Broadcast error: {e}")

async def start_game_flow(bot: Bot, chat_id: int):
    game = ACTIVE_GAMES.get(chat_id)
    if not game: return
    
    next_roles_dict = {}
    for p in game.players.values():
        user = get_user(p.user_id)
        if user.get('next_role'):
            next_roles_dict[p.user_id] = user['next_role']
        update_user_coins(p.user_id, -50)
        
    game.assign_roles(next_roles_dict)
    game.state = "DISTRIBUTION"
    
    await broadcast(bot, game, "🌑 Игра начинается!\nВсем участникам были отправлены их роли в ЛС (Спишитесь с ботом, если вы этого еще не сделали).")
    
    for p in game.get_alive_players():
        role_text = f"🎭 Твоя роль: {p.role_instance.name}\n📖 {p.role_instance.description}\n🔮 {p.role_instance.ability}"
        try:
            await bot.send_message(p.user_id, role_text)
        except Exception as e:
            print(f"DM err {p.user_id}: {e}")
            
    await asyncio.sleep(5)
    asyncio.create_task(run_night_phase(bot, chat_id))
    
async def run_night_phase(bot: Bot, chat_id: int):
    game = ACTIVE_GAMES.get(chat_id)
    if not game: return
    game.state = "NIGHT"
    game.day_count += 1
    game.night_actions = {} 
    
    await broadcast(bot, game, f"🌙 Наступает ночь {game.day_count}. Город засыпает...", animation=GIFS["NIGHT"])
    
    game.ww_msg_ids = {}
    
    alive = game.get_alive_players()
    for p in alive:
        try:
            if p.role_name == "Оборотень":
                others = [x for x in alive if x.role_name != "Оборотень"]
                kb = get_player_selection_kb(others, "ww_vote")
                
                alive_wws = game.get_alive_werewolves()
                votes_text = ""
                for ww in alive_wws:
                    votes_text += f"\n🐺 {ww.username} ➡ ⏳ думает..."
                    
                msg = await bot.send_message(p.user_id, "🐺 Выберите жертву:\n" + votes_text, reply_markup=kb)
                game.ww_msg_ids[p.user_id] = msg.message_id
            elif p.role_name == "Предсказатель":
                kb = get_player_selection_kb(alive, "seer_look", p.user_id)
                await bot.send_message(p.user_id, "🔮 Кого проверить?", reply_markup=kb)
            elif p.role_name == "Купидон" and game.day_count == 1:
                kb = get_player_selection_kb(alive, "cupid_vote")
                await bot.send_message(p.user_id, "💘 Выбери двух влюбленных (нажми на двоих):", reply_markup=kb)
            elif p.role_name == "Ведьма":
                kb = get_witch_action_kb(not game.witch_heal_used, not game.witch_poison_used)
                await bot.send_message(p.user_id, "🧙‍♀️ Зелья:", reply_markup=kb)
            elif p.role_name == "Маленькая девочка":
                await bot.send_message(p.user_id, "👧 Хочешь подсмотреть за Оборотнями?", reply_markup=get_little_girl_kb())
            else:
                await bot.send_message(p.user_id, "💤 Фаза сна. Нажмите чтобы уснуть.", reply_markup=get_passive_night_kb())
        except Exception as e:
            pass
            
    expected_actions = 0
    for p in alive:
        if p.role_name == "Оборотень": expected_actions += 1
        elif p.role_name == "Предсказатель": expected_actions += 1
        elif p.role_name == "Ведьма": expected_actions += 1
        elif p.role_name == "Маленькая девочка": expected_actions += 1
        elif p.role_name == "Купидон" and game.day_count == 1: expected_actions += 1

    # Wait up to 30s
    for _ in range(30 * 2):
        active_submitted = 0
        for p in alive:
            if p.user_id in game.night_actions:
                if p.role_name in ["Оборотень", "Предсказатель", "Ведьма", "Маленькая девочка"] or (p.role_name == "Купидон" and game.day_count == 1):
                    # Check if Cupid needs more clicks
                    if p.role_name == "Купидон" and game.day_count == 1:
                         if isinstance(game.night_actions[p.user_id], list) and len(game.night_actions[p.user_id]) < 2:
                             continue # still waiting for 2nd lover
                    active_submitted += 1
        if active_submitted >= expected_actions:
            break
        await asyncio.sleep(0.5)
        
    await asyncio.sleep(8)
        
    # Parse night actions
    heals = []
    poison = []
    girl_peeped = False
    girl_id = None
    for k, v in game.night_actions.items():
        if isinstance(v, str) and v.startswith("heal:"):
             heals.append(int(v.split(":")[1]))
        elif isinstance(v, str) and v.startswith("poison:"):
             poison.append(int(v.split(":")[1]))
        elif v == "look":
             girl_peeped = True
             girl_id = k

    # Eval WW vote
    ww_votes = [v for k, v in game.night_actions.items() if game.players[k].role_name == "Оборотень" and isinstance(v, int)]
    target_killed = []
    
    if ww_votes:
        from collections import Counter
        counts = Counter(ww_votes)
        max_votes = max(counts.values())
        candidates = [k for k, v in counts.items() if v == max_votes]
        victim_id = random.choice(candidates)
        if victim_id not in heals:
            target_killed.append(victim_id)
            
    if girl_peeped and girl_id:
        if random.random() < 0.30:
            target_killed.append(girl_id)
            
    if poison:
        target_killed.extend(poison)

    for victim_id in target_killed:
        victim = game.players.get(victim_id)
        if not victim: continue
        if victim.role_name == "Инфицированный" and not victim.is_infected:
            victim.role_name = "Оборотень"
            victim.is_infected = True
        else:
            victim.is_alive = False
            game.night_killed.append(victim_id)
            
    # Process lovers
    additional_killed = []
    for vid in game.night_killed:
        if vid in game.lovers:
            other_lover = [l for l in game.lovers if l != vid][0]
            if other_lover not in game.night_killed and other_lover not in additional_killed:
                victim = game.players.get(other_lover)
                if victim:
                    victim.is_alive = False
                    additional_killed.append(other_lover)
    game.night_killed.extend(additional_killed)

    # Process hunter night death
    for vid in game.night_killed:
        if game.players[vid].role_name == "Охотник":
             alive_now = game.get_alive_players()
             if alive_now:
                 target_id = random.choice(alive_now).user_id
                 victim = game.players.get(target_id)
                 if victim:
                     victim.is_alive = False
                     game.night_killed.append(target_id)
                     
    game.night_actions.clear()
    asyncio.create_task(run_morning_phase(bot, chat_id))
    
async def run_morning_phase(bot: Bot, chat_id: int):
    game = ACTIVE_GAMES.get(chat_id)
    if not game: return
    game.state = "DAY"
    
    killed_names = [game.players[vid].username for vid in game.night_killed]
    text = f"🌅 Утро {game.day_count} дня.\n"
    text += f"💀 Погибли: {', '.join(killed_names)}" if killed_names else "💚 Никто не погиб."
        
    alive_names = [f"• {p.username}" for p in game.get_alive_players()]
    text += f"\n\n👥 В живых ({len(alive_names)}):\n" + "\n".join(alive_names)
    
    await broadcast(bot, game, text, animation=GIFS["DAY"])
    game.night_killed = [] 
    
    if await check_and_handle_victory(bot, game): return
    
    await broadcast(bot, game, "💬 Обсуждение! У вас есть 30 секунд.")
    
    await asyncio.sleep(30)
    asyncio.create_task(run_voting_phase(bot, chat_id))
    
async def run_voting_phase(bot: Bot, chat_id: int):
    game = ACTIVE_GAMES.get(chat_id)
    if not game: return
    game.state = "VOTING"
    game.day_votes = {} 
    
    alive = game.get_alive_players()
    kb = get_player_selection_kb(alive, "day_vote")
    
    votes_text = ""
    for p in alive:
        votes_text += f"\n👤 {p.username} ➡ ⏳ думает..."
        
    try:
        msg = await bot.send_message(
            chat_id, 
            "🗳 Голосование началось! (У каждого 1 голос, Изменить нельзя)\n⚖️ Кого отправим на виселицу?\n" + votes_text, 
            reply_markup=kb
        )
        game.day_vote_group_msg_id = msg.message_id
    except Exception:
        pass
        
    for _ in range(30 * 2): 
        if len(game.day_votes) >= len(alive): break
        await asyncio.sleep(0.5)
        
    await asyncio.sleep(8)
    
    try:
        if hasattr(game, "day_vote_group_msg_id"):
            await bot.edit_message_reply_markup(chat_id, game.day_vote_group_msg_id, reply_markup=None)
    except Exception: pass
    
    if game.day_votes:
        from collections import Counter
        counts = Counter()
        for voter_id, target_id in game.day_votes.items():
            counts[target_id] += 1
        max_votes = max(counts.values())
        candidates = [k for k, v in counts.items() if v == max_votes]
        
        if len(candidates) == 1:
            victim = game.players[candidates[0]]
            victim.is_alive = False
            await broadcast(bot, game, f"💀 Казнён {victim.username} (Роль: {victim.role_name}).", animation=GIFS["EXECUTION"])
            
            # Hunter check
            if victim.role_name == "Охотник":
                alive_now = game.get_alive_players()
                if alive_now:
                    target_id = random.choice(alive_now).user_id
                    victim_hunter = game.players[target_id]
                    victim_hunter.is_alive = False
                    await broadcast(bot, game, f"🔫 Умирая, Охотник ({victim.username}) выстрелил наугад и убил {victim_hunter.username} (Роль: {victim_hunter.role_name})!")
            
            # Lovers check
            if victim.user_id in game.lovers:
                other_lover = [l for l in game.lovers if l != victim.user_id][0]
                victim_lover = game.players[other_lover]
                if victim_lover.is_alive:
                     victim_lover.is_alive = False
                     await broadcast(bot, game, f"💔 Не выдержав горя, {victim_lover.username} лишает себя жизни (Роль: {victim_lover.role_name})!")
            
            if victim.role_name == "Таннер":
                await broadcast(bot, game, "🏆 ПОБЕДА ТАННЕРА! 🏆\nТаннер добился своей казни!")
                return await end_game(bot, game, "TANNER_WIN")
        else:
            await broadcast(bot, game, "⚖️ Ничья! Законопослушные граждане решили никого не вешать.")
    else:
        await broadcast(bot, game, "⚖️ Никто не проголосовал. Город расходится по домам.")
        
    if await check_and_handle_victory(bot, game): return
    asyncio.create_task(run_night_phase(bot, chat_id))
    
async def check_and_handle_victory(bot: Bot, game: GameSession):
    res = game.check_victory()
    if res == "WEREWOLVES_WIN":
        await broadcast(bot, game, "🐺 ПОБЕДА ОБОРОТНЕЙ! У мирных жителей нет шансов...", animation=GIFS["WEREWOLVES_WIN"])
        await end_game(bot, game, "WEREWOLVES_WIN")
        return True
    elif res == "VILLAGERS_WIN":
        await broadcast(bot, game, "🌾 ПОБЕДА МИРНЫХ! В городе не осталось оборотней.", animation=GIFS["VILLAGERS_WIN"])
        await end_game(bot, game, "VILLAGERS_WIN")
        return True
    elif res == "DRAW":
        await broadcast(bot, game, "🤷 НИЧЬЯ! Все мертвы.", animation=GIFS["DRAW"])
        await end_game(bot, game, "DRAW")
        return True
    return False
    
async def end_game(bot: Bot, game: GameSession, reason: str):
    for p in game.players.values():
        is_win = False
        if reason == "WEREWOLVES_WIN" and p.role_name == "Оборотень": is_win = True
        elif reason == "VILLAGERS_WIN" and p.role_name not in ["Оборотень", "Таннер"]: is_win = True
        elif reason == "TANNER_WIN" and p.role_name == "Таннер": is_win = True
        update_user_stats(p.user_id, is_win)
        
    chat_id = game.chat_id
    if chat_id in ACTIVE_GAMES: del ACTIVE_GAMES[chat_id]
    
    await broadcast(bot, game, "🏁 Игра окончена. Создайте лобби заново.", reply_markup=get_start_kb())
