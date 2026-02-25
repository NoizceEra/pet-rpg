// Molt Sift Web Dashboard
// Manages bounty posting, claiming, and real-time updates

// Mock bounties database (will be replaced with real API)
let bounties = [
    {
        id: 1,
        title: "Validate Bitcoin Price Data",
        description: "Validate JSON crypto market data against schema",
        rules: "crypto",
        amount: 5.00,
        data: '{"symbol": "BTC", "price": 42850.50, "volume": 1500000000}',
        status: "available",
        createdBy: "user_123",
        createdAt: new Date(Date.now() - 3600000)
    },
    {
        id: 2,
        title: "Trading Order Validation",
        description: "Check if trading orders are properly formatted",
        rules: "trading",
        amount: 3.50,
        data: '{"order_id": "ord_123", "symbol": "ETH/USDT", "side": "buy", "price": 2450.00}',
        status: "available",
        createdBy: "agent_456",
        createdAt: new Date(Date.now() - 7200000)
    },
    {
        id: 3,
        title: "Sentiment Analysis Validation",
        description: "Validate sentiment scores for market sentiment",
        rules: "sentiment",
        amount: 2.00,
        data: '{"text": "Bitcoin is looking bullish", "score": 0.85}',
        status: "claimed",
        claimedBy: "agent_789",
        createdBy: "user_999",
        createdAt: new Date(Date.now() - 14400000)
    }
];

let stats = {
    totalBounties: 3,
    completed: 1,
    totalUsdc: 10.50,
    agents: 2
};

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    loadBounties();
    updateStats();
    setupEventListeners();
    setupModal();
});

function setupEventListeners() {
    // Form submission
    document.getElementById('bountyForm').addEventListener('submit', function(e) {
        e.preventDefault();
        postBounty();
    });

    // Search and filter
    document.getElementById('searchBounties').addEventListener('input', filterBounties);
    document.getElementById('filterRules').addEventListener('change', filterBounties);

    // Smooth scroll links
    document.querySelectorAll('a[onclick*="scrollTo"]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
        });
    });
}

function scrollTo(sectionId) {
    const element = document.getElementById(sectionId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
    }
}

function postBounty() {
    const rawData = document.getElementById('rawData').value.trim();
    const rules = document.getElementById('rules').value;
    const amount = parseFloat(document.getElementById('amount').value);
    const payoutAddr = document.getElementById('payoutAddr').value.trim();
    const description = document.getElementById('description').value.trim();

    // Validate
    if (!rawData || !rules || !amount || !payoutAddr) {
        alert('Please fill in all required fields');
        return;
    }

    // Validate JSON
    try {
        JSON.parse(rawData);
    } catch (e) {
        alert('Invalid JSON data: ' + e.message);
        return;
    }

    // Validate Solana address (basic check)
    if (payoutAddr.length < 32 || payoutAddr.length > 44) {
        alert('Invalid Solana address length');
        return;
    }

    // Create bounty
    const newBounty = {
        id: Math.max(...bounties.map(b => b.id), 0) + 1,
        title: description || `Validate ${rules} data`,
        description: description || `Validate data with ${rules} rules`,
        rules: rules,
        amount: amount,
        data: rawData,
        status: "available",
        createdBy: payoutAddr,
        createdAt: new Date(),
        payoutAddr: payoutAddr
    };

    bounties.unshift(newBounty);
    stats.totalBounties++;
    stats.totalUsdc += amount;

    // Reset form
    document.getElementById('bountyForm').reset();

    // Update UI
    loadBounties();
    updateStats();

    // Show success message
    showNotification('Bounty posted successfully!', 'success');
    
    // Scroll to bounties
    scrollTo('bounties');
}

function loadBounties() {
    const container = document.getElementById('bountiesList');
    
    if (bounties.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>No bounties yet. Be the first to post one!</p></div>';
        return;
    }

    container.innerHTML = bounties.map(bounty => `
        <div class="bounty-card" onclick="openBountyModal(${bounty.id})">
            <div class="bounty-header">
                <h4>${escapeHtml(bounty.title)}</h4>
                <span class="bounty-reward">$${bounty.amount.toFixed(2)}</span>
            </div>
            
            <span class="bounty-rules">${bounty.rules}</span>
            
            <p class="bounty-description">${escapeHtml(bounty.description)}</p>
            
            <div class="bounty-data-preview">${escapeHtml(bounty.data.substring(0, 100))}...</div>
            
            <div class="bounty-footer">
                <span class="bounty-status ${bounty.status}">${bounty.status === 'available' ? '✓ Available' : '⏳ Claimed'}</span>
                <button class="bounty-claim-btn" onclick="claimBounty(event, ${bounty.id})">
                    ${bounty.status === 'available' ? 'Claim' : 'View'}
                </button>
            </div>
        </div>
    `).join('');
}

