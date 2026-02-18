from typing import Dict, Any, List

# Optional slayer keys: slayer_level, slayer_xp, task_range
_IMG_BASE = "https://raw.githubusercontent.com/RSSaltea/PoF-Wildy-Game/main/docs/images/"

NPCS: List[Dict[str, Any]] = [
    {"name": "Revenant goblin", "hp": 50, "tier": 1, "min_wildy": 1, "npc_type": "revenant",
     "atk": 3, "def": 1, "slayer_level": 1, "slayer_xp": 15, "task_range": [15, 30],
     "image": _IMG_BASE + "revenant%20goblin.png"},
    {"name": "Revenant knight", "hp": 50, "tier": 2, "min_wildy": 10, "npc_type": "revenant knight",
     "atk": 5, "def": 3, "slayer_level": 10, "slayer_xp": 30, "task_range": [15, 25],
     "image": _IMG_BASE + "revenant%20knight.png"},
    {"name": "Chaos fanatic", "hp": 90, "tier": 3, "min_wildy": 20, "npc_type": "chaos_fanatic",
     "atk": 7, "def": 5, "slayer_level": 15, "slayer_xp": 50, "task_range": [10, 20],
     "image": _IMG_BASE + "chaos%20fanatic.png"},
    {"name": "Revenant necromancer", "hp": 140, "tier": 4, "min_wildy": 20, "npc_type": "revenant necro",
     "atk": 10, "def": 0, "slayer_level": 25, "slayer_xp": 75, "task_range": [10, 20],
     "image": _IMG_BASE + "revenant%20necromancer.png"},
    {"name": "Revenant abyssal demon", "hp": 140, "tier": 4, "min_wildy": 35, "npc_type": "revenant demon",
     "atk": 9, "def": 3, "slayer_level": 30, "slayer_xp": 75, "task_range": [10, 20],
     "image": _IMG_BASE + "revenant%20abyssal%20demon.png"},
    {"name": "Blighted Cyclops", "hp": 120, "tier": 4, "min_wildy": 35, "npc_type": "blight cyclops",
     "atk": 7, "def": 4, "slayer_level": 25, "slayer_xp": 60, "task_range": [10, 20],
     "image": _IMG_BASE + "blighted%20cyclops.png"},
    {"name": "Abyssal Overlord", "hp": 280, "tier": 4, "min_wildy": 35, "npc_type": "overlord",
     "atk": 11, "def": 7, "slayer_level": 40, "slayer_xp": 150, "task_range": [8, 15],
     "image": _IMG_BASE + "abyssal%20overlord.png"},
    {"name": "Lord Valthyros", "hp": 250, "tier": 4, "min_wildy": 35, "npc_type": "valthyros",
     "atk": 6, "def": 12, "slayer_level": 40, "slayer_xp": 130, "task_range": [8, 15],
     "image": _IMG_BASE + "lord%20valthyros.png"},
    {"name": "Revenant Archon", "hp": 200, "tier": 4, "min_wildy": 40, "npc_type": "revenant archon",
     "atk": 13, "def": 8, "slayer_level": 45, "slayer_xp": 110, "task_range": [8, 15],
     "image": _IMG_BASE + "revenant%20archon.png"},
    {"name": "Zarveth the Veilbreaker", "hp": 420, "tier": 5, "min_wildy": 45, "npc_type": "veilbreaker",
     "atk": 22, "def": 4, "slayer_level": 55, "slayer_xp": 220, "task_range": [5, 12],
     "image": _IMG_BASE + "zarveth%20the%20veilbreaker.png"},
    {"name": "Masked Figure", "hp": 460, "tier": 5, "min_wildy": 47, "npc_type": "masked_figure",
     "atk": 16, "def": 10, "slayer_level": 70, "slayer_xp": 240, "task_range": [6, 14],
     "image": _IMG_BASE + "masked%20figure.png"},
    {"name": "Netharis the Undying", "hp": 550, "tier": 5, "min_wildy": 50, "npc_type": "netharis",
     "atk": 18, "def": 14, "slayer_level": 85, "slayer_xp": 300, "task_range": [3, 10],
     "image": _IMG_BASE + "netharis%20the%20undying.png"},
]

