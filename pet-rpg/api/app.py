"""
Moltgotchi REST API
====================
Flask server exposing all game actions over HTTP.

Base URL: http://localhost:5000

Endpoints:
  GET  /api/health
  GET  /api/pet/<owner_id>
  POST /api/pet/create
  POST /api/pet/<owner_id>/feed
  POST /api/pet/<owner_id>/play
  POST /api/pet/<owner_id>/train
  POST /api/pet/<owner_id>/rest
  GET  /api/pet/<owner_id>/status
  POST /api/battle
  GET  /api/battles/<owner_id>
  GET  /api/battles/<owner_id>/h2h/<opponent_id>
  GET  /api/leaderboard
  GET  /api/species
"""

import sys
import os
import uuid
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(Path(__file__).parent.parent / '.env')

sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, jsonify, request, Response
from flask_cors import CORS

from core.pet import MoltPet, PetStage
from core.battle import BattleEngine, format_battle_ascii
from core.evolution import EvolutionSystem
from core.species import SPECIES_DATA, list_species
from storage.pet_storage import (
    save_pet, load_pet, pet_exists,
    get_pets_by_owner, get_all_pets,
)
from storage.battle_storage import (
    save_battle, load_battle,
    get_battles_by_owner, get_battles_by_pet,
    get_all_battles, get_head_to_head,
)
from ascii.art import render_status, render_battle_result

app = Flask(__name__)

# ─────────────────────────────────────────────
#  CORS Configuration
# ─────────────────────────────────────────────

CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5000').split(',')
CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS if origin.strip()]

print(f"[CORS] Allowed origins: {CORS_ORIGINS}")

