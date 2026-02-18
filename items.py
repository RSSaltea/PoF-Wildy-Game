from typing import Dict, Any

STARTER_ITEMS = {"Starter Sword", "Starter Platebody"}
STARTER_SHOP_COOLDOWN_SEC = 30 * 60

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
    "cape",
    "ammo",
}

POTIONS = {
    "Strength": {"atk": 2, "hits": 10, "aliases": "str,str pot"},
    "Super Strength": {"atk": 4, "hits": 20, "aliases": "super str,sup str"},
}

FOOD: Dict[str, Dict[str, int]] = {
    "Lobster": {"heal": 12},
    "Shark": {"heal": 20},
    "Manta Ray": {"heal": 22, "aliases": "manta"},
    "Anglerfish": {"heal": 24, "aliases": "angler"},
    "Veilfruit": {"heal": 28},
}

_IMG_BASE = "https://github.com/RSSaltea/PoF-Wildy-Game/blob/main/docs/images/items/"

ITEMS: Dict[str, Dict[str, Any]] = {
    # Starter gear (non-stackable)
    "Starter Sword": {"type": "mainhand", "style": "melee", "atk": 2, "stackable": False, "value": 0, "aliases": "start sword,starter sword", "image": _IMG_BASE + "starter%20sword.png?raw=true"}, #
    "Starter Platebody": {"type": "body", "def": 2, "stackable": False, "value": 0, "aliases": "starter plate,start body,starter body", "image": _IMG_BASE + "starter%20platebody.png?raw=true"}, #

    # Weapons (non-stackable)
    "Rune dagger": {"type": "mainhand", "style": "melee", "atk": 3, "def": 1, "stackable": False, "value": 5000, "aliases": "rune dag,rdagger,r dagger,r dag", "image": _IMG_BASE + "rune%20dagger.png?raw=true"}, #
    "Rune scimitar": {"type": "mainhand", "style": "melee", "atk": 3, "stackable": False, "value": 5000, "aliases": "rune scim,rune scimmy,runescim", "image": _IMG_BASE + "rune%20scimitar.png?raw=true"}, #
    "Dragon dagger": {"type": "mainhand", "style": "melee", "atk": 4, "stackable": False, "value": 17000, "aliases": "dds,dragon dagger,d dagger", "image": _IMG_BASE + "dragon%20dagger.png?raw=true"}, #
    "Dragon scimitar": {"type": "mainhand", "style": "melee", "atk": 5, "stackable": False, "value": 32000, "aliases": "d scim,dscim,dragon scim,d scimitar", "image": _IMG_BASE + "dragon%20scimitar.png?raw=true"}, #
    "Dragon 2h sword": {"type": "mainhand,offhand", "style": "melee", "atk": 8, "stackable": False, "value": 54000, "aliases": "d2h,dragon 2h", "image": _IMG_BASE + "dragon%202h%20sword.png?raw=true"}, #
    "Abyssal Whip": {"type": "mainhand", "style": "melee", "atk": 11, "stackable": False, "value": 60000, "aliases": "whip,abby whip,abyssal whip"},
    "Abyssal Scourge": {"type": "mainhand", "style": "melee", "atk": 15, "stackable": False, "value": 72000, "aliases": "scourge,abby scourge,abyssal scourge"},
    "Veilbreaker": {"type": "mainhand", "style": "melee", "atk": 28, "stackable": False, "value": 142000, "aliases": "veil"},
    "Death Guard": {"type": "mainhand", "style": "necro", "atk": 5, "stackable": False, "value": 142000, "aliases": "deathguard"},

    "Viggora's Chainmace": {
        "type": "mainhand",
        "style": "melee",
        "atk": 4,
        "atk_vs_npc": 20,
        "stackable": False,
        "value": 54000,
        "aliases": "chainmace,viggoras chainmace,vigs chainmace,viggora chainmace,Viggora's Chainmace",
    },
    "Abyssal Chainmace": {
        "type": "mainhand",
        "style": "melee",
        "atk": 6,
        "atk_vs_npc": 34,
        "stackable": False,
        "value": 250000,
        "aliases": "abyssal mace,abyssal chainmace,abby chainmace,abby mace",
    },

    # Offhands
    "Rune sq shield": {"type": "offhand", "style": "melee", "def": 3, "stackable": False, "value": 7000, "aliases": "rune sq", "image": _IMG_BASE + "rune%20sq%20shield.png?raw=true"}, #
    "Skull Lantern": {"type": "offhand", "style": "necro", "atk": 4, "stackable": False, "value": 142000, "aliases": "lantern"},
    "Bronze Defender": {"type": "offhand", "style": "melee", "def": 1, "stackable": False, "value": 500, "aliases": "bronze def"},
    "Iron Defender": {"type": "offhand", "style": "melee", "def": 1, "stackable": False, "value": 750, "aliases": "iron def,i def"},
    "Steel Defender": {"type": "offhand", "style": "melee", "def": 1, "stackable": False, "value": 1000, "aliases": "steel def,s def"},
    "Black Defender": {"type": "offhand", "style": "melee", "def": 2, "stackable": False, "value": 1250, "aliases": "black def"},
    "Mithril Defender": {"type": "offhand", "style": "melee", "def": 2, "stackable": False, "value": 1500, "aliases": "mith def,mithril def,m def"},
    "Adamant Defender": {"type": "offhand", "style": "melee", "def": 2, "stackable": False, "value": 1750, "aliases": "addy def,addy defender,a def"},
    "Rune Defender": {"type": "offhand", "style": "melee", "def": 2, "atk": 2, "stackable": False, "value": 2000, "aliases": "rune def,r def"},
    "Bone Defender": {"type": "offhand", "style": "melee", "def": 3, "atk": 3, "stackable": False, "value": 4000, "aliases": "bone def,b def"},

    # Armour / wearables (non-stackable)
    "Rune platebody": {"type": "body", "def": 3, "stackable": False, "value": 12000, "aliases": "rune plate", "image": _IMG_BASE + "rune%20platebody.png?raw=true"}, #
    "Rune chainbody": {"type": "body", "def": 2, "stackable": False, "value": 8000, "aliases": "rune chain", "image": _IMG_BASE + "rune%20chainbody.png?raw=true"}, #
    "Rune platelegs": {"type": "legs", "def": 2, "stackable": False, "value": 9000, "aliases": "rune legs", "image": _IMG_BASE + "rune%20platelegs.png?raw=true"}, #
    "Rune full helm": {"type": "helm", "def": 2, "stackable": False, "value": 8000, "aliases": "rune helm", "image": _IMG_BASE + "rune%20full%20helm.png?raw=true"}, #
    "Rune med helm": {"type": "helm", "def": 1, "stackable": False, "value": 5000, "aliases": "rune med", "image": _IMG_BASE + "rune%20med%20helm.png?raw=true"}, #
    "Dragon boots": {"type": "boots", "def": 3, "atk": 1, "stackable": False, "value": 24000, "aliases": "dboots,dragon boot,d boots,dragon boots", "image": _IMG_BASE + "dragon%20boots.png?raw=true"}, #
    "Dragon platebody": {"type": "body", "def": 8, "stackable": False, "value": 42000, "aliases": "d plate,dplate,dragon plate,d pbody,dragon platebody", "image": _IMG_BASE + "dragon%20platebody.png?raw=true"}, #
    "Dragon platelegs": {"type": "legs", "def": 6, "stackable": False, "value": 32000, "aliases": "d legs,dlegs,dragon leg", "image": _IMG_BASE + "dragon%20platelegs.png?raw=true"},
    "Zarveth's Ascendant Platebody": {"type": "body", "def": 5, "atk": 4, "stackable": False, "value": 142000, "aliases": "zarveth plate,zarveths plate,zarveths platebody,zarveths body", "image": _IMG_BASE + "Zarveths%20Ascendant%20Platebody.png?raw=true"},
    "Zarveth's Ascendant Platelegs": {"type": "legs", "def": 4, "atk": 3, "stackable": False, "value": 72000, "aliases": "zarveth legs,zarveths platelegs,zarveths legs", "image": _IMG_BASE + "Zarveths%20Ascendant%20Platelegs.png?raw=true"},
    "Zarveth's Ascendant Mask": {"type": "helm", "def": 3, "atk": 1, "stackable": False, "value": 62000, "aliases": "zarveth mask,zarveths mask", "image": _IMG_BASE + "Zarveths%20Ascendant%20Mask.png?raw=true"},
    "Black Mask": {"type": "helm", "stackable": False, "value": 100000, "aliases": "black mask,bmask"},
    "Slayer Helmet": {"type": "helm", "stackable": False, "value": 25000, "aliases": "slayer helm,slayer helmet"},
    "Shady Slayer Helm": {"type": "helm", "def": 2, "stackable": False, "value": 40000, "aliases": "shady slayer helm,shady helm,shady slayer helmet"},

    # Amulets
    "Amulet of Seeping": {"type": "amulet", "def": 0, "atk": 2, "stackable": False, "value": 12000, "aliases": "ammy of seeping,seeping"},

    # Rings
    "Ring of Valthyros": {"type": "ring", "def": 5, "atk": 1, "stackable": False, "value": 10000, "aliases": "ring of valth,valth ring"},

    # Capes
    "Shroud of the Undying": {"type": "cape", "def": 5, "stackable": False, "value": 200000, "aliases": "shroud,undying shroud,undying cape"},

    # Wearables (effects described in ITEM_EFFECTS)
    "Bracelet of ethereum": {"type": "gloves", "stackable": False, "value": 12000, "aliases": "ethereum bracelet,bracelet ethereum,bracelet of ethereum,bracelet of ether,ether bracelet,bracelet ether"},
    "Wristwraps of the Damned": {"type": "gloves", "stackable": False, "value": 54000, "aliases": "wristwraps of damned,wotd,wraps of the damned,wristwraps of the damned"},
    "Bracelet of Slayer Aggression": {"type": "gloves", "stackable": False, "value": 80000, "aliases": "brace of slayer,brace of aggro,brace of aggression,slayer bracelet,slayer brace,aggro bracelet,aggro brace,bracelet of aggression,bracelet of aggro"},

    # Stackable / misc drops
    "Small pouch": {"type": "esspouch", "essstorage": 4, "stackable": False, "value": 0, "aliases": "spouch"},
    "Medium pouch": {"type": "esspouch", "essstorage": 6, "stackable": False, "value": 0, "aliases": "mpouch"},
    "Large pouch": {"type": "esspouch", "essstorage": 9, "stackable": False, "value": 0, "aliases": "lpouch"},
    "Giant pouch": {"type": "esspouch", "essstorage": 12, "stackable": False, "value": 0, "aliases": "gpouch"},
    "Colossal pouch": {"type": "esspouch", "essstorage": 16, "stackable": False, "value": 0, "aliases": "cpouch"},
    "Pure essence": {"type": "misc", "stackable": False, "value": 5, "aliases": "ess"},
    "Cyclops Eye": {"type": "misc", "stackable": False, "value": 50, "aliases": "eye"},
    "Revenant ether": {"type": "misc", "stackable": True, "value": 50, "aliases": "ether,rev ether,revenant ether"},
    "Nature rune": {"type": "rune", "multiplier": 1, "stackable": True, "value": 320, "aliases": "nature rune,nats,nature runes"},
    "Law rune": {"type": "rune", "multiplier": 0, "stackable": True, "value": 320, "aliases": "law rune,laws,law runes"},
    "Death rune": {"type": "rune", "multiplier": 0, "stackable": True, "value": 320, "aliases": "death rune,deaths,death runes"},
    "Blood rune": {"type": "rune", "multiplier": 0, "stackable": True, "value": 320, "aliases": "blood rune,bloods,blood runes"},
    "Chaos rune": {"type": "rune", "multiplier": 1, "stackable": True, "value": 240, "aliases": "chaos rune,chaos runes,chaos"},
    "Cosmic rune": {"type": "rune", "multiplier": 1, "stackable": True, "value": 300, "aliases": "cosmic rune,cosmic runes,cosmics"},
    "Uncut sapphire": {"type": "misc", "stackable": False, "value": 500, "aliases": "uncut sapphire,uncut sapphires"},
    "Uncut emerald": {"type": "misc", "stackable": False, "value": 750, "aliases": "uncut emerald,uncut emeralds"},
    "Uncut ruby": {"type": "misc", "stackable": False, "value": 1000, "aliases": "uncut ruby,uncut rubies"},
    "Uncut diamond": {"type": "misc", "stackable": False, "value": 1500, "aliases": "uncut diamond,uncut diamonds"},
    "Uncut dragonstone": {"type": "misc", "stackable": False, "value": 3000, "aliases": "uncut dragonstone,uncut dragonstones"},
    # Cut gems
    "Sapphire": {"type": "misc", "stackable": False, "value": 1000, "aliases": "sapphire,sapphires"},
    "Emerald": {"type": "misc", "stackable": False, "value": 1500, "aliases": "emerald,emeralds"},
    "Ruby": {"type": "misc", "stackable": False, "value": 2000, "aliases": "ruby,rubies"},
    "Diamond": {"type": "misc", "stackable": False, "value": 3000, "aliases": "diamond,diamonds"},
    "Dragonstone": {"type": "misc", "stackable": False, "value": 6000, "aliases": "dragonstone,dragonstones"},
    # Gem crafting
    "Gold Bar": {"type": "misc", "stackable": False, "value": 2000, "aliases": "gold bar,gold,gbar"},
    "Omnigem": {"type": "misc", "stackable": False, "value": 50000, "aliases": "omnigem,omni gem"},
    "Omnigem Amulet": {"type": "misc", "stackable": False, "value": 60000, "aliases": "omnigem amulet,omni amulet,omnigem ammy"},
    "Eclipse of the Five": {"type": "amulet", "atk": 6, "def": -1, "stackable": False, "value": 150000, "aliases": "eclipse,eotf,eclipse of the five,eclipse of five,eclipse amulet"},
    "Shadow Veil": {"type": "misc", "stackable": False, "value": 150000, "aliases": "shadow veil,sveil"},
    "Abyssal ash": {"type": "misc", "stackable": True, "value": 40, "aliases": "abyssal ash,ash"},
    "Abyssal charm": {"type": "misc", "stackable": True, "value": 50, "aliases": "abyssal charm,charm"},
    "Overlord core fragment": {"type": "misc", "stackable": False, "value": 500000, "aliases": "core fragment,overlord fragment,overlord core fragment"},
    "Revenant Relic Shard": {"type": "misc", "stackable": True, "value": 50000, "aliases": "relic shard,rev relic shard,revenant relic shard"},
    "Revenant Totem": {"type": "misc", "stackable": False, "value": 100000, "aliases": "rev totem,revenant totem,totem"},
    "Ancient Effigy": {"type": "misc", "stackable": False, "value": 500000, "aliases": "effigy,ancient effigy"},
    "Ancient Emblem": {"type": "misc", "stackable": False, "value": 1000000, "aliases": "emblem,ancient emblem"},
    "Cursed Bone": {"type": "misc", "stackable": True, "value": 5000, "aliases": "cursed bone,cursed bones,cbone"},
    "Bone key": {"type": "misc", "stackable": True, "value": 30000, "aliases": "bone key,bkey,bone keys"},
    "Bone Rune": {"type": "rune", "multiplier": 0, "stackable": True, "value": 500, "aliases": "bone rune,bone runes"},
    "Mysterious key": {"type": "misc", "stackable": True, "value": 30000, "aliases": "mysterious key,key,keys"},
    # Pets
    "Tiny Revenant": {"type": "misc", "stackable": False, "value": 0, "aliases": "tiny revenant,rev pet"},
    "Baby Chaos Fanatic": {"type": "misc", "stackable": False, "value": 0, "aliases": "baby chaos fanatic,fanatic pet"},
    "Mini Overlord": {"type": "misc", "stackable": False, "value": 0, "aliases": "mini overlord,overlord pet"},
    "Lil' Undying": {"type": "misc", "stackable": False, "value": 0, "aliases": "lil undying,undying pet"},
    "Zarvethy": {"type": "misc", "stackable": False, "value": 0, "aliases": "zarvethy,zarveth pet,veilbreaker pet"},
    "Splat": {"type": "misc", "stackable": False, "value": 0, "aliases": "splat,valthyros pet"},

    # Potions
    "Strength (4)": {"type": "misc", "stackable": False, "value": 5000, "aliases": "strength,str,str pot"},
    "Strength (3)": {"type": "misc", "stackable": False, "value": 3750, "aliases": ""},
    "Strength (2)": {"type": "misc", "stackable": False, "value": 2500, "aliases": ""},
    "Strength (1)": {"type": "misc", "stackable": False, "value": 1250, "aliases": ""},
    "Super Strength (4)": {"type": "misc", "stackable": False, "value": 8000, "aliases": "super strength,super str,sup str"},
    "Super Strength (3)": {"type": "misc", "stackable": False, "value": 6000, "aliases": ""},
    "Super Strength (2)": {"type": "misc", "stackable": False, "value": 4000, "aliases": ""},
    "Super Strength (1)": {"type": "misc", "stackable": False, "value": 2000, "aliases": ""},
}