# Auto-generated from NPCS — do not edit manually
NPC_SLAYER: Dict[str, Dict[str, Any]] = {}
for _npc in NPCS:
    if "slayer_level" in _npc:
        NPC_SLAYER[_npc["npc_type"]] = {
            "level": _npc["slayer_level"],
            "xp": _npc["slayer_xp"],
            "task_range": _npc["task_range"],
        }

NPC_DROPS: Dict[str, Dict[str, Any]] = {
    "revenant": {
        "coins_range": [0, 1000],
        "unique": [
            {"item": "Mysterious key", "min": 1, "max": 1, "chance": "1/50"},
            {"item": "Revenant Relic Shard", "min": 1, "max": 1, "chance": "1/500"},
            {"item": "Revenant Totem", "min": 1, "max": 1, "chance": "1/750", "noted": True},
            {"item": "Viggora's Chainmace", "min": 1, "max": 1, "chance": "1/2000"},
        ],
        "pet": [
            {"item": "Tiny Revenant", "min": 1, "max": 1, "chance": "1/1000"},
        ],
        "loot": [
            {"item": "Revenant ether", "min": 10, "max": 40, "chance": "1/2"},
            {"item": "Bracelet of ethereum", "min": 1, "max": 1, "chance": "1/250"},
        ],
    },
    "revenant knight": {
        "coins_range": [0, 2000],
        "unique": [
            {"item": "Mysterious key", "min": 1, "max": 1, "chance": "1/25"},
            {"item": "Revenant Relic Shard", "min": 1, "max": 1, "chance": "1/250"},
            {"item": "Revenant Totem", "min": 1, "max": 1, "chance": "1/500", "noted": True},
            {"item": "Viggora's Chainmace", "min": 1, "max": 1, "chance": "1/1000"},
        ],
        "pet": [
            {"item": "Tiny Revenant", "min": 1, "max": 1, "chance": "1/1000"},
        ],
        "loot": [
            {"item": "Revenant ether", "min": 10, "max": 80, "chance": "1/2"},
            {"item": "Bracelet of ethereum", "min": 1, "max": 1, "chance": "1/250"},
        ],
    },
    "revenant necro": {
        "coins_range": [0, 2500],
        "unique": [
            {"item": "Mysterious key", "min": 1, "max": 1, "chance": "1/10"},
            {"item": "Revenant Relic Shard", "min": 1, "max": 1, "chance": "1/250"},
            {"item": "Revenant Totem", "min": 1, "max": 1, "chance": "1/500", "noted": True},
            {"item": "Viggora's Chainmace", "min": 1, "max": 1, "chance": "1/900"},
        ],
        "pet": [
            {"item": "Tiny Revenant", "min": 1, "max": 1, "chance": "1/1000"},
        ],
        "loot": [
            {"item": "Revenant ether", "min": 30, "max": 70, "chance": "1/2"},
            {"item": "Bracelet of ethereum", "min": 1, "max": 1, "chance": "1/250"},
            {"item": "Death Guard", "min": 1, "max": 1, "chance": "1/150"},
            {"item": "Skull Lantern", "min": 1, "max": 1, "chance": "1/150"},
        ],
    },
    "revenant demon": {
        "coins_range": [0, 3000],
        "unique": [
            {"item": "Mysterious key", "min": 1, "max": 1, "chance": "1/20"},
            {"item": "Revenant Relic Shard", "min": 1, "max": 1, "chance": "1/200"},
            {"item": "Revenant Totem", "min": 1, "max": 1, "chance": "1/450", "noted": True},
            {"item": "Viggora's Chainmace", "min": 1, "max": 1, "chance": "1/850"},
        ],
        "pet": [
            {"item": "Tiny Revenant", "min": 1, "max": 1, "chance": "1/1000"},
        ],
        "loot": [
            {"item": "Revenant ether", "min": 30, "max": 160, "chance": "1/2"},
            {"item": "Pure essence", "min": 10, "max": 90, "chance": "1/10", "noted": True},
            {"item": "Bracelet of ethereum", "min": 1, "max": 1, "chance": "1/250"},
            {"item": "Abyssal Whip", "min": 1, "max": 1, "chance": "1/200"},
        ],
    },
    "chaos_fanatic": {
        "coins_range": [0, 4000],
        "unique": [
            {"item": "Dragon 2h sword", "min": 1, "max": 1, "chance": "1/100"},
            {"item": "Ancient Effigy", "min": 1, "max": 1, "chance": "1/300"},
            {"item": "Bracelet of Slayer Aggression", "min": 1, "max": 1, "chance": "1/850", "on_task_chance": "1/250"},
        ],
        "pet": [
            {"item": "Baby Chaos Fanatic", "min": 1, "max": 1, "chance": "1/1000"},
        ],
        "loot": [
            {"item": "Chaos rune", "min": 20, "max": 120, "chance": "1/2"},
            {"item": "Uncut sapphire", "min": 1, "max": 3, "chance": "1/3", "noted": True},
            {"item": "Uncut emerald", "min": 1, "max": 2, "chance": "1/5", "noted": True},
        ],
    },
    "blight cyclops": {
        "coins_range": [0, 50],
        "unique": [
            {"item": "Bronze Defender", "min": 1, "max": 1, "chance": "1/50"},
            {"item": "Iron Defender", "min": 1, "max": 1, "chance": "1/50"},
            {"item": "Steel Defender", "min": 1, "max": 1, "chance": "1/50"},
            {"item": "Black Defender", "min": 1, "max": 1, "chance": "1/50"},
            {"item": "Mithril Defender", "min": 1, "max": 1, "chance": "1/50"},
            {"item": "Adamant Defender", "min": 1, "max": 1, "chance": "1/50"},
            {"item": "Rune Defender", "min": 1, "max": 1, "chance": "1/50"},
        ],
        "loot": [
            {"item": "Chaos rune", "min": 20, "max": 120, "chance": "1/2"},
            {"item": "Rune dagger", "min": 1, "max": 1, "chance": "1/20", "noted": True},
            {"item": "Cyclops Eye", "min": 1, "max": 1, "chance": "1/50"},
        ],
    },
    "overlord": {
        "coins_range": [0, 25000],
        "unique": [
            {"item": "Ancient Emblem", "min": 1, "max": 1, "chance": "1/250", "noted": True},
            {"item": "Wristwraps of the Damned", "min": 1, "max": 1, "chance": "1/300"},
        ],
        "pet": [
            {"item": "Mini Overlord", "min": 1, "max": 1, "chance": "1/2000"},
        ],
        "loot": [
            {"item": "Abyssal ash", "min": 5, "max": 25, "chance": "1/2"},
            {"item": "Abyssal charm", "min": 1, "max": 2, "chance": "1/4"},
            {"item": "Overlord core fragment", "min": 1, "max": 1, "chance": "1/6"},
            {"item": "Pure essence", "min": 20, "max": 120, "chance": "1/10", "noted": True},
            {"item": "Small pouch", "min": 1, "max": 1, "chance": "1/10"},
            {"item": "Medium pouch", "min": 1, "max": 1, "chance": "1/50"},
            {"item": "Large pouch", "min": 1, "max": 1, "chance": "1/100"},
            {"item": "Blood rune", "min": 5, "max": 40, "chance": "1/40"},
            {"item": "Abyssal Whip", "min": 1, "max": 1, "chance": "1/100"},
        ],
        "special": [
            {"item": "Abyssal Scourge", "min": 1, "max": 1, "chance": "1/200"},
        ],
    },
    "veilbreaker": {
        "coins_range": [0, 45000],
        "unique": [
            {"item": "Ancient Emblem", "min": 1, "max": 1, "chance": "1/50"},
            {"item": "Veilbreaker", "min": 1, "max": 1, "chance": "1/300"},
            {"item": "Zarveth's Ascendant Platebody", "min": 1, "max": 1, "chance": "1/400"},
            {"item": "Zarveth's Ascendant Platelegs", "min": 1, "max": 1, "chance": "1/400"},
            {"item": "Zarveth's Ascendant Mask", "min": 1, "max": 1, "chance": "1/400"},
        ],
        "pet": [
            {"item": "Zarvethy", "min": 1, "max": 1, "chance": "1/2000"},
        ],
        "loot": [
            {"item": "Veilfruit", "min": 2, "max": 7, "chance": "1/2"},
            {"item": "Veilfruit", "min": 5, "max": 24, "chance": "1/10", "noted": True},
            {"item": "Blood rune", "min": 4, "max": 80, "chance": "1/5"},
            {"item": "Super Strength (4)", "min": 1, "max": 1, "chance": "1/12"},
            {"item": "Uncut ruby", "min": 1, "max": 3, "chance": "1/5", "noted": True},
        ],
    },
    "revenant archon": {
        "coins_range": [0, 8000],
        "unique": [
            {"item": "Bone key", "min": 1, "max": 1, "chance": "1/50"},
            {"item": "Revenant Relic Shard", "min": 1, "max": 1, "chance": "1/150"},
            {"item": "Revenant Totem", "min": 1, "max": 1, "chance": "1/300", "noted": True},
            {"item": "Viggora's Chainmace", "min": 1, "max": 1, "chance": "1/850"},
        ],
        "pet": [
            {"item": "Tiny Revenant", "min": 1, "max": 1, "chance": "1/750"},
        ],
        "loot": [
            {"item": "Revenant ether", "min": 50, "max": 200, "chance": "1/2"},
            {"item": "Cursed Bone", "min": 1, "max": 1, "chance": "1/20"},
            {"item": "Bracelet of ethereum", "min": 1, "max": 1, "chance": "1/150"},
            {"item": "Ancient Emblem", "min": 1, "max": 1, "chance": "1/400", "noted": True},
        ],
    },
    "masked_figure": {
        "coins_range": [0, 30000],
        "unique": [
            {"item": "Black Mask", "min": 1, "max": 1, "chance": "1/1000", "on_task_chance": "1/250"},
            {"item": "Shadow Veil", "min": 1, "max": 1, "chance": "1/400"},
        ],
        "loot": [
            {"item": "Death rune", "min": 20, "max": 100, "chance": "1/2"},
            {"item": "Uncut sapphire", "min": 1, "max": 3, "chance": "1/4", "noted": True},
            {"item": "Abyssal charm", "min": 5, "max": 15, "chance": "1/4"},
            {"item": "Veilfruit", "min": 2, "max": 5, "chance": "1/5"},
            {"item": "Gold Bar", "min": 1, "max": 1, "chance": "1/30"},
        ],
    },
    "netharis": {
        "coins_range": [0, 50000],
        "unique": [
            {"item": "Shroud of the Undying", "min": 1, "max": 1, "chance": "1/500"},
            {"item": "Giant pouch", "min": 1, "max": 1, "chance": "1/100"},
        ],
        "pet": [
            {"item": "Lil' Undying", "min": 1, "max": 1, "chance": "1/3000"},
        ],
        "loot": [
            {"item": "Pure essence", "min": 30, "max": 150, "chance": "1/5", "noted": True},
            {"item": "Uncut diamond", "min": 1, "max": 3, "chance": "1/15", "noted": True},
            {"item": "Uncut dragonstone", "min": 1, "max": 2, "chance": "1/20", "noted": True},
        ],
    },
    "valthyros": {
        "coins_range": [0, 20000],
        "unique": [
            {"item": "Ancient Emblem", "min": 1, "max": 1, "chance": "1/300", "noted": True},
            {"item": "Amulet of Seeping", "min": 1, "max": 1, "chance": "1/300"},
        ],
        "pet": [
            {"item": "Splat", "min": 1, "max": 1, "chance": "1/1000"},
        ],
        "loot": [
            {"item": "Blood rune", "min": 40, "max": 250, "chance": "1/2"},
            {"item": "Ring of Valthyros", "min": 1, "max": 1, "chance": "1/100"},
        ],
    },
}