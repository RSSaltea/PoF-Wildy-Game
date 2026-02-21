from typing import Dict, Any, List

# Optional slayer keys: slayer_level, slayer_xp, task_range
_IMG_BASE = "https://raw.githubusercontent.com/RSSaltea/PoF-Wildy-Game/main/docs/images/"

NPCS: List[Dict[str, Any]] = [
    # ── Tier 1 ──
    {"name": "Revenant goblin", "hp": 50, "tier": 1, "min_wildy": 1, "npc_type": "revenant",
     "stance": "stab", "str_melee": 12, "d_stab": 4, "d_slash": 4, "d_crush": 4, "d_range": 4, "slayer_level": 1, "slayer_xp": 18, "task_range": [15, 30],
     "image": _IMG_BASE + "revenant%20goblin.png"},
    {"name": "Revenant imp", "hp": 40, "tier": 1, "min_wildy": 1, "npc_type": "revenant imp",
     "stance": "range", "str_range": 10, "d_range": 8, "d_magic": -4, "slayer_level": 1, "slayer_xp": 14, "task_range": [15, 30]},
    {"name": "Wandering Warlock", "hp": 35, "tier": 1, "min_wildy": 1, "npc_type": "wandering_warlock",
     "stance": "magic", "str_magic": 8, "d_stab": 4, "d_slash": 4, "d_magic": 8, "slayer_level": 1, "slayer_xp": 12, "task_range": [15, 30]},
    {"name": "Cursed Spirit", "hp": 45, "tier": 1, "min_wildy": 1, "npc_type": "cursed_spirit",
     "stance": "necro", "str_necro": 6, "d_necro": 8, "slayer_level": 1, "slayer_xp": 14, "task_range": [15, 30]},
    {"name": "Feral Scorpion", "hp": 40, "tier": 1, "min_wildy": 1, "npc_type": "feral_scorpion",
     "stance": "crush", "str_melee": 10, "d_stab": 4, "d_slash": 4, "d_crush": 8, "d_magic": -4, "slayer_level": 1, "slayer_xp": 13, "task_range": [15, 30]},
    # ── Tier 2 ──
    {"name": "Revenant knight", "hp": 50, "tier": 2, "min_wildy": 10, "npc_type": "revenant knight",
     "stance": "slash", "str_melee": 20, "d_stab": 12, "d_slash": 12, "d_crush": 12, "d_magic": -4, "d_range": 8, "slayer_level": 10, "slayer_xp": 36, "task_range": [15, 30],
     "image": _IMG_BASE + "revenant%20knight.png"},
    {"name": "Revenant pyromancer", "hp": 60, "tier": 2, "min_wildy": 10, "npc_type": "revenant pyromancer",
     "stance": "magic", "str_magic": 18, "d_stab": 4, "d_slash": 4, "d_magic": 16, "d_range": 12, "slayer_level": 10, "slayer_xp": 32, "task_range": [15, 30]},
    {"name": "Corrupted Ranger", "hp": 55, "tier": 2, "min_wildy": 10, "npc_type": "corrupted_ranger",
     "stance": "range", "str_range": 16, "d_magic": -4, "d_range": 8, "slayer_level": 8, "slayer_xp": 28, "task_range": [15, 30]},
    {"name": "Shade", "hp": 65, "tier": 2, "min_wildy": 10, "npc_type": "shade",
     "stance": "necro", "str_necro": 14, "d_stab": 4, "d_slash": 4, "d_necro": 16, "slayer_level": 10, "slayer_xp": 30, "task_range": [15, 30]},
    {"name": "Infernal Imp", "hp": 60, "tier": 2, "min_wildy": 10, "npc_type": "infernal_imp",
     "stance": "crush", "str_melee": 18, "d_stab": 8, "d_slash": 8, "d_crush": 12, "d_magic": -4, "d_range": 4, "slayer_level": 8, "slayer_xp": 26, "task_range": [15, 30]},
    # ── Tier 3 ──
    {"name": "Chaos fanatic", "hp": 90, "tier": 3, "min_wildy": 20, "npc_type": "chaos_fanatic",
     "stance": "magic", "str_magic": 28, "d_stab": 8, "d_slash": 8, "d_crush": 4, "d_magic": 20, "d_range": 16, "slayer_level": 15, "slayer_xp": 60, "task_range": [10, 20],
     "image": _IMG_BASE + "chaos%20fanatic.png"},
    {"name": "Phantom Archer", "hp": 80, "tier": 3, "min_wildy": 20, "npc_type": "phantom_archer",
     "stance": "range", "str_range": 24, "d_stab": 4, "d_slash": 4, "d_magic": -8, "d_range": 20, "slayer_level": 15, "slayer_xp": 50, "task_range": [10, 20]},
    {"name": "Risen Bonecaller", "hp": 100, "tier": 3, "min_wildy": 25, "npc_type": "risen_bonecaller",
     "stance": "necro", "str_necro": 22, "d_stab": 8, "d_slash": 8, "d_crush": 4, "d_magic": 8, "d_range": 4, "d_necro": 24, "slayer_level": 18, "slayer_xp": 55, "task_range": [10, 20]},
    {"name": "Windstrider", "hp": 120, "tier": 3, "min_wildy": 22, "npc_type": "windstrider",
     "stance": "range", "str_range": 32, "d_stab": 8, "d_slash": 8, "d_crush": 4, "d_magic": -8, "d_range": 24, "slayer_level": 20, "slayer_xp": 60, "task_range": [10, 20]},
    {"name": "Infernal Warlock", "hp": 130, "tier": 3, "min_wildy": 24, "npc_type": "infernal_warlock",
     "stance": "magic", "str_magic": 36, "d_stab": 12, "d_slash": 12, "d_crush": 8, "d_magic": 20, "d_range": 4, "slayer_level": 22, "slayer_xp": 65, "task_range": [10, 20]},
    # ── Tier 4 ──
    {"name": "Revenant necromancer", "hp": 140, "tier": 4, "min_wildy": 20, "npc_type": "revenant necro",
     "stance": "necro", "str_necro": 40, "slayer_level": 25, "slayer_xp": 90, "task_range": [20, 40],
     "image": _IMG_BASE + "revenant%20necromancer.png"},
    {"name": "Revenant abyssal demon", "hp": 140, "tier": 4, "min_wildy": 35, "npc_type": "revenant demon",
     "stance": "slash", "str_melee": 36, "d_stab": 12, "d_slash": 12, "d_crush": 12, "d_magic": -4, "d_range": 8, "slayer_level": 30, "slayer_xp": 90, "task_range": [20, 40],
     "image": _IMG_BASE + "revenant%20abyssal%20demon.png"},
    {"name": "Blighted Cyclops", "hp": 120, "tier": 4, "min_wildy": 35, "npc_type": "blight cyclops",
     "stance": "crush", "str_melee": 28, "d_stab": 16, "d_slash": 16, "d_crush": 12, "d_magic": -4, "d_range": 12, "slayer_level": 25, "slayer_xp": 72, "task_range": [20, 40],
     "image": _IMG_BASE + "blighted%20cyclops.png"},
    {"name": "Abyssal Overlord", "hp": 280, "tier": 4, "min_wildy": 35, "npc_type": "overlord",
     "stance": "crush", "str_melee": 44, "d_stab": 28, "d_slash": 28, "d_crush": 24, "d_magic": -8, "d_range": 24, "slayer_level": 40, "slayer_xp": 180, "task_range": [40, 80],
     "image": _IMG_BASE + "abyssal%20overlord.png"},
    {"name": "Lord Valthyros", "hp": 250, "tier": 4, "min_wildy": 35, "npc_type": "valthyros",
     "stance": "magic", "str_magic": 24, "d_stab": 16, "d_slash": 16, "d_crush": 8, "d_magic": 48, "d_range": 32, "slayer_level": 40, "slayer_xp": 156, "task_range": [40, 80],
     "image": _IMG_BASE + "lord%20valthyros.png"},
    {"name": "Revenant Archon", "hp": 200, "tier": 4, "min_wildy": 40, "npc_type": "revenant archon",
     "stance": "slash", "str_melee": 52, "d_stab": 32, "d_slash": 32, "d_crush": 28, "d_magic": -8, "d_range": 24, "slayer_level": 45, "slayer_xp": 132, "task_range": [40, 80],
     "image": _IMG_BASE + "revenant%20archon.png"},
    {"name": "Hollow Warden", "hp": 220, "tier": 4, "min_wildy": 32, "npc_type": "hollow_warden",
     "stance": "crush", "str_melee": 42, "d_stab": 20, "d_slash": 20, "d_crush": 24, "d_magic": -8, "d_range": 16, "slayer_level": 40, "slayer_xp": 140, "task_range": [30, 60]},
    # ── Tier 5 ──
    {"name": "Zarveth the Veilbreaker", "hp": 420, "tier": 5, "min_wildy": 45, "npc_type": "veilbreaker",
     "stance": "slash", "str_melee": 88, "d_stab": 8, "d_slash": 8, "d_crush": 12, "d_magic": 8, "d_range": 4, "d_necro": 16, "slayer_level": 55, "slayer_xp": 264, "task_range": [60, 120],
     "image": _IMG_BASE + "zarveth%20the%20veilbreaker.png"},
    {"name": "Masked Figure", "hp": 460, "tier": 5, "min_wildy": 47, "npc_type": "masked_figure",
     "stance": "stab", "str_melee": 64, "d_stab": 40, "d_slash": 40, "d_crush": 36, "d_magic": -12, "d_range": 32, "slayer_level": 70, "slayer_xp": 288, "task_range": [60, 120],
     "image": _IMG_BASE + "masked%20figure.png"},
    {"name": "Duskwalker", "hp": 480, "tier": 5, "min_wildy": 47, "npc_type": "duskwalker",
     "stance": "range", "str_range": 72, "d_stab": 20, "d_slash": 20, "d_crush": 12, "d_magic": -16, "d_range": 48, "d_necro": 8, "slayer_level": 65, "slayer_xp": 300, "task_range": [60, 120]},
    {"name": "Emberlord Kael", "hp": 500, "tier": 5, "min_wildy": 48, "npc_type": "emberlord",
     "stance": "magic", "str_magic": 80, "d_stab": 16, "d_slash": 16, "d_crush": 8, "d_magic": 56, "d_range": 12, "d_necro": 12, "slayer_level": 75, "slayer_xp": 330, "task_range": [60, 120]},
    {"name": "Gravekeeper Azriel", "hp": 520, "tier": 5, "min_wildy": 49, "npc_type": "gravekeeper",
     "stance": "necro", "str_necro": 76, "d_stab": 24, "d_slash": 24, "d_crush": 16, "d_magic": 24, "d_range": 16, "d_necro": 48, "slayer_level": 70, "slayer_xp": 320, "task_range": [60, 120]},
    {"name": "Netharis the Undying", "hp": 550, "tier": 5, "min_wildy": 50, "npc_type": "netharis",
     "stance": "necro", "str_necro": 72, "d_stab": 28, "d_slash": 28, "d_crush": 40, "d_magic": 32, "d_range": 16, "d_necro": 56, "slayer_level": 85, "slayer_xp": 360, "task_range": [90, 140],
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
            {"item": "Revenant Relic Shard", "min": 1, "max": 1, "chance": "1/500"},
            {"item": "Revenant Totem", "min": 1, "max": 1, "chance": "1/750", "noted": True},
            {"item": "Viggora's Chainmace", "min": 1, "max": 1, "chance": "1/2000", "on_task_chance": "1/1000"},
        ],
        "pet": [
            {"item": "Tiny Revenant", "min": 1, "max": 1, "chance": "1/1000"},
        ],
        "loot": [
            {"item": "Revenant ether", "min": 10, "max": 40, "chance": "1/2"},
            {"item": "Bracelet of ethereum", "min": 1, "max": 1, "chance": "1/250"},
            {"item": "Mysterious key", "min": 1, "max": 1, "chance": "1/50"},
        ],
    },
    "revenant imp": {
        "coins_range": [0, 800],
        "unique": [
            {"item": "Revenant Relic Shard", "min": 1, "max": 1, "chance": "1/600"},
            {"item": "Rotwood shortbow", "min": 1, "max": 1, "chance": "1/150"},
        ],
        "pet": [
            {"item": "Tiny Revenant", "min": 1, "max": 1, "chance": "1/1200"},
        ],
        "loot": [
            {"item": "Revenant ether", "min": 5, "max": 30, "chance": "1/2"},
            {"item": "Bronze arrows", "min": 15, "max": 50, "chance": "1/2"},
            {"item": "Iron arrows", "min": 5, "max": 20, "chance": "1/5"},
            {"item": "Air rune", "min": 5, "max": 20, "chance": "1/3"},
            {"item": "Mysterious key", "min": 1, "max": 1, "chance": "1/60"},
        ],
    },
    "wandering_warlock": {
        "coins_range": [0, 600],
        "unique": [
            {"item": "Galestaff", "min": 1, "max": 1, "chance": "1/150"},
        ],
        "loot": [
            {"item": "Air rune", "min": 5, "max": 15, "chance": "1/2"},
            {"item": "Water rune", "min": 5, "max": 15, "chance": "1/3"},
            {"item": "Earth rune", "min": 3, "max": 10, "chance": "1/4"},
            {"item": "Fire rune", "min": 3, "max": 10, "chance": "1/5"},
            {"item": "Mysterious key", "min": 1, "max": 1, "chance": "1/60"},
        ],
    },
    "cursed_spirit": {
        "coins_range": [0, 700],
        "loot": [
            {"item": "Bone Rune", "min": 3, "max": 10, "chance": "1/3"},
            {"item": "Death rune", "min": 3, "max": 10, "chance": "1/4"},
            {"item": "Cursed Bone", "min": 1, "max": 1, "chance": "1/12"},
            {"item": "Chaos rune", "min": 3, "max": 10, "chance": "1/3"},
            {"item": "Mysterious key", "min": 1, "max": 1, "chance": "1/60"},
        ],
    },
    "feral_scorpion": {
        "coins_range": [0, 500],
        "loot": [
            {"item": "Bronze arrows", "min": 10, "max": 30, "chance": "1/2"},
            {"item": "Iron arrows", "min": 5, "max": 15, "chance": "1/3"},
            {"item": "Steel arrows", "min": 3, "max": 8, "chance": "1/5"},
            {"item": "Mysterious key", "min": 1, "max": 1, "chance": "1/60"},
        ],
    },
    "revenant knight": {
        "coins_range": [0, 2000],
        "unique": [
            {"item": "Revenant Relic Shard", "min": 1, "max": 1, "chance": "1/250"},
            {"item": "Revenant Totem", "min": 1, "max": 1, "chance": "1/500", "noted": True},
            {"item": "Viggora's Chainmace", "min": 1, "max": 1, "chance": "1/1000", "on_task_chance": "1/750"},
        ],
        "pet": [
            {"item": "Tiny Revenant", "min": 1, "max": 1, "chance": "1/1000"},
        ],
        "loot": [
            {"item": "Revenant ether", "min": 10, "max": 80, "chance": "1/2"},
            {"item": "Bracelet of ethereum", "min": 1, "max": 1, "chance": "1/250"},
            {"item": "Mysterious key", "min": 1, "max": 1, "chance": "1/25"},
        ],
    },
    "revenant pyromancer": {
        "coins_range": [0, 2000],
        "unique": [
            {"item": "Revenant Relic Shard", "min": 1, "max": 1, "chance": "1/300"},
            {"item": "Tidestaff", "min": 1, "max": 1, "chance": "1/200"},
            {"item": "Thornweave body", "min": 1, "max": 1, "chance": "1/250"},
            {"item": "Thornweave legs", "min": 1, "max": 1, "chance": "1/250"},
        ],
        "pet": [
            {"item": "Tiny Revenant", "min": 1, "max": 1, "chance": "1/1000"},
        ],
        "loot": [
            {"item": "Revenant ether", "min": 10, "max": 60, "chance": "1/2"},
            {"item": "Fire rune", "min": 10, "max": 40, "chance": "1/2"},
            {"item": "Water rune", "min": 10, "max": 40, "chance": "1/3"},
            {"item": "Earth rune", "min": 10, "max": 30, "chance": "1/3"},
            {"item": "Air rune", "min": 10, "max": 30, "chance": "1/3"},
            {"item": "Galestaff", "min": 1, "max": 1, "chance": "1/50"},
            {"item": "Thornweave helm", "min": 1, "max": 1, "chance": "1/300"},
            {"item": "Thornweave boots", "min": 1, "max": 1, "chance": "1/300"},
            {"item": "Thornweave gloves", "min": 1, "max": 1, "chance": "1/300"},
            {"item": "Mysterious key", "min": 1, "max": 1, "chance": "1/30"},
        ],
    },
    "corrupted_ranger": {
        "coins_range": [0, 1800],
        "unique": [
            {"item": "Whisperwood bow", "min": 1, "max": 1, "chance": "1/200"},
            {"item": "Scaleweave body", "min": 1, "max": 1, "chance": "1/300"},
            {"item": "Scaleweave chaps", "min": 1, "max": 1, "chance": "1/300"},
        ],
        "loot": [
            {"item": "Iron arrows", "min": 10, "max": 40, "chance": "1/2"},
            {"item": "Steel arrows", "min": 5, "max": 20, "chance": "1/3"},
            {"item": "Mithril arrows", "min": 3, "max": 10, "chance": "1/5"},
            {"item": "Adamant arrows", "min": 1, "max": 5, "chance": "1/8"},
            {"item": "Scaleweave coif", "min": 1, "max": 1, "chance": "1/350"},
            {"item": "Scaleweave boots", "min": 1, "max": 1, "chance": "1/350"},
            {"item": "Scaleweave vambraces", "min": 1, "max": 1, "chance": "1/350"},
            {"item": "Mysterious key", "min": 1, "max": 1, "chance": "1/30"},
        ],
    },
    "shade": {
        "coins_range": [0, 2000],
        "unique": [
            {"item": "Ghostweave robetop", "min": 1, "max": 1, "chance": "1/300"},
            {"item": "Ghostweave robeskirt", "min": 1, "max": 1, "chance": "1/300"},
        ],
        "loot": [
            {"item": "Bone Rune", "min": 5, "max": 15, "chance": "1/2"},
            {"item": "Death rune", "min": 5, "max": 15, "chance": "1/3"},
            {"item": "Cursed Bone", "min": 1, "max": 2, "chance": "1/10"},
            {"item": "Chaos rune", "min": 5, "max": 15, "chance": "1/3"},
            {"item": "Ghostweave hood", "min": 1, "max": 1, "chance": "1/350"},
            {"item": "Ghostweave boots", "min": 1, "max": 1, "chance": "1/350"},
            {"item": "Ghostweave gloves", "min": 1, "max": 1, "chance": "1/350"},
            {"item": "Mysterious key", "min": 1, "max": 1, "chance": "1/30"},
        ],
    },
    "infernal_imp": {
        "coins_range": [0, 1500],
        "loot": [
            {"item": "Fire rune", "min": 5, "max": 20, "chance": "1/2"},
            {"item": "Air rune", "min": 5, "max": 15, "chance": "1/3"},
            {"item": "Earth rune", "min": 5, "max": 10, "chance": "1/4"},
            {"item": "Mysterious key", "min": 1, "max": 1, "chance": "1/30"},
        ],
    },
    "revenant necro": {
        "coins_range": [0, 2500],
        "unique": [
            {"item": "Revenant Relic Shard", "min": 1, "max": 1, "chance": "1/250"},
            {"item": "Revenant Totem", "min": 1, "max": 1, "chance": "1/500", "noted": True},
            {"item": "Viggora's Chainmace", "min": 1, "max": 1, "chance": "1/900", "on_task_chance": "1/550"},
        ],
        "pet": [
            {"item": "Tiny Revenant", "min": 1, "max": 1, "chance": "1/1000"},
        ],
        "loot": [
            {"item": "Revenant ether", "min": 30, "max": 70, "chance": "1/2"},
            {"item": "Bracelet of ethereum", "min": 1, "max": 1, "chance": "1/250"},
            {"item": "Death Guard", "min": 1, "max": 1, "chance": "1/150"},
            {"item": "Skull Lantern", "min": 1, "max": 1, "chance": "1/150"},
            {"item": "Mysterious key", "min": 1, "max": 1, "chance": "1/10"},
            {"item": "Spectral scythe", "min": 1, "max": 1, "chance": "1/100"},
            {"item": "Ghostweave robetop", "min": 1, "max": 1, "chance": "1/120"},
            {"item": "Ghostweave robeskirt", "min": 1, "max": 1, "chance": "1/120"},
            {"item": "Ghostweave hood", "min": 1, "max": 1, "chance": "1/120"},
            {"item": "Ghostweave boots", "min": 1, "max": 1, "chance": "1/120"},
            {"item": "Ghostweave gloves", "min": 1, "max": 1, "chance": "1/120"},
        ],
    },
    "revenant demon": {
        "coins_range": [0, 3000],
        "unique": [
            {"item": "Revenant Relic Shard", "min": 1, "max": 1, "chance": "1/200"},
            {"item": "Revenant Totem", "min": 1, "max": 1, "chance": "1/450", "noted": True},
            {"item": "Viggora's Chainmace", "min": 1, "max": 1, "chance": "1/850", "on_task_chance": "1/350"},
        ],
        "pet": [
            {"item": "Tiny Revenant", "min": 1, "max": 1, "chance": "1/1000"},
        ],
        "loot": [
            {"item": "Revenant ether", "min": 30, "max": 160, "chance": "1/2"},
            {"item": "Pure essence", "min": 10, "max": 90, "chance": "1/10", "noted": True},
            {"item": "Bracelet of ethereum", "min": 1, "max": 1, "chance": "1/250"},
            {"item": "Abyssal Whip", "min": 1, "max": 1, "chance": "1/200"},
            {"item": "Mysterious key", "min": 1, "max": 1, "chance": "1/20"},
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
            {"item": "Stonestaff", "min": 1, "max": 1, "chance": "1/80"},
            {"item": "Thornweave body", "min": 1, "max": 1, "chance": "1/120"},
            {"item": "Thornweave legs", "min": 1, "max": 1, "chance": "1/120"},
            {"item": "Thornweave helm", "min": 1, "max": 1, "chance": "1/120"},
            {"item": "Thornweave boots", "min": 1, "max": 1, "chance": "1/120"},
            {"item": "Thornweave gloves", "min": 1, "max": 1, "chance": "1/120"},
            {"item": "Fire rune", "min": 10, "max": 40, "chance": "1/3"},
            {"item": "Earth rune", "min": 10, "max": 30, "chance": "1/3"},
        ],
    },
    "phantom_archer": {
        "coins_range": [0, 3500],
        "unique": [
            {"item": "Ironwood bow", "min": 1, "max": 1, "chance": "1/120"},
            {"item": "Scaleweave body", "min": 1, "max": 1, "chance": "1/150"},
            {"item": "Scaleweave chaps", "min": 1, "max": 1, "chance": "1/150"},
        ],
        "pet": [
            {"item": "Flickerwisp", "min": 1, "max": 1, "chance": "1/1500"},
        ],
        "loot": [
            {"item": "Mithril arrows", "min": 15, "max": 60, "chance": "1/2"},
            {"item": "Adamant arrows", "min": 5, "max": 25, "chance": "1/4"},
            {"item": "Steel arrows", "min": 20, "max": 80, "chance": "1/2"},
            {"item": "Whisperwood bow", "min": 1, "max": 1, "chance": "1/30"},
            {"item": "Scaleweave coif", "min": 1, "max": 1, "chance": "1/200"},
            {"item": "Scaleweave boots", "min": 1, "max": 1, "chance": "1/200"},
            {"item": "Scaleweave vambraces", "min": 1, "max": 1, "chance": "1/200"},
            {"item": "Uncut emerald", "min": 1, "max": 2, "chance": "1/6", "noted": True},
        ],
    },
    "risen_bonecaller": {
        "coins_range": [0, 4000],
        "unique": [
            {"item": "Spectral scythe", "min": 1, "max": 1, "chance": "1/150"},
            {"item": "Ghostweave robetop", "min": 1, "max": 1, "chance": "1/200"},
            {"item": "Ghostweave robeskirt", "min": 1, "max": 1, "chance": "1/200"},
        ],
        "pet": [
            {"item": "Soulflame", "min": 1, "max": 1, "chance": "1/1500"},
        ],
        "loot": [
            {"item": "Bone Rune", "min": 5, "max": 20, "chance": "1/2"},
            {"item": "Cursed Bone", "min": 1, "max": 2, "chance": "1/8"},
            {"item": "Death Guard", "min": 1, "max": 1, "chance": "1/50"},
            {"item": "Skull Lantern", "min": 1, "max": 1, "chance": "1/50"},
            {"item": "Death rune", "min": 10, "max": 40, "chance": "1/3"},
            {"item": "Ghostweave hood", "min": 1, "max": 1, "chance": "1/250"},
            {"item": "Ghostweave boots", "min": 1, "max": 1, "chance": "1/250"},
            {"item": "Ghostweave gloves", "min": 1, "max": 1, "chance": "1/250"},
        ],
    },
    "windstrider": {
        "coins_range": [0, 5000],
        "unique": [
            {"item": "Hexwood bow", "min": 1, "max": 1, "chance": "1/120"},
            {"item": "Drakescale body", "min": 1, "max": 1, "chance": "1/150"},
            {"item": "Drakescale chaps", "min": 1, "max": 1, "chance": "1/150"},
        ],
        "pet": [
            {"item": "Flickerwisp", "min": 1, "max": 1, "chance": "1/1500"},
        ],
        "loot": [
            {"item": "Adamant arrows", "min": 10, "max": 40, "chance": "1/2"},
            {"item": "Mithril arrows", "min": 15, "max": 60, "chance": "1/2"},
            {"item": "Scaleweave body", "min": 1, "max": 1, "chance": "1/60"},
            {"item": "Scaleweave chaps", "min": 1, "max": 1, "chance": "1/60"},
            {"item": "Whisperwood bow", "min": 1, "max": 1, "chance": "1/40"},
            {"item": "Ironwood bow", "min": 1, "max": 1, "chance": "1/80"},
        ],
    },
    "infernal_warlock": {
        "coins_range": [0, 5500],
        "unique": [
            {"item": "Flamestaff", "min": 1, "max": 1, "chance": "1/120"},
            {"item": "Wraithcaller's robetop", "min": 1, "max": 1, "chance": "1/150"},
            {"item": "Wraithcaller's robeskirt", "min": 1, "max": 1, "chance": "1/150"},
        ],
        "pet": [
            {"item": "Embersprite", "min": 1, "max": 1, "chance": "1/1500"},
        ],
        "loot": [
            {"item": "Fire rune", "min": 15, "max": 50, "chance": "1/2"},
            {"item": "Earth rune", "min": 10, "max": 40, "chance": "1/2"},
            {"item": "Thornweave body", "min": 1, "max": 1, "chance": "1/60"},
            {"item": "Thornweave legs", "min": 1, "max": 1, "chance": "1/60"},
            {"item": "Stonestaff", "min": 1, "max": 1, "chance": "1/40"},
            {"item": "Tidestaff", "min": 1, "max": 1, "chance": "1/80"},
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
    "hollow_warden": {
        "coins_range": [5000, 25000],
        "loot": [
            {"item": "Fire rune", "min": 20, "max": 80, "chance": "1/2"},
            {"item": "Earth rune", "min": 20, "max": 80, "chance": "1/2"},
            {"item": "Air rune", "min": 20, "max": 80, "chance": "1/2"},
            {"item": "Water rune", "min": 15, "max": 60, "chance": "1/2"},
            {"item": "Death rune", "min": 10, "max": 40, "chance": "1/3"},
            {"item": "Adamant arrows", "min": 15, "max": 60, "chance": "1/2"},
            {"item": "Rune arrows", "min": 5, "max": 20, "chance": "1/3"},
            {"item": "Mithril arrows", "min": 20, "max": 80, "chance": "1/2"},
            {"item": "Dragon arrows", "min": 1, "max": 5, "chance": "1/8"},
            {"item": "Cursed Bone", "min": 2, "max": 5, "chance": "1/3"},
            {"item": "Bone Rune", "min": 10, "max": 40, "chance": "1/2"},
            {"item": "Uncut emerald", "min": 2, "max": 4, "chance": "1/4", "noted": True},
            {"item": "Uncut ruby", "min": 1, "max": 3, "chance": "1/6", "noted": True},
            {"item": "Uncut diamond", "min": 1, "max": 2, "chance": "1/10", "noted": True},
            {"item": "Shark", "min": 3, "max": 6, "chance": "1/3"},
            {"item": "Anglerfish", "min": 2, "max": 4, "chance": "1/5"},
            {"item": "Mysterious key", "min": 1, "max": 1, "chance": "1/15"},
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
            {"item": "Viggora's Chainmace", "min": 1, "max": 1, "chance": "1/850", "on_task_chance": "1/250"},
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
            {"item": "Gold Bar", "min": 1, "max": 1, "chance": "1/30"},
        ],
    },
    "duskwalker": {
        "coins_range": [0, 40000],
        "unique": [
            {"item": "Nightfall bow", "min": 1, "max": 1, "chance": "1/350"},
            {"item": "Voidfire body", "min": 1, "max": 1, "chance": "1/400"},
            {"item": "Voidfire chaps", "min": 1, "max": 1, "chance": "1/400"},
            {"item": "Voidfire Quiver", "min": 1, "max": 1, "chance": "1/500"},
            {"item": "Ancient Emblem", "min": 1, "max": 1, "chance": "1/100"},
        ],
        "pet": [
            {"item": "Tiny Dark Archer", "min": 1, "max": 1, "chance": "1/2000"},
        ],
        "loot": [
            {"item": "Dragon arrows", "min": 10, "max": 50, "chance": "1/2"},
            {"item": "Bone bolts", "min": 5, "max": 30, "chance": "1/3"},
            {"item": "Rune arrows", "min": 20, "max": 80, "chance": "1/2"},
            {"item": "Voidfire coif", "min": 1, "max": 1, "chance": "1/200"},
            {"item": "Voidfire boots", "min": 1, "max": 1, "chance": "1/200"},
            {"item": "Voidfire vambraces", "min": 1, "max": 1, "chance": "1/200"},
            {"item": "Drakescale body", "min": 1, "max": 1, "chance": "1/80"},
            {"item": "Drakescale chaps", "min": 1, "max": 1, "chance": "1/80"},
            {"item": "Hexwood bow", "min": 1, "max": 1, "chance": "1/60"},
            {"item": "Bone crossbow", "min": 1, "max": 1, "chance": "1/150"},
            {"item": "Anglerfish", "min": 2, "max": 6, "chance": "1/3"},
        ],
    },
    "emberlord": {
        "coins_range": [0, 45000],
        "unique": [
            {"item": "Soulfire staff", "min": 1, "max": 1, "chance": "1/350"},
            {"item": "Soulfire robetop", "min": 1, "max": 1, "chance": "1/400"},
            {"item": "Soulfire robeskirt", "min": 1, "max": 1, "chance": "1/400"},
            {"item": "Cindertome", "min": 1, "max": 1, "chance": "1/500"},
            {"item": "Ancient Emblem", "min": 1, "max": 1, "chance": "1/100"},
        ],
        "pet": [
            {"item": "Soulflame", "min": 1, "max": 1, "chance": "1/2000"},
        ],
        "loot": [
            {"item": "Blood rune", "min": 20, "max": 100, "chance": "1/2"},
            {"item": "Fire rune", "min": 30, "max": 120, "chance": "1/2"},
            {"item": "Death rune", "min": 20, "max": 80, "chance": "1/3"},
            {"item": "Soulfire hat", "min": 1, "max": 1, "chance": "1/200"},
            {"item": "Soulfire boots", "min": 1, "max": 1, "chance": "1/200"},
            {"item": "Soulfire gloves", "min": 1, "max": 1, "chance": "1/200"},
            {"item": "Wraithcaller's robetop", "min": 1, "max": 1, "chance": "1/80"},
            {"item": "Wraithcaller's robeskirt", "min": 1, "max": 1, "chance": "1/80"},
            {"item": "Voidtouched wand", "min": 1, "max": 1, "chance": "1/100"},
            {"item": "Flamestaff", "min": 1, "max": 1, "chance": "1/40"},
            {"item": "Manta Ray", "min": 2, "max": 6, "chance": "1/3"},
        ],
    },
    "gravekeeper": {
        "coins_range": [0, 42000],
        "unique": [
            {"item": "Netharis's hood", "min": 1, "max": 1, "chance": "1/400"},
            {"item": "Netharis's boots", "min": 1, "max": 1, "chance": "1/400"},
            {"item": "Netharis's gloves", "min": 1, "max": 1, "chance": "1/400"},
            {"item": "Deathwarden staff", "min": 1, "max": 1, "chance": "1/350"},
            {"item": "Ancient Emblem", "min": 1, "max": 1, "chance": "1/100"},
        ],
        "pet": [
            {"item": "Soulflame", "min": 1, "max": 1, "chance": "1/2000"},
        ],
        "loot": [
            {"item": "Bone Rune", "min": 15, "max": 60, "chance": "1/2"},
            {"item": "Death rune", "min": 20, "max": 80, "chance": "1/2"},
            {"item": "Deathwarden robetop", "min": 1, "max": 1, "chance": "1/80"},
            {"item": "Deathwarden robeskirt", "min": 1, "max": 1, "chance": "1/80"},
            {"item": "Spectral scythe", "min": 1, "max": 1, "chance": "1/60"},
            {"item": "Ghostweave robetop", "min": 1, "max": 1, "chance": "1/40"},
            {"item": "Ghostweave robeskirt", "min": 1, "max": 1, "chance": "1/40"},
        ],
    },
    "netharis": {
        "coins_range": [0, 50000],
        "unique": [
            {"item": "Shroud of the Undying", "min": 1, "max": 1, "chance": "1/500"},
            {"item": "Giant pouch", "min": 1, "max": 1, "chance": "1/100"},
            {"item": "Netharis's Grasp", "min": 1, "max": 1, "chance": "1/350"},
            {"item": "Netharis's robetop", "min": 1, "max": 1, "chance": "1/400"},
            {"item": "Netharis's robeskirt", "min": 1, "max": 1, "chance": "1/400"},
            {"item": "Soulbound Grimoire", "min": 1, "max": 1, "chance": "1/500"},
        ],
        "pet": [
            {"item": "Lil' Undying", "min": 1, "max": 1, "chance": "1/3000"},
        ],
        "loot": [
            {"item": "Pure essence", "min": 30, "max": 150, "chance": "1/5", "noted": True},
            {"item": "Uncut diamond", "min": 1, "max": 3, "chance": "1/15", "noted": True},
            {"item": "Uncut dragonstone", "min": 1, "max": 2, "chance": "1/20", "noted": True},
            {"item": "Deathwarden robetop", "min": 1, "max": 1, "chance": "1/80"},
            {"item": "Deathwarden robeskirt", "min": 1, "max": 1, "chance": "1/80"},
            {"item": "Spectral scythe", "min": 1, "max": 1, "chance": "1/50"},
            {"item": "Bone Rune", "min": 10, "max": 50, "chance": "1/3"},
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