ITEM_EFFECTS = {
    "Bracelet of ethereum": {"effect": "When worn you will take 50% reduced damage from Revenants."},
    "Wristwraps of the Damned": {"effect": "When worn you have a small chance to inflict a bleed."},
    "Viggora's Chainmace": {"effect": "Grants +16 attack against ALL NPCs at a cost of 3 Revenant ether per hit (no bonus in PvP)."},
    "Abyssal Chainmace": {"effect": "Grants +28 attack against ALL NPCs at a cost of 3 Revenant ether per hit (no bonus in PvP)."},
    "Amulet of Seeping": {"effect": "Heals 1 + 2% of damage dealt at the cost of 5 Blood runes per successful hit."},
    "Shroud of the Undying": {"effect": "2% chance to completely nullify incoming damage on any hit."},
    "Slayer Helmet": {"effect": "When worn, increases damage dealt to your current slayer task NPC by 20%."},
    "Shady Slayer Helm": {"effect": "When worn, increases damage dealt to your current slayer task NPC by 27%."},
    "Bracelet of Slayer Aggression": {"effect": "When worn, guarantees finding your slayer task NPC when using !w fight <npc>. Costs 20 Chaos runes per fight."},
    # Potions
    "Strength (4)": {"effect": "Drink with `!w drink`. Grants +2 attack for 10 hits. 4 doses."},
    "Strength (3)": {"effect": "Drink with `!w drink`. Grants +2 attack for 10 hits. 3 doses remaining."},
    "Strength (2)": {"effect": "Drink with `!w drink`. Grants +2 attack for 10 hits. 2 doses remaining."},
    "Strength (1)": {"effect": "Drink with `!w drink`. Grants +2 attack for 10 hits. 1 dose remaining."},
    "Super Strength (4)": {"effect": "Drink with `!w drink`. Grants +4 attack for 20 hits. 4 doses."},
    "Super Strength (3)": {"effect": "Drink with `!w drink`. Grants +4 attack for 20 hits. 3 doses remaining."},
    "Super Strength (2)": {"effect": "Drink with `!w drink`. Grants +4 attack for 20 hits. 2 doses remaining."},
    "Super Strength (1)": {"effect": "Drink with `!w drink`. Grants +4 attack for 20 hits. 1 dose remaining."},
    # Keys
    "Mysterious key": {"effect": "Used to open the Wilderness Chest via `!w chest open mysterious`. Grants coins and a chance at rare loot."},
    "Bone key": {"effect": "Used to open the Bone Chest via `!w chest open bone`. Grants coins and a chance at Cursed Bones, Bone Runes, or Dragon platebody."},
    # Pouches
    "Small pouch": {"effect": "Holds 4 Pure essence. Increases runes crafted per `!w rc` by the stored amount."},
    "Medium pouch": {"effect": "Holds 6 Pure essence. Increases runes crafted per `!w rc` by the stored amount."},
    "Large pouch": {"effect": "Holds 9 Pure essence. Increases runes crafted per `!w rc` by the stored amount."},
    "Giant pouch": {"effect": "Holds 12 Pure essence. Increases runes crafted per `!w rc` by the stored amount."},
    "Colossal pouch": {"effect": "Holds 16 Pure essence. Increases runes crafted per `!w rc` by the stored amount."},
    # Gems & enchanted
    "Eclipse of the Five": {"effect": "When worn, grants +6 attack but reduces defence by 1. Crafted from an Omnigem Amulet via `!w enchant`."},
    "Omnigem Amulet": {"effect": "An unenchanted amulet. Use `!w enchant omnigem amulet` to create Eclipse of the Five."},
    "Omnigem": {"effect": "A fused gem containing all five gem types. Used to craft an Omnigem Amulet."},
}

GEM_CUTTING = {
    "Uncut sapphire": "Sapphire",
    "Uncut emerald": "Emerald",
    "Uncut ruby": "Ruby",
    "Uncut diamond": "Diamond",
    "Uncut dragonstone": "Dragonstone",
}

