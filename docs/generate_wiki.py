#!/usr/bin/env python3
"""
Wiki Generator — creates ALL HTML pages for NPCs and items from game data.
Run from the docs/ directory:  python generate_wiki.py
"""
import os, sys, json, html as html_mod

# Add parent so we can import game data
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from wildygame.npcs import NPCS, NPC_DROPS
from wildygame.items import ITEMS, ITEM_EFFECTS, FOOD, UNTRADEABLE

DOCS = os.path.dirname(os.path.abspath(__file__))
NPC_DIR = os.path.join(DOCS, "npcs")
ITEM_DIR = os.path.join(DOCS, "items")
GE_DIR = os.path.join(DOCS, "grand-exchange")

# ─── Helpers ─────────────────────────────────────────────────────────────

def esc(s):
    return html_mod.escape(str(s))

def slug(name):
    return name.lower().replace("'", "").replace("\u2019", "").replace(".", "").replace(",", "").replace("(", "").replace(")", "").replace(" ", "-")

STANCE_TO_STYLE = {"stab": "melee", "slash": "melee", "crush": "melee",
                   "magic": "magic", "range": "range", "necro": "necro"}

def stat_val(v):
    """Format a stat value with colored span."""
    if v > 0:
        return f'<span class="stat-pos">+{v}</span>'
    elif v < 0:
        return f'<span class="stat-neg">{v}</span>'
    else:
        return '<span class="stat-zero">0</span>'

_STYLE_DISP = {"melee": "Melee", "magic": "Magic", "range": "Range", "necro": "Necromancy"}
_STANCE_DISP = {"stab": "Stab", "slash": "Slash", "crush": "Crush", "magic": "Magic", "range": "Range", "necro": "Necromancy"}
def _style_disp(s): return _STYLE_DISP.get(s, s.capitalize())
def _stance_disp(s): return _STANCE_DISP.get(s, s.capitalize())

def img_relative(url):
    """Convert a full GitHub URL to a relative path from npcs/ or items/ dir."""
    if not url:
        return None
    marker = "/docs/"
    idx = url.find(marker)
    if idx >= 0:
        rel = url[idx + len(marker):]
        return "../" + rel
    return None

# ─── Shared HTML fragments ──────────────────────────────────────────────

NAVBAR = '''  <div class="navbar">
    <div class="logo"><span>Wilderness</span> Wiki</div>
    <nav>
      <a href="{home}index.html">Home</a>
      <a href="{home}npcs/index.html"{npc_active}>NPCs</a>
      <a href="{home}items/index.html"{item_active}>Items</a>
      <a href="{home}commands/index.html">Commands</a>
      <a href="{home}grand-exchange/index.html"{ge_active}>Grand Exchange</a>
    </nav>
      <a href="https://discord.com/invite/paws-of-fury" target="_blank" class="discord-btn"><svg viewBox="0 0 24 24"><path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028c.462-.63.874-1.295 1.226-1.994a.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03z"/></svg>Join Discord</a>
    <div class="search-wrapper">
      <input type="text" class="search-input" placeholder="Search wiki...">
      <div class="search-dropdown"></div>
    </div>
  </div>'''

NO_IMG = '<div class="infobox-image" style="display:flex;align-items:center;justify-content:center;min-height:120px;color:#8b949e;">No image</div>'
NO_IMG_CARD = '<div class="npc-card-image" style="display:flex;align-items:center;justify-content:center;color:#8b949e;font-size:0.85em;">No image</div>'

# ─── NPC Descriptions ───────────────────────────────────────────────────

NPC_DESCRIPTIONS = {
    "revenant goblin": "The Revenant Goblin is a restless spirit that haunts the Wilderness. Once a lowly goblin in life, it now wanders the wasteland as a flickering ghost, driven by an insatiable hunger for the living.",
    "revenant imp": "The Revenant Imp is a spectral creature that haunts the Wilderness with a bow in hand. Once a mischievous imp in life, it now fires ghostly arrows at any adventurer foolish enough to wander too close.",
    "wandering_warlock": "The Wandering Warlock is a restless mage who roams the Wilderness, hurling arcane blasts at anyone who crosses its path. Its magical attacks can catch unprepared adventurers off guard.",
    "cursed_spirit": "The Cursed Spirit is a tormented soul bound to the Wilderness by dark necromantic energy. It lashes out with spectral claws, draining the life force of those who dare approach.",
    "feral_scorpion": "The Feral Scorpion is a vicious creature that lurks in the shallow Wilderness. Its pincers deliver crushing blows, making it a dangerous foe for the unarmoured.",
    "revenant knight": "The Revenant Knight is the ghostly remains of a once-noble warrior. Clad in spectral armour and wielding an ethereal blade, it patrols the mid-level Wilderness with deadly precision.",
    "revenant pyromancer": "The Revenant Pyromancer is a ghostly mage that wields fire magic. In life it was a sorcerer; in death, its flames burn even hotter.",
    "corrupted_ranger": "The Corrupted Ranger is a fallen archer twisted by dark energy. Its arrows fly true and strike with unnatural precision, making it a formidable ranged threat.",
    "shade": "The Shade is a dark entity that exists between life and death. It attacks with necromantic energy, draining the very essence of its victims.",
    "infernal_imp": "The Infernal Imp is a demonic creature from the depths of the Wilderness. Its crushing blows are powered by hellfire, dealing heavy melee damage.",
    "chaos_fanatic": "The Chaos Fanatic is a deranged mage who has made the Wilderness his domain. He bombards adventurers with chaotic magical attacks while cackling maniacally. Despite his madness, he guards valuable treasures.",
    "phantom_archer": "The Phantom Archer is a spectral marksman that haunts the mid-level Wilderness. Its ghostly arrows are nearly impossible to dodge, making it a formidable ranged threat.",
    "risen_bonecaller": "The Risen Bonecaller is a necromancer that commands the dead. It attacks with bone magic and can summon spectral minions to aid in combat.",
    "windstrider": "The Windstrider is a swift and deadly ranged boss that dashes through the Wilderness with supernatural speed. Its Evasive Dash ability allows it to dodge incoming attacks entirely.",
    "infernal_warlock": "The Infernal Warlock is a magic boss that commands fire spells. Its Infernal Blaze ability supercharges its attacks, dealing bonus fire damage for several hits.",
    "revenant necro": "The Revenant Necromancer is an elite revenant that haunts the deep Wilderness. It commands dark necromantic magic to raise the dead and unleash deadly attacks on the living.",
    "revenant demon": "The Revenant Abyssal Demon is a ghostly beast that combines the raw power of an abyssal demon with the ethereal nature of a revenant. Its slashing attacks can tear through heavy armour.",
    "blight cyclops": "The Blighted Cyclops is a one-eyed monstrosity corrupted by dark energy. It swings its massive fists with crushing force, and occasionally drops defenders for warriors brave enough to challenge it.",
    "overlord": "The Abyssal Overlord is a massive abyssal creature that rules over the deep Wilderness. Its crushing attacks hit hard, and it guards valuable loot.",
    "valthyros": "Lord Valthyros is a magical entity who has claimed a portion of the Wilderness as his domain. His arcane attacks are dangerous, and his defensive magic makes him difficult to damage with physical attacks.",
    "revenant archon": "The Revenant Archon is an elite revenant warrior and a formidable ghostly combatant. Once a legendary champion in life, it now patrols the deep Wilderness as a relentless spectral force.",
    "hollow_warden": "The Hollow Warden is a massive stone golem that guards the deep Wilderness. Though it drops no unique items, it yields large quantities of resources. Its Stone Shell ability halves incoming damage temporarily.",
    "veilbreaker": "Zarveth the Veilbreaker is a fearsome warrior who shattered the barrier between life and death. He wields great strength and guards coveted melee equipment.",
    "masked_figure": "The Masked Figure is a mysterious assassin who stalks the deepest parts of the Wilderness. Nobody knows who hides behind the mask, but its precision strikes and deadly combat style have claimed countless adventurers.",
    "duskwalker": "The Duskwalker is a ranged boss that stalks the deepest parts of the Wilderness. Its Shadow Volley ability allows it to fire two volleys in rapid succession, overwhelming adventurers.",
    "emberlord": "Emberlord Kael is a magic boss wreathed in eternal flame. Its Flame Burst ability deals unavoidable fire damage, and it guards sought-after magic equipment.",
    "gravekeeper": "Gravekeeper Azriel is a necromancy boss that commands armies of the dead from its throne in the deepest Wilderness. Its Soul Siphon ability heals it while weakening its target's defences.",
    "netharis": "Netharis the Undying is an ancient necromantic entity that commands overwhelming dark magic. She is feared throughout the Wilderness, and only well-equipped adventurers dare face her.",
}

