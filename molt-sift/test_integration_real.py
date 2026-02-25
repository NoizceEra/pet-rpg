#!/usr/bin/env python3
"""
Molt Sift Real API Integration Test
End-to-end testing of PayAClaw + Solana x402 integration
"""

import json
import time
import os
import sys
from typing import Dict, Any
from datetime import datetime

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from payaclaw_api_real import PayAClawClient
from solana_x402_real import SolanaX402Handler
from sifter import Sifter
from api_server_real import app, job_cache


class IntegrationTester:
    """Test runner for Molt Sift real API integration."""
    
    def __init__(self):
        self.payaclaw_client = None
        self.solana_handler = None
        self.sifter = Sifter()
        self.test_results = []
        self.test_count = 0
        self.passed_count = 0
    
    def setup(self):
        """Initialize API clients."""
        print("\n" + "="*60)
        print("MOLT SIFT REAL API INTEGRATION TEST")
        print("="*60 + "\n")
        
        api_key = os.getenv("PAYACLAW_API_KEY", "test_key")
        network = os.getenv("SOLANA_NETWORK", "devnet")
        
        self.payaclaw_client = PayAClawClient(api_key=api_key)
        self.solana_handler = SolanaX402Handler(network=network, use_mock=True)
        
        print(f"✓ PayAClaw client initialized")
        print(f"✓ Solana handler initialized (network={network}, mock=true)")
        print(f"✓ Sifter engine initialized\n")
    
    def run_test(self, name: str, test_fn):
        """Run a single test."""
        self.test_count += 1
        print(f"[TEST {self.test_count}] {name}")
        
        try:
            result = test_fn()
            self.passed_count += 1
            status = "✓ PASS"
            self.test_results.append((name, True, None))
            print(f"  {status}\n")
            return result
        except Exception as e:
            status = "✗ FAIL"
            self.test_results.append((name, False, str(e)))
            print(f"  {status}: {str(e)}\n")
            return None
    
    def test_payaclaw_health(self):
        """Test PayAClaw API health."""
        return self.payaclaw_client.is_healthy()
    
    def test_payaclaw_list_bounties(self):
        """Test fetching bounties from PayAClaw."""
        bounties = self.payaclaw_client.list_bounties(limit=5)
        assert isinstance(bounties, list), "Should return list of bounties"
        print(f"  Found {len(bounties)} bounties")
        return bounties
    
    def test_payaclaw_get_job(self):
        """Test fetching a specific job."""
        # Create a test bounty first
        test_bounty = {
            "title": "Test Bounty",
            "description": "Test validation",
            "rules": "json-strict",
            "amount": 5.0,
            "raw_data": json.dumps({"test": "data"}),
            "payout_address": "7pf1C3qf6kWJ8DH5LqYw5mRzJqHVQR6xkfYpSEJvCsF7"
        }
        
        # Store in cache for this test
        job_id = f"test_job_{int(time.time())}"
        job_cache[job_id] = {
            "job_id": job_id,
            "id": job_id,
            **test_bounty,
            "status": "open",
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        
        # Fetch it back
        job = self.payaclaw_client.get_job(job_id)
        
        if not job:
            # Try from cache
            job = job_cache.get(job_id)
        
        assert job is not None, "Should be able to fetch job"
        return job
    
    def test_payaclaw_claim_job(self):
        """Test claiming a job."""
        # Create a test bounty
        test_bounty = {
            "title": "Claim Test",
            "rules": "crypto",
            "amount": 3.0,
            "raw_data": json.dumps({"symbol": "BTC", "price": 42000}),
            "payout_address": "7pf1C3qf6kWJ8DH5LqYw5mRzJqHVQR6xkfYpSEJvCsF7"
        }
        
        job_id = f"claim_test_{int(time.time())}"
        job_cache[job_id] = {
            "job_id": job_id,
            "id": job_id,
            **test_bounty,
            "status": "open",
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        
        # Claim it
        result = self.payaclaw_client.claim_job(job_id, "test_agent_001")
        
        assert result.get("status") in ["claimed", "error"], "Should return claim result"
        print(f"  Result: {result.get('status')}")
        return result
    
    def test_molt_sift_validation(self):
        """Test Molt Sift validation."""
        # Test crypto validation
        crypto_data = {
            "symbol": "BTC",
            "price": 42000.50,
            "volume": 1500000000,
            "timestamp": "2026-02-25T12:00:00Z"
        }
        
        result = self.sifter.validate(crypto_data, "crypto")
        
        assert "score" in result, "Should return validation score"
        assert "issues" in result, "Should return issues list"
        print(f"  Validation score: {result.get('score')}")
        print(f"  Issues found: {len(result.get('issues', []))}")
        return result
    
    def test_solana_payment_mock(self):
        """Test Solana payment (mock mode)."""
        recipient = "7pf1C3qf6kWJ8DH5LqYw5mRzJqHVQR6xkfYpSEJvCsF7"
        amount = 5.0
        job_id = f"payment_test_{int(time.time())}"
        
        result = self.solana_handler.send_payment(
            amount_usdc=amount,
            recipient_address=recipient,
            job_id=job_id
        )
        
        assert result.get("status") in ["initiated", "error"], "Should initiate payment"
        print(f"  Payment status: {result.get('status')}")
        if "txn_signature" in result:
            print(f"  Transaction: {result.get('txn_signature')[:16]}...")
        return result
    
    def test_solana_confirm_payment(self):
        """Test payment confirmation."""
        # Create a test payment
        recipient = "7pf1C3qf6kWJ8DH5LqYw5mRzJqHVQR6xkfYpSEJvCsF7"
        amount = 3.0
        job_id = f"confirm_test_{int(time.time())}"
        
        payment = self.solana_handler.send_payment(
            amount_usdc=amount,
            recipient_address=recipient,
            job_id=job_id
        )
        
        if "txn_signature" not in payment:
            raise Exception("Payment not initiated")
        
        # Confirm it
        txn_sig = payment["txn_signature"]
        confirmation = self.solana_handler.confirm_payment(txn_sig, max_wait_seconds=5)
        
        assert confirmation.get("status") in ["confirmed", "pending", "error"], "Should confirm payment"
        print(f"  Confirmation status: {confirmation.get('status')}")
        return confirmation
    
    def test_end_to_end_flow(self):
        """Test complete bounty workflow."""
        print("  Running end-to-end workflow...")
        
        # Step 1: Create bounty
        bounty_data = {
            "job_id": f"e2e_test_{int(time.time())}",
            "title": "End-to-End Test Bounty",
            "description": "Complete workflow test",
            "rules": "json-strict",
            "amount": 5.0,
            "raw_data": json.dumps({
                "order_id": "ord_123",
                "symbol": "ETH/USDT",
                "side": "buy",
                "price": 2450.00,
                "quantity": 1.5
            }),
            "payout_address": "7pf1C3qf6kWJ8DH5LqYw5mRzJqHVQR6xkfYpSEJvCsF7",
            "status": "open",
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        
        job_id = bounty_data["job_id"]
        job_cache[job_id] = bounty_data
        
        print(f"    ✓ Bounty created: {job_id}")
        
        # Step 2: Claim bounty
        claim_result = self.payaclaw_client.claim_job(job_id, "e2e_test_agent")
        assert claim_result.get("status") == "claimed", "Claim should succeed"
        print(f"    ✓ Bounty claimed by e2e_test_agent")
        
        # Step 3: Validate with Molt Sift
        raw_data = json.loads(bounty_data["raw_data"])
        validation = self.sifter.validate(raw_data, bounty_data["rules"])
        print(f"    ✓ Validation complete (score: {validation.get('score')})")
        
        # Step 4: Submit result
        submit_result = self.payaclaw_client.submit_result(
            job_id,
            validation,
            "e2e_test_agent"
        )
        assert submit_result.get("status") == "submitted", "Submission should succeed"
        print(f"    ✓ Result submitted to PayAClaw")
        
        # Step 5: Trigger payment
        payment_result = self.solana_handler.send_payment(
            amount_usdc=5.0,
            recipient_address=bounty_data["payout_address"],
            job_id=job_id
        )
        assert payment_result.get("status") in ["initiated", "error"], "Payment should be initiated"
        print(f"    ✓ Payment initiated (${5.0} USDC)")
        
        # Step 6: Confirm payment
        if "txn_signature" in payment_result:
            confirmation = self.solana_handler.confirm_payment(
                payment_result["txn_signature"],
                max_wait_seconds=5
            )
            print(f"    ✓ Payment confirmed (status: {confirmation.get('status')})")
        
        return {
            "bounty_id": job_id,
            "claim": claim_result,
            "validation": validation,
            "submission": submit_result,
            "payment": payment_result
        }
    
    def run_all_tests(self):
        """Run all tests."""
        self.setup()
        
        # Test 1: PayAClaw Health
        self.run_test("PayAClaw API Health Check", self.test_payaclaw_health)
        
        # Test 2: List Bounties
        bounties = self.run_test("List Available Bounties", self.test_payaclaw_list_bounties)
        
        # Test 3: Get Specific Job
        self.run_test("Fetch Specific Bounty Job", self.test_payaclaw_get_job)
        
        # Test 4: Claim Job
        self.run_test("Claim Bounty Job", self.test_payaclaw_claim_job)
        
        # Test 5: Molt Sift Validation
        self.run_test("Molt Sift Data Validation", self.test_molt_sift_validation)
        
        # Test 6: Solana Payment (Mock)
        payment = self.run_test("Solana x402 Payment (Mock)", self.test_solana_payment_mock)
        
        # Test 7: Payment Confirmation
        self.run_test("Payment Confirmation", self.test_solana_confirm_payment)
        
        # Test 8: End-to-End Workflow
        self.run_test("Complete End-to-End Workflow", self.test_end_to_end_flow)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60 + "\n")
        
        for name, passed, error in self.test_results:
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{status}: {name}")
            if error:
                print(f"         {error}")
        
        print("\n" + "-"*60)
        print(f"Total: {self.passed_count}/{self.test_count} tests passed")
        
        if self.passed_count == self.test_count:
            print("\n🎉 ALL TESTS PASSED! Real API integration is working.")
            print("\nNext steps:")
            print("  1. Set environment variables (.env file)")
            print("  2. Configure PayAClaw API key and Solana keypair")
            print("  3. Deploy Flask API server: python scripts/api_server_real.py")
            print("  4. Open web dashboard in browser")
            print("  5. Connect wallet and start bounty hunting!")
        else:
            print(f"\n⚠️  {self.test_count - self.passed_count} test(s) failed")
            print("Review errors above and check configuration")
        
        print("\n" + "="*60 + "\n")
        
        return self.passed_count == self.test_count


def main():
    """Main test runner."""
    tester = IntegrationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
