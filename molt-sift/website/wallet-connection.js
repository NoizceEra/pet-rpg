/**
 * Solana Wallet Connection Module
 * Handles wallet connection, signing, and transaction confirmation
 */

class WalletManager {
    constructor() {
        this.wallet = null;
        this.connected = false;
        this.publicKey = null;
        this.provider = null;
        this.isPhantom = false;
    }

    /**
     * Initialize wallet connection
     * Supports Phantom and Solflare
     */
    async initialize() {
        try {
            // Check for Phantom wallet
            if (window.solana && window.solana.isPhantom) {
                this.provider = window.solana;
                this.isPhantom = true;
                console.log("✓ Phantom wallet detected");
                return true;
            }

            // Check for Solflare
            if (window.solflare) {
                this.provider = window.solflare;
                console.log("✓ Solflare wallet detected");
                return true;
            }

            console.warn("No Solana wallet detected");
            return false;
        } catch (e) {
            console.error("Wallet initialization error:", e);
            return false;
        }
    }

    /**
     * Connect to wallet
     */
    async connect() {
        if (!this.provider) {
            if (!await this.initialize()) {
                throw new Error("No Solana wallet found. Please install Phantom or Solflare.");
            }
        }

        try {
            const response = await this.provider.connect();
            this.publicKey = response.publicKey.toString();
            this.connected = true;
            console.log("✓ Wallet connected:", this.publicKey);
            return this.publicKey;
        } catch (e) {
            if (e.code === 4001) {
                throw new Error("User rejected wallet connection");
            }
            throw new Error(`Wallet connection failed: ${e.message}`);
        }
    }

    /**
     * Disconnect from wallet
     */
    async disconnect() {
        if (this.provider) {
            try {
                await this.provider.disconnect();
                this.connected = false;
                this.publicKey = null;
                console.log("✓ Wallet disconnected");
            } catch (e) {
                console.error("Disconnect error:", e);
            }
        }
    }

    /**
     * Check if wallet is connected
     */
    isConnected() {
        return this.connected && this.publicKey !== null;
    }

    /**
     * Get connected wallet address
     */
    getAddress() {
        return this.publicKey;
    }

    /**
     * Sign a transaction
     */
    async signTransaction(transaction) {
        if (!this.isConnected()) {
            throw new Error("Wallet not connected");
        }

        try {
            const signedTransaction = await this.provider.signTransaction(transaction);
            return signedTransaction;
        } catch (e) {
            throw new Error(`Transaction signing failed: ${e.message}`);
        }
    }

    /**
     * Sign and send transaction
     */
    async signAndSendTransaction(transaction) {
        if (!this.isConnected()) {
            throw new Error("Wallet not connected");
        }

        try {
            const signature = await this.provider.signAndSendTransaction(transaction);
            console.log("✓ Transaction sent:", signature.signature || signature);
            return signature;
        } catch (e) {
            if (e.code === 4001) {
                throw new Error("User rejected transaction");
            }
            throw new Error(`Send transaction failed: ${e.message}`);
        }
    }
}

/**
 * API Client for communicating with backend
 */
class APIClient {
    constructor(baseUrl = "http://localhost:8000/api") {
        this.baseUrl = baseUrl;
        this.timeout = 30000; // 30 seconds
    }

    /**
     * Make API request with timeout and retry logic
     */
    async request(method, endpoint, data = null) {
        const url = `${this.baseUrl}${endpoint}`;
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        try {
            const options = {
                method,
                headers: {
                    "Content-Type": "application/json"
                },
                signal: controller.signal
            };

            if (data) {
                options.body = JSON.stringify(data);
            }

            const response = await fetch(url, options);

            if (!response.ok) {
                throw new Error(`API Error: ${response.status} ${response.statusText}`);
            }

            return await response.json();
        } catch (e) {
            if (e.name === "AbortError") {
                throw new Error("Request timeout");
            }
            throw e;
        } finally {
            clearTimeout(timeoutId);
        }
    }

    /**
     * Fetch available bounties
     */
    async getBounties(filters = {}) {
        return this.request("GET", "/bounties", null);
    }

