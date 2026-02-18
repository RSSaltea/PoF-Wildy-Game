# Player state, item resolution, cooldowns, currency

from typing import Dict, Any, Optional, Tuple, List

from .models import PlayerState, _now, clamp
from .items import ITEMS, FOOD
from .npcs import NPCS


class PlayerManager:

    def __init__(self, cog):
        self.cog = cog
        self._item_alias_map: Dict[str, str] = {}

    def norm(self, s: str) -> str:
        return " ".join(str(s).strip().lower().split())

    def build_item_alias_map(self):
        m: Dict[str, str] = {}

        def add(alias: str, canonical: str):
            a = self.norm(alias)
            if not a:
                return
            if a not in m:
                m[a] = canonical

        # Items + their aliases
        for canonical, meta in ITEMS.items():
            add(canonical, canonical)
            aliases = meta.get("aliases")
            if isinstance(aliases, str):
                for part in aliases.split(","):
                    add(part.strip(), canonical)
            elif isinstance(aliases, (list, tuple)):
                for part in aliases:
                    add(str(part).strip(), canonical)

        # Food aliases
        for canonical, meta in FOOD.items():
            add(canonical, canonical)
            aliases = meta.get("aliases")
            if isinstance(aliases, str):
                for part in aliases.split(","):
                    add(part.strip(), canonical)
            elif isinstance(aliases, (list, tuple)):
                for part in aliases:
                    add(str(part).strip(), canonical)

        self._item_alias_map = m

    def resolve_item(self, query: str) -> Optional[str]:
        return self._item_alias_map.get(self.norm(query))

    def resolve_from_keys_case_insensitive(self, query: str, keys) -> Optional[str]:
        q = self.norm(query)
        for k in keys:
            if self.norm(k) == q:
                return k
        return None

    def resolve_food(self, query: str) -> Optional[str]:
        canonical = self.resolve_item(query)  # uses the alias map
        if canonical and canonical in FOOD:
            return canonical
        return None

    def resolve_npc(self, query: str) -> Optional[Dict[str, Any]]:
        q = self.norm(query)
        for n in NPCS:
            if self.norm(n["name"]) == q:
                return n
        return None

    def get_player(self, user) -> PlayerState:
        p = self.cog.players.get(user.id)
        if p is None:
            p = PlayerState(user_id=user.id)
            self.cog.players[user.id] = p

        p.inventory = p.inventory or {}
        p.active_buffs = p.active_buffs or {}
        p.bank = p.bank or {}
        p.risk = p.risk or {}
        p.equipment = p.equipment or {}
        p.uniques = p.uniques or {}
        p.pets = p.pets or []
        p.pet_counts = getattr(p, "pet_counts", None) or {}
        p.cd = p.cd or {}
        p.locked = getattr(p, "locked", None) or []
        p.blacklist = getattr(p, "blacklist", None) or []
        if getattr(p, "started", None) is None:
            p.started = False
        if not getattr(p, "last_action", 0):
            p.last_action = _now()
        p.hp = clamp(int(p.hp), 0, int(self.cog.config["max_hp"]))
        return p

    def touch(self, p: PlayerState):
        p.last_action = _now()

    def full_heal(self, p: PlayerState):
        p.hp = int(self.cog.config["max_hp"])

    def cd_ready(self, p: PlayerState, key: str, seconds: int) -> Tuple[bool, int]:
        last = int(p.cd.get(key, 0))
        now = _now()
        if now - last >= seconds:
            return True, 0
        return False, seconds - (now - last)

    def set_cd(self, p: PlayerState, key: str):
        p.cd[key] = _now()

    def total_coins(self, p: PlayerState) -> int:
        return int(p.coins) + int(p.bank_coins)

    def spend_coins(self, p: PlayerState, amount: int) -> bool:
        """Spend coins (inv first, then bank). Returns True on success."""
        amount = int(amount)
        if amount <= 0:
            return True

        total = self.total_coins(p)
        if total < amount:
            return False

        take_inv = min(int(p.coins), amount)
        p.coins -= take_inv
        amount -= take_inv

        if amount > 0:
            p.bank_coins -= amount

        return True
