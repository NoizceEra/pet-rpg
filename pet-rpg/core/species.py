"""
Species Data - Pet species definitions and base stats
"""

from typing import Dict

SPECIES_DATA = {
    "MoltCrab": {
        "name": "Molt Crab",
        "base_hp": 30,
        "base_str": 8,
        "base_spd": 5,
        "base_int": 5,
        "color": "#00ffff",
        "description": "A crustacean with a hard shell and sharp claws",
    },
    "Dragon": {
        "name": "Dragon",
        "base_hp": 35,
        "base_str": 12,
        "base_spd": 6,
        "base_int": 8,
        "color": "#ff0000",
        "description": "A fierce fire-breathing reptile",
    },
    "Phoenix": {
        "name": "Phoenix",
        "base_hp": 28,
        "base_str": 10,
        "base_spd": 10,
        "base_int": 10,
        "color": "#ffaa00",
        "description": "A majestic bird that rises from flames",
    },
    "Titan": {
        "name": "Titan",
        "base_hp": 45,
        "base_str": 9,
        "base_spd": 3,
        "base_int": 4,
        "color": "#666666",
        "description": "A colossal creature of immense strength",
    },
    "Mystic": {
        "name": "Mystic",
        "base_hp": 25,
        "base_str": 6,
        "base_spd": 7,
        "base_int": 15,
        "color": "#9900ff",
        "description": "An ethereal being of arcane power",
    },
    "Shadow": {
        "name": "Shadow",
        "base_hp": 30,
        "base_str": 11,
        "base_spd": 9,
        "base_int": 7,
        "color": "#1a1a1a",
        "description": "A creature of darkness and stealth",
    },
    "Gleam": {
        "name": "Gleam",
        "base_hp": 26,
        "base_str": 7,
        "base_spd": 8,
        "base_int": 11,
        "color": "#ffff00",
        "description": "A radiant being of pure light",
    },
    "Nova": {
        "name": "Nova",
        "base_hp": 32,
        "base_str": 10,
        "base_spd": 8,
        "base_int": 9,
        "color": "#ff6600",
        "description": "A celestial entity born from stellar fire",
    },
}


def get_species(species_name: str) -> Dict:
    """Get species data by name"""
    return SPECIES_DATA.get(species_name, SPECIES_DATA["MoltCrab"])


def get_base_stats(species_name: str) -> Dict[str, int]:
    """Get base stats for a species"""
    species = get_species(species_name)
    return {
        "hp": species["base_hp"],
        "strength": species["base_str"],
        "speed": species["base_spd"],
        "intelligence": species["base_int"],
    }


def list_species() -> Dict[str, Dict]:
    """Get all available species"""
    return SPECIES_DATA
