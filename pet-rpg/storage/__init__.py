"""Moltgotchi Storage Layer

Provides persistence for pets and battles
"""

from .pet_storage import (
    PetStorage,
    save_pet,
    load_pet,
    pet_exists,
    get_pets_by_owner,
    get_all_pets,
    delete_pet,
    backup_pets,
)

from .battle_storage import (
    BattleStorage,
    save_battle,
    load_battle,
    get_battles_by_pet,
    get_battles_by_owner,
    get_all_battles,
    get_head_to_head,
)

__all__ = [
    "PetStorage",
    "save_pet",
    "load_pet",
    "pet_exists",
    "get_pets_by_owner",
    "get_all_pets",
    "delete_pet",
    "backup_pets",
    "BattleStorage",
    "save_battle",
    "load_battle",
    "get_battles_by_pet",
    "get_battles_by_owner",
    "get_all_battles",
    "get_head_to_head",
]
