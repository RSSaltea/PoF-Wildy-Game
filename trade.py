from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple, List, FrozenSet, Any

import discord


def _now() -> int:
    return int(time.time())


@dataclass
class TradeOffer:
    items: Dict[str, int] = field(default_factory=dict)
    coins: int = 0


@dataclass
class TradeState:
    a_id: int
    b_id: int
    channel_id: int
    created_at: int

    status: str = "pending"  # pending | active | done | cancelled
    request_message_id: Optional[int] = None
    trade_message_id: Optional[int] = None

    a_confirmed: bool = False
    b_confirmed: bool = False

    offers: Dict[int, TradeOffer] = field(default_factory=dict)

    request_timeout_task: Optional[asyncio.Task] = None


class TradeView(discord.ui.View):
    def __init__(self, manager: "TradeManager", trade_key: FrozenSet[int], *, timeout: float = 600):
        super().__init__(timeout=timeout)
        self.manager = manager
        self.trade_key = trade_key

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        trade = self.manager.trades_by_pair.get(self.trade_key)
        if not trade or trade.status != "active":
            try:
                await interaction.response.send_message("This trade is no longer active.", ephemeral=True)
            except Exception:
                pass
            return False

        if interaction.user.id not in (trade.a_id, trade.b_id):
            await interaction.response.send_message("You are not part of this trade.", ephemeral=True)
            return False

        if interaction.channel is None or getattr(interaction.channel, "id", None) != trade.channel_id:
            await interaction.response.send_message("Wrong channel for this trade.", ephemeral=True)
            return False

        return True

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success)
    async def confirm_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.manager.on_confirm_pressed(interaction, self.trade_key)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.manager.on_cancel_pressed(interaction, self.trade_key)

    async def on_timeout(self):
        try:
            await self.manager.cancel_trade(self.trade_key, reason="⏳ Trade timed out.")
        except Exception:
            pass


