# Crafting recipes

from typing import Dict, Any

CRAFTABLES: Dict[str, Dict[str, Any]] = {
    "Bone Defender": {
        "materials": {
            "Rune Defender": 1,
            "Cursed Bone": 30,
            "Revenant ether": 2000,
            "Revenant Relic Shard": 10,
            "Revenant Totem": 2,
        },
        "description": "A defender forged from cursed bones, stronger than rune. Requires materials from the Revenant Archon.",
    },
    "Abyssal Chainmace": {
        "materials": {
            "Overlord core fragment": 100,
            "Abyssal ash": 2000,
            "Cyclops Eye": 1,
            "Revenant ether": 10000,
            "Viggora's Chainmace": 1,
        },
        "description": "A devastating mace forged from abyssal remnants. Consumes 3 Revenant ether per hit for a massive NPC attack bonus.",
    },
}
