"""
Moltgotchi Battle System
========================
Turn-based Moltgotchi duels using persisted pet data.
"""

import random
from typing import Dict

from pet import Mood, Pet, load_pet, save_pet


class Battle:
    def __init__(self, pet1: Pet, pet2: Pet):
        self.pet1 = pet1
        self.pet2 = pet2
        self.turn = 1
        self.log = []

    def calculate_damage(self, attacker: Pet, defender: Pet) -> int:
        base = attacker.strength * 2
        speed_bonus = (attacker.speed - defender.speed) * 0.5
        crit_chance = attacker.intelligence / 200
        is_crit = random.random() < crit_chance
        damage = int(base + speed_bonus)
        if is_crit:
            damage *= 2
            self.log.append("💥 CRITICAL HIT!")
        variance = random.randint(-3, 3)
        damage = max(1, damage + variance)
        return damage

    def fight(self) -> Dict:
        self.log.append(f"⚔️ BATTLE: {self.pet1.name} vs {self.pet2.name} ⚔️")
        self.log.append("")

        attacker, defender = (
            (self.pet1, self.pet2) if self.pet1.speed >= self.pet2.speed else (self.pet2, self.pet1)
        )

        while self.pet1.health > 0 and self.pet2.health > 0:
            self.log.append(f"--- Turn {self.turn} ---")
            damage = self.calculate_damage(attacker, defender)
            defender.health = max(0, defender.health - damage)
            self.log.append(f"{attacker.name} attacks!")
            self.log.append(f"💥 {damage} damage to {defender.name}")
            self.log.append(f"{defender.name} HP: {defender.health}")
            self.log.append("")
            if defender.health <= 0:
                break
            attacker, defender = defender, attacker
            self.turn += 1

        winner = self.pet1 if self.pet1.health > 0 else self.pet2
        loser = self.pet2 if winner is self.pet1 else self.pet1

        xp_gained = 50 + (loser.level * 10)
        notes = winner.add_xp(xp_gained)
        winner.wins += 1
        loser.losses += 1

        self.log.append(f"🏆 {winner.name} WINS!")
        self.log.append(f"💫 +{xp_gained} XP to {winner.name}")
        self.log += notes

        return {
            "winner": winner,
            "loser": loser,
            "turns": self.turn,
            "xp_gained": xp_gained,
            "log": self.log,
        }

    def auto_battle(self) -> str:
        result = self.fight()
        save_pet(result["winner"])
        save_pet(result["loser"])
        return (
            "\n".join(result["log"]) +
            "\n" +
            f"╭─ RESULT ───────────────╮\n"
            f"│ Winner: {result['winner'].name}\n"
            f"│ Turns: {result['turns']}\n"
            f"│ XP: +{result['xp_gained']}\n"
            f"╰────────────────────────╯"
        )


def cli():
    import sys

    if len(sys.argv) < 3:
        print("Usage: python battle.py <pet_one> <pet_two>")
        return

    name1, name2 = sys.argv[1], sys.argv[2]
    pet1 = load_pet(name1)
    pet2 = load_pet(name2)
    duel = Battle(pet1, pet2)
    print(duel.auto_battle())


if __name__ == "__main__":
    cli()
