from typing import Dict, Any, List, Tuple

# name, base_hp, tier, min_wildy, npc_type, atk_bonus, def_bonus
NPCS: List[Tuple[str, int, int, int, str, int, int]] = [
    ("Revenant goblin", 50, 1, 1, "revenant", 3, 1),
    ("Revenant knight", 50, 2, 10, "revenant knight", 5, 3),
    ("Chaos fanatic", 90, 3, 20, "chaos_fanatic", 7, 5),
    ("Revenant necromancer", 140, 4, 20, "revenant necro", 10, 0),
    ("Revenant abyssal demon", 140, 4, 35, "revenant demon", 9, 3),
    ("Abyssal Overlord", 280, 4, 35, "overlord", 11, 7),
    ("Lord Valthyros", 250, 4, 35, "valthyros", 6, 12),
    ("Zarveth the Veilbreaker", 420, 5, 45, "veilbreaker", 22, 4),
]

NPC_DROPS: Dict[str, Dict[str, Any]] = {
    "revenant": {
        "coins_range": [0, 1000],
        "unique": [
            {"item": "Mysterious key", "min": 1, "max": 1, "chance": "1/50"},
            {"item": "Revenant Relic Shard", "min": 1, "max": 1, "chance": "1/500"},
            {"item": "Revenant Totem", "min": 1, "max": 1, "chance": "1/750"},
        ],
        "pet": [
            {"item": "Tiny Revenant", "min": 1, "max": 1, "chance": "1/1000"},
        ],
        "loot": [
            {"item": "Revenant ether", "min": 10, "max": 40, "chance": "1/2"},
            {"item": "Bracelet of ethereum", "min": 1, "max": 1, "chance": "1/250"},
            {"item": "Viggora's Chainmace", "min": 1, "max": 1, "chance": "1/2000"},
        ],
    },
    "revenant knight": {
        "coins_range": [0, 2000],
        "unique": [
            {"item": "Mysterious key", "min": 1, "max": 1, "chance": "1/25"},
            {"item": "Revenant Relic Shard", "min": 1, "max": 1, "chance": "1/250"},
            {"item": "Revenant Totem", "min": 1, "max": 1, "chance": "1/500"},
        ],
        "pet": [
            {"item": "Tiny Revenant", "min": 1, "max": 1, "chance": "1/1000"},
        ],
        "loot": [
            {"item": "Revenant ether", "min": 10, "max": 80, "chance": "1/2"},
            {"item": "Bracelet of ethereum", "min": 1, "max": 1, "chance": "1/250"},
            {"item": "Viggora's Chainmace", "min": 1, "max": 1, "chance": "1/1000"},
        ],
    },
    "revenant necro": {
        "coins_range": [0, 2500],
        "unique": [
            {"item": "Mysterious key", "min": 1, "max": 1, "chance": "1/10"},
            {"item": "Revenant Relic Shard", "min": 1, "max": 1, "chance": "1/250"},
            {"item": "Revenant Totem", "min": 1, "max": 1, "chance": "1/500"},
        ],
        "pet": [
            {"item": "Tiny Revenant", "min": 1, "max": 1, "chance": "1/1000"},
        ],
        "loot": [
            {"item": "Revenant ether", "min": 30, "max": 70, "chance": "1/2"},
            {"item": "Bracelet of ethereum", "min": 1, "max": 1, "chance": "1/250"},
            {"item": "Death Guard", "min": 1, "max": 1, "chance": "1/150"},
            {"item": "Skull Lantern", "min": 1, "max": 1, "chance": "1/150"},
            {"item": "Viggora's Chainmace", "min": 1, "max": 1, "chance": "1/900"},
        ],
    },
    "revenant demon": {
        "coins_range": [0, 3000],
        "unique": [
            {"item": "Mysterious key", "min": 1, "max": 1, "chance": "1/20"},
            {"item": "Revenant Relic Shard", "min": 1, "max": 1, "chance": "1/200"},
            {"item": "Revenant Totem", "min": 1, "max": 1, "chance": "1/450"},
        ],
        "pet": [
            {"item": "Tiny Revenant", "min": 1, "max": 1, "chance": "1/1000"},
        ],
        "loot": [
            {"item": "Revenant ether", "min": 30, "max": 160, "chance": "1/2"},
            {"item": "Bracelet of ethereum", "min": 1, "max": 1, "chance": "1/250"},
            {"item": "Abyssal Whip", "min": 1, "max": 1, "chance": "1/200"},
            {"item": "Viggora's Chainmace", "min": 1, "max": 1, "chance": "1/850"},
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
            {"item": "Uncut sapphire", "min": 1, "max": 3, "chance": "1/3"},
            {"item": "Uncut emerald", "min": 1, "max": 2, "chance": "1/5"},
        ],
    },
    "overlord": {
        "coins_range": [0, 25000],
        "unique": [
            {"item": "Ancient Emblem", "min": 1, "max": 1, "chance": "1/250"},
            {"item": "Wristwraps of the Damned", "min": 1, "max": 1, "chance": "1/300"},
        ],
        "pet": [
            {"item": "Mini Overlord", "min": 1, "max": 1, "chance": "1/2000"},
        ],
        "loot": [
            {"item": "Abyssal ash", "min": 5, "max": 25, "chance": "1/2"},
            {"item": "Abyssal charm", "min": 1, "max": 2, "chance": "1/4"},
            {"item": "Overlord core fragment", "min": 1, "max": 1, "chance": "1/6"},
            {"item": "Blood rune", "min": 1, "max": 40, "chance": "1/40"},
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
            {"item": "Blood rune", "min": 4, "max": 80, "chance": "1/5"},
            {"item": "Super Strength Potion (4)", "min": 1, "max": 2, "chance": "1/4"},
        ],
    },
    "valthyros": {
        "coins_range": [0, 20000],
        "unique": [
            {"item": "Ancient Emblem", "min": 1, "max": 1, "chance": "1/300"},
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
