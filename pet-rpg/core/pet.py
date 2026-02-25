"""
MoltPet Class - Core pet implementation for Moltgotchi

Handles:
- Pet stats and lifecycle
- Care mechanics (hunger, happiness, health decay)
- XP progression and level-ups
- Evolution triggers
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple
import random
import json


class PetStage(Enum):
    """Pet evolution stages"""
    EGG = "EGG"
    BABY = "BABY"
    TEEN = "TEEN"
    ADULT = "ADULT"
    LEGENDARY = "LEGENDARY"


class EvolutionPath(Enum):
    """Pet evolution paths based on care score"""
    GUARDIAN = "GUARDIAN"      # Care ≥ 80%: HP focus, healing
    BALANCED = "BALANCED"      # Care 30-70%: all-rounder
    WARRIOR = "WARRIOR"        # Care < 30%: STR focus, offensive


class Mood(Enum):
    """Pet mood based on well-being"""
    HAPPY = "happy"
    CONTENT = "content"
    UNHAPPY = "unhappy"
    CRITICAL = "critical"


@dataclass
class MoltPet:
    """A Moltgotchi pet with full game state"""
    
    # === Identity ===
    pet_id: str
    owner_id: str
    name: str
    species: str = "MoltCrab"
    color: str = "#00ffff"  # Hex color for pet
    
    # === Progression ===
    level: int = 1
    xp: int = 0
    xp_to_level: int = 100
    
    # === Stats ===
    hp: int = 30
    max_hp: int = 30
    hunger: int = 100         # 0-100
    happiness: int = 100      # 0-100
    
    strength: int = 8
    speed: int = 5
    intelligence: int = 5     # As percentage (5 = 5% crit)
    
    # === Evolution ===
    evolution_stage: PetStage = PetStage.EGG
    evolution_path: Optional[EvolutionPath] = None
    care_score: float = 100.0  # 0-100 average of hunger/happiness
    
    # === Battle Stats ===
    battles_total: int = 0
    battles_won: int = 0
    battles_lost: int = 0
    current_streak: int = 0
    max_streak: int = 0
    
    # === Timestamps ===
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_fed: str = field(default_factory=lambda: datetime.now().isoformat())
    last_played: str = field(default_factory=lambda: datetime.now().isoformat())
    last_battle: str = field(default_factory=lambda: datetime.now().isoformat())
    last_decay: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # === Abilities (unlocked through evolution) ===
    abilities: List[str] = field(default_factory=lambda: ["Basic Attack"])
    
    def __post_init__(self):
        """Validate on creation"""
        if not self.pet_id or not self.owner_id:
            raise ValueError("pet_id and owner_id required")
    
    # ===== CARE MECHANICS =====
    
    def feed(self) -> str:
        """Feed the pet: restore hunger, increase happiness"""
        self.hunger = min(100, self.hunger + 30)
        self.happiness = min(100, self.happiness + 10)
        self.last_fed = datetime.now().isoformat()
        self.xp += 10
        self._check_level_up()
        return f"🍖 {self.name} eats happily! Hunger: +30"
    
    def play(self) -> str:
        """Play with pet: increase happiness, decrease hunger"""
        self.happiness = min(100, self.happiness + 25)
        self.hunger = max(0, self.hunger - 10)
        self.last_played = datetime.now().isoformat()
        self.xp += 25
        self._check_level_up()
        return f"🎮 {self.name} plays joyfully! Happiness: +25"
    
    def train(self, stat: str) -> str:
        """Train a stat: strength, speed, or intelligence"""
        stat = stat.lower()
        if stat == "strength" or stat == "str":
            self.strength += 1
            stat_name = "strength"
        elif stat == "speed" or stat == "spd":
            self.speed += 1
            stat_name = "speed"
        elif stat == "intelligence" or stat == "int":
            self.intelligence += 1
            stat_name = "intelligence"
        else:
            return f"❌ Unknown stat: {stat}. Try: strength, speed, intelligence"
        
        self.hunger -= 15
        self.xp += 20
        self.hunger = max(0, self.hunger)
        self._check_level_up()
        return f"💪 {self.name} trained {stat_name}! +1 {stat_name}"
    
    def rest(self) -> str:
        """Rest: restore HP and reduce decay"""
        heal_amount = min(20, self.max_hp - self.hp)
        self.hp += heal_amount
        self.happiness = min(100, self.happiness + 5)
        return f"😴 {self.name} rests peacefully... +{heal_amount} HP"
    
    # ===== TIME DECAY =====
    
    def apply_decay(self, hours_elapsed: float = None) -> None:
        """
        Apply hunger/happiness decay over time
        Called every sync to simulate time passing
        """
        if hours_elapsed is None:
            now = datetime.fromisoformat(self.last_decay)
            hours_elapsed = (datetime.now() - now).total_seconds() / 3600
        
        if hours_elapsed < 0.1:  # Ignore very small time deltas
            return
        
        # Hunger decreases ~6% per hour
        hunger_loss = int(6 * hours_elapsed)
        self.hunger = max(0, self.hunger - hunger_loss)
        
        # Happiness decreases ~4% per hour
        happiness_loss = int(4 * hours_elapsed)
        self.happiness = max(0, self.happiness - happiness_loss)
        
        # If starving, take health damage
        if self.hunger < 25:
            health_loss = int(5 * hours_elapsed)
            self.hp = max(0, self.hp - health_loss)
        
        self.last_decay = datetime.now().isoformat()
        self._update_care_score()
    
    def _update_care_score(self) -> None:
        """Update care score: average of hunger/happiness normalized"""
        self.care_score = (self.hunger + self.happiness) / 2.0
    
    # ===== COMBAT =====
    
    def take_damage(self, damage: int) -> bool:
        """Apply damage. Returns True if pet faints"""
        self.hp = max(0, self.hp - damage)
        return self.hp <= 0
    
    def get_battle_stats(self) -> Dict[str, int]:
        """Get combat-relevant stats"""
        return {
            "hp": self.hp,
            "max_hp": self.max_hp,
            "strength": self.strength,
            "speed": self.speed,
            "intelligence": self.intelligence,
            "level": self.level
        }
    
    def record_battle_result(self, won: bool, xp_gained: int = 50) -> None:
        """Record battle result and update stats"""
        self.battles_total += 1
        self.last_battle = datetime.now().isoformat()
        self.xp += xp_gained
        
        if won:
            self.battles_won += 1
            self.current_streak += 1
            self.max_streak = max(self.max_streak, self.current_streak)
        else:
            self.battles_lost += 1
            self.current_streak = 0
        
        self._check_level_up()
    
    def get_winrate(self) -> float:
        """Get battle win rate as percentage"""
        if self.battles_total == 0:
            return 0.0
        return (self.battles_won / self.battles_total) * 100
    
    # ===== PROGRESSION =====
    
    def _check_level_up(self) -> bool:
        """Check if pet should level up. Returns True if leveled."""
        if self.xp >= self.xp_to_level:
            self.xp -= self.xp_to_level
            self.level += 1
            self.max_hp += 5
            self.hp = min(self.max_hp, self.hp + 5)  # Heal on level up
            self.xp_to_level = int(self.xp_to_level * 1.1)  # 10% increase
            self._check_evolution()
            return True
        return False
    
    def _check_evolution(self) -> bool:
        """Check if pet should evolve. Returns True if evolved."""
        # Evolution gates based on stage
        evolution_path = [
            (PetStage.EGG, 0),
            (PetStage.BABY, 3),
            (PetStage.TEEN, 10),
            (PetStage.ADULT, 25),
            (PetStage.LEGENDARY, 50)
        ]
        
        for stage, min_level in evolution_path:
            if self.level >= min_level and self.evolution_stage.value < stage.value:
                self.evolution_stage = stage
                
                # Determine evolution path if transitioning to TEEN
                if stage == PetStage.TEEN:
                    self._determine_evolution_path()
                
                # Apply stat bonuses based on path
                self._apply_evolution_bonuses(stage)
                
                return True
        
        return False
    
    def _determine_evolution_path(self) -> None:
        """Determine evolution path based on care score at TEEN evolution"""
        if self.evolution_path is not None:
            return  # Already determined
        
        if self.care_score >= 80:
            self.evolution_path = EvolutionPath.GUARDIAN
            self.max_hp = int(self.max_hp * 1.3)
            self.abilities.append("Heal")
        elif self.care_score < 30:
            self.evolution_path = EvolutionPath.WARRIOR
            self.strength = int(self.strength * 1.25)
            self.speed = int(self.speed * 1.1)
            self.abilities.append("Rampage")
        else:
            self.evolution_path = EvolutionPath.BALANCED
            self.intelligence += 2
            self.abilities.append("Adapt")
    
    def _apply_evolution_bonuses(self, stage: PetStage) -> None:
        """Apply stat bonuses on evolution"""
        if stage == PetStage.TEEN:
            self.max_hp = int(self.max_hp * 1.2)
        elif stage == PetStage.ADULT:
            self.strength += 3
            self.speed += 2
            self.max_hp = int(self.max_hp * 1.15)
        elif stage == PetStage.LEGENDARY:
            self.strength += 5
            self.speed += 3
            self.intelligence += 3
            self.max_hp = int(self.max_hp * 1.2)
    
    # ===== STATUS & INFO =====
    
    def get_mood(self) -> Mood:
        """Determine mood from well-being stats"""
        avg_wellbeing = (self.hunger + self.happiness) / 2
        
        if avg_wellbeing >= 70:
            return Mood.HAPPY
        elif avg_wellbeing >= 40:
            return Mood.CONTENT
        elif avg_wellbeing >= 20:
            return Mood.UNHAPPY
        else:
            return Mood.CRITICAL
    
    def get_status_bar(self) -> str:
        """ASCII status bar display"""
        return f"""