    /**
     * Post a new bounty
     */
    async postBounty(data) {
        return this.request("POST", "/bounties", data);
    }

    /**
     * Claim a bounty
     */
    async claimBounty(bountyId, agentId) {
        return this.request("POST", `/bounties/${bountyId}/claim`, { agent_id: agentId });
    }

    /**
     * Submit validation result
     */
    async submitResult(bountyId, result) {
        return this.request("POST", `/bounties/${bountyId}/submit`, result);
    }

    /**
     * Process bounty (validate and get payment info)
     */
    async processBounty(bountyId, agentId) {
        return this.request("POST", `/bounties/${bountyId}/process`, { agent_id: agentId });
    }

    /**
     * Get agent statistics
     */
    async getAgentStats(agentId) {
        return this.request("GET", `/agents/${agentId}/stats`);
    }

    /**
     * Check payment status
     */
    async getPaymentStatus(paymentId) {
        return this.request("GET", `/payments/${paymentId}`);
    }

    /**
     * Health check
     */
    async health() {
        try {
            return await this.request("GET", "/health");
        } catch {
            return { status: "error" };
        }
    }
}

/**
 * Molt Sift Integration Manager
 * Coordinates bounty claiming, validation, and payment
 */
class MoltSiftManager {
    constructor(walletManager, apiClient) {
        this.wallet = walletManager;
        this.api = apiClient;
        this.currentBounty = null;
        this.isProcessing = false;
    }

    /**
     * Claim and process a bounty
     */
    async claimAndProcess(bountyId) {
        if (this.isProcessing) {
            throw new Error("Already processing a bounty");
        }

        if (!this.wallet.isConnected()) {
            throw new Error("Wallet not connected");
        }

        this.isProcessing = true;
        const steps = [];

        try {
            // Step 1: Claim bounty
            steps.push({ name: "Claiming bounty...", status: "pending" });
            const claimResult = await this.api.claimBounty(bountyId, this.wallet.getAddress());
            
            if (claimResult.status === "error") {
                throw new Error(claimResult.message);
            }
            steps[steps.length - 1].status = "complete";

            // Step 2: Process bounty (validate with Molt Sift)
            steps.push({ name: "Running validation...", status: "pending" });
            const processResult = await this.api.processBounty(bountyId, this.wallet.getAddress());
            
            if (processResult.status === "error") {
                throw new Error(processResult.message);
            }
            steps[steps.length - 1].status = "complete";

            // Step 3: Wait for payment
            if (processResult.payment_id) {
                steps.push({ name: "Processing payment...", status: "pending" });
                
                // Poll for payment confirmation
                let paymentConfirmed = false;
                let attempts = 0;
                const maxAttempts = 30; // 30 * 2s = 60s timeout

                while (!paymentConfirmed && attempts < maxAttempts) {
                    const paymentStatus = await this.api.getPaymentStatus(processResult.payment_id);
                    
                    if (paymentStatus.status === "confirmed") {
                        paymentConfirmed = true;
                        steps[steps.length - 1].status = "complete";
                        steps.push({
                            name: "✓ Payment confirmed!",
                            status: "complete",
                            amount: paymentStatus.amount_usdc,
                            txn: paymentStatus.txn_signature
                        });
                    } else if (paymentStatus.status === "error") {
                        throw new Error(`Payment failed: ${paymentStatus.message}`);
                    } else {
                        await new Promise(resolve => setTimeout(resolve, 2000));
                        attempts++;
                    }
                }

                if (!paymentConfirmed) {
                    throw new Error("Payment confirmation timeout");
                }
            }

            return {
                status: "success",
                bountyId,
                steps,
                earnings: processResult.amount_usdc,
                txn: processResult.payment_id
            };

        } catch (e) {
            steps[steps.length - 1].status = "error";
            steps[steps.length - 1].error = e.message;

            return {
                status: "error",
                bountyId,
                steps,
                error: e.message
            };
        } finally {
            this.isProcessing = false;
        }
    }

    /**
     * Post a new bounty
     */
    async postBounty(bountyData) {
        if (!this.wallet.isConnected()) {
            throw new Error("Wallet not connected");
        }

        return this.api.postBounty({
            ...bountyData,
            payout_address: this.wallet.getAddress(),
            created_at: new Date().toISOString()
        });
    }
}

