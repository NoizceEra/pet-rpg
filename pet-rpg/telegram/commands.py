"""
Telegram Commands for MoltGotchi
================================
Full command handler for the Telegram bot interface.

Usage (from bot webhook):
    result = handle_command("/pet create Snappy", "telegram_user_123")

Supported commands:
    /pet create [name] [species]   - Hatch a new pet
    /pet status                    - Full status panel
    /pet evolve                    - Trigger evolution (if ready)
    /pet feed                      - +25 hunger
    /pet play                      - +20 happiness
    /pet train [str|spd|int]       - Train a stat
    /pet rest                      - Recover HP
    /pet battle <opponent> [wager] - Fight another player
    /pet battles [n]               - View recent battles
    /pet h2h <opponent_id>         - Head-to-head record
    /pet leaderboard [n]           - Top N pets
    /pet species                   - List available species
    /pet help                      - Show help
"""

import sys
import uuid
from pathlib import Path
from typing import Optional, List

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.pet import MoltPet, PetStage
from core.battle import BattleEngine
from core.evolution import EvolutionSystem
from core.species import SPECIES_DATA

from storage.pet_storage import (
    save_pet, load_pet, pet_exists,
    get_pets_by_owner, get_all_pets,
)
from storage.battle_storage import (
    save_battle, load_battle,
    get_battles_by_owner,
    get_head_to_head,
)

from ascii.art import (
    render_pet,
    render_status,
    render_battle_intro,
    render_battle_result,
    render_evolution_ceremony,
    render_leaderboard,
)


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _load_owner_pet(owner_id: str) -> Optional[MoltPet]:
    """Return the first pet owned by owner_id, or None."""
    pets = get_pets_by_owner(owner_id)
    return pets[0] if pets else None


def _has_pet(owner_id: str) -> bool:
    """Check if owner has any pets."""
    return bool(get_pets_by_owner(owner_id))


def _leaderboard_pets(limit: int = 10) -> List[MoltPet]:
    """Return top pets sorted by wins then level."""
    all_pets = get_all_pets()
    return sorted(all_pets, key=lambda p: (p.battles_won, p.level), reverse=True)[:limit]


def _check_evolution(pet: MoltPet) -> Optional[str]:
    """
    Check if pet should evolve after a care action.
    Evolves and returns a ceremony string if triggered, else None.
    """
    if not EvolutionSystem.should_evolve(pet):
        return None
    event = EvolutionSystem.evolve_pet(pet)
    if not event:
        return None
    ceremony = render_evolution_ceremony(
        pet, event.old_stage, event.new_stage, event.path
    )
    save_pet(pet)
    new_abilities = getattr(event, "new_abilities", []) or []
    ability_lines = "\n".join(f"  ✦ {a}" for a in new_abilities)
    return (
        f"\n```\n{ceremony}\n```\n"
        f"✨ {event.message}"
        + (f"\n\n**New abilities:**\n{ability_lines}" if ability_lines else "")
    )


# ─────────────────────────────────────────────────────────────────────────────
# Command: /pet create [name] [species]
# ─────────────────────────────────────────────────────────────────────────────

def cmd_pet_create(owner_id: str, name: str = None, species: str = "MoltCrab") -> str:
    """Hatch a new pet for the owner."""
    if _has_pet(owner_id):
        pet = _load_owner_pet(owner_id)
        pname = pet.name if pet else "your pet"
        return (
            f"❌ You already have **{pname}**!\n"
            "Use `/pet status` to check on them.\n"
            "_(Only one pet per owner — for now)_"
        )

    name = (name or "MoltPet").strip()[:24]

    # Normalise species name
    matched = next(
        (k for k in SPECIES_DATA if k.lower() == species.strip().lower()),
        "MoltCrab",
    )

    pet = MoltPet(
        pet_id=str(uuid.uuid4()),
        owner_id=owner_id,
        name=name,
        species=matched,
    )

    if save_pet(pet):
        sprite = render_pet(pet)
        return (
            f"🥚 **{name}** has hatched!\n"
            f"```\n{sprite}\n```\n"
            f"Species: **{matched}**\n"
            "Your adventure begins! 🌟\n\n"
            "• `/pet status`            — Full status\n"
            "• `/pet feed`              — Restore hunger\n"
            "• `/pet play`              — Boost happiness\n"
            "• `/pet train str`         — Train strength\n"
            "• `/pet battle <id>`       — Pick a fight!\n"
        )
    return "❌ Error creating pet. Please try again."