NPC_SPECIALS = {
    "windstrider": "Evasive Dash (10%) \u2014 Dodges the player's next attack entirely",
    "infernal_warlock": "Infernal Blaze (8%) \u2014 NPC's attacks deal +3 bonus fire damage for 3 hits",
    "hollow_warden": "Stone Shell (10%) \u2014 Player's damage is halved for 3 hits",
    "duskwalker": "Shadow Volley (8%) \u2014 NPC attacks twice this turn",
    "emberlord": "Flame Burst (10%) \u2014 Deals 5 flat unavoidable damage to the player",
    "gravekeeper": "Soul Siphon (12%) \u2014 Heals for 100% of damage dealt and reduces player defence by 3 for 4 hits",
    "valthyros": "Dark Binding (10%) \u2014 Reduces player's defence by 3 for 4 hits",
    "veilbreaker": "Veil Rend (8%) \u2014 Deals bonus damage that ignores defence",
    "netharis": "Undying Grasp (12%) \u2014 Heals Netharis and reduces player's defence",
}

# ─── NPC page generator ─────────────────────────────────────────────────

def generate_npc_page(npc, drops):
    name = npc["name"]
    e_name = esc(name)
    nt = npc.get("npc_type", "")
    hp = npc.get("hp", 0)
    min_w = npc.get("min_wildy", 1)
    stance = npc.get("stance", "stab")
    style = STANCE_TO_STYLE.get(stance, "melee")

    # Attack power
    str_keys = {"melee": "str_melee", "range": "str_range", "magic": "str_magic", "necro": "str_necro"}
    atk = npc.get(str_keys.get(style, "str_melee"), 0)

    slayer_lv = npc.get("slayer_level", 1)
    slayer_xp = npc.get("slayer_xp", 0)
    special = NPC_SPECIALS.get(nt, "None")
    desc = NPC_DESCRIPTIONS.get(nt, f"{e_name} is a creature found in the Wilderness.")

    # Image
    img_url = npc.get("image", "")
    img_rel = img_relative(img_url)
    if img_rel:
        img_html = f'<div class="infobox-image"><img src="{esc(img_rel)}" alt="{e_name}"></div>'
    else:
        img_html = NO_IMG

    navbar = NAVBAR.format(home="../", npc_active=' class="active"', item_active="", ge_active="")

    # Defence bonuses
    d_stab = npc.get("d_stab", 0)
    d_slash = npc.get("d_slash", 0)
    d_crush = npc.get("d_crush", 0)
    d_magic = npc.get("d_magic", 0)
    d_range = npc.get("d_range", 0)
    d_necro = npc.get("d_necro", 0)

    # Drop table HTML
    drop_html = build_drop_table_html(drops)

    # Ability box in content
    ability_html = ""
    if special != "None":
        ability_html = (
            '\n        <div class="ability-box">'
            '\n          <div class="ability-name">Special Ability</div>'
            '\n          <p>' + esc(special) + '</p>'
            '\n        </div>')

    # Pre-compute ability short name for infobox
    em_dash = "\u2014"
    ability_short = special.split(" " + em_dash)[0] if special != "None" else "None"

    page = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{e_name} \u2014 Wilderness Wiki</title>
  <link rel="stylesheet" href="../style.css">
