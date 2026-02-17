"""
Player state management for the Wilderness game.

Handles player lifecycle, item resolution, cooldowns, and currency.
Follows the same composition pattern as trade.py.
"""

from typing import Dict, Any, Optional, Tuple, List

from .models import PlayerState, _now, clamp
from .items import ITEMS, FOOD
from .npcs import NPCS


class PlayerManager:
    """
    Manages player state operations and item/NPC resolution.

    The cog must provide:
    - players: Dict[int, PlayerState]
    - config: Dict[str, Any]
    """

    def __init__(self, cog):
        self.cog = cog
        self._item_alias_map: Dict[str, str] = {}

    # ── Item name resolution ─────────────────────────────────────────────────

    def norm(self, s: str) -> str:
        """Normalize string for case-insensitive comparison."""
        return " ".join(str(s).strip().lower().split())

    def build_item_alias_map(self):
        """Build canonical item name lookup map from ITEMS and FOOD aliases."""
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

        # Food + their aliases  ✅ (this is the missing bit)
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
        """Resolve query to canonical item name (supports aliases)."""
        return self._item_alias_map.get(self.norm(query))

    def resolve_from_keys_case_insensitive(self, query: str, keys) -> Optional[str]:
        """Resolve query to an existing key from a dict keys (case-insensitive)."""
        q = self.norm(query)
        for k in keys:
            if self.norm(k) == q:
                return k
        return None

    def resolve_food(self, query: str) -> Optional[str]:
        """
        Resolve food item name (supports aliases).
        Only returns a canonical food name that exists in FOOD.
        """
        canonical = self.resolve_item(query)  # uses the alias map
        if canonical and canonical in FOOD:
            return canonical
        return None

    def resolve_npc(self, query: str) -> Optional[Tuple[str, int, int, int, str, int, int]]:
        """Resolve NPC name to its data tuple."""
        q = self.norm(query)
        for n in NPCS:
            if self.norm(n[0]) == q:
                return n
        return None

    # ── Player lifecycle ──────────────────────────────────────────────────────

    def get_player(self, user) -> PlayerState:
        """Get or create player state, ensuring all fields are initialized."""
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
        """Update player's last action timestamp."""
        p.last_action = _now()

    def full_heal(self, p: PlayerState):
        """Restore player HP to maximum."""
        p.hp = int(self.cog.config["max_hp"])

    # ── Cooldowns ────────────────────────────────────────────────────────────

    def cd_ready(self, p: PlayerState, key: str, seconds: int) -> Tuple[bool, int]:
        """Check if cooldown has elapsed. Returns (ready, remaining_seconds)."""
        last = int(p.cd.get(key, 0))
        now = _now()
        if now - last >= seconds:
            return True, 0
        return False, seconds - (now - last)

    def set_cd(self, p: PlayerState, key: str):
        """Start a cooldown at the current time."""
        p.cd[key] = _now()

    # ── Currency ─────────────────────────────────────────────────────────────

    def total_coins(self, p: PlayerState) -> int:
        """Get total coins (inventory + bank)."""
        return int(p.coins) + int(p.bank_coins)

    def spend_coins(self, p: PlayerState, amount: int) -> bool:
        """
        Spend coins from inventory first, then bank.
        Returns True if payment was successful.
        """
        amount = int(amount)
        if amount <= 0:
            return True

        total = self.total_coins(p)
        if total < amount:
            return False

        # Spend inventory coins first
        take_inv = min(int(p.coins), amount)
        p.coins -= take_inv
        amount -= take_inv

        # Then bank coins
        if amount > 0:
            p.bank_coins -= amount

        return True