# ─────────────────────────────────────────────────────────────────────────────
# Command: /pet status
# ─────────────────────────────────────────────────────────────────────────────

def cmd_pet_status(owner_id: str) -> str:
    """Show full status panel."""
    pet = _load_owner_pet(owner_id)
    if not pet:
        return "❌ You don't have a pet! Use `/pet create` to get started."
    return f"```\n{render_status(pet)}\n```"


# ─────────────────────────────────────────────────────────────────────────────
# Commands: /pet feed  /pet play  /pet train  /pet rest
# ─────────────────────────────────────────────────────────────────────────────

def cmd_pet_feed(owner_id: str) -> str:
    pet = _load_owner_pet(owner_id)
    if not pet:
        return "❌ You don't have a pet! Use `/pet create` to get started."
    msg = pet.feed()
    save_pet(pet)
    return msg + (_check_evolution(pet) or "")


def cmd_pet_play(owner_id: str) -> str:
    pet = _load_owner_pet(owner_id)
    if not pet:
        return "❌ You don't have a pet! Use `/pet create` to get started."
    msg = pet.play()
    save_pet(pet)
    return msg + (_check_evolution(pet) or "")


def cmd_pet_train(owner_id: str, stat: str = "str") -> str:
    pet = _load_owner_pet(owner_id)
    if not pet:
        return "❌ You don't have a pet! Use `/pet create` to get started."
    stat = stat.lower()
    valid = {"str", "strength", "spd", "speed", "int", "intelligence"}
    if stat not in valid:
        return f"❌ Unknown stat: `{stat}`\nChoose one of: `str` · `spd` · `int`"
    msg = pet.train(stat)
    save_pet(pet)
    return msg + (_check_evolution(pet) or "")


def cmd_pet_rest(owner_id: str) -> str:
    pet = _load_owner_pet(owner_id)
    if not pet:
        return "❌ You don't have a pet! Use `/pet create` to get started."
    msg = pet.rest()
    save_pet(pet)
    return msg


# ─────────────────────────────────────────────────────────────────────────────
# Command: /pet evolve
# ─────────────────────────────────────────────────────────────────────────────

def cmd_pet_evolve(owner_id: str) -> str:
    """Manually trigger evolution check."""
    pet = _load_owner_pet(owner_id)
    if not pet:
        return "❌ You don't have a pet! Use `/pet create` to get started."

    if not EvolutionSystem.should_evolve(pet):
        progress = EvolutionSystem.get_evolution_progress(pet)
        return f"🔮 **{pet.name}** is not ready to evolve yet.\n\n{progress}"

    event = EvolutionSystem.evolve_pet(pet)
    if not event:
        return "⚠️ Evolution check failed. Try again after levelling up."

    ceremony = render_evolution_ceremony(
        pet, event.old_stage, event.new_stage, event.path
    )
    save_pet(pet)

    new_abilities = getattr(event, "new_abilities", []) or []
    ability_block = (
        "\n**New abilities unlocked:**\n"
        + "\n".join(f"  ✦ {a}" for a in new_abilities)
        if new_abilities else ""
    )
    return (
        f"```\n{ceremony}\n```\n"
        f"✨ {event.message}"
        + ability_block
    )


# ─────────────────────────────────────────────────────────────────────────────
# Command: /pet battle <opponent_id> [wager]
# ─────────────────────────────────────────────────────────────────────────────

def cmd_pet_battle(
    owner_id: str,
    opponent_id: str = None,
    wager: float = 0.0,
) -> str:
    """Initiate a battle between two players' pets."""
    if not opponent_id:
        return "❌ Usage: `/pet battle <opponent_id> [wager_usdc]`"

    if owner_id == opponent_id:
        return "❌ You can't battle yourself!"

    pet = _load_owner_pet(owner_id)
    if not pet:
        return "❌ You don't have a pet! Use `/pet create` to get started."

    opp = _load_owner_pet(opponent_id)
    if not opp:
        return f"❌ **{opponent_id}** doesn't have a pet yet!"

    if wager < 0:
        return "❌ Wager must be a positive value."
    if wager > 100:
        return "❌ Maximum wager is 100 USDC per battle."

    # Temporarily restore full HP so battle is fair
    saved_hp_atk = pet.hp
    saved_hp_def = opp.hp
    pet.hp = pet.max_hp
    opp.hp = opp.max_hp

    engine = BattleEngine(pet, opp, wager)
    result = engine.simulate()

    # Restore pre-battle HP
    pet.hp = max(1, saved_hp_atk)
    opp.hp = max(1, saved_hp_def)

    save_pet(pet)
    save_pet(opp)
    battle_id = save_battle(result)

    intro   = render_battle_intro(pet, opp, wager)
    outcome = render_battle_result(result)

    winner_name = pet.name if result.get("winner") == "attacker" else opp.name
    xp_gain     = result.get("xp_reward", 50)
    usdc_gain   = result.get("usdc_reward", 0.0)

    summary = f"🏆 **{winner_name}** wins!\n• XP earned: +{xp_gain}\n"
    if usdc_gain > 0:
        summary += f"• USDC reward: +${usdc_gain:.2f}\n"
    summary += f"• Battle ID: `{battle_id}`"

    return f"```\n{intro}\n\n{outcome}\n```\n{summary}"


