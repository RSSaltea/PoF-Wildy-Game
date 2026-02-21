#!/usr/bin/env python3
"""
Wiki Generator — creates HTML pages for all new NPCs and items.
Run from the docs/ directory:  python generate_wiki.py
"""
import os, sys, html as html_mod

# Add parent so we can import game data
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from wildygame.npcs import NPCS, NPC_DROPS
from wildygame.items import ITEMS, ITEM_EFFECTS

DOCS = os.path.dirname(os.path.abspath(__file__))
NPC_DIR = os.path.join(DOCS, "npcs")
ITEM_DIR = os.path.join(DOCS, "items")

# ─── Shared HTML fragments ───

NAVBAR = '''  <div class="navbar">
    <div class="logo"><span>Wilderness</span> Wiki</div>
    <nav>
      <a href="{home}index.html">Home</a>
      <a href="{home}npcs/index.html"{npc_active}>NPCs</a>
      <a href="{home}items/index.html"{item_active}>Items</a>
      <a href="{home}commands/index.html">Commands</a>
    </nav>
    <a href="https://discord.com/invite/paws-of-fury" target="_blank" class="discord-btn"><svg viewBox="0 0 24 24"><path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028c.462-.63.874-1.295 1.226-1.994a.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03z"/></svg>Join Discord</a>
    <div class="search-wrapper">
      <input type="text" class="search-input" placeholder="Search wiki...">
      <div class="search-dropdown"></div>
    </div>
  </div>'''

NO_IMG = '<div class="infobox-image" style="display:flex;align-items:center;justify-content:center;min-height:120px;color:#8b949e;">No image</div>'
NO_IMG_CARD = '<div class="npc-card-image" style="display:flex;align-items:center;justify-content:center;color:#8b949e;font-size:0.85em;">No image</div>'

def esc(s):
    return html_mod.escape(str(s))

def slug(name):
    return name.lower().replace("'", "").replace("'", "").replace(".", "").replace(",", "").replace("(", "").replace(")", "").replace(" ", "-")

STANCE_TO_STYLE = {"stab": "melee", "slash": "melee", "crush": "melee", "magic": "magic", "range": "range", "necro": "necro"}

# ─── NPC descriptions ───

NPC_DESCRIPTIONS = {
    "revenant imp": "The Revenant Imp is a spectral creature that haunts the Wilderness with a bow in hand. Once a mischievous imp in life, it now fires ghostly arrows at any adventurer foolish enough to wander too close.",
    "wandering_warlock": "The Wandering Warlock is a restless mage who roams the Wilderness, hurling arcane blasts at anyone who crosses its path. Though relatively weak, its magical attacks can catch unprepared adventurers off guard.",
    "cursed_spirit": "The Cursed Spirit is a tormented soul bound to the Wilderness by dark necromantic energy. It lashes out with spectral claws, draining the life force of those who dare approach.",
    "feral_scorpion": "The Feral Scorpion is a vicious creature that lurks in the shallow Wilderness. Its powerful pincers deliver crushing blows, making it a dangerous foe for the unarmoured.",
    "revenant pyromancer": "The Revenant Pyromancer is a ghostly mage that wields devastating fire magic. In life it was a powerful sorcerer; in death, its flames burn even hotter.",
    "corrupted_ranger": "The Corrupted Ranger is a fallen archer twisted by dark energy. Its arrows fly true and strike with unnatural precision, making it a formidable ranged threat.",
    "shade": "The Shade is a dark entity that exists between life and death. It attacks with necromantic energy, draining the very essence of its victims.",
    "infernal_imp": "The Infernal Imp is a demonic creature from the depths of the Wilderness. Its crushing blows are powered by hellfire, dealing devastating melee damage.",
    "phantom_archer": "The Phantom Archer is a spectral marksman that haunts the mid-level Wilderness. Its ghostly arrows are nearly impossible to dodge, and it occasionally drops the elusive Flickerwisp pet.",
    "risen_bonecaller": "The Risen Bonecaller is a powerful necromancer that commands the dead. It attacks with bone magic and can summon spectral minions to aid in combat.",
    "windstrider": "The Windstrider is a swift and deadly ranged boss that dashes through the Wilderness with supernatural speed. Its Evasive Dash ability allows it to dodge incoming attacks entirely.",
    "infernal_warlock": "The Infernal Warlock is a powerful magic boss that commands devastating fire spells. Its Infernal Blaze ability supercharges its attacks, dealing bonus fire damage for several hits.",
    "hollow_warden": "The Hollow Warden is a massive stone golem that guards the deep Wilderness. Though it drops no unique items, it yields incredible quantities of resources. Its Stone Shell ability halves incoming damage temporarily.",
    "duskwalker": "The Duskwalker is an elite ranged boss that stalks the deepest parts of the Wilderness. Its Shadow Volley ability allows it to fire two volleys in rapid succession, overwhelming even the most prepared adventurers.",
    "emberlord": "Emberlord Kael is a terrifying magic boss wreathed in eternal flame. Its Flame Burst ability deals unavoidable fire damage, and it drops some of the most powerful magic equipment in the game.",
    "gravekeeper": "Gravekeeper Azriel is the ultimate necromancy boss, commanding armies of the dead from its throne in the deepest Wilderness. Its Soul Siphon ability heals it while weakening its target's defences.",
}

