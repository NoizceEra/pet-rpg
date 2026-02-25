"""
Moltgotchi - Autonomous Pet Loop
=================================
A rebranded, persistent upgrade of PetRPG tuned for fast CLI play.
"""

import json
import random
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DATA_DIR = Path("data")
STATE_FILE = DATA_DIR / "moltgotchi_pets.json"
GAME_NAME = "Moltgotchi"


# === ASCII Art Templates ===

PETS = {
    "egg": """
        ┌─────────────┐
        │             │
        │   ╭─────╮   │
        │   │  🦪 │   │
        │   ╰─────╯   │
        │             │
        └─────────────┘
        """,
    "baby": {
        "happy": """
      ╭─────────────────╮
      │  ◕‿◕  BABY     │
      │     ᵔᴥᵔ        │
      │    ___|||___    │
      │   /  ◡◡  \\   │
      ╰─────────────────╯
        """,
        "sad": """
      ╭─────────────────╮
      │  ◕︵◕  BABY     │
      │     ᵔ︵ᵔ        │
      │    ___|||___    │
      │   /  ◠◠  \\   │
      ╰─────────────────╯
        """,
        "battle": """
      ╭─────────────────╮
      │  ◕⚔◕  BABY     │
      │     ᵔ◆ᵔ        │
      │    ___|||___    │
      │   /  ◡◡  \\   │
      ╰─────────────────╯
        """
    },
    "teen": {
        "happy": """
    ╭──────────────────────╮
    │   ∧＿∧  TEEN        │
    │  （｡･ω･)｡          │
    │  /　 ⊂      *:.,    │\n    │  (　)人　♪ ♪       │
    ╰──────────────────────╯
        """,
        "sad": """
    ╭──────────────────────╮
    │   ∧︵∧  TEEN        │
    │  （｡︵｡)｡          │
    │  /　 ⊂       *:.,  │
    │  (　)人　♪ ♪       │
    ╰──────────────────────╯
        """,
        "battle": """
    ╭──────────────────────╮
    │   ∧⚔∧  TEEN        │
    │  （｡･◆･)｡          │
    │  /　 ⊂      *:.,   │
    │  (　)人　♪ ♪       │
    ╰──────────────────────╯
        """
    },
    "adult": {
        "happy": """
        ╭──────────────────────────╮
        │     ∧＿∧   ADULT        │
        │    (｡･ω･｡)★★★          │
        │   /　⊂  oclass         │
        │  ヽ( ・ω・)ノ  °       │
        │   (  且且 且  )         │
        ╰──────────────────────────╯
        """,
        "sad": """
        ╭──────────────────────────╮
        │     ∧︵∧   ADULT        │
        │    (｡︵｡)★★★            │
        │   /　⊂  oclass         │
        │  ヽ( ・ω・)ノ  °       │
        │   (  且且 且  )         │
        ╰──────────────────────────╯
        """,
        "battle": """
        ╭──────────────────────────╮
        │     ∧⚔∧   ADULT        │
        │    (｡･◆･)★★★           │
        │   /　⊂  oclass         │
        │  ヽ( ・ω・)ノ  °       │
        │   (  且且 且  )         │
        ╰──────────────────────────╯
        """
    },
    "legendary": {
        "happy": """
     ✦ ╭──────────────────────────╮ ✦
    ╭╯  │    ∧◇∧  LEGENDARY    │  ╰╮
    │   │   (｡･◆･｡)★★★          │   │
    ╰╮  │  /　⊂   oclass         │  ╭╯
       │  │ ヽ( ◆ω◆)ノ °✦       │ 
     ✦ │   (  ◆且◆  )      ✦   │ ✦
       ╰──────────────────────────╯
        """,
        "battle": """
     ⚔️ ╭──────────────────────────╮ ⚔️
    ╭╯  │    ∧◇∧  LEGENDARY    │  ╰╮
    │   │   (｡･◆･｡)★★★          │   │
    ╰╮  │  /　⊂   oclass         │  ╭╯
       │  │ ヽ( ◆ω◆)ノ °⚔       │ 
     ⚔️ │   (  ◆且◆  )    ⚔️   │ ⚔️
       ╰──────────────────────────╯
        """
    }
}


class PetStage(Enum):
    EGG = "egg"
    BABY = "baby"
    TEEN = "teen"
    ADULT = "adult"
    LEGENDARY = "legendary"


class Mood(Enum):
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    EXCITED = "battle"


STAT_CAP = 100


