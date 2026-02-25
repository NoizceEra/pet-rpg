"""
Molt Sift Flask API Server - Real Integration
Endpoints for bounty posting, claiming, validation, and payment processing.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any

# Import real API clients
from payaclaw_api_real import PayAClawClient
from solana_x402_real import SolanaX402Handler
from sifter import Sifter

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize clients
PAYACLAW_API_KEY = os.getenv("PAYACLAW_API_KEY", "test_key")
PAYACLAW_API_URL = os.getenv("PAYACLAW_API_URL", "https://api.payaclaw.ai/v1")
SOLANA_NETWORK = os.getenv("SOLANA_NETWORK", "devnet")
SOLANA_KEYPAIR_PATH = os.getenv("SOLANA_KEYPAIR_PATH", None)

payaclaw_client = PayAClawClient(api_key=PAYACLAW_API_KEY, api_url=PAYACLAW_API_URL)
solana_handler = SolanaX402Handler(network=SOLANA_NETWORK, keypair_path=SOLANA_KEYPAIR_PATH)
sifter = Sifter()

# In-memory job tracking (would use database in production)
job_cache = {}
job_results = {}


@app.before_request
def before_request():
    """Validate API key if provided."""
    api_key = request.headers.get("X-API-Key")
    if api_key and api_key != PAYACLAW_API_KEY:
        return {"status": "error", "message": "Invalid API key"}, 401


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    try:
        payaclaw_healthy = payaclaw_client.is_healthy()
        solana_healthy = solana_handler.is_healthy()
        
        return jsonify({
            "status": "ok" if (payaclaw_healthy and solana_healthy) else "degraded",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "services": {
                "payaclaw": "ok" if payaclaw_healthy else "error",
                "solana": "ok" if solana_healthy else "error"
            }
        })
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }), 500


@app.route("/api/bounties", methods=["GET"])
def get_bounties():
    """Fetch available bounties from PayAClaw."""
    try:
        limit = request.args.get("limit", 50, type=int)
        offset = request.args.get("offset", 0, type=int)
        
        # Fetch from PayAClaw
        bounties = payaclaw_client.list_bounties(limit=limit, offset=offset)
        
        return jsonify({
            "status": "success",
            "bounties": bounties,
            "count": len(bounties),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
    
    except Exception as e:
        logger.error(f"Get bounties error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "bounties": []
        }), 500


@app.route("/api/bounties/<job_id>", methods=["GET"])
def get_bounty(job_id):
    """Get a specific bounty."""
    try:
        bounty = payaclaw_client.get_job(job_id)
        
        if not bounty:
            return jsonify({
                "status": "error",
                "message": f"Bounty {job_id} not found"
            }), 404
        
        return jsonify({
            "status": "success",
            "bounty": bounty,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
    
    except Exception as e:
        logger.error(f"Get bounty error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/api/bounties", methods=["POST"])
def post_bounty():
    """Post a new bounty."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["title", "raw_data", "rules", "amount"]
        if not all(field in data for field in required_fields):
            return jsonify({
                "status": "error",
                "message": "Missing required fields: title, raw_data, rules, amount"
            }), 400
        
        # Validate JSON raw data
        if isinstance(data["raw_data"], str):
            try:
                json.loads(data["raw_data"])
            except:
                return jsonify({
                    "status": "error",
                    "message": "Invalid JSON in raw_data"
                }), 400
        
        # Create bounty via PayAClaw API
        # (In real implementation, this would POST to /bounties endpoint)
        bounty_id = f"job_{datetime.utcnow().timestamp()}"
        
        bounty = {
            "job_id": bounty_id,
            "id": bounty_id,
            "title": data.get("title"),
            "description": data.get("description", ""),
            "rules": data.get("rules"),
            "validation_rules": data.get("rules"),
            "amount_usdc": data.get("amount"),
            "amount": data.get("amount"),
            "raw_data": data.get("raw_data"),
            "data": data.get("raw_data"),
            "payout_address": data.get("payout_address"),
            "status": "open",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "created_by": data.get("payout_address")
        }
        
        job_cache[bounty_id] = bounty
        
        logger.info(f"New bounty posted: {bounty_id}")
        
        return jsonify({
            "status": "success",
            "job_id": bounty_id,
            "bounty": bounty,
            "message": f"Bounty posted successfully. Reward: ${data.get('amount')} USDC"
        }), 201
    
    except Exception as e:
        logger.error(f"Post bounty error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/api/bounties/<job_id>/claim", methods=["POST"])