NPC_SPECIALS = {
    "windstrider": "Evasive Dash (10%) — Dodges the player's next attack entirely",
    "infernal_warlock": "Infernal Blaze (8%) — NPC's attacks deal +3 bonus fire damage for 3 hits",
    "hollow_warden": "Stone Shell (10%) — Player's damage is halved for 3 hits",
    "duskwalker": "Shadow Volley (8%) — NPC attacks twice this turn",
    "emberlord": "Flame Burst (10%) — Deals 5 flat unavoidable damage to the player",
    "gravekeeper": "Soul Siphon (12%) — Heals for 100% of damage dealt and reduces player defence by 3 for 4 hits",
}

# ─── NPC page generator ───

def npc_display_name(npc):
    name = npc["name"]
    nt = npc.get("npc_type", "")
    # Some NPCs have display-friendly names already
    return name

def generate_npc_page(npc, drops):
    name = npc["name"]
    e_name = esc(name)
    nt = npc.get("npc_type", "")
    tier = npc.get("tier", 1)
    hp = npc.get("hp", 0)
    min_w = npc.get("min_wildy", 1)
    stance = npc.get("stance", "stab")
    style = STANCE_TO_STYLE.get(stance, "melee")

    # Attack power
    if style == "melee":
        atk = npc.get("str_melee", 0)
    elif style == "range":
        atk = npc.get("str_range", 0)
    elif style == "magic":
        atk = npc.get("str_magic", 0)
    elif style == "necro":
        atk = npc.get("str_necro", 0)
    else:
        atk = 0

    # Sum of positive d_* values for "Defence" display
    d_total = 0
    for k in ["d_stab", "d_slash", "d_crush", "d_magic", "d_range", "d_necro"]:
        v = npc.get(k, 0)
        if v > 0:
            d_total += v
    def_display = d_total // 4  # back to old-scale for display consistency

    slayer_lv = npc.get("slayer_level", 1)
    slayer_xp = npc.get("slayer_xp", 0)
    special = NPC_SPECIALS.get(nt, "None")
    desc = NPC_DESCRIPTIONS.get(nt, f"{e_name} is a creature found in the Wilderness.")

    navbar = NAVBAR.format(home="../", npc_active=' class="active"', item_active="")

    # Drop table
    drop_html = ""
    if drops:
        coins = drops.get("coins")
        loot = drops.get("loot", [])
        unique = drops.get("unique", [])
        pet = drops.get("pet", [])

        drop_html += '\n        <details class="drop-section" open>\n        <summary><h2>Drop Table</h2></summary>\n'

        if coins:
            drop_html += f'\n        <details class="drop-inner" open>\n        <summary><h3>Coins</h3></summary>\n        <p>{coins[0]:,}&ndash;{coins[1]:,} coins</p>\n        </details>\n'

        if loot:
            drop_html += '\n        <details class="drop-inner" open>\n        <summary><h3>Loot</h3></summary>\n        <table>\n          <thead>\n            <tr>\n              <th>Item</th>\n              <th>Quantity</th>\n              <th>Drop Rate</th>\n            </tr>\n          </thead>\n          <tbody>\n'
            for entry in loot:
                item_name = entry.get("item", "")
                mn = entry.get("min", 1)
                mx = entry.get("max", 1)
                chance = entry.get("chance", "?")
                noted = " (noted)" if entry.get("noted") else ""
                qty = f"{mn}" if mn == mx else f"{mn}&ndash;{mx}"
                item_slug = slug(item_name)
                drop_html += f'            <tr>\n              <td><a href="../items/{item_slug}.html">{esc(item_name)}</a>{noted}</td>\n              <td>{qty}</td>\n              <td>{chance}</td>\n            </tr>\n'
            drop_html += '          </tbody>\n        </table>\n        </details>\n'

        if unique:
            drop_html += '\n        <details class="drop-inner" open>\n        <summary><h3>Unique</h3></summary>\n        <table>\n          <thead>\n            <tr>\n              <th>Item</th>\n              <th>Quantity</th>\n              <th>Drop Rate</th>\n            </tr>\n          </thead>\n          <tbody>\n'
            for entry in unique:
                item_name = entry.get("item", "")
                mn = entry.get("min", 1)
                mx = entry.get("max", 1)
                chance = entry.get("chance", "?")
                noted = " (noted)" if entry.get("noted") else ""
                qty = f"{mn}" if mn == mx else f"{mn}&ndash;{mx}"
                item_slug = slug(item_name)
                drop_html += f'            <tr class="drop-unique">\n              <td><a href="../items/{item_slug}.html">{esc(item_name)}</a>{noted}</td>\n              <td>{qty}</td>\n              <td>{chance}</td>\n            </tr>\n'
            drop_html += '          </tbody>\n        </table>\n        </details>\n'

        if pet:
            drop_html += '\n        <details class="drop-inner" open>\n        <summary><h3>Pet</h3></summary>\n        <table>\n          <thead>\n            <tr>\n              <th>Item</th>\n              <th>Quantity</th>\n              <th>Drop Rate</th>\n            </tr>\n          </thead>\n          <tbody>\n'
            for entry in pet:
                item_name = entry.get("item", "")
                chance = entry.get("chance", "?")
                item_slug = slug(item_name)
                drop_html += f'            <tr class="drop-pet">\n              <td><a href="../items/{item_slug}.html">{esc(item_name)}</a></td>\n              <td>1</td>\n              <td>{chance}</td>\n            </tr>\n'
            drop_html += '          </tbody>\n        </table>\n        </details>\n'

        drop_html += '\n        </details>'

    page = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{e_name} — Wilderness Wiki</title>
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
{drop_html}
      </div>
      <div class="infobox">
        {NO_IMG}
        <div class="infobox-name">{e_name}</div>
        <div class="infobox-stats">
          <div class="infobox-row"><span class="infobox-label">Wilderness Level</span><span class="infobox-value">{min_w}+</span></div>
          <div class="infobox-row"><span class="infobox-label">Health</span><span class="infobox-value">{hp}</span></div>
          <div class="infobox-row"><span class="infobox-label">Attack Style</span><span class="infobox-value">{esc(style.capitalize())}</span></div>
          <div class="infobox-row"><span class="infobox-label">Attack</span><span class="infobox-value">{atk}</span></div>
          <div class="infobox-row"><span class="infobox-label">Defence</span><span class="infobox-value">{def_display}</span></div>
          <div class="infobox-row"><span class="infobox-label">Slayer Level</span><span class="infobox-value">{slayer_lv}</span></div>
          <div class="infobox-row"><span class="infobox-label">Slayer XP</span><span class="infobox-value">{slayer_xp}</span></div>
          <div class="infobox-row"><span class="infobox-label">Ability</span><span class="infobox-value">{esc(special)}</span></div>
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