@dataclass
class Pet:
    name: str
    owner: str = "caretaker"
    stage: PetStage = PetStage.EGG
    hunger: int = 60
    happiness: int = 55
    health: int = 100
    strength: int = 10
    speed: int = 10
    intelligence: int = 10
    level: int = 1
    xp: int = 0
    wins: int = 0
    losses: int = 0
    care_score: int = 50
    kindness: int = 50
    battle_score: int = 0
    eggs_hatched: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_tick: str = field(default_factory=lambda: datetime.now().isoformat())
    last_fed: str = field(default_factory=lambda: datetime.now().isoformat())
    last_played: str = field(default_factory=lambda: datetime.now().isoformat())
    achievements: List[str] = field(default_factory=list)

    # === Core Helpers ===
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "owner": self.owner,
            "stage": self.stage.value,
            "hunger": self.hunger,
            "happiness": self.happiness,
            "health": self.health,
            "strength": self.strength,
            "speed": self.speed,
            "intelligence": self.intelligence,
            "level": self.level,
            "xp": self.xp,
            "wins": self.wins,
            "losses": self.losses,
            "care_score": self.care_score,
            "kindness": self.kindness,
            "battle_score": self.battle_score,
            "eggs_hatched": self.eggs_hatched,
            "created_at": self.created_at,
            "last_tick": self.last_tick,
            "last_fed": self.last_fed,
            "last_played": self.last_played,
            "achievements": self.achievements,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Pet":
        data = data.copy()
        data["stage"] = PetStage(data.get("stage", "egg"))
        return cls(**data)

    # === Progression ===
    def xp_threshold(self) -> int:
        return 120 + (self.level * 45)

    def add_xp(self, amount: int) -> List[str]:
        notes = []
        self.xp += amount
        while self.xp >= self.xp_threshold():
            self.xp -= self.xp_threshold()
            self.level += 1
            self.health = min(STAT_CAP, self.health + 5)
            notes.append(f"⬆️ Level up! {self.name} is now level {self.level}.")
            if self.evolve():
                notes.append(f"✨ Evolution unlocked → {self.stage.value.upper()} stage!")
        return notes

    def evolve(self) -> bool:
        path = [PetStage.EGG, PetStage.BABY, PetStage.TEEN, PetStage.ADULT, PetStage.LEGENDARY]
        idx = path.index(self.stage)
        if idx >= len(path) - 1:
            return False
        gates = [0, 3, 10, 22, 40]
        if self.level >= gates[idx + 1]:
            self.stage = path[idx + 1]
            self.eggs_hatched += 1
            return True
        return False

    def apply_time_decay(self, now: Optional[datetime] = None) -> None:
        now = now or datetime.now()
        last = datetime.fromisoformat(self.last_tick)
        elapsed = max(0.0, (now - last).total_seconds() / 3600)
        if elapsed < 0.1:
            return
        hunger_loss = int(6 * elapsed)
        happiness_loss = int(4 * elapsed)
        self.hunger = max(0, self.hunger - hunger_loss)
        self.happiness = max(0, self.happiness - happiness_loss)
        if self.hunger < 25:
            self.health = max(0, self.health - int(5 * elapsed))
        self.last_tick = now.isoformat()

    def get_mood(self) -> Mood:
        avg = (self.hunger + self.happiness + self.health) / 3
        if avg >= 70:
            return Mood.HAPPY
        if avg >= 40:
            return Mood.SAD
        return Mood.ANGRY

    def get_ascii(self, override: Optional[Mood] = None) -> str:
        mood = override or self.get_mood()
        if self.stage == PetStage.EGG:
            return PETS["egg"]
        art = PETS.get(self.stage.value, {})
        return art.get(mood.value, art.get("happy", PETS["baby"]["happy"]))

    # === Actions ===
    def feed(self) -> List[str]:
        self.apply_time_decay()
        self.hunger = min(STAT_CAP, self.hunger + 35)
        self.happiness = min(STAT_CAP, self.happiness + 5)
        self.care_score = min(STAT_CAP, self.care_score + 4)
        self.last_fed = datetime.now().isoformat()
        return [random.choice([
            "*munches happily*",
            "*shell clacks approvingly*",
            "*tiny burp echoes*",
        ]), "Hunger restored."]

    def play(self) -> List[str]:
        self.apply_time_decay()
        self.happiness = min(STAT_CAP, self.happiness + 30)
        self.hunger = max(0, self.hunger - 10)
        self.speed = min(STAT_CAP, self.speed + 3)
        self.last_played = datetime.now().isoformat()
        return ["*glitchy giggles fill the room*", "Speed +3"]

    def train(self) -> List[str]:
        self.apply_time_decay()
        self.strength = min(STAT_CAP, self.strength + 4)
        self.intelligence = min(STAT_CAP, self.intelligence + 2)
        self.happiness = max(0, self.happiness - 5)
        notes = ["Training montage engaged.", "Strength +4, INT +2"]
        notes += self.add_xp(40)
        return notes

    def rest(self) -> List[str]:
        self.apply_time_decay()
        healed = min(20, STAT_CAP - self.health)
        self.health += healed
        self.happiness = min(STAT_CAP, self.happiness + 5)
        return [f"Power nap complete (+{healed} HP)."]

    def tick_summary(self) -> str:
        last = datetime.fromisoformat(self.last_tick)
        ago = datetime.now() - last
        hours = int(ago.total_seconds() // 3600)
        minutes = int((ago.total_seconds() % 3600) // 60)
        return f"Last upkeep {hours}h {minutes}m ago"

    def status_panel(self) -> str:
        return f"""
╭─ {self.name} | {self.stage.value.upper()} ({GAME_NAME})
│ Level {self.level} | XP {self.xp}/{self.xp_threshold()}
│ Mood: {self.get_mood().name.title()} | {self.tick_summary()}
├─ CARE
│ 🍔 Hunger     {self.hunger:3d}/100
│ 😊 Happiness  {self.happiness:3d}/100
│ ❤️ Health     {self.health:3d}/100
├─ BATTLE
│ ⚔️ STR  {self.strength:3d}   💨 SPD {self.speed:3d}
│ 🧠 INT  {self.intelligence:3d}
├─ RECORDS
│ Wins {self.wins} | Losses {self.losses}
│ Care Score {self.care_score}% | Kindness {self.kindness}%
╰───────────────────────────────
""".strip()


# === Persistence ===

def _load_state() -> Dict[str, Dict]:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except json.JSONDecodeError:
            pass
    return {}


def _save_state(state: Dict[str, Dict]) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def load_pet(name: str, owner: str = "caretaker", auto_create: bool = True) -> Pet:
    state = _load_state()
    key = name.lower()
    if key in state:
        pet = Pet.from_dict(state[key])
    elif auto_create:
        pet = Pet(name=name, owner=owner)
        state[key] = pet.to_dict()
        _save_state(state)
    else:
        raise FileNotFoundError(f"No Moltgotchi named {name}")
    pet.apply_time_decay()
    return pet


def save_pet(pet: Pet) -> None:
    state = _load_state()
    state[pet.name.lower()] = pet.to_dict()
    _save_state(state)


def list_pets() -> List[str]:
    state = _load_state()
    rows = []
    for data in state.values():
        pet = Pet.from_dict(data)
        rows.append(f"- {pet.name} (Lv {pet.level} {pet.stage.value}) | mood {pet.get_mood().name}")
    return rows


# === CLI ===

def print_usage():
    print(f"{GAME_NAME} CLI")
    print("Usage:")
    print("  python pet.py list")
    print("  python pet.py create <name> [owner]")
    print("  python pet.py <name> [status|feed|play|train|rest|ascii|tick]")


def main():
    import sys

    if len(sys.argv) == 1:
        print_usage()
        return

    cmd = sys.argv[1].lower()

    if cmd == "list":
        pets = list_pets()
        if not pets:
            print("No Moltgotchi registered yet. Use 'create <name>'.")
        else:
            print("Registered Moltgotchi:")
            for row in pets:
                print("  " + row)
        return

    if cmd == "create":
        if len(sys.argv) < 3:
            print("Provide a pet name: python pet.py create <name>")
            return
        name = sys.argv[2]
        owner = sys.argv[3] if len(sys.argv) > 3 else "caretaker"
        pet = load_pet(name, owner, auto_create=True)
        save_pet(pet)
        print(f"Created Moltgotchi '{name}' for {owner}.")
        print(pet.status_panel())
        return

    # Otherwise treat first arg as pet name
    name = sys.argv[1]
    action = sys.argv[2].lower() if len(sys.argv) > 2 else "status"

    pet = load_pet(name)
    output: List[str] = []

    if action == "status":
        output.append(pet.status_panel())
        output.append(pet.get_ascii())
    elif action == "feed":
        output += pet.feed()
        output.append(pet.status_panel())
        output.append(pet.get_ascii())
    elif action == "play":
        output += pet.play()
        output.append(pet.status_panel())
    elif action == "train":
        output += pet.train()
        output.append(pet.status_panel())
    elif action == "rest":
        output += pet.rest()
        output.append(pet.status_panel())
    elif action == "ascii":
        output.append(pet.get_ascii())
    elif action == "tick":
        before = pet.tick_summary()
        pet.apply_time_decay()
        after = pet.tick_summary()
        output.append(f"Decay synced. {before} -> {after}")
    else:
        output.append(f"Unknown action '{action}'.")
        output.append("Try status|feed|play|train|rest|ascii|tick")

    save_pet(pet)
    print("\n".join(output))


if __name__ == "__main__":
    main()