</head>
<body>
{navbar}
  <div class="container">
    <div class="breadcrumb"><a href="../index.html">Home</a><span class="sep">/</span><a href="index.html">NPCs</a><span class="sep">/</span>{e_name}</div>
    <div class="npc-layout">
      <div class="content">
        <h1>{e_name}</h1>
        <p>{desc}</p>
{ability_html}
{drop_html}
      </div>
      <div class="infobox">
        {img_html}
        <div class="infobox-name">{e_name}</div>
        <div class="infobox-stats">
          <div class="infobox-header">Combat Info</div>
          <div class="infobox-row"><span class="infobox-label">Wilderness Level</span><span class="infobox-value">{min_w}+</span></div>
          <div class="infobox-row"><span class="infobox-label">Health</span><span class="infobox-value">{hp}</span></div>
          <div class="infobox-row"><span class="infobox-label">Attack Style</span><span class="infobox-value">{esc(_style_disp(style))} ({esc(_stance_disp(stance))})</span></div>
          <div class="infobox-row"><span class="infobox-label">Attack Strength</span><span class="infobox-value">{atk}</span></div>
          <div class="infobox-row"><span class="infobox-label">Ability</span><span class="infobox-value">{esc(ability_short)}</span></div>
          <div class="infobox-header">Defence Bonuses</div>
          <div class="infobox-row"><span class="infobox-label">Stab</span><span class="infobox-value">{stat_val(d_stab)}</span></div>
          <div class="infobox-row"><span class="infobox-label">Slash</span><span class="infobox-value">{stat_val(d_slash)}</span></div>
          <div class="infobox-row"><span class="infobox-label">Crush</span><span class="infobox-value">{stat_val(d_crush)}</span></div>
          <div class="infobox-row"><span class="infobox-label">Magic</span><span class="infobox-value">{stat_val(d_magic)}</span></div>
          <div class="infobox-row"><span class="infobox-label">Range</span><span class="infobox-value">{stat_val(d_range)}</span></div>
          <div class="infobox-row"><span class="infobox-label">Necromancy</span><span class="infobox-value">{stat_val(d_necro)}</span></div>
          <div class="infobox-header">Slayer Info</div>
          <div class="infobox-row"><span class="infobox-label">Slayer Level</span><span class="infobox-value">{slayer_lv}</span></div>
          <div class="infobox-row"><span class="infobox-label">Slayer XP</span><span class="infobox-value">{slayer_xp}</span></div>
        </div>
      </div>
    </div>
  </div>
  <div class="footer">Wilderness Wiki</div>
  <script src="../search.js"></script>
