from typing import Dict, Any

STARTER_ITEMS = {"Starter Sword", "Starter Platebody"}
STARTER_SHOP_COOLDOWN_SEC = 30 * 60

# equipment slots
EQUIP_SLOT_SET = {
    "helm",
    "body",
    "legs",
    "offhand",
    "mainhand",
    "boots",
    "amulet",
    "gloves",
    "ring",
}

POTIONS: Dict[str, Dict[str, int]] = {
    "Super Strength": {"atk": 2, "hits": 5, "aliases": "super str,sup str"},
}

# Food (not stackable)
FOOD: Dict[str, Dict[str, int]] = {
    "Lobster": {"heal": 12},
    "Shark": {"heal": 20},
    "Manta Ray": {"heal": 26},
    "Veilfruit": {"heal": 34},
}

ITEMS: Dict[str, Dict[str, Any]] = {
    # Starter gear (non-stackable)
    "Starter Sword": {"type": "mainhand", "atk": 1, "stackable": False, "value": 0, "aliases": "start sword,starter sword"},
    "Starter Platebody": {"type": "body", "def": 1, "stackable": False, "value": 0, "aliases": "starter plate,start body,starter body"},

    # Weapons (non-stackable)
    "Rune scimitar": {"type": "mainhand", "atk": 2, "stackable": False, "value": 5000, "aliases": "rune scim,rune scimmy,runescim"},
    "Dragon dagger": {"type": "mainhand", "atk": 3, "stackable": False, "value": 17000, "aliases": "dds,dragon dagger,d dagger"},
    "Dragon scimitar": {"type": "mainhand", "atk": 4, "stackable": False, "value": 32000, "aliases": "d scim,dscim,dragon scim,d scimitar"},
    "Dragon 2h sword": {"type": "mainhand", "atk": 7, "stackable": False, "value": 54000, "aliases": "d2h,dragon 2h"},
    "Abyssal Whip": {"type": "mainhand", "atk": 10, "stackable": False, "value": 60000, "aliases": "whip,abby whip,abyssal whip"},
    "Abyssal Scourge": {"type": "mainhand", "atk": 14, "stackable": False, "value": 72000, "aliases": "scourge,abby scourge,abyssal scourge"},
    "Veilbreaker": {"type": "mainhand", "atk": 28, "stackable": False, "value": 142000, "aliases": "veil"},

    "Viggora's Chainmace": {
        "type": "mainhand",
        "atk": 4,
        "atk_vs_npc": 20,
        "stackable": False,
        "value": 54000,
        "aliases": "chainmace,viggoras chainmace,vigs chainmace,viggora chainmace",
    },

    # Armour / wearables (non-stackable)
    "Rune platebody": {"type": "body", "def": 4, "stackable": False, "value": 12000, "aliases": "rune plate"},
    "Rune chainbody": {"type": "body", "def": 2, "stackable": False, "value": 8000, "aliases": "rune chain"},
    "Rune med helm": {"type": "helm", "def": 1, "stackable": False, "value": 5000, "aliases": "rune med"},
    "Rune sq shield": {"type": "offhand", "def": 2, "stackable": False, "value": 7000, "aliases": "rune sq"},
    "Dragon boots": {"type": "boots", "def": 3, "atk": 1, "stackable": False, "value": 24000, "aliases": "dboots,dragon boot,d boots,dragon boots"},
    "Dragon platebody": {"type": "body", "def": 7, "stackable": False, "value": 42000, "aliases": "d plate,dplate,dragon plate,d pbody,dragon platebody"},
    "Zarveth's Ascendant Platebody": {"type": "body", "def": 7, "atk": 4, "stackable": False, "value": 142000, "aliases": "zarveth plate,zarveths plate,zarveths platebody,zarveths body"},
    "Zarveth's Ascendant Platelegs": {"type": "legs", "def": 5, "atk": 3, "stackable": False, "value": 72000, "aliases": "zarveth legs,zarveths platelegs,zarveths legs"},
    "Zarveth's Ascendant Mask": {"type": "helm", "def": 3, "atk": 1, "stackable": False, "value": 62000, "aliases": "zarveth mask,zarveths mask"},

    # Wearables (effects described in ITEM_EFFECTS)
    "Bracelet of ethereum": {"type": "amulet", "stackable": False, "value": 12000, "aliases": "ethereum bracelet,bracelet ethereum,bracelet of ethereum"},
    "Wristwraps of the Damned": {"type": "gloves", "stackable": False, "value": 54000, "aliases": "wristwraps of damned,wotd,wraps of the damned,wristwraps of the damned"},

    # Stackable / misc drops (stackable)
    "Revenant ether": {"type": "misc", "stackable": True, "value": 50, "aliases": "ether,rev ether,revenant ether"},
    "Nature rune": {"type": "misc", "stackable": True, "value": 320, "aliases": "nature rune,nats,nature runes"},
    "Law rune": {"type": "misc", "stackable": True, "value": 320, "aliases": "law rune,laws,law runes"},
    "Death rune": {"type": "misc", "stackable": True, "value": 320, "aliases": "death rune,deaths,death runes"},
    "Blood rune": {"type": "misc", "stackable": True, "value": 320, "aliases": "blood rune,bloods,blood runes"},
    "Chaos rune": {"type": "misc", "stackable": True, "value": 240, "aliases": "chaos rune,chaos runes,chaos"},
    "Uncut sapphire": {"type": "misc", "stackable": False, "value": 5000, "aliases": "uncut sapphire,sapphire,uncut sapphires"},
    "Uncut emerald": {"type": "misc", "stackable": False, "value": 7500, "aliases": "uncut emerald,emerald,uncut emeralds"},
    "Abyssal ash": {"type": "misc", "stackable": True, "value": 40, "aliases": "abyssal ash,ash"},
    "Abyssal charm": {"type": "misc", "stackable": True, "value": 50, "aliases": "abyssal charm,charm"},
    "Overlord core fragment": {"type": "misc", "stackable": False, "value": 500000, "aliases": "core fragment,overlord fragment,overlord core fragment"},
    "Revenant Relic Shard": {"type": "misc", "stackable": True, "value": 50000, "aliases": "relic shard,rev relic shard,revenant relic shard"},
    "Revenant Totem": {"type": "misc", "stackable": False, "value": 100000, "aliases": "rev totem,revenant totem,totem"},
    "Ancient Effigy": {"type": "misc", "stackable": False, "value": 500000, "aliases": "effigy,ancient effigy"},
    "Ancient Emblem": {"type": "misc", "stackable": False, "value": 1000000, "aliases": "emblem,ancient emblem"},
    "Mysterious key": {"type": "misc", "stackable": True, "value": 30000, "aliases": "mysterious key,key,keys"},
    # Pets
    "Tiny Revenant": {"type": "misc", "stackable": False, "value": 0, "aliases": "tiny revenant,rev pet"},
    "Baby Chaos Fanatic": {"type": "misc", "stackable": False, "value": 0, "aliases": "baby chaos fanatic,fanatic pet"},
    "Mini Overlord": {"type": "misc", "stackable": False, "value": 0, "aliases": "mini overlord,overlord pet"},

    # Potions
    "Super Strength (4)": {"type": "misc", "stackable": False, "value": 0, "aliases": "super str,sup str"},
    "Super Strength (3)": {"type": "misc", "stackable": False, "value": 0, "aliases": "super str,sup str"},
    "Super Strength (2)": {"type": "misc", "stackable": False, "value": 0, "aliases": "super str,sup str"},
    "Super Strength (1)": {"type": "misc", "stackable": False, "value": 0, "aliases": "super str,sup str"},
}

ITEM_EFFECTS = {
    "Bracelet of ethereum": {"effect": "When worn you will take 50% reduced damage from Revenants."},
    "Wristwraps of the Damned": {"effect": "When worn, Abyssal Overlord spawns with 30% less base HP."},
    "Viggora's Chainmace": {"effect": "Grants +16 attack against ALL NPCs (no bonus in PvP)."},
}


