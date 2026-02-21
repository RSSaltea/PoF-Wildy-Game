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

# ── Stance-based combat constants ─────────────────────────────────────────
STANCES = ("stab", "slash", "crush", "magic", "range", "necro")

STANCE_TO_STYLE = {
    "stab": "melee", "slash": "melee", "crush": "melee",
    "magic": "magic", "range": "range", "necro": "necro",
}

ATK_KEYS = tuple(f"a_{s}" for s in STANCES)
DEF_KEYS = tuple(f"d_{s}" for s in STANCES)
STR_KEYS = ("str_melee", "str_range", "str_magic", "str_necro")
ALL_COMBAT_KEYS = ATK_KEYS + DEF_KEYS + STR_KEYS

POTIONS = {
    "Strength": {"str": 2, "hits": 10, "aliases": "str,str pot"},
    "Super Strength": {"str": 4, "hits": 20, "aliases": "super str,sup str"},
}

FOOD: Dict[str, Dict[str, int]] = {
    "Lobster": {"heal": 12},
    "Shark": {"heal": 20},
    "Manta Ray": {"heal": 22, "aliases": "manta"},
    "Anglerfish": {"heal": 24, "aliases": "angler"},
    "Veilfruit": {"heal": 28},
}

_IMG_BASE = "https://raw.githubusercontent.com/RSSaltea/PoF-Wildy-Game/main/docs/images/items/"