</body>
</html>
'''
    return page

# ─── Drop table builder ─────────────────────────────────────────────────

def build_drop_table_html(drops):
    if not drops:
        return ""
    coins = drops.get("coins_range")
    loot = drops.get("loot", [])
    unique = drops.get("unique", [])
    pet = drops.get("pet", [])

    html = '\n        <details class="drop-section" open>\n        <summary><h2>Drop Table</h2></summary>\n'

    if coins:
        html += f'\n        <details class="drop-inner" open>\n        <summary><h3>Coins</h3></summary>\n        <p>{coins[0]:,}&ndash;{coins[1]:,} coins</p>\n        </details>\n'

    if loot:
        html += drop_table_section("Loot", loot, "")

    if unique:
        html += drop_table_section("Unique", unique, "drop-unique")

    if pet:
        html += drop_table_section("Pet", pet, "drop-pet")

    html += '\n        </details>'
    return html


def drop_table_section(title, entries, css_class):
    cls = f' class="{css_class}"' if css_class else ""
    html = f'\n        <details class="drop-inner" open>\n        <summary><h3>{title}</h3></summary>\n        <table>\n          <thead>\n            <tr>\n              <th>Item</th>\n              <th>Quantity</th>\n              <th>Drop Rate</th>\n            </tr>\n          </thead>\n          <tbody>\n'
    for entry in entries:
        item_name = entry.get("item", "")
        mn = entry.get("min", 1)
        mx = entry.get("max", 1)
        chance = entry.get("chance", "?")
        noted = " (noted)" if entry.get("noted") else ""
        qty = f"{mn}" if mn == mx else f"{mn}&ndash;{mx}"
        item_slug = slug(item_name)
        html += f'            <tr{cls}>\n              <td><a href="../items/{item_slug}.html">{esc(item_name)}</a>{noted}</td>\n              <td>{qty}</td>\n              <td>{chance}</td>\n            </tr>\n'
    html += '          </tbody>\n        </table>\n        </details>\n'
    return html

# ─── Item page generator ────────────────────────────────────────────────

EQUIP_SLOTS = {"mainhand", "offhand", "helm", "body", "legs", "boots", "gloves", "cape", "ring", "amulet", "ammo"}

def is_equippable(meta):
    t = str(meta.get("type", "")).lower()
    return any(s in t for s in EQUIP_SLOTS)

def item_slot_display(meta):
    t = str(meta.get("type", "")).lower()
    if "mainhand" in t and "offhand" in t:
        return "Two-handed"
    if "mainhand" in t:
        return "Mainhand"
    if "offhand" in t:
        return "Offhand"
    if "ammo" in t:
        return "Ammo"
    slot_map = {"helm": "Helm", "body": "Body", "legs": "Legs", "boots": "Boots",
                "gloves": "Gloves", "cape": "Cape", "ring": "Ring", "amulet": "Amulet"}
    for s, label in slot_map.items():
        if s in t:
            return label
    return t.capitalize() if t else "\u2014"

def item_style_display(meta):
    style = str(meta.get("style", "")).lower()
    t = str(meta.get("type", "")).lower()
    # Armour without an explicit style is universal
    is_armour_slot = any(s in t for s in ["helm", "body", "legs", "boots", "gloves"])
    if not style:
        if is_armour_slot:
            return "All Styles"
        # Infer from stats on the item
        for sk in ["str_melee", "a_stab", "a_slash", "a_crush"]:
            if meta.get(sk, 0):
                return "Melee"
        for sk in ["str_range", "a_range"]:
            if meta.get(sk, 0):
                return "Range"
        for sk in ["str_magic", "a_magic"]:
            if meta.get(sk, 0):
                return "Magic"
        for sk in ["str_necro", "a_necro"]:
            if meta.get(sk, 0):
                return "Necromancy"
        # Check d_* values for armour
        has_def = any(meta.get(f"d_{s}", 0) != 0 for s in ["stab", "slash", "crush", "magic", "range", "necro"])
        if has_def:
            return "All Styles"
        return "\u2014"
    return _style_disp(style)


def generate_item_page(name, meta):
    e_name = esc(name)
    effects = ITEM_EFFECTS.get(name, {})
    navbar = NAVBAR.format(home="../", npc_active="", item_active=' class="active"', ge_active="")

    t = str(meta.get("type", "")).lower()
    stackable = "Yes" if meta.get("stackable") else "No"
    equippable = "Yes" if is_equippable(meta) else "No"
    value = meta.get("value", 0)
    value_str = f"{value:,} coins" if value else "\u2014"
    slot = item_slot_display(meta)
    style = item_style_display(meta)
    consumes_raw = meta.get("consumes", "")
    consumes = {"arrow": "Any arrows", "bolt": "Bone bolts"}.get(consumes_raw, consumes_raw)
    effect_text = effects.get("effect", "")

    # Image
    img_url = meta.get("image", "")
    img_rel = img_relative(img_url)
    if img_rel:
        img_html = f'<div class="infobox-image"><img src="{esc(img_rel)}" alt="{e_name}"></div>'
    else:
        img_html = NO_IMG

    # Build infobox rows
    info_rows = []
    info_rows.append(f'          <div class="infobox-header">Info</div>')
    info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Equippable</span><span class="infobox-value">{equippable}</span></div>')
    info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Stackable</span><span class="infobox-value">{stackable}</span></div>')

    if equippable == "Yes":
        info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Slot</span><span class="infobox-value">{esc(slot)}</span></div>')
        if style != "\u2014":
            info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Style</span><span class="infobox-value">{esc(style)}</span></div>')

        # Attack bonuses (from meta directly)
        a_stab = meta.get("a_stab", 0)
        a_slash = meta.get("a_slash", 0)
        a_crush = meta.get("a_crush", 0)
        a_magic = meta.get("a_magic", 0)
        a_range = meta.get("a_range", 0)
        a_necro = meta.get("a_necro", 0)
        has_atk = any(v != 0 for v in [a_stab, a_slash, a_crush, a_magic, a_range, a_necro])

        # Defence bonuses (from meta directly)
        d_stab = meta.get("d_stab", 0)
        d_slash = meta.get("d_slash", 0)
        d_crush = meta.get("d_crush", 0)
        d_magic = meta.get("d_magic", 0)
        d_range = meta.get("d_range", 0)
        d_necro = meta.get("d_necro", 0)
        has_def = any(v != 0 for v in [d_stab, d_slash, d_crush, d_magic, d_range, d_necro])

        # Strength bonuses (from meta directly)
        str_melee = meta.get("str_melee", 0)
        str_range = meta.get("str_range", 0)
        str_magic = meta.get("str_magic", 0)
        str_necro = meta.get("str_necro", 0)
        has_str = any(v != 0 for v in [str_melee, str_range, str_magic, str_necro])

        # Show Attack Bonuses section
        if has_atk:
            info_rows.append(f'          <div class="infobox-header">Attack Bonuses</div>')
            info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Stab</span><span class="infobox-value">{stat_val(a_stab)}</span></div>')
            info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Slash</span><span class="infobox-value">{stat_val(a_slash)}</span></div>')
            info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Crush</span><span class="infobox-value">{stat_val(a_crush)}</span></div>')
            info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Magic</span><span class="infobox-value">{stat_val(a_magic)}</span></div>')
            info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Range</span><span class="infobox-value">{stat_val(a_range)}</span></div>')
            info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Necromancy</span><span class="infobox-value">{stat_val(a_necro)}</span></div>')

        # Show Defence Bonuses section
        if has_def:
            info_rows.append(f'          <div class="infobox-header">Defence Bonuses</div>')
            info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Stab</span><span class="infobox-value">{stat_val(d_stab)}</span></div>')
            info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Slash</span><span class="infobox-value">{stat_val(d_slash)}</span></div>')
            info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Crush</span><span class="infobox-value">{stat_val(d_crush)}</span></div>')
            info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Magic</span><span class="infobox-value">{stat_val(d_magic)}</span></div>')
            info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Range</span><span class="infobox-value">{stat_val(d_range)}</span></div>')
            info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Necromancy</span><span class="infobox-value">{stat_val(d_necro)}</span></div>')

        # Show Strength Bonuses section
        if has_str:
            info_rows.append(f'          <div class="infobox-header">Strength Bonuses</div>')
            info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Melee</span><span class="infobox-value">{stat_val(str_melee)}</span></div>')
            info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Range</span><span class="infobox-value">{stat_val(str_range)}</span></div>')
            info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Magic</span><span class="infobox-value">{stat_val(str_magic)}</span></div>')
            info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Necromancy</span><span class="infobox-value">{stat_val(str_necro)}</span></div>')

        # Special bonuses (atk_vs_npc for ether weapons)
        atk_vs_npc = meta.get("atk_vs_npc", 0)
        if atk_vs_npc:
            info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">NPC Bonus</span><span class="infobox-value">{stat_val(atk_vs_npc)}</span></div>')

        if consumes:
            info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Consumes</span><span class="infobox-value">{esc(consumes)}</span></div>')

    else:
        # Non-equippable: show type
        if t == "pet" or t == "misc" and name in PET_NAMES:
            info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Type</span><span class="infobox-value">Pet</span></div>')
        elif "rune" in t:
            info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Type</span><span class="infobox-value">Rune</span></div>')
        elif "ammo" in t:
            info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Type</span><span class="infobox-value">Ammo</span></div>')
        elif "esspouch" in t:
            ess = meta.get("essstorage", 0)
            info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Type</span><span class="infobox-value">Ess Pouch</span></div>')
            if ess:
                info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Capacity</span><span class="infobox-value">{ess}</span></div>')
        elif name in FOOD:
            info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Type</span><span class="infobox-value">Food</span></div>')
            info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Heals</span><span class="infobox-value">{FOOD[name]["heal"]} HP</span></div>')
        else:
            type_label = t.capitalize() if t else "Item"
            info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Type</span><span class="infobox-value">{esc(type_label)}</span></div>')

    info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Value</span><span class="infobox-value">{value_str}</span></div>')
    ge_price = meta.get("ge_price", 0)
    if ge_price:
        info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">GE Price</span><span class="infobox-value">{ge_price:,} coins</span></div>')

    # Effect description in content area
    effect_html = ""
    if effect_text:
        effect_html = f'''
        <div class="ability-box">
          <div class="ability-name">Special Effect</div>
          <p>{esc(effect_text)}</p>
        </div>'''

    # Build sources from NPC_DROPS
    source_rows = []
    for nt, drops in NPC_DROPS.items():
        for section in ["loot", "unique", "pet"]:
            for entry in drops.get(section, []):
                if entry.get("item", "").lower() == name.lower():
                    npc_name = nt
                    for n in NPCS:
                        if n.get("npc_type") == nt:
                            npc_name = n["name"]
                            break
                    mn = entry.get("min", 1)
                    mx = entry.get("max", 1)
                    chance = entry.get("chance", "?")
                    qty = f"{mn}" if mn == mx else f"{mn}&ndash;{mx}"
                    css_class = ' class="drop-pet"' if section == "pet" else (' class="drop-unique"' if section == "unique" else "")
                    npc_slug = slug(npc_name)
                    source_rows.append(f'            <tr{css_class}><td><a href="../npcs/{npc_slug}.html">{esc(npc_name)}</a></td><td>{qty}</td><td>{chance}</td></tr>')

    sources_html = ""
    if source_rows:
        sources_html = (
            '\n        <details class="drop-section" open>'
            '\n        <summary><h2>Sources</h2></summary>'
            '\n        <table>'
            '\n          <thead>'
            '\n            <tr>'
            '\n              <th>Source</th>'
            '\n              <th>Quantity</th>'
            '\n              <th>Drop Rate</th>'
            '\n            </tr>'
            '\n          </thead>'
            '\n          <tbody>\n'
            + "\n".join(source_rows) +
            '\n          </tbody>'
            '\n        </table>'
            '\n        </details>')

    info_rows_html = "\n".join(info_rows)

    page = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{e_name} \u2014 Wilderness Wiki</title>
  <link rel="stylesheet" href="../style.css">
</head>
<body>
{navbar}

  <div class="container">
    <div class="breadcrumb">
      <a href="../index.html">Home</a><span class="sep">/</span>
      <a href="index.html">Items</a><span class="sep">/</span>
      {e_name}
    </div>

    <div class="npc-layout">
      <div class="content">
        <h1>{e_name}</h1>
{effect_html}
{sources_html}
      </div>

      <div class="infobox">
        {img_html}
        <div class="infobox-name">{e_name}</div>
        <div class="infobox-stats">
{info_rows_html}
        </div>
      </div>
    </div>
  </div>

  <div class="footer">Wilderness Wiki</div>
  <script src="../search.js"></script>
</body>
</html>
'''
    return page

