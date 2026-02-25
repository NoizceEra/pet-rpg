"""
PayAClaw Real API Client - Production-grade integration
Handles job fetching, claiming, and result submission via real PayAClaw endpoints.
"""

import requests
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PayAClawAPIError(Exception):
    """Custom exception for PayAClaw API errors."""
    pass


class PayAClawClient:
    """Production PayAClaw API client with real endpoints."""
    
    def __init__(self, api_key: str, api_url: str = "https://api.payaclaw.ai/v1"):
        """
        Initialize real PayAClaw API client.
        
        Args:
            api_key: PayAClaw API key (from environment or config)
            api_url: PayAClaw API base URL
        """
        self.api_key = api_key
        self.api_url = api_url
        self.session_id = self._generate_session_id()
        self.timeout = 30  # seconds
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        
        # Setup session with auth
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Molt-Sift/1.0"
        })
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        timestamp = str(time.time())
        return hashlib.md5(timestamp.encode()).hexdigest()[:16]
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None,
                     params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path (without base URL)
            data: Request body data
            params: Query parameters
        
        Returns:
            Response JSON
        
        Raises:
            PayAClawAPIError: On API errors
        """
        url = f"{self.api_url}/{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"[Attempt {attempt + 1}/{self.max_retries}] {method} {endpoint}")
                
                if method == "GET":
                    response = self.session.get(url, params=params, timeout=self.timeout)
                elif method == "POST":
                    response = self.session.post(url, json=data, params=params, timeout=self.timeout)
                elif method == "PUT":
                    response = self.session.put(url, json=data, params=params, timeout=self.timeout)
                elif method == "DELETE":
                    response = self.session.delete(url, params=params, timeout=self.timeout)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                # Check for success
                if response.status_code in [200, 201]:
                    return response.json()
                
                # Handle errors
                if response.status_code == 401:
                    raise PayAClawAPIError("Authentication failed: invalid API key")
                elif response.status_code == 404:
                    raise PayAClawAPIError(f"Not found: {endpoint}")
                elif response.status_code == 429:
                    # Rate limit - wait and retry
                    wait_time = int(response.headers.get("Retry-After", self.retry_delay))
                    logger.warning(f"Rate limited. Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
                elif response.status_code >= 500:
                    # Server error - retry with exponential backoff
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Server error {response.status_code}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    error_msg = response.json().get("message", response.text)
                    raise PayAClawAPIError(f"API error ({response.status_code}): {error_msg}")
                    
            except requests.Timeout:
                logger.warning(f"Request timeout on attempt {attempt + 1}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))
                else:
                    raise PayAClawAPIError(f"Request timeout after {self.max_retries} attempts")
            except requests.RequestException as e:
                logger.error(f"Request error: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))
                else:
                    raise PayAClawAPIError(f"Request failed: {str(e)}")
        
        raise PayAClawAPIError(f"Failed to complete request after {self.max_retries} attempts")
    
    def list_bounties(self, job_type: str = "molt-sift", 
                     filters: Optional[Dict[str, str]] = None,
                     limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List available bounty jobs from PayAClaw.
        
        Args:
            job_type: Job type filter (default: "molt-sift")
            filters: Additional filters
            limit: Maximum number of results
            offset: Pagination offset
        
        Returns:
            List of bounty job objects
        """
        try:
            params = {
                "type": job_type,
                "limit": limit,
                "offset": offset,
                "status": "open"
            }
            
            if filters:
                if "min_amount" in filters:
                    params["min_amount"] = filters["min_amount"]
                if "max_amount" in filters:
                    params["max_amount"] = filters["max_amount"]
            
            response = self._make_request("GET", "jobs", params=params)
            
            # Validate response structure
            if "jobs" not in response:
                logger.warning("Unexpected response format from PayAClaw")
                return []
            
            logger.info(f"Found {len(response['jobs'])} available bounties")
            return response["jobs"]
            
        except PayAClawAPIError as e:
            logger.error(f"Failed to list bounties: {str(e)}")
            return []
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch details for a specific job.
        
        Args:
            job_id: Job ID to fetch
        
        Returns:
            Job details or None if not found
        """
        try:
            response = self._make_request("GET", f"jobs/{job_id}")
            return response.get("job")
        except PayAClawAPIError as e:
            logger.error(f"Failed to fetch job {job_id}: {str(e)}")
            return None
    
    def claim_job(self, job_id: str, agent_id: str) -> Dict[str, Any]:
        """
        Claim a bounty job.
        
        Args:
            job_id: Job ID to claim
            agent_id: Identifier for claiming agent
        
        Returns:
            Claim confirmation with job details
        """
        try:
            data = {
                "agent_id": agent_id,
                "session_id": self.session_id
            }
            
            response = self._make_request("POST", f"jobs/{job_id}/claim", data=data)
            
            logger.info(f"Successfully claimed job {job_id}")
            return response
            
        except PayAClawAPIError as e:
            logger.error(f"Failed to claim job {job_id}: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "job_id": job_id
            }
    
    def submit_result(self, job_id: str, validation_result: Dict[str, Any], 
                     agent_id: str) -> Dict[str, Any]:
        """
        Submit validation result for a claimed job.
        
        Args:
            job_id: Job ID for the result
            validation_result: Result from Molt Sift validation
            agent_id: Identifier for the agent
        
        Returns:
            Submission confirmation with payment details
        """
        try:
            data = {
                "agent_id": agent_id,
                "validation_result": validation_result,
                "session_id": self.session_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
            response = self._make_request("POST", f"jobs/{job_id}/submit", data=data)
            
            logger.info(f"Successfully submitted result for job {job_id}")
            return response
            
        except PayAClawAPIError as e:
            logger.error(f"Failed to submit result for job {job_id}: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "job_id": job_id
            }
    
    def trigger_payment(self, result_id: str, job_id: str, agent_id: str,
                       amount_usdc: float, payout_address: str) -> Dict[str, Any]:
        """
        Trigger payment for a completed job.
        
        Args:
            result_id: ID of submitted result
            job_id: Job ID for payment
            agent_id: Agent to receive payment
            amount_usdc: Amount in USDC
            payout_address: Solana wallet address
        
        Returns:
            Payment confirmation
        """
        try:
            # Validate address
            if not self._is_valid_solana_address(payout_address):
                return {
                    "status": "error",
                    "message": f"Invalid Solana address: {payout_address}"
                }
            
            data = {
                "result_id": result_id,
                "agent_id": agent_id,
                "amount_usdc": amount_usdc,
                "payout_address": payout_address,
                "payment_method": "x402",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
            response = self._make_request("POST", f"jobs/{job_id}/pay", data=data)
            
            logger.info(f"Payment initiated for job {job_id}: ${amount_usdc} -> {payout_address}")
            return response
            
        except PayAClawAPIError as e:
            logger.error(f"Failed to trigger payment for job {job_id}: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "job_id": job_id
            }
    
    def get_agent_stats(self, agent_id: str) -> Dict[str, Any]:
        """
        Get statistics for an agent.
        
        Args:
            agent_id: Agent identifier
        
        Returns:
            Agent statistics including earnings, jobs completed, etc.
        """
        try:
            response = self._make_request("GET", f"agents/{agent_id}/stats")
            return response
        except PayAClawAPIError as e:
            logger.error(f"Failed to fetch agent stats for {agent_id}: {str(e)}")
            return {
                "agent_id": agent_id,
                "error": str(e),
                "jobs_claimed": 0,
                "jobs_completed": 0,
                "total_earned_usdc": 0.0
            }
    
    def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """
        Get status of a payment.
        
        Args:
            payment_id: Payment/transaction ID
        
        Returns:
            Payment status details
        """
        try:
            response = self._make_request("GET", f"payments/{payment_id}")
            return response
        except PayAClawAPIError as e:
            logger.error(f"Failed to fetch payment status {payment_id}: {str(e)}")
            return {
                "id": payment_id,
                "status": "unknown",
                "error": str(e)
            }
    
    @staticmethod
    def _is_valid_solana_address(address: str) -> bool:
        """
        Validate Solana address format.
        
        Args:
            address: Address to validate
        
        Returns:
            True if valid format, False otherwise
        """
        # Solana addresses are base58 encoded, 32-44 chars typically
        if not address or len(address) < 32 or len(address) > 44:
            return False
        
        # Basic base58 character check
        base58_chars = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        return all(c in base58_chars for c in address)
    
    def is_healthy(self) -> bool:
        """Check API health and connectivity."""
        try:
            response = self._make_request("GET", "health")
            return response.get("status") == "ok"
        except PayAClawAPIError:
            return False
    
    def get_session_id(self) -> str:
        """Get current session ID."""
        return self.session_id
    
    def close(self):
        """Close the session."""
        self.session.close()


# Example usage and testing
if __name__ == "__main__":
    import os
    
    # Get API key from environment
    api_key = os.getenv("PAYACLAW_API_KEY", "test_key_default")
    
    # Initialize client
    client = PayAClawClient(api_key=api_key)
    
    try:
        # Test health
        if client.is_healthy():
            print("✓ PayAClaw API is healthy")
        else:
            print("✗ PayAClaw API health check failed")
        
        # Test list bounties
        bounties = client.list_bounties(limit=5)
        if bounties:
            print(f"✓ Found {len(bounties)} bounties")
        else:
            print("✗ No bounties found")
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
    finally:
        client.close()