function filterBounties() {
    const search = document.getElementById('searchBounties').value.toLowerCase();
    const rulesFilter = document.getElementById('filterRules').value;

    const filtered = bounties.filter(b => {
        const matchesSearch = b.title.toLowerCase().includes(search) || 
                            b.description.toLowerCase().includes(search);
        const matchesRules = !rulesFilter || b.rules === rulesFilter;
        return matchesSearch && matchesRules;
    });

    const container = document.getElementById('bountiesList');
    
    if (filtered.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>No bounties match your search.</p></div>';
        return;
    }

    container.innerHTML = filtered.map(bounty => `
        <div class="bounty-card" onclick="openBountyModal(${bounty.id})">
            <div class="bounty-header">
                <h4>${escapeHtml(bounty.title)}</h4>
                <span class="bounty-reward">$${bounty.amount.toFixed(2)}</span>
            </div>
            
            <span class="bounty-rules">${bounty.rules}</span>
            
            <p class="bounty-description">${escapeHtml(bounty.description)}</p>
            
            <div class="bounty-data-preview">${escapeHtml(bounty.data.substring(0, 100))}...</div>
            
            <div class="bounty-footer">
                <span class="bounty-status ${bounty.status}">${bounty.status === 'available' ? '✓ Available' : '⏳ Claimed'}</span>
                <button class="bounty-claim-btn" onclick="claimBounty(event, ${bounty.id})">
                    ${bounty.status === 'available' ? 'Claim' : 'View'}
                </button>
            </div>
        </div>
    `).join('');
}

function openBountyModal(bountyId) {
    const bounty = bounties.find(b => b.id === bountyId);
    if (!bounty) return;

    const modal = document.getElementById('bountyModal');
    const modalBody = document.getElementById('modalBody');

    modalBody.innerHTML = `
        <h3>${escapeHtml(bounty.title)}</h3>
        <p style="color: #666; margin-bottom: 20px;">${escapeHtml(bounty.description)}</p>
        
        <div style="background: #f5f5f5; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            <p><strong>Rules:</strong> ${bounty.rules}</p>
            <p><strong>Reward:</strong> $${bounty.amount.toFixed(2)} USDC</p>
            <p><strong>Status:</strong> ${bounty.status}</p>
            <p><strong>Posted:</strong> ${formatDate(bounty.createdAt)}</p>
        </div>
        
        <h4 style="margin-top: 20px; margin-bottom: 10px;">Data to Validate:</h4>
        <pre style="background: #f0f0f0; padding: 15px; border-radius: 8px; overflow-x: auto; font-size: 12px;">${escapeHtml(bounty.data)}</pre>
    `;

    const claimBtn = document.getElementById('claimBtn');
    claimBtn.textContent = bounty.status === 'available' ? 'Claim Bounty' : 'Already Claimed';
    claimBtn.disabled = bounty.status === 'claimed';
    claimBtn.onclick = () => claimBountyFromModal(bountyId);

    modal.style.display = 'block';
}

function claimBounty(event, bountyId) {
    event.stopPropagation();
    claimBountyFromModal(bountyId);
}

function claimBountyFromModal(bountyId) {
    const bounty = bounties.find(b => b.id === bountyId);
    if (!bounty || bounty.status === 'claimed') {
        alert('This bounty is no longer available');
        return;
    }

    // In real implementation, this would:
    // 1. Call molt-sift validation
    // 2. Submit result to PayAClaw
    // 3. Trigger Solana payment

    showNotification(`Bounty claimed! Running Molt Sift validation...`, 'info');

    // Simulate validation
    setTimeout(() => {
        bounty.status = 'claimed';
        bounty.claimedBy = 'agent_current';
        loadBounties();
        updateStats();
        
        document.getElementById('bountyModal').style.display = 'none';
        
        showNotification(`Validation complete! Submitting result...`, 'success');
        
        // Simulate payment
        setTimeout(() => {
            showNotification(`Payment initiated! $${bounty.amount.toFixed(2)} USDC sent.`, 'success');
        }, 1500);
    }, 2000);
}

function updateStats() {
    document.getElementById('statBounties').textContent = stats.totalBounties;
    document.getElementById('statCompleted').textContent = bounties.filter(b => b.status === 'claimed').length;
    document.getElementById('statUsdc').textContent = '$' + stats.totalUsdc.toFixed(2);
    document.getElementById('statAgents').textContent = new Set(bounties.map(b => b.createdBy || b.claimedBy)).size;
}

function setupModal() {
    const modal = document.getElementById('bountyModal');
    const closeBtn = document.querySelector('.close');

    closeBtn.onclick = () => {
        modal.style.display = 'none';
    };

    window.onclick = (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    };
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        font-weight: 600;
        z-index: 2000;
        animation: slideIn 0.3s ease;
    `;

    if (type === 'success') {
        notification.style.background = '#2ecc71';
        notification.style.color = 'white';
    } else if (type === 'error') {
        notification.style.background = '#e74c3c';
        notification.style.color = 'white';
    } else {
        notification.style.background = '#3498db';
        notification.style.color = 'white';
    }

    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function formatDate(date) {
    const now = new Date();
    const diff = now - date;
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (hours < 1) return 'Just now';
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;

    return date.toLocaleDateString();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Add CSS animation
const style = document.createElement('style');
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