ITEMS: Dict[str, Dict[str, Any]] = {
    # Starter gear (non-stackable)
    "Starter Sword": {"type": "mainhand", "style": "melee", "stance": "slash", "str_melee": 8, "stackable": False, "value": 0, "aliases": "start sword,starter sword", "image": _IMG_BASE + "starter%20sword.png"},
    "Starter Platebody": {"type": "body", "d_stab": 8, "d_slash": 8, "d_crush": 8, "d_range": 8, "stackable": False, "value": 0, "aliases": "starter plate,start body,starter body", "image": _IMG_BASE + "starter%20platebody.png"},

    # Weapons (non-stackable)
    "Rune dagger": {"type": "mainhand", "style": "melee", "stance": "stab", "str_melee": 12, "d_stab": 4, "d_slash": 4, "stackable": False, "value": 5000, "aliases": "rune dag,rdagger,r dagger,r dag", "image": _IMG_BASE + "rune%20dagger.png"},
    "Rune scimitar": {"type": "mainhand", "style": "melee", "stance": "slash", "str_melee": 12, "stackable": False, "value": 5000, "aliases": "rune scim,rune scimmy,runescim", "image": _IMG_BASE + "rune%20scimitar.png"},
    "Dragon dagger": {"type": "mainhand", "style": "melee", "stance": "stab", "str_melee": 16, "stackable": False, "value": 17000, "aliases": "dds,dragon dagger,d dagger", "image": _IMG_BASE + "dragon%20dagger.png"},
    "Dragon scimitar": {"type": "mainhand", "style": "melee", "stance": "slash", "str_melee": 20, "stackable": False, "value": 32000, "aliases": "d scim,dscim,dragon scim,d scimitar", "image": _IMG_BASE + "dragon%20scimitar.png"},
    "Dragon 2h sword": {"type": "mainhand,offhand", "style": "melee", "stance": "crush", "str_melee": 32, "stackable": False, "value": 54000, "aliases": "d2h,dragon 2h", "image": _IMG_BASE + "dragon%202h%20sword.png"},
    "Abyssal Whip": {"type": "mainhand", "style": "melee", "stance": "slash", "str_melee": 44, "stackable": False, "value": 60000, "aliases": "whip,abby whip,abyssal whip"},
    "Abyssal Scourge": {"type": "mainhand", "style": "melee", "stance": "slash", "str_melee": 60, "stackable": False, "value": 72000, "aliases": "scourge,abby scourge,abyssal scourge"},
    "Veilbreaker": {"type": "mainhand", "style": "melee", "stance": "slash", "str_melee": 112, "stackable": False, "value": 142000, "aliases": "veil"},
    "Death Guard": {"type": "mainhand", "style": "necro", "stance": "necro", "str_necro": 20, "stackable": False, "value": 142000, "aliases": "deathguard"},

    # Range Weapons
    "Rotwood shortbow": {"type": "mainhand", "style": "range", "stance": "range", "str_range": 4, "consumes": "arrow", "stackable": False, "value": 5000, "aliases": "rotwood bow,rotwood"},
    "Whisperwood bow": {"type": "mainhand", "style": "range", "stance": "range", "str_range": 8, "consumes": "arrow", "stackable": False, "value": 15000, "aliases": "whisperwood,wbow"},
    "Ironwood bow": {"type": "mainhand", "style": "range", "stance": "range", "str_range": 12, "consumes": "arrow", "stackable": False, "value": 35000, "aliases": "ironwood,ibow"},
    "Hexwood bow": {"type": "mainhand", "style": "range", "stance": "range", "str_range": 20, "consumes": "arrow", "stackable": False, "value": 55000, "aliases": "hexwood,hbow"},
    "Bone crossbow": {"type": "mainhand", "style": "range", "stance": "range", "str_range": 20, "consumes": "bolt", "stackable": False, "value": 70000, "aliases": "bone xbow,bone cbow,bcbow"},
    "Nightfall bow": {"type": "mainhand,offhand", "style": "range", "stance": "range", "str_range": 28, "consumes": "arrow", "stackable": False, "value": 120000, "aliases": "nightfall,nbow"},

    # Magic Weapons
    "Galestaff": {"type": "mainhand", "style": "magic", "stance": "magic", "str_magic": 12, "a_magic": 4, "consumes": "Air rune", "stackable": False, "value": 5000, "aliases": "gale staff,gale"},
    "Tidestaff": {"type": "mainhand", "style": "magic", "stance": "magic", "str_magic": 20, "a_magic": 6, "consumes": "Water rune", "stackable": False, "value": 18000, "aliases": "tide staff,tide"},
    "Stonestaff": {"type": "mainhand", "style": "magic", "stance": "magic", "str_magic": 32, "a_magic": 8, "consumes": "Earth rune", "stackable": False, "value": 35000, "aliases": "stone staff,stone"},
    "Flamestaff": {"type": "mainhand", "style": "magic", "stance": "magic", "str_magic": 48, "a_magic": 10, "consumes": "Fire rune", "stackable": False, "value": 55000, "aliases": "flame staff,flame"},
    "Voidtouched wand": {"type": "mainhand", "style": "magic", "stance": "magic", "str_magic": 64, "a_magic": 12, "consumes": "Death rune", "stackable": False, "value": 80000, "aliases": "voidtouched,vwand"},
    "Soulfire staff": {"type": "mainhand,offhand", "style": "magic", "stance": "magic", "str_magic": 96, "a_magic": 16, "consumes": "Blood rune", "stackable": False, "value": 150000, "aliases": "soulfire,sf staff"},

    # Necromancy Weapons
    "Spectral scythe": {"type": "mainhand", "style": "necro", "stance": "necro", "str_necro": 40, "stackable": False, "value": 55000, "aliases": "spectral,scythe"},
    "Deathwarden staff": {"type": "mainhand,offhand", "style": "necro", "stance": "necro", "str_necro": 64, "stackable": False, "value": 90000, "aliases": "deathwarden,dw staff"},
    "Netharis's Grasp": {"type": "mainhand", "style": "necro", "stance": "necro", "str_necro": 80, "stackable": False, "value": 150000, "aliases": "netharis grasp,ng"},

    "Viggora's Chainmace": {"type": "mainhand", "style": "melee", "stance": "crush", "str_melee": 16, "atk_vs_npc": 80, "stackable": False, "value": 54000, "aliases": "chainmace,viggoras chainmace,vigs chainmace,viggora chainmace,Viggora's Chainmace"},
    "Abyssal Chainmace": {"type": "mainhand", "style": "melee", "stance": "crush", "str_melee": 24, "atk_vs_npc": 136, "stackable": False, "value": 250000, "aliases": "abyssal mace,abyssal chainmace,abby chainmace,abby mace"},

    # Offhands
    "Rune sq shield": {"type": "offhand", "style": "melee", "d_stab": 12, "d_slash": 12, "d_crush": 12, "d_range": 8, "stackable": False, "value": 7000, "aliases": "rune sq", "image": _IMG_BASE + "rune%20sq%20shield.png"},
    "Skull Lantern": {"type": "offhand", "style": "necro", "a_necro": 16, "stackable": False, "value": 142000, "aliases": "lantern"},
    "Voidfire Quiver": {"type": "offhand", "style": "range", "a_range": 16, "str_range": 8, "stackable": False, "value": 100000, "aliases": "voidfire quiver,vquiver"},
    "Cindertome": {"type": "offhand", "style": "magic", "a_magic": 16, "str_magic": 8, "stackable": False, "value": 100000, "aliases": "cindertome,ctome"},
    "Soulbound Grimoire": {"type": "offhand", "style": "necro", "a_necro": 20, "str_necro": 12, "stackable": False, "value": 120000, "aliases": "soulbound grimoire,grimoire,sgrimoire"},
    "Bronze Defender": {"type": "offhand", "style": "melee", "d_stab": 4, "d_slash": 4, "d_crush": 4, "stackable": False, "value": 500, "aliases": "bronze def"},
    "Iron Defender": {"type": "offhand", "style": "melee", "d_stab": 4, "d_slash": 4, "d_crush": 4, "stackable": False, "value": 750, "aliases": "iron def,i def"},
    "Steel Defender": {"type": "offhand", "style": "melee", "d_stab": 4, "d_slash": 4, "d_crush": 4, "stackable": False, "value": 1000, "aliases": "steel def,s def"},
    "Black Defender": {"type": "offhand", "style": "melee", "d_stab": 8, "d_slash": 8, "d_crush": 8, "stackable": False, "value": 1250, "aliases": "black def"},
    "Mithril Defender": {"type": "offhand", "style": "melee", "d_stab": 8, "d_slash": 8, "d_crush": 8, "stackable": False, "value": 1500, "aliases": "mith def,mithril def,m def"},
    "Adamant Defender": {"type": "offhand", "style": "melee", "d_stab": 8, "d_slash": 8, "d_crush": 8, "stackable": False, "value": 1750, "aliases": "addy def,addy defender,a def"},
    "Rune Defender": {"type": "offhand", "style": "melee", "d_stab": 8, "d_slash": 8, "d_crush": 8, "str_melee": 8, "stackable": False, "value": 2000, "aliases": "rune def,r def"},
    "Bone Defender": {"type": "offhand", "style": "melee", "d_stab": 12, "d_slash": 12, "d_crush": 12, "str_melee": 12, "stackable": False, "value": 4000, "aliases": "bone def,b def"},

    # Armour / wearables (non-stackable)
    "Rune platebody": {"type": "body", "d_stab": 12, "d_slash": 12, "d_crush": 12, "d_magic": -4, "d_range": 8, "stackable": False, "value": 12000, "aliases": "rune plate", "image": _IMG_BASE + "rune%20platebody.png"},
    "Rune chainbody": {"type": "body", "d_stab": 8, "d_slash": 8, "d_crush": 8, "d_range": 8, "stackable": False, "value": 8000, "aliases": "rune chain", "image": _IMG_BASE + "rune%20chainbody.png"},
    "Rune platelegs": {"type": "legs", "d_stab": 8, "d_slash": 8, "d_crush": 8, "d_range": 8, "stackable": False, "value": 9000, "aliases": "rune legs", "image": _IMG_BASE + "rune%20platelegs.png"},
    "Rune full helm": {"type": "helm", "d_stab": 8, "d_slash": 8, "d_crush": 8, "d_range": 8, "stackable": False, "value": 8000, "aliases": "rune helm", "image": _IMG_BASE + "rune%20full%20helm.png"},
    "Rune med helm": {"type": "helm", "d_stab": 4, "d_slash": 4, "d_crush": 4, "d_range": 4, "stackable": False, "value": 5000, "aliases": "rune med", "image": _IMG_BASE + "rune%20med%20helm.png"},
    "Dragon boots": {"type": "boots", "d_stab": 12, "d_slash": 12, "d_crush": 12, "d_magic": -4, "d_range": 8, "str_melee": 4, "stackable": False, "value": 24000, "aliases": "dboots,dragon boot,d boots,dragon boots", "image": _IMG_BASE + "dragon%20boots.png"},
    "Dragon platebody": {"type": "body", "d_stab": 32, "d_slash": 32, "d_crush": 28, "d_magic": -8, "d_range": 24, "stackable": False, "value": 42000, "aliases": "d plate,dplate,dragon plate,d pbody,dragon platebody", "image": _IMG_BASE + "dragon%20platebody.png"},
    "Dragon platelegs": {"type": "legs", "d_stab": 24, "d_slash": 24, "d_crush": 20, "d_magic": -8, "d_range": 20, "stackable": False, "value": 32000, "aliases": "d legs,dlegs,dragon leg", "image": _IMG_BASE + "dragon%20platelegs.png"},
    "Zarveth's Ascendant Platebody": {"type": "body", "d_stab": 20, "d_slash": 20, "d_crush": 16, "d_magic": -8, "d_range": 16, "str_melee": 16, "stackable": False, "value": 142000, "aliases": "zarveth plate,zarveths plate,zarveths platebody,zarveths body", "image": _IMG_BASE + "Zarveths%20Ascendant%20Platebody.png"},
    "Zarveth's Ascendant Platelegs": {"type": "legs", "d_stab": 16, "d_slash": 16, "d_crush": 12, "d_magic": -4, "d_range": 12, "str_melee": 12, "stackable": False, "value": 72000, "aliases": "zarveth legs,zarveths platelegs,zarveths legs", "image": _IMG_BASE + "Zarveths%20Ascendant%20Platelegs.png"},
    "Zarveth's Ascendant Mask": {"type": "helm", "d_stab": 12, "d_slash": 12, "d_crush": 12, "d_magic": -4, "d_range": 8, "str_melee": 4, "stackable": False, "value": 62000, "aliases": "zarveth mask,zarveths mask", "image": _IMG_BASE + "Zarveths%20Ascendant%20Mask.png"},
    "Black Mask": {"type": "helm", "stackable": False, "value": 100000, "aliases": "black mask,bmask"},
    "Slayer Helmet": {"type": "helm", "stackable": False, "value": 25000, "aliases": "slayer helm,slayer helmet"},
    "Shady Slayer Helm": {"type": "helm", "d_stab": 8, "d_slash": 8, "d_crush": 8, "d_range": 8, "stackable": False, "value": 40000, "aliases": "shady slayer helm,shady helm,shady slayer helmet"},

    # Amulets
    "Amulet of Seeping": {"type": "amulet", "str_melee": 8, "stackable": False, "value": 12000, "aliases": "ammy of seeping,seeping"},
    "Eclipse of the Five": {"type": "amulet", "str_melee": 24, "str_magic": 8, "str_range": 8, "str_necro": 8, "d_stab": -4, "d_slash": -4, "d_crush": -4, "d_range": -4, "stackable": False, "value": 64000, "aliases": "eclipse,eotf,eclipse of the five,eclipse of five,eclipse amulet", "image": _IMG_BASE + "eclipse%20of%20the%20five.png"},

    # Rings
    "Ring of Valthyros": {"type": "ring", "d_stab": 20, "d_slash": 20, "d_crush": 16, "d_range": 16, "str_melee": 4, "stackable": False, "value": 10000, "aliases": "ring of valth,valth ring"},

    # Capes
    "Shroud of the Undying": {"type": "cape", "d_stab": 20, "d_slash": 20, "d_crush": 16, "d_range": 16, "stackable": False, "value": 200000, "aliases": "shroud,undying shroud,undying cape"},

    # Wearables (effects described in ITEM_EFFECTS)
    "Bracelet of ethereum": {"type": "gloves", "stackable": False, "value": 12000, "aliases": "ethereum bracelet,bracelet ethereum,bracelet of ethereum,bracelet of ether,ether bracelet,bracelet ether"},
    "Wristwraps of the Damned": {"type": "gloves", "stackable": False, "value": 54000, "aliases": "wristwraps of damned,wotd,wraps of the damned,wristwraps of the damned"},
    "Bracelet of Slayer Aggression": {"type": "gloves", "stackable": False, "value": 80000, "aliases": "brace of slayer,brace of aggro,brace of aggression,slayer bracelet,slayer brace,aggro bracelet,aggro brace,bracelet of aggression,bracelet of aggro"},

    # Range Armour
    "Scaleweave coif": {"type": "helm", "style": "range", "d_magic": 4, "d_range": 4, "stackable": False, "value": 4000, "aliases": "scaleweave coif,sw coif"},
    "Scaleweave body": {"type": "body", "style": "range", "d_magic": 12, "d_range": 8, "str_range": 2, "stackable": False, "value": 8000, "aliases": "scaleweave body,sw body"},
    "Scaleweave chaps": {"type": "legs", "style": "range", "d_magic": 8, "d_range": 4, "str_range": 1, "stackable": False, "value": 6000, "aliases": "scaleweave chaps,sw chaps"},
    "Scaleweave boots": {"type": "boots", "style": "range", "d_magic": 4, "d_range": 4, "str_range": 1, "stackable": False, "value": 3500, "aliases": "scaleweave boots,sw boots"},
    "Scaleweave vambraces": {"type": "gloves", "style": "range", "d_magic": 4, "d_range": 4, "str_range": 1, "stackable": False, "value": 3000, "aliases": "scaleweave vambraces,sw vambraces,scaleweave vambs"},
    "Drakescale body": {"type": "body", "style": "range", "d_magic": 24, "d_range": 16, "str_range": 6, "stackable": False, "value": 30000, "aliases": "drakescale body,drake body"},
    "Drakescale chaps": {"type": "legs", "style": "range", "d_magic": 16, "d_range": 12, "str_range": 4, "stackable": False, "value": 22000, "aliases": "drakescale chaps,drake chaps"},
    "Voidfire coif": {"type": "helm", "style": "range", "d_stab": 4, "d_slash": 4, "d_crush": 4, "d_magic": 16, "d_range": 12, "str_range": 4, "stackable": False, "value": 55000, "aliases": "voidfire coif,vf coif"},
    "Voidfire body": {"type": "body", "style": "range", "d_stab": 4, "d_slash": 4, "d_crush": 4, "d_magic": 36, "d_range": 24, "str_range": 12, "stackable": False, "value": 100000, "aliases": "voidfire body,vf body"},
    "Voidfire chaps": {"type": "legs", "style": "range", "d_stab": 4, "d_slash": 4, "d_crush": 4, "d_magic": 24, "d_range": 16, "str_range": 8, "stackable": False, "value": 75000, "aliases": "voidfire chaps,vf chaps"},
    "Voidfire boots": {"type": "boots", "style": "range", "d_stab": 4, "d_slash": 4, "d_crush": 4, "d_magic": 16, "d_range": 12, "str_range": 4, "stackable": False, "value": 50000, "aliases": "voidfire boots,vf boots"},
    "Voidfire vambraces": {"type": "gloves", "style": "range", "d_stab": 4, "d_slash": 4, "d_crush": 4, "d_magic": 12, "d_range": 8, "str_range": 4, "stackable": False, "value": 45000, "aliases": "voidfire vambraces,vf vambraces,voidfire vambs"},

    # Magic Armour
    "Thornweave helm": {"type": "helm", "style": "magic", "d_stab": 4, "d_slash": 4, "d_crush": 4, "d_magic": 4, "stackable": False, "value": 4000, "aliases": "thornweave helm,tw helm"},
    "Thornweave body": {"type": "body", "style": "magic", "d_stab": 12, "d_slash": 12, "d_crush": 8, "d_magic": 8, "str_magic": 2, "stackable": False, "value": 8000, "aliases": "thornweave body,tw body"},
    "Thornweave legs": {"type": "legs", "style": "magic", "d_stab": 8, "d_slash": 8, "d_crush": 4, "d_magic": 4, "str_magic": 1, "stackable": False, "value": 6000, "aliases": "thornweave legs,tw legs"},
    "Thornweave boots": {"type": "boots", "style": "magic", "d_stab": 4, "d_slash": 4, "d_crush": 4, "d_magic": 4, "str_magic": 1, "stackable": False, "value": 3500, "aliases": "thornweave boots,tw boots"},
    "Thornweave gloves": {"type": "gloves", "style": "magic", "d_stab": 4, "d_slash": 4, "d_crush": 4, "d_magic": 4, "str_magic": 1, "stackable": False, "value": 3000, "aliases": "thornweave gloves,tw gloves"},
    "Wraithcaller's robetop": {"type": "body", "style": "magic", "d_stab": 24, "d_slash": 24, "d_crush": 16, "d_magic": 16, "str_magic": 6, "stackable": False, "value": 35000, "aliases": "wraithcaller robetop,wraithcaller top,wc top"},
    "Wraithcaller's robeskirt": {"type": "legs", "style": "magic", "d_stab": 16, "d_slash": 16, "d_crush": 12, "d_magic": 12, "str_magic": 4, "stackable": False, "value": 25000, "aliases": "wraithcaller robeskirt,wraithcaller skirt,wc skirt"},
    "Soulfire hat": {"type": "helm", "style": "magic", "d_stab": 16, "d_slash": 16, "d_crush": 12, "d_magic": 12, "str_magic": 4, "stackable": False, "value": 55000, "aliases": "soulfire hat,sf hat"},
    "Soulfire robetop": {"type": "body", "style": "magic", "d_stab": 36, "d_slash": 36, "d_crush": 24, "d_magic": 24, "d_range": 4, "str_magic": 12, "stackable": False, "value": 100000, "aliases": "soulfire robetop,soulfire top,sf top"},
    "Soulfire robeskirt": {"type": "legs", "style": "magic", "d_stab": 24, "d_slash": 24, "d_crush": 16, "d_magic": 16, "d_range": 4, "str_magic": 8, "stackable": False, "value": 75000, "aliases": "soulfire robeskirt,soulfire skirt,sf skirt"},
    "Soulfire boots": {"type": "boots", "style": "magic", "d_stab": 16, "d_slash": 16, "d_crush": 12, "d_magic": 12, "d_range": 4, "str_magic": 4, "stackable": False, "value": 50000, "aliases": "soulfire boots,sf boots"},
    "Soulfire gloves": {"type": "gloves", "style": "magic", "d_stab": 12, "d_slash": 12, "d_crush": 8, "d_magic": 8, "str_magic": 4, "stackable": False, "value": 45000, "aliases": "soulfire gloves,sf gloves"},

    # Necro Armour
    "Ghostweave hood": {"type": "helm", "style": "necro", "d_stab": 4, "d_slash": 4, "d_crush": 4, "d_magic": 4, "d_range": 4, "d_necro": 4, "stackable": False, "value": 4500, "aliases": "ghostweave hood,gw hood"},
    "Ghostweave robetop": {"type": "body", "style": "necro", "d_stab": 4, "d_slash": 4, "d_crush": 4, "d_magic": 4, "d_range": 4, "d_necro": 12, "str_necro": 2, "stackable": False, "value": 10000, "aliases": "ghostweave top,gw top"},
    "Ghostweave robeskirt": {"type": "legs", "style": "necro", "d_stab": 4, "d_slash": 4, "d_crush": 4, "d_magic": 4, "d_range": 4, "d_necro": 8, "str_necro": 1, "stackable": False, "value": 7000, "aliases": "ghostweave skirt,gw skirt"},
    "Ghostweave boots": {"type": "boots", "style": "necro", "d_stab": 4, "d_slash": 4, "d_crush": 4, "d_magic": 4, "d_range": 4, "d_necro": 4, "str_necro": 1, "stackable": False, "value": 4000, "aliases": "ghostweave boots,gw boots"},
    "Ghostweave gloves": {"type": "gloves", "style": "necro", "d_stab": 4, "d_slash": 4, "d_crush": 4, "d_magic": 4, "d_range": 4, "d_necro": 4, "str_necro": 1, "stackable": False, "value": 3500, "aliases": "ghostweave gloves,gw gloves"},
    "Deathwarden robetop": {"type": "body", "style": "necro", "d_stab": 8, "d_slash": 8, "d_crush": 8, "d_magic": 8, "d_range": 8, "d_necro": 24, "str_necro": 6, "stackable": False, "value": 40000, "aliases": "deathwarden top,dw top"},
    "Deathwarden robeskirt": {"type": "legs", "style": "necro", "d_stab": 8, "d_slash": 8, "d_crush": 4, "d_magic": 4, "d_range": 4, "d_necro": 16, "str_necro": 4, "stackable": False, "value": 30000, "aliases": "deathwarden skirt,dw skirt"},
    "Netharis's hood": {"type": "helm", "style": "necro", "d_stab": 8, "d_slash": 8, "d_crush": 4, "d_magic": 8, "d_range": 4, "d_necro": 16, "str_necro": 4, "stackable": False, "value": 60000, "aliases": "netharis hood,nh hood"},
    "Netharis's robetop": {"type": "body", "style": "necro", "d_stab": 12, "d_slash": 12, "d_crush": 8, "d_magic": 12, "d_range": 8, "d_necro": 36, "str_necro": 12, "stackable": False, "value": 110000, "aliases": "netharis robetop,netharis top,nh top"},
    "Netharis's robeskirt": {"type": "legs", "style": "necro", "d_stab": 8, "d_slash": 8, "d_crush": 4, "d_magic": 8, "d_range": 4, "d_necro": 24, "str_necro": 8, "stackable": False, "value": 85000, "aliases": "netharis robeskirt,netharis skirt,nh skirt"},
    "Netharis's boots": {"type": "boots", "style": "necro", "d_stab": 8, "d_slash": 8, "d_crush": 4, "d_magic": 8, "d_range": 4, "d_necro": 16, "str_necro": 4, "stackable": False, "value": 55000, "aliases": "netharis boots,nh boots"},
    "Netharis's gloves": {"type": "gloves", "style": "necro", "d_stab": 4, "d_slash": 4, "d_crush": 4, "d_magic": 4, "d_range": 4, "d_necro": 12, "str_necro": 4, "stackable": False, "value": 50000, "aliases": "netharis gloves,nh gloves"},

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
    "Omnigem Amulet": {"type": "misc", "stackable": False, "value": 60000, "aliases": "omnigem amulet,omni amulet,omnigem ammy", "image": _IMG_BASE + "omnigem%20amulet.png"},
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
    "Air rune": {"type": "rune", "multiplier": 1, "stackable": True, "value": 100, "aliases": "air rune,air runes,airs"},
    "Water rune": {"type": "rune", "multiplier": 1, "stackable": True, "value": 100, "aliases": "water rune,water runes,waters"},
    "Earth rune": {"type": "rune", "multiplier": 1, "stackable": True, "value": 100, "aliases": "earth rune,earth runes,earths"},
    "Fire rune": {"type": "rune", "multiplier": 1, "stackable": True, "value": 150, "aliases": "fire rune,fire runes,fires"},
    # Arrows (ammo)
    "Bronze arrows": {"type": "ammo", "ammo_type": "arrow", "str_range": 8, "stackable": True, "value": 10, "aliases": "bronze arrow,bronze arrows"},
    "Iron arrows": {"type": "ammo", "ammo_type": "arrow", "str_range": 12, "stackable": True, "value": 25, "aliases": "iron arrow,iron arrows"},
    "Steel arrows": {"type": "ammo", "ammo_type": "arrow", "str_range": 16, "stackable": True, "value": 50, "aliases": "steel arrow,steel arrows"},
    "Mithril arrows": {"type": "ammo", "ammo_type": "arrow", "str_range": 20, "stackable": True, "value": 100, "aliases": "mithril arrow,mithril arrows,mith arrows"},
    "Adamant arrows": {"type": "ammo", "ammo_type": "arrow", "str_range": 28, "stackable": True, "value": 200, "aliases": "adamant arrow,adamant arrows,addy arrows"},
    "Rune arrows": {"type": "ammo", "ammo_type": "arrow", "str_range": 40, "stackable": True, "value": 400, "aliases": "rune arrow,rune arrows"},
    "Dragon arrows": {"type": "ammo", "ammo_type": "arrow", "str_range": 60, "stackable": True, "value": 800, "aliases": "dragon arrow,dragon arrows,d arrows"},
    "Bone bolts": {"type": "ammo", "ammo_type": "bolt", "str_range": 36, "stackable": True, "value": 600, "aliases": "bone bolt,bone bolts,bbolts"},
    "Mysterious key": {"type": "misc", "stackable": True, "value": 30000, "aliases": "mysterious key,key,keys"},
    # Pets
    "Tiny Revenant": {"type": "misc", "stackable": False, "value": 0, "aliases": "tiny revenant,rev pet"},
    "Baby Chaos Fanatic": {"type": "misc", "stackable": False, "value": 0, "aliases": "baby chaos fanatic,fanatic pet"},
    "Mini Overlord": {"type": "misc", "stackable": False, "value": 0, "aliases": "mini overlord,overlord pet"},
    "Lil' Undying": {"type": "misc", "stackable": False, "value": 0, "aliases": "lil undying,undying pet"},
    "Zarvethy": {"type": "misc", "stackable": False, "value": 0, "aliases": "zarvethy,zarveth pet,veilbreaker pet"},
    "Splat": {"type": "misc", "stackable": False, "value": 0, "aliases": "splat,valthyros pet"},
    "Flickerwisp": {"type": "misc", "stackable": False, "value": 0, "aliases": "flickerwisp,flicker"},
    "Tiny Dark Archer": {"type": "misc", "stackable": False, "value": 0, "aliases": "tiny dark archer,dark archer pet,tda"},
    "Soulflame": {"type": "misc", "stackable": False, "value": 0, "aliases": "soulflame,soul flame"},
    "Embersprite": {"type": "misc", "stackable": False, "value": 0, "aliases": "embersprite,ember sprite"},

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
    "Viggora's Chainmace": {"effect": "Grants +80 strength against ALL NPCs at a cost of 3 Revenant ether per hit (no bonus in PvP)."},
    "Abyssal Chainmace": {"effect": "Grants +136 strength against ALL NPCs at a cost of 3 Revenant ether per hit (no bonus in PvP)."},
    "Amulet of Seeping": {"effect": "Heals 1 + 2% of damage dealt at the cost of 5 Blood runes per successful hit."},
    "Shroud of the Undying": {"effect": "2% chance to completely nullify incoming damage on any hit."},
    "Slayer Helmet": {"effect": "When worn, increases damage dealt to your current slayer task NPC by 20%."},
    "Shady Slayer Helm": {"effect": "When worn, increases damage dealt to your current slayer task NPC by 27%."},
    "Bracelet of Slayer Aggression": {"effect": "When worn, guarantees finding your slayer task NPC when using !w fight <npc>. Costs 20 Chaos runes per fight."},
    # Potions
    "Strength (4)": {"effect": "Drink with `!w drink`. Grants +2 strength for 10 hits. 4 doses."},
    "Strength (3)": {"effect": "Drink with `!w drink`. Grants +2 strength for 10 hits. 3 doses remaining."},
    "Strength (2)": {"effect": "Drink with `!w drink`. Grants +2 strength for 10 hits. 2 doses remaining."},
    "Strength (1)": {"effect": "Drink with `!w drink`. Grants +2 strength for 10 hits. 1 dose remaining."},
    "Super Strength (4)": {"effect": "Drink with `!w drink`. Grants +4 strength for 20 hits. 4 doses."},
    "Super Strength (3)": {"effect": "Drink with `!w drink`. Grants +4 strength for 20 hits. 3 doses remaining."},
    "Super Strength (2)": {"effect": "Drink with `!w drink`. Grants +4 strength for 20 hits. 2 doses remaining."},
    "Super Strength (1)": {"effect": "Drink with `!w drink`. Grants +4 strength for 20 hits. 1 dose remaining."},
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
    "Eclipse of the Five": {"effect": "When worn, grants +24 melee strength and +8 magic/range/necro strength, but reduces all defences by 1. Crafted from an Omnigem Amulet via `!w enchant`."},
    "Omnigem Amulet": {"effect": "An unenchanted amulet. Use `!w enchant omnigem amulet` to create Eclipse of the Five."},
    "Omnigem": {"effect": "A fused gem containing all five gem types. Used to craft an Omnigem Amulet."},
    # Range weapons
    "Rotwood shortbow": {"effect": "Fires any arrows. 20% chance to consume 1 arrow per hit."},
    "Whisperwood bow": {"effect": "Fires any arrows. 20% chance to consume 1 arrow per hit."},
    "Ironwood bow": {"effect": "Fires any arrows. 20% chance to consume 1 arrow per hit."},
    "Hexwood bow": {"effect": "Fires any arrows. 20% chance to consume 1 arrow per hit."},
    "Bone crossbow": {"effect": "Fires Bone bolts. 20% chance to consume 1 bolt per hit."},
    "Nightfall bow": {"effect": "A devastating two-handed range weapon. Fires any arrows. 20% chance to consume 1 arrow per hit."},
    # Magic weapons
    "Galestaff": {"effect": "Channels Air runes. 20% chance to consume 1 rune per hit."},
    "Tidestaff": {"effect": "Channels Water runes. 20% chance to consume 1 rune per hit."},
    "Stonestaff": {"effect": "Channels Earth runes. 20% chance to consume 1 rune per hit."},
    "Flamestaff": {"effect": "Channels Fire runes. 20% chance to consume 1 rune per hit."},
    "Voidtouched wand": {"effect": "Channels Death runes. 20% chance to consume 1 rune per hit."},
    "Soulfire staff": {"effect": "A devastating two-handed magic weapon. Channels Blood runes. 20% chance to consume 1 rune per hit."},
    # Necro weapons
    "Spectral scythe": {"effect": "A mid-tier necromancy scythe."},
    "Deathwarden staff": {"effect": "A powerful two-handed necromancy staff."},
    "Netharis's Grasp": {"effect": "The most powerful necromancy weapon, wrested from Netharis herself."},
    # Offhands
    "Voidfire Quiver": {"effect": "A range offhand that boosts accuracy and strength."},
    "Cindertome": {"effect": "A magic offhand that boosts accuracy and strength."},
    "Soulbound Grimoire": {"effect": "A necromancy offhand that boosts accuracy and strength."},
}

GEM_CUTTING = {
    "Uncut sapphire": "Sapphire",
    "Uncut emerald": "Emerald",
    "Uncut ruby": "Ruby",
    "Uncut diamond": "Diamond",
    "Uncut dragonstone": "Dragonstone",
}
