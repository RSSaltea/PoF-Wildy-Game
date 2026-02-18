# cd "C:\Users\admin\OneDrive\Desktop\paws of fury bot\cogs\wildygame"
# git add .
# git commit -m "change"
# git push


import discord
from discord.ext import commands
import asyncio
import random
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
from .pets import get_all_pets, get_pet_sources, resolve_pet

from .models import (
    PlayerState,
    DuelState,
    JsonStore,
    _now,
    clamp,
)

from .ui_components import (
    FightLogView,
    DuelView,
    NPCInfoView,
    CraftableInfoView,
    BreakdownInfoView,
    BankView,
    InventoryView,
    GroundView,
    KillCountView,
    HighscoresView,
)

from .player_manager import PlayerManager
from .inventory_manager import InventoryManager
from .loot_manager import LootManager
from .combat_manager import CombatManager
from .craft import CraftManager
from .craftable import CRAFTABLES
from .breakdown import BreakdownManager
from .breakdownitems import BREAKDOWNS
from .runecraft import RunecraftManager
from .preset import PresetManager
from .slayer import SlayerManager, SLAYER_SHOP, SLAYER_BLOCK_COST, MAX_SLAYER_BLOCKS
from .npcs import NPC_SLAYER

ALLOWED_CHANNEL_IDS = {1465451116803391529, 1472610522313523323, 1472942650381570171, 1472986472700448768, 1473103361862664338}
TRADE_ONLY_CHANNEL_IDS = {1472986668695814277}
INFO_ONLY_CHANNEL_IDS = {1472997615766343740}
BROADCAST_CHANNEL_ID = 1473373945729126641

TRADE_CHANNEL_CMDS = {"w trade", "w deposit", "w bank", "w inv", "w inventory"}
INFO_CHANNEL_CMDS = {"w stats", "w examine", "w inspect", "w insp", "w npcs", "w bank", "w inv", "w kc", "w killcount", "w highscores", "w hs", "w slayer"}

REVENANT_TYPES = {"revenant", "revenant knight", "revenant demon", "revenant necro", "revenant archon"}