# ─── Pet names set ───────────────────────────────────────────────────────

PET_NAMES = {
    "Tiny Revenant", "Baby Chaos Fanatic", "Mini Overlord", "Lil' Undying",
    "Zarvethy", "Splat", "Flickerwisp", "Tiny Dark Archer", "Soulflame", "Embersprite",
}

# ─── Item index card stat summary ───────────────────────────────────────

def item_card_stat(name, meta):
    """Short stat string for the items index card."""
    t = str(meta.get("type", "")).lower()

    # Weapons: show primary str bonus
    if "mainhand" in t:
        for sk, label in [("str_melee", "Melee Strength"), ("str_range", "Range Strength"),
                          ("str_magic", "Magic Strength"), ("str_necro", "Necromancy Strength")]:
            v = meta.get(sk, 0)
            if v:
                return f"+{v} {label}"
        return item_slot_display(meta)

    # Offhands: show str bonus if any, else attack bonus, else def
    if "offhand" in t and "mainhand" not in t:
        for sk, label in [("str_melee", "Melee Strength"), ("str_range", "Range Strength"),
                          ("str_magic", "Magic Strength"), ("str_necro", "Necromancy Strength")]:
            v = meta.get(sk, 0)
            if v:
                return f"+{v} {label}"
        for ak, label in [("a_stab", "Stab Attack"), ("a_slash", "Slash Attack"), ("a_crush", "Crush Attack"),
                          ("a_magic", "Magic Attack"), ("a_range", "Range Attack"), ("a_necro", "Necromancy Attack")]:
            v = meta.get(ak, 0)
            if v:
                return f"+{v} {label}"
        # Defence only
        best_d = 0
        best_label = ""
        for dk, label in [("d_stab", "Stab Defence"), ("d_slash", "Slash Defence"), ("d_crush", "Crush Defence"),
                          ("d_magic", "Magic Defence"), ("d_range", "Range Defence"), ("d_necro", "Necromancy Defence")]:
            v = meta.get(dk, 0)
            if v > best_d:
                best_d = v
                best_label = label
        if best_d:
            return f"+{best_d} {best_label}"
        return "Offhand"

    # Armour: show str bonus if any, else highest def
    slot = item_slot_display(meta)
    for sk, label in [("str_melee", "Melee Strength"), ("str_range", "Range Strength"),
                      ("str_magic", "Magic Strength"), ("str_necro", "Necromancy Strength")]:
        v = meta.get(sk, 0)
        if v:
            return f"+{v} {label}"

    # Show highest positive d_* value
    best_d = 0
    best_label = ""
    for dk, label in [("d_stab", "Stab"), ("d_slash", "Slash"), ("d_crush", "Crush"),
                      ("d_magic", "Magic"), ("d_range", "Range"), ("d_necro", "Necromancy")]:
        v = meta.get(dk, 0)
        if v > best_d:
            best_d = v
            best_label = label
    if best_d:
        return f"+{best_d} {best_label} Defence"

    # Non-combat: type label
    if name in PET_NAMES:
        return "Pet"
    if t == "ammo":
        return "Ammo"
    if t == "rune":
        return "Rune"
    if name in FOOD:
        return f"Heals {FOOD[name]['heal']}"
    if "esspouch" in t:
        ess = meta.get("essstorage", 0)
        return f"Holds {ess} ess" if ess else "Pouch"
    return slot if slot != "\u2014" else "Item"

# ─── Item categorization for index ──────────────────────────────────────

ARMOUR_SLOTS = {"helm", "body", "legs", "boots"}

def categorize_item(name, meta):
    t = str(meta.get("type", "")).lower()
    style = str(meta.get("style", "")).lower()

    # Two-handed weapons
    if "mainhand" in t and "offhand" in t:
        if style == "range": return "range_weapons"
        if style == "magic": return "magic_weapons"
        if style == "necro": return "necro_weapons"
        return "melee_weapons"

    # Mainhand weapons
    if "mainhand" in t:
        if style == "necro": return "necro_weapons"
        if style == "magic": return "magic_weapons"
        if style == "range": return "range_weapons"
        return "melee_weapons"

    # Offhands (not two-handed)
    if "offhand" in t:
        return "offhands"

    # Ammo
    if t == "ammo":
        return "ammo"

    # Runes
    if t == "rune":
        return "runes"

    # Pets
    if name in PET_NAMES:
        return "pets"

    # Potions
    if "strength" in name.lower() and "(" in name:
        return "potions"

    # Ess pouches
    if "esspouch" in t:
        return "miscellaneous"

    # Armour slots
    for slot_key in ARMOUR_SLOTS:
        if slot_key in t:
            return "armour"

    # Gloves - check if it's armour or accessory
    if "gloves" in t:
        # Items with combat stats are armour; special gloves (bracelet of ethereum, etc.) are accessories
        has_combat = any(meta.get(k, 0) for k in ["d_stab", "d_slash", "d_crush", "d_magic", "d_range", "d_necro", "str_melee", "str_range", "str_magic", "str_necro"])
        if has_combat:
            return "armour"
        return "accessories"

    # Accessories
    if any(s in t for s in ["amulet", "ring", "cape"]):
        return "accessories"

    # Food
    if name in FOOD:
        return "food"

    # Valuables (keys, emblems, gems)
    if name in {"Mysterious key", "Bone key", "Ancient Effigy", "Ancient Emblem",
                "Uncut sapphire", "Uncut emerald", "Uncut ruby", "Uncut diamond",
                "Uncut dragonstone", "Black Mask", "Shadow Veil"}:
        return "valuables"

    # Materials
    return "materials"


