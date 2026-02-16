import discord
from discord.ext import commands
import asyncio
import json
import os
import random
import time
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, Tuple, List
import re

from .items import (
    ITEMS,
    FOOD,
    EQUIP_SLOT_SET,
    STARTER_ITEMS,
    STARTER_SHOP_COOLDOWN_SEC,
    POTIONS,
)
from .npcs import NPCS
from .config_default import DEFAULT_CONFIG
from .trade import TradeManager

DATA_DIR = "data/wilderness"
PLAYERS_FILE = os.path.join(DATA_DIR, "players.json")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")

ALLOWED_CHANNEL_IDS = {1465451116803391529, 1472610522313523323}

AFK_TIMEOUT_SEC = 60 * 60
AFK_SWEEP_INTERVAL_SEC = 5 * 60


def _now() -> int:
    return int(time.time())


def clamp(n: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, n))


def parse_chance(v: Any) -> float:
    """
    Accepts:
    - "1/50" (or "3/100")
    - "0.02" (string) or 0.02 (float/int)
    - "2%" (optional convenience)
    Returns: probability in [0,1]
    """
    if v is None:
        return 0.0
    if isinstance(v, (int, float)):
        return max(0.0, min(1.0, float(v)))
    s = str(v).strip().lower()
    if not s:
        return 0.0
    if s.endswith("%"):
        try:
            pct = float(s[:-1].strip())
            return max(0.0, min(1.0, pct / 100.0))
        except Exception:
            return 0.0
    if "/" in s:
        try:
            a, b = s.split("/", 1)
            num = float(a.strip())
            den = float(b.strip())
            if den <= 0:
                return 0.0
            return max(0.0, min(1.0, num / den))
        except Exception:
            return 0.0
    try:
        return max(0.0, min(1.0, float(s)))
    except Exception:
        return 0.0


@dataclass
class PlayerState:
    user_id: int
    started: bool = False
    coins: int = 0
    bank_coins: int = 0
    inventory: Dict[str, int] = None
    bank: Dict[str, int] = None
    in_wilderness: bool = False
    wildy_level: int = 1
    hp: int = 99
    skulled: bool = False
    risk: Dict[str, int] = None
    equipment: Dict[str, str] = None
    uniques: Dict[str, int] = None
    pets: List[str] = None
    kills: int = 0
    deaths: int = 0
    ventures: int = 0
    escapes: int = 0
    biggest_win: int = 0
    biggest_loss: int = 0
    unique_drops: int = 0
    pet_drops: int = 0
    cd: Dict[str, int] = None
    last_action: int = 0
    active_buffs: Dict[str, Dict[str, int]] = None
    blacklist: List[str] = None
    locked: List[str] = None

    def __post_init__(self):
        if self.inventory is None:
            self.inventory = {}
        if self.bank is None:
            self.bank = {}
        if self.risk is None:
            self.risk = {}
        if self.equipment is None:
            self.equipment = {}
        if self.uniques is None:
            self.uniques = {}
        if self.pets is None:
            self.pets = []
        if self.cd is None:
            self.cd = {}
        if not self.last_action:
            self.last_action = _now()
        if self.active_buffs is None:
            self.active_buffs = {}
        if self.blacklist is None:
            self.blacklist = []
        if self.locked is None:
            self.locked = []

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "PlayerState":
        return PlayerState(**d)


class JsonStore:
    def __init__(self):
        self._lock = asyncio.Lock()
        os.makedirs(DATA_DIR, exist_ok=True)

    async def _read_json(self, path: str, default: Any) -> Any:
        def _read():
            if not os.path.exists(path):
                return default
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)

        return await asyncio.to_thread(_read)

    async def _write_json(self, path: str, data: Any) -> None:
        def _write():
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(tmp, path)

        await asyncio.to_thread(_write)

    async def load_config(self) -> Dict[str, Any]:
        async with self._lock:
            cfg = await self._read_json(CONFIG_FILE, DEFAULT_CONFIG)
            changed = False
            for k, v in DEFAULT_CONFIG.items():
                if k not in cfg:
                    cfg[k] = v
                    changed = True
            if changed:
                await self._write_json(CONFIG_FILE, cfg)
            return cfg

    async def load_players(self) -> Dict[str, Any]:
        async with self._lock:
            return await self._read_json(PLAYERS_FILE, {})

    async def save_players(self, players: Dict[str, Any]) -> None:
        async with self._lock:
            await self._write_json(PLAYERS_FILE, players)


# Turn-based PvP
@dataclass
class DuelState:
    a_id: int
    b_id: int
    channel_id: int
    started_at: int
    turn_id: int
    log: List[str]
    a_acted: bool = False
    b_acted: bool = False


class FightLogView(discord.ui.View):
    def __init__(self, *, author_id: int, pages: List[str], title: str = "Fight Log"):
        super().__init__(timeout=180)
        self.author_id = author_id
        self.pages = pages
        self.title = title
        self.page = 0
        self._sync_buttons()

    def _sync_buttons(self):
        last = max(0, len(self.pages) - 1)
        self.first_btn.disabled = (self.page <= 0)
        self.prev_btn.disabled = (self.page <= 0)
        self.next_btn.disabled = (self.page >= last)
        self.last_btn.disabled = (self.page >= last)

    def _render(self) -> str:
        total = max(1, len(self.pages))
        header = f"📜 **{self.title}** — Page **{self.page + 1}/{total}**\n"
        return header + self.pages[self.page]

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Only the fighter can control these pages.", ephemeral=True)
            return False
        return True

    @discord.ui.button(emoji="⏮️", style=discord.ButtonStyle.secondary)
    async def first_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = 0
        self._sync_buttons()
        await interaction.response.edit_message(content=self._render(), view=self)

    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = max(0, self.page - 1)
        self._sync_buttons()
        await interaction.response.edit_message(content=self._render(), view=self)

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.secondary)
    async def next_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = min(len(self.pages) - 1, self.page + 1)
        self._sync_buttons()
        await interaction.response.edit_message(content=self._render(), view=self)

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary)
    async def last_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = max(0, len(self.pages) - 1)
        self._sync_buttons()
        await interaction.response.edit_message(content=self._render(), view=self)

    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
        return


