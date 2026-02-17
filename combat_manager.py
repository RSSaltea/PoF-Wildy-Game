import discord
import asyncio
import random
from typing import Dict, Any, Optional, Tuple, List, TYPE_CHECKING

from .models import PlayerState, DuelState, clamp, parse_chance, _now
from .npcs import NPCS
from .items import FOOD, ITEMS

if TYPE_CHECKING:
    from .wilderness import Wilderness

REVENANT_TYPES = {"revenant", "revenant knight", "revenant demon", "revenant necro", "revenant archon"}
ETHER_WEAPONS = {"Viggora's Chainmace", "Abyssal Chainmace"}
AFK_TIMEOUT_SEC = 60 * 60
AFK_SWEEP_INTERVAL_SEC = 5 * 60


class CombatManager:
    def __init__(self, cog: "Wilderness"):
        self.cog = cog

    
    def hp_line_pvm(self, your_hp: int, npc_name: str, npc_hp: int, npc_max: int) -> str:
        return f"❤️ You: **{your_hp}/{self.cog.config['max_hp']}** | {npc_name}: **{max(0, npc_hp)}/{npc_max}**"

    def hp_line_pvp(self, a_name: str, a_hp: int, b_name: str, b_hp: int) -> str:
        return f"❤️ {a_name}: **{a_hp}/{self.cog.config['max_hp']}** | {b_name}: **{b_hp}/{self.cog.config['max_hp']}**"

    def ground_drop_lines(self, ground_drops: List[Tuple[str, int, int]]) -> List[str]:
        if not ground_drops:
            return []

        totals: Dict[str, int] = {}
        for item, qty, _run_id in ground_drops:
            if qty <= 0:
                continue
            totals[item] = totals.get(item, 0) + int(qty)

        if not totals:
            return []

        lines: List[str] = []
        lines.append("🫳 **On ground (5 min):**")
        for name, q in sorted(totals.items(), key=lambda x: x[0].lower()):
            lines.append(f"- **{name} x{q}**")
        return lines

    
    def pair_key(self, a: int, b: int) -> frozenset:
        return frozenset({a, b})

    def duel_active_for_user(self, uid: int) -> Optional[DuelState]:
        for k, d in self.cog.duels_by_pair.items():
            if uid in k:
                return d
        return None

    def duel_render(
        self,
        duel: DuelState,
        a: discord.Member,
        b: discord.Member,
        pa: PlayerState,
        pb: PlayerState,
        ended: bool,
    ) -> str:
        lines: List[str] = []
        if not ended:
            turn_name = a.display_name if duel.turn_id == duel.a_id else b.display_name
            lines.append(f"⚔️ **Fight**: {a.display_name} attacked {b.display_name} — turn: **{turn_name}**")
            lines.append("🌀 Teleport chance: **50%** if it's your first action, otherwise **20%**.")
        else:
            lines.append(f"⚔️ **Fight ended**: {a.display_name} vs {b.display_name}")
        tail = duel.log[-14:]
        lines.extend(tail if tail else ["(no actions yet)"])
        return "\n".join(lines)

    
    def pvp_transfer_all_items(self, winner: PlayerState, loser: PlayerState) -> List[str]:
        """Transfer all loser items to winner (no coins)."""
        lines: List[str] = []
        for item, qty in list(loser.inventory.items()):
            if qty <= 0:
                continue
            dest = self.cog._try_put_item(winner, item, qty)
            lines.append(f"📦 Looted {item} x{qty} {dest}".rstrip())
        loser.inventory.clear()

        for slot, item in list(loser.equipment.items()):
            dest = self.cog._try_put_item(winner, item, 1)
            lines.append(f"🛡️ Looted equipped ({slot}) {item} x1 {dest}".rstrip())
        loser.equipment.clear()
        return lines

    def food_summary_lines(self, eaten: Dict[str, int], inv: Dict[str, int]) -> List[str]:
        eaten = eaten or {}
        inv = inv or {}

        keys = set()
        for k, v in eaten.items():
            if int(v) > 0:
                keys.add(k)
        for k, v in inv.items():
            if k in FOOD and int(v) > 0:
                keys.add(k)

        if not keys:
            return []

        def sort_key(name: str):
            return (name.lower(), name)

        lines: List[str] = []
        eaten_pairs = [(k, int(eaten.get(k, 0))) for k in keys]
        eaten_pairs = [(k, v) for (k, v) in eaten_pairs if v > 0]
        eaten_pairs.sort(key=lambda kv: sort_key(kv[0]))

        left_pairs = [(k, int(inv.get(k, 0))) for k in keys]
        left_pairs.sort(key=lambda kv: sort_key(kv[0]))

        if eaten_pairs:
            lines.append("🍖 **Food eaten:** " + ", ".join(f"**{k} x{v}**" for k, v in eaten_pairs))
        else:
            lines.append("🍖 **Food eaten:** (none)")

        lines.append("🥩 **Food left:** " + ", ".join(f"**{k} x{v}**" for k, v in left_pairs))

        return lines

    def format_items_short(self, items: Dict[str, int], max_lines: int = 12) -> str:
        if not items:
            return "(none)"
        pairs = [(k, int(v)) for k, v in items.items() if int(v) > 0]
        pairs.sort(key=lambda x: (x[0].lower(), x[0]))
        lines = [f"- {k} x{v}" for k, v in pairs]
        if len(lines) > max_lines:
            rest = len(lines) - max_lines
            lines = lines[:max_lines] + [f"... (+{rest} more)"]
        return "\n".join(lines) if lines else "(none)"

    def fmt_entry(self, e: Dict[str, Any]) -> str:
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

    def build_pages(self, lines: List[str], per_page: int = 10) -> List[str]:
        pages: List[str] = []
        for i in range(0, len(lines), per_page):
            pages.append("\n".join(lines[i:i + per_page]))
        return pages or ["(no log)"]

    
    def npc_info_embed(self, npc_name: str, guild: Optional[discord.Guild]) -> discord.Embed:
        npc = self.cog._resolve_npc(npc_name) or NPCS[0]
        name, base_hp, tier, min_wildy, npc_type, atk_bonus, def_bonus = npc

        drops = (self.cog.config.get("npc_drops", {}) or {}).get(npc_type, {}) or {}
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
                    s = self.fmt_entry(e)
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

    
    async def afk_sweeper(self):
        try:
            while True:
                await asyncio.sleep(AFK_SWEEP_INTERVAL_SEC)
                if not self.cog._ready:
                    continue
                now = _now()
                to_tele: List[int] = []
                async with self.cog._mem_lock:
                    for uid, p in self.cog.players.items():
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
                    p = self.cog.players.get(uid)
                    if not p:
                        continue

                    duel = self.duel_active_for_user(uid)
                    if duel:
                        key = self.pair_key(duel.a_id, duel.b_id)
                        self.cog.duels_by_pair.pop(key, None)
                        if duel.channel_id:
                            self.cog.duels_by_channel.pop(duel.channel_id, None)

                        ch = self.cog.bot.get_channel(duel.channel_id) if duel.channel_id else None
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

                    p.wildy_run_id = int(p.wildy_run_id) + 1
                    p.ground_items = []
                    p.in_wilderness = False
                    p.skulled = False
                    p.wildy_level = 1
                    self.cog._full_heal(p)

                await self.cog._persist()

        except asyncio.CancelledError:
            return

    
    async def duel_action(
        self,
        interaction: discord.Interaction,
        duel: DuelState,
        action: str,
    ):
        from .ui_components import DuelView

        ch = interaction.channel
        if ch is None or ch.id not in self.cog.ALLOWED_CHANNEL_IDS:
            return

        async with self.cog._mem_lock:
            key = self.pair_key(duel.a_id, duel.b_id)
            if self.cog.duels_by_pair.get(key) is None:
                await interaction.response.send_message("This fight is no longer active.", ephemeral=True)
                return

            guild = interaction.guild
            if guild is None:
                await interaction.response.send_message("Fights only work in servers.", ephemeral=True)
                return

            a_member = guild.get_member(duel.a_id)
            b_member = guild.get_member(duel.b_id)
            if a_member is None or b_member is None:
                self.cog.duels_by_pair.pop(key, None)
                self.cog.duels_by_channel.pop(duel.channel_id, None)
                await interaction.response.send_message("A fighter is missing.", ephemeral=True)
                return

            pa = self.cog._get_player(a_member)
            pb = self.cog._get_player(b_member)

            self.cog._touch(pa)
            self.cog._touch(pb)

            if _now() - duel.started_at > int(self.cog.config["pvp_total_timeout_sec"]):
                self.cog.duels_by_pair.pop(key, None)
                self.cog.duels_by_channel.pop(duel.channel_id, None)
                await interaction.response.send_message("⏱️ Fight timed out.", ephemeral=False)
                return

            if interaction.user.id != duel.turn_id:
                await interaction.response.send_message("It's not your turn.", ephemeral=True)
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
                    self.hp_line_pvp(a_member.display_name, pa.hp, b_member.display_name, pb.hp)
                )

                if random.random() <= chance:
                    duel.log.append(f"✨ {attacker_member.display_name} teleports out! (**{int(chance*100)}%** roll)")
                    attacker.wildy_run_id = int(attacker.wildy_run_id) + 1
                    attacker.in_wilderness = False
                    attacker.skulled = False
                    attacker.wildy_level = 1
                    self.cog._full_heal(attacker)

                    await self.cog._persist()
                    self.cog.duels_by_pair.pop(key, None)
                    self.cog.duels_by_channel.pop(duel.channel_id, None)
                    await interaction.response.edit_message(
                        content=self.duel_render(duel, a_member, b_member, pa, pb, ended=True),
                        view=None
                    )
                    return
                else:
                    duel.log.append(f"🧊 Teleblock! {attacker_member.display_name} failed to teleport. (**{int(chance*100)}%** roll)")
                    duel.turn_id = defender_id
                    await self.cog._persist()
                    await interaction.response.edit_message(
                        content=self.duel_render(duel, a_member, b_member, pa, pb, ended=False),
                        view=DuelView(self.cog, duel)
                    )
                    return

            if action == "eat":
                food = self.cog._best_food_in_inventory(attacker)
                if not food:
                    await interaction.response.send_message("You have no food in your inventory.", ephemeral=True)
                    return
                heal = int(FOOD.get(food, {}).get("heal", 0))
                if heal <= 0:
                    await interaction.response.send_message("That food has no heal value.", ephemeral=True)
                    return
                if not self.cog._remove_item(attacker.inventory, food, 1):
                    await interaction.response.send_message("You have no food in your inventory.", ephemeral=True)
                    return
                before = attacker.hp
                attacker.hp = clamp(attacker.hp + heal, 0, int(self.cog.config["max_hp"]))
                mark_acted(attacker_id)
                duel.log.append(
                    self.hp_line_pvp(a_member.display_name, pa.hp, b_member.display_name, pb.hp)
                )
                duel.log.append(f"🍖 {attacker_member.display_name} eats and heals **{attacker.hp - before}**.")
                duel.turn_id = defender_id
                await self.cog._persist()
                await interaction.response.edit_message(
                    content=self.duel_render(duel, a_member, b_member, pa, pb, ended=False),
                    view=DuelView(self.cog, duel)
                )
                return

            if action == "hit":
                atk_bonus, _ = self.cog._equipped_bonus(attacker, vs_npc=False)
                _, def_bonus = self.cog._equipped_bonus(defender, vs_npc=False)
                atk_stat = 6 + atk_bonus + int(attacker.wildy_level / 12)
                def_stat = 5 + def_bonus + int(defender.wildy_level / 12)
                roll_a = random.randint(0, atk_stat)
                roll_d = random.randint(0, def_stat)
                hit = max(0, roll_a - roll_d)
                defender.hp = clamp(defender.hp - hit, 0, int(self.cog.config["max_hp"]))

                # Amulet of Seeping lifesteal (PvP)
                healed = self.cog._apply_seeping_heal(attacker, hit)
                if healed > 0:
                    duel.log.append(f"🩸 Amulet of Seeping heals **{healed}**.")

                mark_acted(attacker_id)

                duel.log.append(
                    self.hp_line_pvp(a_member.display_name, pa.hp, b_member.display_name, pb.hp)
                )
                duel.log.append(f"🗡️ {attacker_member.display_name} attacks and deals **{hit}**.")
                duel.log.extend(self.cog._consume_buffs_on_hit(attacker))

                if defender.hp <= 0:
                    lost_inv_snapshot = dict(defender.inventory)
                    lost_equip_snapshot = dict(defender.equipment)

                    duel.log.append(
                        self.hp_line_pvp(a_member.display_name, pa.hp, b_member.display_name, pb.hp)
                    )
                    duel.log.append(f"☠️ {defender_member.display_name} has been defeated!")

                    attacker.kills += 1
                    defender.deaths += 1

                    loot_lines = self.pvp_transfer_all_items(attacker, defender)
                    duel.log.extend(loot_lines[:6])

                    if lost_inv_snapshot or lost_equip_snapshot:
                        duel.log.append(f"📉 {defender_member.display_name} lost:")
                        if lost_inv_snapshot:
                            duel.log.append("• Inventory:")
                            for line in self.format_items_short(lost_inv_snapshot, max_lines=8).splitlines():
                                duel.log.append(f"  {line}")
                        else:
                            duel.log.append("• Inventory: (none)")
                        if lost_equip_snapshot:
                            duel.log.append("• Equipped:")
                            eq_lines = [f"- {slot}: {item}" for slot, item in sorted(lost_equip_snapshot.items())]
                            if len(eq_lines) > 8:
                                eq_lines = eq_lines[:8] + [f"... (+{len(lost_equip_snapshot)-8} more)"]
                            for line in eq_lines:
                                duel.log.append(f"  {line}")
                        else:
                            duel.log.append("• Equipped: (none)")

                    defender.hp = int(self.cog.config["starting_hp"])
                    defender.wildy_run_id = int(defender.wildy_run_id) + 1
                    defender.ground_items = []
                    defender.in_wilderness = False
                    defender.wildy_level = 1
                    defender.skulled = False
                    self.cog._full_heal(defender)

                    await self.cog._persist()
                    self.cog.duels_by_pair.pop(key, None)
                    self.cog.duels_by_channel.pop(duel.channel_id, None)
                    await interaction.response.edit_message(
                        content=self.duel_render(duel, a_member, b_member, pa, pb, ended=True),
                        view=None
                    )
                    return

                duel.turn_id = defender_id
                await self.cog._persist()
                await interaction.response.edit_message(
                    content=self.duel_render(duel, a_member, b_member, pa, pb, ended=False),
                    view=DuelView(self.cog, duel)
                )
                return

    
    def simulate_pvm_fight_and_loot(
        self,
        p: PlayerState,
        chosen_npc: Tuple[str, int, int, int, str, int, int],
        *,
        header_lines: Optional[List[str]] = None,
    ) -> Tuple[bool, str, List[str], Dict[str, int], int, List[str], List[Tuple[str, int, int]], Dict[str, int], List[Tuple[str, str, str]]]:
        """
        Returns:
        (won, npc_name, events, lost_items_on_death, bank_loss_on_death,
         loot_lines_on_win, ground_drops, eaten_food, broadcasts)
        broadcasts: [(drop_type, item_name, npc_name), ...] for unique/special/pet
        """
        npc_name, npc_hp, npc_tier, _, npc_type, npc_atk_bonus, npc_def_bonus = chosen_npc

        npc_hp += int(p.wildy_level / 8)
        npc_max = npc_hp

        npc_atk = 1 + npc_tier + npc_atk_bonus + int(p.wildy_level / 12)
        npc_def_stat = npc_tier + npc_def_bonus + int(p.wildy_level / 20)

        your_hp = p.hp
        start_hp = p.hp

        events: List[str] = []
        eaten_food: Dict[str, int] = {}

        if header_lines:
            events.extend(header_lines)

        events.append(f"👹 **{npc_name}** (HP **{npc_max}**) — You start **{start_hp}/{self.cog.config['max_hp']}**")

        force_zero_next_hit = False
        bleed_hits = 0

        while npc_hp > 0 and your_hp > 0:
            charged = False
            mainhand = p.equipment.get("mainhand", "")
            mh_meta = ITEMS.get(mainhand, {})
            if mh_meta.get("atk_vs_npc") and mainhand in ETHER_WEAPONS:
                if p.inventory.get("Revenant ether", 0) >= 3:
                    charged = True
                    self.cog._remove_item(p.inventory, "Revenant ether", 3)

            atk_bonus, def_bonus = self.cog._equipped_bonus(p, vs_npc=True, chainmace_charged=charged)
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

            # Wristwraps
            if p.equipment.get("gloves") == "Wristwraps of the Damned":
                if hit > 0 and random.random() < 0.05:
                    bleed_hits = 3
                    events.append("🩸 **Bleed inflicted!** Next 3 hits deal +2 damage.")

            if bleed_hits > 0 and hit > 0:
                bleed_hits -= 1
                hit += 2
                events.append(f"🩸 Bleed deals +2 damage. ({bleed_hits} hits remaining)")

            npc_hp = max(0, npc_hp - hit)
            events.append(f"🗡️ You hit **{hit}** | You: **{your_hp}/{self.cog.config['max_hp']}** | {npc_name}: **{npc_hp}/{npc_max}**")
            events.extend(self.cog._consume_buffs_on_hit(p))

            healed = self.cog._apply_seeping_heal(p, hit)
            if healed > 0:
                your_hp = int(p.hp)
                events.append(f"🩸 Amulet of Seeping heals **{healed}** | You: **{your_hp}/{self.cog.config['max_hp']}**")

            if npc_hp <= 0:
                break

            roll_na = random.randint(0, npc_atk)
            roll_nd = random.randint(0, your_def)
            npc_hit = max(0, roll_na - roll_nd)

            if npc_type in REVENANT_TYPES and p.equipment.get("amulet") == "Bracelet of ethereum":
                npc_hit = int(npc_hit * 0.5)

            your_hp = clamp(your_hp - npc_hit, 0, int(self.cog.config["max_hp"]))
            events.append(f"💥 {npc_name} hits **{npc_hit}** | You: **{your_hp}/{self.cog.config['max_hp']}** | {npc_name}: **{npc_hp}/{npc_max}**")

            if your_hp > 0:
                before = your_hp
                your_hp, ate_food, extra_roll, healed_amt = self.cog._maybe_auto_eat_after_hit(p, your_hp)
                if ate_food:
                    eaten_food[ate_food] = eaten_food.get(ate_food, 0) + 1
                    events.append(
                        f"🍖 Auto-eat **{ate_food}** (+{your_hp - before}) | You: **{your_hp}/{self.cog.config['max_hp']}**"
                    )

            # Zarveth 5% proc
            if npc_name == "Zarveth the Veilbreaker" and your_hp > 0 and npc_hp > 0:
                if random.random() < 0.05:
                    force_zero_next_hit = True
                    events.append("🌀 **Zarveth the Veilbreaker** shatters the veil! Your **next hit will deal 0**.")

        if your_hp <= 0:
            lost_items = dict(p.inventory)
            p.inventory.clear()

            bank_loss = int(p.bank_coins * 0.10)
            if bank_loss > 0:
                p.bank_coins -= bank_loss

            return False, npc_name, events, lost_items, bank_loss, [], [], eaten_food, []

        p.kills += 1
        p.npc_kills[npc_name] = p.npc_kills.get(npc_name, 0) + 1
        p.hp = your_hp

        loot_lines: List[str] = []
        auto_drops: Dict[str, int] = {}
        ground_drops: List[Tuple[str, int, int]] = []  # (item, qty, run_id)
        broadcasts: List[Tuple[str, str, str]] = []  # (drop_type, item, npc_name)

        max_items = 3
        items_dropped = 0

        coins = self.cog._npc_coin_roll(npc_type)
        if coins > 0:
            p.coins += coins
            loot_lines.append(f"🪙 Coins: **+{coins}**")
        else:
            loot_lines.append("🪙 Coins: **+0**")

        def can_drop() -> bool:
            return items_dropped < max_items

        if can_drop():
            w_roll = self.cog._loot_for_level(p.wildy_level)
            if w_roll:
                item, qty = w_roll
                dest, on_ground = self.cog._try_put_item_or_ground_with_blacklist(p, item, qty, auto_drops)
                loot_lines.append(f"🎁 Wildy loot: **{item} x{qty}** {dest}".rstrip())
                if on_ground > 0:
                    ground_drops.append((item, on_ground, int(p.wildy_run_id)))
                items_dropped += 1

        if can_drop():
            npc_loot = self.cog._npc_roll_table(npc_type, "loot")
            if npc_loot:
                item, qty = npc_loot
                dest, on_ground = self.cog._try_put_item_or_ground_with_blacklist(p, item, qty, auto_drops)
                loot_lines.append(f"👹 {npc_name} loot: **{item} x{qty}** {dest}".rstrip())
                if on_ground > 0:
                    ground_drops.append((item, on_ground, int(p.wildy_run_id)))
                items_dropped += 1

        if can_drop():
            npc_unique = self.cog._npc_roll_table_for_player(p, npc_type, "unique")
            if npc_unique:
                item, qty = npc_unique
                dest, on_ground = self.cog._try_put_item_or_ground_with_blacklist(p, item, qty, auto_drops)

                if not self.cog._is_blacklisted(p, item):
                    p.uniques[item] = p.uniques.get(item, 0) + qty
                    p.unique_drops += 1

                loot_lines.append(f"✨ UNIQUE: **{item} x{qty}** {dest}".rstrip())
                if on_ground > 0:
                    ground_drops.append((item, on_ground, int(p.wildy_run_id)))
                items_dropped += 1
                broadcasts.append(("Unique", item, npc_name))

        if can_drop():
            npc_special = self.cog._npc_roll_table(npc_type, "special")
            if npc_special:
                item, qty = npc_special
                if self.cog._is_blacklisted(p, item):
                    self.cog._record_autodrop(auto_drops, item, qty)
                    loot_lines.append(f"🩸 SPECIAL: **{item} x{qty}** (blacklisted - dropped)")
                else:
                    dest, on_ground = self.cog._try_put_item_or_ground(p, item, qty)
                    loot_lines.append(f"🩸 SPECIAL: **{item} x{qty}** {dest}".rstrip())
                    if on_ground > 0:
                        ground_drops.append((item, on_ground, int(p.wildy_run_id)))
                broadcasts.append(("Special", item, npc_name))
                items_dropped += 1

        pet = self.cog._npc_roll_pet(npc_type)
        if pet:
            if pet not in p.pets:
                p.pets.append(pet)
                p.pet_drops += 1
            loot_lines.append(f"🐾 PET: **{pet}**")
            broadcasts.append(("Pet", pet, npc_name))

        if auto_drops:
            loot_lines.append("🗑️ Auto-dropped (blacklist):")
            for name, q in sorted(auto_drops.items(), key=lambda x: x[0].lower()):
                loot_lines.append(f"- {name} x{q}")

        now = _now()
        for item, qty, _rid in ground_drops:
            if qty > 0:
                p.ground_items.append([item, qty, now])

        g_lines = self.ground_drop_lines(ground_drops)
        if g_lines:
            loot_lines.append("")
            loot_lines.extend(g_lines)

        food_lines = self.food_summary_lines(eaten_food, p.inventory)
        if food_lines:
            loot_lines.append("")
            loot_lines.extend(food_lines)

        return True, npc_name, events, {}, 0, loot_lines, ground_drops, eaten_food, broadcasts
