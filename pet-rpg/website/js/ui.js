/**
 * MoltGotchi UI Module
 * DOM manipulation, rendering, and event handling
 */

// ─────────────────────────────────────────────────────────────────────
// DOM Elements Cache
// ─────────────────────────────────────────────────────────────────────

const DOM = {
  // Main sections
  createPetSection: document.getElementById('create-pet-section'),
  petDashboard: document.getElementById('pet-dashboard'),
  mainContent: document.getElementById('main-content'),
  
  // Pet display
  petName: document.getElementById('pet-name'),
  petLevel: document.getElementById('pet-level'),
  petSprite: document.getElementById('pet-sprite'),
  petSpecies: document.getElementById('pet-species'),
  
  // Stat bars
  hpBar: document.getElementById('hp-bar'),
  hungerBar: document.getElementById('hunger-bar'),
  happinessBar: document.getElementById('happiness-bar'),
  
  // Stat values
  hpValue: document.getElementById('hp-value'),
  hungerValue: document.getElementById('hunger-value'),
  happinessValue: document.getElementById('happiness-value'),
  
  // Action buttons
  feedBtn: document.getElementById('feed-btn'),
  playBtn: document.getElementById('play-btn'),
  trainBtn: document.getElementById('train-btn'),
  restBtn: document.getElementById('rest-btn'),
  evolveBtn: document.getElementById('evolve-btn'),
  battleBtn: document.getElementById('battle-btn'),
  
  // Tables
  leaderboardTable: document.getElementById('leaderboard-table'),
  battlesTable: document.getElementById('battles-table'),
  
  // Modals
  createPetModal: document.getElementById('create-pet-modal'),
  trainModal: document.getElementById('train-modal'),
  battleModal: document.getElementById('battle-modal'),
  
  // Form inputs
  petNameInput: document.getElementById('pet-name-input'),
  petSpeciesSelect: document.getElementById('pet-species-select'),
  createPetBtn: document.getElementById('create-pet-btn'),
  
  // Notifications
  notificationContainer: document.getElementById('notification-container'),
};

// ─────────────────────────────────────────────────────────────────────
// Loading States
// ─────────────────────────────────────────────────────────────────────

function setLoading(show) {
  gameState.setLoading(show);
  const loaders = document.querySelectorAll('[data-loader]');
  loaders.forEach(loader => {
    loader.style.display = show ? 'block' : 'none';
  });
}

function showNotification(message, type = 'info') {
  const notification = gameState.addNotification(message, type);
  
  const div = document.createElement('div');
  div.className = `notification notification-${type}`;
  div.id = `notif-${notification.id}`;
  div.innerHTML = message;
  
  DOM.notificationContainer.appendChild(div);
  
  setTimeout(() => {
    const elem = document.getElementById(`notif-${notification.id}`);
    if (elem) elem.remove();
  }, UI_CONFIG.NOTIFICATION_DURATION);
}

// ─────────────────────────────────────────────────────────────────────
// Pet Display
// ─────────────────────────────────────────────────────────────────────

function renderPet(pet) {
  if (!pet) return;
  
  DOM.petName.textContent = pet.name || '???';
  DOM.petLevel.textContent = `Level ${pet.level}`;
  DOM.petSpecies.textContent = pet.species;
  
  // ASCII art sprite (placeholder - would be replaced with actual art)
  DOM.petSprite.textContent = `🐾 ${pet.species}`;
}

function renderStatus(pet) {
  if (!pet) return;
  
  renderPet(pet);
  
  // Update stat bars
  const hpPercent = (pet.hp / pet.max_hp) * 100;
  DOM.hpBar.style.width = hpPercent + '%';
  DOM.hpValue.textContent = `${pet.hp}/${pet.max_hp}`;
  
  const hungerPercent = pet.hunger || 0;
  DOM.hungerBar.style.width = hungerPercent + '%';
  DOM.hungerValue.textContent = Math.round(hungerPercent) + '%';
  
  const happinessPercent = pet.happiness || 0;
  DOM.happinessBar.style.width = happinessPercent + '%';
  DOM.happinessValue.textContent = Math.round(happinessPercent) + '%';
  
  // Store pet in state
  gameState.setPet(pet);
}

// ─────────────────────────────────────────────────────────────────────
// Tables Rendering
// ─────────────────────────────────────────────────────────────────────

function renderLeaderboard(pets) {
  const tbody = DOM.leaderboardTable.querySelector('tbody');
  tbody.innerHTML = '';
  
  pets.forEach((pet, index) => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${index + 1}</td>
      <td>${pet.name}</td>
      <td>${pet.owner_id || '???'}</td>
      <td>⚔️ ${pet.battles_won || 0}</td>
      <td>📊 Lvl ${pet.level}</td>
    `;
    tbody.appendChild(row);
  });
}

function renderBattles(battles) {
  const tbody = DOM.battlesTable.querySelector('tbody');
  tbody.innerHTML = '';
  
  battles.forEach((battle) => {
    const att = battle.attacker_name || 'Unknown';
    const def = battle.defender_name || 'Unknown';
    const winner = battle.winner === 'attacker' ? '✅' : '❌';
    
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${att} vs ${def}</td>
      <td>${winner}</td>
      <td>${battle.turns || '?'} turns</td>
      <td>${new Date(battle.timestamp).toLocaleDateString()}</td>
    `;
    tbody.appendChild(row);
  });
}

