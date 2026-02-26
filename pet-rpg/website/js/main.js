/**
 * MoltGotchi Main Application
 * Initialization and event binding
 */

// ─────────────────────────────────────────────────────────────────────
// Initialization
// ─────────────────────────────────────────────────────────────────────

async function initializeApp() {
  console.log('[App] Initializing MoltGotchi...');
  console.log('[App] OFFLINE MODE ENABLED - All gameplay is local');
  
  // Populate species dropdown
  populateSpeciesDropdown();
  
  // OFFLINE MODE: Always use localStorage
  gameState.setOnline(false);
  api.isAvailable = false;
  
  showNotification('🎮 OFFLINE MODE: Play locally with full pet gameplay!', 'info');
  
  // Try to load saved pet from localStorage
  const savedPetJson = localStorage.getItem('moltgotchi_pet_demo');
  if (savedPetJson) {
    try {
      const pet = JSON.parse(savedPetJson);
      gameState.setPet(pet);
      renderStatus(pet);
      showPetDashboard();
      console.log('[App] Loaded saved pet:', pet.name);
    } catch (e) {
      console.error('[App] Failed to load saved pet:', e);
      showCreatePetUI();
    }
  } else {
    showCreatePetUI();
  }
  
  console.log('[App] Initialization complete - offline mode active');
}

function populateSpeciesDropdown() {
  const select = DOM.petSpeciesSelect;
  
  // Clear existing options (except the default)
  while (select.children.length > 1) {
    select.removeChild(select.lastChild);
  }
  
  // Add species options
  SPECIES.forEach(species => {
    const option = document.createElement('option');
    option.value = species;
    option.textContent = species;
    select.appendChild(option);
  });
}

// ─────────────────────────────────────────────────────────────────────
// Event Listeners
// ─────────────────────────────────────────────────────────────────────

function bindEventListeners() {
  // Create pet
  DOM.createPetBtn.addEventListener('click', handleCreatePet);
  DOM.petNameInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleCreatePet();
  });
  
  // Care actions
  DOM.feedBtn.addEventListener('click', handleFeed);
  DOM.playBtn.addEventListener('click', handlePlay);
  DOM.restBtn.addEventListener('click', handleRest);
  DOM.evolveBtn.addEventListener('click', handleEvolution);
  
  // Training
  document.addEventListener('click', (e) => {
    if (e.target.dataset.stat) {
      handleTrain(e.target.dataset.stat);
    }
  });
  
  // Battle button
  DOM.battleBtn.addEventListener('click', () => {
    showBattleDialog();
  });
  
  // Battle form submission
  const battleForm = document.getElementById('battle-form');
  if (battleForm) {
    battleForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const opponentId = document.getElementById('opponent-id-input').value;
      const wager = parseFloat(document.getElementById('wager-input').value) || 0;
      handleBattle(opponentId, wager);
      closeBattleDialog();
    });
  }
  
  console.log('[App] Event listeners bound');
}

// ─────────────────────────────────────────────────────────────────────
// Modal Dialogs
// ─────────────────────────────────────────────────────────────────────

function showBattleDialog() {
  const modal = document.getElementById('battle-modal');
  if (modal) modal.style.display = 'block';
}

function closeBattleDialog() {
  const modal = document.getElementById('battle-modal');
  if (modal) modal.style.display = 'none';
}

// Close modals when clicking X
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('close-btn')) {
    e.target.closest('.modal').style.display = 'none';
  }
});

// Close modals when clicking outside
window.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal')) {
    e.target.style.display = 'none';
  }
});

// ─────────────────────────────────────────────────────────────────────
// Auto-Refresh Timers
// ─────────────────────────────────────────────────────────────────────

let leaderboardRefreshTimer = null;
let battlesRefreshTimer = null;

function startAutoRefresh() {
  // Refresh leaderboard every 30 seconds
  leaderboardRefreshTimer = setInterval(() => {
    if (gameState.getOnline()) {
      refreshLeaderboard().catch(console.error);
    }
  }, UI_CONFIG.LEADERBOARD_REFRESH);
  
  // Refresh battles every 10 seconds
  battlesRefreshTimer = setInterval(() => {
    if (gameState.getOnline()) {
      refreshBattles().catch(console.error);
    }
  }, UI_CONFIG.BATTLE_REFRESH);
  
  console.log('[App] Auto-refresh timers started');
}

function stopAutoRefresh() {
  if (leaderboardRefreshTimer) clearInterval(leaderboardRefreshTimer);
  if (battlesRefreshTimer) clearInterval(battlesRefreshTimer);
  console.log('[App] Auto-refresh timers stopped');
}

// ─────────────────────────────────────────────────────────────────────
// Online/Offline Detection
// ─────────────────────────────────────────────────────────────────────

window.addEventListener('online', () => {
  gameState.setOnline(true);
  showNotification('🌐 Back online!', 'success');
  startAutoRefresh();
});

window.addEventListener('offline', () => {
  gameState.setOnline(false);
  showNotification('📡 You are offline', 'warning');
  stopAutoRefresh();
});

// ─────────────────────────────────────────────────────────────────────
// Page Unload
// ─────────────────────────────────────────────────────────────────────

window.addEventListener('beforeunload', () => {
  stopAutoRefresh();
});

// ─────────────────────────────────────────────────────────────────────
// Main Entry Point
// ─────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  console.log('🐾 MoltGotchi Web Client Starting...');
  bindEventListeners();
  initializeApp();
});

console.log('[Main] Script loaded');
