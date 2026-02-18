import discord
import random
from typing import Dict, Optional, Tuple, List, TYPE_CHECKING

import time

from .items import ITEMS, FOOD, EQUIP_SLOT_SET, POTIONS
from .models import PlayerState, clamp

GROUND_ITEM_TTL = 300  # 5 minutes
NOTED_PREFIX = "Noted "
ETHER_WEAPONS = {"Viggora's Chainmace", "Abyssal Chainmace"}

if TYPE_CHECKING:
    from .wilderness import Wilderness

DEFENDER_ORDER = [
    "Bronze Defender",
    "Iron Defender",
    "Steel Defender",
    "Black Defender",
    "Mithril Defender",
    "Adamant Defender",
    "Rune Defender",
]


class InventoryManager:
    def __init__(self, cog: "Wilderness"):
        self.cog = cog


    def is_noted(self, item_name: str) -> bool:
        return item_name.startswith(NOTED_PREFIX)

    def unnote(self, item_name: str) -> str:
        if item_name.startswith(NOTED_PREFIX):
            return item_name[len(NOTED_PREFIX):]
        return item_name

    def note(self, item_name: str) -> str:
        if item_name.startswith(NOTED_PREFIX):
            return item_name
        return NOTED_PREFIX + item_name


    def is_stackable(self, item_name: str) -> bool:
        if self.is_noted(item_name):
            return True
        meta = ITEMS.get(item_name)
        if meta is None:
            return False
        return bool(meta.get("stackable", False))

    def inv_slots_used(self, bag: Dict[str, int]) -> int:
        used = 0
        for name, qty in bag.items():
            if qty <= 0:
                continue
            if name in FOOD:
                used += qty
                continue
            if self.is_stackable(name):
                used += 1
            else:
                used += qty
        return used

    def inv_free_slots(self, bag: Dict[str, int]) -> int:
        max_inv = int(self.cog.config["max_inventory_items"])
        return max(0, max_inv - self.inv_slots_used(bag))

    def slots_needed_to_add(self, bag: Dict[str, int], item: str, qty: int) -> int:
        if qty <= 0:
            return 0
        if item in FOOD:
            return qty
        if self.is_stackable(item):
            return 0 if bag.get(item, 0) > 0 else 1
        return qty

    def player_owns_esspouch(self, p: PlayerState, item: str) -> bool:
        meta = ITEMS.get(item, {})
        if meta.get("type") != "esspouch":
            return False
        return (p.inventory.get(item, 0) + p.bank.get(item, 0)) > 0

    def add_item(self, bag: Dict[str, int], item: str, qty: int):
        if qty <= 0:
            return
        bag[item] = bag.get(item, 0) + qty
        if bag[item] <= 0:
            bag.pop(item, None)

    def remove_item(self, bag: Dict[str, int], item: str, qty: int) -> bool:
        if qty <= 0:
            return False
        have = bag.get(item, 0)
        if have < qty:
            return False
        left = have - qty
        if left <= 0:
            bag.pop(item, None)
        else:
            bag[item] = left
        return True


    def item_slot(self, item_name: str) -> Optional[str]:
        meta = ITEMS.get(item_name)
        if not meta:
            return None
        slot = str(meta.get("type", "")).strip().lower()
        if slot == "mainhand,offhand":
            return "mainhand"
        if slot in EQUIP_SLOT_SET:
            return slot
        return None

    def is_twohanded(self, item_name: str) -> bool:
        meta = ITEMS.get(item_name)
        if not meta:
            return False
        return str(meta.get("type", "")).strip().lower() == "mainhand,offhand"

    def next_defender_drop(self, p: PlayerState) -> Optional[str]:
        """Returns the next defender tier based on currently equipped offhand."""
        equipped = p.equipment.get("offhand")
        if equipped not in DEFENDER_ORDER:
            return DEFENDER_ORDER[0]
        idx = DEFENDER_ORDER.index(equipped)
        if idx + 1 >= len(DEFENDER_ORDER):
            return None
        return DEFENDER_ORDER[idx + 1]

    def equipped_bonus(
        self,
        p: PlayerState,
        *,
        vs_npc: bool,
        chainmace_charged: Optional[bool] = None,
    ) -> Tuple[int, int]:
        atk = 0
        deff = 0

        for item in p.equipment.values():
            meta = ITEMS.get(item, {})
            atk += int(meta.get("atk", 0))
            deff += int(meta.get("def", 0))

            if vs_npc:
                if meta.get("atk_vs_npc") and item in ETHER_WEAPONS:
                    charged = chainmace_charged
                    if charged is None:
                        charged = (p.inventory.get("Revenant ether", 0) >= 3)
                    if not charged:
                        continue
                atk += int(meta.get("atk_vs_npc", 0))

        buffs = getattr(p, "active_buffs", None) or {}
        for buff in buffs.values():
            atk += int(buff.get("atk", 0))
            deff += int(buff.get("def", 0))

        return atk, deff


    def consume_buffs_on_hit(self, p: PlayerState) -> List[str]:
        """Tick buffs, return log lines for any that expire."""
        expired_msgs: List[str] = []
        buffs = getattr(p, "active_buffs", None) or {}
        to_remove = []
        for name, buff in buffs.items():
            buff["remaining_hits"] = int(buff.get("remaining_hits", 0)) - 1
            if buff["remaining_hits"] <= 0:
                to_remove.append(name)
        for name in to_remove:
            buffs.pop(name, None)
            expired_msgs.append(f"🧪 **{name}** has worn off.")
        p.active_buffs = buffs
        return expired_msgs

    def apply_seeping_heal(self, p: PlayerState, damage_dealt: int) -> int:
        """Amulet of Seeping: costs 5 Blood runes per hit, heals 1 + 2% of damage dealt."""
        if damage_dealt <= 0:
            return 0
        if p.equipment.get("amulet") != "Amulet of Seeping":
            return 0

        RUNE_NAME = "Blood rune"
        RUNE_COST = 5

        if int(p.inventory.get(RUNE_NAME, 0)) < RUNE_COST:
            return 0
        if not self.remove_item(p.inventory, RUNE_NAME, RUNE_COST):
            return 0

        max_hp = int(self.cog.config["max_hp"])
        before = int(p.hp)
        heal_amt = 1 + int(damage_dealt * 0.02)
        p.hp = clamp(before + heal_amt, 0, max_hp)
        return int(p.hp) - before

    def best_food_in_inventory(self, p: PlayerState) -> Optional[str]:
        best = None
        best_heal = -1
        for name, meta in FOOD.items():
            heal = int(meta.get("heal", 0))
            if heal <= 0:
                continue
            if p.inventory.get(name, 0) > 0 and heal > best_heal:
                best = name
                best_heal = heal
        return best

    def maybe_auto_eat_after_hit(self, p: PlayerState, your_hp: int) -> Tuple[int, Optional[str], int, int]:
        """Auto-eat when HP is <= (heal + random threshold)."""
        food = self.best_food_in_inventory(p)
        if not food:
            return your_hp, None, 0, 0

        heal = int(FOOD.get(food, {}).get("heal", 0))
        if heal <= 0:
            return your_hp, None, 0, 0

        r_lo, r_hi = self.cog.config.get("auto_eat_extra_range", [1, 10])
        try:
            r_lo = int(r_lo)
            r_hi = int(r_hi)
        except Exception:
            r_lo, r_hi = 1, 10
        if r_hi < r_lo:
            r_hi = r_lo

        extra = random.randint(r_lo, r_hi)
        threshold = heal + extra

        if your_hp > 0 and your_hp <= threshold and p.inventory.get(food, 0) > 0:
            if self.remove_item(p.inventory, food, 1):
                before = your_hp
                your_hp = clamp(your_hp + heal, 0, int(self.cog.config["max_hp"]))
                return your_hp, food, threshold, (your_hp - before)

        return your_hp, None, threshold, 0


    def bank_category_for_item(self, item_name: str) -> str:
        if self.is_noted(item_name):
            item_name = self.unnote(item_name)
        if item_name in FOOD:
            return "Food"

        norm_name = self.cog._norm(item_name)
        for base in POTIONS.keys():
            if norm_name.startswith(self.cog._norm(base)):
                return "Potions"

        meta = ITEMS.get(item_name, {})
        t = str(meta.get("type", "")).lower()

        if t == "mainhand":
            return "Weapons"
        if t in ("helm", "body", "legs", "boots", "cape", "gloves"):
            return "Armour"
        if t == "offhand":
            return "Offhands"
        if t in ("amulet", "ring"):
            return "Jewellery"
        if t == "rune":
            return "Runes"
        if t == "esspouch":
            return "Pouches"

        return "Misc"

    def chunk_lines(self, lines: list, max_chars: int = 950) -> list:
        """Split lines into chunks to fit embed field limits."""
        chunks = []
        cur = ""
        for line in lines:
            if not cur:
                nxt = line
            else:
                nxt = cur + "\n" + line
            if len(nxt) > max_chars:
                chunks.append(cur)
                cur = line
            else:
                cur = nxt
        if cur:
            chunks.append(cur)
        return chunks or ["(none)"]

    def bank_categories_for_user(self, user_id: int) -> List[str]:
        p = self.cog.players.get(int(user_id))
        if not p:
            return ["All"]

        cats = set()
        for item, qty in (p.bank or {}).items():
            if int(qty) <= 0:
                continue
            cats.add(self.bank_category_for_item(item))

        order = ["All", "Food", "Potions", "Weapons", "Armour", "Offhands", "Jewellery", "Misc"]
        present = [c for c in order if c == "All" or c in cats]
        return present or ["All"]

    def bank_embed(self, user: discord.abc.User, category: str) -> discord.Embed:
        p = self.cog._get_player(user)

        items = [(k, int(v)) for k, v in (p.bank or {}).items() if int(v) > 0]
        items.sort(key=lambda kv: self.cog._norm(kv[0]))

        if category != "All":
            items = [(k, v) for (k, v) in items if self.bank_category_for_item(k) == category]

        emb = discord.Embed(
            title=f"🏦 {user.display_name}'s Bank",
            description=f"Category: **{category}**",
        )
        emb.add_field(
            name="🪙 Bank Coins",
            value=f"**{int(p.bank_coins):,}**",
            inline=False,
        )

        if not items:
            emb.add_field(name="Items", value="(none)", inline=False)
            return emb

        lines = [f"• {name} x{qty}" for name, qty in items]
        chunks = self.chunk_lines(lines, max_chars=950)

        if len(chunks) == 1:
            emb.add_field(name="Items", value=chunks[0], inline=False)
        else:
            for i, ch in enumerate(chunks, start=1):
                emb.add_field(name=f"Items ({i}/{len(chunks)})", value=ch, inline=False)

        return emb

    def inv_categories_for_user(self, user_id: int) -> List[str]:
        p = self.cog.players.get(int(user_id))
        if not p:
            return ["All"]

        cats = set()
        for item, qty in (p.inventory or {}).items():
            if int(qty) <= 0:
                continue
            cats.add(self.bank_category_for_item(item))

        order = ["All", "Food", "Potions", "Weapons", "Armour", "Offhands", "Jewellery", "Misc"]
        present = [c for c in order if c == "All" or c in cats]
        return present or ["All"]

    def inv_embed(self, user: discord.abc.User, category: str) -> discord.Embed:
        p = self.cog._get_player(user)

        used = self.inv_slots_used(p.inventory)
        max_inv = int(self.cog.config["max_inventory_items"])

        locked = getattr(p, "locked", None) or []
        locked_norm = {self.cog._norm(x) for x in locked}

        def is_locked_item(name: str) -> bool:
            return self.cog._norm(name) in locked_norm

        items = [(k, int(v)) for k, v in (p.inventory or {}).items() if int(v) > 0]
        items.sort(key=lambda kv: self.cog._norm(kv[0]))

        if category != "All":
            items = [(k, v) for (k, v) in items if self.bank_category_for_item(k) == category]

        emb = discord.Embed(
            title=f"🎒 {user.display_name}'s Inventory",
            description=f"Slots: **{used}/{max_inv}**\nCategory: **{category}**",
        )
        emb.add_field(
            name="🪙 Coins",
            value=f"**{int(p.coins):,}**",
            inline=False,
        )

        if not items:
            emb.add_field(name="Items", value="(none)", inline=False)
            return emb

        lines = []
        for name, qty in items:
            lock_icon = " 🔒" if is_locked_item(name) else ""
            lines.append(f"• {name} x{qty}{lock_icon}")

        chunks = self.chunk_lines(lines, max_chars=950)

        if len(chunks) == 1:
            emb.add_field(name="Items", value=chunks[0], inline=False)
        else:
            for i, ch in enumerate(chunks, start=1):
                emb.add_field(name=f"Items ({i}/{len(chunks)})", value=ch, inline=False)

        return emb


    def is_locked(self, p: PlayerState, item_name: str) -> bool:
        if not item_name:
            return False
        locked = getattr(p, "locked", None) or []
        target = self.cog._norm(item_name)
        return any(self.cog._norm(x) == target for x in locked)

    def locked_pretty(self, p: PlayerState) -> str:
        locked = getattr(p, "locked", None) or []
        if not locked:
            return "(none)"
        return "\n".join(f"- {x}" for x in sorted(locked, key=lambda s: s.lower()))

    def is_blacklisted(self, p: PlayerState, item_name: str) -> bool:
        if not item_name:
            return False
        bl = getattr(p, "blacklist", None) or []
        target = self.cog._norm(item_name)
        base_target = self.cog._norm(self.unnote(item_name)) if self.is_noted(item_name) else None
        return any(
            self.cog._norm(x) == target or (base_target and self.cog._norm(x) == base_target)
            for x in bl
        )

    def record_autodrop(self, auto_drops: Dict[str, int], item: str, qty: int):
        if qty > 0:
            auto_drops[item] = auto_drops.get(item, 0) + qty


    def try_put_item_with_blacklist(
        self,
        p: PlayerState,
        item: str,
        qty: int,
        auto_drops: Dict[str, int],
    ) -> str:
        """If blacklisted, record as auto-drop; otherwise try normal placement."""
        if qty <= 0:
            return "(none)"
        if self.is_blacklisted(p, item):
            self.record_autodrop(auto_drops, item, qty)
            return "(blacklisted - dropped)"
        return self.try_put_item(p, item, qty)

    def try_put_item(self, p: PlayerState, item: str, qty: int) -> str:
        """Add to inventory, respecting slot limits. Overflow is lost."""
        if qty <= 0:
            return "(none)"

        max_inv = int(self.cog.config["max_inventory_items"])
        slots_needed = self.slots_needed_to_add(p.inventory, item, qty)

        if slots_needed == 0:
            self.add_item(p.inventory, item, qty)
            return ""

        used = self.inv_slots_used(p.inventory)
        space = max_inv - used
        if space <= 0:
            return "(inventory full - lost)"

        if self.is_stackable(item) and item not in FOOD:
            if space >= 1:
                self.add_item(p.inventory, item, qty)
                return ""
            return "(inventory full - lost)"

        take = min(space, qty)
        if take > 0:
            self.add_item(p.inventory, item, take)
        rem = qty - take
        if rem > 0:
            return f"(x{take} inv, x{rem} lost)"
        return ""

    def try_put_item_or_ground_with_blacklist(
        self,
        p: PlayerState,
        item: str,
        qty: int,
        auto_drops: Dict[str, int],
    ) -> Tuple[str, int]:
        """If blacklisted, record as auto-drop. Otherwise place in inventory or on ground."""
        if qty <= 0:
            return "(none)", 0
        if self.is_blacklisted(p, item):
            self.record_autodrop(auto_drops, item, qty)
            return "(blacklisted - dropped)", 0
        return self.try_put_item_or_ground(p, item, qty)

    def try_put_item_or_ground(self, p: PlayerState, item: str, qty: int) -> Tuple[str, int]:
        """Add to inventory first. Remainder goes to ground."""
        if qty <= 0:
            return "(none)", 0

        if self.player_owns_esspouch(p, item):
            return "(already owned - dropped)", 0

        if item not in FOOD and self.is_stackable(item):
            if p.inventory.get(item, 0) > 0:
                self.add_item(p.inventory, item, qty)
                return "", 0

        max_inv = int(self.cog.config["max_inventory_items"])
        used = self.inv_slots_used(p.inventory)
        free = max_inv - used
        if free <= 0:
            return "(inventory full - on ground)", qty

        if item not in FOOD and self.is_stackable(item):
            # New stack needs 1 slot (already checked existing stack above)
            self.add_item(p.inventory, item, qty)
            return "", 0

        take = min(free, qty)
        if take > 0:
            self.add_item(p.inventory, item, take)
        rem = qty - take
        if rem > 0:
            return f"(x{take} inv, x{rem} on ground)", rem
        return "", 0


    def prune_ground_items(self, p: PlayerState):
        now = int(time.time())
        p.ground_items = [
            entry for entry in (p.ground_items or [])
            if now - int(entry[2]) < GROUND_ITEM_TTL
        ]

    def active_ground_items(self, p: PlayerState) -> Dict[str, int]:
        self.prune_ground_items(p)
        totals: Dict[str, int] = {}
        for item, qty, _ts in p.ground_items:
            totals[item] = totals.get(item, 0) + int(qty)
        return totals

    def remove_ground_item(self, p: PlayerState, item: str, qty: int):
        remaining = qty
        new_list = []
        for entry in (p.ground_items or []):
            if remaining <= 0 or entry[0] != item:
                new_list.append(entry)
                continue
            entry_qty = int(entry[1])
            if entry_qty <= remaining:
                remaining -= entry_qty
                # skip this entry entirely (consumed)
            else:
                entry[1] = entry_qty - remaining
                remaining = 0
                new_list.append(entry)
        p.ground_items = new_list
