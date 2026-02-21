from typing import Dict, Any

from .items import ITEM_EFFECTS
from .npcs import NPC_DROPS
from .wildy_drops import CHEST_COIN_RANGE, CHEST_REWARDS, SHOP_ITEMS, LOOT_TABLES

DEFAULT_CONFIG: Dict[str, Any] = {
    "prefix": "!",
    "starting_coins": 1000,
    "starting_hp": 99,
    "max_hp": 99,
    "venture_cooldown_sec": 20,
    "attack_cooldown_sec": 20,
    "teleport_cooldown_sec": 20,
    "bank_cooldown_sec": 5,
    "pvp_total_timeout_sec": 6 * 60,
    "max_inventory_items": 28,
    "coins_item_name": "Coins",
    "deep_wildy_level_cap": 50,
    "auto_eat_extra_range": [1, 10],

    "item_effects": ITEM_EFFECTS,

    "chest_coin_range": CHEST_COIN_RANGE,
    "chest_rewards": CHEST_REWARDS,
    "shop_items": SHOP_ITEMS,
    "loot_tables": LOOT_TABLES,

    "npc_drops": NPC_DROPS,
}