╭─ {self.name} | Level {self.level} {self.evolution_stage.value}
│ HP:   {'█' * int(self.hp / self.max_hp * 10)}{'░' * (10 - int(self.hp / self.max_hp * 10))} {self.hp}/{self.max_hp}
│ Hunger: {'█' * int(self.hunger / 10)}{'░' * (10 - int(self.hunger / 10))} {int(self.hunger)}%
│ Happy:  {'█' * int(self.happiness / 10)}{'░' * (10 - int(self.happiness / 10))} {int(self.happiness)}%
│
│ STR: {self.strength:3d} | SPD: {self.speed:3d} | INT: {self.intelligence:3d}%
│ Mood: {self.get_mood().name} | Care: {self.care_score:.1f}%
│
│ Battles: {self.battles_won}W {self.battles_lost}L | Streak: {self.current_streak}
╰─ XP: {self.xp}/{self.xp_to_level}
"""
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary for storage"""
        return {
            "pet_id": self.pet_id,
            "owner_id": self.owner_id,
            "name": self.name,
            "species": self.species,
            "color": self.color,
            "level": self.level,
            "xp": self.xp,
            "xp_to_level": self.xp_to_level,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "hunger": self.hunger,
            "happiness": self.happiness,
            "strength": self.strength,
            "speed": self.speed,
            "intelligence": self.intelligence,
            "evolution_stage": self.evolution_stage.value,
            "evolution_path": self.evolution_path.value if self.evolution_path else None,
            "care_score": self.care_score,
            "battles_total": self.battles_total,
            "battles_won": self.battles_won,
            "battles_lost": self.battles_lost,
            "current_streak": self.current_streak,
            "max_streak": self.max_streak,
            "created_at": self.created_at,
            "last_fed": self.last_fed,
            "last_played": self.last_played,
            "last_battle": self.last_battle,
            "last_decay": self.last_decay,
            "abilities": self.abilities,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "MoltPet":
        """Deserialize from dictionary"""
        data = data.copy()
        data["evolution_stage"] = PetStage[data.get("evolution_stage", "EGG")]
        path = data.get("evolution_path")
        data["evolution_path"] = EvolutionPath[path] if path else None
        return cls(**data)