class Wilderness(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.store = JsonStore()
        self.config: Dict[str, Any] = DEFAULT_CONFIG.copy()
        self.players: Dict[int, PlayerState] = {}
        self._ready = False
        self._mem_lock = asyncio.Lock()

        self.duels_by_pair: Dict[frozenset, DuelState] = {}
        self.duels_by_channel: Dict[int, DuelState] = {}

        self._afk_task: Optional[asyncio.Task] = None

        self.ALLOWED_CHANNEL_IDS = ALLOWED_CHANNEL_IDS
        self.TRADE_ONLY_CHANNEL_IDS = TRADE_ONLY_CHANNEL_IDS

        self.player_mgr = PlayerManager(self)
        self.inv_mgr = InventoryManager(self)
        self.loot_mgr = LootManager(self)
        self.combat_mgr = CombatManager(self)
        self.trade_mgr = TradeManager(self, allowed_channel_ids=ALLOWED_CHANNEL_IDS | TRADE_ONLY_CHANNEL_IDS)
        self.craft_mgr = CraftManager(self)
        self.breakdown_mgr = BreakdownManager(self)
        self.rc_mgr = RunecraftManager(self)
        self.preset_mgr = PresetManager(self)
        self.slayer_mgr = SlayerManager(self)


    def _norm(self, s: str) -> str:
        return self.player_mgr.norm(s)

    def _build_item_alias_map(self):
        self.player_mgr.build_item_alias_map()

    def _resolve_item(self, query: str) -> Optional[str]:
        return self.player_mgr.resolve_item(query)

    def _resolve_from_keys_case_insensitive(self, query: str, keys) -> Optional[str]:
        return self.player_mgr.resolve_from_keys_case_insensitive(query, keys)

    def _resolve_food(self, query: str) -> Optional[str]:
        return self.player_mgr.resolve_food(query)

    def _resolve_npc(self, query: str) -> Optional[Dict[str, Any]]:
        return self.player_mgr.resolve_npc(query)

    def _hp_line_pvm(self, your_hp, npc_name, npc_hp, npc_max): return self.combat_mgr.hp_line_pvm(your_hp, npc_name, npc_hp, npc_max)
    def _hp_line_pvp(self, a_name, a_hp, b_name, b_hp): return self.combat_mgr.hp_line_pvp(a_name, a_hp, b_name, b_hp)

    async def cog_load(self):
        self.config = await self.store.load_config()
        raw_players = await self.store.load_players()
        self.players = {}
        for user_id_str, pdata in raw_players.items():
            try:
                self.players[int(user_id_str)] = PlayerState.from_dict(pdata)
            except Exception:
                continue
        self.player_mgr.build_item_alias_map()
        self._ready = True
        if self._afk_task is None or self._afk_task.done():
            self._afk_task = asyncio.create_task(self.combat_mgr.afk_sweeper())

    async def cog_unload(self):
        if self._afk_task and not self._afk_task.done():
            self._afk_task.cancel()

    async def _ensure_ready(self, ctx: commands.Context) -> bool:
        ch = getattr(ctx, "channel", None)
        if ch is None:
            return False

        cmd_name = ctx.command.qualified_name if ctx.command else ""

        if ch.id in TRADE_ONLY_CHANNEL_IDS:
            if cmd_name in TRADE_CHANNEL_CMDS or cmd_name.startswith("w trade"):
                return self._ready or (await ctx.reply("Wilderness is still loading.") and False)
            await ctx.reply("This channel is for **trading, bank & inventory** only.")
            return False

        if ch.id in INFO_ONLY_CHANNEL_IDS:
            if cmd_name in INFO_CHANNEL_CMDS:
                return self._ready or (await ctx.reply("Wilderness is still loading.") and False)
            await ctx.reply("This channel is for **stats, examine, inspect & npcs** only.")
            return False

        if ch.id not in ALLOWED_CHANNEL_IDS:
            return False

        if not self._ready:
            await ctx.reply("Wilderness is still loading. Try again in a moment.")
            return False

        RC_PASSTHROUGH = {"w stats", "w examine", "w inspect", "w insp", "w npcs",
                          "w inv", "w inventory", "w deposit", "w bank", "w hp",
                          "w gear", "w worn", "w pets", "w craftables", "w breakdownitems",
                          "w kc", "w highscores", "w hs", "w slayer", "w alch"}
        if cmd_name not in RC_PASSTHROUGH:
            uid = ctx.author.id
            if uid in self.players:
                busy, left, rune = self.rc_mgr.is_busy(self.players[uid])
                if busy:
                    await ctx.reply(
                        f"You are currently crafting **{rune}**. It will take you **{left}s** to return."
                    )
                    return False

        return True

    async def _persist(self):
        raw = {str(uid): p.to_dict() for uid, p in self.players.items()}
        await self.store.save_players(raw)

    def _get_player(self, user: discord.abc.User) -> PlayerState:
        return self.player_mgr.get_player(user)

    def _touch(self, p: PlayerState):
        self.player_mgr.touch(p)

    def _cd_ready(self, p: PlayerState, key: str, seconds: int) -> Tuple[bool, int]:
        return self.player_mgr.cd_ready(p, key, seconds)

    def _set_cd(self, p: PlayerState, key: str):
        self.player_mgr.set_cd(p, key)

    def _is_stackable(self, item_name): return self.inv_mgr.is_stackable(item_name)
    def _inv_slots_used(self, bag): return self.inv_mgr.inv_slots_used(bag)
    def _inv_free_slots(self, bag): return self.inv_mgr.inv_free_slots(bag)
    def _slots_needed_to_add(self, bag, item, qty): return self.inv_mgr.slots_needed_to_add(bag, item, qty)
    def _add_item(self, bag, item, qty): self.inv_mgr.add_item(bag, item, qty)
    def _remove_item(self, bag, item, qty): return self.inv_mgr.remove_item(bag, item, qty)
    def _player_owns_esspouch(self, p, item): return self.inv_mgr.player_owns_esspouch(p, item)

    def _total_coins(self, p: PlayerState) -> int:
        return self.player_mgr.total_coins(p)

    def _spend_coins(self, p: PlayerState, amount: int) -> bool:
        return self.player_mgr.spend_coins(p, amount)

    def _item_slot(self, item_name): return self.inv_mgr.item_slot(item_name)
    def _is_twohanded(self, item_name): return self.inv_mgr.is_twohanded(item_name)
    def _next_defender_drop(self, p): return self.inv_mgr.next_defender_drop(p)
    def _equipped_bonus(self, p, *, vs_npc, chainmace_charged=None): return self.inv_mgr.equipped_bonus(p, vs_npc=vs_npc, chainmace_charged=chainmace_charged)
    def _consume_buffs_on_hit(self, p): return self.inv_mgr.consume_buffs_on_hit(p)
    def _apply_seeping_heal(self, p, damage_dealt): return self.inv_mgr.apply_seeping_heal(p, damage_dealt)
    def _best_food_in_inventory(self, p): return self.inv_mgr.best_food_in_inventory(p)

    def _band(self, wildy_level): return self.loot_mgr.band(wildy_level)
    def _roll_pick_one(self, entries): return self.loot_mgr.roll_pick_one(entries)
    def _loot_for_level(self, wildy_level): return self.loot_mgr.loot_for_level(wildy_level)
    def _npc_roll_table_for_player(self, p, npc_type, key): return self.loot_mgr.npc_roll_table_for_player(p, npc_type, key)
    def _npc_roll_table(self, npc_type, key): return self.loot_mgr.npc_roll_table(npc_type, key)
    def _npc_roll_pet(self, npc_type): return self.loot_mgr.npc_roll_pet(npc_type)
    def _npc_coin_roll(self, npc_type): return self.loot_mgr.npc_coin_roll(npc_type)


    def _bank_category_for_item(self, item_name): return self.inv_mgr.bank_category_for_item(item_name)
    def _chunk_lines(self, lines, max_chars=950): return self.inv_mgr.chunk_lines(lines, max_chars)
    def _bank_categories_for_user(self, user_id): return self.inv_mgr.bank_categories_for_user(user_id)
    def _bank_embed(self, user, category): return self.inv_mgr.bank_embed(user, category)
    def _inv_categories_for_user(self, user_id): return self.inv_mgr.inv_categories_for_user(user_id)
    def _inv_embed(self, user, category): return self.inv_mgr.inv_embed(user, category)

    def _full_heal(self, p: PlayerState):
        self.player_mgr.full_heal(p)

    def _is_locked(self, p, item_name): return self.inv_mgr.is_locked(p, item_name)
    def _locked_pretty(self, p): return self.inv_mgr.locked_pretty(p)
    def _is_blacklisted(self, p, item_name): return self.inv_mgr.is_blacklisted(p, item_name)
    def _record_autodrop(self, auto_drops, item, qty): self.inv_mgr.record_autodrop(auto_drops, item, qty)
    def _try_put_item_with_blacklist(self, p, item, qty, auto_drops): return self.inv_mgr.try_put_item_with_blacklist(p, item, qty, auto_drops)
    def _try_put_item(self, p, item, qty): return self.inv_mgr.try_put_item(p, item, qty)
    def _try_put_item_or_ground_with_blacklist(self, p, item, qty, auto_drops): return self.inv_mgr.try_put_item_or_ground_with_blacklist(p, item, qty, auto_drops)
    def _try_put_item_or_ground(self, p, item, qty): return self.inv_mgr.try_put_item_or_ground(p, item, qty)
    def _maybe_auto_eat_after_hit(self, p, your_hp): return self.inv_mgr.maybe_auto_eat_after_hit(p, your_hp)
    def _is_noted(self, item_name): return self.inv_mgr.is_noted(item_name)
    def _unnote(self, item_name): return self.inv_mgr.unnote(item_name)
    def _note(self, item_name): return self.inv_mgr.note(item_name)
    def _prune_ground_items(self, p): self.inv_mgr.prune_ground_items(p)
    def _active_ground_items(self, p): return self.inv_mgr.active_ground_items(p)
    def _remove_ground_item(self, p, item, qty): self.inv_mgr.remove_ground_item(p, item, qty)

    def _pair_key(self, a, b): return self.combat_mgr.pair_key(a, b)
    def _duel_active_for_user(self, uid): return self.combat_mgr.duel_active_for_user(uid)
    def _duel_render(self, duel, a, b, pa, pb, ended): return self.combat_mgr.duel_render(duel, a, b, pa, pb, ended)
    def _pvp_transfer_all_items(self, winner, loser): return self.combat_mgr.pvp_transfer_all_items(winner, loser)
    def _food_summary_lines(self, eaten, inv): return self.combat_mgr.food_summary_lines(eaten, inv)
    def _format_items_short(self, items, max_lines=12): return self.combat_mgr.format_items_short(items, max_lines)
    def _fmt_entry(self, e): return self.combat_mgr.fmt_entry(e)
    def _npc_info_embed(self, npc_name, guild): return self.combat_mgr.npc_info_embed(npc_name, guild)

    def _craftable_info_embed(self, craft_name: str) -> discord.Embed:
        from .items import ITEM_EFFECTS
        recipe = CRAFTABLES.get(craft_name, {})
        stats = ITEMS.get(craft_name, {})
        desc = recipe.get("description", "")
        materials = recipe.get("materials", {})

        emb = discord.Embed(title=f"\U0001f528 Craftable: {craft_name}")
        if desc:
            emb.description = f"*{desc}*"

        stat_lines = []
        if stats.get("type"):
            stat_lines.append(f"Slot: **{stats['type']}**")
        if stats.get("atk"):
            stat_lines.append(f"ATK: **{stats['atk']}**")
        if stats.get("atk_vs_npc"):
            stat_lines.append(f"ATK vs NPC: **{stats['atk_vs_npc']}**")
        if stats.get("def"):
            stat_lines.append(f"DEF: **{stats['def']}**")
        if stats.get("value"):
            stat_lines.append(f"Value: **{stats['value']:,}** coins")
        if stat_lines:
            emb.add_field(name="Stats", value="\n".join(stat_lines), inline=True)

        effect_data = ITEM_EFFECTS.get(craft_name)
        if effect_data:
            emb.add_field(name="Effect", value=effect_data["effect"], inline=True)

        mat_lines = [f"**{mat}** x{qty:,}" for mat, qty in materials.items()]
        emb.add_field(name="Materials", value="\n".join(mat_lines) if mat_lines else "(none)", inline=False)

        return emb

    def _breakdown_info_embed(self, item_name: str) -> discord.Embed:
        from .items import ITEM_EFFECTS
        info = BREAKDOWNS.get(item_name, {})
        stats = ITEMS.get(item_name, {})
        desc = info.get("description", "")
        results = info.get("result", {})

        emb = discord.Embed(title=f"\U0001f4a5 Breakdown: {item_name}")
        if desc:
            emb.description = f"*{desc}*"

        stat_lines = []
        if stats.get("type"):
            stat_lines.append(f"Slot: **{stats['type']}**")
        if stats.get("atk"):
            stat_lines.append(f"ATK: **{stats['atk']}**")
        if stats.get("atk_vs_npc"):
            stat_lines.append(f"ATK vs NPC: **{stats['atk_vs_npc']}**")
        if stats.get("def"):
            stat_lines.append(f"DEF: **{stats['def']}**")
        if stats.get("value"):
            stat_lines.append(f"Value: **{stats['value']:,}** coins")
        if stat_lines:
            emb.add_field(name="Item Stats", value="\n".join(stat_lines), inline=True)

        effect_data = ITEM_EFFECTS.get(item_name)
        if effect_data:
            emb.add_field(name="Effect", value=effect_data["effect"], inline=True)

        result_lines = [f"**{mat}** x{qty:,}" for mat, qty in results.items()]
        emb.add_field(name="You Receive", value="\n".join(result_lines) if result_lines else "(none)", inline=False)

        return emb

    async def _afk_sweeper(self):
        await self.combat_mgr.afk_sweeper()

    async def _duel_action(self, interaction: discord.Interaction, duel: DuelState, action: str):
        await self.combat_mgr.duel_action(interaction, duel, action)

    def _build_pages(self, lines, per_page=10): return self.combat_mgr.build_pages(lines, per_page)
    def _simulate_pvm_fight_and_loot(self, p, chosen_npc, *, header_lines=None): return self.combat_mgr.simulate_pvm_fight_and_loot(p, chosen_npc, header_lines=header_lines)

    def _highscores_embed(self, category: str, guild: Optional[discord.Guild]) -> discord.Embed:
        CATS = {
            "kills": ("⚔️ Highscores — Kills", lambda p: int(p.kills), lambda uid, v: f"{v:,} kills"),
            "deaths": ("💀 Highscores — Deaths", lambda p: int(p.deaths), lambda uid, v: f"{v:,} deaths"),
            "coins": ("💰 Highscores — Wealth", lambda p: int(p.coins) + int(p.bank_coins), lambda uid, v: f"{v:,} coins"),
            "slayer": ("🗡️ Highscores — Slayer", lambda p: int(p.slayer_xp or 0),
                       lambda uid, v: f"Level {self.slayer_mgr.level_for_xp(v)} ({v:,} XP)"),
            "unique": ("✨ Highscores — Unique Drops", lambda p: int(p.unique_drops), lambda uid, v: f"{v:,} uniques"),
            "pets": ("🐾 Highscores — Pets", lambda p: len(getattr(p, "pets", []) or []), lambda uid, v: f"{v} pets"),
            "tasks": ("🗡️ Highscores — Slayer Tasks", lambda p: int(p.slayer_tasks_done or 0), lambda uid, v: f"{v:,} tasks"),
        }

        if category == "overall":
            # Rank by total actions, show top 5 with all stats
            scored = []
            for uid, p in self.players.items():
                total = int(p.kills) + int(p.deaths) + int(p.escapes)
                if total > 0:
                    scored.append((uid, total, p))
            scored.sort(key=lambda x: x[1], reverse=True)
            top = scored[:5]

            emb = discord.Embed(title="🏆 Highscores — Overall", color=0xFFD700)
            if not top:
                emb.description = "No data to display."
                return emb

            for rank, (uid, total, p) in enumerate(top, 1):
                member = guild.get_member(uid) if guild else None
                name = member.display_name if member else f"User#{uid}"
                medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"**{rank}.**")
                slayer_lvl = self.slayer_mgr.level_for_xp(int(p.slayer_xp or 0))
                slayer_xp = int(p.slayer_xp or 0)
                wealth = int(p.coins) + int(p.bank_coins)
                pets = len(getattr(p, "pets", []) or [])
                lines = (
                    f"⚔️ {int(p.kills):,} kills · 💀 {int(p.deaths):,} deaths\n"
                    f"💰 {wealth:,} coins · ✨ {int(p.unique_drops):,} uniques\n"
                    f"🗡️ Slayer Level {slayer_lvl} ({slayer_xp:,} XP) · {int(p.slayer_tasks_done or 0):,} tasks\n"
                    f"🐾 {pets} pets"
                )
                emb.add_field(name=f"{medal} {name}", value=lines, inline=False)
            return emb

        title, score_fn, fmt_fn = CATS.get(category, CATS["kills"])

        scored = []
        for uid, p in self.players.items():
            score = score_fn(p)
            if score > 0:
                scored.append((uid, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        top = scored[:50]

        emb = discord.Embed(title=title, color=0xFFD700)
        if not top:
            emb.description = "No data to display."
            return emb

        lines = []
        for rank, (uid, score) in enumerate(top, 1):
            member = guild.get_member(uid) if guild else None
            name = member.display_name if member else f"User#{uid}"
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"**{rank}.**")
            lines.append(f"{medal} {name} — {fmt_fn(uid, score)}")
        emb.description = "\n".join(lines)
        return emb

    async def _send_broadcasts(self, user: discord.abc.User, broadcasts: List):
        if not broadcasts:
            return
        ch = self.bot.get_channel(BROADCAST_CHANNEL_ID)
        if not ch:
            return
        for drop_type, item_name, npc_name in broadcasts:
            if drop_type == "Unique":
                emoji = "✨"
                colour = discord.Colour.gold()
            elif drop_type == "Special":
                emoji = "🩸"
                colour = discord.Colour.red()
            else:
                emoji = "🐾"
                colour = discord.Colour.purple()
            emb = discord.Embed(
                title=f"{emoji} {drop_type} Drop!",
                description=(
                    f"{user.mention} got a **{drop_type}** drop!\n"
                    f"They received **{item_name}** from **{npc_name}**!"
                ),
                colour=colour,
            )
            try:
                await ch.send(embed=emb)
            except Exception:
                pass

    @commands.group(name="w", invoke_without_command=True)
    async def w(self, ctx: commands.Context):
        if not await self._ensure_ready(ctx):
            return
        emb = discord.Embed(title="Wilderness Commands")
        emb.add_field(name="Getting Started", value=(
            "`!w start` — Create your profile\n"
            "`!w reset` — Wipe your profile and start over"
        ), inline=False)
        emb.add_field(name="Combat & Exploring", value=(
            "`!w venture <level>` — Enter the Wilderness\n"
            "`!w fight <npc>` — Fight an NPC\n"
            "`!w attack @player` — Attack another player\n"
            "`!w tele` — Teleport out\n"
            "`!w eat [qty] [food]` — Eat food to heal\n"
            "`!w drink <potion>` — Drink a potion"
        ), inline=False)
        emb.add_field(name="Equipment & Inventory", value=(
            "`!w equip <item>` — Equip an item\n"
            "`!w unequip <slot>` — Unequip a slot (or `all`)\n"
            "`!w gear` — View equipped gear\n"
            "`!w inv` — View your inventory\n"
            "`!w drop <qty> <item>` — Drop items\n"
            "`!w ground` — View ground items\n"
            "`!w ground pickup [qty] <item>` — Pick up"
        ), inline=False)
        emb.add_field(name="Banking", value=(
            "`!w deposit` — Deposit inventory to bank\n"
            "`!w deposit all` — Deposit everything\n"
            "`!w bank` — View your bank\n"
            "`!w withdraw [qty] <item> [noted]` — Withdraw"
        ), inline=False)
        emb.add_field(name="Info & Stats", value=(
            "`!w hp` — Check your HP\n"
            "`!w stats [@player]` — View profile\n"
            "`!w kc [npc]` — View kill counts\n"
            "`!w inspect <item>` — Inspect an item\n"
            "`!w examine @player` — Inspect player gear\n"
            "`!w npcs` — Browse NPC info\n"
            "`!w pets` — View your pets"
        ), inline=False)
        emb.add_field(name="Crafting & Resources", value=(
            "`!w craft <item>` — Craft an item\n"
            "`!w craftables` — Browse craftable items\n"
            "`!w breakdown <item>` — Break down an item\n"
            "`!w breakdownitems` — Browse breakdowns\n"
            "`!w rc <rune>` — Craft runes\n"
            "`!w alch <item>` — High alch an item\n"
            "`!w alch auto <item>` — Toggle auto-alch on drops"
        ), inline=False)
        emb.add_field(name="Slayer", value=(
            "`!w slayer` — View slayer level and info\n"
            "`!w slayer task` — View or get a slayer task\n"
            "`!w slayer skip` — Skip task (30 points)\n"
            "`!w slayer npcs` — List slayer NPCs\n"
            "`!w slayer shop` — View slayer shop\n"
            "`!w slayer buy <item>` — Buy from slayer shop\n"
            "`!w slayer block [npc]` — View or block an NPC\n"
            "`!w slayer block remove <npc>` — Unblock"
        ), inline=False)
        emb.add_field(name="Trading & Shop", value=(
            "`!w trade @player` — Start a trade\n"
            "`!w trade accept` — Accept a trade\n"
            "`!w shop list` — View the shop\n"
            "`!w shop buy [qty] <item>` — Buy\n"
            "`!w shop sell [qty] <item>` — Sell\n"
            "`!w chest open mysterious` — Open with a Mysterious key\n"
            "`!w chest open bone` — Open with a Bone key"
        ), inline=False)
        emb.add_field(name="Presets & Settings", value=(
            "`!w preset create <name>` — Save / override preset\n"
            "`!w preset load <name>` — Load preset\n"
            "`!w preset delete <name>` — Delete preset\n"
            "`!w preset check <name>` — Inspect preset\n"
            "`!w presets` — List your presets\n"
            "`!w lock <item>` — Lock from deposit\n"
            "`!w lock remove <item>` — Unlock\n"
            "`!w blacklist` — View blacklist\n"
            "`!w blacklist remove <item>` — Remove\n"
            "`!w blacklist clear` — Clear blacklist"
        ), inline=False)
        await ctx.reply(embed=emb)

    @w.group(name="trade", invoke_without_command=True)
    async def trade_cmd(self, ctx: commands.Context, target: Optional[discord.Member] = None):
        if not await self._ensure_ready(ctx):
            return

        if target is None:
            await ctx.reply(
                "Usage:\n"
                "`!w trade @player` (request)\n"
                "`!w trade accept`\n"
                "`!w trade add <quantity> <item>`\n"
                "`!w trade remove <quantity> <item>`\n"
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

        emb = self._npc_info_embed(NPCS[0]["name"], ctx.guild)
        view = NPCInfoView(self, author_id=ctx.author.id)
        await ctx.reply(embed=emb, view=view)

    @w.command(name="eat")
    async def eat_cmd(self, ctx: commands.Context, *args):
        if not await self._ensure_ready(ctx):
            return

        if self._duel_active_for_user(ctx.author.id):
            await ctx.reply("You're in a PvP fight — use the **Eat** button on your turn.")
            return

        qty = 1
        food_query = ""
        auto_best = False

        if not args:
            # No args -> auto-eat best food x1
            auto_best = True
        elif len(args) == 1:
            # Single arg: could be qty (number) or food name
            try:
                q = int(args[0])
                if q > 0:
                    qty = q
                    auto_best = True
                else:
                    food_query = args[0].strip()
            except ValueError:
                food_query = args[0].strip()
        else:
            # 2+ args: try [qty] <food name>
            try:
                q = int(args[0])
                if q > 0:
                    qty = q
                    food_query = " ".join(args[1:]).strip()
                else:
                    food_query = " ".join(args).strip()
            except ValueError:
                food_query = " ".join(args).strip()

        food_key = None
        if auto_best:
            # Find best food in inventory (highest heal)
            async with self._mem_lock:
                p = self._get_player(ctx.author)
                best_heal = 0
                for item_name, item_qty in p.inventory.items():
                    if item_qty <= 0:
                        continue
                    if item_name in FOOD:
                        h = int(FOOD[item_name].get("heal", 0))
                        if h > best_heal:
                            best_heal = h
                            food_key = item_name
            if not food_key:
                await ctx.reply("You don't have any food in your inventory.")
                return
        else:
            food_key = self._resolve_food(food_query)
            if not food_key:
                await ctx.reply("Unknown food. Example: `!w eat lobster` or `!w eat 3 shark`.")
                return

        heal = int(FOOD[food_key].get("heal", 0))
        if heal <= 0:
            await ctx.reply("That food has no heal value.")
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)

            have = int(p.inventory.get(food_key, 0))
            if have <= 0:
                await ctx.reply(f"You don't have **{food_key}** in your inventory.")
                return

            eat_qty = min(int(qty), have)
            if eat_qty <= 0:
                await ctx.reply("Quantity must be > 0.")
                return

            max_hp = int(self.config["max_hp"])
            before_hp = int(p.hp)

            # Eat multiple, but stop once full HP or you run out
            actually_ate = 0
            while actually_ate < eat_qty and p.hp < max_hp and int(p.inventory.get(food_key, 0)) > 0:
                if not self._remove_item(p.inventory, food_key, 1):
                    break
                actually_ate += 1
                p.hp = clamp(int(p.hp) + heal, 0, max_hp)

            if actually_ate <= 0:
                await ctx.reply(f"❤️ You're already full HP (**{p.hp}/{max_hp}**).")
                return

            self._touch(p)
            await self._persist()

        healed_total = int(p.hp) - before_hp
        left = int(p.inventory.get(food_key, 0))
        await ctx.reply(
            f"🍖 You eat **{food_key} x{actually_ate}** and heal **{healed_total}**. "
            f"HP: **{p.hp}/{self.config['max_hp']}** (left: **{left}**)."
        )

    @w.command(name="drop")
    async def drop_cmd(self, ctx: commands.Context, *args):
        if not await self._ensure_ready(ctx):
            return

        if self._duel_active_for_user(ctx.author.id):
            await ctx.reply("You’re in a PvP fight — finish the fight before dropping items.")
            return

        if not args:
            await ctx.reply("Usage: `!w drop <item>` or `!w drop <qty> <item>`")
            return

        qty: Optional[int] = None
        item_query: str = ""

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
            await ctx.reply("Usage: `!w drop <item>` or `!w drop <qty> <item>`")
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)
            inv_key = self._resolve_from_keys_case_insensitive(item_query, p.inventory.keys())
            if not inv_key:
                maybe = self._resolve_item(item_query) or self._resolve_food(item_query)
                if maybe:
                    inv_key = self._resolve_from_keys_case_insensitive(maybe, p.inventory.keys())

            if not inv_key:
                await ctx.reply("That item isn’t in your inventory.")
                return

            have = int(p.inventory.get(inv_key, 0))
            if have <= 0:
                await ctx.reply("That item isn’t in your inventory.")
                return

            drop_qty = have if qty is None else min(int(qty), have)
            if drop_qty <= 0:
                await ctx.reply("Quantity must be > 0.")
                return

            ok = self._remove_item(p.inventory, inv_key, drop_qty)
            if not ok:
                await ctx.reply("Couldn't drop that amount (weird state).")
                return

            # Place on ground if in wilderness
            dropped_to_ground = p.in_wilderness
            if dropped_to_ground:
                p.ground_items.append([inv_key, drop_qty, _now()])

            self._touch(p)
            await self._persist()

        if dropped_to_ground:
            if drop_qty == have:
                await ctx.reply(f"🫳 Dropped **{inv_key} x{drop_qty}** on the ground. Pick up with `!w ground`.")
            else:
                await ctx.reply(f"🫳 Dropped **{inv_key} x{drop_qty}** on the ground. You have **{have - drop_qty}** left.")
        else:
            if drop_qty == have:
                await ctx.reply(f"🗑️ Dropped **{inv_key} x{drop_qty}** from your inventory.")
            else:
                await ctx.reply(f"🗑️ Dropped **{inv_key} x{drop_qty}**. You have **{have - drop_qty}** left.")

    @w.group(name="ground", invoke_without_command=True)
    async def ground_cmd(self, ctx: commands.Context):
        if not await self._ensure_ready(ctx):
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)

            if not p.in_wilderness:
                await ctx.reply("You're not in the Wilderness.")
                return

            ground = self._active_ground_items(p)
            await self._persist()

        if not ground:
            await ctx.reply("🫳 Nothing on the ground.")
            return

        lines = ["🫳 **On ground (5 min):**"]
        for name, qty in sorted(ground.items(), key=lambda x: x[0].lower()):
            lines.append(f"- **{name} x{qty}**")

        view = GroundView(cog=self, author_id=ctx.author.id, ground=ground)
        await ctx.reply("\n".join(lines), view=view)

    @ground_cmd.command(name="pickup", aliases=["pick"])
    async def ground_pickup_cmd(self, ctx: commands.Context, *args):
        if not await self._ensure_ready(ctx):
            return

        if not args:
            await ctx.reply("Usage: `!w ground pickup <item>` or `!w ground pickup <qty> <item>`")
            return

        qty: Optional[int] = None
        item_query: str = ""

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
            await ctx.reply("Usage: `!w ground pickup <item>` or `!w ground pickup <qty> <item>`")
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)

            if not p.in_wilderness:
                await ctx.reply("You're not in the Wilderness.")
                return

            ground = self._active_ground_items(p)
            if not ground:
                await ctx.reply("🫳 Nothing on the ground.")
                return

            # Resolve item name from ground keys
            inv_key = self._resolve_from_keys_case_insensitive(item_query, ground.keys())
            if not inv_key:
                maybe = self._resolve_item(item_query) or self._resolve_food(item_query)
                if maybe:
                    inv_key = self._resolve_from_keys_case_insensitive(maybe, ground.keys())

            if not inv_key:
                await ctx.reply("That item isn't on the ground.")
                return

            available = ground.get(inv_key, 0)
            if available <= 0:
                await ctx.reply("That item isn't on the ground.")
                return

            pick_qty = available if qty is None else min(int(qty), available)
            if pick_qty <= 0:
                await ctx.reply("Quantity must be > 0.")
                return

            free = self._inv_free_slots(p.inventory)
            is_stack = self._is_stackable(inv_key) and inv_key not in FOOD
            if is_stack:
                # Stackables use 1 slot (or 0 if already in inv) — pick up all
                if p.inventory.get(inv_key, 0) > 0:
                    take = pick_qty
                elif free >= 1:
                    take = pick_qty
                else:
                    take = 0
            else:
                take = min(pick_qty, free)

            if take <= 0:
                await ctx.reply(
                    f"No inventory space. You have **{free}** free slot(s)."
                )
                return

            self._add_item(p.inventory, inv_key, take)
            self._remove_ground_item(p, inv_key, take)
            self._touch(p)
            await self._persist()

        remaining = available - take
        if remaining <= 0:
            await ctx.reply(f"🫳 Picked up **{inv_key} x{take}** from the ground.")
        else:
            await ctx.reply(f"🫳 Picked up **{inv_key} x{take}**. **{remaining}** still on the ground.")

    @w.command(name="inspect", aliases=["insp"])
    async def inspect(self, ctx: commands.Context, *, itemname: str):
        if not await self._ensure_ready(ctx):
            return
        raw = itemname.strip()

        food_key = self._resolve_food(raw)
        if food_key:
            food_meta = FOOD[food_key]
            heal = int(food_meta.get("heal", 0))
            emb = discord.Embed(title=f"\U0001f356 {food_key}", color=0x3fb950)
            emb.add_field(name="Heals", value=f"**{heal} HP**", inline=True)
            await ctx.reply(embed=emb)
            return

        item_key = self._resolve_item(raw)
        meta = ITEMS.get(item_key) if item_key else None
        if meta and self._item_slot(item_key):
            slot = self._item_slot(item_key)
            atk = int(meta.get("atk", 0))
            deff = int(meta.get("def", 0))
            atk_vs_npc = int(meta.get("atk_vs_npc", 0))
            sell_value = int(meta.get("value", 0))
            is_2h = self._is_twohanded(item_key)

            slot_display = "Two-handed" if is_2h else slot.capitalize()
            emb = discord.Embed(title=f"\U0001f9e9 {item_key}", color=0x58a6ff)
            emb.add_field(name="Slot", value=slot_display, inline=True)

            stat_text = f"+{atk} atk / +{deff} def"
            if atk_vs_npc:
                stat_text += f"\n+{atk_vs_npc} atk vs NPCs"
            emb.add_field(name="Stats", value=stat_text, inline=True)

            if sell_value > 0:
                emb.add_field(name="Value", value=f"{sell_value:,} coins", inline=True)

            effect = (self.config.get("item_effects", {}) or {}).get(item_key, {}).get("effect")
            if effect:
                emb.add_field(name="Effect", value=effect, inline=False)

            image_url = meta.get("image")
            if image_url:
                emb.set_thumbnail(url=image_url)

            await ctx.reply(embed=emb)
            return

        if item_key and meta:
            emb = discord.Embed(title=f"\U0001f4e6 {item_key}", color=0xd29922)
            stackable = bool(meta.get("stackable", False))
            emb.add_field(name="Stackable", value="Yes" if stackable else "No", inline=True)
            sell_value = int(meta.get("value", 0))
            if sell_value > 0:
                emb.add_field(name="Value", value=f"{sell_value:,} coins", inline=True)
            effect = (self.config.get("item_effects", {}) or {}).get(item_key, {}).get("effect")
            if effect:
                emb.add_field(name="Effect", value=effect, inline=False)
            image_url = meta.get("image")
            if image_url:
                emb.set_thumbnail(url=image_url)
            await ctx.reply(embed=emb)
            return

        effects = (self.config.get("item_effects", {}) or {})
        effect_key = None
        for k in effects.keys():
            if self._norm(k) == self._norm(raw):
                effect_key = k
                break
        if effect_key:
            emb = discord.Embed(title=f"\u2728 {effect_key}", color=0xbc8cff)
            emb.add_field(name="Effect", value=effects[effect_key].get("effect", ""), inline=False)
            ek_meta = ITEMS.get(effect_key, {})
            image_url = ek_meta.get("image")
            if image_url:
                emb.set_thumbnail(url=image_url)
            await ctx.reply(embed=emb)
            return

        await ctx.reply(f"**{raw}**\nThis item has no use currently.")

    @w.command(name="examine", aliases=["look", "inspectplayer"])
    async def examine_cmd(self, ctx: commands.Context, *, target: Optional[str] = None):
        """Show a player's equipped gear."""
        if not await self._ensure_ready(ctx):
            return

        if not target:
            await ctx.reply("Usage: `!w examine <playername or @mention>`")
            return

        member = None

        if ctx.message.mentions:
            member = ctx.message.mentions[0]

        elif target.isdigit():
            uid = int(target)
            if ctx.guild:
                member = ctx.guild.get_member(uid)

        if not member and ctx.guild:
            search = target.lower().strip()
            for m in ctx.guild.members:
                if m.display_name.lower() == search or m.name.lower() == search:
                    member = m
                    break

        if not member:
            await ctx.reply("Player not found.")
            return

        if member.id not in self.players:
            await ctx.reply("That player has not entered the Wilderness yet.")
            return

        p = self.players[member.id]
        gear = getattr(p, "equipment", None) or {}

        if not gear:
            await ctx.reply(f"🧍 **{member.display_name}** has no gear equipped.")
            return

        slot_order = [
            "helm", "cape", "amulet",
            "body", "legs",
           "gloves", "boots",
            "ring",
            "mainhand", "offhand",
        ]

        lines = []
        used = set()

        for slot in slot_order:
            if slot in gear and gear[slot]:
                lines.append(f"• **{slot}**: {gear[slot]}")
                used.add(slot)

        for slot, item in sorted(gear.items(), key=lambda kv: kv[0]):
            if slot in used:
                continue
            if item:
                lines.append(f"• **{slot}**: {item}")

        emb = discord.Embed(
            title=f"🕵️ Examine: {member.display_name}",
            description="\n".join(lines),
        )
        if member.display_avatar:
            emb.set_thumbnail(url=member.display_avatar.url)

        await ctx.reply(embed=emb)

    @w.command(name="pets", aliases=["pet"])
    async def pets_cmd(self, ctx: commands.Context, *, pet: Optional[str] = None):
        """View your pets or look up a specific pet by name."""
        if not await self._ensure_ready(ctx):
            return

        p = self._get_player(ctx.author)

        owned = list(getattr(p, "pets", None) or [])
        owned_norm = {self._norm(x) for x in owned}

        all_pets = get_all_pets()
        pet_sources = get_pet_sources()

        if pet:
            canonical = resolve_pet(pet)
            if not canonical:
                await ctx.reply("Unknown pet. Try `!w pets` to see your pets.")
                return

            is_owned = (self._norm(canonical) in owned_norm)

            src_lines = []
            for npc_type, chance in pet_sources.get(canonical, []):
                src_lines.append(f"• **{npc_type}** — `{chance}`")

            emb = discord.Embed(
                title=f"🐾 Pet: {canonical}",
                description=("✅ You own this pet." if is_owned else "❌ You don’t own this pet."),
            )

            emb.add_field(name="Owned", value="✅ Yes" if is_owned else "❌ No", inline=True)
            emb.add_field(name="Your total pets", value=str(len(owned)), inline=True)

            emb.add_field(
                name="Drops from",
                value="\n".join(src_lines) if src_lines else "(unknown)",
                inline=False,
            )

            await ctx.reply(embed=emb)
            return

        emb = discord.Embed(
            title=f"🐾 {ctx.author.display_name}'s Pets",
            description=f"Owned: **{len(owned)} / {len(all_pets)}**",
        )

        if not owned:
            emb.add_field(name="Pets", value="(none)", inline=False)
            await ctx.reply(embed=emb)
            return

        owned_sorted = sorted(owned, key=lambda s: s.lower())
        lines = [f"• {x}" for x in owned_sorted]
        chunks = self._chunk_lines(lines, max_chars=950)

        if len(chunks) == 1:
            emb.add_field(name="Pets", value=chunks[0], inline=False)
        else:
            for i, ch in enumerate(chunks, start=1):
                emb.add_field(name=f"Pets ({i}/{len(chunks)})", value=ch, inline=False)

        await ctx.reply(embed=emb)

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

    @w.command(name="gear", aliases=["worn"])
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

            # Block equipping an offhand if a 2h weapon is in mainhand
            if slot == "offhand":
                mh = p.equipment.get("mainhand")
                if mh and self._is_twohanded(mh):
                    await ctx.reply(
                        f"You can't equip an offhand while wielding **{mh}** (two-handed). "
                        f"Unequip your mainhand first."
                    )
                    return

            # Style compatibility check for mainhand/offhand
            new_style = ITEMS.get(item_key, {}).get("style")
            if new_style and new_style != "all" and slot in ("mainhand", "offhand"):
                other_slot = "offhand" if slot == "mainhand" else "mainhand"
                other_item = p.equipment.get(other_slot)
                if other_item:
                    other_style = ITEMS.get(other_item, {}).get("style")
                    if other_style and other_style != "all" and other_style != new_style:
                        await ctx.reply(
                            f"You can't equip **{item_key}** ({new_style}) with **{other_item}** ({other_style}). "
                            f"Unequip your {other_slot} first or use a matching style."
                        )
                        return

            # Work out how many free slots we need for the swap
            is_2h = self._is_twohanded(item_key)
            old_mh = p.equipment.get(slot)          # item currently in the target slot
            old_oh = p.equipment.get("offhand") if is_2h else None  # offhand to clear for 2h
            slots_needed = (1 if old_mh else 0) + (1 if old_oh else 0)

            if slots_needed > 0 and self._inv_free_slots(p.inventory) < slots_needed:
                await ctx.reply(f"No inventory space to swap gear (need **{slots_needed}** free slot(s)).")
                return

            # Return old items to inventory
            removed_extra = None
            if old_mh:
                self._add_item(p.inventory, old_mh, 1)
            if old_oh:
                self._add_item(p.inventory, old_oh, 1)
                p.equipment.pop("offhand", None)
                removed_extra = old_oh

            # Take the new item from inventory or bank
            if p.in_wilderness:
                self._remove_item(p.inventory, inv_key, 1)
            else:
                if has_in_inv:
                    self._remove_item(p.inventory, inv_key, 1)
                else:
                    self._remove_item(p.bank, bank_key, 1)

            p.equipment[slot] = item_key
            await self._persist()

        msg = f"✅ Equipped **{item_key}** in slot **{slot}**."
        if removed_extra:
            msg += f"\n↩️ **{removed_extra}** was unequipped from your offhand."
        await ctx.reply(msg)

    @w.command(name="unequip")
    async def unequip(self, ctx: commands.Context, slot: str):
        if not await self._ensure_ready(ctx):
            return
        slot = slot.strip().lower()

        if slot == "all":
            async with self._mem_lock:
                p = self._get_player(ctx.author)
                if not p.equipment:
                    await ctx.reply("You have nothing equipped.")
                    return

                equipped_count = len(p.equipment)
                free = self._inv_free_slots(p.inventory)
                if free < equipped_count:
                    await ctx.reply(f"Not enough inventory space. You need **{equipped_count}** free slot(s), you have **{free}**.")
                    return

                removed = []
                for s, item in list(p.equipment.items()):
                    self._add_item(p.inventory, item, 1)
                    removed.append(f"**{item}** ({s})")
                p.equipment.clear()
                await self._persist()

            await ctx.reply(f"✅ Unequipped all: {', '.join(removed)}.")
            return

        if slot not in EQUIP_SLOT_SET:
            await ctx.reply(f"Unknown slot. Slots: {', '.join(sorted(EQUIP_SLOT_SET))}, all")
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

    @w.command(name="inv", aliases=["inventory"])
    async def inv(self, ctx: commands.Context):
        if not await self._ensure_ready(ctx):
            return

        p = self._get_player(ctx.author)
        has_any = bool(p.inventory) or bool(p.coins)
        if not has_any:
            await ctx.reply("Your inventory is empty.")
            return

        start_category = "All"
        emb = self._inv_embed(ctx.author, start_category)
        view = InventoryView(self, author_id=ctx.author.id, current_category=start_category)
        await ctx.reply(embed=emb, view=view)

    @w.command(name="bank", aliases=["bankview"])
    async def bank_view_cmd(self, ctx: commands.Context):
        if not await self._ensure_ready(ctx):
            return

        p = self._get_player(ctx.author)
        has_any = bool(p.bank) or bool(p.bank_coins)
        if not has_any:
            await ctx.reply("Your bank is empty.")
            return

        start_category = "All"
        emb = self._bank_embed(ctx.author, start_category)
        view = BankView(self, author_id=ctx.author.id, current_category=start_category)
        await ctx.reply(embed=emb, view=view)

    @w.command(name="deposit", aliases=["depo"])
    async def deposit_cmd(self, ctx: commands.Context, *, args: str = ""):
        if not await self._ensure_ready(ctx):
            return

        bank_all = args.strip().lower() == "all"

        async with self._mem_lock:
            p = self._get_player(ctx.author)

            ok, left = self._cd_ready(p, "bank", int(self.config["bank_cooldown_sec"]))
            if not ok:
                await ctx.reply(f"Bank cooldown: **{left}s**")
                return

            if p.in_wilderness:
                await ctx.reply("You can't deposit in the Wilderness. !w tele out first.")
                return

            banked_items: Dict[str, int] = {}
            banked_equip: Dict[str, str] = {}
            kept_locked: Dict[str, int] = {}
            banked_coins = int(p.coins)

            # Move inventory items — skip locked unless bank_all
            for item, qty in list(p.inventory.items()):
                if qty <= 0:
                    continue

                if not bank_all and self._is_locked(p, item):
                    kept_locked[item] = qty
                    continue

                # Normal banking — noted items become unnoted in bank
                bank_name = self._unnote(item) if self._is_noted(item) else item
                self._add_item(p.bank, bank_name, qty)
                banked_items[item] = qty
                p.inventory.pop(item, None)

            # Bank equipped gear if bank_all
            if bank_all:
                for slot, item in list(p.equipment.items()):
                    if item:
                        self._add_item(p.bank, item, 1)
                        banked_equip[slot] = item
                p.equipment.clear()

            # Bank coins
            if p.coins > 0:
                p.bank_coins += p.coins
                p.coins = 0

            self._set_cd(p, "bank")
            await self._persist()

        lines = []

        if banked_items:
            lines.append("📦 **Banked items:**")
            lines.append(self._format_items_short(banked_items, max_lines=18))
        else:
            lines.append("📦 **Banked items:** (none)")
        if banked_equip:
            equip_str = ", ".join(f"**{item}** ({slot})" for slot, item in banked_equip.items())
            lines.append(f"🛡️ **Banked equipment:** {equip_str}")
        if banked_coins > 0:
            lines.append(f"🪙 **Banked coins:** {banked_coins:,}")

        if not bank_all:
            lines.append("(Equipped gear unchanged.)")

        await ctx.reply("\n".join(lines))

    @w.command(name="withdraw", aliases=["withdra"])
    async def withdraw(self, ctx: commands.Context, *args):
        if not await self._ensure_ready(ctx):
            return

        if not args:
            await ctx.reply("Usage: `!w withdraw <item>` or `!w withdraw <qty> <item> [noted]`")
            return

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

        want_noted = False
        if item_query.lower().endswith(" noted"):
            want_noted = True
            item_query = item_query[:-6].strip()

        if not item_query:
            await ctx.reply("Usage: `!w withdraw <item>` or `!w withdraw <qty> <item> [noted]`")
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)
            if p.in_wilderness:
                await ctx.reply("Withdraw items out of the Wilderness. !w tele first.")
                return
            
            # Find item in bank (case-insensitive), supporting aliases
            bank_key = self._resolve_from_keys_case_insensitive(item_query, p.bank.keys())
            if not bank_key:
                maybe_canonical = self._resolve_item(item_query)
                if maybe_canonical:
                    bank_key = self._resolve_from_keys_case_insensitive(maybe_canonical, p.bank.keys())

            if not bank_key:
                await ctx.reply("That item isn’t in your bank.")
                return

            have = int(p.bank.get(bank_key, 0))
            if have <= 0:
                await ctx.reply("That item isn’t in your bank.")
                return

            # Clamp qty to what they have
            qty = int(qty)
            if qty <= 0:
                await ctx.reply("Quantity must be > 0.")
                return
            qty = min(qty, have)

            # Determine the item name going into inventory
            if want_noted:
                if self._is_stackable(bank_key):
                    await ctx.reply(f"**{bank_key}** already stacks — no need to note it.")
                    return
                inv_item = self._note(bank_key)
            else:
                inv_item = bank_key

            space = self._inv_free_slots(p.inventory)
            if space <= 0:
                await ctx.reply("Your inventory is full.")
                return

            # How many can we actually take based on slot rules?
            if inv_item in FOOD or (not self._is_stackable(inv_item) and inv_item not in FOOD):
                take = min(space, qty)
            else:
                need = self._slots_needed_to_add(p.inventory, inv_item, qty)
                take = qty if (need == 0 or space >= need) else 0

            if take <= 0:
                await ctx.reply("No inventory space for that item.")
                return

            self._remove_item(p.bank, bank_key, take)
            self._add_item(p.inventory, inv_item, take)
            await self._persist()

        if take < qty:
            await ctx.reply(f"Withdrew **{inv_item} x{take}** (inventory full; {qty - take} left in bank).")
        else:
            await ctx.reply(f"Withdrew **{inv_item} x{take}**.")

    @w.command(name="stats", aliases=["profile", "me"])
    async def stats_cmd(self, ctx: commands.Context, *, target: Optional[str] = None):
        if not await self._ensure_ready(ctx):
            return

        member = None

        if not target:
            member = ctx.author

        else:
            # Try mention first
            if ctx.message.mentions:
                member = ctx.message.mentions[0]

            # Try exact ID match
            elif target.isdigit() and int(target) in self.players:
                member = ctx.guild.get_member(int(target)) if ctx.guild else None

            # Try name match (case-insensitive)
            else:
                search = target.lower()
                if ctx.guild:
                    for m in ctx.guild.members:
                        if m.display_name.lower() == search or m.name.lower() == search:
                            member = m
                            break

        if not member:
            await ctx.reply("Player not found.")
            return

        if member.id not in self.players:
            await ctx.reply("That player has not entered the Wilderness yet.")
            return

        p = self.players[member.id]

        where = f"Wilderness (lvl {p.wildy_level})" if p.in_wilderness else "Safe"
        total_coins = int(p.coins) + int(p.bank_coins)

        emb = discord.Embed(
            title=f"📊 {member.display_name}'s Wilderness Stats",
            description=f"Status: **{where}**\nHP: **{p.hp}/{self.config['max_hp']}**",
        )

        kd = (p.kills / p.deaths) if int(p.deaths) > 0 else float(p.kills)

        emb.add_field(
            name="⚔️ Combat",
            value=(
                f"Kills: **{int(p.kills)}**\n"
                f"Deaths: **{int(p.deaths)}**\n"
                f"K/D: **{kd:.2f}**" if int(p.deaths) > 0 else
                f"Kills: **{int(p.kills)}**\n"
                f"Deaths: **{int(p.deaths)}**\n"
                f"K/D: **∞**"
            ),
            inline=True,
        )

        emb.add_field(
            name="🧭 Exploring",
            value=(
                f"Ventures: **{int(p.ventures)}**\n"
                f"Escapes: **{int(p.escapes)}**\n"
                f"Skulled: **{'Yes' if p.skulled else 'No'}**"
            ),
            inline=True,
        )

        emb.add_field(
            name="💰 Wealth",
            value=(
                f"Coins (inv): **{int(p.coins):,}**\n"
                f"Coins (bank): **{int(p.bank_coins):,}**\n"
                f"Total: **{total_coins:,}**"
            ),
            inline=True,
        )

        emb.add_field(
            name="✨ Drops",
            value=(
                f"Unique drops: **{int(p.unique_drops)}**\n"
                f"Pet drops: **{int(p.pet_drops)}**\n"
                f"Pets owned: **{len(getattr(p, 'pets', []) or [])}**"
            ),
            inline=True,
        )

        emb.add_field(
            name="📈 Biggest Win/Loss",
            value=(
                f"Biggest win: **{int(p.biggest_win):,}**\n"
                f"Biggest loss: **{int(p.biggest_loss):,}**"
            ),
            inline=True,
        )

        slayer_lvl = self.slayer_mgr.get_slayer_level(p)
        slayer_xp = int(p.slayer_xp or 0)
        slayer_pts = int(p.slayer_points or 0)
        slayer_done = int(p.slayer_tasks_done or 0)
        emb.add_field(
            name="🗡️ Slayer",
            value=(
                f"Level: **{slayer_lvl}**\n"
                f"XP: **{slayer_xp:,}**\n"
                f"Points: **{slayer_pts:,}**\n"
                f"Tasks done: **{slayer_done}**"
            ),
            inline=True,
        )

        if member.display_avatar:
            emb.set_thumbnail(url=member.display_avatar.url)

        await ctx.reply(embed=emb)

    @w.command(name="kc", aliases=["killcount"])
    async def kc_cmd(self, ctx: commands.Context, *, npc_name: str = ""):
        if not await self._ensure_ready(ctx):
            return

        p = self._get_player(ctx.author)
        npc_kills = getattr(p, "npc_kills", {}) or {}
        total_kills = int(p.kills)

        if npc_name.strip():
            query = npc_name.strip().lower()
            matched = None
            for name in npc_kills:
                if name.lower() == query:
                    matched = name
                    break
            if not matched:
                # Try partial match
                for name in npc_kills:
                    if query in name.lower():
                        matched = name
                        break
            if not matched:
                await ctx.reply(f"No kills recorded for **{npc_name}**.")
                return

            emb = discord.Embed(title=f"⚔️ {ctx.author.display_name}'s Kill Count")
            emb.add_field(name=matched, value=f"**{npc_kills[matched]:,}** kills", inline=False)
            if ctx.author.display_avatar:
                emb.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.reply(embed=emb)
            return

        if not npc_kills:
            emb = discord.Embed(title=f"⚔️ {ctx.author.display_name}'s Kill Count")
            emb.description = f"Total kills: **{total_kills:,}**\n\nNo NPC kills recorded yet."
            if ctx.author.display_avatar:
                emb.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.reply(embed=emb)
            return

        sorted_npcs = sorted(npc_kills.items(), key=lambda x: x[1], reverse=True)
        per_page = 5
        pages = [sorted_npcs[i:i + per_page] for i in range(0, len(sorted_npcs), per_page)]

        embeds = []
        for page_idx, page_data in enumerate(pages):
            emb = discord.Embed(
                title=f"⚔️ {ctx.author.display_name}'s Kill Count",
                description=f"Total kills: **{total_kills:,}**",
            )
            lines = []
            for npc, count in page_data:
                lines.append(f"**{npc}** — {count:,} kills")
            emb.add_field(name="NPC Kills", value="\n".join(lines), inline=False)
            emb.set_footer(text=f"Page {page_idx + 1}/{len(pages)}")
            if ctx.author.display_avatar:
                emb.set_thumbnail(url=ctx.author.display_avatar.url)
            embeds.append(emb)

        if len(embeds) == 1:
            await ctx.reply(embed=embeds[0])
        else:
            view = KillCountView(author_id=ctx.author.id, embeds=embeds)
            await ctx.reply(embed=embeds[0], view=view)

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
                wildy_level = random.randint(1, cap)

            wildy_level = clamp(int(wildy_level), 1, cap)

            if p.in_wilderness:
                if wildy_level == p.wildy_level:
                    await ctx.reply(
                        f"You're already at Wilderness level **{p.wildy_level}**."
                    )
                    return

                going_deeper = wildy_level > p.wildy_level
                p.wildy_level = wildy_level

                if going_deeper and not p.skulled:
                    skull_chance = min(0.10 + (wildy_level / cap) * 0.35, 0.45)
                    if random.random() < skull_chance:
                        p.skulled = True

                p.ventures += 1
                self._touch(p)
                self._set_cd(p, "venture")
                await self._persist()

                if going_deeper:
                    arrow = "⬆️"
                    direction = "deeper"
                else:
                    arrow = "⬇️"
                    direction = "back"

                await ctx.reply(
                    f"{arrow} You venture **{direction}** in the Wilderness (**level {wildy_level}**). "
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


    @w.command(name="fight")
    async def fight_npc(self, ctx: commands.Context, *, npcname: Optional[str] = None):
        """Fight an NPC, optionally targeting a specific one (75% chance to encounter it)."""
        if not await self._ensure_ready(ctx):
            return

        forced_npc: Optional[Tuple[str, int, int, int, str, int, int]] = None
        forced_success = False

        async with self._mem_lock:
            p = self._get_player(ctx.author)

            # 5 second fight cooldown
            ok, left = self._cd_ready(p, "fight", 1)
            if not ok:
                await ctx.reply(f"Fight cooldown: **{left}s**")
                return

            if not p.in_wilderness:
                await ctx.reply("You’re not in the Wilderness. Use !w venture.")
                return

            self._set_cd(p, "fight")


            self._touch(p)

            eligible = [n for n in NPCS if p.wildy_level >= n["min_wildy"]] or [NPCS[0]]

            if npcname:
                forced_npc = self._resolve_npc(npcname)
                if not forced_npc:
                    await ctx.reply("Unknown NPC. Use `!w npcs` to see the list.")
                    return
                if p.wildy_level < int(forced_npc["min_wildy"]):
                    await ctx.reply(
                        f"That NPC requires Wilderness level **{forced_npc['min_wildy']}**. "
                        f"You're currently **{p.wildy_level}**."
                    )
                    return

                # Bracelet of Slayer Aggression: 100% if targeting slayer task, costs 20 Chaos rune
                aggro_brace = p.equipment.get("gloves") == "Bracelet of Slayer Aggression"
                task = p.slayer_task
                on_task_target = (
                    aggro_brace and task
                    and task.get("npc_type") == forced_npc["npc_type"]
                    and int(task.get("remaining", 0)) > 0
                    and p.inventory.get("Chaos rune", 0) >= 20
                )
                if on_task_target:
                    self._remove_item(p.inventory, "Chaos rune", 20)
                forced_success = on_task_target or (random.random() <= 0.75)
                if forced_success:
                    chosen = forced_npc
                else:
                    pool = [n for n in eligible if self._norm(n["name"]) != self._norm(forced_npc["name"])]
                    chosen = random.choice(pool) if pool else random.choice(eligible)
            else:
                chosen = random.choice(eligible)

            # Build header lines for targeted fight info
            header_lines: List[str] = []
            if forced_npc:
                if forced_success:
                    header_lines.append(f"🎯 Targeted fight: **{forced_npc['name']}** — **SUCCESS**")
                else:
                    header_lines.append(f"🎯 Targeted fight: **{forced_npc['name']}** — **FAILED**, random encounter instead…")

            won, npc_name, events, lost_items, bank_loss, loot_lines, ground_drops, eaten_food, broadcasts, slayer_task_info = \
                self._simulate_pvm_fight_and_loot(p, chosen, header_lines=header_lines or None)

            if not won:
                food_lines = self._food_summary_lines(eaten_food, lost_items)

                p.deaths += 1
                p.wildy_run_id = int(p.wildy_run_id) + 1
                p.ground_items = []
                p.in_wilderness = False
                p.skulled = False
                p.wildy_level = 1
                p.hp = int(self.config["starting_hp"])
                self._full_heal(p)
                await self._persist()

                pages = self._build_pages(events, per_page=10)
                summary = (
                    f"☠️ **You died to {npc_name}.**\n"
                    f"📉 **Lost from inventory:**\n{self._format_items_short(lost_items, max_lines=18)}\n"
                    f"🏦 Lost bank coins: **{bank_loss:,}** (10%)"
                    + (("\n\n" + "\n".join(food_lines)) if food_lines else "")
                )
                pages.append(summary)

                npc_image = chosen.get("image")
                view = FightLogView(
                    author_id=ctx.author.id,
                    pages=pages,
                    title=f"{ctx.author.display_name} vs {npc_name}",
                    cog=self,
                    ground_drops=ground_drops,
                    start_on_last=True,
                    npc_image=npc_image,
                )
                await ctx.reply(embed=view._render_embed(), view=view)

                return

            self._touch(p)
            await self._persist()

            pages = self._build_pages(events, per_page=10)
            summary = (
                f"✅ **You have killed {npc_name}!**\n"
                f"End HP: **{p.hp}/{self.config['max_hp']}**\n"
                + ("\n".join(loot_lines) if loot_lines else "(no loot)")
            )
            pages.append(summary)

            npc_image = chosen.get("image")
            view = FightLogView(author_id=ctx.author.id, pages=pages, title=f"{ctx.author.display_name} vs {npc_name}", cog=self, ground_drops=ground_drops, start_on_last=True, npc_image=npc_image)
            await ctx.reply(embed=view._render_embed(), view=view)

            if slayer_task_info:
                emb = discord.Embed(
                    title="✅ Slayer Task Complete!",
                    description=(
                        f"**{ctx.author.display_name}** has completed their slayer task!\n\n"
                        f"🗡️ Slayer Level: **{slayer_task_info['level']}**\n"
                        f"⭐ Points earned: **+{slayer_task_info['points']}** (Total: **{slayer_task_info['total_points']}**)\n"
                        f"📋 Tasks completed: **{slayer_task_info['tasks_done']}**\n\n"
                        f"Use `!w slayer task` to get a new assignment!"
                    ),
                    color=0x00FF00,
                )
                await ctx.send(embed=emb)

            # Low HP / no food warning
            has_food = any(p.inventory.get(f, 0) > 0 for f in FOOD)
            warnings = []
            if p.hp < 20:
                warnings.append(f"Your HP is critically low (**{p.hp}/{self.config['max_hp']}**)")
            if not has_food:
                warnings.append("You have **no food** remaining in your inventory")
            if warnings:
                emb = discord.Embed(
                    title="⚠️ Warning!",
                    description="\n".join(f"- {w}" for w in warnings)
                        + "\n\nConsider using `!w eat`, `!w tele`, or restocking before your next fight!",
                    color=0xFF4444,
                )
                await ctx.send(embed=emb)

        await self._send_broadcasts(ctx.author, broadcasts)

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

    @w.command(name="tele", aliases=["teleport", "tp"])
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

            if random.random() < 0.20:
                eligible = [n for n in NPCS if p.wildy_level >= n["min_wildy"]] or [NPCS[0]]
                chosen = random.choice(eligible)

                header = [
                    f"⚠️ **Ambush!** You tried to teleport but were attacked by **{chosen['name']}** (Wildy {p.wildy_level})."
                ]

                won, npc_name, events, lost_items, bank_loss, loot_lines, ground_drops, eaten_food, broadcasts, slayer_task_info = \
                    self._simulate_pvm_fight_and_loot(p, chosen, header_lines=header)

                npc_image = chosen.get("image")

                if not won:
                    food_lines = self._food_summary_lines(eaten_food, lost_items)

                    p.deaths += 1
                    p.wildy_run_id = int(p.wildy_run_id) + 1
                    p.ground_items = []
                    p.in_wilderness = False
                    p.skulled = False
                    p.wildy_level = 1
                    p.hp = int(self.config["starting_hp"])
                    self._full_heal(p)
                    await self._persist()

                    pages = self._build_pages(events, per_page=10)
                    summary = (
                        f"☠️ **You died during the ambush.**\n"
                        f"📉 **Lost from inventory:**\n{self._format_items_short(lost_items, max_lines=18)}\n"
                        f"🏦 Lost bank coins: **{bank_loss:,}** (10%)"
                        + (("\n\n" + "\n".join(food_lines)) if food_lines else "")
                    )
                    pages.append(summary)

                    view = FightLogView(
                        author_id=ctx.author.id,
                        pages=pages,
                        title=f"Ambush! {ctx.author.display_name} vs {npc_name}",
                        cog=self,
                        ground_drops=ground_drops,
                        start_on_last=True,
                        npc_image=npc_image,
                    )
                    await ctx.reply(embed=view._render_embed(), view=view)
                    return

                self._touch(p)
                await self._persist()

                pages = self._build_pages(events, per_page=10)
                summary = (
                    f"✅ **You have killed {npc_name}!** Your teleport was interrupted.\n"
                    f"End HP: **{p.hp}/{self.config['max_hp']}**\n"
                    + ("\n".join(loot_lines) if loot_lines else "(no loot)")
                    + f"\n\nYou are still in the Wilderness (level {p.wildy_level}). Try `!w tele` again."
                )
                pages.append(summary)

                view = FightLogView(
                    author_id=ctx.author.id,
                    pages=pages,
                    title=f"Ambush! {ctx.author.display_name} vs {npc_name}",
                    cog=self,
                    ground_drops=ground_drops,
                    start_on_last=True,
                    npc_image=npc_image,
                )
                await ctx.reply(embed=view._render_embed(), view=view)

                if slayer_task_info:
                    emb = discord.Embed(
                        title="✅ Slayer Task Complete!",
                        description=(
                            f"**{ctx.author.display_name}** has completed their slayer task!\n\n"
                            f"🗡️ Slayer Level: **{slayer_task_info['level']}**\n"
                            f"⭐ Points earned: **+{slayer_task_info['points']}** (Total: **{slayer_task_info['total_points']}**)\n"
                            f"📋 Tasks completed: **{slayer_task_info['tasks_done']}**\n\n"
                            f"Use `!w slayer task` to get a new assignment!"
                        ),
                        color=0x00FF00,
                    )
                    await ctx.send(embed=emb)

                # Low HP / no food warning
                has_food = any(p.inventory.get(f, 0) > 0 for f in FOOD)
                warnings = []
                if p.hp < 20:
                    warnings.append(f"Your HP is critically low (**{p.hp}/{self.config['max_hp']}**)")
                if not has_food:
                    warnings.append("You have **no food** remaining in your inventory")
                if warnings:
                    emb = discord.Embed(
                        title="⚠️ Warning!",
                        description="\n".join(f"- {w}" for w in warnings)
                            + "\n\nConsider using `!w eat`, `!w tele`, or restocking before your next fight!",
                        color=0xFF4444,
                    )
                    await ctx.send(embed=emb)

                await self._send_broadcasts(ctx.author, broadcasts)
                return

            # 80% successful teleport
            p.wildy_run_id = int(p.wildy_run_id) + 1
            p.ground_items = []
            p.in_wilderness = False
            p.skulled = False
            p.wildy_level = 1
            p.escapes += 1
            self._full_heal(p)
            await self._persist()

        await ctx.reply("✨ Teleport successful! (You are fully healed)")


    @w.group(name="lock", invoke_without_command=True)
    async def lock_cmd(self, ctx: commands.Context, *, itemname: Optional[str] = None):
        """Lock an item so it stays in your inventory when you deposit."""
        if not await self._ensure_ready(ctx):
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)

            # No item -> show help + current locks
            if not itemname:
                await ctx.reply(
                    "**Inventory Lock**\n"
                    "`!w lock <itemname>` — lock an item so it stays in your inventory when you `!w deposit`\n"
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
            "It will stay in your inventory when you use `!w deposit`.\n\n"
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
        await ctx.reply(
            "**Chests:**\n"
            "`!w chest open mysterious` — Open with a **Mysterious key**\n"
            "`!w chest open bone` — Open with a **Bone key**"
        )

    @chest.command(name="open")
    async def chest_open(self, ctx: commands.Context, chest_type: str = ""):
        if not await self._ensure_ready(ctx):
            return

        ct = chest_type.strip().lower()
        if ct not in ("mysterious", "bone"):
            await ctx.reply("Usage: `!w chest open mysterious` or `!w chest open bone`")
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)
            if p.in_wilderness:
                await ctx.reply("Open chests out of the Wilderness.")
                return

            if ct == "mysterious":
                key_name = "Mysterious key"
                if p.inventory.get(key_name, 0) < 1:
                    await ctx.reply(f"You need a **{key_name}** in your inventory.")
                    return

                self._remove_item(p.inventory, key_name, 1)

                lo, hi = self.config["chest_coin_range"]
                coins = random.randint(int(lo), int(hi))
                p.coins += coins

                reward = self._roll_pick_one(self.config.get("chest_rewards", []))
                if reward:
                    item, qty = reward
                    auto_drops: Dict[str, int] = {}
                    dest = self._try_put_item_with_blacklist(p, item, qty, auto_drops)
                    result = f"🗝️ Mysterious chest: **{item} x{qty}** {dest} + **{coins:,} coins**!"
                    if auto_drops:
                        result += "\n🗑️ Auto-dropped (blacklist):"
                        for name, q in sorted(auto_drops.items(), key=lambda x: x[0].lower()):
                            result += f"\n- {name} x{q}"
                else:
                    result = f"🗝️ Mysterious chest: **{coins:,} coins** (no special reward this time)."

            else:
                key_name = "Bone key"
                if p.inventory.get(key_name, 0) < 1:
                    await ctx.reply(f"You need a **{key_name}** in your inventory.")
                    return

                self._remove_item(p.inventory, key_name, 1)

                coins = random.randint(5000, 45000)
                p.coins += coins

                bone_rewards = [
                    {"item": "Cursed Bone", "min": 1, "max": 1, "chance": "1/50"},
                    {"item": "Bone Rune", "min": 5, "max": 25, "chance": "1/10"},
                    {"item": "Dragon platebody", "min": 1, "max": 1, "chance": "1/50"},
                ]
                reward = self._roll_pick_one(bone_rewards)
                if reward:
                    item, qty = reward
                    auto_drops: Dict[str, int] = {}
                    dest = self._try_put_item_with_blacklist(p, item, qty, auto_drops)
                    result = f"🦴 Bone chest: **{item} x{qty}** {dest} + **{coins:,} coins**!"
                    if auto_drops:
                        result += "\n🗑️ Auto-dropped (blacklist):"
                        for name, q in sorted(auto_drops.items(), key=lambda x: x[0].lower()):
                            result += f"\n- {name} x{q}"
                else:
                    result = f"🦴 Bone chest: **{coins:,} coins** (no special reward this time)."

            await self._persist()

        await ctx.reply(result)

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
            resolved = self._resolve_item(item_query)
            if resolved and resolved in items:
                shop_key = resolved
        if not shop_key:
            await ctx.reply("That item isn't sold here. Use `!w shop list`.")
            return

        price_each = int(items[shop_key])

        async with self._mem_lock:
            p = self._get_player(ctx.author)
            if p.in_wilderness:
                await ctx.reply("Buy items out of the Wilderness.")
                return

            if self._player_owns_esspouch(p, shop_key):
                await ctx.reply(f"You already own a **{shop_key}**.")
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

        meta = ITEMS.get(canonical, {})
        price_each = int(meta.get("value", 0))

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



    @w.command(name="craftables")
    async def craftables_cmd(self, ctx: commands.Context):
        if not await self._ensure_ready(ctx):
            return

        if not CRAFTABLES:
            await ctx.reply("No craftable items available.")
            return

        first_name = next(iter(CRAFTABLES))
        emb = self._craftable_info_embed(first_name)
        view = CraftableInfoView(self, author_id=ctx.author.id)
        await ctx.reply(embed=emb, view=view)

    @w.command(name="craft")
    async def craft_cmd(self, ctx: commands.Context, *, item_query: str = ""):
        if not await self._ensure_ready(ctx):
            return

        if not item_query:
            await ctx.reply("Usage: `!w craft <item name>`. Use `!w craftables` to see available recipes.")
            return

        craft_name = None
        norm_query = self._norm(item_query)
        for name in CRAFTABLES:
            if self._norm(name) == norm_query:
                craft_name = name
                break
        if not craft_name:
            resolved = self._resolve_item(item_query)
            if resolved and resolved in CRAFTABLES:
                craft_name = resolved
        if not craft_name:
            await ctx.reply(f"**{item_query}** is not a craftable item. Use `!w craftables` to see recipes.")
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)
            ok, msg = self.craft_mgr.craft(p, craft_name)
            if ok:
                self._touch(p)
                await self._persist()

        await ctx.reply(msg)


    @w.command(name="breakdownitems")
    async def breakdownitems_cmd(self, ctx: commands.Context):
        if not await self._ensure_ready(ctx):
            return

        if not BREAKDOWNS:
            await ctx.reply("No breakdownable items available.")
            return

        first_name = next(iter(BREAKDOWNS))
        emb = self._breakdown_info_embed(first_name)
        view = BreakdownInfoView(self, author_id=ctx.author.id)
        await ctx.reply(embed=emb, view=view)

    @w.command(name="breakdown")
    async def breakdown_cmd(self, ctx: commands.Context, *, item_query: str = ""):
        if not await self._ensure_ready(ctx):
            return

        if not item_query:
            await ctx.reply("Usage: `!w breakdown <item name>`. Use `!w breakdownitems` to see what can be broken down.")
            return

        bd_name = None
        norm_query = self._norm(item_query)
        for name in BREAKDOWNS:
            if self._norm(name) == norm_query:
                bd_name = name
                break
        if not bd_name:
            resolved = self._resolve_item(item_query)
            if resolved and resolved in BREAKDOWNS:
                bd_name = resolved
        if not bd_name:
            await ctx.reply(f"**{item_query}** cannot be broken down. Use `!w breakdownitems` to see options.")
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)
            ok, msg = self.breakdown_mgr.breakdown(p, bd_name)
            if ok:
                self._touch(p)
                await self._persist()

        await ctx.reply(msg)


    @w.command(name="rc", aliases=["runecraft"])
    async def rc_cmd(self, ctx: commands.Context, *, rune_query: str = ""):
        if not await self._ensure_ready(ctx):
            return

        if not rune_query:
            await ctx.reply("Usage: `!w rc <rune name>` — e.g. `!w rc nature rune`")
            return

        rune_name = self.rc_mgr.resolve_rune(rune_query)
        if not rune_name:
            await ctx.reply(f"**{rune_query}** is not a valid rune.")
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)
            ok, msg = self.rc_mgr.craft_runes(p, rune_name)
            if ok:
                self._touch(p)
                await self._persist()

        await ctx.reply(msg)


    @w.command(name="presets")
    async def presets_list_cmd(self, ctx: commands.Context):
        if not await self._ensure_ready(ctx):
            return
        async with self._mem_lock:
            p = self._get_player(ctx.author)
            names = self.preset_mgr.list_presets(p)
        if names:
            listing = "\n".join(f"  • {n}" for n in names)
            await ctx.reply(f"**Your presets:**\n{listing}\n\nUse `!w preset create/load/delete/check <name>`.")
        else:
            await ctx.reply("You have no presets. Use `!w preset create <name>` to save one.")

    @w.group(name="preset", invoke_without_command=True)
    async def preset_group(self, ctx: commands.Context):
        if not await self._ensure_ready(ctx):
            return
        async with self._mem_lock:
            p = self._get_player(ctx.author)
            names = self.preset_mgr.list_presets(p)
        if names:
            listing = "\n".join(f"  • {n}" for n in names)
            await ctx.reply(f"**Your presets:**\n{listing}\n\nUse `!w preset create/load/delete/check <name>`.")
        else:
            await ctx.reply("You have no presets. Use `!w preset create <name>` to save one.")

    @preset_group.command(name="create")
    async def preset_create(self, ctx: commands.Context, *, name: str = ""):
        if not await self._ensure_ready(ctx):
            return
        if not name:
            await ctx.reply("Usage: `!w preset create <name>`")
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)
            if p.in_wilderness:
                await ctx.reply("You can't manage presets while in the Wilderness.")
                return
            ok, msg = self.preset_mgr.create(p, name)
            if ok:
                self._touch(p)
                await self._persist()

        await ctx.reply(msg)

    @preset_group.command(name="override")
    async def preset_override(self, ctx: commands.Context, *, name: str = ""):
        if not await self._ensure_ready(ctx):
            return
        if not name:
            await ctx.reply("Usage: `!w preset override <name>`")
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)
            if p.in_wilderness:
                await ctx.reply("You can't manage presets while in the Wilderness.")
                return
            ok, msg = self.preset_mgr.create(p, name)
            if ok:
                self._touch(p)
                await self._persist()

        await ctx.reply(msg)

    @preset_group.command(name="load")
    async def preset_load(self, ctx: commands.Context, *, name: str = ""):
        if not await self._ensure_ready(ctx):
            return
        if not name:
            await ctx.reply("Usage: `!w preset load <name>`")
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)
            if p.in_wilderness:
                await ctx.reply("You can't load presets while in the Wilderness.")
                return
            ok, msg = self.preset_mgr.load(p, name)
            if ok:
                self._touch(p)
                await self._persist()

        await ctx.reply(msg)

    @preset_group.command(name="delete")
    async def preset_delete(self, ctx: commands.Context, *, name: str = ""):
        if not await self._ensure_ready(ctx):
            return
        if not name:
            await ctx.reply("Usage: `!w preset delete <name>`")
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)
            ok, msg = self.preset_mgr.delete(p, name)
            if ok:
                self._touch(p)
                await self._persist()

        await ctx.reply(msg)

    @preset_group.command(name="check")
    async def preset_check(self, ctx: commands.Context, *, name: str = ""):
        if not await self._ensure_ready(ctx):
            return
        if not name:
            await ctx.reply("Usage: `!w preset check <name>`")
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)
            ok, key_or_err, data = self.preset_mgr.check(p, name)

        if not ok:
            await ctx.reply(key_or_err)
            return

        equip = data.get("equipment", {})
        inv = data.get("inventory", {})

        emb = discord.Embed(title=f"📋 Preset: {key_or_err}")

        if equip:
            equip_lines = [f"**{slot}:** {item}" for slot, item in sorted(equip.items())]
            emb.add_field(name="🛡️ Equipment", value="\n".join(equip_lines), inline=False)
        else:
            emb.add_field(name="🛡️ Equipment", value="(none)", inline=False)

        if inv:
            inv_lines = [f"{item} x{qty:,}" for item, qty in sorted(inv.items(), key=lambda x: x[0].lower())]
            emb.add_field(name="🎒 Inventory", value="\n".join(inv_lines), inline=False)
        else:
            emb.add_field(name="🎒 Inventory", value="(empty)", inline=False)

        if ctx.author.display_avatar:
            emb.set_thumbnail(url=ctx.author.display_avatar.url)

        await ctx.reply(embed=emb)

    # ── Alchemy ──────────────────────────────────────────────────────

    @w.group(name="alch", invoke_without_command=True)
    async def alch_cmd(self, ctx: commands.Context, *, item_name: str = ""):
        if not await self._ensure_ready(ctx):
            return

        if not item_name.strip():
            await ctx.reply("Usage: `!w alch <item>` — High-alch an item for coins (costs 1 Nature rune per item).\n"
                            "`!w alch auto <item>` — Toggle auto-alch on drops.")
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)
            resolved = self._resolve_item(item_name.strip())
            if not resolved:
                await ctx.reply(f"Unknown item: **{item_name.strip()}**")
                return

            value = ITEMS.get(resolved, {}).get("value", 0)
            if value <= 0:
                await ctx.reply(f"**{resolved}** has no alch value.")
                return

            inv_key = self._resolve_from_keys_case_insensitive(resolved, p.inventory.keys())
            inv_qty = p.inventory.get(inv_key, 0) if inv_key else 0
            if inv_qty <= 0:
                await ctx.reply(f"You don't have any **{resolved}** in your inventory.")
                return

            nats = p.inventory.get("Nature rune", 0)
            if nats <= 0:
                await ctx.reply("You need at least **1 Nature rune** to alch.")
                return

            alch_qty = min(inv_qty, nats)
            total_gp = value * alch_qty

            self._remove_item(p.inventory, inv_key, alch_qty)
            self._remove_item(p.inventory, "Nature rune", alch_qty)
            p.coins += total_gp
            await self._persist()

        await ctx.reply(f"🔥 Alched **{resolved} x{alch_qty}** → **{total_gp:,} coins** (-{alch_qty} Nature rune)")

    @alch_cmd.command(name="auto")
    async def alch_auto_cmd(self, ctx: commands.Context, *, item_name: str = ""):
        if not await self._ensure_ready(ctx):
            return

        if not item_name.strip():
            async with self._mem_lock:
                p = self._get_player(ctx.author)
                auto_list = getattr(p, "alch_auto", None) or []
            if not auto_list:
                await ctx.reply("Your auto-alch list is empty.\nUsage: `!w alch auto <item>` to toggle.")
                return
            lines = [f"• **{i}**" for i in sorted(auto_list)]
            await ctx.reply("🔥 **Auto-alch list:**\n" + "\n".join(lines))
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)
            resolved = self._resolve_item(item_name.strip())
            if not resolved:
                await ctx.reply(f"Unknown item: **{item_name.strip()}**")
                return

            if p.alch_auto is None:
                p.alch_auto = []

            if resolved in p.alch_auto:
                p.alch_auto.remove(resolved)
                await self._persist()
                await ctx.reply(f"🔥 Removed **{resolved}** from auto-alch.")
            else:
                value = ITEMS.get(resolved, {}).get("value", 0)
                if value <= 0:
                    await ctx.reply(f"**{resolved}** has no alch value.")
                    return
                p.alch_auto.append(resolved)
                await self._persist()
                await ctx.reply(f"🔥 Added **{resolved}** to auto-alch. Drops will be auto-alched for **{value:,} coins** each (costs 1 Nature rune per item).")

    # ── Slayer ───────────────────────────────────────────────────────

    @w.group(name="slayer", invoke_without_command=True)
    async def slayer_cmd(self, ctx: commands.Context):
        if not await self._ensure_ready(ctx):
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)

        slayer_lvl = self.slayer_mgr.get_slayer_level(p)
        current_xp, next_xp = self.slayer_mgr.xp_to_next(p)
        pts = int(p.slayer_points or 0)
        done = int(p.slayer_tasks_done or 0)

        emb = discord.Embed(title=f"🗡️ {ctx.author.display_name}'s Slayer Info", color=0x8B0000)
        emb.add_field(name="Level", value=f"**{slayer_lvl}**", inline=True)
        if slayer_lvl < 120:
            emb.add_field(name="XP", value=f"**{current_xp:,}** / **{next_xp:,}**", inline=True)
        else:
            emb.add_field(name="XP", value=f"**{current_xp:,}**", inline=True)
        emb.add_field(name="Points", value=f"**{pts:,}**", inline=True)
        emb.add_field(name="Tasks Done", value=f"**{done}**", inline=True)

        task = p.slayer_task
        if task and int(task.get("remaining", 0)) > 0:
            killed = int(task["total"]) - int(task["remaining"])
            emb.add_field(
                name="Current Task",
                value=f"Kill **{task['npc']}** — **{killed}/{task['total']}** ({task['remaining']} remaining)",
                inline=False,
            )
        else:
            emb.add_field(
                name="Current Task",
                value="No active task. Use `!w slayer task` to get one.",
                inline=False,
            )

        if ctx.author.display_avatar:
            emb.set_thumbnail(url=ctx.author.display_avatar.url)

        await ctx.reply(embed=emb)

    @slayer_cmd.command(name="task")
    async def slayer_task_cmd(self, ctx: commands.Context):
        if not await self._ensure_ready(ctx):
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)

            task = p.slayer_task
            if task and int(task.get("remaining", 0)) > 0:
                await ctx.reply(f"🗡️ Current task: Kill **{task['remaining']}/{task['total']} {task['npc']}**.")
                return

            ok, result = self.slayer_mgr.assign_task(p)
            if not ok:
                await ctx.reply(result)
                return

            task = p.slayer_task
            npc_type = task["npc_type"]
            info = NPC_SLAYER.get(npc_type, {})
            xp_per = info.get("xp", 0)
            total_xp = xp_per * task["total"]

            # Find min wildy level for this NPC
            npc_data = self._resolve_npc(task["npc"])
            min_wildy = npc_data["min_wildy"] if npc_data else "?"

            await self._persist()

        emb = discord.Embed(title="🗡️ New Slayer Task!", color=0x8B0000)
        emb.description = (
            f"Kill **{task['total']} {task['npc']}**\n\n"
            f"XP per kill: **{xp_per}**\n"
            f"Total XP: **{total_xp:,}**\n"
            f"Min wilderness level: **{min_wildy}**"
        )
        await ctx.reply(embed=emb)

    @slayer_cmd.command(name="skip")
    async def slayer_skip_cmd(self, ctx: commands.Context):
        if not await self._ensure_ready(ctx):
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)
            ok, msg = self.slayer_mgr.skip_task(p)
            if ok:
                await self._persist()

        await ctx.reply(f"🗡️ {msg}")

    @slayer_cmd.command(name="shop")
    async def slayer_shop_cmd(self, ctx: commands.Context):
        if not await self._ensure_ready(ctx):
            return

        emb = discord.Embed(title="🗡️ Slayer Shop", color=0x8B0000)
        for key, item in SLAYER_SHOP.items():
            emb.add_field(
                name=f"{item['name']} — {item['cost']} pts",
                value=item["description"],
                inline=False,
            )
        emb.add_field(
            name=f"Block NPC — {SLAYER_BLOCK_COST} pts",
            value=f"Block an NPC from task assignments (max {MAX_SLAYER_BLOCKS}). Use `!w slayer block <npc>`.",
            inline=False,
        )
        emb.set_footer(text="Use !w slayer buy <item> to purchase.")
        await ctx.reply(embed=emb)

    @slayer_cmd.command(name="buy")
    async def slayer_buy_cmd(self, ctx: commands.Context, *, item_name: str = ""):
        if not await self._ensure_ready(ctx):
            return

        if not item_name.strip():
            await ctx.reply("Usage: `!w slayer buy <item>`")
            return

        query = item_name.strip().lower()
        matched_key = None
        for key, shop_item in SLAYER_SHOP.items():
            if query == key.lower() or query == shop_item["name"].lower():
                matched_key = key
                break
        if not matched_key:
            for key, shop_item in SLAYER_SHOP.items():
                if query in key.lower() or query in shop_item["name"].lower():
                    matched_key = key
                    break

        if not matched_key:
            await ctx.reply(f"Item not found in slayer shop: **{item_name.strip()}**")
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)
            ok, msg = self.slayer_mgr.buy_shop_item(p, matched_key)
            if ok:
                await self._persist()

        await ctx.reply(f"🗡️ {msg}")

    @slayer_cmd.command(name="npcs")
    async def slayer_npcs_cmd(self, ctx: commands.Context):
        if not await self._ensure_ready(ctx):
            return

        lines = []
        for npc in NPCS:
            info = NPC_SLAYER.get(npc["npc_type"])
            if not info:
                continue
            lines.append(f"**{npc['name']}** — Slayer {info['level']} | {info['xp']} XP | Wildy {npc['min_wildy']}+")

        emb = discord.Embed(title="🗡️ Slayer NPCs", color=0x8B0000)
        emb.description = "\n".join(lines) if lines else "No slayer NPCs found."
        await ctx.reply(embed=emb)

    @slayer_cmd.group(name="block", invoke_without_command=True)
    async def slayer_block_cmd(self, ctx: commands.Context, *, npc_name: str = ""):
        if not await self._ensure_ready(ctx):
            return

        if not npc_name.strip():
            async with self._mem_lock:
                p = self._get_player(ctx.author)
                blocked = list(p.slayer_blocked or [])

            if not blocked:
                await ctx.reply(f"🗡️ Your block list is empty (**0/{MAX_SLAYER_BLOCKS}**). Use `!w slayer block <npc>` to block one.")
                return

            lines = []
            for npc_type in blocked:
                name = npc_type
                for npc in NPCS:
                    if npc["npc_type"] == npc_type:
                        name = npc["name"]
                        break
                lines.append(f"• **{name}**")
            await ctx.reply(f"🗡️ **Block list ({len(blocked)}/{MAX_SLAYER_BLOCKS}):**\n" + "\n".join(lines))
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)
            ok, msg = self.slayer_mgr.block_npc(p, npc_name.strip())
            if ok:
                await self._persist()

        await ctx.reply(f"🗡️ {msg}")

    @slayer_block_cmd.command(name="remove")
    async def slayer_block_remove_cmd(self, ctx: commands.Context, *, npc_name: str = ""):
        if not await self._ensure_ready(ctx):
            return

        if not npc_name.strip():
            await ctx.reply("Usage: `!w slayer block remove <npc>`")
            return

        async with self._mem_lock:
            p = self._get_player(ctx.author)
            ok, msg = self.slayer_mgr.unblock_npc(p, npc_name.strip())
            if ok:
                await self._persist()

        await ctx.reply(f"🗡️ {msg}")

    # ── Highscores ───────────────────────────────────────────────────

    @w.command(name="highscores", aliases=["hs"])
    async def highscores_cmd(self, ctx: commands.Context, *, category: str = ""):
        if not await self._ensure_ready(ctx):
            return

        cat = category.strip().lower() if category.strip() else "overall"
        valid_cats = {"overall", "kills", "deaths", "coins", "slayer", "unique", "pets", "tasks"}
        if cat not in valid_cats:
            cat = "overall"

        emb = self._highscores_embed(cat, ctx.guild)
        view = HighscoresView(self, ctx.author.id, ctx.guild, cat)
        await ctx.reply(embed=emb, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(Wilderness(bot))