def claim_bounty(job_id):
    """Claim a bounty job."""
    try:
        data = request.get_json() or {}
        agent_id = data.get("agent_id")
        
        if not agent_id:
            return jsonify({
                "status": "error",
                "message": "agent_id required"
            }), 400
        
        # Try to get from cache first, then from PayAClaw
        bounty = job_cache.get(job_id)
        if not bounty:
            bounty = payaclaw_client.get_job(job_id)
        
        if not bounty:
            return jsonify({
                "status": "error",
                "message": f"Bounty {job_id} not found"
            }), 404
        
        if bounty.get("status") != "open":
            return jsonify({
                "status": "error",
                "message": f"Bounty {job_id} is not available"
            }), 400
        
        # Claim via PayAClaw
        claim_result = payaclaw_client.claim_job(job_id, agent_id)
        
        if claim_result.get("status") == "claimed":
            # Update cache
            if job_id in job_cache:
                job_cache[job_id]["status"] = "claimed"
                job_cache[job_id]["claimed_by"] = agent_id
            
            logger.info(f"Bounty claimed: {job_id} by {agent_id}")
            
            return jsonify({
                "status": "success",
                "job_id": job_id,
                "message": "Bounty claimed successfully",
                "claim": claim_result
            }), 200
        else:
            return jsonify(claim_result), 400
    
    except Exception as e:
        logger.error(f"Claim bounty error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/api/bounties/<job_id>/process", methods=["POST"])
def process_bounty(job_id):
    """
    Process bounty: claim, validate with Molt Sift, submit result, and initiate payment.
    """
    try:
        data = request.get_json() or {}
        agent_id = data.get("agent_id")
        
        if not agent_id:
            return jsonify({
                "status": "error",
                "message": "agent_id required"
            }), 400
        
        # Get bounty
        bounty = job_cache.get(job_id)
        if not bounty:
            bounty = payaclaw_client.get_job(job_id)
        
        if not bounty:
            return jsonify({
                "status": "error",
                "message": f"Bounty {job_id} not found"
            }), 404
        
        # Step 1: Validate with Molt Sift
        raw_data = bounty.get("raw_data") or bounty.get("data")
        rules = bounty.get("rules") or bounty.get("validation_rules")
        
        try:
            if isinstance(raw_data, str):
                raw_data = json.loads(raw_data)
        except:
            raw_data = {"raw": raw_data}
        
        validation_result = sifter.validate(raw_data, rules)
        logger.info(f"Validation complete: {job_id} - Score: {validation_result.get('score')}")
        
        # Step 2: Submit result to PayAClaw
        submit_result = payaclaw_client.submit_result(job_id, validation_result, agent_id)
        
        if submit_result.get("status") == "error":
            return jsonify(submit_result), 400
        
        result_id = submit_result.get("result_id", f"{job_id}_result")
        
        # Step 3: Trigger payment
        amount_usdc = bounty.get("amount_usdc") or bounty.get("amount", 5.0)
        payout_address = bounty.get("payout_address")
        
        payment_result = None
        if payout_address:
            # Trigger Solana payment
            payment_result = solana_handler.send_payment(
                amount_usdc=amount_usdc,
                recipient_address=payout_address,
                job_id=job_id
            )
            
            if payment_result.get("status") == "error":
                logger.warning(f"Payment initiation failed: {payment_result.get('message')}")
            else:
                logger.info(f"Payment initiated: {job_id} - {amount_usdc} USDC")
                
                # Confirm payment
                confirm_result = solana_handler.confirm_payment(
                    payment_result.get("txn_signature"),
                    max_wait_seconds=30
                )
                payment_result.update(confirm_result)
        
        # Update cache
        if job_id in job_cache:
            job_cache[job_id]["status"] = "completed"
        
        job_results[job_id] = {
            "validation": validation_result,
            "submission": submit_result,
            "payment": payment_result
        }
        
        return jsonify({
            "status": "success",
            "job_id": job_id,
            "agent_id": agent_id,
            "amount_usdc": amount_usdc,
            "validation_score": validation_result.get("score"),
            "result_id": result_id,
            "payment_id": payment_result.get("txn_signature") if payment_result else None,
            "payment_status": payment_result.get("status") if payment_result else "pending",
            "message": "Bounty processed successfully"
        }), 200
    
    except Exception as e:
        logger.error(f"Process bounty error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/api/bounties/<job_id>/submit", methods=["POST"])
