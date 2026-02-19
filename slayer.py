# Slayer system - tasks, XP, points, shop

import math
import random
from typing import TYPE_CHECKING, Tuple, Optional, List, Dict, Any

from .npcs import NPCS, NPC_SLAYER
from .models import PlayerState

if TYPE_CHECKING:
    from .wilderness import Wilderness

# OSRS XP table - xp_for_level[L] = XP needed to reach level L
_XP_TABLE: List[int] = [0, 0]  # index 0 unused; level 1 = 0 XP
_total = 0
for _n in range(1, 126):
    _total += math.floor(_n + 300 * (2 ** (_n / 7)))
    _XP_TABLE.append(math.floor(_total / 4))

MAX_SLAYER_LEVEL = 120
MAX_SLAYER_BLOCKS = 3
SLAYER_BLOCK_COST = 500

SLAYER_SHOP = {
    "slayer_helmet": {
        "name": "Slayer Helmet Unlock",
        "cost": 2500,
        "description": "Unlocks the ability to craft the Slayer Helmet.",
    },
}


class SlayerManager:
    def __init__(self, cog: "Wilderness"):
        self.cog = cog

    def xp_for_level(self, level: int) -> int:
        level = max(1, min(level, len(_XP_TABLE) - 1))
        return _XP_TABLE[level]

    def level_for_xp(self, xp: int) -> int:
        xp = max(0, int(xp))
        for lvl in range(MAX_SLAYER_LEVEL, 0, -1):
            if xp >= _XP_TABLE[lvl]:
                return lvl
        return 1

    def get_slayer_level(self, p: PlayerState) -> int:
        return self.level_for_xp(int(p.slayer_xp or 0))

    def xp_to_next(self, p: PlayerState) -> Tuple[int, int]:
        """Returns (current_xp, xp_needed_for_next_level). If max level, next = current."""
        lvl = self.get_slayer_level(p)
        current = int(p.slayer_xp or 0)
        if lvl >= MAX_SLAYER_LEVEL:
            return current, current
        return current, self.xp_for_level(lvl + 1)

    def npc_slayer_info(self, npc_type: str) -> Optional[Dict[str, Any]]:
        return NPC_SLAYER.get(npc_type)

    def can_receive_xp(self, p: PlayerState, npc_type: str) -> bool:
        info = NPC_SLAYER.get(npc_type)
        if not info:
            return False
        return self.get_slayer_level(p) >= info["level"]

    def is_on_task(self, p: PlayerState, npc_type: str) -> bool:
        task = p.slayer_task
        if not task:
            return False
        return task.get("npc_type") == npc_type and int(task.get("remaining", 0)) > 0

    def task_points_reward(self, tasks_done: int) -> int:
        if tasks_done > 0 and tasks_done % 500 == 0:
            return 280
        if tasks_done > 0 and tasks_done % 100 == 0:
            return 140
        if tasks_done > 0 and tasks_done % 40 == 0:
            return 80
        if tasks_done > 0 and tasks_done % 10 == 0:
            return 20
        return 5

    def on_npc_kill(self, p: PlayerState, npc_type: str) -> Tuple[int, bool, int]:
        """Handle slayer XP and task progress on kill.
        Returns (xp_gained, task_completed, points_earned).
        """
        xp_gained = 0
        task_completed = False
        points_earned = 0

        task = p.slayer_task
        on_task = task and task.get("npc_type") == npc_type and int(task.get("remaining", 0)) > 0

        if on_task:
            info = NPC_SLAYER.get(npc_type)
            if info and self.get_slayer_level(p) >= info["level"]:
                xp_gained = int(info["xp"])
                p.slayer_xp = int(p.slayer_xp or 0) + xp_gained

            task["remaining"] = int(task["remaining"]) - 1
            if task["remaining"] <= 0:
                task_completed = True
                p.slayer_tasks_done = int(p.slayer_tasks_done or 0) + 1
                points_earned = self.task_points_reward(p.slayer_tasks_done)
                p.slayer_points = int(p.slayer_points or 0) + points_earned
                p.slayer_task = None

        return xp_gained, task_completed, points_earned

    def assign_task(self, p: PlayerState) -> Tuple[bool, str]:
        if p.slayer_task and int(p.slayer_task.get("remaining", 0)) > 0:
            t = p.slayer_task
            return False, f"You already have a task: Kill **{t['remaining']}/{t['total']} {t['npc']}**."

        slayer_lvl = self.get_slayer_level(p)
        blocked = set(p.slayer_blocked or [])
        eligible = []
        for npc in NPCS:
            npc_type = npc["npc_type"]
            info = NPC_SLAYER.get(npc_type)
            if not info:
                continue
            if npc_type in blocked:
                continue
            if slayer_lvl >= info["level"]:
                eligible.append(npc)

        if not eligible:
            return False, "No monsters available for your slayer level."

        # Weight by slayer level — higher level NPCs are more likely to be assigned
        weights = [NPC_SLAYER[npc["npc_type"]]["level"] for npc in eligible]
        chosen = random.choices(eligible, weights=weights, k=1)[0]
        npc_name = chosen["name"]
        npc_type = chosen["npc_type"]
        info = NPC_SLAYER[npc_type]
        lo, hi = info["task_range"]
        count = random.randint(lo, hi)

        p.slayer_task = {
            "npc": npc_name,
            "npc_type": npc_type,
            "total": count,
            "remaining": count,
        }

        return True, npc_name

    def skip_task(self, p: PlayerState) -> Tuple[bool, str]:
        if not p.slayer_task or int(p.slayer_task.get("remaining", 0)) <= 0:
            return False, "You don't have an active task to skip."

        cost = 30
        points = int(p.slayer_points or 0)
        if points < cost:
            return False, f"You need **{cost}** slayer points to skip. You have **{points}**."

        old_task = p.slayer_task["npc"]
        p.slayer_points = points - cost
        p.slayer_task = None
        return True, f"Skipped task: **{old_task}**. Cost **{cost}** points."

    def buy_shop_item(self, p: PlayerState, item_key: str) -> Tuple[bool, str]:
        shop_item = SLAYER_SHOP.get(item_key)
        if not shop_item:
            return False, "That item doesn't exist in the slayer shop."

        cost = shop_item["cost"]
        points = int(p.slayer_points or 0)

        if item_key in (p.slayer_unlocks or []):
            return False, f"You've already purchased **{shop_item['name']}**."

        if points < cost:
            return False, f"You need **{cost}** slayer points. You have **{points}**."

        p.slayer_points = points - cost
        if p.slayer_unlocks is None:
            p.slayer_unlocks = []
        p.slayer_unlocks.append(item_key)
        return True, f"Purchased **{shop_item['name']}** for **{cost}** points!"

    def block_npc(self, p: PlayerState, npc_name: str) -> Tuple[bool, str]:
        if p.slayer_blocked is None:
            p.slayer_blocked = []

        # Resolve npc_name to npc_type
        matched = None
        for npc in NPCS:
            if npc["name"].lower() == npc_name.lower():
                matched = npc
                break
        if not matched:
            for npc in NPCS:
                if npc_name.lower() in npc["name"].lower():
                    matched = npc
                    break
        if not matched:
            return False, f"Unknown NPC: **{npc_name}**"

        npc_type = matched["npc_type"]
        if npc_type in p.slayer_blocked:
            return False, f"**{matched['name']}** is already on your block list."

        if len(p.slayer_blocked) >= MAX_SLAYER_BLOCKS:
            return False, f"Your block list is full (**{MAX_SLAYER_BLOCKS}/{MAX_SLAYER_BLOCKS}**). Remove one first."

        points = int(p.slayer_points or 0)
        if points < SLAYER_BLOCK_COST:
            return False, f"You need **{SLAYER_BLOCK_COST}** slayer points to block. You have **{points}**."

        p.slayer_points = points - SLAYER_BLOCK_COST
        p.slayer_blocked.append(npc_type)
        return True, f"Blocked **{matched['name']}** for **{SLAYER_BLOCK_COST}** points. ({len(p.slayer_blocked)}/{MAX_SLAYER_BLOCKS})"

    def unblock_npc(self, p: PlayerState, npc_name: str) -> Tuple[bool, str]:
        if not p.slayer_blocked:
            return False, "Your block list is empty."

        # Resolve npc_name to npc_type
        matched = None
        for npc in NPCS:
            if npc["npc_type"] in p.slayer_blocked and npc["name"].lower() == npc_name.lower():
                matched = npc
                break
        if not matched:
            for npc in NPCS:
                if npc["npc_type"] in p.slayer_blocked and npc_name.lower() in npc["name"].lower():
                    matched = npc
                    break
        if not matched:
            return False, f"**{npc_name}** is not on your block list."

        p.slayer_blocked.remove(matched["npc_type"])
        return True, f"Removed **{matched['name']}** from your block list."
