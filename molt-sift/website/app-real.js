/**
 * Molt Sift Web Dashboard - Real API Integration
 * Complete bounty posting, claiming, validation, and payment flow
 */

// Global state
let bounties = [];
let stats = {
    totalBounties: 0,
    completed: 0,
    totalUsdc: 0,
    agents: 0
};

// API client instance (initialized after wallet-connection.js)
let api = null;
let sift = null;

// Initialize on page load
document.addEventListener("DOMContentLoaded", async function() {
    // Wait for wallet-connection.js to initialize
    const checkInterval = setInterval(() => {
        if (window.MoltSift && window.MoltSift.api()) {
            clearInterval(checkInterval);
            api = window.MoltSift.api();
            sift = window.MoltSift.siftManager();
            initializeDashboard();
        }
    }, 100);
    
    // Timeout after 5 seconds
    setTimeout(() => clearInterval(checkInterval), 5000);
});

/**
 * Initialize dashboard
 */
async function initializeDashboard() {
    console.log("Initializing Molt Sift Dashboard...");
    
    setupEventListeners();
    setupModal();
    
    // Load initial bounties
    await refreshBounties();
    
    // Refresh bounties every 30 seconds
    setInterval(refreshBounties, 30000);
    
    console.log("✓ Dashboard initialized");
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    const bountyForm = document.getElementById("bountyForm");
    if (bountyForm) {
        bountyForm.addEventListener("submit", postBountyHandler);
    }
    
    const searchInput = document.getElementById("searchBounties");
    if (searchInput) {
        searchInput.addEventListener("input", filterBounties);
    }
    
    const filterSelect = document.getElementById("filterRules");
    if (filterSelect) {
        filterSelect.addEventListener("change", filterBounties);
    }
    
    // Smooth scroll links
    document.querySelectorAll("a[onclick*='scrollTo']").forEach(link => {
        link.addEventListener("click", function(e) {
            e.preventDefault();
        });
    });
}

/**
 * Refresh bounties from API
 */
async function refreshBounties() {
    try {
        const response = await api.getBounties();
        
        if (response.status === "error") {
            console.error("Failed to fetch bounties:", response.message);
            showNotification("Failed to load bounties", "error");
            return;
        }
        
        bounties = response.bounties || [];
        updateStats();
        loadBounties();
        
        console.log(`✓ Loaded ${bounties.length} bounties`);
        
    } catch (e) {
        console.error("Bounty refresh error:", e);
        showNotification("Error loading bounties", "error");
    }
}

/**
 * Post bounty handler
 */
async function postBountyHandler(e) {
    e.preventDefault();
    
    const wallet = window.MoltSift.wallet();
    if (!wallet.isConnected()) {
        showNotification("Please connect wallet first", "error");
        return;
    }
    
    const rawData = document.getElementById("rawData").value.trim();
    const rules = document.getElementById("rules").value;
    const amount = parseFloat(document.getElementById("amount").value);
    const description = document.getElementById("description").value.trim();
    
    // Validation
    if (!rawData || !rules || !amount || amount <= 0) {
        showNotification("Please fill in all required fields with valid values", "error");
        return;
    }
    
    // Validate JSON
    try {
        JSON.parse(rawData);
    } catch (e) {
        showNotification(`Invalid JSON: ${e.message}`, "error");
        return;
    }
    
    const spinner = window.MoltSift.showLoadingSpinner("Posting bounty...");
    
    try {
        const result = await sift.postBounty({
            title: description || `Validate ${rules} data`,
            description: description || `Validate data with ${rules} rules`,
            rules,
            amount,
            raw_data: rawData
        });
        
        if (result.status === "error") {
            throw new Error(result.message);
        }
        
        window.MoltSift.hideLoadingSpinner();
        
        // Reset form
        document.getElementById("bountyForm").reset();
        
        // Refresh bounties
        await refreshBounties();
        
        showNotification(`✓ Bounty posted! Earning $${amount.toFixed(2)} USDC`, "success");
        scrollTo("bounties");
        
    } catch (e) {
        window.MoltSift.hideLoadingSpinner();
        console.error("Post bounty error:", e);
        showNotification(e.message || "Failed to post bounty", "error");
    }
}

/**
 * Load bounties into DOM
 */