# ─── Item page generator ───

def item_stat_summary(name, meta, effects):
    """Build a short stat string for the index card."""
    # Check if it's a weapon (has str_*)
    parts = []
    for sk in ["str_melee", "str_range", "str_magic", "str_necro"]:
        v = effects.get(sk, 0) if effects else 0
        if v:
            style_label = sk.replace("str_", "").capitalize()
            parts.append(f"+{v} {style_label}")

    # Attack bonuses
    for ak in ["a_stab", "a_slash", "a_crush", "a_magic", "a_range", "a_necro"]:
        v = (effects or {}).get(ak, 0)
        if v:
            parts.append(f"+{v} atk")
            break  # just show one

    # Defence summary
    d_total = 0
    for dk in ["d_stab", "d_slash", "d_crush", "d_magic", "d_range", "d_necro"]:
        v = (effects or {}).get(dk, 0)
        if v > 0:
            d_total += v
    if d_total:
        parts.append(f"+{d_total // 4} def")

    if parts:
        return " / ".join(parts[:2])

    # Type-based fallback
    t = str(meta.get("type", "")).lower()
    if "ammo" in t:
        return "Ammo"
    if "rune" in t:
        return "Rune"
    if "pet" in t:
        return "Pet"
    return meta.get("type", "Item").capitalize() if meta.get("type") else "Item"


