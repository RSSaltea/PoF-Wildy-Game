# pets.py

from typing import Dict, List, Optional, Tuple
from .npcs import NPC_DROPS


def _norm(s: str) -> str:
    return " ".join(str(s).strip().lower().split())


# ---------------------------------------------------------
# Collect all pets dynamically from NPC_DROPS
# ---------------------------------------------------------

def get_all_pets() -> List[str]:
    """
    Returns a sorted list of all pet names defined in NPC_DROPS.
    """
    pets = set()

    for npc_type, data in (NPC_DROPS or {}).items():
        for entry in (data.get("pet", []) or []):
            item = str(entry.get("item", "")).strip()
            if item:
                pets.add(item)

    return sorted(pets, key=lambda s: s.lower())


def get_pet_sources() -> Dict[str, List[Tuple[str, str]]]:
    """
    Returns:
        {
            "Tiny Revenant": [("revenant", "1/1000"), ...],
            ...
        }
    """
    sources: Dict[str, List[Tuple[str, str]]] = {}

    for npc_type, data in (NPC_DROPS or {}).items():
        for entry in (data.get("pet", []) or []):
            pet_name = str(entry.get("item", "")).strip()
            chance = str(entry.get("chance", "Unknown"))

            if not pet_name:
                continue

            sources.setdefault(pet_name, []).append((npc_type, chance))

    return sources


# ---------------------------------------------------------
# Alias system
# ---------------------------------------------------------

PET_ALIASES: Dict[str, str] = {
    # Tiny Revenant
    "tiny rev": "Tiny Revenant",
    "rev pet": "Tiny Revenant",
    "tr": "Tiny Revenant",

    # Mini Overlord
    "mini ol": "Mini Overlord",
    "overlord pet": "Mini Overlord",
    "mo": "Mini Overlord",

    # Zarvethy
    "zarv": "Zarvethy",
    "veil pet": "Zarvethy",

    # Splat
    "valth pet": "Splat",
}


def resolve_pet(query: str) -> Optional[str]:
    """
    Resolves user input into a canonical pet name.
    Accepts:
        - Exact pet name (case-insensitive)
        - Alias
    """
    if not query:
        return None

    q = _norm(query)

    # Alias match
    for alias, name in PET_ALIASES.items():
        if _norm(alias) == q:
            return name

    # Exact match
    for pet in get_all_pets():
        if _norm(pet) == q:
            return pet

    return None