# ─── Index page generators ──────────────────────────────────────────────

def make_item_card(name, meta):
    """Generate an item card HTML for the index grid."""
    e_name = esc(name)
    s = slug(name)
    stat = item_card_stat(name, meta)
    img_url = meta.get("image", "")
    img_rel = img_relative(img_url)
    if img_rel:
        img_html = f'<div class="npc-card-image"><img src="{esc(img_rel)}" alt="{e_name}"></div>'
    else:
        img_html = NO_IMG_CARD
    return f'''      <a class="npc-card" href="{s}.html">
        {img_html}
        <div class="npc-card-name">{e_name}</div>
        <div class="npc-card-tier">{esc(stat)}</div>
      </a>'''


def make_npc_card(npc):
    """Generate an NPC card HTML for the index grid."""
    name = npc["name"]
    e_name = esc(name)
    s = slug(name)
    tier = npc.get("tier", 1)
    hp = npc.get("hp", 0)
    min_w = npc.get("min_wildy", 1)
    img_url = npc.get("image", "")
    img_rel = img_relative(img_url)
    if img_rel:
        img_html = f'<div class="npc-card-image"><img src="{esc(img_rel)}" alt="{e_name}"></div>'
    else:
        img_html = NO_IMG_CARD
    return f'''      <a class="npc-card" href="{s}.html">
        {img_html}
        <div class="npc-card-name">{e_name}</div>
        <div class="npc-card-tier"><span class="tier tier-{tier}">Tier {tier}</span> &middot; {hp} HP &middot; Lvl {min_w}+</div>
      </a>'''


def generate_npc_index():
    """Generate the NPC index page with NPCs grouped by tier."""
    navbar = NAVBAR.format(home="../", npc_active=' class="active"', item_active="", ge_active="")

    # Group by tier
    tiers = {}
    for npc in NPCS:
        tier = npc.get("tier", 1)
        tiers.setdefault(tier, []).append(npc)

    sections = ""
    for tier_num in sorted(tiers.keys()):
        npcs_in_tier = tiers[tier_num]
        cards = "\n".join(make_npc_card(npc) for npc in npcs_in_tier)
        sections += f'''
    <details class="drop-section" open>
    <summary><h2>Tier {tier_num}</h2></summary>
    <div class="npc-grid">
{cards}
    </div>
    </details>
'''

    page = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>NPCs \u2014 Wilderness Wiki</title>
  <link rel="stylesheet" href="../style.css">
</head>
<body>
{navbar}

  <div class="container">
    <div class="breadcrumb">
      <a href="../index.html">Home</a><span class="sep">/</span>
      NPCs
    </div>

    <h1>NPCs</h1>
    <p>All NPCs in the Wilderness \u2014 from lowly revenants to fearsome bosses.</p>
{sections}
  </div>

  <div class="footer">Wilderness Wiki</div>
  <script src="../search.js"></script>
</body>
</html>
'''
    return page


def generate_items_index():
    """Generate the items index page with items organized by category."""
    navbar = NAVBAR.format(home="../", npc_active="", item_active=' class="active"', ge_active="")

    # Categorize all items
    categories = {
        "melee_weapons": [],
        "range_weapons": [],
        "magic_weapons": [],
        "necro_weapons": [],
        "offhands": [],
        "armour": [],
        "accessories": [],
        "food": [],
        "potions": [],
        "ammo": [],
        "runes": [],
        "materials": [],
        "valuables": [],
        "miscellaneous": [],
        "pets": [],
    }

    for name, meta in ITEMS.items():
        cat = categorize_item(name, meta)
        if cat in categories:
            categories[cat].append((name, meta))

    # Add food from FOOD dict (items not in ITEMS)
    for food_name, food_data in FOOD.items():
        if food_name not in ITEMS:
            categories["food"].append((food_name, {"type": "food", "value": 0, "stackable": False}))

    # Sort weapons by str value (ascending)
    def weapon_sort_key(item_tuple):
        n, m = item_tuple
        for sk in ["str_melee", "str_range", "str_magic", "str_necro"]:
            v = m.get(sk, 0)
            if v: return v
        return 0

    for cat in ["melee_weapons", "range_weapons", "magic_weapons", "necro_weapons"]:
        categories[cat].sort(key=weapon_sort_key)

    # Sort armour by value (ascending)
    categories["armour"].sort(key=lambda x: x[1].get("value", 0))

    # Section definitions
    SECTIONS = [
        ("melee_weapons", "Melee Weapons"),
        ("range_weapons", "Range Weapons"),
        ("magic_weapons", "Magic Weapons"),
        ("necro_weapons", "Necromancy Weapons"),
        ("offhands", "Offhands"),
        ("armour", "Armour"),
        ("accessories", "Accessories"),
        ("food", "Food"),
        ("potions", "Potions"),
        ("ammo", "Ammo"),
        ("runes", "Runes"),
        ("materials", "Materials"),
        ("valuables", "Valuables"),
        ("miscellaneous", "Miscellaneous"),
        ("pets", "Pets"),
    ]

    sections_html = ""
    for cat_key, cat_title in SECTIONS:
        items_in_cat = categories.get(cat_key, [])
        if not items_in_cat:
            continue
        cards = "\n".join(make_item_card(n, m) for n, m in items_in_cat)
        sections_html += f'''
    <details class="drop-section" open>
    <summary><h2>{cat_title}</h2></summary>
    <div class="npc-grid">
{cards}
    </div>
    </details>
'''

    page = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Items \u2014 Wilderness Wiki</title>
  <link rel="stylesheet" href="../style.css">
</head>
<body>
{navbar}

  <div class="container">
    <div class="breadcrumb">
      <a href="../index.html">Home</a><span class="sep">/</span>
      Items
    </div>

    <h1>Items</h1>
    <p>All items in the Wilderness \u2014 weapons, armour, accessories, consumables, materials, and more.</p>
{sections_html}
  </div>

  <div class="footer">Wilderness Wiki</div>
  <script src="../search.js"></script>
</body>
</html>
'''
    return page


# ─── Grand Exchange page generator ─────────────────────────────────────