def item_slot_display(meta, effects):
    t = str(meta.get("type", "")).lower()
    if "mainhand" in t and "offhand" in t:
        return "Two-handed"
    if "mainhand" in t:
        return "Mainhand"
    if "offhand" in t:
        return "Offhand"
    if "ammo" in t:
        return "Ammo"
    slot_map = {"helm": "Helm", "body": "Body", "legs": "Legs", "boots": "Boots", "gloves": "Gloves",
                "cape": "Cape", "ring": "Ring", "amulet": "Amulet"}
    for s, label in slot_map.items():
        if s in t:
            return label
    return t.capitalize() if t else "—"


def item_style_display(meta, effects):
    style = str(meta.get("style", "")).lower()
    if not style:
        # Infer from effects
        if effects:
            for sk in ["str_melee", "a_stab", "a_slash", "a_crush"]:
                if effects.get(sk, 0):
                    return "Melee"
            for sk in ["str_range", "a_range"]:
                if effects.get(sk, 0):
                    return "Range"
            for sk in ["str_magic", "a_magic"]:
                if effects.get(sk, 0):
                    return "Magic"
            for sk in ["str_necro", "a_necro"]:
                if effects.get(sk, 0):
                    return "Necro"
        return "—"
    return style.capitalize()


def generate_item_page(name, meta, effects):
    e_name = esc(name)
    navbar = NAVBAR.format(home="../", npc_active="", item_active=' class="active"')

    t = str(meta.get("type", "")).lower()
    stackable = "Yes" if meta.get("stackable") else "No"
    equippable = "Yes" if any(s in t for s in ["mainhand", "offhand", "helm", "body", "legs", "boots", "gloves", "cape", "ring", "amulet", "ammo"]) else "No"
    value = meta.get("value", 0)
    value_str = f"{value:,} coins" if value else "—"

    slot = item_slot_display(meta, effects)
    style = item_style_display(meta, effects)
    consumes = meta.get("consumes", "")

    # Build infobox rows
    info_rows = []
    info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Equippable</span><span class="infobox-value">{equippable}</span></div>')
    info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Stackable</span><span class="infobox-value">{stackable}</span></div>')

    if equippable == "Yes":
        info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Slot</span><span class="infobox-value">{esc(slot)}</span></div>')
        if style != "—":
            info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Style</span><span class="infobox-value">{esc(style)}</span></div>')

        # Show attack stats
        if effects:
            for sk, label in [("str_melee", "Melee Str"), ("str_range", "Range Str"), ("str_magic", "Magic Str"), ("str_necro", "Necro Str")]:
                v = effects.get(sk, 0)
                if v:
                    info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">{label}</span><span class="infobox-value">+{v}</span></div>')

            for ak, label in [("a_stab", "Stab Atk"), ("a_slash", "Slash Atk"), ("a_crush", "Crush Atk"), ("a_magic", "Magic Atk"), ("a_range", "Range Atk"), ("a_necro", "Necro Atk")]:
                v = effects.get(ak, 0)
                if v:
                    info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">{label}</span><span class="infobox-value">+{v}</span></div>')

            # Defence stats
            d_parts = []
            for dk, label in [("d_stab", "Stab Def"), ("d_slash", "Slash Def"), ("d_crush", "Crush Def"), ("d_magic", "Magic Def"), ("d_range", "Range Def"), ("d_necro", "Necro Def")]:
                v = effects.get(dk, 0)
                if v != 0:
                    sign = "+" if v > 0 else ""
                    info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">{label}</span><span class="infobox-value">{sign}{v}</span></div>')

        if consumes:
            info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Consumes</span><span class="infobox-value">{esc(consumes)}</span></div>')

    if meta.get("type", "").lower() in ("pet",):
        info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Type</span><span class="infobox-value">Pet</span></div>')
    elif "rune" in t:
        info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Type</span><span class="infobox-value">Rune</span></div>')
    elif "ammo" in t:
        info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Type</span><span class="infobox-value">Ammo</span></div>')

    info_rows.append(f'          <div class="infobox-row"><span class="infobox-label">Value</span><span class="infobox-value">{value_str}</span></div>')

    # Build sources from NPC_DROPS
    source_rows = []
    for nt, drops in NPC_DROPS.items():
        for section in ["loot", "unique", "pet"]:
            for entry in drops.get(section, []):
                if entry.get("item", "").lower() == name.lower():
                    # Find NPC name from npc_type
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
        sources_html = '''
        <details class="drop-section" open>
        <summary><h2>Sources</h2></summary>
        <table>
          <thead>
            <tr>
              <th>Source</th>
              <th>Quantity</th>
              <th>Drop Rate</th>
            </tr>
          </thead>
          <tbody>
''' + "\n".join(source_rows) + '''
          </tbody>
        </table>
        </details>'''

    page = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{e_name} — Wilderness Wiki</title>
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
{sources_html}
      </div>

      <div class="infobox">
        {NO_IMG}
        <div class="infobox-name">{e_name}</div>
        <div class="infobox-stats">
{chr(10).join(info_rows)}
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

