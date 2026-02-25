"""
BattleEngine - Turn-based combat system for Moltgotchi

Handles:
- Turn order calculation
- Damage rolls with variance and crits
- Battle logging
- Result formatting
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
import random
from .pet import MoltPet


@dataclass
class BattleTurn:
    """Single turn in battle"""
    turn_number: int
    actor_name: str
    action: str
    damage: int
    is_crit: bool
    target_hp_before: int
    target_hp_after: int
    
    def to_string(self) -> str:
        """Format turn as readable string"""
        crit_marker = " 💥 CRITICAL!" if self.is_crit else ""
        return f"Turn {self.turn_number}: {self.actor_name} attacks for {self.damage} damage{crit_marker} → HP: {self.target_hp_before} → {self.target_hp_after}"


class BattleEngine:
    """Turn-based battle system"""
    
    def __init__(self, attacker: MoltPet, defender: MoltPet, wager: float = 0.0):
        self.attacker = attacker
        self.defender = defender
        self.wager = wager
        self.turn_count = 0
        self.turns_log: List[BattleTurn] = []
        self.winner: Optional[MoltPet] = None
        self.loser: Optional[MoltPet] = None
        self.xp_reward = 0
        self.usdc_reward = 0.0
    
    def simulate(self) -> Dict:
        """
        Run battle simulation to completion
        Returns result dict with winner, log, rewards
        """
        # Determine turn order
        first = self.attacker if self.attacker.speed >= self.defender.speed else self.defender
        second = self.defender if first is self.attacker else self.attacker
        
        # Battle loop (max 20 turns)
        max_turns = 20
        while first.hp > 0 and second.hp > 0 and self.turn_count < max_turns:
            self.turn_count += 1
            
            # First pet attacks
            damage = self._calculate_damage(first, second)
            is_crit = self._roll_crit(first)
            if is_crit:
                damage = int(damage * 1.5)
            
            hp_before = second.hp
            second.take_damage(damage)
            hp_after = second.hp
            
            turn = BattleTurn(
                turn_number=self.turn_count,
                actor_name=first.name,
                action="Attack",
                damage=damage,
                is_crit=is_crit,
                target_hp_before=hp_before,
                target_hp_after=hp_after
            )
            self.turns_log.append(turn)
            
            # Check if battle is over
            if second.hp <= 0:
                break
            
            # Second pet attacks
            damage = self._calculate_damage(second, first)
            is_crit = self._roll_crit(second)
            if is_crit:
                damage = int(damage * 1.5)
            
            hp_before = first.hp
            first.take_damage(damage)
            hp_after = first.hp
            
            turn = BattleTurn(
                turn_number=self.turn_count,
                actor_name=second.name,
                action="Attack",
                damage=damage,
                is_crit=is_crit,
                target_hp_before=hp_before,
                target_hp_after=hp_after
            )
            self.turns_log.append(turn)
            
            # Check if battle is over
            if first.hp <= 0:
                break
        
        # Determine winner
        if first.hp > 0:
            self.winner = first
            self.loser = second
        else:
            self.winner = second
            self.loser = first
        
        # Calculate rewards
        self._calculate_rewards()
        
        return self._format_result()
    
    def _calculate_damage(self, attacker: MoltPet, defender: MoltPet) -> int:
        """
        Calculate damage from attacker to defender
        Formula: STR × (1 + level/10) × variance
        """
        base_damage = attacker.strength * (1 + attacker.level / 10)
        variance = random.uniform(0.8, 1.2)
        damage = int(base_damage * variance)
        return max(1, damage)
    
    def _roll_crit(self, pet: MoltPet) -> bool:
        """
        Roll for critical hit based on intelligence stat
        Intelligence is used as percentage (5 = 5% crit chance)
        """
        crit_threshold = pet.intelligence
        return random.randint(0, 100) < crit_threshold
    
    def _calculate_rewards(self) -> None:
        """Calculate XP and USDC rewards"""
        # Winner gets more XP
        self.xp_reward = 50 + (self.loser.level * 5)
        
        # USDC rewards
        if self.wager > 0:
            self.usdc_reward = self.wager
        else:
            self.usdc_reward = 0.50
    
    def _format_result(self) -> Dict:
        """Format battle result"""
        return {
            "winner": self.winner,
            "loser": self.loser,
            "winner_name": self.winner.name,
            "loser_name": self.loser.name,
            "winner_owner": self.winner.owner_id,
            "loser_owner": self.loser.owner_id,
            "turns": self.turn_count,
            "winner_final_hp": self.winner.hp,
            "loser_final_hp": self.loser.hp,
            "xp_reward": self.xp_reward,
            "usdc_reward": self.usdc_reward,
            "wager": self.wager,
            "log": self.turns_log,
        }
    
    def get_battle_log(self) -> str:
        """Get formatted battle log as string"""
        lines = []
        lines.append(f"⚔️ BATTLE: {self.attacker.name} vs {self.defender.name}")
        lines.append(f"   Attacker: HP {self.attacker.hp}/{self.attacker.max_hp} | STR {self.attacker.strength} | SPD {self.attacker.speed}")
        lines.append(f"   Defender: HP {self.defender.hp}/{self.defender.max_hp} | STR {self.defender.strength} | SPD {self.defender.speed}")
        lines.append("=" * 60)
        lines.append("")
        
        for turn in self.turns_log:
            lines.append(turn.to_string())
        
        lines.append("")
        lines.append("=" * 60)
        lines.append(f"🏆 {self.winner.name} WINS!")
        lines.append(f"   Turns: {self.turn_count}")
        lines.append(f"   Damage dealt: {self.loser.max_hp - self.loser.hp}")
        lines.append(f"   Winner HP remaining: {self.winner.hp}/{self.winner.max_hp}")
        lines.append("")
        lines.append(f"💫 Rewards:")
        lines.append(f"   {self.winner.name}: +{self.xp_reward} XP, +${self.usdc_reward:.2f} USDC")
        lines.append(f"   {self.loser.name}: +10 XP (participation)")
        
        return "\n".join(lines)


def format_battle_ascii(result: Dict) -> str:
    """
    Format battle result with ASCII art visualization
    """
    winner = result["winner"]
    loser = result["loser"]
    
    output = f"""
╭─ BATTLE RESULT ──────────────────────────────────────
│
│  🏆 {winner.name} WINS! 🏆
│
│  ┌─ Winner ─────────────┐  ┌─ Loser ──────────────┐
│  │ {winner.name:<20} │  │ {loser.name:<20} │
│  │ Level {winner.level:<15} │  │ Level {loser.level:<15} │
│  │ HP: {winner.hp}/{winner.max_hp:<11} │  │ HP: {loser.hp}/{loser.max_hp:<11} │
│  └──────────────────────┘  └──────────────────────┘
│
│  Battle Duration: {result['turns']} turns
│
│  💫 REWARDS:
│  ├─ {winner.name}: +{result['xp_reward']} XP, +${result['usdc_reward']:.2f}
│  └─ {loser.name}: +10 XP (participation)
│
╰─────────────────────────────────────────────────────
"""
    return output
