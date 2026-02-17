"""
Discord UI components for the Wilderness game.

This module contains all custom UI elements:
- GroundPickupButton: Interactive item pickup after combat
- FightLogView: Paginated fight log with navigation
- DuelView: PvP turn-based combat interface
- NPCInfoSelect/NPCInfoView: NPC information dropdown
- BankCategorySelect/BankView: Bank category browser
- InventoryCategorySelect/InventoryView: Inventory category browser
"""

from typing import TYPE_CHECKING, Optional, List, Tuple
import discord

from .models import DuelState
from .npcs import NPCS

if TYPE_CHECKING:
    from .wilderness import Wilderness


class GroundPickupButton(discord.ui.Button):
    """Interactive button for picking up dropped items."""

    def __init__(
        self,
        *,
        cog: "Wilderness",
        author_id: int,
        item: str,
        qty: int,
        run_id: int,
    ):
        super().__init__(
            emoji="🫳",
            style=discord.ButtonStyle.success,
            label=f"Pick up {item} x{qty}",
        )
        self.cog = cog
        self.author_id = author_id
        self.item = item
        self.qty = int(qty)
        self.run_id = int(run_id)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Only the fighter can pick this up.", ephemeral=True)
            return

        async with self.cog._mem_lock:
            p = self.cog._get_player(interaction.user)

            # Invalidate if they teleported/died since the drop
            if int(p.wildy_run_id) != self.run_id or not p.in_wilderness:
                await interaction.response.send_message(
                    "You can't pick this up anymore (you teleported or died after it dropped).",
                    ephemeral=True
                )
                return

            # Check if it fits NOW
            need = self.cog._slots_needed_to_add(p.inventory, self.item, self.qty)
            free = self.cog._inv_free_slots(p.inventory)
            if need > free:
                await interaction.response.send_message(
                    f"Still no space. You need **{need}** free slot(s), you have **{free}**.",
                    ephemeral=True
                )
                return

            # Add item
            self.cog._add_item(p.inventory, self.item, self.qty)
            self.cog._touch(p)
            await self.cog._persist()

        # Disable this one button after successful pickup
        self.disabled = True
        await interaction.response.edit_message(view=self.view)
        await interaction.followup.send(f"🫳 Picked up **{self.item} x{self.qty}**.", ephemeral=True)


class FightLogView(discord.ui.View):
    """Paginated fight log with navigation buttons."""

    def __init__(
        self,
        *,
        author_id: int,
        pages: List[str],
        title: str = "Fight Log",
        cog: Optional["Wilderness"] = None,
        ground_drops: Optional[List[Tuple[str, int, int]]] = None,
        start_on_last: bool = False,
    ):
        super().__init__(timeout=300)
        self.author_id = author_id
        self.pages = pages
        self.title = title

        self.page = (max(0, len(self.pages) - 1) if start_on_last else 0)

        self._sync_buttons()

        self._ground_buttons: List[GroundPickupButton] = []
        if cog and ground_drops:
            for (item, qty, run_id) in ground_drops:
                if qty <= 0:
                    continue
                btn = GroundPickupButton(cog=cog, author_id=author_id, item=item, qty=qty, run_id=run_id)
                self._ground_buttons.append(btn)
                self.add_item(btn)

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
    """PvP turn-based combat interface."""

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
            await interaction.response.send_message("It's not your turn.", ephemeral=True)
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
    """NPC information dropdown."""

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
    """Container for NPC info dropdown."""

    def __init__(self, cog: "Wilderness", author_id: int):
        super().__init__(timeout=180)
        self.add_item(NPCInfoSelect(cog, author_id))

    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, discord.ui.Select):
                child.disabled = True
        return


class BankCategorySelect(discord.ui.Select):
    """Bank category dropdown."""

    def __init__(self, cog: "Wilderness", author_id: int, categories: List[str], current: str):
        self.cog = cog
        self.author_id = author_id

        opts = []
        for c in categories:
            opts.append(discord.SelectOption(label=c, value=c, default=(c == current)))

        super().__init__(
            placeholder="Select a bank category…",
            min_values=1,
            max_values=1,
            options=opts[:25],
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Only the command user can use this menu.", ephemeral=True)
            return

        category = self.values[0]
        emb = self.cog._bank_embed(interaction.user, category)
        view = BankView(self.cog, self.author_id, category)
        await interaction.response.edit_message(embed=emb, view=view)


class BankView(discord.ui.View):
    """Bank category browser."""

    def __init__(self, cog: "Wilderness", author_id: int, current_category: str):
        super().__init__(timeout=180)
        self.cog = cog
        self.author_id = author_id
        self.current_category = current_category

        categories = cog._bank_categories_for_user(author_id)
        if current_category not in categories:
            current_category = categories[0] if categories else "All"

        self.add_item(BankCategorySelect(cog, author_id, categories, current_category))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Only the command user can use this menu.", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, discord.ui.Select):
                child.disabled = True


class InventoryCategorySelect(discord.ui.Select):
    """Inventory category dropdown."""

    def __init__(self, cog: "Wilderness", author_id: int, categories: List[str], current: str):
        self.cog = cog
        self.author_id = author_id

        opts = []
        for c in categories:
            opts.append(discord.SelectOption(label=c, value=c, default=(c == current)))

        super().__init__(
            placeholder="Select an inventory category…",
            min_values=1,
            max_values=1,
            options=opts[:25],
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Only the command user can use this menu.", ephemeral=True)
            return

        category = self.values[0]
        emb = self.cog._inv_embed(interaction.user, category)
        view = InventoryView(self.cog, self.author_id, category)
        await interaction.response.edit_message(embed=emb, view=view)


class InventoryView(discord.ui.View):
    """Inventory category browser."""

    def __init__(self, cog: "Wilderness", author_id: int, current_category: str):
        super().__init__(timeout=180)
        self.cog = cog
        self.author_id = author_id
        self.current_category = current_category

        categories = cog._inv_categories_for_user(author_id)
        if current_category not in categories:
            current_category = categories[0] if categories else "All"

        self.add_item(InventoryCategorySelect(cog, author_id, categories, current_category))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Only the command user can use this menu.", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, discord.ui.Select):
                child.disabled = True