def _load_ge_offers():
    """Try to load GE offers from the data file. Returns dict {item: {buy, sell}} or {}."""
    ge_path = os.path.join(DOCS, "..", "..", "..", "data", "wilderness", "ge_offers.json")
    ge_path = os.path.normpath(ge_path)
    prices = {}  # item_name -> {"buy": highest_buy, "sell": lowest_sell}
    try:
        with open(ge_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        # raw is {user_id: [offer_dict, ...]}
        for uid, offers in raw.items():
            for o in offers:
                if not o:
                    continue
                item = o.get("item", "")
                side = o.get("side", "")
                price = o.get("price_each", 0)
                filled = o.get("filled", 0)
                qty = o.get("qty", 0)
                if filled >= qty:
                    continue  # fully filled, skip
                if not item or not price:
                    continue
                if item not in prices:
                    prices[item] = {"buy": 0, "sell": 0}
                if side == "buy":
                    if price > prices[item]["buy"]:
                        prices[item]["buy"] = price
                elif side == "sell":
                    if prices[item]["sell"] == 0 or price < prices[item]["sell"]:
                        prices[item]["sell"] = price
    except (FileNotFoundError, json.JSONDecodeError, Exception):
        pass
    return prices


def generate_ge_page():
    """Generate the Grand Exchange price database page."""
    navbar = NAVBAR.format(home="../", npc_active="", item_active="", ge_active=' class="active"')

    ge_prices = _load_ge_offers()

    # Build item data array for JS
    items_js = []
    for name, meta in ITEMS.items():
        if name in UNTRADEABLE:
            continue
        ge_price = meta.get("ge_price", 0) or meta.get("value", 0)
        img_url = meta.get("image", "")
        img_rel = img_relative(img_url)
        cat = categorize_item(name, meta)
        # On the GE page, offhands go into their combat style category
        if cat == "offhands":
            style = str(meta.get("style", "")).lower()
            style_map = {"melee": "melee_weapons", "range": "range_weapons",
                         "magic": "magic_weapons", "necro": "necro_weapons"}
            cat = style_map.get(style, "melee_weapons")
        ge = ge_prices.get(name, {})
        buy_price = ge.get("buy", 0)
        sell_price = ge.get("sell", 0)
        items_js.append({
            "name": name,
            "slug": slug(name),
            "guide": ge_price,
            "buy": buy_price,
            "sell": sell_price,
            "cat": cat,
            "img": img_rel or "",
        })

    # Also add food items not in ITEMS
    for food_name in FOOD:
        if food_name not in ITEMS:
            ge = ge_prices.get(food_name, {})
            items_js.append({
                "name": food_name,
                "slug": slug(food_name),
                "guide": 0,
                "buy": ge.get("buy", 0),
                "sell": ge.get("sell", 0),
                "cat": "food",
                "img": "",
            })

    items_json = json.dumps(items_js, separators=(",", ":"))

    # Category labels for filter buttons
    cat_labels = [
        ("all", "All Items"),
        ("melee_weapons", "Melee"),
        ("range_weapons", "Range"),
        ("magic_weapons", "Magic"),
        ("necro_weapons", "Necro"),
        ("armour", "Armour"),
        ("accessories", "Accessories"),
        ("food", "Food"),
        ("potions", "Potions"),
        ("ammo", "Ammo"),
        ("runes", "Runes"),
        ("materials", "Materials"),
        ("valuables", "Valuables"),
    ]
    filter_btns = '\n        '.join(
        f'<button class="ge-filter-btn{" active" if k == "all" else ""}" data-cat="{k}">{label}</button>'
        for k, label in cat_labels
    )

    page = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Grand Exchange \u2014 Wilderness Wiki</title>
  <link rel="stylesheet" href="../style.css">
</head>
<body>
{navbar}
  <div class="container">
    <div class="breadcrumb"><a href="../index.html">Home</a><span class="sep">/</span>Grand Exchange</div>

    <div class="page-header">
      <h1>Grand Exchange</h1>
      <div class="subtitle">Search item prices, view active buy &amp; sell offers, and find guide prices for all tradeable items.</div>
    </div>

    <div class="ge-search-container">
      <div class="ge-search-wrapper">
        <input type="text" class="ge-search-input" placeholder="Search for an item..." autocomplete="off" id="ge-search">
        <div class="ge-suggestions" id="ge-suggestions"></div>
      </div>
    </div>

    <div class="ge-filters">
      {filter_btns}
    </div>

    <div class="ge-summary" id="ge-summary"></div>

    <table class="ge-table">
      <thead>
        <tr>
          <th class="ge-th-item">Item</th>
          <th class="ge-th-price">Guide Price</th>
          <th class="ge-th-price">Buy Offer</th>
          <th class="ge-th-price">Sell Offer</th>
        </tr>
      </thead>
      <tbody id="ge-tbody"></tbody>
    </table>

    <div class="ge-note">
      <p>Prices are updated each time the wiki is regenerated. Use <code>!w ge</code> in-game for live offers.</p>
    </div>
  </div>
  <div class="footer">Wilderness Wiki</div>
  <script src="../search.js"></script>
  <script>
  (function() {{
    var ITEMS = {items_json};
    var tbody = document.getElementById("ge-tbody");
    var searchInput = document.getElementById("ge-search");
    var suggestions = document.getElementById("ge-suggestions");
    var summaryEl = document.getElementById("ge-summary");
    var activeCat = "all";
    var searchQuery = "";

    function formatCoins(n) {{
      if (!n || n === 0) return "\u2014";
      return n.toLocaleString() + " gp";
    }}

    function renderTable() {{
      var q = searchQuery.toLowerCase().trim();
      var words = q ? q.split(/\\s+/) : [];
      var filtered = [];

      for (var i = 0; i < ITEMS.length; i++) {{
        var item = ITEMS[i];
        if (activeCat !== "all" && item.cat !== activeCat) continue;
        if (words.length > 0) {{
          var name = item.name.toLowerCase();
          var match = true;
          for (var w = 0; w < words.length; w++) {{
            if (name.indexOf(words[w]) < 0) {{ match = false; break; }}
          }}
          if (!match) continue;
        }}
        filtered.push(item);
      }}

      // Sort: items with offers first, then by value descending
      filtered.sort(function(a, b) {{
        var aHas = (a.buy > 0 || a.sell > 0) ? 1 : 0;
        var bHas = (b.buy > 0 || b.sell > 0) ? 1 : 0;
        if (bHas !== aHas) return bHas - aHas;
        return b.guide - a.guide;
      }});

      summaryEl.textContent = filtered.length + " item" + (filtered.length !== 1 ? "s" : "") + " found";

      var html = "";
      for (var j = 0; j < filtered.length; j++) {{
        var it = filtered[j];
        var imgTag = it.img ? '<img src="' + it.img + '" alt="" class="ge-row-img">' : '';
        html += '<tr class="ge-row" onclick="window.location.href=\\'../items/' + it.slug + '.html\\'">' +
          '<td class="ge-cell-item">' + imgTag + '<a href="../items/' + it.slug + '.html">' + it.name + '</a></td>' +
          '<td class="ge-cell-price">' + formatCoins(it.guide) + '</td>' +
          '<td class="ge-cell-price ge-buy">' + formatCoins(it.buy) + '</td>' +
          '<td class="ge-cell-price ge-sell">' + formatCoins(it.sell) + '</td>' +
          '</tr>';
      }}
      tbody.innerHTML = html;
    }}

    // Search input
    searchInput.addEventListener("input", function() {{
      searchQuery = this.value;
      renderSuggestions();
      renderTable();
    }});

    function renderSuggestions() {{
      var q = searchQuery.toLowerCase().trim();
      if (!q) {{ suggestions.style.display = "none"; return; }}
      var words = q.split(/\\s+/);
      var matches = [];
      for (var i = 0; i < ITEMS.length; i++) {{
        var name = ITEMS[i].name.toLowerCase();
        var score = 0;
        if (name === q) score += 100;
        else if (name.indexOf(q) === 0) score += 60;
        else if (name.indexOf(q) >= 0) score += 40;
        for (var w = 0; w < words.length; w++) {{
          if (name.indexOf(words[w]) >= 0) score += 10;
        }}
        if (score > 0) matches.push({{ idx: i, score: score }});
      }}
      matches.sort(function(a, b) {{ return b.score - a.score; }});
      matches = matches.slice(0, 8);

      if (matches.length === 0) {{ suggestions.style.display = "none"; return; }}
      var html = "";
      for (var m = 0; m < matches.length; m++) {{
        var it = ITEMS[matches[m].idx];
        html += '<a class="ge-suggestion" href="../items/' + it.slug + '.html" data-name="' + it.name + '">' + it.name +
          '<span class="ge-suggestion-price">' + formatCoins(it.guide) + '</span></a>';
      }}
      suggestions.innerHTML = html;
      suggestions.style.display = "block";

      // Click suggestion to filter
      var links = suggestions.querySelectorAll(".ge-suggestion");
      for (var l = 0; l < links.length; l++) {{
        links[l].addEventListener("click", function(e) {{
          e.preventDefault();
          searchInput.value = this.getAttribute("data-name");
          searchQuery = searchInput.value;
          suggestions.style.display = "none";
          renderTable();
        }});
      }}
    }}

    searchInput.addEventListener("focus", function() {{
      if (this.value) renderSuggestions();
    }});

    // Close suggestions on outside click
    document.addEventListener("click", function(e) {{
      if (!document.querySelector(".ge-search-wrapper").contains(e.target)) {{
        suggestions.style.display = "none";
      }}
    }});

    // Keyboard nav for suggestions
    searchInput.addEventListener("keydown", function(e) {{
      var items = suggestions.querySelectorAll(".ge-suggestion");
      var active = suggestions.querySelector(".ge-suggestion.active");
      var idx = -1;
      for (var i = 0; i < items.length; i++) {{
        if (items[i] === active) {{ idx = i; break; }}
      }}
      if (e.key === "ArrowDown") {{
        e.preventDefault();
        if (active) active.classList.remove("active");
        idx = (idx + 1) % items.length;
        items[idx].classList.add("active");
      }} else if (e.key === "ArrowUp") {{
        e.preventDefault();
        if (active) active.classList.remove("active");
        idx = idx <= 0 ? items.length - 1 : idx - 1;
        items[idx].classList.add("active");
      }} else if (e.key === "Enter") {{
        if (active) {{
          e.preventDefault();
          searchInput.value = active.getAttribute("data-name");
          searchQuery = searchInput.value;
          suggestions.style.display = "none";
          renderTable();
        }}
      }} else if (e.key === "Escape") {{
        suggestions.style.display = "none";
      }}
    }});

    // Category filter buttons
    var btns = document.querySelectorAll(".ge-filter-btn");
    for (var b = 0; b < btns.length; b++) {{
      btns[b].addEventListener("click", function() {{
        for (var x = 0; x < btns.length; x++) btns[x].classList.remove("active");
        this.classList.add("active");
        activeCat = this.getAttribute("data-cat");
        renderTable();
      }});
    }}

    // Initial render
    renderTable();
  }})();
  </script>
</body>
</html>
'''
    return page


# ─── Main ────────────────────────────────────────────────────────────────

def main():
    os.makedirs(NPC_DIR, exist_ok=True)
    os.makedirs(ITEM_DIR, exist_ok=True)
    os.makedirs(GE_DIR, exist_ok=True)

    npc_count = 0
    item_count = 0

    # ─── Generate ALL NPC pages ───
    print("Generating NPC pages...")
    for npc in NPCS:
        nt = npc.get("npc_type", "")
        drops = NPC_DROPS.get(nt, {})
        html = generate_npc_page(npc, drops)
        fname = slug(npc["name"]) + ".html"
        fpath = os.path.join(NPC_DIR, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(html)
        npc_count += 1
        print(f"  NPC: {fname}")

    # ─── Generate ALL item pages ───
    print("\nGenerating item pages...")
    for item_name, meta in ITEMS.items():
        html = generate_item_page(item_name, meta)
        fname = slug(item_name) + ".html"
        fpath = os.path.join(ITEM_DIR, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(html)
        item_count += 1
        print(f"  Item: {fname}")

    # Generate food pages (from FOOD dict, items not in ITEMS)
    for food_name, food_data in FOOD.items():
        if food_name not in ITEMS:
            meta = {"type": "food", "value": 0, "stackable": False}
            html = generate_item_page(food_name, meta)
            fname = slug(food_name) + ".html"
            fpath = os.path.join(ITEM_DIR, fname)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(html)
            item_count += 1
            print(f"  Item: {fname}")

    # ─── Generate index pages ───
    print("\nGenerating index pages...")

    npc_index = generate_npc_index()
    with open(os.path.join(NPC_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(npc_index)
    print("  NPC index: index.html")

    items_index = generate_items_index()
    with open(os.path.join(ITEM_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(items_index)
    print("  Items index: index.html")

    ge_page = generate_ge_page()
    with open(os.path.join(GE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(ge_page)
    print("  Grand Exchange: grand-exchange/index.html")

    print(f"\nDone! Generated {npc_count} NPC pages and {item_count} item pages + 3 index pages.")


if __name__ == "__main__":
    main()