class TradeManager:

    def __init__(self, cog: Any, *, allowed_channel_ids: Optional[set[int]] = None):
        self.cog = cog

        if allowed_channel_ids is not None:
            self.allowed_channel_ids: set[int] = set(allowed_channel_ids)
        else:
            self.allowed_channel_ids = set(getattr(cog, "ALLOWED_CHANNEL_IDS", set()))

        self.trades_by_pair: Dict[FrozenSet[int], TradeState] = {}
        self.trades_by_user: Dict[int, FrozenSet[int]] = {}

    async def start_trade_request(self, ctx, target) -> None:
        ch = getattr(ctx, "channel", None)
        if ch is None or getattr(ch, "id", None) not in self.allowed_channel_ids:
            return

        if target.bot or target.id == ctx.author.id:
            await ctx.reply("Pick a real person (not yourself, not a bot).")
            return

        async with self.cog._mem_lock:
            a = self.cog._get_player(ctx.author)
            b = self.cog._get_player(target)

            if a.in_wilderness or b.in_wilderness:
                await ctx.reply("Trades can only be started **out of the Wilderness**.")
                return

            if self._user_in_trade(ctx.author.id) or self._user_in_trade(target.id):
                await ctx.reply("One of you is already in a trade.")
                return

            if getattr(self.cog, "_duel_active_for_user", None):
                if self.cog._duel_active_for_user(ctx.author.id) or self.cog._duel_active_for_user(target.id):
                    await ctx.reply("Finish your PvP fight before trading.")
                    return

            key: FrozenSet[int] = frozenset({ctx.author.id, target.id})
            trade = TradeState(
                a_id=ctx.author.id,
                b_id=target.id,
                channel_id=ch.id,
                created_at=_now(),
                offers={
                    ctx.author.id: TradeOffer(),
                    target.id: TradeOffer(),
                },
            )
            self.trades_by_pair[key] = trade
            self.trades_by_user[ctx.author.id] = key
            self.trades_by_user[target.id] = key

        msg = await ctx.reply(
            f"🤝 **Trade request**: {ctx.author.mention} wants to trade with {target.mention}\n"
            f"{target.mention}, type `!w trade accept` within **30s**."
        )

        async with self.cog._mem_lock:
            trade = self.trades_by_pair.get(key)
            if not trade or trade.status != "pending":
                return
            trade.request_message_id = msg.id
            trade.request_timeout_task = asyncio.create_task(self._auto_deny_after_30s(key, msg))

    async def accept_trade(self, ctx) -> None:
        ch = getattr(ctx, "channel", None)
        if ch is None:
            return

        async with self.cog._mem_lock:
            key = self.trades_by_user.get(ctx.author.id)
            if not key:
                await ctx.reply("You have no pending trade to accept.")
                return

            trade = self.trades_by_pair.get(key)
            if not trade or trade.status != "pending":
                await ctx.reply("You have no pending trade to accept.")
                return

            if ctx.author.id != trade.b_id:
                await ctx.reply("Only the **trade target** can accept. (The other person started it.)")
                return

            if getattr(ch, "id", None) != trade.channel_id:
                await ctx.reply("Accept the trade in the same channel it was started in.")
                return

            if trade.request_timeout_task and not trade.request_timeout_task.done():
                trade.request_timeout_task.cancel()

            trade.status = "active"

        await self._edit_request_message(trade, content="✅ Trade accepted! Opening trade window…")

        emb = await self._render_trade_embed(ctx.guild, trade)
        view = TradeView(self, key, timeout=600)

        trade_msg = await ctx.reply(embed=emb, view=view)

        async with self.cog._mem_lock:
            trade = self.trades_by_pair.get(key)
            if trade and trade.status == "active":
                trade.trade_message_id = trade_msg.id

    async def add_to_trade(self, ctx, qty: int, itemname: str) -> None:
        await self._mutate_offer(ctx, qty, itemname, mode="add")

    async def remove_from_trade(self, ctx, qty: int, itemname: str) -> None:
        await self._mutate_offer(ctx, qty, itemname, mode="remove")

    async def cancel_trade_by_command(self, ctx) -> None:
        async with self.cog._mem_lock:
            key = self.trades_by_user.get(ctx.author.id)
        if not key:
            await ctx.reply("You are not in a trade.")
            return
        await self.cancel_trade(key, reason="❌ Trade cancelled.")

    async def on_confirm_pressed(self, interaction: discord.Interaction, trade_key: FrozenSet[int]):
        async with self.cog._mem_lock:
            trade = self.trades_by_pair.get(trade_key)
            if not trade or trade.status != "active":
                await self._safe_ephemeral(interaction, "This trade is no longer active.")
                return

            uid = interaction.user.id
            if uid == trade.a_id:
                trade.a_confirmed = True
            elif uid == trade.b_id:
                trade.b_confirmed = True
            else:
                await self._safe_ephemeral(interaction, "You are not part of this trade.")
                return

            if trade.a_confirmed and trade.b_confirmed:
                ok, err = self._try_complete_trade_locked(trade)
                if not ok:
                    trade.a_confirmed = False
                    trade.b_confirmed = False
                    emb = await self._render_trade_embed(interaction.guild, trade, footer_override=f"⚠️ {err}")
                    await self._safe_edit(interaction, embed=emb, view=TradeView(self, trade_key, timeout=600))
                    return

                trade.status = "done"
                await self.cog._persist()

                done_emb = await self._render_trade_embed(interaction.guild, trade, footer_override="✅ Trade completed!")
                await self._safe_edit(interaction, embed=done_emb, view=None)

                self._cleanup_trade_locked(trade_key)
                return

            emb = await self._render_trade_embed(interaction.guild, trade)

        await self._safe_edit(interaction, embed=emb, view=TradeView(self, trade_key, timeout=600))

    async def on_cancel_pressed(self, interaction: discord.Interaction, trade_key: FrozenSet[int]):
        try:
            await interaction.response.defer()
        except Exception:
            pass

        await self.cancel_trade(trade_key, reason="❌ Trade cancelled.")

        try:
            await interaction.edit_original_response(view=None)
        except Exception:
            pass

    def _user_in_trade(self, uid: int) -> bool:
        key = self.trades_by_user.get(uid)
        if not key:
            return False
        t = self.trades_by_pair.get(key)
        return bool(t and t.status in ("pending", "active"))

    async def _auto_deny_after_30s(self, key: FrozenSet[int], request_msg: discord.Message):
        try:
            await asyncio.sleep(30)
        except asyncio.CancelledError:
            return

        async with self.cog._mem_lock:
            trade = self.trades_by_pair.get(key)
            if not trade or trade.status != "pending":
                return
            trade.status = "cancelled"

        try:
            await request_msg.edit(content="⌛ Trade request expired (no accept within 30s).")
        except Exception:
            pass

        async with self.cog._mem_lock:
            self._cleanup_trade_locked(key)

    async def _edit_request_message(self, trade: TradeState, *, content: str):
        if not trade.request_message_id:
            return
        ch = self.cog.bot.get_channel(trade.channel_id)
        if not isinstance(ch, discord.abc.Messageable):
            return
        try:
            msg = await ch.fetch_message(trade.request_message_id)
            await msg.edit(content=content)
        except Exception:
            pass

    async def cancel_trade(self, key: FrozenSet[int], *, reason: str):
        async with self.cog._mem_lock:
            trade = self.trades_by_pair.get(key)
            if not trade or trade.status not in ("pending", "active"):
                self._cleanup_trade_locked(key)
                return
            trade.status = "cancelled"
            if trade.request_timeout_task and not trade.request_timeout_task.done():
                trade.request_timeout_task.cancel()

        await self._edit_request_message(trade, content=reason)

        if trade.trade_message_id:
            ch = self.cog.bot.get_channel(trade.channel_id)
            if isinstance(ch, discord.abc.Messageable):
                try:
                    msg = await ch.fetch_message(trade.trade_message_id)
                    emb = await self._render_trade_embed(getattr(msg, "guild", None), trade, footer_override=reason)
                    await msg.edit(embed=emb, view=None)
                except Exception:
                    pass

        async with self.cog._mem_lock:
            self._cleanup_trade_locked(key)

    async def _mutate_offer(self, ctx, qty: int, itemname: str, *, mode: str):
        if qty <= 0:
            await ctx.reply("Quantity must be > 0.")
            return

        ch = getattr(ctx, "channel", None)
        if ch is None:
            return

        async with self.cog._mem_lock:
            key = self.trades_by_user.get(ctx.author.id)
            if not key:
                await ctx.reply("You are not in an active trade.")
                return
            trade = self.trades_by_pair.get(key)
            if not trade or trade.status != "active":
                await ctx.reply("You are not in an active trade.")
                return
            if getattr(ch, "id", None) != trade.channel_id:
                await ctx.reply("Use trade commands in the same channel as the trade window.")
                return

            is_coins, canonical_item = self._resolve_trade_asset(ctx.author, itemname)
            if not is_coins and not canonical_item:
                await ctx.reply("Unknown item. Try `!w inspect <itemname>` to check names/aliases.")
                return

            offer = trade.offers.get(ctx.author.id) or TradeOffer()
            trade.offers[ctx.author.id] = offer

            trade.a_confirmed = False
            trade.b_confirmed = False

            p = self.cog._get_player(ctx.author)

            if is_coins:
                total_coins = int(p.coins) + int(getattr(p, "bank_coins", 0))

                if mode == "add":
                    if total_coins < (offer.coins + qty):
                        await ctx.reply(
                            f"You only have **{total_coins:,}** total coins "
                            f"(inv {int(p.coins):,} + bank {int(getattr(p, 'bank_coins', 0)):,})."
                        )
                        return
                    offer.coins += qty
                else:
                    if offer.coins < qty:
                        await ctx.reply("You haven't offered that many coins.")
                        return
                    offer.coins = max(0, offer.coins - qty)

            else:
                have_inv = int(p.inventory.get(canonical_item, 0))
                have_bank = int(p.bank.get(canonical_item, 0))
                have_total = have_inv + have_bank

                cur = int(offer.items.get(canonical_item, 0))

                if mode == "add":
                    if have_total < (cur + qty):
                        await ctx.reply(
                            f"You only have **{have_total}** of **{canonical_item}** "
                            f"(inv {have_inv}, bank {have_bank})."
                        )
                        return
                    offer.items[canonical_item] = cur + qty
                else:
                    if cur < qty:
                        await ctx.reply("You haven't offered that many of that item.")
                        return
                    newv = cur - qty
                    if newv <= 0:
                        offer.items.pop(canonical_item, None)
                    else:
                        offer.items[canonical_item] = newv

        await self._update_trade_message(key)

    async def _update_trade_message(self, key: FrozenSet[int], *, footer_override: Optional[str] = None):
        async with self.cog._mem_lock:
            trade = self.trades_by_pair.get(key)
            if not trade or trade.status != "active":
                return
            msg_id = trade.trade_message_id
            channel_id = trade.channel_id

        if not msg_id:
            return

        ch = self.cog.bot.get_channel(channel_id)
        if not isinstance(ch, discord.abc.Messageable):
            return
        try:
            msg = await ch.fetch_message(msg_id)
        except Exception:
            return

        async with self.cog._mem_lock:
            trade = self.trades_by_pair.get(key)
            if not trade or trade.status != "active":
                return
            emb = await self._render_trade_embed(getattr(msg, "guild", None), trade, footer_override=footer_override)

        try:
            await msg.edit(embed=emb, view=TradeView(self, key, timeout=600))
        except Exception:
            pass

    def _resolve_trade_asset(self, user, itemname: str) -> Tuple[bool, Optional[str]]:
        """Return (is_coins, canonical_item_name), resolving aliases, food, inventory and bank keys."""
        q = self.cog._norm(itemname)
        coins_name = self.cog._norm(self.cog.config.get("coins_item_name", "Coins"))

        if q in ("coins", "coin") or q == coins_name:
            return True, None

        canonical = self.cog._resolve_item(itemname)
        if canonical:
            return False, canonical

        food_key = self.cog._resolve_food(itemname)
        if food_key:
            return False, food_key

        p = self.cog._get_player(user)

        inv_key = self.cog._resolve_from_keys_case_insensitive(itemname, p.inventory.keys())
        if inv_key:
            return False, inv_key

        bank_key = self.cog._resolve_from_keys_case_insensitive(itemname, p.bank.keys())
        if bank_key:
            return False, bank_key

        return False, None

    async def _render_trade_embed(self, guild, trade: TradeState, *, footer_override: Optional[str] = None) -> discord.Embed:
        a_name = f"<@{trade.a_id}>"
        b_name = f"<@{trade.b_id}>"
        if guild:
            ma = guild.get_member(trade.a_id)
            mb = guild.get_member(trade.b_id)
            if ma:
                a_name = ma.display_name
            if mb:
                b_name = mb.display_name

        a_offer = trade.offers.get(trade.a_id) or TradeOffer()
        b_offer = trade.offers.get(trade.b_id) or TradeOffer()

        def fmt_offer(of: TradeOffer) -> str:
            lines: List[str] = []
            if of.coins > 0:
                lines.append(f"🪙 Coins: **{of.coins:,}**")
            for item, qty in sorted(of.items.items(), key=lambda x: x[0].lower()):
                lines.append(f"• {item} x{qty}")
            return "\n".join(lines) if lines else "(nothing)"

        a_ok = "✅" if trade.a_confirmed else "❌"
        b_ok = "✅" if trade.b_confirmed else "❌"

        emb = discord.Embed(
            title="🤝 Trade Window",
            description=(
                f"**{a_name}** confirmed: {a_ok}\n"
                f"**{b_name}** confirmed: {b_ok}\n\n"
                f"Use `!w trade add <qty> <item>` / `!w trade remove <qty> <item>` (inv+bank).\n"
                f"On completion, received items are deposited into your **bank**.\n"
                f"Click **Confirm** when ready. Either player can **Cancel**."
            ),
        )
        emb.add_field(name=f"{a_name} offers", value=fmt_offer(a_offer), inline=True)
        emb.add_field(name=f"{b_name} offers", value=fmt_offer(b_offer), inline=True)

        if footer_override:
            emb.set_footer(text=footer_override)
        elif trade.status == "active":
            emb.set_footer(text="Trade is active.")
        elif trade.status == "done":
            emb.set_footer(text="✅ Trade completed!")
        elif trade.status == "cancelled":
            emb.set_footer(text="❌ Trade cancelled.")
        else:
            emb.set_footer(text=f"Status: {trade.status}")

        return emb

    def _try_complete_trade_locked(self, trade: TradeState) -> Tuple[bool, str]:
        """Execute the trade, drawing from both inventory and bank; received items go to bank."""
        a_id, b_id = trade.a_id, trade.b_id
        a_offer = trade.offers.get(a_id) or TradeOffer()
        b_offer = trade.offers.get(b_id) or TradeOffer()

        a_user = self.cog.bot.get_user(a_id) or discord.Object(id=a_id)
        b_user = self.cog.bot.get_user(b_id) or discord.Object(id=b_id)
        pa = self.cog._get_player(a_user)
        pb = self.cog._get_player(b_user)

        a_total_coins = int(pa.coins) + int(getattr(pa, "bank_coins", 0))
        b_total_coins = int(pb.coins) + int(getattr(pb, "bank_coins", 0))
        if a_total_coins < int(a_offer.coins):
            return False, "Player A no longer has the offered coins (inv+bank)."
        if b_total_coins < int(b_offer.coins):
            return False, "Player B no longer has the offered coins (inv+bank)."

        def split_outgoing(
            inv: Dict[str, int],
            bank: Dict[str, int],
            outgoing: Dict[str, int],
        ) -> Tuple[Optional[Dict[str, int]], Optional[Dict[str, int]]]:
            take_inv: Dict[str, int] = {}
            take_bank: Dict[str, int] = {}
            for item, qty in outgoing.items():
                qty = int(qty)
                if qty <= 0:
                    continue
                inv_have = int(inv.get(item, 0))
                bank_have = int(bank.get(item, 0))
                if inv_have + bank_have < qty:
                    return None, None
                inv_take = min(inv_have, qty)
                bank_take = qty - inv_take
                if inv_take:
                    take_inv[item] = inv_take
                if bank_take:
                    take_bank[item] = bank_take
            return take_inv, take_bank

        a_take_inv, a_take_bank = split_outgoing(pa.inventory, pa.bank, a_offer.items)
        if a_take_inv is None:
            for item, qty in a_offer.items.items():
                if int(pa.inventory.get(item, 0)) + int(pa.bank.get(item, 0)) < int(qty):
                    return False, f"Player A no longer has {item} x{int(qty)} (inv+bank)."
            return False, "Player A no longer has the offered items (inv+bank)."

        b_take_inv, b_take_bank = split_outgoing(pb.inventory, pb.bank, b_offer.items)
        if b_take_inv is None:
            for item, qty in b_offer.items.items():
                if int(pb.inventory.get(item, 0)) + int(pb.bank.get(item, 0)) < int(qty):
                    return False, f"Player B no longer has {item} x{int(qty)} (inv+bank)."
            return False, "Player B no longer has the offered items (inv+bank)."

        for item in b_offer.items:
            if self.cog._player_owns_esspouch(pa, item):
                return False, f"Player A already owns **{item}** — cannot receive another."
        for item in a_offer.items:
            if self.cog._player_owns_esspouch(pb, item):
                return False, f"Player B already owns **{item}** — cannot receive another."

        for item, qty in a_take_inv.items():
            if not self.cog._remove_item(pa.inventory, item, int(qty)):
                return False, "Failed to remove an item from Player A inventory (state changed)."
        for item, qty in a_take_bank.items():
            if not self.cog._remove_item(pa.bank, item, int(qty)):
                return False, "Failed to remove an item from Player A bank (state changed)."

        for item, qty in b_take_inv.items():
            if not self.cog._remove_item(pb.inventory, item, int(qty)):
                return False, "Failed to remove an item from Player B inventory (state changed)."
        for item, qty in b_take_bank.items():
            if not self.cog._remove_item(pb.bank, item, int(qty)):
                return False, "Failed to remove an item from Player B bank (state changed)."

        if int(a_offer.coins) > 0:
            if not self.cog._spend_coins(pa, int(a_offer.coins)):
                return False, "Player A no longer has the offered coins (state changed)."
        if int(b_offer.coins) > 0:
            if not self.cog._spend_coins(pb, int(b_offer.coins)):
                return False, "Player B no longer has the offered coins (state changed)."

        for item, qty in b_offer.items.items():
            self.cog._add_item(pa.bank, item, int(qty))
        for item, qty in a_offer.items.items():
            self.cog._add_item(pb.bank, item, int(qty))

        pa.bank_coins = int(getattr(pa, "bank_coins", 0)) + int(b_offer.coins)
        pb.bank_coins = int(getattr(pb, "bank_coins", 0)) + int(a_offer.coins)

        return True, ""

    def _cleanup_trade_locked(self, key: FrozenSet[int]):
        trade = self.trades_by_pair.pop(key, None)
        if not trade:
            return
        self.trades_by_user.pop(trade.a_id, None)
        self.trades_by_user.pop(trade.b_id, None)

    async def _safe_ephemeral(self, interaction: discord.Interaction, msg: str):
        try:
            if interaction.response.is_done():
                await interaction.followup.send(msg, ephemeral=True)
            else:
                await interaction.response.send_message(msg, ephemeral=True)
        except Exception:
            pass

    async def _safe_edit(self, interaction: discord.Interaction, *, embed: discord.Embed, view: Optional[discord.ui.View]):
        """Safely edit the message the button interaction came from."""
        try:
            if interaction.response.is_done():
                await interaction.edit_original_response(embed=embed, view=view)
            else:
                await interaction.response.edit_message(embed=embed, view=view)
        except Exception:
            try:
                if interaction.message:
                    await interaction.message.edit(embed=embed, view=view)
            except Exception:
                pass