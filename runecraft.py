# Runecrafting - craft runes from pure essence

from typing import TYPE_CHECKING, Tuple, Optional

from .items import ITEMS
from .models import PlayerState, _now

if TYPE_CHECKING:
    from .wilderness import Wilderness

RC_COOLDOWN_SEC = 25
RC_BLOCKED = {"Bone Rune"}


class RunecraftManager:
    def __init__(self, cog: "Wilderness"):
        self.cog = cog

    def resolve_rune(self, query: str) -> Optional[str]:
        resolved = self.cog._resolve_item(query)
        if resolved:
            meta = ITEMS.get(resolved, {})
            if meta.get("type") == "rune" and resolved not in RC_BLOCKED:
                return resolved
        norm_q = self.cog._norm(query)
        for name, meta in ITEMS.items():
            if meta.get("type") == "rune" and name not in RC_BLOCKED and self.cog._norm(name) == norm_q:
                return name
        return None

    def _pouch_bonus(self, p: PlayerState) -> int:
        """Extra essence from pouches in inv."""
        bonus = 0
        for item_name, qty in p.inventory.items():
            if qty <= 0:
                continue
            meta = ITEMS.get(item_name, {})
            if meta.get("type") == "esspouch":
                bonus += int(meta.get("essstorage", 0)) * int(qty)
        return bonus

    def _count_non_pouch_items(self, p: PlayerState) -> int:
        from .items import FOOD
        slots = 0
        for item_name, qty in p.inventory.items():
            if qty <= 0:
                continue
            meta = ITEMS.get(item_name, {})
            if meta.get("type") == "esspouch":
                # Pouches take slots but we count them
                slots += int(qty)
                continue
            if item_name in FOOD:
                slots += int(qty)
            elif meta.get("stackable") or self.cog._is_stackable(item_name):
                slots += 1
            else:
                slots += int(qty)
        return slots

    def is_busy(self, p: PlayerState) -> Tuple[bool, int, str]:
        """Returns (busy, secs_left, rune_name)."""
        last = int(p.cd.get("runecraft", 0))
        rune = p.cd.get("runecraft_rune", "")
        elapsed = _now() - last
        if elapsed < RC_COOLDOWN_SEC and rune:
            return True, RC_COOLDOWN_SEC - elapsed, str(rune)
        return False, 0, ""

    def craft_runes(self, p: PlayerState, rune_name: str) -> Tuple[bool, str]:
        """Craft runes using pure ess from bank. Returns (ok, msg)."""
        meta = ITEMS.get(rune_name, {})
        if meta.get("type") != "rune":
            return False, f"**{rune_name}** is not a rune."

        busy, left, busy_rune = self.is_busy(p)
        if busy:
            return False, f"You are currently crafting **{busy_rune}**. It will take you **{left}s** to return."

        max_slots = int(self.cog.config.get("max_inventory_items", 28))
        used_slots = self._count_non_pouch_items(p)
        free_slots = max(0, max_slots - used_slots)

        pouch_bonus = self._pouch_bonus(p)

        total_essence_capacity = free_slots + pouch_bonus
        if total_essence_capacity <= 0:
            return False, "You have no free inventory space to carry Pure essence."

        bank_essence = p.bank.get("Pure essence", 0)
        if bank_essence <= 0:
            return False, "You don't have any **Pure essence** in your bank."

        essence_used = min(total_essence_capacity, bank_essence)

        multiplier = int(meta.get("multiplier", 0))
        runes_produced = essence_used * (1 + multiplier)

        p.bank["Pure essence"] = p.bank.get("Pure essence", 0) - essence_used
        if p.bank["Pure essence"] <= 0:
            del p.bank["Pure essence"]

        p.bank[rune_name] = p.bank.get(rune_name, 0) + runes_produced

        p.cd["runecraft"] = _now()
        p.cd["runecraft_rune"] = rune_name

        return True, (
            f"You craft **{runes_produced:,} {rune_name}** from **{essence_used:,} Pure essence**.\n"
            f"The runes have been deposited into your bank.\n"
            f"You will be busy for **{RC_COOLDOWN_SEC}s**."
        )
