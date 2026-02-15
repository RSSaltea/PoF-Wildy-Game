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

# Food (not stackable)
FOOD: Dict[str, Dict[str, int]] = {
    "Lobster": {"heal": 12},
    "Shark": {"heal": 20},
    "Manta Ray": {"heal": 26},
}

ITEMS: Dict[str, Dict[str, Any]] = {
    # Starter gear (non-stackable)
    "Starter Sword": {"type": "mainhand", "atk": 2, "stackable": False, "aliases": "start sword,starter sword"},
    "Starter Platebody": {"type": "body", "def": 1, "stackable": False, "aliases": "starter plate,start body,starter body"},

    # Weapons (non-stackable)
    "Rune scimitar": {"type": "mainhand", "atk": 2, "stackable": False, "aliases": "rune scim,rune scimmy,runescim"},
    "Dragon dagger": {"type": "mainhand", "atk": 3, "stackable": False, "aliases": "dds,dragon dagger,d dagger"},
    "Dragon scimitar": {"type": "mainhand", "atk": 4, "stackable": False, "aliases": "d scim,dscim,dragon scim,d scimitar"},
    "Dragon 2h sword": {"type": "mainhand", "atk": 7, "stackable": False, "aliases": "d2h,dragon 2h"},
    "Abyssal Whip": {"type": "mainhand", "atk": 10, "stackable": False, "aliases": "whip,abby whip,abyssal whip"},
    "Abyssal Scourge": {"type": "mainhand", "atk": 14, "stackable": False, "aliases": "scourge,abby scourge,abyssal scourge"},

    "Viggora's Chainmace": {
        "type": "mainhand",
        "atk": 4,
        "atk_vs_npc": 14,
        "stackable": False,
        "aliases": "chainmace,viggoras chainmace,vigs chainmace,viggora chainmace",
    },

    # Armour / wearables (non-stackable)
    "Rune platebody": {"type": "body", "def": 2, "stackable": False, "aliases": "rune plate,rune body,rune platebody"},
    "Dragon boots": {"type": "boots", "def": 1, "stackable": False, "aliases": "dboots,dragon boot,d boots,dragon boots"},
    "Dragon platebody": {"type": "body", "def": 4, "stackable": False, "aliases": "d plate,dplate,dragon plate,d pbody,dragon platebody"},

    # Wearables (effects described in ITEM_EFFECTS)
    "Bracelet of ethereum": {"type": "amulet", "stackable": False, "aliases": "ethereum bracelet,bracelet ethereum,bracelet of ethereum"},
    "Wristwraps of the Damned": {"type": "gloves", "stackable": False, "aliases": "wristwraps of damned,wotd,wraps of the damned,wristwraps of the damned"},

    # Stackable / misc drops (stackable)
    "Revenant ether": {"type": "misc", "stackable": True, "aliases": "ether,rev ether,revenant ether"},
    "Nature rune": {"type": "misc", "stackable": True, "aliases": "nature rune,nats,nature runes"},
    "Law rune": {"type": "misc", "stackable": True, "aliases": "law rune,laws,law runes"},
    "Death rune": {"type": "misc", "stackable": True, "aliases": "death rune,deaths,death runes"},
    "Blood rune": {"type": "misc", "stackable": True, "aliases": "blood rune,bloods,blood runes"},
    "Chaos rune": {"type": "misc", "stackable": True, "aliases": "chaos rune,chaos runes,chaos"},
    "Uncut sapphire": {"type": "misc", "stackable": False, "aliases": "uncut sapphire,sapphire,uncut sapphires"},
    "Uncut emerald": {"type": "misc", "stackable": False, "aliases": "uncut emerald,emerald,uncut emeralds"},
    "Abyssal ash": {"type": "misc", "stackable": True, "aliases": "abyssal ash,ash"},
    "Abyssal charm": {"type": "misc", "stackable": True, "aliases": "abyssal charm,charm"},
    "Overlord core fragment": {"type": "misc", "stackable": False, "aliases": "core fragment,overlord fragment,overlord core fragment"},
    "Revenant Relic Shard": {"type": "misc", "stackable": True, "aliases": "relic shard,rev relic shard,revenant relic shard"},
    "Revenant Totem": {"type": "misc", "stackable": False, "aliases": "rev totem,revenant totem,totem"},
    "Ancient Effigy": {"type": "misc", "stackable": False, "aliases": "effigy,ancient effigy"},
    "Ancient Emblem": {"type": "misc", "stackable": False, "aliases": "emblem,ancient emblem"},
    "Mysterious key": {"type": "misc", "stackable": True, "aliases": "mysterious key,key,keys"},
    # Pets
    "Tiny Revenant": {"type": "misc", "stackable": False, "aliases": "tiny revenant,rev pet"},
    "Baby Chaos Fanatic": {"type": "misc", "stackable": False, "aliases": "baby chaos fanatic,fanatic pet"},
    "Mini Overlord": {"type": "misc", "stackable": False, "aliases": "mini overlord,overlord pet"},
}

ITEM_EFFECTS = {
    "Bracelet of ethereum": {"effect": "When worn you will take 50% reduced damage from Revenants."},
    "Wristwraps of the Damned": {"effect": "When worn, Abyssal Overlord spawns with 30% less base HP."},
    "Viggora's Chainmace": {"effect": "Grants +7 attack against ALL NPCs (no bonus in PvP)."},
}