# ─────────────────────────────────────────────────────────────────────────────
# Command: /pet battles [n]
# ─────────────────────────────────────────────────────────────────────────────

def cmd_pet_battles(owner_id: str, limit: int = 5) -> str:
    """Show recent battle history for an owner."""
    battles = get_battles_by_owner(owner_id)
    battles = battles[:limit] if battles else []

    if not battles:
        return "📜 No battles yet! Challenge someone: `/pet battle <opponent_id>`"

    lines = ["📜 **RECENT BATTLES**", "═" * 40]
    for i, b in enumerate(battles, 1):
        att_name = b.get("attacker_name") or b.get("attacker", {}).get("name", "?")
        def_name = b.get("defender_name") or b.get("defender", {}).get("name", "?")
        att_owner = b.get("attacker_owner") or b.get("attacker", {}).get("owner_id", "")
        winner   = b.get("winner", "?")
        turns    = b.get("turns", "?")
        ts       = str(b.get("timestamp", ""))[:10]

        # Did the calling user win?
        i_won = (winner == "attacker" and att_owner == owner_id) or \
                (winner == "defender" and att_owner != owner_id)
        icon = "🏆" if i_won else "💀"

        lines.append(f"{i}. {icon}  {att_name} vs {def_name}  [{turns} turns · {ts}]")

    lines.append("═" * 40)
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Command: /pet h2h <opponent_id>
# ─────────────────────────────────────────────────────────────────────────────

