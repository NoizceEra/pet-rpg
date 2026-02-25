"""
ASCII Rendering Engine for Moltgotchi

Renders:
- Pet sprites per species / stage / mood
- Status panels with HP/hunger/happiness bars
- Battle screens (intro, turn-by-turn, result)
- Leaderboard tables
- Evolution ceremony
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.pet import MoltPet, PetStage, EvolutionPath, Mood


# ─────────────────────────────────────────────
#  SPRITE LIBRARY
#  Keys: (stage, path_or_None, mood)
# ─────────────────────────────────────────────

SPRITES: dict[tuple, str] = {

    # ── EGG ──────────────────────────────────
    (PetStage.EGG, None, "normal"): """
     ╭───────╮
     │  ( )  │
     │ (   ) │
     │  ╰─╯  │
     ╰───────╯
""",

    # ── BABY ─────────────────────────────────
    (PetStage.BABY, None, "normal"): """
      /\\_/\\
     ( o.o )
      > ^ <
     /|   |\\
    (_|   |_)
""",
    (PetStage.BABY, None, "happy"): """
      /\\_/\\
     ( ^.^ )
      > ^ <
     /|   |\\
    (_|   |_)
     (✓   ✓)
""",
    (PetStage.BABY, None, "hurt"): """
      /\\_/\\
     ( x.x )
      > < <
     /| - |\\
    (_| - |_)
     (✗   ✗)
""",
    (PetStage.BABY, None, "battle"): """
      /\\_/\\
     ( >.< )
      > ⚔ <
     /|   |\\
    (_|   |_)
""",

    # ── TEEN – GUARDIAN ──────────────────────
    (PetStage.TEEN, EvolutionPath.GUARDIAN, "normal"): """
       /\\_/\\
      ( ◎.◎ )
       > + <
      /|███|\\
     (_|███|_)
    ✨Shiny Shell✨
""",
    (PetStage.TEEN, EvolutionPath.GUARDIAN, "battle"): """
       /\\_/\\
      ( ◎⚔◎ )
       > + <
      /|███|\\
     (_|███|_)
    ✨GUARDIAN✨
""",

    # ── TEEN – WARRIOR ───────────────────────
    (PetStage.TEEN, EvolutionPath.WARRIOR, "normal"): """
       /\\_/\\
      ( ●.● )
       > < <
      /|████|\\
     (_|████|_)
    ⚫ Dark Shell ⚫
""",
    (PetStage.TEEN, EvolutionPath.WARRIOR, "battle"): """
       /\\_/\\
      ( ●⚔● )
       >\\W/<
      /|████|\\
     (_|████|_)
    ⚔️  WARRIOR ⚔️
""",

    # ── TEEN – BALANCED ──────────────────────
    (PetStage.TEEN, EvolutionPath.BALANCED, "normal"): """
       /\\_/\\
      ( o.o )
       > ^ <
      /|███|\\
     (_|███|_)
    🌙 Balanced 🌙
""",
    (PetStage.TEEN, EvolutionPath.BALANCED, "battle"): """
       /\\_/\\
      ( o⚔o )
       > ^ <
      /|███|\\
     (_|███|_)
    🌙 BALANCED 🌙
""",

    # ── ADULT – GUARDIAN ─────────────────────
    (PetStage.ADULT, EvolutionPath.GUARDIAN, "normal"): """
       /\\_/\\
      ( ◎.◎ )
       > + <
      /|███████|\\
     (_|███████|_)
    ⭐ RADIANT FORM ⭐
""",
    (PetStage.ADULT, EvolutionPath.GUARDIAN, "battle"): """
       /\\_/\\
      ( ◎⚔◎ )
       > + <
      /|███████|\\
     (_|███████|_)
    ⭐ ETERNAL GUARDIAN ⭐
""",

    # ── ADULT – WARRIOR ──────────────────────
    (PetStage.ADULT, EvolutionPath.WARRIOR, "normal"): """
       /\\_/\\
      ( ●.● )
       > W <
      /|███████|\\
     (_|███████|_)
    ⚔️  SAVAGE FORM ⚔️
""",
    (PetStage.ADULT, EvolutionPath.WARRIOR, "battle"): """
       /\\_/\\
      ( ●⚔● )
       >\\W/<
      /|███████|\\
     (_|███████|_)
    ◆ UNCHAINED WARRIOR ◆
""",

    # ── ADULT – BALANCED ─────────────────────
    (PetStage.ADULT, EvolutionPath.BALANCED, "normal"): """
       /\\_/\\
      ( o.o )
       > ^ <
      /|██████|\\
     (_|██████|_)
    🌙 INFINITE BALANCED 🌙
""",

    # ── LEGENDARY ────────────────────────────
    (PetStage.LEGENDARY, EvolutionPath.GUARDIAN, "normal"): """
  🟡  /\\_/\\  🟡
  🟡 ( ◎.◎ ) 🟡
  🟡  > + <  🟡
  🟡 /|████|\\ 🟡
  🟡(_|████|_)🟡
  🌟 ETERNAL GUARDIAN 🌟