/**
 * UI Helper - Show loading spinner
 */
function showLoadingSpinner(message = "Processing...") {
    const spinner = document.createElement("div");
    spinner.id = "loading-spinner";
    spinner.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.6);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        z-index: 10000;
    `;
    
    spinner.innerHTML = `
        <div style="
            width: 50px;
            height: 50px;
            border: 5px solid #f3f3f3;
            border-top: 5px solid #3498db;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 20px;
        "></div>
        <p style="color: white; font-size: 16px; margin: 0;">${message}</p>
        <style>
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    `;
    
    document.body.appendChild(spinner);
    return spinner;
}

/**
 * UI Helper - Hide loading spinner
 */
function hideLoadingSpinner() {
    const spinner = document.getElementById("loading-spinner");
    if (spinner) {
        spinner.remove();
    }
}

/**
 * UI Helper - Show progress steps
 */
function showProgressSteps(steps) {
    const container = document.createElement("div");
    container.id = "progress-steps";
    container.style.cssText = `
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin-top: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    `;
    
    const html = steps.map((step, idx) => {
        const icon = step.status === "complete" ? "✓" : 
                    step.status === "error" ? "✗" : "⏳";
        const color = step.status === "complete" ? "#2ecc71" :
                     step.status === "error" ? "#e74c3c" : "#3498db";
        
        return `
            <div style="
                display: flex;
                align-items: center;
                margin-bottom: ${idx === steps.length - 1 ? "0" : "12px"};
                opacity: ${step.status === "pending" ? "0.6" : "1"};
            ">
                <span style="
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    width: 30px;
                    height: 30px;
                    border-radius: 50%;
                    background: ${color};
                    color: white;
                    font-weight: bold;
                    margin-right: 12px;
                    flex-shrink: 0;
                ">${icon}</span>
                <span style="flex-grow: 1;">${step.name}</span>
                ${step.amount ? `<span style="color: #27ae60; font-weight: bold;">+$${step.amount.toFixed(2)}</span>` : ""}
            </div>
        `;
    }).join("");
    
    container.innerHTML = html;
    return container;
}

// Global instances
let walletManager = null;
let apiClient = null;
let siftManager = null;

// Initialize on page load
document.addEventListener("DOMContentLoaded", async function() {
    walletManager = new WalletManager();
    apiClient = new APIClient();
    siftManager = new MoltSiftManager(walletManager, apiClient);
    
    // Check if wallet is available
    const walletAvailable = await walletManager.initialize();
    
    // Update UI to show wallet status
    const walletBtn = document.getElementById("connectWalletBtn");
    if (walletBtn) {
        if (walletAvailable) {
            walletBtn.innerHTML = "🔓 Connect Wallet";
            walletBtn.onclick = async () => {
                try {
                    showLoadingSpinner("Connecting wallet...");
                    const address = await walletManager.connect();
                    hideLoadingSpinner();
                    updateWalletUI(address);
                    showNotification(`Connected: ${address.slice(0, 8)}...`, "success");
                } catch (e) {
                    hideLoadingSpinner();
                    showNotification(e.message, "error");
                }
            };
        } else {
            walletBtn.innerHTML = "⚠️ No Wallet Detected";
            walletBtn.disabled = true;
            showNotification("No Solana wallet detected. Install Phantom or Solflare.", "error");
        }
    }
    
    // Check API health
    const health = await apiClient.health();
    if (health.status !== "ok") {
        console.warn("API health check failed:", health);
    }
});

/**
 * Update UI to show connected wallet
 */
function updateWalletUI(address) {
    const walletBtn = document.getElementById("connectWalletBtn");
    if (walletBtn) {
        walletBtn.innerHTML = `✓ Connected: ${address.slice(0, 8)}...`;
        walletBtn.disabled = true;
    }
}

/**
 * Export for use in HTML
 */
window.MoltSift = {
    wallet: () => walletManager,
    api: () => apiClient,
    siftManager: () => siftManager,
    showLoadingSpinner,
    hideLoadingSpinner,
    showProgressSteps
};
