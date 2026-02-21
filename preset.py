# Gear/inventory preset saving and loading

from typing import TYPE_CHECKING, Tuple, List, Dict, Optional

from .items import ITEMS, FOOD, EQUIP_SLOT_SET
from .models import PlayerState

if TYPE_CHECKING:
    from .wilderness import Wilderness

MAX_PRESETS = 10


class PresetManager:
    def __init__(self, cog: "Wilderness"):
        self.cog = cog

    def create(self, p: PlayerState, name: str) -> Tuple[bool, str]:
        """Save current gear + inv as a preset."""
        name = name.strip()
        if not name:
            return False, "Preset name cannot be empty."
        if len(name) > 30:
            return False, "Preset name too long (max 30 characters)."
        if len(p.presets) >= MAX_PRESETS and name.lower() not in {k.lower() for k in p.presets}:
            return False, f"You can have at most **{MAX_PRESETS}** presets. Delete one first."

        existing_key = None
        for k in p.presets:
            if k.lower() == name.lower():
                existing_key = k
                break
        if existing_key:
            del p.presets[existing_key]

        p.presets[name] = {
            "equipment": dict(p.equipment),
            "inventory": dict(p.inventory),
        }
        return True, f"Preset **{name}** saved."

    def delete(self, p: PlayerState, name: str) -> Tuple[bool, str]:
        key = self._find_key(p, name)
        if not key:
            return False, f"No preset named **{name}**."
        del p.presets[key]
        return True, f"Preset **{key}** deleted."

    def check(self, p: PlayerState, name: str) -> Tuple[bool, Optional[str], dict]:
        """Look up a preset. Returns (found, key_or_error, data)."""
        key = self._find_key(p, name)
        if not key:
            return False, f"No preset named **{name}**.", {}
        return True, key, p.presets[key]

    def load(self, p: PlayerState, name: str) -> Tuple[bool, str]:
        """Load a preset - banks everything then withdraws preset gear/inv from bank."""
        key = self._find_key(p, name)
        if not key:
            return False, f"No preset named **{name}**."

        data = p.presets[key]
        target_equip = data.get("equipment", {})
        target_inv = data.get("inventory", {})

        for slot, item in list(p.equipment.items()):
            if item:
                if slot == "ammo2":
                    continue  # handled with ammo
                elif slot == "ammo":
                    ammo_meta = ITEMS.get(item, {})
                    if ammo_meta.get("ammo_type") == "quiver":
                        self.cog._add_item(p.bank, item, 1)
                        ammo2 = p.equipment.get("ammo2")
                        if ammo2 and p.ammo_qty > 0:
                            self.cog._add_item(p.bank, ammo2, p.ammo_qty)
                    else:
                        self.cog._add_item(p.bank, item, p.ammo_qty)
                    p.ammo_qty = 0
                else:
                    self.cog._add_item(p.bank, item, 1)
        p.equipment.clear()

        for item, qty in list(p.inventory.items()):
            if qty > 0:
                self.cog._add_item(p.bank, item, qty)
        p.inventory.clear()

        missing = []
        for slot, item in target_equip.items():
            if not item:
                continue
            bank_have = p.bank.get(item, 0)
            if bank_have >= 1:
                self.cog._remove_item(p.bank, item, 1)
                p.equipment[slot] = item
            else:
                missing.append(item)

        for item, qty in target_inv.items():
            if qty <= 0:
                continue
            bank_have = p.bank.get(item, 0)
            # If the preset has a noted item, check bank for the unnoted version
            if bank_have <= 0 and self.cog._is_noted(item):
                unnoted = self.cog._unnote(item)
                bank_have_unnoted = p.bank.get(unnoted, 0)
                take = min(qty, bank_have_unnoted)
                if take > 0:
                    self.cog._remove_item(p.bank, unnoted, take)
                    self.cog._add_item(p.inventory, item, take)
                if take < qty:
                    missing.append(f"{item} x{qty - take}")
            else:
                take = min(qty, bank_have)
                if take > 0:
                    self.cog._remove_item(p.bank, item, take)
                    self.cog._add_item(p.inventory, item, take)
                if take < qty:
                    missing.append(f"{item} x{qty - take}")

        msg = f"Loaded preset **{key}**."
        if missing:
            msg += "\n⚠️ Missing from bank: " + ", ".join(f"**{m}**" for m in missing)
        return True, msg

    def list_presets(self, p: PlayerState) -> List[str]:
        return list(p.presets.keys())

    def _find_key(self, p: PlayerState, name: str) -> Optional[str]:
        lower = name.strip().lower()
        for k in p.presets:
            if k.lower() == lower:
                return k
        return None