def submit_bounty(job_id):
    """Submit validation result for a bounty."""
    try:
        data = request.get_json() or {}
        agent_id = data.get("agent_id")
        
        if not agent_id:
            return jsonify({
                "status": "error",
                "message": "agent_id required"
            }), 400
        
        # Get bounty
        bounty = job_cache.get(job_id)
        if not bounty:
            bounty = payaclaw_client.get_job(job_id)
        
        if not bounty:
            return jsonify({
                "status": "error",
                "message": f"Bounty {job_id} not found"
            }), 404
        
        # Validate data
        raw_data = bounty.get("raw_data") or bounty.get("data")
        rules = bounty.get("rules") or bounty.get("validation_rules")
        
        try:
            if isinstance(raw_data, str):
                raw_data = json.loads(raw_data)
        except:
            raw_data = {"raw": raw_data}
        
        # Validate with Molt Sift
        validation_result = sifter.validate(raw_data, rules)
        
        # Submit to PayAClaw
        result = payaclaw_client.submit_result(job_id, validation_result, agent_id)
        
        logger.info(f"Result submitted: {job_id}")
        
        return jsonify({
            "status": "success",
            "job_id": job_id,
            "result_id": result.get("result_id"),
            "validation_score": validation_result.get("score"),
            "message": "Result submitted successfully"
        }), 200
    
    except Exception as e:
        logger.error(f"Submit bounty error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/api/payments/<payment_id>", methods=["GET"])
def get_payment_status(payment_id):
    """Get payment status."""
    try:
        payment_status = solana_handler.get_payment_status(payment_id)
        
        return jsonify({
            "status": "success",
            "payment_status": payment_status,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
    
    except Exception as e:
        logger.error(f"Get payment status error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/api/agents/<agent_id>/stats", methods=["GET"])
def get_agent_stats(agent_id):
    """Get agent statistics."""
    try:
        stats = payaclaw_client.get_agent_stats(agent_id)
        
        return jsonify({
            "status": "success",
            "stats": stats,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
    
    except Exception as e:
        logger.error(f"Get agent stats error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/api/jobs", methods=["GET"])
def list_jobs():
    """List all jobs (cached and from PayAClaw)."""
    try:
        # Get from PayAClaw
        payaclaw_jobs = payaclaw_client.list_bounties(limit=100)
        
        # Combine with cache
        all_jobs = list(job_cache.values()) + payaclaw_jobs
        
        # Remove duplicates
        seen = set()
        unique_jobs = []
        for job in all_jobs:
            job_id = job.get("job_id") or job.get("id")
            if job_id not in seen:
                seen.add(job_id)
                unique_jobs.append(job)
        
        return jsonify({
            "status": "success",
            "jobs": unique_jobs,
            "count": len(unique_jobs),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
    
    except Exception as e:
        logger.error(f"List jobs error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "jobs": list(job_cache.values())
        }), 500


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({
        "status": "error",
        "message": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({
        "status": "error",
        "message": "Internal server error"
    }), 500


def start_api_server(host: str = "0.0.0.0", port: int = 8000, debug: bool = False):
    """Start the Flask API server."""
    logger.info(f"Starting Molt Sift API Server on {host}:{port}")
    logger.info(f"PayAClaw API: {PAYACLAW_API_URL}")
    logger.info(f"Solana Network: {SOLANA_NETWORK}")
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    import sys
    
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    debug = "--debug" in sys.argv
    
    start_api_server(port=port, debug=debug)
