# UI views, buttons, dropdowns for the wilderness game

from typing import TYPE_CHECKING, Optional, List, Tuple, Dict
import discord

from .models import DuelState
from .items import FOOD
from .npcs import NPCS
from .craftable import CRAFTABLES
from .breakdownitems import BREAKDOWNS

if TYPE_CHECKING:
    from .wilderness import Wilderness


class GroundPickupButton(discord.ui.Button):

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
            if int(p.wildy_run_id) != self.run_id:
                await interaction.response.send_message(
                    "You can't pick this up anymore (you teleported or died after it dropped).",
                    ephemeral=True
                )
                return

            # Determine how many we can pick up
            free = self.cog._inv_free_slots(p.inventory)
            is_stack = self.cog._is_stackable(self.item) and self.item not in FOOD
            if is_stack:
                # Stackables use 1 slot (or 0 if already in inv) — pick up all
                if p.inventory.get(self.item, 0) > 0:
                    pick_qty = self.qty
                elif free >= 1:
                    pick_qty = self.qty
                else:
                    pick_qty = 0
            else:
                pick_qty = min(self.qty, free)

            if pick_qty <= 0:
                await interaction.response.send_message(
                    f"No inventory space. You have **{free}** free slot(s).",
                    ephemeral=True
                )
                return

            # Add item
            self.cog._add_item(p.inventory, self.item, pick_qty)
            # Remove from persisted ground_items
            self.cog._remove_ground_item(p, self.item, pick_qty)
            self.cog._touch(p)
            await self.cog._persist()
            leftover = self.qty - pick_qty

        if leftover <= 0:
            self.disabled = True
        else:
            self.qty = leftover
            self.label = f"Pick up {self.item} x{leftover}"
        await interaction.response.edit_message(view=self.view)
        await interaction.followup.send(f"🫳 Picked up **{self.item} x{pick_qty}**.", ephemeral=True)


