"""
Evolution System - Pet evolution mechanics

Handles:
- Evolution stage transitions
- Evolution path determination (Guardian/Balanced/Warrior)
- Stat bonuses and ability unlocks
- Visual transformations (ASCII art)
"""

from enum import Enum
from typing import Dict, List, Optional
from .pet import MoltPet, PetStage, EvolutionPath


# ASCII art for different evolution paths
EVOLUTION_FORMS = {
    PetStage.EGG: {
        "ascii": """
        ◯
       ◉◯◉
        ◯
""",
        "description": "Egg (Unhatched)"
    },
    PetStage.BABY: {
        "guardian": {
            "ascii": """
       /\\_/\\
      ( ◕.◕ )
       > + <
      /|███|\\
     (_|███|_)
    ✨Shiny Shell✨
""",
            "description": "Guardian Baby (Bright & Shiny)"
        },
        "warrior": {
            "ascii": """
       /\\_/\\
      ( ●.● )
       > < <
      /|███|\\
     (_|███|_)
    ⚫Dark Shell⚫
""",
            "description": "Warrior Baby (Dark & Scarred)"
        },
        "balanced": {
            "ascii": """
       /\\_/\\
      ( o.o )
       > ^ <
      /|███|\\
     (_|███|_)
    Standard Shell
""",
            "description": "Balanced Baby (Natural)"
        },
        "default": {
            "ascii": """
       /\\_/\\
      ( o.o )
       > ^ <
      /|   |\\
     (_|   |_)
""",
            "description": "Baby (Not yet evolved)"
        }
    },
    PetStage.TEEN: {
        "guardian": {
            "ascii": """
       /\\_/\\
      ( ◎.◎ )
       > + <
      /|███████|\\
     (_|███████|_)
    ⭐RADIANT FORM⭐
""",
            "description": "Guardian Teen (Radiant)"
        },
        "warrior": {
            "ascii": """
       /\\_/\\
      ( ●.● )
       > W <
      /|███████|\\
     (_|███████|_)
    ⚔️SAVAGE FORM⚔️
""",
            "description": "Warrior Teen (Savage)"
        },
        "balanced": {
            "ascii": """
       /\\_/\\
      ( o.o )
       > ^ <
      /|█████|\\
     (_|█████|_)
    🌙BALANCED FORM🌙
""",
            "description": "Balanced Teen (Versatile)"
        }
    },
    PetStage.ADULT: {
        "guardian": {
            "ascii": """
       /\\_/\\
      ( ◎.◎ )
       > + <
      /|███████|\\
     (_|███████|_)
    🟡ETERNAL GUARDIAN🟡
""",
            "description": "Guardian Adult (Eternal)"
        },
        "warrior": {
            "ascii": """
       /\\_/\\
      ( ●.● )
       > W <
      /|███████|\\
     (_|███████|_)
    ◆UNCHAINED WARRIOR◆
""",
            "description": "Warrior Adult (Unchained)"
        },
        "balanced": {
            "ascii": """
       /\\_/\\
      ( o.o )
       > ^ <
      /|█████|\\
     (_|█████|_)
    ⭐INFINITE BALANCED⭐
""",
            "description": "Balanced Adult (Infinite)"
        }
    },
    PetStage.LEGENDARY: {
        "guardian": {
            "ascii": """
    ✦ ╭──────────╮ ✦
   ╭╯  │∧◇∧      │  ╰╮
   │   │(◎◎)★★★  │   │
   ╰╮  │ > + <    │  ╭╯
     │  │/|███|\\  │ 
   ✦ │  (_|███|_) │ ✦
      ╰──────────╯
""",
            "description": "Legendary Guardian (Ascended)"
        },
        "warrior": {
            "ascii": """
    ⚔️ ╭──────────╮ ⚔️
   ╭╯  │∧◇∧      │  ╰╮
   │   │(●●)★★★  │   │
   ╰╮  │ > W <    │  ╭╯
     │  │/|███|\\  │ 
   ⚔️ │  (_|███|_) │ ⚔️
      ╰──────────╯
""",
            "description": "Legendary Warrior (Ascended)"
        },
        "balanced": {
            "ascii": """
    🌟 ╭──────────╮ 🌟
   ╭╯  │∧◇∧      │  ╰╮
   │   │(o◆o)★★★ │   │
   ╰╮  │ > ^ <    │  ╭╯
     │  │/|█████| │ 
   🌟 │  (_|█████|_)🌟
      ╰──────────╯
""",
            "description": "Legendary Balanced (Ascended)"
        }
    }
}


