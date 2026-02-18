# Crafting system - pulls materials from inv + bank

from typing import TYPE_CHECKING, Optional, Tuple, List

from .craftable import CRAFTABLES
from .items import ITEMS
from .models import PlayerState, _now

if TYPE_CHECKING:
    from .wilderness import Wilderness

CRAFT_COOLDOWN_SEC = 60


class CraftManager:
    def __init__(self, cog: "Wilderness"):
        self.cog = cog

    def list_craftables(self) -> List[Tuple[str, dict, dict]]:
        """All craftable items as (name, recipe, stats) tuples."""
        results = []
        for name, recipe in CRAFTABLES.items():
            stats = ITEMS.get(name, {})
            results.append((name, recipe, stats))
        return results

    def _total_have(self, p: PlayerState, mat: str) -> int:
        return p.inventory.get(mat, 0) + p.bank.get(mat, 0)

    def check_materials(self, p: PlayerState, item_name: str) -> Tuple[bool, str]:
        """Check if player has all required mats. Returns (ok, msg)."""
        recipe = CRAFTABLES.get(item_name)
        if not recipe:
            return False, f"**{item_name}** is not a craftable item."

        materials = recipe["materials"]
        missing = []
        for mat, needed in materials.items():
            have = self._total_have(p, mat)
            if have < needed:
                missing.append(f"  • **{mat}** — need {needed:,}, have {have:,}")

        if missing:
            msg = f"You're missing materials for **{item_name}**:\n" + "\n".join(missing)
            return False, msg

        return True, ""

    def _consume_material(self, p: PlayerState, mat: str, needed: int) -> None:
        """Takes from inv first, remainder from bank."""
        inv_have = p.inventory.get(mat, 0)
        if inv_have >= needed:
            p.inventory[mat] = inv_have - needed
            if p.inventory[mat] <= 0:
                del p.inventory[mat]
        else:
            # Take everything from inventory, rest from bank
            remainder = needed - inv_have
            if inv_have > 0:
                del p.inventory[mat]
            p.bank[mat] = p.bank.get(mat, 0) - remainder
            if p.bank[mat] <= 0:
                del p.bank[mat]

    def craft(self, p: PlayerState, item_name: str) -> Tuple[bool, str]:
        """Craft an item, consuming mats from inv + bank. Returns (ok, msg)."""
        recipe = CRAFTABLES.get(item_name)
        if not recipe:
            return False, f"**{item_name}** is not a craftable item."

        cd_key = "craft"
        last = p.cd.get(cd_key, 0)
        elapsed = _now() - last
        if elapsed < CRAFT_COOLDOWN_SEC:
            remaining = CRAFT_COOLDOWN_SEC - elapsed
            return False, f"Crafting on cooldown — **{remaining}s** remaining."

        unlock = recipe.get("requires_unlock")
        if unlock and unlock not in (p.slayer_unlocks or []):
            return False, f"You haven't unlocked the ability to craft **{item_name}**."

        ok, msg = self.check_materials(p, item_name)
        if not ok:
            return False, msg

        materials = recipe["materials"]

        for mat, needed in materials.items():
            self._consume_material(p, mat, needed)

        self.cog._add_item(p.inventory, item_name, 1)

        p.cd[cd_key] = _now()

        return True, f"You crafted **{item_name}**!"
