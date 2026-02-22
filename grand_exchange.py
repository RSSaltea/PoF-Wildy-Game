"""Grand Exchange — player-to-player buy/sell offer system."""

from __future__ import annotations

import asyncio
import json
import os
import time
from dataclasses import dataclass, asdict
from typing import Optional, List, Tuple, TYPE_CHECKING

import discord

from .items import ITEMS, FOOD, UNTRADEABLE

if TYPE_CHECKING:
    from .wilderness import Wilderness

DATA_DIR = "data/wilderness"
GE_FILE = os.path.join(DATA_DIR, "ge_offers.json")
MAX_SLOTS = 4


def _now() -> int:
    return int(time.time())


# ═══════════════════════════════════════════════════════════════════
#  Item Categories for Select Menus
# ═══════════════════════════════════════════════════════════════════

_GEM_NAMES = {
    "Uncut sapphire", "Uncut emerald", "Uncut ruby", "Uncut diamond",
    "Uncut dragonstone", "Sapphire", "Emerald", "Ruby", "Diamond",
    "Dragonstone", "Omnigem", "Omnigem Amulet",
}


def _build_ge_categories():
    melee, ranged, magic, necro = [], [], [], []
    bodies, legwear, helms = [], [], []
    boots, gloves, accessories = [], [], []
    runes, ammo_list = [], []
    potions, gems, materials = [], [], []

    _style_buckets = {
        "melee": melee, "range": ranged, "magic": magic, "necro": necro,
    }

    for name, meta in ITEMS.items():
        if name in UNTRADEABLE:
            continue
        itype = meta.get("type", "misc").split(",")[0].strip()
        style = meta.get("style", "")

        if itype == "mainhand":
            _style_buckets.get(style, melee).append(name)
        elif itype == "offhand":
            # Put offhands into their respective style category
            _style_buckets.get(style, melee).append(name)
        elif itype == "body":
            bodies.append(name)
        elif itype == "legs":
            legwear.append(name)
        elif itype == "helm":
            helms.append(name)
        elif itype == "boots":
            boots.append(name)
        elif itype == "gloves":
            gloves.append(name)
        elif itype in ("amulet", "ring", "cape"):
            accessories.append(name)
        elif itype == "rune":
            runes.append(name)
        elif itype == "ammo":
            ammo_list.append(name)
        elif itype == "misc":
            if "(" in name and ")" in name:
                potions.append(name)
            elif name in _GEM_NAMES:
                gems.append(name)
            elif meta.get("value", 1) == 0:
                pass  # pets are untradeable
            else:
                materials.append(name)

    food_list = list(FOOD.keys())

    cats = {}
    for label, items in [
        ("\u2694\ufe0f Melee Weapons", melee),
        ("\U0001f3f9 Range Weapons", ranged),
        ("\U0001fa84 Magic Weapons", magic),
        ("\U0001f480 Necro Weapons", necro),
        ("\U0001f9ba Body Armour", bodies),
        ("\U0001f456 Leg Armour", legwear),
        ("\u26d1\ufe0f Helmets", helms),
        ("\U0001f97e Boots & Gloves", boots + gloves),
        ("\U0001f48d Accessories", accessories),
        ("\u2728 Runes", runes),
        ("\U0001f3af Ammunition", ammo_list),
        ("\U0001f356 Food & Potions", food_list + potions),
        ("\U0001f4a0 Gems", gems),
        ("\U0001f4e6 Materials & Keys", materials),
    ]:
        if items:
            cats[label] = items
    return cats


GE_CATEGORIES = _build_ge_categories()


# ═══════════════════════════════════════════════════════════════════
#  Data Model
# ═══════════════════════════════════════════════════════════════════

@dataclass
class GEOffer:
    offer_id: int
    user_id: int
    offer_type: str       # "buy" | "sell"
    item: str             # canonical item name
    price_each: int       # coins per item
    quantity: int          # total wanted / offered
    filled: int = 0       # how many matched so far
    claimed: int = 0      # how many fills the player has claimed
    coins_pending: int = 0  # coins waiting to be claimed (refunds / earnings)
    created_at: int = 0
    slot: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "GEOffer":
        allowed = set(GEOffer.__dataclass_fields__.keys())
        return GEOffer(**{k: v for k, v in d.items() if k in allowed})

    @property
    def claimable_items(self) -> int:
        return max(0, self.filled - self.claimed)

    @property
    def has_claimable(self) -> bool:
        return self.claimable_items > 0 or self.coins_pending > 0

    @property
    def remaining(self) -> int:
        return max(0, self.quantity - self.filled)

    @property
    def is_complete(self) -> bool:
        return self.filled >= self.quantity

    @property
    def progress_pct(self) -> int:
        if self.quantity <= 0:
            return 100
        return int(self.filled / self.quantity * 100)

    def progress_bar(self, length: int = 10) -> str:
        if self.quantity <= 0:
            return "🟩" * length
        filled_blocks = round(self.filled / self.quantity * length)
        filled_blocks = min(filled_blocks, length)
        if self.is_complete:
            return "🟩" * length
        if self.filled > 0:
            amber = max(1, filled_blocks)  # at least 1 block to show progress
            return "🟨" * amber + "⬛" * (length - amber)
        return "⬛" * length