class EvolutionEvent:
    """Represents an evolution event"""
    
    def __init__(self, pet_name: str, old_stage: PetStage, new_stage: PetStage, 
                 path: Optional[EvolutionPath] = None, stat_boosts: Optional[Dict] = None):
        self.pet_name = pet_name
        self.old_stage = old_stage
        self.new_stage = new_stage
        self.path = path
        self.stat_boosts = stat_boosts or {}
        self.message = self._generate_message()
    
    def _generate_message(self) -> str:
        """Generate evolution message"""
        if self.path:
            return f"✨ {self.pet_name} evolved to {self.new_stage.value} ({self.path.value})! ✨"
        else:
            return f"✨ {self.pet_name} evolved to {self.new_stage.value}! ✨"
    
    def __str__(self) -> str:
        return self.message


class EvolutionSystem:
    """Manages pet evolution"""
    
    # Evolution level gates
    EVOLUTION_GATES = {
        PetStage.EGG: 0,
        PetStage.BABY: 3,
        PetStage.TEEN: 10,
        PetStage.ADULT: 25,
        PetStage.LEGENDARY: 50
    }
    
    # Path-specific stat multipliers
    PATH_MULTIPLIERS = {
        EvolutionPath.GUARDIAN: {
            "max_hp": 1.3,
            "strength": 1.0,
            "speed": 1.0,
            "intelligence": 1.0,
        },
        EvolutionPath.WARRIOR: {
            "max_hp": 1.0,
            "strength": 1.25,
            "speed": 1.1,
            "intelligence": 1.0,
        },
        EvolutionPath.BALANCED: {
            "max_hp": 1.0,
            "strength": 1.0,
            "speed": 1.0,
            "intelligence": 1.2,
        }
    }
    
    # Ability unlocks by stage and path
    ABILITY_UNLOCKS = {
        PetStage.BABY: {
            EvolutionPath.GUARDIAN: ["Heal"],
            EvolutionPath.WARRIOR: ["Rampage"],
            EvolutionPath.BALANCED: ["Adapt"],
        },
        PetStage.TEEN: {
            EvolutionPath.GUARDIAN: ["Guardian Shield"],
            EvolutionPath.WARRIOR: ["Power Strike"],
            EvolutionPath.BALANCED: ["Mimic"],
        },
        PetStage.ADULT: {
            EvolutionPath.GUARDIAN: ["Healing Aura"],
            EvolutionPath.WARRIOR: ["Devastating Blow"],
            EvolutionPath.BALANCED: ["Perfect Form"],
        },
        PetStage.LEGENDARY: {
            EvolutionPath.GUARDIAN: ["Eternal Guardian"],
            EvolutionPath.WARRIOR: ["Ultimate Rampage"],
            EvolutionPath.BALANCED: ["Transcendence"],
        }
    }
    
    @staticmethod
    def get_evolution_gates() -> Dict[PetStage, int]:
        """Get level requirements for each evolution stage"""
        return EvolutionSystem.EVOLUTION_GATES
    
    @staticmethod
    def should_evolve(pet: MoltPet) -> bool:
        """Check if pet should evolve to next stage"""
        current_stage = pet.evolution_stage
        
        # Can't evolve past legendary
        if current_stage == PetStage.LEGENDARY:
            return False
        
        # Get next stage
        stage_order = [PetStage.EGG, PetStage.BABY, PetStage.TEEN, PetStage.ADULT, PetStage.LEGENDARY]
        current_idx = stage_order.index(current_stage)
        next_stage = stage_order[current_idx + 1]
        
        # Check if level gate is met
        required_level = EvolutionSystem.EVOLUTION_GATES[next_stage]
        return pet.level >= required_level
    
    @staticmethod
    def evolve_pet(pet: MoltPet) -> Optional[EvolutionEvent]:
        """
        Evolve pet to next stage
        Returns EvolutionEvent if evolution happened, None otherwise
        """
        if not EvolutionSystem.should_evolve(pet):
            return None
        
        old_stage = pet.evolution_stage
        
        # Get next stage
        stage_order = [PetStage.EGG, PetStage.BABY, PetStage.TEEN, PetStage.ADULT, PetStage.LEGENDARY]
        current_idx = stage_order.index(old_stage)
        next_stage = stage_order[current_idx + 1]
        
        # Update stage
        pet.evolution_stage = next_stage
        
        # Determine path if evolving to TEEN
        if next_stage == PetStage.TEEN:
            EvolutionSystem._determine_path(pet)
        
        # Apply stat bonuses
        stat_boosts = EvolutionSystem._apply_stage_bonuses(pet, next_stage)
        
        # Unlock abilities
        if pet.evolution_path and next_stage in EvolutionSystem.ABILITY_UNLOCKS:
            new_abilities = EvolutionSystem.ABILITY_UNLOCKS[next_stage].get(pet.evolution_path, [])
            for ability in new_abilities:
                if ability not in pet.abilities:
                    pet.abilities.append(ability)
        
        return EvolutionEvent(pet.name, old_stage, next_stage, pet.evolution_path, stat_boosts)
    
    @staticmethod
    def _determine_path(pet: MoltPet) -> None:
        """
        Determine evolution path based on care score
        Called when evolving from BABY to TEEN
        """
        if pet.evolution_path is not None:
            return  # Already determined
        
        care = pet.care_score
        
        if care >= 80:
            pet.evolution_path = EvolutionPath.GUARDIAN
        elif care < 30:
            pet.evolution_path = EvolutionPath.WARRIOR
        else:
            pet.evolution_path = EvolutionPath.BALANCED
    
    @staticmethod
    def _apply_stage_bonuses(pet: MoltPet, stage: PetStage) -> Dict[str, float]:
        """Apply stat bonuses for evolution stage"""
        boosts = {}
        
        if stage == PetStage.BABY:
            pet.max_hp = int(pet.max_hp * 1.2)
            boosts["max_hp"] = 1.2
        
        elif stage == PetStage.TEEN:
            # Apply path multipliers
            if pet.evolution_path:
                multipliers = EvolutionSystem.PATH_MULTIPLIERS[pet.evolution_path]
                pet.max_hp = int(pet.max_hp * multipliers["max_hp"])
                pet.strength = int(pet.strength * multipliers["strength"])
                pet.speed = int(pet.speed * multipliers["speed"])
                pet.intelligence = int(pet.intelligence * multipliers["intelligence"])
                boosts = multipliers
            else:
                # Fallback if no path (shouldn't happen)
                pet.max_hp = int(pet.max_hp * 1.15)
                boosts["max_hp"] = 1.15
        
        elif stage == PetStage.ADULT:
            pet.strength += 3
            pet.speed += 2
            pet.max_hp = int(pet.max_hp * 1.15)
            boosts["strength"] = 3
            boosts["speed"] = 2
            boosts["max_hp"] = 1.15
        
        elif stage == PetStage.LEGENDARY:
            pet.strength += 5
            pet.speed += 3
            pet.intelligence += 3
            pet.max_hp = int(pet.max_hp * 1.2)
            boosts["strength"] = 5
            boosts["speed"] = 3
            boosts["intelligence"] = 3
            boosts["max_hp"] = 1.2
        
        return boosts
    
    @staticmethod
    def get_evolution_form(pet: MoltPet) -> str:
        """Get ASCII art for pet's current evolution form"""
        stage = pet.evolution_stage
        
        if stage not in EVOLUTION_FORMS:
            return ""
        
        form_data = EVOLUTION_FORMS[stage]
        
        # For stages with paths
        if isinstance(form_data, dict) and pet.evolution_path:
            path_key = pet.evolution_path.value.lower()
            if path_key in form_data:
                return form_data[path_key].get("ascii", form_data.get("default", {}).get("ascii", ""))
        
        # Fallback
        if "ascii" in form_data:
            return form_data["ascii"]
        
        if "default" in form_data:
            return form_data["default"].get("ascii", "")
        
        return ""
    
    @staticmethod
    def get_evolution_description(pet: MoltPet) -> str:
        """Get description of pet's current evolution form"""
        stage = pet.evolution_stage
        
        if stage not in EVOLUTION_FORMS:
            return "Unknown form"
        
        form_data = EVOLUTION_FORMS[stage]
        
        # For stages with paths
        if isinstance(form_data, dict) and pet.evolution_path:
            path_key = pet.evolution_path.value.lower()
            if path_key in form_data:
                return form_data[path_key].get("description", "Unknown")
        
        # Fallback
        if "description" in form_data:
            return form_data["description"]
        
        if "default" in form_data:
            return form_data["default"].get("description", "Unknown")
        
        return "Unknown"
    
    @staticmethod
    def get_evolution_progress(pet: MoltPet) -> Dict:
        """Get evolution progress info"""
        stage_order = [PetStage.EGG, PetStage.BABY, PetStage.TEEN, PetStage.ADULT, PetStage.LEGENDARY]
        current_idx = stage_order.index(pet.evolution_stage)
        
        # Current stage gate
        current_gate = EvolutionSystem.EVOLUTION_GATES[pet.evolution_stage]
        
        # Next stage
        if current_idx < len(stage_order) - 1:
            next_stage = stage_order[current_idx + 1]
            next_gate = EvolutionSystem.EVOLUTION_GATES[next_stage]
            levels_until = max(0, next_gate - pet.level)
        else:
            next_stage = None
            next_gate = None
            levels_until = 0
        
        return {
            "current_stage": pet.evolution_stage.value,
            "next_stage": next_stage.value if next_stage else None,
            "levels_until_evolution": levels_until,
            "can_evolve": EvolutionSystem.should_evolve(pet),
            "evolution_path": pet.evolution_path.value if pet.evolution_path else None,
        }