""",
    (PetStage.LEGENDARY, EvolutionPath.WARRIOR, "normal"): """
  ⚔️  /\\_/\\  ⚔️
  ◆  ( ●.● )  ◆
  ◆   > W <   ◆
  ◆  /|████|\\ ◆
  ◆ (_|████|_)◆
  ◆ UNCHAINED WARRIOR ◆
""",
    (PetStage.LEGENDARY, EvolutionPath.BALANCED, "normal"): """
  🌟  /\\_/\\  🌟
  ⭐ ( o.o ) ⭐
  ⭐  > ^ <  ⭐
  ⭐ /|████|\\ ⭐
  ⭐(_|████|_)⭐
  🌙 TRANSCENDENT 🌙
""",
}


def _get_sprite(pet: MoltPet, mood: str = "normal") -> str:
    """Look up sprite, falling back gracefully."""
    path = pet.evolution_path

    # Try exact match
    key = (pet.evolution_stage, path, mood)
    if key in SPRITES:
        return SPRITES[key]

    # Fall back to "normal" mood
    key_normal = (pet.evolution_stage, path, "normal")
    if key_normal in SPRITES:
        return SPRITES[key_normal]

    # Fall back to path=None (BABY/EGG)
    key_nopath = (pet.evolution_stage, None, "normal")
    if key_nopath in SPRITES:
        return SPRITES[key_nopath]

    return "\n  [???]\n"


def _bar(value: float, max_value: float, width: int = 10) -> str:
    filled = int(round(value / max_value * width)) if max_value else 0
    filled = max(0, min(width, filled))
    return "█" * filled + "░" * (width - filled)


def _mood_from_pet(pet: MoltPet) -> str:
    m = pet.get_mood()
    return m.value if hasattr(m, "value") else str(m).lower()


# ─────────────────────────────────────────────
#  PUBLIC RENDERERS
# ─────────────────────────────────────────────

def render_pet(pet: MoltPet, state: str = "auto") -> str:
    """
    Return the sprite string for a pet.
    state: "auto" | "normal" | "happy" | "hurt" | "battle"
    """
    if state == "auto":
        state = _mood_from_pet(pet)
        if pet.hp <= pet.max_hp * 0.25:
            state = "hurt"
    return _get_sprite(pet, state)


def render_status(pet: MoltPet) -> str:
    """Full status panel with ASCII art + stat bars."""
    stage_label = pet.evolution_stage.value
    path_label  = f" · {pet.evolution_path.value}" if pet.evolution_path else ""
    mood        = _mood_from_pet(pet)

    hp_bar      = _bar(pet.hp,        pet.max_hp)
    hunger_bar  = _bar(pet.hunger,    100)
    happy_bar   = _bar(pet.happiness, 100)
    xp_bar      = _bar(pet.xp,        pet.xp_to_level)

    sprite = _get_sprite(pet, mood)

    winrate = f"{pet.get_winrate():.1f}%" if pet.battles_total else "—"

    return (
        f"🦀 {pet.name}  ·  Level {pet.level}  ·  {stage_label}{path_label}\n"
        f"{'═' * 46}\n"
        f"{sprite}\n"
        f"❤️  HP      {hp_bar} {pet.hp}/{pet.max_hp}\n"
        f"🍖  Hunger  {hunger_bar} {int(pet.hunger)}%\n"
        f"😊  Happy   {happy_bar} {int(pet.happiness)}%\n"
        f"✨  XP      {xp_bar} {pet.xp}/{pet.xp_to_level}\n"
        f"\n"
        f"STR {pet.strength:3d}  ·  SPD {pet.speed:3d}  ·  INT {pet.intelligence:3d}%\n"
        f"Care score: {pet.care_score:.0f}%  ·  Mood: {mood.upper()}\n"
        f"\n"
        f"Battles: {pet.battles_won}W / {pet.battles_lost}L  ·  "
        f"Winrate: {winrate}  ·  Streak: {pet.current_streak}\n"
        f"{'═' * 46}"
    )


def render_battle_intro(attacker: MoltPet, defender: MoltPet, wager: float = 0.0) -> str:
    """Pre-battle matchup card."""
    att_hp = _bar(attacker.hp, attacker.max_hp)
    def_hp = _bar(defender.hp, defender.max_hp)

    wager_line = f"\n💰  WAGER: ${wager:.2f} USDC" if wager > 0 else ""

    return (
        f"⚔️   BATTLE CHALLENGE  ⚔️\n"
        f"{'═' * 52}\n"
        f"  {attacker.name:<20}  vs  {defender.name}\n"
        f"  @{attacker.owner_id:<19}       @{defender.owner_id}\n"
        f"  Lv {attacker.level:<18}       Lv {defender.level}\n"
        f"\n"
        f"  HP  {att_hp} {attacker.hp:3d}/{attacker.max_hp:<4d}"
        f"    HP  {def_hp} {defender.hp:3d}/{defender.max_hp}\n"
        f"  STR {attacker.strength:<3d}  SPD {attacker.speed:<3d}  INT {attacker.intelligence}%"
        f"   STR {defender.strength:<3d}  SPD {defender.speed:<3d}  INT {defender.intelligence}%\n"
        f"{'═' * 52}"
        f"{wager_line}"
    )


def render_battle_turn(
    turn_num: int,
    actor_name: str,
    target_name: str,
    damage: int,
    is_crit: bool,
    target_hp: int,
    target_max_hp: int,
) -> str:
    """One turn of battle output."""
    crit_tag = "  💥 CRITICAL!" if is_crit else ""
    hp_bar   = _bar(target_hp, target_max_hp, 8)
    return (
        f"  Turn {turn_num:2d}: {actor_name} ⚔️  {target_name}"
        f"  -{damage} dmg{crit_tag}\n"
        f"           {target_name} HP: {hp_bar} {target_hp}/{target_max_hp}"
    )


def render_battle_result(result: dict) -> str:
    """Full battle result card."""
    winner = result["winner"]
    loser  = result["loser"]

    # Turn log
    log_lines = []
    for t in result.get("log", []):
        is_crit = t.is_crit if hasattr(t, "is_crit") else t.get("is_crit", False)
        damage  = t.damage  if hasattr(t, "damage")  else t.get("damage", 0)
        actor   = t.actor_name if hasattr(t, "actor_name") else t.get("actor", "?")
        hp_a    = t.target_hp_after if hasattr(t, "target_hp_after") else t.get("target_hp_after", 0)
        hp_b    = t.target_hp_before if hasattr(t, "target_hp_before") else t.get("target_hp_before", 0)
        turn_n  = t.turn_number if hasattr(t, "turn_number") else t.get("turn", 0)
        crit_tag = " 💥 CRIT!" if is_crit else ""
        log_lines.append(f"  T{turn_n:02d}  {actor:>14}  -{damage:3d}{crit_tag}  HP: {hp_a}")

    log_block = "\n".join(log_lines) if log_lines else "  (no turns logged)"

    return (
        f"⚔️   BATTLE RESULT  ⚔️\n"
        f"{'═' * 48}\n"
        f"\n"
        f"{log_block}\n"
        f"\n"
        f"{'─' * 48}\n"
        f"🏆  {winner.name} WINS  "
        f"(HP {winner.hp}/{winner.max_hp} remaining)\n"
        f"💔  {loser.name} fainted\n"
        f"\n"
        f"💫  REWARDS\n"
        f"    {winner.name}: +{result['xp_reward']} XP  ·  +${result['usdc_reward']:.2f} USDC\n"
        f"    {loser.name}: +10 XP  (participation)\n"
        f"{'═' * 48}"
    )


def render_evolution_ceremony(
    pet: MoltPet,
    old_stage: PetStage,
    new_stage: PetStage,
    path: EvolutionPath | None = None,
) -> str:
    """Flashy evolution screen."""
    path_label = f" ({path.value})" if path else ""
    new_sprite = _get_sprite(pet, "normal")

    return (
        f"{'✨' * 23}\n"
        f"\n"
        f"  {pet.name} is evolving!\n"
        f"  {old_stage.value}  →  {new_stage.value}{path_label}\n"
        f"\n"
        f"{'✨' * 23}\n"
        f"\n"
        f"{new_sprite}\n"
        f"{'─' * 46}\n"
        f"🎉  {pet.name} became a {new_stage.value}{path_label}!\n"
        + (f"🔓  New abilities: {', '.join(pet.abilities[-2:])}\n" if len(pet.abilities) >= 2 else "")
        + f"📈  Max HP: {pet.max_hp}  ·  STR: {pet.strength}"
        f"  ·  SPD: {pet.speed}  ·  INT: {pet.intelligence}%\n"
        f"{'✨' * 23}"
    )


def render_leaderboard(pets: list[MoltPet], title: str = "🏆 WEEKLY LEADERBOARD 🏆") -> str:
    """Tabular leaderboard."""
    header = (
        f"\n{title}\n"
        f"{'═' * 62}\n"
        f" {'':2}  {'Pet':<14} {'Owner':<16} {'Lv':>4} "
        f"{'W':>5} {'WR%':>6} {'Streak':>7}\n"
        f"{'─' * 62}\n"
    )
    medals = ["🥇", "🥈", "🥉"]
    rows = []
    for i, pet in enumerate(pets, 1):
        medal = medals[i - 1] if i <= 3 else f"{i:2}."
        wr    = f"{pet.get_winrate():.1f}" if pet.battles_total else "—"
        rows.append(
            f" {medal:2}  {pet.name:<14} {pet.owner_id:<16} {pet.level:>4} "
            f"{pet.battles_won:>5} {wr:>6} {pet.current_streak:>7}"
        )
    footer = f"{'═' * 62}\n"
    return header + "\n".join(rows) + "\n" + footer