# ─── Determine which NPCs/items are NEW (don't have pages yet) ───

# New NPCs by npc_type
NEW_NPC_TYPES = {
    "revenant imp", "wandering_warlock", "cursed_spirit", "feral_scorpion",
    "revenant pyromancer", "corrupted_ranger", "shade", "infernal_imp",
    "phantom_archer", "risen_bonecaller", "windstrider", "infernal_warlock",
    "hollow_warden", "duskwalker", "emberlord", "gravekeeper",
}

# New items to generate pages for
NEW_ITEMS = [
    # Elemental runes
    "Air rune", "Water rune", "Earth rune", "Fire rune",
    # Arrows & bolts
    "Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows",
    "Adamant arrows", "Rune arrows", "Dragon arrows", "Bone bolts",
    # Range weapons
    "Rotwood shortbow", "Whisperwood bow", "Ironwood bow", "Hexwood bow",
    "Bone crossbow", "Nightfall bow",
    # Range offhand
    "Voidfire Quiver",
    # Range armour
    "Scaleweave coif", "Scaleweave body", "Scaleweave chaps", "Scaleweave boots", "Scaleweave vambraces",
    "Drakescale body", "Drakescale chaps",
    "Voidfire coif", "Voidfire body", "Voidfire chaps", "Voidfire boots", "Voidfire vambraces",
    # Magic weapons
    "Galestaff", "Tidestaff", "Stonestaff", "Flamestaff", "Voidtouched wand", "Soulfire staff",
    # Magic offhand
    "Cindertome",
    # Magic armour
    "Thornweave helm", "Thornweave body", "Thornweave legs", "Thornweave boots", "Thornweave gloves",
    "Wraithcaller's robetop", "Wraithcaller's robeskirt",
    "Soulfire hat", "Soulfire robetop", "Soulfire robeskirt", "Soulfire boots", "Soulfire gloves",
    # Necro weapons
    "Spectral scythe", "Deathwarden staff", "Netharis's Grasp",
    # Necro offhand
    "Soulbound Grimoire",
    # Necro armour
    "Ghostweave hood", "Ghostweave robetop", "Ghostweave robeskirt", "Ghostweave boots", "Ghostweave gloves",
    "Deathwarden robetop", "Deathwarden robeskirt",
    "Netharis's hood", "Netharis's robetop", "Netharis's robeskirt", "Netharis's boots", "Netharis's gloves",
    # Pets
    "Flickerwisp", "Tiny Dark Archer", "Soulflame", "Embersprite",
]


def main():
    os.makedirs(NPC_DIR, exist_ok=True)
    os.makedirs(ITEM_DIR, exist_ok=True)

    npc_count = 0
    item_count = 0

    # ─── Generate NPC pages ───
    for npc in NPCS:
        nt = npc.get("npc_type", "")
        if nt not in NEW_NPC_TYPES:
            continue

        drops = NPC_DROPS.get(nt, {})
        html = generate_npc_page(npc, drops)
        fname = slug(npc["name"]) + ".html"
        fpath = os.path.join(NPC_DIR, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(html)
        npc_count += 1
        print(f"  NPC: {fname}")

    # ─── Generate Item pages ───
    for item_name in NEW_ITEMS:
        meta = ITEMS.get(item_name, {})
        effects = ITEM_EFFECTS.get(item_name, {})
        if not meta and not effects:
            print(f"  SKIP (no data): {item_name}")
            continue

        html = generate_item_page(item_name, meta, effects)
        fname = slug(item_name) + ".html"
        fpath = os.path.join(ITEM_DIR, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(html)
        item_count += 1
        print(f"  Item: {fname}")

    print(f"\nDone! Generated {npc_count} NPC pages and {item_count} item pages.")


if __name__ == "__main__":
    main()