class DuelView(discord.ui.View):
    def __init__(self, cog: "Wilderness", duel: DuelState):
        super().__init__(timeout=None)
        self.cog = cog
        self.duel = duel

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id not in (self.duel.a_id, self.duel.b_id):
            await interaction.response.send_message("You aren't in this fight.", ephemeral=True)
            return False
        return True

    async def _check_turn(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.duel.turn_id:
            await interaction.response.send_message("It’s not your turn.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.danger)
    async def hit_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check_turn(interaction):
            return
        await self.cog._duel_action(interaction, self.duel, action="hit")

    @discord.ui.button(label="Eat", style=discord.ButtonStyle.success)
    async def eat_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check_turn(interaction):
            return
        await self.cog._duel_action(interaction, self.duel, action="eat")

    @discord.ui.button(label="Teleport", style=discord.ButtonStyle.primary)
    async def tele_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check_turn(interaction):
            return
        await self.cog._duel_action(interaction, self.duel, action="tele")


class NPCInfoSelect(discord.ui.Select):
    def __init__(self, cog: "Wilderness", author_id: int):
        self.cog = cog
        self.author_id = author_id
        options = []
        for (name, base_hp, tier, min_wildy, npc_type, atk_bonus, def_bonus) in NPCS:
            options.append(
                discord.SelectOption(
                    label=name,
                    description=f"Min wildy {min_wildy} • Tier {tier}",
                    value=name,
                )
            )
        super().__init__(
            placeholder="Select an NPC to view details…",
            min_values=1,
            max_values=1,
            options=options[:25],
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Only the command user can use this menu.", ephemeral=True)
            return
        npc_name = self.values[0]
        emb = self.cog._npc_info_embed(npc_name, interaction.guild)
        await interaction.response.edit_message(embed=emb, view=self.view)


class NPCInfoView(discord.ui.View):
    def __init__(self, cog: "Wilderness", author_id: int):
        super().__init__(timeout=180)
        self.add_item(NPCInfoSelect(cog, author_id))

    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, discord.ui.Select):
                child.disabled = True
        return


class Wilderness(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.trade_mgr = TradeManager(self, allowed_channel_ids=ALLOWED_CHANNEL_IDS)
        self.bot = bot
        self.store = JsonStore()
        self.config: Dict[str, Any] = DEFAULT_CONFIG.copy()
        self.players: Dict[int, PlayerState] = {}
        self._ready = False
        self._mem_lock = asyncio.Lock()

        self.duels_by_pair: Dict[frozenset, DuelState] = {}
        self.duels_by_channel: Dict[int, DuelState] = {}

        self._item_alias_map: Dict[str, str] = {}

        self._afk_task: Optional[asyncio.Task] = None

    def _norm(self, s: str) -> str:
        return " ".join(str(s).strip().lower().split())

    def _build_item_alias_map(self):
        m: Dict[str, str] = {}

        def add(alias: str, canonical: str):
            a = self._norm(alias)
            if not a:
                return
            if a not in m:
                m[a] = canonical

        for canonical, meta in ITEMS.items():
            add(canonical, canonical)
            aliases = meta.get("aliases")
            if isinstance(aliases, str):
                for part in aliases.split(","):
                    add(part.strip(), canonical)
            elif isinstance(aliases, (list, tuple)):
                for part in aliases:
                    add(str(part).strip(), canonical)

        # Food aliases
        for food_name in FOOD.keys():
            add(food_name, food_name)

        self._item_alias_map = m

    def _resolve_item(self, query: str) -> Optional[str]:
        """Resolve query -> canonical item name (supports aliases)."""
        return self._item_alias_map.get(self._norm(query))

    def _resolve_from_keys_case_insensitive(self, query: str, keys) -> Optional[str]:
        """Resolve query to an existing key from a dict keys (case-insensitive)."""
        q = self._norm(query)
        for k in keys:
            if self._norm(k) == q:
                return k
        return None

    def _resolve_food(self, query: str) -> Optional[str]:
        q = self._norm(query)
        for k in FOOD.keys():
            if self._norm(k) == q:
                return k
        return None

    def _resolve_npc(self, query: str) -> Optional[Tuple[str, int, int, int, str, int, int]]:
        q = self._norm(query)
        for n in NPCS:
            if self._norm(n[0]) == q:
                return n
        return None

    def _hp_line_pvm(self, your_hp: int, npc_name: str, npc_hp: int, npc_max: int) -> str:
        return f"❤️ You: **{your_hp}/{self.config['max_hp']}** | {npc_name}: **{max(0, npc_hp)}/{npc_max}**"

    def _hp_line_pvp(self, a_name: str, a_hp: int, b_name: str, b_hp: int) -> str:
        return f"❤️ {a_name}: **{a_hp}/{self.config['max_hp']}** | {b_name}: **{b_hp}/{self.config['max_hp']}**"

    async def cog_load(self):
        self.config = await self.store.load_config()
        raw_players = await self.store.load_players()
        self.players = {}
        for user_id_str, pdata in raw_players.items():
            try:
                self.players[int(user_id_str)] = PlayerState.from_dict(pdata)
            except Exception:
                continue
        self._build_item_alias_map()
        self._ready = True
        if self._afk_task is None or self._afk_task.done():
            self._afk_task = asyncio.create_task(self._afk_sweeper())

    async def cog_unload(self):
        if self._afk_task and not self._afk_task.done():
            self._afk_task.cancel()

    async def _ensure_ready(self, ctx: commands.Context) -> bool:
        ch = getattr(ctx, "channel", None)
        if ch is None or getattr(ch, "id", None) not in ALLOWED_CHANNEL_IDS:
            return False
        if not self._ready:
            await ctx.reply("Wilderness is still loading. Try again in a moment.")
            return False
        return True

    async def _persist(self):
        raw = {str(uid): p.to_dict() for uid, p in self.players.items()}
        await self.store.save_players(raw)

    def _get_player(self, user: discord.abc.User) -> PlayerState:
        p = self.players.get(user.id)
        if p is None:
            p = PlayerState(user_id=user.id)
            self.players[user.id] = p

        p.inventory = p.inventory or {}
        p.active_buffs = p.active_buffs or {}
        p.bank = p.bank or {}
        p.risk = p.risk or {}
        p.equipment = p.equipment or {}
        p.uniques = p.uniques or {}
        p.pets = p.pets or []
        p.cd = p.cd or {}
        p.locked = getattr(p, "locked", None) or []
        p.blacklist = getattr(p, "blacklist", None) or []
        if getattr(p, "started", None) is None:
            p.started = False
        if not getattr(p, "last_action", 0):
            p.last_action = _now()
        p.hp = clamp(int(p.hp), 0, int(self.config["max_hp"]))
        return p

    def _touch(self, p: PlayerState):
        p.last_action = _now()

    def _cd_ready(self, p: PlayerState, key: str, seconds: int) -> Tuple[bool, int]:
        last = int(p.cd.get(key, 0))
        now = _now()
        if now - last >= seconds:
            return True, 0
        return False, seconds - (now - last)

    def _set_cd(self, p: PlayerState, key: str):
        p.cd[key] = _now()

    # Inventory slot math (stackables)
    def _is_stackable(self, item_name: str) -> bool:
        meta = ITEMS.get(item_name)
        if meta is None:
            return False
        return bool(meta.get("stackable", False))

    def _inv_slots_used(self, bag: Dict[str, int]) -> int:
        used = 0
        for name, qty in bag.items():
            if qty <= 0:
                continue
            # food is non-stackable by design
            if name in FOOD:
                used += qty
                continue
            # items
            if self._is_stackable(name):
                used += 1
            else:
                used += qty
        return used

    def _inv_free_slots(self, bag: Dict[str, int]) -> int:
        max_inv = int(self.config["max_inventory_items"])
        return max(0, max_inv - self._inv_slots_used(bag))

    def _slots_needed_to_add(self, bag: Dict[str, int], item: str, qty: int) -> int:
        if qty <= 0:
            return 0
        if item in FOOD:
            return qty
        if self._is_stackable(item):
            return 0 if bag.get(item, 0) > 0 else 1
        return qty

    def _add_item(self, bag: Dict[str, int], item: str, qty: int):
        if qty <= 0:
            return
        bag[item] = bag.get(item, 0) + qty
        if bag[item] <= 0:
            bag.pop(item, None)

    def _remove_item(self, bag: Dict[str, int], item: str, qty: int) -> bool:
        if qty <= 0:
            return False
        have = bag.get(item, 0)
        if have < qty:
            return False
        left = have - qty
        if left <= 0:
            bag.pop(item, None)
        else:
            bag[item] = left
        return True

    def _total_coins(self, p: PlayerState) -> int:
        return int(p.coins) + int(p.bank_coins)

    def _spend_coins(self, p: PlayerState, amount: int) -> bool:
        """
        Spend coins from inventory first, then bank.
        Returns True if payment successful.
        """
        amount = int(amount)
        if amount <= 0:
            return True

        total = self._total_coins(p)
        if total < amount:
            return False

        # Spend inventory coins first
        take_inv = min(int(p.coins), amount)
        p.coins -= take_inv
        amount -= take_inv

        # Then bank coins
        if amount > 0:
            p.bank_coins -= amount

        return True

    def _item_slot(self, item_name: str) -> Optional[str]:
        meta = ITEMS.get(item_name)
        if not meta:
            return None
        slot = str(meta.get("type", "")).strip().lower()
        if slot in EQUIP_SLOT_SET:
            return slot
        return None

    # NOTE:
    # - PvP should NOT consume ether (so we never charge ether in _duel_action).
    # - PvM SHOULD consume 3 ether per hit IF available.
    # - If you don't have 3 ether, you still get normal atk (e.g. 4), but NOT atk_vs_npc (e.g. 20).
    #
    # This function supports an override for "charged this hit" so that:
    # - we can check ether first (>=3), consume it, and STILL apply atk_vs_npc for that hit
    #   even if consuming drops you below 3 afterward.
    def _equipped_bonus(
        self,
        p: PlayerState,
        *,
        vs_npc: bool,
        chainmace_charged: Optional[bool] = None,
    ) -> Tuple[int, int]:
        atk = 0
        deff = 0

        # Gear bonuses
        for item in p.equipment.values():
            meta = ITEMS.get(item, {})
            atk += int(meta.get("atk", 0))
            deff += int(meta.get("def", 0))

            if vs_npc:
                if item == "Viggora's Chainmace":
                    charged = chainmace_charged
                    if charged is None:
                        charged = (p.inventory.get("Revenant ether", 0) >= 3)
                    if not charged:
                        continue  # no atk_vs_npc when not charged
                atk += int(meta.get("atk_vs_npc", 0))

        # Potion / temporary buff bonuses
        buffs = getattr(p, "active_buffs", None) or {}
        for buff in buffs.values():
            atk += int(buff.get("atk", 0))
            deff += int(buff.get("def", 0))

        return atk, deff

    def _consume_buffs_on_hit(self, p: PlayerState) -> List[str]:
        """Consumes 1 hit from each active buff. Returns lines to log when buffs expire."""
        expired_msgs: List[str] = []
        buffs = getattr(p, "active_buffs", None) or {}
        to_remove = []
        for name, buff in buffs.items():
            buff["remaining_hits"] = int(buff.get("remaining_hits", 0)) - 1
            if buff["remaining_hits"] <= 0:
                to_remove.append(name)
        for name in to_remove:
            buffs.pop(name, None)
            expired_msgs.append(f"🧪 **{name}** has worn off.")
        p.active_buffs = buffs
        return expired_msgs

    def _apply_seeping_heal(self, p: PlayerState, damage_dealt: int) -> int:
        """
        Amulet of Seeping:
        Costs 5 Blood runes per successful (non-zero) hit.
        Heals 1 + 2% of damage dealt (only if damage > 0 and you can pay).
        Returns the amount actually healed.
        """
        if damage_dealt <= 0:
            return 0

        if p.equipment.get("amulet") != "Amulet of Seeping":
            return 0

        RUNE_NAME = "Blood rune"
        RUNE_COST = 5

        # Must have enough runes in INVENTORY to heal
        if int(p.inventory.get(RUNE_NAME, 0)) < RUNE_COST:
            return 0

        # Spend runes, then heal
        if not self._remove_item(p.inventory, RUNE_NAME, RUNE_COST):
            return 0  # safety fallback

        max_hp = int(self.config["max_hp"])
        before = int(p.hp)

        heal_amt = 1 + int(damage_dealt * 0.02)
        p.hp = clamp(before + heal_amt, 0, max_hp)

        return int(p.hp) - before

    def _best_food_in_inventory(self, p: PlayerState) -> Optional[str]:
        best = None
        best_heal = -1
        for name, meta in FOOD.items():
            heal = int(meta.get("heal", 0))
            if heal <= 0:
                continue
            if p.inventory.get(name, 0) > 0 and heal > best_heal:
                best = name
                best_heal = heal
        return best

    def _band(self, wildy_level: int) -> str:
        if wildy_level <= 15:
            return "shallow"
        if wildy_level <= 30:
            return "mid"
        return "deep"

    def _roll_pick_one(self, entries: List[Dict[str, Any]]) -> Optional[Tuple[str, int]]:
        """
        Rolls every entry individually.
        If multiple entries succeed, pick the RAREST successful one (lowest chance).
        If tied, pick randomly among the tied rarest.
        """
        successes: List[Tuple[float, str, int]] = []  # (chance, item, qty)
        for e in entries or []:
            try:
                item = str(e.get("item", "")).strip()
                if not item:
                    continue
                ch = parse_chance(e.get("chance", 0))
                if ch <= 0:
                    continue
                if random.random() <= ch:
                    lo = int(e.get("min", 1))
                    hi = int(e.get("max", lo))
                    if hi < lo:
                        hi = lo
                    qty = random.randint(lo, hi)
                    if qty > 0:
                        successes.append((ch, item, qty))
            except Exception:
                continue
        if not successes:
            return None
        min_ch = min(s[0] for s in successes)
        rarest = [s for s in successes if s[0] == min_ch]
        _, item, qty = random.choice(rarest)
        return item, qty

    def _loot_for_level(self, wildy_level: int) -> Optional[Tuple[str, int]]:
        band = self._band(wildy_level)
        table = self.config.get("loot_tables", {}).get(band, [])
        return self._roll_pick_one(table)

    def _npc_roll_table(self, npc_type: str, key: str) -> Optional[Tuple[str, int]]:
        npc_drop = self.config.get("npc_drops", {}).get(npc_type, {})
        entries = npc_drop.get(key, [])
        return self._roll_pick_one(entries)

    def _npc_roll_pet(self, npc_type: str) -> Optional[str]:
        npc_drop = self.config.get("npc_drops", {}).get(npc_type, {})
        entries = npc_drop.get("pet", []) or []
        for e in entries:
            try:
                item = str(e.get("item", "")).strip()
                if not item:
                    continue
                ch = parse_chance(e.get("chance", 0))
                if ch > 0 and random.random() <= ch:
                    return item
            except Exception:
                continue
        return None

    def _npc_coin_roll(self, npc_type: str) -> int:
        npc_drop = self.config.get("npc_drops", {}).get(npc_type, {})
        lo, hi = npc_drop.get("coins_range", [0, 0])
        try:
            lo = int(lo)
            hi = int(hi)
        except Exception:
            lo, hi = 0, 0
        if hi < lo:
            hi = lo
        return random.randint(lo, hi) if hi > 0 else 0

    def _full_heal(self, p: PlayerState):
        p.hp = int(self.config["max_hp"])

    def _is_locked(self, p: PlayerState, item_name: str) -> bool:
        """True if item_name matches any entry in p.locked (case/space insensitive)."""
        if not item_name:
            return False
        locked = getattr(p, "locked", None) or []
        target = self._norm(item_name)
        return any(self._norm(x) == target for x in locked)

    def _locked_pretty(self, p: PlayerState) -> str:
        locked = getattr(p, "locked", None) or []
        if not locked:
            return "(none)"
        return "\n".join(f"- {x}" for x in sorted(locked, key=lambda s: s.lower()))

    def _is_blacklisted(self, p: PlayerState, item_name: str) -> bool:
        """True if item_name matches any entry in p.blacklist (case/space insensitive)."""
        if not item_name:
            return False
        bl = getattr(p, "blacklist", None) or []
        target = self._norm(item_name)
        return any(self._norm(x) == target for x in bl)

    def _record_autodrop(self, auto_drops: Dict[str, int], item: str, qty: int):
        if qty > 0:
            auto_drops[item] = auto_drops.get(item, 0) + qty

    def _try_put_item_with_blacklist(
        self,
        p: PlayerState,
        item: str,
        qty: int,
        auto_drops: Dict[str, int],
    ) -> str:
        """
        If blacklisted: do NOT add to inventory; record in auto_drops; return log suffix.
        Else: normal _try_put_item.
        """
        if qty <= 0:
            return "(none)"

        if self._is_blacklisted(p, item):
            self._record_autodrop(auto_drops, item, qty)
            return "(blacklisted - dropped)"

        return self._try_put_item(p, item, qty)

    def _try_put_item(self, p: PlayerState, item: str, qty: int) -> str:
        """
        ✅ Inventory ONLY.
        Attempts to add to inventory with slot limit (stackables use 1 slot total).
        If inventory is full, overflow is LOST (NOT banked).
        Returns a short destination string for logging.
        """
        if qty <= 0:
            return "(none)"

        max_inv = int(self.config["max_inventory_items"])

        slots_needed = self._slots_needed_to_add(p.inventory, item, qty)

        if slots_needed == 0:
            self._add_item(p.inventory, item, qty)
            return ""

        used = self._inv_slots_used(p.inventory)
        space = max_inv - used
        if space <= 0:
            return "(inventory full - lost)"

        # Stackable but not already in bag: needs 1 free slot
        if self._is_stackable(item) and item not in FOOD:
            if space >= 1:
                self._add_item(p.inventory, item, qty)
                return ""
            return "(inventory full - lost)"

        # Non-stackable (or food): fill what we can
        take = min(space, qty)
        if take > 0:
            self._add_item(p.inventory, item, take)
        rem = qty - take
        if rem > 0:
            return f"(x{take} inv, x{rem} lost)"
        return ""


    def _maybe_auto_eat_after_hit(self, p: PlayerState, your_hp: int) -> Tuple[int, Optional[str], int, int]:
        """
        Auto-eat when HP is <= (heal + random(1..10)) for the best food in inventory.
        Returns: (new_hp, food_name_or_None, threshold_roll, healed_amount)
        """
        food = self._best_food_in_inventory(p)
        if not food:
            return your_hp, None, 0, 0

        heal = int(FOOD.get(food, {}).get("heal", 0))
        if heal <= 0:
            return your_hp, None, 0, 0

        r_lo, r_hi = self.config.get("auto_eat_extra_range", [1, 10])
        try:
            r_lo = int(r_lo)
            r_hi = int(r_hi)
        except Exception:
            r_lo, r_hi = 1, 10
        if r_hi < r_lo:
            r_hi = r_lo

        extra = random.randint(r_lo, r_hi)
        threshold = heal + extra

        if your_hp > 0 and your_hp <= threshold and p.inventory.get(food, 0) > 0:
            if self._remove_item(p.inventory, food, 1):
                before = your_hp
                your_hp = clamp(your_hp + heal, 0, int(self.config["max_hp"]))
                return your_hp, food, threshold, (your_hp - before)

        return your_hp, None, threshold, 0

    def _pair_key(self, a: int, b: int) -> frozenset:
        return frozenset({a, b})

    def _duel_active_for_user(self, uid: int) -> Optional[DuelState]:
        for k, d in self.duels_by_pair.items():
            if uid in k:
                return d
        return None

    def _duel_render(self, duel: DuelState, a: discord.Member, b: discord.Member, pa: PlayerState, pb: PlayerState, ended: bool) -> str:
        lines: List[str] = []
        if not ended:
            turn_name = a.display_name if duel.turn_id == duel.a_id else b.display_name
            lines.append(f"⚔️ **Fight**: {a.display_name} attacked {b.display_name} — turn: **{turn_name}**")
            lines.append("🌀 Teleport chance: **50%** if it’s your first action, otherwise **20%**.")
        else:
            lines.append(f"⚔️ **Fight ended**: {a.display_name} vs {b.display_name}")
        tail = duel.log[-14:]
        lines.extend(tail if tail else ["(no actions yet)"])
        return "\n".join(lines)

    def _pvp_transfer_all_items(self, winner: PlayerState, loser: PlayerState) -> List[str]:
        """Winner receives ALL loser equipped + inventory items. Coins are NOT transferred."""
        lines: List[str] = []
        for item, qty in list(loser.inventory.items()):
            if qty <= 0:
                continue
            dest = self._try_put_item(winner, item, qty)
            lines.append(f"📦 Looted {item} x{qty} {dest}".rstrip())
        loser.inventory.clear()

        for slot, item in list(loser.equipment.items()):
            dest = self._try_put_item(winner, item, 1)
            lines.append(f"🛡️ Looted equipped ({slot}) {item} x1 {dest}".rstrip())
        loser.equipment.clear()
        return lines

    def _format_items_short(self, items: Dict[str, int], max_lines: int = 12) -> str:
        if not items:
            return "(none)"
        pairs = [(k, int(v)) for k, v in items.items() if int(v) > 0]
        pairs.sort(key=lambda x: (x[0].lower(), x[0]))
        lines = [f"- {k} x{v}" for k, v in pairs]
        if len(lines) > max_lines:
            rest = len(lines) - max_lines
            lines = lines[:max_lines] + [f"... (+{rest} more)"]
        return "\n".join(lines) if lines else "(none)"

    def _fmt_entry(self, e: Dict[str, Any]) -> str:
        item = str(e.get("item", "")).strip()
        lo = int(e.get("min", 1))
        hi = int(e.get("max", lo))
        ch_raw = e.get("chance", "")
        ch = parse_chance(ch_raw)
        if hi < lo:
            hi = lo
        qty = f"{lo}" if lo == hi else f"{lo}-{hi}"
        if not item:
            return ""
        if isinstance(ch_raw, str) and ch_raw.strip():
            chance_str = ch_raw.strip()
        else:
            chance_str = f"{int(ch*100)}%" if ch > 0 else "0%"
        return f"- {item} x{qty} • {chance_str}"

    def _npc_info_embed(self, npc_name: str, guild: Optional[discord.Guild]) -> discord.Embed:
        npc = self._resolve_npc(npc_name) or NPCS[0]
        name, base_hp, tier, min_wildy, npc_type, atk_bonus, def_bonus = npc

        drops = (self.config.get("npc_drops", {}) or {}).get(npc_type, {}) or {}
        coins_range = drops.get("coins_range", [0, 0])
        try:
            c_lo, c_hi = int(coins_range[0]), int(coins_range[1])
        except Exception:
            c_lo, c_hi = 0, 0

        def section_lines(key: str) -> str:
            arr = drops.get(key, []) or []
            lines = []
            for e in arr:
                try:
                    s = self._fmt_entry(e)
                    if s:
                        lines.append(s)
                except Exception:
                    continue
            return "\n".join(lines) if lines else "(none)"

        emb = discord.Embed(
            title=f"👹 NPC: {name}",
            description=f"Min Wilderness level: **{min_wildy}**\nType: **{npc_type}**\nTier: **{tier}**",
        )
        emb.add_field(
            name="Base Stats",
            value=f"Base HP: **{base_hp}**\nAtk bonus: **{atk_bonus}**\nDef bonus: **{def_bonus}**",
            inline=True,
        )
        emb.add_field(name="Scaling", value="In fights, HP/Atk/Def scale with your Wilderness level.", inline=True)

        emb.add_field(name="Coins", value=f"Range: **{c_lo:,}–{c_hi:,}**", inline=False)
        emb.add_field(name="Loot", value=section_lines("loot"), inline=False)
        emb.add_field(name="Uniques", value=section_lines("unique"), inline=False)

        if drops.get("special"):
            emb.add_field(name="Special", value=section_lines("special"), inline=False)

        emb.add_field(name="Pet", value=section_lines("pet"), inline=False)

        if guild and guild.icon:
            emb.set_thumbnail(url=guild.icon.url)

        return emb

    async def _afk_sweeper(self):
        try:
            while True:
                await asyncio.sleep(AFK_SWEEP_INTERVAL_SEC)
                if not self._ready:
                    continue
                now = _now()
                to_tele: List[int] = []
                async with self._mem_lock:
                    for uid, p in self.players.items():
                        try:
                            if not p.in_wilderness:
                                continue
                            last = int(getattr(p, "last_action", 0) or 0)
                            if last and (now - last) >= AFK_TIMEOUT_SEC:
                                to_tele.append(uid)
                        except Exception:
                            continue

                if not to_tele:
                    continue

                for uid in to_tele:
                    p = self.players.get(uid)
                    if not p:
                        continue

                    duel = self._duel_active_for_user(uid)
                    if duel:
                        key = self._pair_key(duel.a_id, duel.b_id)
                        self.duels_by_pair.pop(key, None)
                        if duel.channel_id:
                            self.duels_by_channel.pop(duel.channel_id, None)

                        ch = self.bot.get_channel(duel.channel_id) if duel.channel_id else None
                        if isinstance(ch, discord.abc.Messageable):
                            try:
                                a_m = None
                                b_m = None
                                if hasattr(ch, "guild") and ch.guild:
                                    a_m = ch.guild.get_member(duel.a_id)
                                    b_m = ch.guild.get_member(duel.b_id)
                                a_name = a_m.display_name if a_m else str(duel.a_id)
                                b_name = b_m.display_name if b_m else str(duel.b_id)
                                await ch.send(
                                    f"⏳ AFK: **{a_name if uid == duel.a_id else b_name}** was inactive for 60 minutes and was auto-teleported out. Fight ended."
                                )
                            except Exception:
                                pass

                    p.in_wilderness = False
                    p.skulled = False
                    p.wildy_level = 1
                    self._full_heal(p)

                await self._persist()

        except asyncio.CancelledError:
            return

    # Fight
    async def _duel_action(self, interaction: discord.Interaction, duel: DuelState, action: str):
        ch = interaction.channel
        if ch is None or ch.id not in ALLOWED_CHANNEL_IDS:
            return

        async with self._mem_lock:
            key = self._pair_key(duel.a_id, duel.b_id)
            if self.duels_by_pair.get(key) is None:
                await interaction.response.send_message("This fight is no longer active.", ephemeral=True)
                return

            guild = interaction.guild
            if guild is None:
                await interaction.response.send_message("Fights only work in servers.", ephemeral=True)
                return

            a_member = guild.get_member(duel.a_id)
            b_member = guild.get_member(duel.b_id)
            if a_member is None or b_member is None:
                self.duels_by_pair.pop(key, None)
                self.duels_by_channel.pop(duel.channel_id, None)
                await interaction.response.send_message("A fighter is missing.", ephemeral=True)
                return

            pa = self._get_player(a_member)
            pb = self._get_player(b_member)

            self._touch(pa)
            self._touch(pb)

            if _now() - duel.started_at > int(self.config["pvp_total_timeout_sec"]):
                self.duels_by_pair.pop(key, None)
                self.duels_by_channel.pop(duel.channel_id, None)
                await interaction.response.send_message("⏱️ Fight timed out.", ephemeral=False)
                return

            if interaction.user.id != duel.turn_id:
                await interaction.response.send_message("It’s not your turn.", ephemeral=True)
                return

            attacker_id = duel.turn_id
            defender_id = duel.b_id if attacker_id == duel.a_id else duel.a_id

            attacker_member = a_member if attacker_id == duel.a_id else b_member
            defender_member = b_member if defender_id == duel.b_id else a_member

            attacker = pa if attacker_id == duel.a_id else pb
            defender = pb if defender_id == duel.b_id else pa

            def mark_acted(uid: int):
                if uid == duel.a_id:
                    duel.a_acted = True
                elif uid == duel.b_id:
                    duel.b_acted = True

            def has_acted(uid: int) -> bool:
                if uid == duel.a_id:
                    return bool(duel.a_acted)
                if uid == duel.b_id:
                    return bool(duel.b_acted)
                return True

            if action == "tele":
                chance = 0.50 if not has_acted(attacker_id) else 0.20
                mark_acted(attacker_id)

                duel.log.append(
                    self._hp_line_pvp(a_member.display_name, pa.hp, b_member.display_name, pb.hp)
                )

                if random.random() <= chance:
                    duel.log.append(f"✨ {attacker_member.display_name} teleports out! (**{int(chance*100)}%** roll)")
                    attacker.in_wilderness = False
                    attacker.skulled = False
                    attacker.wildy_level = 1
                    self._full_heal(attacker)

                    await self._persist()
                    self.duels_by_pair.pop(key, None)
                    self.duels_by_channel.pop(duel.channel_id, None)
                    await interaction.response.edit_message(
                        content=self._duel_render(duel, a_member, b_member, pa, pb, ended=True),
                        view=None
                    )
                    return
                else:
                    duel.log.append(f"🧊 Teleblock! {attacker_member.display_name} failed to teleport. (**{int(chance*100)}%** roll)")
                    duel.turn_id = defender_id
                    await self._persist()
                    await interaction.response.edit_message(
                        content=self._duel_render(duel, a_member, b_member, pa, pb, ended=False),
                        view=DuelView(self, duel)
                    )
                    return

            if action == "eat":
                food = self._best_food_in_inventory(attacker)
                if not food:
                    await interaction.response.send_message("You have no food in your inventory.", ephemeral=True)
                    return
                heal = int(FOOD.get(food, {}).get("heal", 0))
                if heal <= 0:
                    await interaction.response.send_message("That food has no heal value.", ephemeral=True)
                    return
                if not self._remove_item(attacker.inventory, food, 1):
                    await interaction.response.send_message("You have no food in your inventory.", ephemeral=True)
                    return
                before = attacker.hp
                attacker.hp = clamp(attacker.hp + heal, 0, int(self.config["max_hp"]))
                mark_acted(attacker_id)
                duel.log.append(
                    self._hp_line_pvp(a_member.display_name, pa.hp, b_member.display_name, pb.hp)
                )
                duel.log.append(f"🍖 {attacker_member.display_name} eats and heals **{attacker.hp - before}**.")
                duel.turn_id = defender_id
                await self._persist()
                await interaction.response.edit_message(
                    content=self._duel_render(duel, a_member, b_member, pa, pb, ended=False),
                    view=DuelView(self, duel)
                )
                return

            if action == "hit":
                # PvP SHOULD NOT consume ether. We just use normal bonuses.
                atk_bonus, _ = self._equipped_bonus(attacker, vs_npc=False)
                _, def_bonus = self._equipped_bonus(defender, vs_npc=False)
                atk_stat = 6 + atk_bonus + int(attacker.wildy_level / 12)
                def_stat = 5 + def_bonus + int(defender.wildy_level / 12)
                roll_a = random.randint(0, atk_stat)
                roll_d = random.randint(0, def_stat)
                hit = max(0, roll_a - roll_d)
                defender.hp = clamp(defender.hp - hit, 0, int(self.config["max_hp"]))

                # 🩸 Amulet of Seeping lifesteal (PvP)
                healed = self._apply_seeping_heal(attacker, hit)
                if healed > 0:
                    duel.log.append(f"🩸 Amulet of Seeping heals **{healed}**.")

                mark_acted(attacker_id)

                duel.log.append(
                    self._hp_line_pvp(a_member.display_name, pa.hp, b_member.display_name, pb.hp)
                )
                duel.log.append(f"🗡️ {attacker_member.display_name} attacks and deals **{hit}**.")
                duel.log.extend(self._consume_buffs_on_hit(attacker))

                if defender.hp <= 0:
                    lost_inv_snapshot = dict(defender.inventory)
                    lost_equip_snapshot = dict(defender.equipment)

                    duel.log.append(
                        self._hp_line_pvp(a_member.display_name, pa.hp, b_member.display_name, pb.hp)
                    )
                    duel.log.append(f"☠️ {defender_member.display_name} has been defeated!")

                    attacker.kills += 1
                    defender.deaths += 1

                    loot_lines = self._pvp_transfer_all_items(attacker, defender)
                    duel.log.extend(loot_lines[:6])

                    if lost_inv_snapshot or lost_equip_snapshot:
                        duel.log.append(f"📉 {defender_member.display_name} lost:")
                        if lost_inv_snapshot:
                            duel.log.append("• Inventory:")
                            for line in self._format_items_short(lost_inv_snapshot, max_lines=8).splitlines():
                                duel.log.append(f"  {line}")
                        else:
                            duel.log.append("• Inventory: (none)")
                        if lost_equip_snapshot:
                            duel.log.append("• Equipped:")
                            eq_lines = [f"- {slot}: {item}" for slot, item in sorted(lost_equip_snapshot.items())]
                            if len(eq_lines) > 8:
                                eq_lines = eq_lines[:8] + [f"... (+{len(lost_equip_snapshot)-8} more)"]
                            for l in eq_lines:
                                duel.log.append(f"  {l}")
                        else:
                            duel.log.append("• Equipped: (none)")

                    defender.hp = int(self.config["starting_hp"])
                    defender.in_wilderness = False
                    defender.wildy_level = 1
                    defender.skulled = False
                    self._full_heal(defender)

                    await self._persist()
                    self.duels_by_pair.pop(key, None)
                    self.duels_by_channel.pop(duel.channel_id, None)
                    await interaction.response.edit_message(
                        content=self._duel_render(duel, a_member, b_member, pa, pb, ended=True),
                        view=None
                    )
                    return

                duel.turn_id = defender_id
                await self._persist()
                await interaction.response.edit_message(
                    content=self._duel_render(duel, a_member, b_member, pa, pb, ended=False),
                    view=DuelView(self, duel)
                )
                return

    def _build_pages(self, lines: List[str], per_page: int = 10) -> List[str]:
        pages: List[str] = []
        for i in range(0, len(lines), per_page):
            pages.append("\n".join(lines[i:i + per_page]))
        return pages or ["(no log)"]
    
    def _simulate_pvm_fight_and_loot(
        self,
        p: PlayerState,
        chosen_npc: Tuple[str, int, int, int, str, int, int],
        *,
        header_lines: Optional[List[str]] = None,
    ) -> Tuple[bool, str, List[str], Dict[str, int], int, List[str]]:
        """
        Returns:
        (won, npc_name, events, lost_items_on_death, bank_loss_on_death, loot_lines_on_win)
        """

        npc_name, npc_hp, npc_tier, _, npc_type, npc_atk_bonus, npc_def_bonus = chosen_npc

        if npc_type == "overlord" and p.equipment.get("gloves") == "Wristwraps of the Damned":
            npc_hp = int(npc_hp * 0.70)

        npc_hp += int(p.wildy_level / 8)
        npc_max = npc_hp

        npc_atk = 1 + npc_tier + npc_atk_bonus + int(p.wildy_level / 12)
        npc_def_stat = npc_tier + npc_def_bonus + int(p.wildy_level / 20)

        your_hp = p.hp
        start_hp = p.hp

        events: List[str] = []
        if header_lines:
            events.extend(header_lines)

        events.append(f"👹 **{npc_name}** (HP **{npc_max}**) — You start **{start_hp}/{self.config['max_hp']}**")

        force_zero_next_hit = False

        while npc_hp > 0 and your_hp > 0:
            charged = False
            if p.equipment.get("mainhand") == "Viggora's Chainmace":
                if p.inventory.get("Revenant ether", 0) >= 3:
                    charged = True
                    self._remove_item(p.inventory, "Revenant ether", 3)

            atk_bonus, def_bonus = self._equipped_bonus(p, vs_npc=True, chainmace_charged=charged)
            your_atk = 6 + atk_bonus + int(p.wildy_level / 15)
            your_def = 6 + def_bonus + int(p.wildy_level / 20)

            roll_a = random.randint(0, your_atk)
            roll_d = random.randint(0, npc_def_stat)
            hit = max(0, roll_a - roll_d)

            # Zarveth forced zero mechanic
            if force_zero_next_hit:
                hit = 0
                force_zero_next_hit = False
                events.append("🕳️ The veil disrupts your swing — your hit is forced to **0**!")

            npc_hp = max(0, npc_hp - hit)
            events.append(f"🗡️ You hit **{hit}** | You: **{your_hp}/{self.config['max_hp']}** | {npc_name}: **{npc_hp}/{npc_max}**")
            events.extend(self._consume_buffs_on_hit(p))
            # Amulet of Seeping lifesteal
            healed = self._apply_seeping_heal(p, hit)
            if healed > 0:
                your_hp = int(p.hp)
                events.append(f"🩸 Amulet of Seeping heals **{healed}** | You: **{your_hp}/{self.config['max_hp']}**")

            if npc_hp <= 0:
                break

            roll_na = random.randint(0, npc_atk)
            roll_nd = random.randint(0, your_def)
            npc_hit = max(0, roll_na - roll_nd)

            if npc_type == "revenant" and p.equipment.get("amulet") == "Bracelet of ethereum":
                npc_hit = int(npc_hit * 0.5)

            your_hp = clamp(your_hp - npc_hit, 0, int(self.config["max_hp"]))
            events.append(f"💥 {npc_name} hits **{npc_hit}** | You: **{your_hp}/{self.config['max_hp']}** | {npc_name}: **{npc_hp}/{npc_max}**")

            # Zarveth 5% proc
            if npc_name == "Zarveth the Veilbreaker" and your_hp > 0 and npc_hp > 0:
                if random.random() < 0.05:
                    force_zero_next_hit = True
                    events.append("🌀 **Zarveth the Veilbreaker** shatters the veil! Your **next hit will deal 0**.")

            if your_hp > 0:
                before = your_hp
                your_hp, ate_food, _, healed = self._maybe_auto_eat_after_hit(p, your_hp)
                if ate_food:
                    events.append(f"🍖 Auto-eat **{ate_food}** (+{your_hp - before})")

        # ------------------ PLAYER DIED ------------------
        if your_hp <= 0:
            lost_items = dict(p.inventory)
            p.inventory.clear()

            bank_loss = int(p.bank_coins * 0.10)
            if bank_loss > 0:
                p.bank_coins -= bank_loss

            return False, npc_name, events, lost_items, bank_loss, []

        p.kills += 1
        p.hp = your_hp

        loot_lines: List[str] = []
        auto_drops: Dict[str, int] = {}

        max_items = 3
        items_dropped = 0

        coins = self._npc_coin_roll(npc_type)
        if coins > 0:
            p.coins += coins
            loot_lines.append(f"🪙 Coins: **+{coins}**")
        else:
            loot_lines.append("🪙 Coins: **+0**")

        def can_drop():
            return items_dropped < max_items

        if can_drop():
            w_roll = self._loot_for_level(p.wildy_level)
            if w_roll:
                item, qty = w_roll
                dest = self._try_put_item_with_blacklist(p, item, qty, auto_drops) 
                loot_lines.append(f"🎁 Wildy loot: **{item} x{qty}** {dest}".rstrip())
                items_dropped += 1

        if can_drop():
            npc_loot = self._npc_roll_table(npc_type, "loot")
            if npc_loot:
                item, qty = npc_loot
                dest = self._try_put_item_with_blacklist(p, item, qty, auto_drops)
                loot_lines.append(f"👹 {npc_name} loot: **{item} x{qty}** {dest}".rstrip())
                items_dropped += 1

        if can_drop():
            npc_unique = self._npc_roll_table(npc_type, "unique")
            if npc_unique:
                item, qty = npc_unique
                dest = self._try_put_item_with_blacklist(p, item, qty, auto_drops)
                if not self._is_blacklisted(p, item):
                    p.uniques[item] = p.uniques.get(item, 0) + qty
                    p.unique_drops += 1
                loot_lines.append(f"✨ UNIQUE: **{item} x{qty}** {dest}".rstrip())

                items_dropped += 1

        if can_drop():
            npc_special = self._npc_roll_table(npc_type, "special")
            if npc_special:
                item, qty = npc_special
                dest = self._try_put_item_with_blacklist(p, item, qty, auto_drops)
                loot_lines.append(f"🩸 SPECIAL: **{item} x{qty}** {dest}".rstrip())
                items_dropped += 1

        pet = self._npc_roll_pet(npc_type)
        if pet:
            if pet not in p.pets:
                p.pets.append(pet)
                p.pet_drops += 1
            loot_lines.append(f"🐾 PET: **{pet}**")

        if auto_drops:
            loot_lines.append("🗑️ Auto-dropped (blacklist):")
            for name, q in sorted(auto_drops.items(), key=lambda x: x[0].lower()):
                loot_lines.append(f"- {name} x{q}")

        return True, npc_name, events, {}, 0, loot_lines

    # Commands
    @commands.group(name="w", invoke_without_command=True)
    async def w(self, ctx: commands.Context):
        if not await self._ensure_ready(ctx):
            return
        await ctx.reply(
            "**Wilderness commands**\n"
            "!w start (one-time until reset)\n"
            "!w reset (wipe your profile)\n"
            "!w hp / !w health\n"
            "!w venture <level>\n"
            "!w equip <item> / !w unequip <slot> / !w gear\n"
            "!w inspect <itemname>\n"
            "!w fight <npc name>\n"
            "!w npcs\n"
            "!w attack @user\n"
            "!w tele\n"
            "!w eat <foodname>\n"
            "!w drink <potionname>\n"
            "!w drop <itemname>\n"
            "!w bank / !w bankview\n"
            "!w withdraw <qty> <item>\n"
            "!w inv\n"
            "!w chest open\n"
            "!w trade <playername> / !w trade accept"
            "!w shop list / !w shop buy <quantity> <item> / !w shop sell <quantity> <item>\n"
            "!w blacklist / !w blacklist remove <item> / !w blacklist clear\n"
            "!w lock <itemname> / !w lock remove <itemname>"
        )

    @w.group(name="trade", invoke_without_command=True)
    async def trade_cmd(self, ctx: commands.Context, target: Optional[discord.Member] = None):
        if not await self._ensure_ready(ctx):
            return

        if target is None:
            await ctx.reply(
                "Usage:\n"
                "`!w trade @player` (request)\n"
                "`!w trade accept`\n"
                "`!w trade add <qty> <item>`\n"
                "`!w trade remove <qty> <item>`\n"
                "`!w trade cancel`"
            )
            return

        await self.trade_mgr.start_trade_request(ctx, target)

    @trade_cmd.command(name="accept")
    async def trade_accept_cmd(self, ctx: commands.Context):
        if not await self._ensure_ready(ctx):
            return
        await self.trade_mgr.accept_trade(ctx)

    @trade_cmd.command(name="add")
    async def trade_add_cmd(self, ctx: commands.Context, qty: int, *, itemname: str):
        if not await self._ensure_ready(ctx):
            return
        await self.trade_mgr.add_to_trade(ctx, qty, itemname)

    @trade_cmd.command(name="remove", aliases=["rm", "del"])
    async def trade_remove_cmd(self, ctx: commands.Context, qty: int, *, itemname: str):
        if not await self._ensure_ready(ctx):
            return
        await self.trade_mgr.remove_from_trade(ctx, qty, itemname)

    @trade_cmd.command(name="cancel")
    async def trade_cancel_cmd(self, ctx: commands.Context):
        if not await self._ensure_ready(ctx):
            return
        await self.trade_mgr.cancel_trade_by_command(ctx)

    @w.group(name="blacklist", invoke_without_command=True)
    async def blacklist_cmd(self, ctx: commands.Context, *, itemname: Optional[str] = None):
        if not await self._ensure_ready(ctx):
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)

            # If no item provided -> show list
            if not itemname:
                bl = getattr(p, "blacklist", None) or []
                if not bl:
                    await ctx.reply("🚫 Your blacklist is empty.\nAdd one: `!w blacklist <itemname>`")
                    return
                pretty = "\n".join(f"- {x}" for x in sorted(bl, key=lambda s: s.lower()))
                await ctx.reply(f"🚫 **Blacklisted items:**\n{pretty}")
                return

            # Resolve item (supports aliases + food)
            canonical = self._resolve_item(itemname)
            if not canonical:
                food_key = self._resolve_food(itemname)
                canonical = food_key

            if not canonical:
                await ctx.reply("Unknown item. Try `!w inspect <itemname>` to check names/aliases.")
                return

            # Prevent duplicates using normalized compare
            if any(self._norm(x) == self._norm(canonical) for x in (p.blacklist or [])):
                await ctx.reply(f"🚫 **{canonical}** is already blacklisted.")
                return

            p.blacklist = (p.blacklist or []) + [canonical]
            await self._persist()

        await ctx.reply(
            f"🚫 Blacklisted **{canonical}**.\n"
            f"If it drops, it will be **auto-dropped immediately** and shown in the post-fight loot log."
        )

    @blacklist_cmd.command(name="remove", aliases=["rm", "del"])
    async def blacklist_remove_cmd(self, ctx: commands.Context, *, itemname: str):
        if not await self._ensure_ready(ctx):
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)
            bl = getattr(p, "blacklist", None) or []
            if not bl:
                await ctx.reply("Your blacklist is empty.")
                return

            target_norm = self._norm(itemname)
            new_bl = [x for x in bl if self._norm(x) != target_norm]

            if len(new_bl) == len(bl):
                await ctx.reply("That item is not on your blacklist.")
                return

            p.blacklist = new_bl
            await self._persist()

        await ctx.reply("✅ Removed from your blacklist.")

    @blacklist_cmd.command(name="clear")
    async def blacklist_clear_cmd(self, ctx: commands.Context):
        if not await self._ensure_ready(ctx):
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)
            p.blacklist = []
            await self._persist()

        await ctx.reply("✅ Cleared your blacklist.")

    @w.command(name="drink")
    async def drink_cmd(self, ctx: commands.Context, *, potion_name: str):
        if not await self._ensure_ready(ctx):
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)

            query = self._norm(potion_name)

            base_name = None
            potion_data = None

            for name, meta in POTIONS.items():
                aliases = meta.get("aliases", "")
                alias_list = [self._norm(a) for a in aliases.split(",")] if aliases else []
                if query == self._norm(name) or query in alias_list:
                    base_name = name
                    potion_data = meta
                    break

            if not base_name:
                await ctx.reply("Unknown potion.")
                return

            inv_item = None
            uses = 0
            best_uses = 999999  # big number

            for item in p.inventory.keys():
                if self._norm(item).startswith(self._norm(base_name)):
                    match = re.search(r"\((\d+)\)", item)
                    if match:
                        u = int(match.group(1))
                        if u < best_uses:
                            best_uses = u
                            uses = u
                            inv_item = item

            if not inv_item or uses <= 0:
                await ctx.reply(f"You don’t have any **{base_name}**.")
                return

            # Remove current potion
            self._remove_item(p.inventory, inv_item, 1)

            # Apply buff
            p.active_buffs[base_name] = {
                "atk": potion_data.get("atk", 0),
                "remaining_hits": potion_data.get("hits", 0)
            }

            # Downgrade dose
            uses -= 1
            if uses > 0:
                new_name = f"{base_name} ({uses})"
                self._add_item(p.inventory, new_name, 1)

            await self._persist()

        await ctx.reply(
            f"🧪 You drink **{base_name}**!\n"
            f"+{potion_data['atk']} attack for {potion_data['hits']} hits."
        )

    @w.command(name="hp", aliases=["health"])
    async def hp_cmd(self, ctx: commands.Context):
        if not await self._ensure_ready(ctx):
            return
        p = self._get_player(ctx.author)
        where = "Wilderness" if p.in_wilderness else "Safe"
        await ctx.reply(f"❤️ HP: **{p.hp}/{self.config['max_hp']}** — {where}")

    @w.command(name="npcs")
    async def npcs_cmd(self, ctx: commands.Context):
        if not await self._ensure_ready(ctx):
            return

        emb = self._npc_info_embed(NPCS[0][0], ctx.guild)
        view = NPCInfoView(self, author_id=ctx.author.id)
        await ctx.reply(embed=emb, view=view)

    @w.command(name="eat")
    async def eat_cmd(self, ctx: commands.Context, *, foodname: str):
        if not await self._ensure_ready(ctx):
            return

        # Don't allow during an active PvP
        if self._duel_active_for_user(ctx.author.id):
            await ctx.reply("You’re in a PvP fight — use the **Eat** button on your turn.")
            return

        food_key = self._resolve_food(foodname)
        if not food_key:
            await ctx.reply("Unknown food. Example: `!w eat lobster` or `!w eat shark`.")
            return

        heal = int(FOOD[food_key].get("heal", 0))
        if heal <= 0:
            await ctx.reply("That food has no heal value.")
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)
            if p.inventory.get(food_key, 0) <= 0:
                await ctx.reply(f"You don’t have **{food_key}** in your inventory.")
                return
            if not self._remove_item(p.inventory, food_key, 1):
                await ctx.reply(f"You don’t have **{food_key}** in your inventory.")
                return
            before = p.hp
            p.hp = clamp(p.hp + heal, 0, int(self.config["max_hp"]))
            self._touch(p)
            await self._persist()

        await ctx.reply(f"🍖 You eat **{food_key}** and heal **{p.hp - before}**. HP: **{p.hp}/{self.config['max_hp']}**")

    @w.command(name="drop")
    async def drop_cmd(self, ctx: commands.Context, *, itemname: str):
        if not await self._ensure_ready(ctx):
            return

        if self._duel_active_for_user(ctx.author.id):
            await ctx.reply("You’re in a PvP fight — finish the fight before dropping items.")
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)
            inv_key = self._resolve_from_keys_case_insensitive(itemname, p.inventory.keys())
            if not inv_key:
                maybe = self._resolve_item(itemname)
                if maybe:
                    inv_key = self._resolve_from_keys_case_insensitive(maybe, p.inventory.keys())

            if not inv_key:
                await ctx.reply("That item isn’t in your inventory.")
                return

            qty = int(p.inventory.get(inv_key, 0))
            if qty <= 0:
                await ctx.reply("That item isn’t in your inventory.")
                return

            p.inventory.pop(inv_key, None)
            self._touch(p)
            await self._persist()

        await ctx.reply(f"🗑️ Dropped **{inv_key} x{qty}** from your inventory.")

    @w.command(name="inspect")
    async def inspect(self, ctx: commands.Context, *, itemname: str):
        if not await self._ensure_ready(ctx):
            return
        raw = itemname.strip()

        food_key = self._resolve_food(raw)
        if food_key:
            heal = int(FOOD[food_key].get("heal", 0))
            await ctx.reply(f"🍖 **{food_key}**\nHeals: **{heal} HP**")
            return

        # equippable (supports aliases)
        item_key = self._resolve_item(raw)
        meta = ITEMS.get(item_key) if item_key else None
        if meta and self._item_slot(item_key):
            slot = self._item_slot(item_key)
            atk = int(meta.get("atk", 0))
            deff = int(meta.get("def", 0))
            atk_vs_npc = int(meta.get("atk_vs_npc", 0))
            stackable = bool(meta.get("stackable", False))
            sell_value = int(meta.get("value", 0))

            parts = [
                f"🧩 **{item_key}**",
                f"Slot: **{slot}**",
                f"Stackable: **{stackable}**",
            ]

            stat_line = f"Stats: **+{atk} atk / +{deff} def**"
            if atk_vs_npc:
                stat_line += f" | **+{atk_vs_npc} atk vs NPCs**"
            parts.append(stat_line)

            if sell_value > 0:
                parts.append(f"💰 Sell value: **{sell_value:,} coins**")

            effect = (self.config.get("item_effects", {}) or {}).get(item_key, {}).get("effect")
            if effect:
                parts.append(f"Effect: {effect}")

            await ctx.reply("\n".join(parts))
            return

        if item_key and meta:
            stackable = bool(meta.get("stackable", False))
            effect = (self.config.get("item_effects", {}) or {}).get(item_key, {}).get("effect")
            lines = [f"📦 **{item_key}**", f"Stackable: **{stackable}**"]
            if effect:
                lines.append(f"Effect: {effect}")
            await ctx.reply("\n".join(lines))
            return

        effects = (self.config.get("item_effects", {}) or {})
        effect_key = None
        for k in effects.keys():
            if self._norm(k) == self._norm(raw):
                effect_key = k
                break
        if effect_key:
            await ctx.reply(f"✨ **{effect_key}**\nEffect: {effects[effect_key].get('effect', '')}")
            return

        await ctx.reply(f"**{raw}**\nThis item has no use currently.")

    @w.command(name="reset")
    async def reset(self, ctx: commands.Context):
        if not await self._ensure_ready(ctx):
            return
        async with self._mem_lock:
            self.players.pop(ctx.author.id, None)
            await self._persist()
        await ctx.reply("✅ Your Wilderness profile has been **reset**. Use !w start to begin again.")

    @w.command(name="start")
    async def start(self, ctx: commands.Context):
        if not await self._ensure_ready(ctx):
            return
        async with self._mem_lock:
            p = self._get_player(ctx.author)
            if p.started:
                await ctx.reply("You’ve already started. Use !w reset if you want to wipe and start over.")
                return
            p.started = True
            p.coins = int(self.config["starting_coins"])
            p.bank_coins = 0
            p.inventory.clear()
            p.bank.clear()
            p.risk.clear()
            p.equipment.clear()
            p.uniques.clear()
            p.pets.clear()
            p.kills = p.deaths = p.ventures = p.escapes = 0
            p.biggest_win = p.biggest_loss = 0
            p.unique_drops = p.pet_drops = 0
            p.cd.clear()
            p.hp = int(self.config["starting_hp"])
            p.in_wilderness = False
            p.wildy_level = 1
            p.skulled = False
            p.last_action = _now()
            self._add_item(p.inventory, "Starter Sword", 1)
            self._add_item(p.inventory, "Starter Platebody", 1)
            await self._persist()

        await ctx.reply(
            f"Profile created! You have **{p.coins} coins** and **{p.hp}/{self.config['max_hp']} HP**.\n"
            f"Starter gear received: **Starter Sword** and **Starter Platebody**.\n"
            f"Equip your gear: !w equip starter sword and !w equip starter platebody.\n"
            f"Then venture out: !w venture 5."
        )

    # Equipment
    @w.command(name="gear")
    async def gear(self, ctx: commands.Context):
        if not await self._ensure_ready(ctx):
            return
        p = self._get_player(ctx.author)
        if not p.equipment:
            await ctx.reply("You have nothing equipped.")
            return
        atk, deff = self._equipped_bonus(p, vs_npc=False)
        lines = [f"- **{slot}**: {item}" for slot, item in p.equipment.items()]
        await ctx.reply("**Equipped:**\n" + "\n".join(lines) + f"\nBonuses (PvP): **+{atk} atk / +{deff} def**")

    @w.command(name="equip")
    async def equip(self, ctx: commands.Context, *, item: str):
        if not await self._ensure_ready(ctx):
            return
        raw = item.strip()
        item_key = self._resolve_item(raw)
        if not item_key:
            await ctx.reply("That item isn’t equippable (or no slot defined for it).")
            return
        slot = self._item_slot(item_key)
        if not slot:
            await ctx.reply("That item isn’t equippable (or no slot defined for it).")
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)
            if p.in_wilderness:
                inv_key = self._resolve_from_keys_case_insensitive(item_key, p.inventory.keys())
                has_in_inv = (inv_key is not None and p.inventory.get(inv_key, 0) > 0)
                if not has_in_inv:
                    await ctx.reply(f"You must have **{item_key}** in your inventory to equip it in the Wilderness.")
                    return
            else:
                inv_key = self._resolve_from_keys_case_insensitive(item_key, p.inventory.keys())
                bank_key = self._resolve_from_keys_case_insensitive(item_key, p.bank.keys())
                has_in_inv = (inv_key is not None and p.inventory.get(inv_key, 0) > 0)
                has_in_bank = (bank_key is not None and p.bank.get(bank_key, 0) > 0)
                if not has_in_inv and not has_in_bank:
                    await ctx.reply(f"You don’t have **{item_key}** in your inventory or bank.")
                    return

            old = p.equipment.get(slot)
            if old:
                if self._inv_free_slots(p.inventory) < 1:
                    await ctx.reply("No inventory space to swap gear (need 1 free slot).")
                    return
                self._add_item(p.inventory, old, 1)

            if p.in_wilderness:
                self._remove_item(p.inventory, inv_key, 1)
            else:
                if has_in_inv:
                    self._remove_item(p.inventory, inv_key, 1)
                else:
                    self._remove_item(p.bank, bank_key, 1)

            p.equipment[slot] = item_key
            await self._persist()

        await ctx.reply(f"✅ Equipped **{item_key}** in slot **{slot}**.")

    @w.command(name="unequip")
    async def unequip(self, ctx: commands.Context, slot: str):
        if not await self._ensure_ready(ctx):
            return
        slot = slot.strip().lower()
        if slot not in EQUIP_SLOT_SET:
            await ctx.reply(f"Unknown slot. Slots: {', '.join(sorted(EQUIP_SLOT_SET))}")
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)
            item = p.equipment.get(slot)
            if not item:
                await ctx.reply("Nothing equipped in that slot.")
                return

            if self._inv_free_slots(p.inventory) < 1:
                await ctx.reply("No inventory space to unequip (need 1 free slot).")
                return

            self._add_item(p.inventory, item, 1)
            p.equipment.pop(slot, None)
            await self._persist()

        await ctx.reply(f"✅ Unequipped **{item}** from **{slot}**.")

    # Inventory / Bank
    @w.command(name="inv")
    async def inv(self, ctx: commands.Context):
        if not await self._ensure_ready(ctx):
            return

        p = self._get_player(ctx.author)

        inv = p.inventory.copy()
        inv[self.config["coins_item_name"]] = p.coins

        used = self._inv_slots_used(p.inventory)
        max_inv = int(self.config["max_inventory_items"])

        locked = getattr(p, "locked", None) or []

        def is_locked_display(name: str) -> bool:
            # Coins shouldn't be lockable (and aren't in p.inventory anyway)
            if name == self.config["coins_item_name"]:
                return False
            target = self._norm(name)
            return any(self._norm(x) == target for x in locked)

        if inv:
            lines = []
            for k, v in sorted(inv.items(), key=lambda kv: self._norm(kv[0])):
                lock_icon = " 🔒" if is_locked_display(k) else ""
                lines.append(f"- {k} x{v}{lock_icon}")
            pretty = "\n".join(lines)
        else:
            pretty = "Empty"

        await ctx.reply(f"**Inventory ({used}/{max_inv} slots):**\n{pretty}")

    @w.command(name="bankview")
    async def bankview(self, ctx: commands.Context):
        if not await self._ensure_ready(ctx):
            return
        p = self._get_player(ctx.author)
        bank = p.bank.copy()
        if p.bank_coins:
            bank[self.config["coins_item_name"]] = p.bank_coins
        if not bank:
            await ctx.reply("Your bank is empty.")
            return
        pretty = "\n".join([f"- {k} x{v}" for k, v in sorted(bank.items())])
        await ctx.reply(f"**Bank:**\n{pretty}")

    @w.command(name="bank")
    async def bank_cmd(self, ctx: commands.Context):
        if not await self._ensure_ready(ctx):
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)

            ok, left = self._cd_ready(p, "bank", int(self.config["bank_cooldown_sec"]))
            if not ok:
                await ctx.reply(f"Bank cooldown: **{left}s**")
                return

            if p.in_wilderness:
                await ctx.reply("You can’t bank in the Wilderness. !w tele out first.")
                return

            banked_items: Dict[str, int] = {}
            kept_locked: Dict[str, int] = {}
            banked_coins = int(p.coins)

            # Move inventory items except locked ones
            for item, qty in list(p.inventory.items()):
                if qty <= 0:
                    continue

                if self._is_locked(p, item):
                    kept_locked[item] = qty
                    continue

                # Normal banking
                self._add_item(p.bank, item, qty)
                banked_items[item] = qty
                p.inventory.pop(item, None)

            # Bank coins
            if p.coins > 0:
                p.bank_coins += p.coins
                p.coins = 0

            self._set_cd(p, "bank")
            await self._persist()

        # ----- Output message -----
        lines = []

        if banked_items:
            lines.append("📦 **Banked items:**")
            lines.append(self._format_items_short(banked_items, max_lines=18))
        else:
            lines.append("📦 **Banked items:** (none)")
        if banked_coins > 0:
            lines.append(f"🪙 **Banked coins:** {banked_coins:,}")

        lines.append("(Equipped gear unchanged.)")

        await ctx.reply("\n".join(lines))

    @w.command(name="withdraw", aliases=["withdra"])
    async def withdraw(self, ctx: commands.Context, qty: int, *, item: str):
        if not await self._ensure_ready(ctx):
            return
        if qty <= 0:
            await ctx.reply("Quantity must be > 0.")
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)
            if p.in_wilderness:
                await ctx.reply("Withdraw items out of the Wilderness. !w tele first.")
                return

            bank_key = self._resolve_from_keys_case_insensitive(item, p.bank.keys())

            if not bank_key:
                maybe_canonical = self._resolve_item(item)
                if maybe_canonical:
                    bank_key = self._resolve_from_keys_case_insensitive(maybe_canonical, p.bank.keys())

            if not bank_key:
                await ctx.reply("That item isn’t in your bank.")
                return

            have = p.bank.get(bank_key, 0)
            if have < qty:
                await ctx.reply(f"You only have **{have}** of **{bank_key}** in your bank.")
                return

            space = self._inv_free_slots(p.inventory)
            if space <= 0:
                await ctx.reply("Your inventory is full.")
                return

            if bank_key in FOOD or (not self._is_stackable(bank_key) and bank_key not in FOOD):
                take = min(space, qty)
            else:
                need = self._slots_needed_to_add(p.inventory, bank_key, qty)
                take = qty if (need == 0 or space >= need) else 0

            if take <= 0:
                await ctx.reply("No inventory space for that item.")
                return

            self._remove_item(p.bank, bank_key, take)
            self._add_item(p.inventory, bank_key, take)
            await self._persist()

        if take < qty:
            await ctx.reply(f"Withdrew **{bank_key} x{take}** (inventory full; {qty - take} left in bank).")
        else:
            await ctx.reply(f"Withdrew **{bank_key} x{take}**.")

    # Venture
    @w.command(name="venture")
    async def venture(self, ctx: commands.Context, wildy_level: Optional[int] = None):
        if not await self._ensure_ready(ctx):
            return

        if self._duel_active_for_user(ctx.author.id):
            await ctx.reply("You’re in a PvP fight — finish it before venturing deeper.")
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)

            ok, left = self._cd_ready(p, "venture", int(self.config["venture_cooldown_sec"]))
            if not ok:
                await ctx.reply(f"Venture cooldown: **{left}s**")
                return

            if not p.started:
                await ctx.reply("You haven’t started yet. Use !w start.")
                return

            cap = int(self.config["deep_wildy_level_cap"])

            if not p.equipment:
                await ctx.reply("You must equip gear first. Example: !w equip starter sword.")
                return

            if wildy_level is None:
                if not p.in_wilderness:
                    wildy_level = random.randint(1, cap)
                else:
                    if p.wildy_level >= cap:
                        await ctx.reply(f"You're already at the deepest wilderness level (**{cap}**).")
                        return
                    wildy_level = random.randint(p.wildy_level + 1, cap)

            wildy_level = clamp(int(wildy_level), 1, cap)

            if p.in_wilderness:
                if wildy_level <= p.wildy_level:
                    await ctx.reply(
                        f"You’re already in the Wilderness at level **{p.wildy_level}**. "
                        f"Pick a higher level to venture deeper (max **{cap}**)."
                    )
                    return

                p.wildy_level = wildy_level

                if not p.skulled:
                    skull_chance = min(0.10 + (wildy_level / cap) * 0.35, 0.45)
                    if random.random() < skull_chance:
                        p.skulled = True

                p.ventures += 1
                self._touch(p)
                self._set_cd(p, "venture")
                await self._persist()

                await ctx.reply(
                    f"⬆️ You venture **deeper** into the Wilderness (**level {wildy_level}**). "
                    f"{'☠️ You are **SKULLED**.' if p.skulled else 'You are not skulled.'}\n"
                    f"Next: !w fight or !w attack @user or !w tele."
                )
                return

            p.in_wilderness = True
            p.wildy_level = wildy_level
            p.ventures += 1

            skull_chance = min(0.10 + (wildy_level / cap) * 0.35, 0.45)
            if random.random() < skull_chance:
                p.skulled = True

            self._touch(p)
            self._set_cd(p, "venture")
            await self._persist()

        await ctx.reply(
            f"⚔️ You venture into the **Wilderness (level {wildy_level})**. "
            f"{'☠️ You are **SKULLED**.' if p.skulled else 'You are not skulled.'}\n"
            f"Next: !w fight or !w attack @user or !w tele."
        )


    # NPC Fight
    @w.command(name="fight")
    async def fight_npc(self, ctx: commands.Context, *, npcname: Optional[str] = None):
        """
        !w fight              -> existing behavior (random eligible NPC)
        !w fight <npcname>    -> 50% chance to force that NPC, otherwise random eligible NPC
        """
        if not await self._ensure_ready(ctx):
            return

        forced_npc: Optional[Tuple[str, int, int, int, str, int, int]] = None
        forced_success = False

        async with self._mem_lock:
            p = self._get_player(ctx.author)
            if not p.in_wilderness:
                await ctx.reply("You’re not in the Wilderness. Use !w venture.")
                return

            self._touch(p)

            eligible = [n for n in NPCS if p.wildy_level >= n[3]] or [NPCS[0]]

            if npcname:
                forced_npc = self._resolve_npc(npcname)
                if not forced_npc:
                    await ctx.reply("Unknown NPC. Use `!w npcs` to see the list.")
                    return
                if p.wildy_level < int(forced_npc[3]):
                    await ctx.reply(
                        f"That NPC requires Wilderness level **{forced_npc[3]}**. "
                        f"You're currently **{p.wildy_level}**."
                    )
                    return

                forced_success = (random.random() <= 0.50)
                if forced_success:
                    chosen = forced_npc
                else:
                    pool = [n for n in eligible if self._norm(n[0]) != self._norm(forced_npc[0])]
                    chosen = random.choice(pool) if pool else random.choice(eligible)
            else:
                chosen = random.choice(eligible)

            npc_name, npc_hp, npc_tier, _, npc_type, npc_atk_bonus, npc_def_bonus = chosen

            if npc_type == "overlord" and p.equipment.get("gloves") == "Wristwraps of the Damned":
                npc_hp = int(npc_hp * 0.70)

            # HP scaling (change /8 to whatever scaling you want)
            npc_hp = npc_hp + int(p.wildy_level / 8)
            npc_max = npc_hp

            npc_atk = 1 + npc_tier + npc_atk_bonus + int(p.wildy_level / 12)
            npc_def_stat = npc_tier + npc_def_bonus + int(p.wildy_level / 20)

            start_hp = p.hp
            your_hp = p.hp

            events: List[str] = []
            if forced_npc:
                if forced_success:
                    events.append(f"🎯 Targeted fight: **{forced_npc[0]}** — **SUCCESS (50%)**")
                else:
                    events.append(f"🎯 Targeted fight: **{forced_npc[0]}** — **FAILED (50%)**, random encounter instead…")

            events.append(f"👹 **{npc_name}** (HP **{npc_max}**) — You start **{start_hp}/{self.config['max_hp']}**")

            force_zero_next_hit = False

            while npc_hp > 0 and your_hp > 0:
                # PvM ether consumption: 3 per hit IF available. If not available, chainmace is uncharged.
                charged = False
                if p.equipment.get("mainhand") == "Viggora's Chainmace":
                    if p.inventory.get("Revenant ether", 0) >= 3:
                        charged = True
                        self._remove_item(p.inventory, "Revenant ether", 3)

                atk_bonus, def_bonus = self._equipped_bonus(p, vs_npc=True, chainmace_charged=charged)
                your_atk = 6 + atk_bonus + int(p.wildy_level / 15)
                your_def = 6 + def_bonus + int(p.wildy_level / 20)

                roll_a = random.randint(0, your_atk)
                roll_d = random.randint(0, npc_def_stat)
                hit = max(0, roll_a - roll_d)

                # --- Zarveth debuff: force your next hit to 0 ---
                if force_zero_next_hit:
                    hit = 0
                    force_zero_next_hit = False
                    events.append("🕳️ The veil disrupts your swing — your hit is forced to **0**!")

                npc_hp = max(0, npc_hp - hit)
                events.append(
                    f"🗡️ You hit **{hit}** | You: **{your_hp}/{self.config['max_hp']}** | {npc_name}: **{npc_hp}/{npc_max}**"
                )
                # Amulet of Seeping lifesteal
                healed = self._apply_seeping_heal(p, hit)
                if healed > 0:
                    your_hp = int(p.hp)
                    events.append(f"🩸 Amulet of Seeping heals **{healed}** | You: **{your_hp}/{self.config['max_hp']}**")

                events.extend(self._consume_buffs_on_hit(p))
                if npc_hp <= 0:
                    break

                roll_na = random.randint(0, npc_atk)
                roll_nd = random.randint(0, your_def)
                npc_hit = max(0, roll_na - roll_nd)

                if npc_type == "revenant" and p.equipment.get("amulet") == "Bracelet of ethereum":
                    npc_hit = int(npc_hit * 0.5)

                your_hp = clamp(your_hp - npc_hit, 0, int(self.config["max_hp"]))
                events.append(
                    f"💥 {npc_name} hits **{npc_hit}** | You: **{your_hp}/{self.config['max_hp']}** | {npc_name}: **{npc_hp}/{npc_max}**"
                )

                # --- Zarveth special: 5% chance to apply debuff on its attack ---
                if npc_name == "Zarveth the Veilbreaker" and your_hp > 0 and npc_hp > 0:
                    if random.random() < 0.05:
                        force_zero_next_hit = True
                        events.append("🌀 **Zarveth the Veilbreaker** shatters the veil! Your **next hit will deal 0**.")

                if your_hp > 0:
                    before = your_hp
                    your_hp, ate_food, extra_roll, healed = self._maybe_auto_eat_after_hit(p, your_hp)
                    if ate_food:
                        events.append(f"🍖 Auto-eat **{ate_food}** (+{your_hp - before}) | You: **{your_hp}/{self.config['max_hp']}**")


            def build_pages(lines: List[str], per_page: int = 10) -> List[str]:
                pages: List[str] = []
                for i in range(0, len(lines), per_page):
                    chunk = lines[i:i + per_page]
                    pages.append("\n".join(chunk))
                return pages or ["(no log)"]

            if your_hp <= 0:
                lost_items = dict(p.inventory)

                p.inventory.clear()
                bank_loss = int(p.bank_coins * 0.10)
                if bank_loss > 0:
                    p.bank_coins = max(0, p.bank_coins - bank_loss)

                p.deaths += 1
                p.in_wilderness = False
                p.skulled = False
                p.wildy_level = 1
                p.hp = int(self.config["starting_hp"])
                self._full_heal(p)
                await self._persist()

                pages = build_pages(events, per_page=10)
                pages[-1] += (
                    f"\n\n☠️ **You died to {npc_name}.**\n"
                    f"📉 **Lost from inventory:**\n{self._format_items_short(lost_items, max_lines=18)}\n"
                    f"🏦 Lost bank coins: **{bank_loss:,}** (10%)"
                )

                view = FightLogView(author_id=ctx.author.id, pages=pages, title=f"{ctx.author.display_name} vs {npc_name}")
                await ctx.reply(content=view._render(), view=view)
                return

            p.kills += 1
            p.hp = clamp(your_hp, 0, int(self.config["max_hp"]))
            self._touch(p)

            loot_lines: List[str] = []
            auto_drops: Dict[str, int] = {} 

            max_items = 3
            items_dropped = 0

            coins = self._npc_coin_roll(npc_type)
            if coins > 0:
                p.coins += coins
                loot_lines.append(f"🪙 Coins: **+{coins}**")
            else:
                loot_lines.append("🪙 Coins: **+0**")

            def can_drop_more() -> bool:
                return items_dropped < max_items

            if can_drop_more():
                w_roll = self._loot_for_level(p.wildy_level)
                if w_roll:
                    item, qty = w_roll
                    dest = self._try_put_item_with_blacklist(p, item, qty, auto_drops)
                    loot_lines.append(f"🎁 Wildy loot: **{item} x{qty}** {dest}".rstrip())
                    items_dropped += 1

            if can_drop_more():
                npc_loot = self._npc_roll_table(npc_type, "loot")
                if npc_loot:
                    item, qty = npc_loot
                    dest = self._try_put_item_with_blacklist(p, item, qty, auto_drops)
                    loot_lines.append(f"👹 {npc_name} loot: **{item} x{qty}** {dest}".rstrip())
                    items_dropped += 1

            if can_drop_more():
                npc_unique = self._npc_roll_table(npc_type, "unique")
                if npc_unique:
                    item, qty = npc_unique
                    dest = self._try_put_item_with_blacklist(p, item, qty, auto_drops)
                    if not self._is_blacklisted(p, item):
                        p.uniques[item] = p.uniques.get(item, 0) + qty
                        p.unique_drops += 1
                    loot_lines.append(f"✨ UNIQUE: **{item} x{qty}** {dest}".rstrip())
                    items_dropped += 1

            if can_drop_more():
                npc_special = self._npc_roll_table(npc_type, "special")
                if npc_special:
                    item, qty = npc_special
                    dest = self._try_put_item_with_blacklist(p, item, qty, auto_drops) 
                    loot_lines.append(f"🩸 SPECIAL: **{item} x{qty}** {dest}".rstrip())
                    items_dropped += 1

            pet = self._npc_roll_pet(npc_type)
            if pet:
                if pet not in p.pets:
                    p.pets.append(pet)
                    p.pet_drops += 1
                loot_lines.append(f"🐾 PET: **{pet}**")

            if auto_drops:
                loot_lines.append("🗑️ Auto-dropped (blacklist):")
                for name, q in sorted(auto_drops.items(), key=lambda x: x[0].lower()):
                    loot_lines.append(f"- {name} x{q}")

            await self._persist()

            pages = build_pages(events, per_page=10)
            pages[-1] += (
                f"\n\n✅ **You win!** End HP: **{p.hp}/{self.config['max_hp']}**\n"
                + ("\n".join(loot_lines) if loot_lines else "(no loot)")
            )

            view = FightLogView(author_id=ctx.author.id, pages=pages, title=f"{ctx.author.display_name} vs {npc_name}")
            await ctx.reply(content=view._render(), view=view)

    # Turn-based PvP fight (attack)
    @w.command(name="attack")
    async def attack(self, ctx: commands.Context, target: discord.Member):
        if not await self._ensure_ready(ctx):
            return
        if target.bot or target.id == ctx.author.id:
            await ctx.reply("Pick a real person (not yourself, not a bot).")
            return
        async with self._mem_lock:
            a = self._get_player(ctx.author)
            b = self._get_player(target)
            ok, left = self._cd_ready(a, "attack", int(self.config["attack_cooldown_sec"]))
            if not ok:
                await ctx.reply(f"Attack cooldown: **{left}s**")
                return
            if not a.in_wilderness:
                await ctx.reply("You’re not in the Wilderness. Use !w venture.")
                return
            if not b.in_wilderness:
                await ctx.reply(f"{target.display_name} is not in the Wilderness.")
                return
            if self._duel_active_for_user(ctx.author.id) or self._duel_active_for_user(target.id):
                await ctx.reply("One of you is already in a fight.")
                return
            if ctx.channel and self.duels_by_channel.get(ctx.channel.id):
                await ctx.reply("There’s already an active fight in this channel.")
                return

            a.skulled = True
            b.skulled = True

            self._touch(a)
            self._touch(b)

            duel = DuelState(
                a_id=ctx.author.id,
                b_id=target.id,
                channel_id=ctx.channel.id if ctx.channel else 0,
                started_at=_now(),
                turn_id=random.choice([ctx.author.id, target.id]),
                log=["⚔️ Fight started!"],
                a_acted=False,
                b_acted=False,
            )
            self.duels_by_pair[self._pair_key(duel.a_id, duel.b_id)] = duel
            if duel.channel_id:
                self.duels_by_channel[duel.channel_id] = duel

            self._set_cd(a, "attack")
            await self._persist()

        await ctx.reply(
            self._duel_render(duel, ctx.author, target, self._get_player(ctx.author), self._get_player(target), ended=False),
            view=DuelView(self, duel),
        )

    @w.command(name="tele")
    async def tele(self, ctx: commands.Context):
        if not await self._ensure_ready(ctx):
            return

        if self._duel_active_for_user(ctx.author.id):
            await ctx.reply("You’re in a PvP fight — use the **Teleport** button on your turn.")
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)

            ok, left = self._cd_ready(p, "tele", int(self.config["teleport_cooldown_sec"]))
            if not ok:
                await ctx.reply(f"Teleport cooldown: **{left}s**")
                return

            if not p.in_wilderness:
                await ctx.reply("You’re not in the Wilderness.")
                return

            self._touch(p)
            self._set_cd(p, "tele")

            # 20% ambush
            if random.random() < 0.20:
                eligible = [n for n in NPCS if p.wildy_level >= n[3]] or [NPCS[0]]
                chosen = random.choice(eligible)

                header = [
                    f"⚠️ **Ambush!** You tried to teleport but were attacked by **{chosen[0]}** (Wildy {p.wildy_level})."
                ]

                won, npc_name, events, lost_items, bank_loss, loot_lines = \
                    self._simulate_pvm_fight_and_loot(p, chosen, header_lines=header)

                if not won:
                    p.deaths += 1
                    p.in_wilderness = False
                    p.skulled = False
                    p.wildy_level = 1
                    p.hp = int(self.config["starting_hp"])
                    self._full_heal(p)
                    await self._persist()

                    await ctx.reply(
                        "\n".join(events[-12:])
                        + f"\n\n☠️ You died during the ambush.\n"
                        + f"📉 Lost from inventory:\n{self._format_items_short(lost_items, 18)}\n"
                        + f"🏦 Lost bank coins: **{bank_loss:,}** (10%)."
                    )
                    return

                await self._persist()

                await ctx.reply(
                    "\n".join(events[-12:])
                    + "\n\n✅ You survived the ambush! Your teleport was interrupted.\n"
                    + "\n".join(loot_lines)
                    + f"\n\nYou are still in the Wilderness (level {p.wildy_level}). Try `!w tele` again."
                )
                return

            # 80% successful teleport
            p.in_wilderness = False
            p.skulled = False
            p.wildy_level = 1
            p.escapes += 1
            self._full_heal(p)
            await self._persist()

        await ctx.reply("✨ Teleport successful! (You are fully healed)")

    # Chest

    @w.group(name="lock", invoke_without_command=True)
    async def lock_cmd(self, ctx: commands.Context, *, itemname: Optional[str] = None):
        """
        !w lock
        !w lock <itemname>
        """
        if not await self._ensure_ready(ctx):
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)

            # No item -> show help + current locks
            if not itemname:
                await ctx.reply(
                    "**Inventory Lock**\n"
                    "`!w lock <itemname>` — lock an item so it stays in your inventory when you `!w bank`\n"
                    "`!w lock remove <itemname>` — unlock it\n\n"
                    f"🔒 **Locked items:**\n{self._locked_pretty(p)}"
                )
                return

            # Resolve item using aliases/food first
            canonical = self._resolve_item(itemname) or self._resolve_food(itemname) or itemname.strip()

            # Find the actual inventory key (preserves casing)
            inv_key = self._resolve_from_keys_case_insensitive(canonical, p.inventory.keys())
            if not inv_key:
                # Try also direct (maybe they typed exact inv item like "Super potion (2)")
                inv_key = self._resolve_from_keys_case_insensitive(itemname, p.inventory.keys())

            if not inv_key or int(p.inventory.get(inv_key, 0)) <= 0:
                await ctx.reply("That item isn’t in your inventory, so it can’t be locked.")
                return

            # Prevent duplicates
            if any(self._norm(x) == self._norm(inv_key) for x in (p.locked or [])):
                await ctx.reply(f"🔒 **{inv_key}** is already locked.\n\nLocked items:\n{self._locked_pretty(p)}")
                return

            p.locked = (p.locked or []) + [inv_key]
            await self._persist()

        await ctx.reply(
            f"🔒 Locked **{inv_key}**.\n"
            "It will stay in your inventory when you use `!w bank`.\n\n"
            f"Locked items:\n{self._locked_pretty(p)}"
        )

    @lock_cmd.command(name="remove", aliases=["rm", "del"])
    async def lock_remove_cmd(self, ctx: commands.Context, *, itemname: str):
        if not await self._ensure_ready(ctx):
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)
            locked = getattr(p, "locked", None) or []
            if not locked:
                await ctx.reply("You have no locked items.")
                return

            target_norm = self._norm(itemname)

            # Allow remove by canonical alias match too
            canonical = self._resolve_item(itemname) or self._resolve_food(itemname) or itemname
            canon_norm = self._norm(canonical)

            new_locked = [x for x in locked if self._norm(x) not in (target_norm, canon_norm)]
            if len(new_locked) == len(locked):
                await ctx.reply("That item is not locked.")
                return

            p.locked = new_locked
            await self._persist()

        await ctx.reply(f"✅ Unlocked.\n\n🔒 Locked items:\n{self._locked_pretty(p)}")
    
    @w.group(name="chest", invoke_without_command=True)
    async def chest(self, ctx: commands.Context):
        if not await self._ensure_ready(ctx):
            return
        await ctx.reply("Use !w chest open (requires **Mysterious key** in your inventory).")

    @chest.command(name="open")
    async def chest_open(self, ctx: commands.Context):
        if not await self._ensure_ready(ctx):
            return
        async with self._mem_lock:
            p = self._get_player(ctx.author)
            if p.in_wilderness:
                await ctx.reply("Open chests out of the Wilderness.")
                return
            if p.inventory.get("Mysterious key", 0) < 1:
                await ctx.reply("You need a **Mysterious key** in your inventory.")
                return

            self._remove_item(p.inventory, "Mysterious key", 1)

            lo, hi = self.config["chest_coin_range"]
            coins = random.randint(int(lo), int(hi))
            p.coins += coins

            reward = self._roll_pick_one(self.config.get("chest_rewards", []))
            if reward:
                item, qty = reward
                auto_drops: Dict[str, int] = {}
                dest = self._try_put_item_with_blacklist(p, item, qty, auto_drops)

                result = f"🗝️ Chest loot: **{item} x{qty}** {dest} + **{coins} coins**!"

                if auto_drops:
                    result += "\n🗑️ Auto-dropped (blacklist):"
                    for name, q in sorted(auto_drops.items(), key=lambda x: x[0].lower()):
                        result += f"\n- {name} x{q}"
            else:
                result = f"🗝️ Chest loot: **{coins} coins** (no special reward this time)."

            await self._persist()

        await ctx.reply(result)

    # Shop
    @w.group(name="shop", invoke_without_command=True)
    async def shop(self, ctx: commands.Context):
        if not await self._ensure_ready(ctx):
            return
        await ctx.reply("Use !w shop list or !w shop buy <item>.")

    @shop.command(name="list")
    async def shop_list(self, ctx: commands.Context):
        if not await self._ensure_ready(ctx):
            return
        items = self.config.get("shop_items", {})
        lines = [f"- **{name}** — {int(price):,} coins" for name, price in items.items()]
        await ctx.reply("**Shop:**\n" + "\n".join(lines))

    @shop.command(name="buy")
    async def shop_buy(self, ctx: commands.Context, *args):
        if not await self._ensure_ready(ctx):
            return

        if not args:
            await ctx.reply("Usage: `!w shop buy <item>` or `!w shop buy <qty> <item>`")
            return

        items = self.config.get("shop_items", {}) or {}

        qty = 1
        item_query = ""

        if len(args) >= 2:
            try:
                qty_try = int(args[0])
                if qty_try > 0:
                    qty = qty_try
                    item_query = " ".join(args[1:]).strip()
                else:
                    item_query = " ".join(args).strip()
            except ValueError:
                item_query = " ".join(args).strip()
        else:
            item_query = " ".join(args).strip()

        if not item_query:
            await ctx.reply("Usage: `!w shop buy <item>` or `!w shop buy <qty> <item>`")
            return

        shop_key = None
        for k in items.keys():
            if self._norm(k) == self._norm(item_query):
                shop_key = k
                break
        if not shop_key:
            await ctx.reply("That item isn’t sold here. Use `!w shop list`.")
            return

        price_each = int(items[shop_key])

        async with self._mem_lock:
            p = self._get_player(ctx.author)
            if p.in_wilderness:
                await ctx.reply("Buy items out of the Wilderness.")
                return

            if shop_key in STARTER_ITEMS:
                key = f"starterbuy:{shop_key}"
                ok, left = self._cd_ready(p, key, STARTER_SHOP_COOLDOWN_SEC)
                if not ok:
                    await ctx.reply(f"That starter item is on cooldown: **{left}s** remaining.")
                    return
                if qty != 1:
                    await ctx.reply("Starter items can only be bought **one at a time**.")
                    return

            total_coins = self._total_coins(p)

            if price_each <= 0:
                max_afford = qty
            else:
                max_afford = total_coins // price_each
                if max_afford <= 0:
                    await ctx.reply(
                        f"You need **{price_each:,} coins**, but you only have **{total_coins:,}** "
                        f"(inv {p.coins:,} + bank {p.bank_coins:,})."
                    )
                    return

            want = min(qty, max_afford)

            space = self._inv_free_slots(p.inventory)
            if space <= 0:
                await ctx.reply("No inventory space to buy that.")
                return

            if shop_key in FOOD:
                can_fit = min(space, want)
            elif self._is_stackable(shop_key):
                need = self._slots_needed_to_add(p.inventory, shop_key, want)
                can_fit = want if (need == 0 or space >= need) else 0
            else:
                can_fit = min(space, want)

            if can_fit <= 0:
                await ctx.reply("No inventory space to buy that.")
                return

            total_cost = price_each * can_fit

            if not self._spend_coins(p, total_cost):
                await ctx.reply("You don’t have enough coins.")
                return

            self._add_item(p.inventory, shop_key, can_fit)

            if shop_key in STARTER_ITEMS:
                self._set_cd(p, f"starterbuy:{shop_key}")

            self._touch(p)
            await self._persist()

        if can_fit < qty:
            await ctx.reply(
                f"✅ Bought **{shop_key} x{can_fit}** for **{total_cost:,} coins** "
                f"(limited by coins/space)."
            )
        else:
            await ctx.reply(f"✅ Bought **{shop_key} x{can_fit}** for **{total_cost:,} coins**.")

    @shop.command(name="sell")
    async def shop_sell(self, ctx: commands.Context, *args):
        if not await self._ensure_ready(ctx):
            return

        if not args:
            await ctx.reply("Usage: `!w shop sell <item>` or `!w shop sell <qty> <item>`")
            return

        # Parse: [qty] <item name / alias>
        qty = 1
        item_query = ""

        if len(args) >= 2:
            try:
                qty_try = int(args[0])
                if qty_try > 0:
                    qty = qty_try
                    item_query = " ".join(args[1:]).strip()
                else:
                    item_query = " ".join(args).strip()
            except ValueError:
                item_query = " ".join(args).strip()
        else:
            item_query = " ".join(args).strip()

        if not item_query:
            await ctx.reply("Usage: `!w shop sell <item>` or `!w shop sell <qty> <item>`")
            return

        # Resolve aliases -> canonical item name (e.g. dscim -> Dragon scimitar)
        canonical = self._resolve_item(item_query)
        if not canonical:
            # As a convenience, try matching exact inventory key name (case-insensitive)
            async with self._mem_lock:
                p = self._get_player(ctx.author)
                inv_key_direct = self._resolve_from_keys_case_insensitive(item_query, p.inventory.keys())
            canonical = inv_key_direct

        if not canonical:
            await ctx.reply("Unknown item.")
            return

        # Price source: ITEMS[canonical]["value"]
        meta = ITEMS.get(canonical, {})
        price_each = int(meta.get("value", 0))

        # OPTIONAL fallback: if you haven't migrated an item yet, allow old config sell table
        if price_each <= 0:
            sell_items = self.config.get("shop_sell_items", {}) or {}
            sell_key = None
            for k in sell_items.keys():
                if self._norm(k) == self._norm(canonical) or self._norm(k) == self._norm(item_query):
                    sell_key = k
                    break
            if sell_key:
                price_each = int(sell_items[sell_key])

        if price_each <= 0:
            await ctx.reply("That item has no shop value (can’t be sold).")
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)
            if p.in_wilderness:
                await ctx.reply("Sell items out of the Wilderness.")
                return

            # Find the exact inventory key (preserves original casing)
            inv_key = self._resolve_from_keys_case_insensitive(canonical, p.inventory.keys())
            have = int(p.inventory.get(inv_key, 0)) if inv_key else 0

            if have <= 0:
                await ctx.reply(f"You don’t have **{canonical}** in your inventory.")
                return

            sell_qty = min(int(qty), have)
            if sell_qty <= 0:
                await ctx.reply("Quantity must be > 0.")
                return

            if not self._remove_item(p.inventory, inv_key, sell_qty):
                await ctx.reply("Couldn’t remove that amount from your inventory (weird state).")
                return

            total = price_each * sell_qty
            p.coins += total
            self._touch(p)
            await self._persist()

        if sell_qty < qty:
            await ctx.reply(
                f"💰 Sold **{canonical} x{sell_qty}** for **{total:,} coins** "
                f"(you only had {have})."
            )
        else:
            await ctx.reply(f"💰 Sold **{canonical} x{sell_qty}** for **{total:,} coins**.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Wilderness(bot))