// ─────────────────────────────────────────────────────────────────────
// Section Visibility
// ─────────────────────────────────────────────────────────────────────

function showSection(section) {
  document.querySelectorAll('[data-section]').forEach(s => {
    s.style.display = 'none';
  });
  const target = document.querySelector(`[data-section="${section}"]`);
  if (target) target.style.display = 'block';
}

function showCreatePetUI() {
  DOM.createPetSection.style.display = 'block';
  DOM.petDashboard.style.display = 'none';
  showNotification('Create your first pet to get started!', 'info');
}

function showPetDashboard() {
  DOM.createPetSection.style.display = 'none';
  DOM.petDashboard.style.display = 'block';
}

// ─────────────────────────────────────────────────────────────────────
// Event Handlers - Pet Actions
// ─────────────────────────────────────────────────────────────────────

async function handleCreatePet() {
  const name = DOM.petNameInput.value.trim();
  const species = DOM.petSpeciesSelect.value;
  
  if (!name) {
    showNotification('Please enter a pet name', 'warning');
    return;
  }
  
  setLoading(true);
  try {
    const pet = await api.createPet(gameState.userId, name, species);
    gameState.setPet(pet);
    renderStatus(pet);
    showPetDashboard();
    showNotification(`${name} has hatched! 🥚`, 'success');
  } catch (error) {
    gameState.setError(error);
  } finally {
    setLoading(false);
  }
}

async function handleFeed() {
  setLoading(true);
  try {
    const pet = await api.feedPet(gameState.userId);
    renderStatus(pet);
    showNotification('Fed ' + pet.name + '! 🍖', 'success');
  } catch (error) {
    gameState.setError(error);
  } finally {
    setLoading(false);
  }
}

async function handlePlay() {
  setLoading(true);
  try {
    const pet = await api.playPet(gameState.userId);
    renderStatus(pet);
    showNotification(pet.name + ' had fun! 🎾', 'success');
  } catch (error) {
    gameState.setError(error);
  } finally {
    setLoading(false);
  }
}

async function handleTrain(stat) {
  setLoading(true);
  try {
    const pet = await api.trainPet(gameState.userId, stat);
    renderStatus(pet);
    showNotification(`Trained ${STAT_LABELS[stat]}! 💪`, 'success');
  } catch (error) {
    gameState.setError(error);
  } finally {
    setLoading(false);
  }
}

async function handleRest() {
  setLoading(true);
  try {
    const pet = await api.restPet(gameState.userId);
    renderStatus(pet);
    showNotification(pet.name + ' is rested! 😴', 'success');
  } catch (error) {
    gameState.setError(error);
  } finally {
    setLoading(false);
  }
}

// ─────────────────────────────────────────────────────────────────────
// Event Handlers - Battles
// ─────────────────────────────────────────────────────────────────────

async function handleBattle(opponentId, wager = 0) {
  if (!opponentId) {
    showNotification('Select an opponent!', 'warning');
    return;
  }
  
  setLoading(true);
  try {
    const result = await api.startBattle(gameState.userId, opponentId, wager);
    
    const winner = result.winner === 'attacker' 
      ? result.attacker_name 
      : result.defender_name;
    
    showNotification(`${winner} wins! ⚔️`, 'success');
    
    // Refresh pet and battles
    const pet = await api.getPet(gameState.userId);
    renderStatus(pet);
    refreshBattles();
    refreshLeaderboard();
  } catch (error) {
    gameState.setError(error);
  } finally {
    setLoading(false);
  }
}

// ─────────────────────────────────────────────────────────────────────
// Event Handlers - Leaderboard & Battles
// ─────────────────────────────────────────────────────────────────────

async function refreshLeaderboard() {
  try {
    const pets = await api.getLeaderboard(UI_CONFIG.LEADERBOARD_LIMIT);
    renderLeaderboard(pets);
  } catch (error) {
    console.error('Failed to load leaderboard:', error);
  }
}

async function refreshBattles() {
  try {
    const battles = await api.getBattles(gameState.userId, UI_CONFIG.BATTLES_PER_PAGE);
    renderBattles(battles);
  } catch (error) {
    console.error('Failed to load battles:', error);
  }
}

async function handleEvolution() {
  setLoading(true);
  try {
    const result = await api.checkEvolution(gameState.userId);
    if (result.evolved) {
      showNotification('Evolution! ✨', 'success');
      const pet = await api.getPet(gameState.userId);
      renderStatus(pet);
    } else {
      showNotification('Not ready to evolve yet', 'info');
    }
  } catch (error) {
    gameState.setError(error);
  } finally {
    setLoading(false);
  }
}

console.log('[UI] Initialized with DOM cache');