class FightLogView(discord.ui.View):

    def __init__(
        self,
        *,
        author_id: int,
        pages: List[str],
        title: str = "Fight Log",
        cog: Optional["Wilderness"] = None,
        ground_drops: Optional[List[Tuple[str, int, int]]] = None,
        start_on_last: bool = False,
        npc_image: Optional[str] = None,
        embed_color: int = 0x2B2D31,
    ):
        super().__init__(timeout=300)
        self.author_id = author_id
        self.pages = pages
        self.title = title
        self.npc_image = npc_image
        self.embed_color = embed_color

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

    def _render_embed(self) -> discord.Embed:
        total = max(1, len(self.pages))
        emb = discord.Embed(
            title=f"📜 {self.title} — Page {self.page + 1}/{total}",
            description=self.pages[self.page],
            color=self.embed_color,
        )
        if self.npc_image:
            emb.set_thumbnail(url=self.npc_image)
        return emb

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Only the fighter can control these pages.", ephemeral=True)
            return False
        return True

    @discord.ui.button(emoji="⏮️", style=discord.ButtonStyle.secondary)
    async def first_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = 0
        self._sync_buttons()
        await interaction.response.edit_message(embed=self._render_embed(), view=self)

    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = max(0, self.page - 1)
        self._sync_buttons()
        await interaction.response.edit_message(embed=self._render_embed(), view=self)

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.secondary)
    async def next_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = min(len(self.pages) - 1, self.page + 1)
        self._sync_buttons()
        await interaction.response.edit_message(embed=self._render_embed(), view=self)

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary)
    async def last_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = max(0, len(self.pages) - 1)
        self._sync_buttons()
        await interaction.response.edit_message(embed=self._render_embed(), view=self)

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

    def __init__(self, cog: "Wilderness", author_id: int):
        self.cog = cog
        self.author_id = author_id
        options = []
        for npc in NPCS:
            options.append(
                discord.SelectOption(
                    label=npc["name"],
                    description=f"Min wildy {npc['min_wildy']} • Tier {npc['tier']}",
                    value=npc["name"],
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


class CraftableInfoSelect(discord.ui.Select):

    def __init__(self, cog: "Wilderness", author_id: int):
        self.cog = cog
        self.author_id = author_id
        options = []
        for name, recipe in CRAFTABLES.items():
            desc = recipe.get("description", "")
            if len(desc) > 80:
                desc = desc[:77] + "..."
            options.append(
                discord.SelectOption(
                    label=name,
                    description=desc or "Craftable item",
                    value=name,
                )
            )
        super().__init__(
            placeholder="Select a craftable item to view details…",
            min_values=1,
            max_values=1,
            options=options[:25],
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Only the command user can use this menu.", ephemeral=True)
            return
        craft_name = self.values[0]
        emb = self.cog._craftable_info_embed(craft_name)
        await interaction.response.edit_message(embed=emb, view=self.view)


class CraftableInfoView(discord.ui.View):

    def __init__(self, cog: "Wilderness", author_id: int):
        super().__init__(timeout=180)
        self.add_item(CraftableInfoSelect(cog, author_id))

    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, discord.ui.Select):
                child.disabled = True
        return


class BreakdownInfoSelect(discord.ui.Select):

    def __init__(self, cog: "Wilderness", author_id: int):
        self.cog = cog
        self.author_id = author_id
        options = []
        for name, info in BREAKDOWNS.items():
            desc = info.get("description", "")
            if len(desc) > 80:
                desc = desc[:77] + "..."
            options.append(
                discord.SelectOption(
                    label=name,
                    description=desc or "Breakdownable item",
                    value=name,
                )
            )
        super().__init__(
            placeholder="Select an item to view breakdown details…",
            min_values=1,
            max_values=1,
            options=options[:25],
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Only the command user can use this menu.", ephemeral=True)
            return
        item_name = self.values[0]
        emb = self.cog._breakdown_info_embed(item_name)
        await interaction.response.edit_message(embed=emb, view=self.view)


class BreakdownInfoView(discord.ui.View):

    def __init__(self, cog: "Wilderness", author_id: int):
        super().__init__(timeout=180)
        self.add_item(BreakdownInfoSelect(cog, author_id))

    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, discord.ui.Select):
                child.disabled = True
        return


class BankCategorySelect(discord.ui.Select):

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


class GroundPickupViewButton(discord.ui.Button):

    def __init__(self, *, cog: "Wilderness", author_id: int, item: str, qty: int):
        super().__init__(
            emoji="🫳",
            style=discord.ButtonStyle.success,
            label=f"Pick up {item} x{qty}",
        )
        self.cog = cog
        self.author_id = author_id
        self.item = item
        self.qty = int(qty)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Only the owner can pick this up.", ephemeral=True)
            return

        async with self.cog._mem_lock:
            p = self.cog._get_player(interaction.user)

            # Check item still exists on ground
            ground = self.cog._active_ground_items(p)
            available = ground.get(self.item, 0)
            if available <= 0:
                await interaction.response.send_message(
                    f"**{self.item}** is no longer on the ground.",
                    ephemeral=True,
                )
                return

            want = min(self.qty, available)

            # Determine how many we can pick up
            free = self.cog._inv_free_slots(p.inventory)
            is_stack = self.cog._is_stackable(self.item) and self.item not in FOOD
            if is_stack:
                # Stackables use 1 slot (or 0 if already in inv) — pick up all
                if p.inventory.get(self.item, 0) > 0:
                    pick_qty = want
                elif free >= 1:
                    pick_qty = want
                else:
                    pick_qty = 0
            else:
                pick_qty = min(want, free)

            if pick_qty <= 0:
                await interaction.response.send_message(
                    f"No inventory space. You have **{free}** free slot(s).",
                    ephemeral=True,
                )
                return

            self.cog._add_item(p.inventory, self.item, pick_qty)
            self.cog._remove_ground_item(p, self.item, pick_qty)
            self.cog._touch(p)
            await self.cog._persist()
            leftover = want - pick_qty

        if leftover <= 0:
            self.disabled = True
        else:
            self.qty = leftover
            self.label = f"Pick up {self.item} x{leftover}"
        await interaction.response.edit_message(view=self.view)
        await interaction.followup.send(f"🫳 Picked up **{self.item} x{pick_qty}**.", ephemeral=True)


class GroundView(discord.ui.View):

    def __init__(self, cog: "Wilderness", author_id: int, ground: Dict[str, int]):
        super().__init__(timeout=300)
        self.author_id = author_id

        for item, qty in sorted(ground.items(), key=lambda x: x[0].lower()):
            if qty <= 0:
                continue
            self.add_item(GroundPickupViewButton(cog=cog, author_id=author_id, item=item, qty=qty))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Only the owner can use this.", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True


class KillCountView(discord.ui.View):

    def __init__(self, *, author_id: int, embeds: list):
        super().__init__(timeout=300)
        self.author_id = author_id
        self.embeds = embeds
        self.page = 0
        self._sync_buttons()

    def _sync_buttons(self):
        last = max(0, len(self.embeds) - 1)
        self.prev_btn.disabled = (self.page <= 0)
        self.next_btn.disabled = (self.page >= last)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Only the owner can use this.", ephemeral=True)
            return False
        return True

    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = max(0, self.page - 1)
        self._sync_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.page], view=self)

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.secondary)
    async def next_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = min(len(self.embeds) - 1, self.page + 1)
        self._sync_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.page], view=self)

    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True


# ── Highscores dropdown ─────────────────────────────────────────

HIGHSCORE_CATEGORIES = [
    ("overall", "🏆 Overall"),
    ("kills", "⚔️ Kills"),
    ("deaths", "💀 Deaths"),
    ("coins", "💰 Wealth"),
    ("slayer", "🗡️ Slayer"),
    ("unique", "✨ Unique Drops"),
    ("pets", "🐾 Pets"),
    ("tasks", "🗡️ Slayer Tasks"),
]


class HighscoresSelect(discord.ui.Select):

    def __init__(self, cog: "Wilderness", author_id: int, guild: Optional[discord.Guild], current: str):
        self.cog = cog
        self.author_id = author_id
        self.guild = guild

        opts = []
        for key, label in HIGHSCORE_CATEGORIES:
            opts.append(discord.SelectOption(label=label, value=key, default=(key == current)))

        super().__init__(
            placeholder="Select a category…",
            min_values=1,
            max_values=1,
            options=opts,
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Only the command user can use this menu.", ephemeral=True)
            return

        cat = self.values[0]
        emb = self.cog._highscores_embed(cat, self.guild)
        view = HighscoresView(self.cog, self.author_id, self.guild, cat)
        await interaction.response.edit_message(embed=emb, view=view)


class HighscoresView(discord.ui.View):

    def __init__(self, cog: "Wilderness", author_id: int, guild: Optional[discord.Guild], current: str):
        super().__init__(timeout=180)
        self.author_id = author_id
        self.add_item(HighscoresSelect(cog, author_id, guild, current))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Only the command user can use this menu.", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, discord.ui.Select):
                child.disabled = True
