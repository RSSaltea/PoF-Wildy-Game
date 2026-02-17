import random
from typing import Dict, Any, Optional, Tuple, List, TYPE_CHECKING

from .items import ITEMS
from .models import PlayerState, parse_chance

if TYPE_CHECKING:
    from .wilderness import Wilderness


class LootManager:
    def __init__(self, cog: "Wilderness"):
        self.cog = cog

    def band(self, wildy_level: int) -> str:
        if wildy_level <= 10:
            return "shallow"
        if wildy_level <= 20:
            return "mid"
        if wildy_level <= 35:
            return "deep"
        return "hell"

    def roll_pick_one(self, entries: List[Dict[str, Any]]) -> Optional[Tuple[str, int]]:
        """Roll each entry, keep the rarest success."""
        successes: List[Tuple[float, str, int, bool]] = []
        for e in entries or []:
            try:
                item = str(e.get("item", "")).strip()
                if not item:
                    continue
                ch = parse_chance(e.get("chance", 0))
                if ch <= 0:
                    continue
                if random.random() <= ch:
                    lo = int(e.get("min", 1))
                    hi = int(e.get("max", lo))
                    if hi < lo:
                        hi = lo
                    qty = random.randint(lo, hi)
                    noted = bool(e.get("noted", False))
                    if qty > 0:
                        successes.append((ch, item, qty, noted))
            except Exception:
                continue
        if not successes:
            return None
        min_ch = min(s[0] for s in successes)
        rarest = [s for s in successes if s[0] == min_ch]
        _, item, qty, noted = random.choice(rarest)
        if noted and not bool(ITEMS.get(item, {}).get("stackable", False)):
            item = "Noted " + item
        return item, qty

    def loot_for_level(self, wildy_level: int) -> Optional[Tuple[str, int]]:
        band = self.band(wildy_level)
        table = self.cog.config.get("loot_tables", {}).get(band, [])
        return self.roll_pick_one(table)

    def npc_roll_table_for_player(self, p: PlayerState, npc_type: str, key: str) -> Optional[Tuple[str, int]]:
        npc_drop = self.cog.config.get("npc_drops", {}).get(npc_type, {}) or {}
        entries = (npc_drop.get(key, []) or [])

        if npc_type == "blight cyclops" and key == "unique":
            next_def = self.cog._next_defender_drop(p)
            if not next_def:
                return None

            chosen_entry = None
            for e in entries:
                if str(e.get("item", "")).strip() == next_def:
                    chosen_entry = e
                    break

            if not chosen_entry:
                return None

            return self.roll_pick_one([chosen_entry])

        return self.roll_pick_one(entries)

    def npc_roll_table(self, npc_type: str, key: str) -> Optional[Tuple[str, int]]:
        npc_drop = self.cog.config.get("npc_drops", {}).get(npc_type, {})
        entries = npc_drop.get(key, [])
        return self.roll_pick_one(entries)

    def npc_roll_pet(self, npc_type: str) -> Optional[str]:
        npc_drop = self.cog.config.get("npc_drops", {}).get(npc_type, {})
        entries = npc_drop.get("pet", []) or []
        for e in entries:
            try:
                item = str(e.get("item", "")).strip()
                if not item:
                    continue
                ch = parse_chance(e.get("chance", 0))
                if ch > 0 and random.random() <= ch:
                    return item
            except Exception:
                continue
        return None

    def npc_coin_roll(self, npc_type: str) -> int:
        npc_drop = self.cog.config.get("npc_drops", {}).get(npc_type, {})
        lo, hi = npc_drop.get("coins_range", [0, 0])
        try:
            lo = int(lo)
            hi = int(hi)
        except Exception:
            lo, hi = 0, 0
        if hi < lo:
            hi = lo
        return random.randint(lo, hi) if hi > 0 else 0
