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
    "Slayer Helmet": {
        "materials": {
            "Black Mask": 1,
            "Chaos rune": 25000,
            "Cyclops Eye": 5,
            "Abyssal charm": 500,
        },
        "description": "A helmet infused with slayer knowledge. Increases damage to slayer task targets by 10%.",
        "requires_unlock": "slayer_helmet",
    },
    "Shady Slayer Helm": {
        "materials": {
            "Slayer Helmet": 1,
            "Shadow Veil": 1,
        },
        "description": "An upgraded slayer helmet shrouded in shadow. Increases damage to slayer task targets by 13% and grants +2 DEF.",
    },
}
