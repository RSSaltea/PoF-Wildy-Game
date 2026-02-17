# Breaks items down into their component materials

from typing import TYPE_CHECKING, Tuple, List

from .breakdownitems import BREAKDOWNS
from .items import ITEMS
from .models import PlayerState, _now

if TYPE_CHECKING:
    from .wilderness import Wilderness

BREAKDOWN_COOLDOWN_SEC = 60


class BreakdownManager:
    def __init__(self, cog: "Wilderness"):
        self.cog = cog

    def list_breakdowns(self) -> List[Tuple[str, dict, dict]]:
        """All breakdownable items as (name, info, stats) tuples."""
        results = []
        for name, info in BREAKDOWNS.items():
            stats = ITEMS.get(name, {})
            results.append((name, info, stats))
        return results

    def breakdown(self, p: PlayerState, item_name: str) -> Tuple[bool, str]:
        """Break down an item into materials. Returns (ok, msg)."""
        info = BREAKDOWNS.get(item_name)
        if not info:
            return False, f"**{item_name}** cannot be broken down."

        cd_key = "breakdown"
        last = p.cd.get(cd_key, 0)
        elapsed = _now() - last
        if elapsed < BREAKDOWN_COOLDOWN_SEC:
            remaining = BREAKDOWN_COOLDOWN_SEC - elapsed
            return False, f"Breakdown on cooldown — **{remaining}s** remaining."

        have = p.inventory.get(item_name, 0)
        if have < 1:
            return False, f"You don't have **{item_name}** in your inventory."

        results = info["result"]

        p.inventory[item_name] = p.inventory.get(item_name, 0) - 1
        if p.inventory[item_name] <= 0:
            del p.inventory[item_name]

        for mat, qty in results.items():
            self.cog._add_item(p.inventory, mat, qty)

        p.cd[cd_key] = _now()

        result_lines = ", ".join(f"**{m}** x{q:,}" for m, q in results.items())
        return True, f"You broke down **{item_name}** and received: {result_lines}"
