from typing import Dict, List, Optional, Tuple
from .npcs import NPC_DROPS

def _norm(s: str) -> str:
    return " ".join(str(s).strip().lower().split())

def get_all_pets() -> List[str]:
    pets = set()

    for npc_type, data in (NPC_DROPS or {}).items():
        for entry in (data.get("pet", []) or []):
            item = str(entry.get("item", "")).strip()
            if item:
                pets.add(item)

    return sorted(pets, key=lambda s: s.lower())

def get_pet_sources() -> Dict[str, List[Tuple[str, str]]]:
    sources: Dict[str, List[Tuple[str, str]]] = {}

    for npc_type, data in (NPC_DROPS or {}).items():
        for entry in (data.get("pet", []) or []):
            pet_name = str(entry.get("item", "")).strip()
            chance = str(entry.get("chance", "Unknown"))

            if not pet_name:
                continue

            sources.setdefault(pet_name, []).append((npc_type, chance))

    return sources

PET_ALIASES: Dict[str, str] = {
    "tiny rev": "Tiny Revenant",
    "rev pet": "Tiny Revenant",
    "tr": "Tiny Revenant",

    "mini ol": "Mini Overlord",
    "overlord pet": "Mini Overlord",
    "mo": "Mini Overlord",

    "zarv": "Zarvethy",
    "veil pet": "Zarvethy",

    "valth pet": "Splat",
}

def resolve_pet(query: str) -> Optional[str]:
    if not query:
        return None

    q = _norm(query)

    for alias, name in PET_ALIASES.items():
        if _norm(alias) == q:
            return name

    for pet in get_all_pets():
        if _norm(pet) == q:
            return pet

    return None