# ═══════════════════════════════════════════════════════════════════
#  Manager  (persistence · CRUD · matching engine)
# ═══════════════════════════════════════════════════════════════════

class GEManager:

    def __init__(self, cog: "Wilderness"):
        self.cog = cog
        self.offers: List[GEOffer] = []
        self.next_id: int = 1
        self._lock = asyncio.Lock()

    # ── Persistence ────────────────────────────────────────────────

    async def load(self):
        if not os.path.exists(GE_FILE):
            return
        def _read():
            with open(GE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        data = await asyncio.to_thread(_read)
        self.next_id = data.get("next_id", 1)
        self.offers = [GEOffer.from_dict(d) for d in data.get("offers", [])]

    async def save(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        data = {
            "next_id": self.next_id,
            "offers": [o.to_dict() for o in self.offers],
        }
        def _write():
            tmp = GE_FILE + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(tmp, GE_FILE)
        await asyncio.to_thread(_write)

    # ── Queries ────────────────────────────────────────────────────

    def player_slots(self, user_id: int) -> List[Optional[GEOffer]]:
        """Return the player's 4 GE slots (None = empty)."""
        slots: List[Optional[GEOffer]] = [None] * MAX_SLOTS
        for o in self.offers:
            if o.user_id == user_id and 0 <= o.slot < MAX_SLOTS:
                slots[o.slot] = o
        return slots

    # ── CRUD ───────────────────────────────────────────────────────

    async def create_offer(
        self, user_id: int, slot: int, offer_type: str,
        item: str, quantity: int, price_each: int,
    ) -> Tuple[bool, str]:
        if item in UNTRADEABLE:
            return False, f"**{item}** is untradeable."
        async with self._lock:
            slots = self.player_slots(user_id)
            if slots[slot] is not None:
                return False, "That slot is already in use."

            user_obj = self.cog.bot.get_user(user_id) or discord.Object(id=user_id)

            async with self.cog._mem_lock:
                p = self.cog._get_player(user_obj)

                if offer_type == "buy":
                    cost = price_each * quantity
                    if int(p.bank_coins) < cost:
                        return False, (
                            f"Not enough coins in bank.\n"
                            f"Need **{cost:,}** GP, you have **{int(p.bank_coins):,}** GP."
                        )
                    p.bank_coins = int(p.bank_coins) - cost
                else:  # sell
                    have = int(p.bank.get(item, 0))
                    if have < quantity:
                        return False, (
                            f"Not enough **{item}** in bank.\n"
                            f"Need **{quantity}**, you have **{have}**."
                        )
                    self.cog._remove_item(p.bank, item, quantity)

                await self.cog._persist()

            offer = GEOffer(
                offer_id=self.next_id,
                user_id=user_id,
                offer_type=offer_type,
                item=item,
                price_each=price_each,
                quantity=quantity,
                created_at=_now(),
                slot=slot,
            )
            self.next_id += 1
            self.offers.append(offer)

            await self._match_offer(offer)
            await self.save()

            status = "completed instantly" if offer.is_complete else "placed"
            return True, (
                f"{'Buy' if offer_type == 'buy' else 'Sell'} offer {status}: "
                f"**{quantity}x {item}** @ **{price_each:,}** GP each."
            )

    async def claim_offer(self, user_id: int, slot: int) -> Tuple[bool, str]:
        """Withdraw filled items/coins without closing the offer."""
        async with self._lock:
            slots = self.player_slots(user_id)
            offer = slots[slot]
            if offer is None:
                return False, "No offer in that slot."

            items_to_claim = offer.claimable_items
            coins_to_claim = offer.coins_pending

            if items_to_claim <= 0 and coins_to_claim <= 0:
                return False, "Nothing to claim."

            user_obj = self.cog.bot.get_user(user_id) or discord.Object(id=user_id)

            async with self.cog._mem_lock:
                p = self.cog._get_player(user_obj)

                if offer.offer_type == "buy":
                    if items_to_claim > 0:
                        self.cog._add_item(p.bank, offer.item, items_to_claim)
                    if coins_to_claim > 0:
                        p.bank_coins = int(p.bank_coins) + coins_to_claim
                else:  # sell
                    if coins_to_claim > 0:
                        p.bank_coins = int(p.bank_coins) + coins_to_claim

                await self.cog._persist()

            offer.claimed = offer.filled
            offer.coins_pending = 0
            await self.save()

            parts = []
            if offer.offer_type == "buy":
                if items_to_claim > 0:
                    parts.append(f"**{items_to_claim}x {offer.item}**")
                if coins_to_claim > 0:
                    parts.append(f"**{coins_to_claim:,}** GP refund")
            else:
                if coins_to_claim > 0:
                    parts.append(f"**{coins_to_claim:,}** GP")

            return True, f"Claimed {', '.join(parts)} → bank."

    async def claim_all(self, user_id: int) -> Tuple[bool, str]:
        """Claim all pending items/coins across every slot."""
        async with self._lock:
            slots = self.player_slots(user_id)
            total_items: dict = {}
            total_coins = 0

            for offer in slots:
                if offer is None or not offer.has_claimable:
                    continue
                if offer.offer_type == "buy":
                    ci = offer.claimable_items
                    if ci > 0:
                        total_items[offer.item] = total_items.get(offer.item, 0) + ci
                    total_coins += offer.coins_pending
                else:
                    total_coins += offer.coins_pending

            if not total_items and total_coins <= 0:
                return False, "Nothing to claim."

            user_obj = self.cog.bot.get_user(user_id) or discord.Object(id=user_id)

            async with self.cog._mem_lock:
                p = self.cog._get_player(user_obj)
                for item_name, count in total_items.items():
                    self.cog._add_item(p.bank, item_name, count)
                if total_coins > 0:
                    p.bank_coins = int(p.bank_coins) + total_coins
                await self.cog._persist()

            for offer in slots:
                if offer is None:
                    continue
                offer.claimed = offer.filled
                offer.coins_pending = 0

            await self.save()

            parts = [f"**{c}x {n}**" for n, c in total_items.items()]
            if total_coins > 0:
                parts.append(f"**{total_coins:,}** GP")
            return True, f"Claimed {', '.join(parts)} → bank."

    async def cancel_offer(self, user_id: int, slot: int) -> Tuple[bool, str]:
        async with self._lock:
            slots = self.player_slots(user_id)
            offer = slots[slot]
            if offer is None:
                return False, "No offer in that slot."

            user_obj = self.cog.bot.get_user(user_id) or discord.Object(id=user_id)
            remaining = offer.remaining
            unclaimed_items = offer.claimable_items
            unclaimed_coins = offer.coins_pending

            async with self.cog._mem_lock:
                p = self.cog._get_player(user_obj)

                if offer.offer_type == "buy":
                    # Refund reserved coins for the unfilled portion
                    if remaining > 0:
                        p.bank_coins = int(p.bank_coins) + offer.price_each * remaining
                    # Deliver unclaimed purchased items
                    if unclaimed_items > 0:
                        self.cog._add_item(p.bank, offer.item, unclaimed_items)
                    # Deliver unclaimed refund coins
                    if unclaimed_coins > 0:
                        p.bank_coins = int(p.bank_coins) + unclaimed_coins
                else:  # sell
                    # Return unfilled items
                    if remaining > 0:
                        self.cog._add_item(p.bank, offer.item, remaining)
                    # Deliver unclaimed sale earnings
                    if unclaimed_coins > 0:
                        p.bank_coins = int(p.bank_coins) + unclaimed_coins

                await self.cog._persist()

            self.offers.remove(offer)
            await self.save()

            parts = []
            if offer.offer_type == "buy":
                refund_gp = offer.price_each * remaining + unclaimed_coins
                if refund_gp > 0:
                    parts.append(f"**{refund_gp:,}** GP")
                if unclaimed_items > 0:
                    parts.append(f"**{unclaimed_items}x {offer.item}**")
            else:
                if remaining > 0:
                    parts.append(f"**{remaining}x {offer.item}**")
                if unclaimed_coins > 0:
                    parts.append(f"**{unclaimed_coins:,}** GP")

            returned = ", ".join(parts) if parts else "nothing"
            return True, f"Offer cancelled. Returned {returned} to your bank."

    async def collect_offer(self, user_id: int, slot: int) -> Tuple[bool, str]:
        async with self._lock:
            slots = self.player_slots(user_id)
            offer = slots[slot]
            if offer is None:
                return False, "No offer in that slot."
            if not offer.is_complete:
                return False, "Offer is not yet complete."

            # Deliver any unclaimed items/coins before clearing
            unclaimed_items = offer.claimable_items
            unclaimed_coins = offer.coins_pending

            if unclaimed_items > 0 or unclaimed_coins > 0:
                user_obj = self.cog.bot.get_user(user_id) or discord.Object(id=user_id)
                async with self.cog._mem_lock:
                    p = self.cog._get_player(user_obj)
                    if offer.offer_type == "buy":
                        if unclaimed_items > 0:
                            self.cog._add_item(p.bank, offer.item, unclaimed_items)
                        if unclaimed_coins > 0:
                            p.bank_coins = int(p.bank_coins) + unclaimed_coins
                    else:
                        if unclaimed_coins > 0:
                            p.bank_coins = int(p.bank_coins) + unclaimed_coins
                    await self.cog._persist()

            self.offers.remove(offer)
            await self.save()
            return True, "Slot cleared. All items & coins delivered to your bank."

    async def edit_quantity(
        self, user_id: int, slot: int, new_qty: int,
    ) -> Tuple[bool, str]:
        async with self._lock:
            slots = self.player_slots(user_id)
            offer = slots[slot]
            if offer is None:
                return False, "No offer in that slot."
            if offer.is_complete:
                return False, "Offer already complete."
            if new_qty <= 0:
                return False, "Quantity must be > 0."
            if new_qty < offer.filled:
                return False, f"Can't go below filled amount (**{offer.filled}**)."
            if new_qty == offer.quantity:
                return False, "Quantity unchanged."

            diff = new_qty - offer.quantity
            user_obj = self.cog.bot.get_user(user_id) or discord.Object(id=user_id)

            async with self.cog._mem_lock:
                p = self.cog._get_player(user_obj)

                if offer.offer_type == "buy":
                    if diff > 0:
                        extra = offer.price_each * diff
                        if int(p.bank_coins) < extra:
                            return False, f"Need **{extra:,}** more GP in bank."
                        p.bank_coins = int(p.bank_coins) - extra
                    else:
                        p.bank_coins = int(p.bank_coins) + offer.price_each * abs(diff)
                else:  # sell
                    if diff > 0:
                        have = int(p.bank.get(offer.item, 0))
                        if have < diff:
                            return False, f"Need **{diff}** more **{offer.item}** in bank."
                        self.cog._remove_item(p.bank, offer.item, diff)
                    else:
                        self.cog._add_item(p.bank, offer.item, abs(diff))

                await self.cog._persist()

            offer.quantity = new_qty

            if diff > 0 and not offer.is_complete:
                await self._match_offer(offer)

            await self.save()
            return True, f"Quantity updated to **{new_qty}**."

    # ── Matching Engine ────────────────────────────────────────────

    async def _match_offer(self, offer: GEOffer):
        """Match *offer* against resting counter-offers.

        Price rule (standard exchange behaviour):
        • Incoming BUY  matches existing SELLs → trade at SELL price
        • Incoming SELL matches existing BUYs  → trade at BUY  price
        The incoming side always gets a deal at least as good as they asked for.
        """
        if offer.is_complete:
            return

        if offer.offer_type == "buy":
            # Match cheapest sells first, then FIFO
            counters = sorted(
                (o for o in self.offers
                 if o.offer_type == "sell"
                 and o.item == offer.item
                 and not o.is_complete
                 and o.price_each <= offer.price_each
                 and o.user_id != offer.user_id),
                key=lambda o: (o.price_each, o.created_at),
            )

            for sell in counters:
                if offer.is_complete:
                    break
                qty = min(offer.remaining, sell.remaining)
                if qty <= 0:
                    continue

                trade_price = sell.price_each  # buyer pays seller's listed price

                offer.filled += qty
                sell.filled += qty

                # Accumulate for claiming — no immediate bank transfer
                offer.coins_pending += (offer.price_each - trade_price) * qty
                sell.coins_pending += trade_price * qty

        else:  # sell
            # Match highest buyers first, then FIFO
            counters = sorted(
                (o for o in self.offers
                 if o.offer_type == "buy"
                 and o.item == offer.item
                 and not o.is_complete
                 and o.price_each >= offer.price_each
                 and o.user_id != offer.user_id),
                key=lambda o: (-o.price_each, o.created_at),
            )

            for buy in counters:
                if offer.is_complete:
                    break
                qty = min(offer.remaining, buy.remaining)
                if qty <= 0:
                    continue

                trade_price = buy.price_each  # seller receives buyer's listed price

                offer.filled += qty
                buy.filled += qty

                # Accumulate for claiming — no immediate bank transfer
                offer.coins_pending += trade_price * qty


# ═══════════════════════════════════════════════════════════════════
#  Embed Helpers
# ═══════════════════════════════════════════════════════════════════

def _slot_line(idx: int, offer: Optional[GEOffer]) -> str:
    label = f"**Slot {idx + 1}**"
    if offer is None:
        return f"{label} — Empty"
    typ = "Buy" if offer.offer_type == "buy" else "Sell"
    emoji = "✅" if offer.is_complete else ("🟢" if offer.offer_type == "buy" else "🔴")
    claim = " 📥" if offer.has_claimable else ""
    return (
        f"{label} — {emoji} {typ}: **{offer.item}** "
        f"({offer.filled}/{offer.quantity}){claim}\n"
        f"{offer.progress_bar(10)}"
    )


def _main_embed(slots: List[Optional[GEOffer]]) -> discord.Embed:
    lines = [_slot_line(i, o) for i, o in enumerate(slots)]
    return discord.Embed(
        title="📊 Grand Exchange",
        description=(
            "Select a slot to view details or create an offer.\n"
            "Items & coins are held from your **bank**.\n\n"
            + "\n\n".join(lines)
        ),
        color=0x2B2D31,
    )


def _empty_slot_embed(slot: int) -> discord.Embed:
    return discord.Embed(
        title=f"📊 Grand Exchange — Slot {slot + 1}",
        description="This slot is empty. Choose an action:",
        color=0x2B2D31,
    )


def _detail_embed(offer: GEOffer) -> discord.Embed:
    typ_label = "🟢 Buy" if offer.offer_type == "buy" else "🔴 Sell"
    if offer.is_complete:
        typ_label += " — Complete!"

    lines = [
        f"**Type:** {typ_label}",
        f"**Item:** {offer.item}",
        f"**Price:** {offer.price_each:,} GP each",
        f"**Progress:** {offer.filled}/{offer.quantity} ({offer.progress_pct}%)",
        offer.progress_bar(10),
        "",
    ]

    if offer.offer_type == "buy":
        reserved = offer.price_each * offer.quantity
        lines.append(f"**Total Reserved:** {reserved:,} GP")
        lines.append(f"**Items Received:** {offer.filled}x {offer.item}")
    else:
        lines.append(f"**Items Listed:** {offer.quantity}x {offer.item}")
        lines.append(f"**Items Sold:** {offer.filled}x {offer.item}")

    # Claimable section
    if offer.has_claimable:
        lines.append("")
        claim_parts = []
        ci = offer.claimable_items
        if offer.offer_type == "buy":
            if ci > 0:
                claim_parts.append(f"{ci}x {offer.item}")
            if offer.coins_pending > 0:
                claim_parts.append(f"{offer.coins_pending:,} GP")
        else:
            if offer.coins_pending > 0:
                claim_parts.append(f"{offer.coins_pending:,} GP")
        if claim_parts:
            lines.append(f"📥 **Claimable:** {', '.join(claim_parts)}")

    if offer.is_complete and not offer.has_claimable:
        lines.append("\n*All items & coins claimed. Collect to free the slot.*")
    elif offer.is_complete:
        lines.append("\n*Claim remaining items, then collect to free the slot.*")

    color = 0x00FF44 if offer.is_complete else 0x2B2D31
    return discord.Embed(
        title=f"📊 Grand Exchange — Slot {offer.slot + 1}",
        description="\n".join(lines),
        color=color,
    )


# ═══════════════════════════════════════════════════════════════════
#  UI Views & Buttons
# ═══════════════════════════════════════════════════════════════════

# ── Open button (sent in the public channel) ──────────────────────

class GEOpenView(discord.ui.View):
    """Public message with a button that spawns the ephemeral GE panel."""

    def __init__(self, ge: GEManager, user_id: int):
        super().__init__(timeout=60)
        self.ge = ge
        self.user_id = user_id

    @discord.ui.button(label="Open Grand Exchange", style=discord.ButtonStyle.primary, emoji="📊")
    async def open_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Only the command user can open this.", ephemeral=True)
            return

        slots = self.ge.player_slots(self.user_id)
        emb = _main_embed(slots)
        view = GEMainView(self.ge, self.user_id)
        await interaction.response.send_message(embed=emb, view=view, ephemeral=True)

    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True


# ── Main panel (ephemeral — 4 slot buttons) ──────────────────────

class GEMainView(discord.ui.View):

    def __init__(self, ge: GEManager, user_id: int):
        super().__init__(timeout=180)
        self.ge = ge
        self.user_id = user_id

        slots = ge.player_slots(user_id)
        for i, offer in enumerate(slots):
            self.add_item(_SlotButton(ge, user_id, i, offer))

        # Show Claim All button when any slot has claimable items/coins
        if any(o is not None and o.has_claimable for o in slots):
            self.add_item(_ClaimAllButton(ge, user_id))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your GE panel.", ephemeral=True)
            return False
        return True


class _SlotButton(discord.ui.Button):

    def __init__(self, ge: GEManager, user_id: int, slot: int, offer: Optional[GEOffer]):
        self.ge = ge
        self.user_id = user_id
        self.slot = slot
        self.offer = offer

        if offer is None:
            label = f"Slot {slot + 1}: Empty"
            style = discord.ButtonStyle.secondary
        elif offer.is_complete:
            name = offer.item[:20]
            label = f"✅ {name} {offer.filled}/{offer.quantity}"
            style = discord.ButtonStyle.success
        else:
            typ = "Buy" if offer.offer_type == "buy" else "Sell"
            name = offer.item[:15]
            label = f"{typ}: {name} {offer.filled}/{offer.quantity}"
            style = (discord.ButtonStyle.primary
                     if offer.offer_type == "buy"
                     else discord.ButtonStyle.danger)

        super().__init__(label=label, style=style, row=0)

    async def callback(self, interaction: discord.Interaction):
        if self.offer is None:
            emb = _empty_slot_embed(self.slot)
            view = _EmptySlotView(self.ge, self.user_id, self.slot)
        else:
            emb = _detail_embed(self.offer)
            view = _DetailView(self.ge, self.user_id, self.slot, self.offer)
        await interaction.response.edit_message(embed=emb, view=view)


# ── Empty-slot view (Buy / Sell / Back) ───────────────────────────

class _EmptySlotView(discord.ui.View):

    def __init__(self, ge: GEManager, user_id: int, slot: int):
        super().__init__(timeout=180)
        self.ge = ge
        self.user_id = user_id
        self.slot = slot

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your GE panel.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Buy", style=discord.ButtonStyle.success, emoji="🟢")
    async def buy_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        emb = discord.Embed(
            title=f"📊 Grand Exchange — Slot {self.slot + 1} (Buy)",
            description="Select a category:",
            color=0x2B2D31,
        )
        view = _CategoryView(self.ge, self.user_id, self.slot, "buy")
        await interaction.response.edit_message(embed=emb, view=view)

    @discord.ui.button(label="Sell", style=discord.ButtonStyle.danger, emoji="🔴")
    async def sell_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        emb = discord.Embed(
            title=f"📊 Grand Exchange — Slot {self.slot + 1} (Sell)",
            description="Select a category:",
            color=0x2B2D31,
        )
        view = _CategoryView(self.ge, self.user_id, self.slot, "sell")
        await interaction.response.edit_message(embed=emb, view=view)

    @discord.ui.button(label="Back", style=discord.ButtonStyle.secondary)
    async def back_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        slots = self.ge.player_slots(self.user_id)
        emb = _main_embed(slots)
        view = GEMainView(self.ge, self.user_id)
        await interaction.response.edit_message(embed=emb, view=view)


# ── Category select (Buy/Sell → pick category → pick item) ───────

class _CategoryView(discord.ui.View):

    def __init__(self, ge: GEManager, user_id: int, slot: int, offer_type: str):
        super().__init__(timeout=180)
        self.ge = ge
        self.user_id = user_id
        self.slot = slot
        self.offer_type = offer_type

        options = [
            discord.SelectOption(label=cat_name, value=cat_name)
            for cat_name in GE_CATEGORIES
        ]
        self.add_item(_CategorySelect(ge, user_id, slot, offer_type, options))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your GE panel.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Back", style=discord.ButtonStyle.secondary, row=1)
    async def back_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        emb = _empty_slot_embed(self.slot)
        view = _EmptySlotView(self.ge, self.user_id, self.slot)
        await interaction.response.edit_message(embed=emb, view=view)


class _CategorySelect(discord.ui.Select):

    def __init__(self, ge: GEManager, user_id: int, slot: int,
                 offer_type: str, options: list):
        super().__init__(placeholder="Choose a category\u2026", options=options, row=0)
        self.ge = ge
        self.user_id = user_id
        self.slot = slot
        self.offer_type = offer_type

    async def callback(self, interaction: discord.Interaction):
        cat = self.values[0]
        items = GE_CATEGORIES.get(cat, [])
        typ = "Buy" if self.offer_type == "buy" else "Sell"
        emb = discord.Embed(
            title=f"📊 Grand Exchange — Slot {self.slot + 1} ({typ})",
            description=f"**{cat}**\nSelect an item:",
            color=0x2B2D31,
        )
        view = _ItemSelectView(
            self.ge, self.user_id, self.slot, self.offer_type, cat, items,
        )
        await interaction.response.edit_message(embed=emb, view=view)


class _ItemSelectView(discord.ui.View):

    def __init__(self, ge: GEManager, user_id: int, slot: int,
                 offer_type: str, category: str, items: list):
        super().__init__(timeout=180)
        self.ge = ge
        self.user_id = user_id
        self.slot = slot
        self.offer_type = offer_type
        self.category = category

        options = [
            discord.SelectOption(label=name, value=name)
            for name in items[:25]
        ]
        self.add_item(_ItemSelect(ge, user_id, slot, offer_type, options))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your GE panel.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Back", style=discord.ButtonStyle.secondary, row=1)
    async def back_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        typ = "Buy" if self.offer_type == "buy" else "Sell"
        emb = discord.Embed(
            title=f"📊 Grand Exchange — Slot {self.slot + 1} ({typ})",
            description="Select a category:",
            color=0x2B2D31,
        )
        view = _CategoryView(self.ge, self.user_id, self.slot, self.offer_type)
        await interaction.response.edit_message(embed=emb, view=view)


class _ItemSelect(discord.ui.Select):

    def __init__(self, ge: GEManager, user_id: int, slot: int,
                 offer_type: str, options: list):
        super().__init__(placeholder="Choose an item\u2026", options=options, row=0)
        self.ge = ge
        self.user_id = user_id
        self.slot = slot
        self.offer_type = offer_type

    async def callback(self, interaction: discord.Interaction):
        item = self.values[0]
        modal = _OfferModal(self.ge, self.user_id, self.slot, self.offer_type, item)
        await interaction.response.send_modal(modal)


# ── Create-offer modal (qty + price only — item already selected) ─

class _OfferModal(discord.ui.Modal):

    qty_input = discord.ui.TextInput(
        label="Quantity",
        placeholder="e.g. 100",
        max_length=10,
    )
    price_input = discord.ui.TextInput(
        label="Price Each (GP)",
        placeholder="e.g. 500",
        max_length=15,
    )

    def __init__(self, ge: GEManager, user_id: int, slot: int,
                 offer_type: str, item: str):
        typ = "Buy" if offer_type == "buy" else "Sell"
        # Modal title max 45 chars — truncate item name if needed
        title_text = f"{typ}: {item}"
        if len(title_text) > 45:
            title_text = title_text[:42] + "\u2026"
        super().__init__(title=title_text)
        self.ge = ge
        self.user_id = user_id
        self.slot = slot
        self.offer_type = offer_type
        self.item = item

    async def on_submit(self, interaction: discord.Interaction):
        # ── Parse quantity ─────────────────────────────────────────
        try:
            qty = int(self.qty_input.value.strip().replace(",", ""))
            if qty <= 0:
                raise ValueError
        except (ValueError, TypeError):
            emb = _empty_slot_embed(self.slot)
            emb.description = "❌ Invalid quantity. Enter a positive number.\n\nTry again:"
            emb.color = 0xFF4444
            view = _EmptySlotView(self.ge, self.user_id, self.slot)
            await interaction.response.edit_message(embed=emb, view=view)
            return

        # ── Parse price ────────────────────────────────────────────
        try:
            price = int(self.price_input.value.strip().replace(",", ""))
            if price <= 0:
                raise ValueError
        except (ValueError, TypeError):
            emb = _empty_slot_embed(self.slot)
            emb.description = "❌ Invalid price. Enter a positive number.\n\nTry again:"
            emb.color = 0xFF4444
            view = _EmptySlotView(self.ge, self.user_id, self.slot)
            await interaction.response.edit_message(embed=emb, view=view)
            return

        # ── Create offer ───────────────────────────────────────────
        ok, msg = await self.ge.create_offer(
            self.user_id, self.slot, self.offer_type, self.item, qty, price,
        )

        slots = self.ge.player_slots(self.user_id)
        emb = _main_embed(slots)
        emb.set_footer(text=f"{'✅' if ok else '❌'} {msg}")
        view = GEMainView(self.ge, self.user_id)
        await interaction.response.edit_message(embed=emb, view=view)


# ── Detail view (active or complete offer) ────────────────────────

class _DetailView(discord.ui.View):

    def __init__(self, ge: GEManager, user_id: int, slot: int, offer: GEOffer):
        super().__init__(timeout=180)
        self.ge = ge
        self.user_id = user_id
        self.slot = slot
        self.offer = offer

        if offer.has_claimable:
            self.add_item(_ClaimButton(ge, user_id, slot))
        if offer.is_complete:
            self.add_item(_CollectButton(ge, user_id, slot))
        else:
            self.add_item(_EditButton(ge, user_id, slot))
            self.add_item(_CancelButton(ge, user_id, slot))
        self.add_item(_BackButton(ge, user_id))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your GE panel.", ephemeral=True)
            return False
        return True


class _ClaimAllButton(discord.ui.Button):

    def __init__(self, ge: GEManager, user_id: int):
        super().__init__(label="Claim All", style=discord.ButtonStyle.success, emoji="📥", row=1)
        self.ge = ge
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        ok, msg = await self.ge.claim_all(self.user_id)
        slots = self.ge.player_slots(self.user_id)
        emb = _main_embed(slots)
        emb.set_footer(text=f"{'✅' if ok else '❌'} {msg}")
        view = GEMainView(self.ge, self.user_id)
        await interaction.response.edit_message(embed=emb, view=view)


class _ClaimButton(discord.ui.Button):

    def __init__(self, ge: GEManager, user_id: int, slot: int):
        super().__init__(label="Claim", style=discord.ButtonStyle.success, emoji="📥")
        self.ge = ge
        self.user_id = user_id
        self.slot = slot

    async def callback(self, interaction: discord.Interaction):
        ok, msg = await self.ge.claim_offer(self.user_id, self.slot)
        slots = self.ge.player_slots(self.user_id)
        offer = slots[self.slot]
        if offer:
            emb = _detail_embed(offer)
            emb.set_footer(text=f"{'✅' if ok else '❌'} {msg}")
            view = _DetailView(self.ge, self.user_id, self.slot, offer)
        else:
            emb = _main_embed(slots)
            emb.set_footer(text=f"{'✅' if ok else '❌'} {msg}")
            view = GEMainView(self.ge, self.user_id)
        await interaction.response.edit_message(embed=emb, view=view)


class _CollectButton(discord.ui.Button):

    def __init__(self, ge: GEManager, user_id: int, slot: int):
        super().__init__(label="Collect", style=discord.ButtonStyle.success, emoji="✅")
        self.ge = ge
        self.user_id = user_id
        self.slot = slot

    async def callback(self, interaction: discord.Interaction):
        ok, msg = await self.ge.collect_offer(self.user_id, self.slot)
        slots = self.ge.player_slots(self.user_id)
        emb = _main_embed(slots)
        emb.set_footer(text=f"{'✅' if ok else '❌'} {msg}")
        view = GEMainView(self.ge, self.user_id)
        await interaction.response.edit_message(embed=emb, view=view)


class _EditButton(discord.ui.Button):

    def __init__(self, ge: GEManager, user_id: int, slot: int):
        super().__init__(label="Edit Qty", style=discord.ButtonStyle.primary, emoji="✏️")
        self.ge = ge
        self.user_id = user_id
        self.slot = slot

    async def callback(self, interaction: discord.Interaction):
        modal = _EditModal(self.ge, self.user_id, self.slot)
        await interaction.response.send_modal(modal)


class _CancelButton(discord.ui.Button):

    def __init__(self, ge: GEManager, user_id: int, slot: int):
        super().__init__(label="Cancel Offer", style=discord.ButtonStyle.danger, emoji="❌")
        self.ge = ge
        self.user_id = user_id
        self.slot = slot

    async def callback(self, interaction: discord.Interaction):
        ok, msg = await self.ge.cancel_offer(self.user_id, self.slot)
        slots = self.ge.player_slots(self.user_id)
        emb = _main_embed(slots)
        emb.set_footer(text=f"{'✅' if ok else '❌'} {msg}")
        view = GEMainView(self.ge, self.user_id)
        await interaction.response.edit_message(embed=emb, view=view)


class _BackButton(discord.ui.Button):

    def __init__(self, ge: GEManager, user_id: int):
        super().__init__(label="Back", style=discord.ButtonStyle.secondary)
        self.ge = ge
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        slots = self.ge.player_slots(self.user_id)
        emb = _main_embed(slots)
        view = GEMainView(self.ge, self.user_id)
        await interaction.response.edit_message(embed=emb, view=view)


# ── Edit-quantity modal ───────────────────────────────────────────

class _EditModal(discord.ui.Modal, title="Edit Quantity"):

    qty_input = discord.ui.TextInput(
        label="New Quantity",
        placeholder="e.g. 150",
        max_length=10,
    )

    def __init__(self, ge: GEManager, user_id: int, slot: int):
        super().__init__()
        self.ge = ge
        self.user_id = user_id
        self.slot = slot

    async def on_submit(self, interaction: discord.Interaction):
        try:
            new_qty = int(self.qty_input.value.strip().replace(",", ""))
        except (ValueError, TypeError):
            # Can't edit message from here reliably — send ephemeral error
            await interaction.response.send_message("❌ Invalid quantity.", ephemeral=True)
            return

        ok, msg = await self.ge.edit_quantity(self.user_id, self.slot, new_qty)

        # Refresh to detail view (or main if offer is gone)
        slots = self.ge.player_slots(self.user_id)
        offer = slots[self.slot]
        if offer:
            emb = _detail_embed(offer)
            emb.set_footer(text=f"{'✅' if ok else '❌'} {msg}")
            view = _DetailView(self.ge, self.user_id, self.slot, offer)
        else:
            emb = _main_embed(slots)
            emb.set_footer(text=f"{'✅' if ok else '❌'} {msg}")
            view = GEMainView(self.ge, self.user_id)

        await interaction.response.edit_message(embed=emb, view=view)
