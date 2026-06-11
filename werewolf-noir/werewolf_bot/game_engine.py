import random
from roles import ROLE_MAP, ALL_ROLES_POOL, ACTIVE_ROLES_POOL

class GamePlayer:
    def __init__(self, user_id, username):
        self.user_id = user_id
        self.username = username
        self.role_name = None
        self.role_instance = None
        self.is_alive = True
        self.in_love_with = None
        self.is_infected = False

class GameSession:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.players = {}  # user_id -> GamePlayer
        self.state = "LOBBY"  # LOBBY, DAY, NIGHT, VOTING
        self.day_count = 0
        self.creator_id = None
        self.werewolves_votes = {}
        self.night_actions = {}
        self.day_votes = {}
        self.ww_msg_ids = {}
        self.day_vote_msg_ids = {}
        self.witch_heal_used = False
        self.witch_poison_used = False
        self.night_killed = []
        self.night_healed = []
        self.lovers = []

    def get_alive_players(self):
        return [p for p in self.players.values() if p.is_alive]

    def get_alive_werewolves(self):
        return [p for p in self.get_alive_players() if p.role_name == "Оборотень"]

    def assign_roles(self, next_roles_dict):
        alive = self.get_alive_players()
        num_werewolves = max(1, len(alive) // 4)
        
        roles_to_distribute = []
        
        # Consider shop items (next_roles)
        for p in alive:
            if p.user_id in next_roles_dict and next_roles_dict[p.user_id]:
                r = next_roles_dict[p.user_id]
                roles_to_distribute.append(r)
            else:
                roles_to_distribute.append(None)
                
        # Fill missing with standard distribution
        werewolves_added = roles_to_distribute.count("Оборотень")
        while werewolves_added < num_werewolves:
            for i in range(len(roles_to_distribute)):
                if roles_to_distribute[i] is None:
                    roles_to_distribute[i] = "Оборотень"
                    werewolves_added += 1
                    break

        for i in range(len(roles_to_distribute)):
             if roles_to_distribute[i] is None:
                 roles_to_distribute[i] = random.choice(["Обыватель", "Обыватель", "Ведьма", "Предсказатель", "Купидон", "Маленькая девочка", "Охотник", "Таннер", "Инфицированный"])

        random.shuffle(roles_to_distribute)
        
        for p, role in zip(alive, roles_to_distribute):
            p.role_name = role
            p.role_instance = ROLE_MAP[role]()

    def check_victory(self):
        alive_players = self.get_alive_players()
        if not alive_players:
             return "DRAW"

        alive_werewolves = self.get_alive_werewolves()
        tanners_dead = [p for p in self.players.values() if p.role_name == "Таннер" and not p.is_alive]
        
        # This is basic victory condition
        if len(alive_werewolves) >= len(alive_players) / 2:
            return "WEREWOLVES_WIN"
        elif len(alive_werewolves) == 0:
            return "VILLAGERS_WIN"
        return None

ACTIVE_GAMES = {} # chat_id -> GameSession