def cmd_pet_h2h(owner_id: str, opponent_id: str = None) -> str:
    """Head-to-head record between two players."""
    if not opponent_id:
        return "❌ Usage: `/pet h2h <opponent_id>`"

    pet = _load_owner_pet(owner_id)
    opp = _load_owner_pet(opponent_id)

    if not pet:
        return "❌ You don't have a pet! Use `/pet create` to get started."
    if not opp:
        return f"❌ **{opponent_id}** doesn't have a pet!"

    records = get_head_to_head(pet.pet_id, opp.pet_id)
    total  = records.get("total", 0)
    wins   = records.get("pet1_wins", 0)
    losses = records.get("pet2_wins", 0)

    if total == 0:
        return (
            f"🥊 No battles yet between **{pet.name}** and **{opp.name}**!\n"
            f"Challenge them: `/pet battle {opponent_id}`"
        )

    bar_len  = 20
    win_fill = round(wins / total * bar_len)
    bar      = "█" * win_fill + "░" * (bar_len - win_fill)
    pct      = wins / total * 100

    return (
        f"🥊 **{pet.name}** vs **{opp.name}**\n"
        f"{'─' * 32}\n"
        f"Total fights : {total}\n"
        f"You won      : {wins}    They won: {losses}\n"
        f"[{bar}]  {pct:.1f}%"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Command: /pet leaderboard [n]
# ─────────────────────────────────────────────────────────────────────────────

def cmd_pet_leaderboard(limit: int = 10) -> str:
    """Show top pets by wins."""
    pets = _leaderboard_pets(limit)
    if not pets:
        return "🏆 No pets on the board yet! Be the first: `/pet create`"
    board = render_leaderboard(pets, title="🏆  MOLTGOTCHI LEADERBOARD  🏆")
    return f"```\n{board}\n```"


# ─────────────────────────────────────────────────────────────────────────────
# Command: /pet species
# ─────────────────────────────────────────────────────────────────────────────

def cmd_pet_species() -> str:
    """List all available species with base stats."""
    lines = ["🐾 **AVAILABLE SPECIES**", "─" * 35]
    for sname, data in SPECIES_DATA.items():
        hp  = data.get("base_hp",  "?")
        st  = data.get("base_str", "?")
        sp  = data.get("base_spd", "?")
        iq  = data.get("base_int", "?")
        desc = data.get("description", "")
        lines.append(
            f"**{sname}**\n"
            f"  HP:{hp}  STR:{st}  SPD:{sp}  INT:{iq}\n"
            f"  _{desc}_\n"
        )
    lines.append("Usage: `/pet create <name> <species>`")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Command: /pet help
# ─────────────────────────────────────────────────────────────────────────────

def cmd_help() -> str:
    """Return the full help text."""
    return (
        "🐾 **MOLTGOTCHI COMMANDS**\n"
        "══════════════════════════════════════\n\n"
        "**🥚 Creation & Status**\n"
        "  `/pet create [name] [species]` — Hatch a pet\n"
        "  `/pet status`                  — Full status panel\n"
        "  `/pet evolve`                  — Evolve (if ready)\n"
        "  `/pet species`                 — List species\n\n"
        "**🍖 Care**\n"
        "  `/pet feed`                    — +25 hunger\n"
        "  `/pet play`                    — +20 happiness\n"
        "  `/pet train [str|spd|int]`     — +1 to a stat\n"
        "  `/pet rest`                    — Recover HP\n\n"
        "**⚔️ Battles**\n"
        "  `/pet battle <id> [wager]`     — Challenge a player\n"
        "  `/pet battles [n]`             — Recent battle log\n"
        "  `/pet h2h <opponent_id>`       — Head-to-head record\n\n"
        "**🏆 Rankings**\n"
        "  `/pet leaderboard [n]`         — Top N pets\n\n"
        "  `/pet help`                    — This message\n"
        "══════════════════════════════════════"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Main dispatcher
# ─────────────────────────────────────────────────────────────────────────────

def handle_command(message_text: str, owner_id: str) -> str:
    """
    Route a raw Telegram message to the correct command handler.

    Args:
        message_text : Full message string, e.g. "/pet battle user42 0.5"
        owner_id     : Telegram user ID (string) of the message sender

    Returns:
        Formatted response string (Markdown V2 compatible).
    """
    parts = message_text.strip().split()

    if not parts:
        return cmd_help()

    # Accept both "/pet ..." and "pet ..."
    cmd_root = parts[0].lstrip("/").lower()
    if cmd_root != "pet":
        return cmd_help()

    subcommand = parts[1].lower() if len(parts) > 1 else "help"
    args = parts[2:] if len(parts) > 2 else []

    # ── create ────────────────────────────────────────
    if subcommand == "create":
        name    = args[0] if args else None
        species = args[1] if len(args) > 1 else "MoltCrab"
        return cmd_pet_create(owner_id, name, species)

    # ── status ────────────────────────────────────────
    elif subcommand in ("status", "stat", "s"):
        return cmd_pet_status(owner_id)

    # ── care actions ─────────────────────────────────
    elif subcommand == "feed":
        return cmd_pet_feed(owner_id)

    elif subcommand == "play":
        return cmd_pet_play(owner_id)

    elif subcommand == "train":
        stat = args[0] if args else "str"
        return cmd_pet_train(owner_id, stat)

    elif subcommand == "rest":
        return cmd_pet_rest(owner_id)

    # ── evolution ─────────────────────────────────────
    elif subcommand == "evolve":
        return cmd_pet_evolve(owner_id)

    # ── battles ───────────────────────────────────────
    elif subcommand in ("battle", "fight", "b"):
        opponent = args[0] if args else None
        try:
            wager = float(args[1]) if len(args) > 1 else 0.0
        except ValueError:
            wager = 0.0
        return cmd_pet_battle(owner_id, opponent, wager)

    elif subcommand in ("battles", "history", "log"):
        try:
            limit = int(args[0]) if args else 5
        except ValueError:
            limit = 5
        return cmd_pet_battles(owner_id, limit)

    elif subcommand in ("h2h", "versus", "vs"):
        opponent = args[0] if args else None
        return cmd_pet_h2h(owner_id, opponent)

    # ── rankings ──────────────────────────────────────
    elif subcommand in ("leaderboard", "lb", "top"):
        try:
            limit = int(args[0]) if args else 10
        except ValueError:
            limit = 10
        return cmd_pet_leaderboard(limit)

    # ── species list ──────────────────────────────────
    elif subcommand == "species":
        return cmd_pet_species()

    # ── help / fallback ───────────────────────────────
    elif subcommand in ("help", "h", "?"):
        return cmd_help()

    else:
        return f"❓ Unknown command: `{subcommand}`\n\n" + cmd_help()
