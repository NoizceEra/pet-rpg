"""Moltgotchi Core Game Engine

Complete game mechanics for Moltgotchi:
- Pet management and lifecycle
- Battle system
- Evolution mechanics
- Species definitions
"""

from .pet import MoltPet, PetStage, EvolutionPath, Mood
from .battle import BattleEngine, BattleTurn, format_battle_ascii
from .evolution import EvolutionSystem, EvolutionEvent, EVOLUTION_FORMS
from .species import SPECIES_DATA, get_species, get_base_stats, list_species

__all__ = [
    # Pet classes
    "MoltPet",
    "PetStage",
    "EvolutionPath",
    "Mood",
    # Battle classes
    "BattleEngine",
    "BattleTurn",
    "format_battle_ascii",
    # Evolution classes
    "EvolutionSystem",
    "EvolutionEvent",
    "EVOLUTION_FORMS",
    # Species
    "SPECIES_DATA",
    "get_species",
    "get_base_stats",
    "list_species",
]