CORS(app, resources={
    r"/api/*": {
        "origins": CORS_ORIGINS,
        "methods": ["GET", "POST", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": False,
    }
})


# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────

def _ok(data, status: int = 200):
    return jsonify(data), status


def _err(msg: str, status: int = 400):
    return jsonify({"error": msg}), status


def _require_pet(owner_id: str):
    """Load pet or return 404 response tuple."""
    pets = get_pets_by_owner(owner_id)
    if not pets:
        return None, _err(f"No pet found for owner '{owner_id}'", 404)
    return pets[0], None


def _leaderboard_data(limit: int = 10) -> list[dict]:
    """Sort all pets by wins descending."""
    all_pets = get_all_pets()
    all_pets.sort(key=lambda p: (p.battles_won, p.level), reverse=True)
    return [p.to_dict() for p in all_pets[:limit]]


# ─────────────────────────────────────────────
#  Health
# ─────────────────────────────────────────────

@app.get("/api/health")
def health():
    return _ok({"status": "ok", "game": "Moltgotchi"})


# ─────────────────────────────────────────────
#  Pet CRUD
# ─────────────────────────────────────────────

@app.post("/api/pet/create")
def create_pet():
    """
    Body: { owner_id, name, species? }
    """
    data = request.get_json(silent=True) or {}
    owner_id = data.get("owner_id", "").strip()
    name     = data.get("name", "MoltPet").strip()
    species  = data.get("species", "MoltCrab")

    if not owner_id:
        return _err("owner_id required")

    existing = get_pets_by_owner(owner_id)
    if existing:
        return _err(f"Owner '{owner_id}' already has a pet", 409)

    if species not in SPECIES_DATA:
        return _err(f"Unknown species '{species}'. Choose from: {list(SPECIES_DATA)}")

    pet = MoltPet(
        pet_id=str(uuid.uuid4()),
        owner_id=owner_id,
        name=name,
        species=species,
    )
    save_pet(pet)
    return _ok({"message": f"🎉 {name} created!", "pet": pet.to_dict()}, 201)


@app.get("/api/pet/<owner_id>")
def get_pet(owner_id: str):
    pet, err = _require_pet(owner_id)
    if err:
        return err
    return _ok(pet.to_dict())


@app.get("/api/pet/<owner_id>/status")
def get_pet_status(owner_id: str):
    """Returns pet data + rendered ASCII status panel."""
    pet, err = _require_pet(owner_id)
    if err:
        return err
    return _ok({
        "pet": pet.to_dict(),
        "ascii": render_status(pet),
    })


@app.delete("/api/pet/<owner_id>")
def delete_pet_endpoint(owner_id: str):
    from storage.pet_storage import delete_pet
    pets = get_pets_by_owner(owner_id)
    if not pets:
        return _err("Pet not found", 404)
    delete_pet(pets[0].pet_id)
    return _ok({"message": "Pet deleted"})


# ─────────────────────────────────────────────
#  Care Actions
# ─────────────────────────────────────────────

@app.post("/api/pet/<owner_id>/feed")
def feed_pet(owner_id: str):
    pet, err = _require_pet(owner_id)
    if err:
        return err
    msg = pet.feed()
    save_pet(pet)
    return _ok({"message": msg, "pet": pet.to_dict()})


@app.post("/api/pet/<owner_id>/play")
def play_pet(owner_id: str):
    pet, err = _require_pet(owner_id)
    if err:
        return err
    msg = pet.play()
    save_pet(pet)
    return _ok({"message": msg, "pet": pet.to_dict()})


@app.post("/api/pet/<owner_id>/train")
def train_pet(owner_id: str):
    """
    Body: { stat: "strength" | "speed" | "intelligence" }
    """
    pet, err = _require_pet(owner_id)
    if err:
        return err
    data = request.get_json(silent=True) or {}
    stat = data.get("stat", "strength")
    msg = pet.train(stat)
    save_pet(pet)
    return _ok({"message": msg, "pet": pet.to_dict()})


@app.post("/api/pet/<owner_id>/rest")
def rest_pet(owner_id: str):
    pet, err = _require_pet(owner_id)
    if err:
        return err
    msg = pet.rest()
    save_pet(pet)
    return _ok({"message": msg, "pet": pet.to_dict()})


@app.post("/api/pet/<owner_id>/decay")
def decay_pet(owner_id: str):
    """Manually trigger time-decay (used by cron)."""
    pet, err = _require_pet(owner_id)
    if err:
        return err
    pet.apply_decay()
    save_pet(pet)
    return _ok({"message": "Decay applied", "pet": pet.to_dict()})


# ─────────────────────────────────────────────
#  Evolution
# ─────────────────────────────────────────────

@app.post("/api/pet/<owner_id>/evolve")
def evolve_pet(owner_id: str):
    pet, err = _require_pet(owner_id)
    if err:
        return err
    if not EvolutionSystem.should_evolve(pet):
        progress = EvolutionSystem.get_evolution_progress(pet)
        return _ok({
            "evolved": False,
            "progress": progress,
            "pet": pet.to_dict(),
        })
    event = EvolutionSystem.evolve_pet(pet)
    save_pet(pet)
    return _ok({
        "evolved": True,
        "message": str(event),
        "old_stage": event.old_stage.value,
        "new_stage": event.new_stage.value,
        "path": event.path.value if event.path else None,
        "stat_boosts": event.stat_boosts,
        "pet": pet.to_dict(),
    })


@app.get("/api/pet/<owner_id>/evolution")
def evolution_progress(owner_id: str):
    pet, err = _require_pet(owner_id)
    if err:
        return err
    return _ok(EvolutionSystem.get_evolution_progress(pet))


# ─────────────────────────────────────────────
#  Battles
# ─────────────────────────────────────────────

@app.post("/api/battle")
def battle():
    """
    Body: {
        attacker_owner: str,
        defender_owner: str,
        wager?: float          (default 0)
    }
    """
    data = request.get_json(silent=True) or {}
    att_owner = data.get("attacker_owner", "").strip()
    def_owner = data.get("defender_owner", "").strip()
    wager     = float(data.get("wager", 0.0))

    if not att_owner or not def_owner:
        return _err("attacker_owner and defender_owner required")
    if att_owner == def_owner:
        return _err("Cannot battle yourself")

    att_pets = get_pets_by_owner(att_owner)
    def_pets = get_pets_by_owner(def_owner)

    if not att_pets:
        return _err(f"Attacker '{att_owner}' has no pet", 404)
    if not def_pets:
        return _err(f"Defender '{def_owner}' has no pet", 404)

    attacker = att_pets[0]
    defender = def_pets[0]

    # Snapshot HP before (pets' HP resets after battle)
    att_full_hp = attacker.max_hp
    def_full_hp = defender.max_hp
    attacker.hp = attacker.max_hp
    defender.hp = defender.max_hp

    # Run battle
    engine = BattleEngine(attacker, defender, wager)
    result = engine.simulate()

    # Record results on pets
    won_att = result["winner"].owner_id == att_owner
    attacker.record_battle_result(won=won_att,   xp_gained=result["xp_reward"] if won_att else 10)
    defender.record_battle_result(won=not won_att, xp_gained=result["xp_reward"] if not won_att else 10)

    # Restore HP post-battle
    attacker.hp = att_full_hp
    defender.hp = def_full_hp

    save_pet(attacker)
    save_pet(defender)
    battle_id = save_battle(result)

    return _ok({
        "battle_id": battle_id,
        "winner_owner": result["winner"].owner_id,
        "loser_owner":  result["loser"].owner_id,
        "winner_name":  result["winner_name"],
        "loser_name":   result["loser_name"],
        "turns":        result["turns"],
        "xp_reward":    result["xp_reward"],
        "usdc_reward":  result["usdc_reward"],
        "ascii":        render_battle_result(result),
        "attacker":     attacker.to_dict(),
        "defender":     defender.to_dict(),
    })


@app.get("/api/battles/<owner_id>")
def get_owner_battles(owner_id: str):
    limit = request.args.get("limit", 20, type=int)
    battles = get_battles_by_owner(owner_id, limit)
    return _ok(battles)


@app.get("/api/battles/<owner_id>/h2h/<opponent_id>")
def head_to_head(owner_id: str, opponent_id: str):
    att_pets = get_pets_by_owner(owner_id)
    def_pets = get_pets_by_owner(opponent_id)
    if not att_pets or not def_pets:
        return _err("One or both owners have no pet", 404)
    h2h = get_head_to_head(att_pets[0].name, def_pets[0].name)
    return _ok(h2h)


@app.get("/api/battle/<battle_id>")
def get_battle(battle_id: str):
    battle = load_battle(battle_id)
    if not battle:
        return _err("Battle not found", 404)
    return _ok(battle)


# ─────────────────────────────────────────────
#  Leaderboard
# ─────────────────────────────────────────────

@app.get("/api/leaderboard")
def leaderboard():
    limit = request.args.get("limit", 10, type=int)
    return _ok(_leaderboard_data(limit))


# ─────────────────────────────────────────────
#  Species
# ─────────────────────────────────────────────

@app.get("/api/species")
def species_list():
    return _ok(list_species())


@app.get("/api/species/<name>")
def species_detail(name: str):
    from core.species import get_species
    s = get_species(name)
    if not s:
        return _err(f"Unknown species '{name}'", 404)
    return _ok(s)


# ─────────────────────────────────────────────
#  Error handlers
# ─────────────────────────────────────────────

@app.errorhandler(404)
def not_found(_):
    return _err("Not found", 404)


@app.errorhandler(405)
def method_not_allowed(_):
    return _err("Method not allowed", 405)


@app.errorhandler(500)
def server_error(e):
    return _err(f"Internal server error: {e}", 500)


# ─────────────────────────────────────────────
#  Run
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "1") == "1"
    print(f"🐾 Moltgotchi API starting on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
