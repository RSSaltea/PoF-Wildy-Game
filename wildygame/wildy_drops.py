
from typing import Dict, Any, List

CHEST_COIN_RANGE = [5000, 25000]

CHEST_REWARDS: List[Dict[str, Any]] = [
    {"item": "Dragon platebody", "min": 1, "max": 1, "chance": "1/100"},
]

SHOP_ITEMS: Dict[str, int] = {
    "Starter Sword": 0,
    "Starter Platebody": 0,
    "Mysterious key": 100000,
    "Lobster": 1000,
    "Shark": 2000,
}

LOOT_TABLES: Dict[str, List[Dict[str, Any]]] = {
    "shallow": [
        {"item": "Nature rune", "min": 1, "max": 3, "chance": "1/2"},
        {"item": "Law rune", "min": 1, "max": 2, "chance": "1/2"},
        {"item": "Lobster", "min": 1, "max": 4, "chance": "1/2"},
        {"item": "Shark", "min": 1, "max": 2, "chance": "1/6"},
        {"item": "Rune scimitar", "min": 1, "max": 1, "chance": "1/50"},
        {"item": "Rune chainbody", "min": 1, "max": 1, "chance": "1/80"},
        {"item": "Rune med helm", "min": 1, "max": 1, "chance": "1/40"},
        {"item": "Rune sq shield", "min": 1, "max": 1, "chance": "1/45"},
    ],
    "mid": [
        {"item": "Death rune", "min": 5, "max": 25, "chance": "1/2"},
        {"item": "Blood rune", "min": 3, "max": 20, "chance": "1/2"},
        {"item": "Shark", "min": 1, "max": 4, "chance": "1/2"},
        {"item": "Rune platebody", "min": 1, "max": 1, "chance": "1/80"},
        {"item": "Rune platelegs", "min": 1, "max": 1, "chance": "1/80"},
        {"item": "Rune full helm", "min": 1, "max": 1, "chance": "1/80"},
        {"item": "Dragon dagger", "min": 1, "max": 1, "chance": "1/120"},
    ],
    "deep": [
        {"item": "Blood rune", "min": 20, "max": 90, "chance": "1/2"},
        {"item": "Shark", "min": 2, "max": 10, "chance": "1/2"},
        {"item": "Manta Ray", "min": 1, "max": 4, "chance": "1/3"},
        {"item": "Dragon scimitar", "min": 1, "max": 1, "chance": "1/250"},
        {"item": "Dragon platelegs", "min": 1, "max": 1, "chance": "1/400"},
        {"item": "Dragon boots", "min": 1, "max": 1, "chance": "1/400"},
        {"item": "Abyssal Whip", "min": 1, "max": 1, "chance": "1/500"},
        {"item": "Ancient Emblem", "min": 1, "max": 1, "chance": "1/300"},
    ],
}
