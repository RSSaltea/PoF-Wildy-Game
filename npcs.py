from typing import Dict, Any, List, Tuple

# name, base_hp, tier, min_wildy, npc_type, atk_bonus, def_bonus
NPCS: List[Tuple[str, int, int, int, str, int, int]] = [
    ("Revenant goblin", 50, 1, 1, "revenant", 3, 1),
    ("Revenant knight", 50, 2, 10, "revenant knight", 5, 3),
    ("Chaos fanatic", 90, 3, 20, "chaos_fanatic", 7, 5),
    ("Revenant necromancer", 140, 4, 20, "revenant necro", 10, 0),
    ("Revenant abyssal demon", 140, 4, 35, "revenant demon", 9, 3),
    ("Blighted Cyclops", 120, 4, 35, "blight cyclops", 7, 4),
    ("Abyssal Overlord", 280, 4, 35, "overlord", 11, 7),
    ("Lord Valthyros", 250, 4, 35, "valthyros", 6, 12),
    ("Revenant Archon", 200, 4, 40, "revenant archon", 13, 8),
    ("Zarveth the Veilbreaker", 420, 5, 45, "veilbreaker", 22, 4),
]

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