function loadBounties() {
    const container = document.getElementById("bountiesList");
    
    if (!container) return;
    
    if (bounties.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <p>No bounties available. Be the first to post one!</p>
                <p style="font-size: 12px; color: #999; margin-top: 10px;">
                    Bounties refresh every 30 seconds
                </p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = bounties.map(bounty => `
        <div class="bounty-card" onclick="openBountyModal('${bounty.id || bounty.job_id}')">
            <div class="bounty-header">
                <h4>${escapeHtml(bounty.title || `Job ${bounty.id}`)}</h4>
                <span class="bounty-reward">$${(bounty.amount || bounty.amount_usdc || 0).toFixed(2)}</span>
            </div>
            
            <span class="bounty-rules">${bounty.rules || bounty.validation_rules || 'general'}</span>
            
            <p class="bounty-description">${escapeHtml(bounty.description || 'Validate data')}</p>
            
            <div class="bounty-data-preview">
                ${escapeHtml(
                    (typeof bounty.data === 'string' ? bounty.data : JSON.stringify(bounty.data || {}))
                    .substring(0, 100)
                )}...
            </div>
            
            <div class="bounty-footer">
                <span class="bounty-status ${bounty.status === 'open' ? 'available' : 'claimed'}">
                    ${bounty.status === 'open' ? '✓ Available' : '⏳ Claimed'}
                </span>
                <button class="bounty-claim-btn" onclick="claimBountyBtn(event, '${bounty.id || bounty.job_id}')">
                    ${bounty.status === 'open' ? 'Claim & Validate' : 'View'}
                </button>
            </div>
        </div>
    `).join("");
}

/**
 * Filter bounties
 */
function filterBounties() {
    const search = document.getElementById("searchBounties").value.toLowerCase();
    const rulesFilter = document.getElementById("filterRules").value;
    
    const filtered = bounties.filter(b => {
        const title = (b.title || "").toLowerCase();
        const description = (b.description || "").toLowerCase();
        const rules = (b.rules || b.validation_rules || "").toLowerCase();
        
        const matchesSearch = title.includes(search) || description.includes(search);
        const matchesRules = !rulesFilter || rules === rulesFilter;
        return matchesSearch && matchesRules;
    });
    
    const container = document.getElementById("bountiesList");
    
    if (filtered.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>No bounties match your search.</p></div>';
        return;
    }
    
    container.innerHTML = filtered.map(bounty => `
        <div class="bounty-card" onclick="openBountyModal('${bounty.id || bounty.job_id}')">
            <div class="bounty-header">
                <h4>${escapeHtml(bounty.title || `Job ${bounty.id}`)}</h4>
                <span class="bounty-reward">$${(bounty.amount || bounty.amount_usdc || 0).toFixed(2)}</span>
            </div>
            
            <span class="bounty-rules">${bounty.rules || bounty.validation_rules || 'general'}</span>
            
            <p class="bounty-description">${escapeHtml(bounty.description || 'Validate data')}</p>
            
            <div class="bounty-data-preview">
                ${escapeHtml(
                    (typeof bounty.data === 'string' ? bounty.data : JSON.stringify(bounty.data || {}))
                    .substring(0, 100)
                )}...
            </div>
            
            <div class="bounty-footer">
                <span class="bounty-status ${bounty.status === 'open' ? 'available' : 'claimed'}">
                    ${bounty.status === 'open' ? '✓ Available' : '⏳ Claimed'}
                </span>
                <button class="bounty-claim-btn" onclick="claimBountyBtn(event, '${bounty.id || bounty.job_id}')">
                    ${bounty.status === 'open' ? 'Claim & Validate' : 'View'}
                </button>
            </div>
        </div>
    `).join("");
}

/**
 * Open bounty modal
 */
function openBountyModal(bountyId) {
    const bounty = bounties.find(b => (b.id || b.job_id) === bountyId);
    if (!bounty) return;
    
    const modal = document.getElementById("bountyModal");
    const modalBody = document.getElementById("modalBody");
    
    const dataStr = typeof bounty.data === 'string' ? bounty.data : JSON.stringify(bounty.data || {}, null, 2);
    
    modalBody.innerHTML = `
        <h3>${escapeHtml(bounty.title || `Job ${bounty.id}`)}</h3>
        <p style="color: #666; margin-bottom: 20px;">${escapeHtml(bounty.description || 'Validate this data')}</p>
        
        <div style="background: #f5f5f5; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            <p><strong>Rules:</strong> ${bounty.rules || bounty.validation_rules || 'general'}</p>
            <p><strong>Reward:</strong> $${(bounty.amount || bounty.amount_usdc || 0).toFixed(2)} USDC</p>
            <p><strong>Status:</strong> ${bounty.status === 'open' ? '✓ Available' : '⏳ Claimed'}</p>
            <p><strong>Posted:</strong> ${formatDate(bounty.created_at || bounty.createdAt || new Date())}</p>
        </div>
        
        <h4 style="margin-top: 20px; margin-bottom: 10px;">Data to Validate:</h4>
        <pre style="background: #f0f0f0; padding: 15px; border-radius: 8px; overflow-x: auto; font-size: 12px;">${escapeHtml(dataStr)}</pre>
    `;
    
    const claimBtn = document.getElementById("claimBtn");
    claimBtn.textContent = bounty.status === 'open' ? 'Claim & Validate' : 'Already Claimed';
    claimBtn.disabled = bounty.status !== 'open';
    claimBtn.onclick = () => claimBountyFromModal(bountyId);
    
    modal.style.display = "block";
}

/**
 * Claim bounty button handler
 */
function claimBountyBtn(event, bountyId) {
    event.stopPropagation();
    claimBountyFromModal(bountyId);
}

/**
 * Claim bounty from modal
 */
async function claimBountyFromModal(bountyId) {
    const wallet = window.MoltSift.wallet();
    if (!wallet.isConnected()) {
        showNotification("Please connect wallet first", "error");
        return;
    }
    
    const bounty = bounties.find(b => (b.id || b.job_id) === bountyId);
    if (!bounty || bounty.status !== 'open') {
        showNotification("This bounty is no longer available", "error");
        return;
    }
    
    // Close modal
    document.getElementById("bountyModal").style.display = "none";
    
    // Process bounty
    try {
        const result = await sift.claimAndProcess(bountyId);
        
        if (result.status === "success") {
            // Show progress steps
            const progressContainer = document.getElementById("bountiesList");
            progressContainer.insertBefore(
                window.MoltSift.showProgressSteps(result.steps),
                progressContainer.firstChild
            );
            
            showNotification(
                `✓ Success! Earned $${result.earnings.toFixed(2)} USDC`,
                "success"
            );
            
            // Refresh bounties
            await refreshBounties();
            
        } else {
            showNotification(
                `Error: ${result.error || 'Processing failed'}`,
                "error"
            );
            
            // Show failed steps for debugging
            const progressContainer = document.getElementById("bountiesList");
            progressContainer.insertBefore(
                window.MoltSift.showProgressSteps(result.steps),
                progressContainer.firstChild
            );
        }
        
    } catch (e) {
        console.error("Claim bounty error:", e);
        showNotification(e.message || "Failed to process bounty", "error");
    }
}

/**
 * Update statistics
 */
function updateStats() {
    const statBounties = document.getElementById("statBounties");
    const statCompleted = document.getElementById("statCompleted");
    const statUsdc = document.getElementById("statUsdc");
    const statAgents = document.getElementById("statAgents");
    
    if (statBounties) statBounties.textContent = bounties.length;
    if (statCompleted) statCompleted.textContent = bounties.filter(b => b.status !== 'open').length;
    
    const totalUsdc = bounties.reduce((sum, b) => sum + (b.amount || b.amount_usdc || 0), 0);
    if (statUsdc) statUsdc.textContent = "$" + totalUsdc.toFixed(2);
    
    const agents = new Set();
    bounties.forEach(b => {
        if (b.created_by || b.createdBy) agents.add(b.created_by || b.createdBy);
    });
    if (statAgents) statAgents.textContent = agents.size;
}

/**
 * Setup modal
 */
function setupModal() {
    const modal = document.getElementById("bountyModal");
    const closeBtn = document.querySelector(".close");
    
    if (closeBtn) {
        closeBtn.onclick = () => {
            modal.style.display = "none";
        };
    }
    
    window.onclick = (event) => {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    };
}

/**
 * Scroll to section
 */
function scrollTo(sectionId) {
    const element = document.getElementById(sectionId);
    if (element) {
        element.scrollIntoView({ behavior: "smooth" });
    }
}

/**
 * Show notification
 */
function showNotification(message, type = "info") {
    const notification = document.createElement("div");
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        font-weight: 600;
        z-index: 2000;
        animation: slideIn 0.3s ease;
        max-width: 400px;
    `;
    
    if (type === "success") {
        notification.style.background = "#2ecc71";
        notification.style.color = "white";
    } else if (type === "error") {
        notification.style.background = "#e74c3c";
        notification.style.color = "white";
    } else {
        notification.style.background = "#3498db";
        notification.style.color = "white";
    }
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = "slideOut 0.3s ease";
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

/**
 * Format date
 */
function formatDate(date) {
    if (!date) return "Unknown";
    const dateObj = new Date(date);
    const now = new Date();
    const diff = now - dateObj;
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (hours < 1) return "Just now";
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    
    return dateObj.toLocaleDateString();
}

/**
 * Escape HTML
 */
function escapeHtml(text) {
    if (!text) return "";
    const div = document.createElement("div");
    div.textContent = String(text);
    return div.innerHTML;
}

// Add CSS animations
const style = document.createElement("style");
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
