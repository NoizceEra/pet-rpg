/**
 * MoltGotchi API Client
 * Wrapper around fetch() for all API communications
 */

class APIClient {
  constructor(baseURL) {
    this.baseURL = baseURL;
    this.timeout = UI_CONFIG.API_TIMEOUT;
  }

  /**
   * Wrapper for fetch with error handling and timeout
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      if (error.name === 'AbortError') {
        throw new Error('Request timeout - API may be offline');
      }
      throw error;
    }
  }

  // ─────────────────────────────────────────────────────────────
  // Health & Info
  // ─────────────────────────────────────────────────────────────

  async getHealth() {
    return this.request('/health');
  }

  async getSpecies() {
    return this.request('/species');
  }

  async getSpeciesDetail(name) {
    return this.request(`/species/${name}`);
  }

  // ─────────────────────────────────────────────────────────────
  // Pet Management
  // ─────────────────────────────────────────────────────────────

  async createPet(ownerId, name, species = 'MoltCrab') {
    return this.request('/pet/create', {
      method: 'POST',
      body: JSON.stringify({
        owner_id: ownerId,
        name: name || 'MoltPet',
        species: species,
      }),
    });
  }

  async getPet(ownerId) {
    return this.request(`/pet/${ownerId}`);
  }

  async getPetStatus(ownerId) {
    return this.request(`/pet/${ownerId}/status`);
  }

  async deletePet(ownerId) {
    return this.request(`/pet/${ownerId}`, {
      method: 'DELETE',
    });
  }

  // ─────────────────────────────────────────────────────────────
  // Care Actions
  // ─────────────────────────────────────────────────────────────

  async feedPet(ownerId) {
    return this.request(`/pet/${ownerId}/feed`, {
      method: 'POST',
    });
  }

  async playPet(ownerId) {
    return this.request(`/pet/${ownerId}/play`, {
      method: 'POST',
    });
  }

  async trainPet(ownerId, stat = 'strength') {
    return this.request(`/pet/${ownerId}/train`, {
      method: 'POST',
      body: JSON.stringify({ stat }),
    });
  }

  async restPet(ownerId) {
    return this.request(`/pet/${ownerId}/rest`, {
      method: 'POST',
    });
  }

  // ─────────────────────────────────────────────────────────────
  // Evolution
  // ─────────────────────────────────────────────────────────────

  async getEvolutionProgress(ownerId) {
    return this.request(`/pet/${ownerId}/evolution`);
  }

  async checkEvolution(ownerId) {
    return this.request(`/pet/${ownerId}/evolve`, {
      method: 'POST',
    });
  }

  // ─────────────────────────────────────────────────────────────
  // Battles
  // ─────────────────────────────────────────────────────────────

  async startBattle(attackerOwner, defenderOwner, wager = 0.0) {
    return this.request('/battle', {
      method: 'POST',
      body: JSON.stringify({
        attacker_owner: attackerOwner,
        defender_owner: defenderOwner,
        wager: wager,
      }),
    });
  }

  async getBattles(ownerId, limit = 10) {
    return this.request(`/battles/${ownerId}?limit=${limit}`);
  }

  async getHeadToHead(ownerId, opponentId) {
    return this.request(`/battles/${ownerId}/h2h/${opponentId}`);
  }

  async getBattle(battleId) {
    return this.request(`/battle/${battleId}`);
  }

  // ─────────────────────────────────────────────────────────────
  // Leaderboard
  // ─────────────────────────────────────────────────────────────

  async getLeaderboard(limit = 10) {
    return this.request(`/leaderboard?limit=${limit}`);
  }
}

// Initialize global API client
const api = new APIClient(API_BASE_URL || 'http://localhost:5000/api');

// Track if API is available
api.isAvailable = API_BASE_URL !== null;

console.log('[APIClient] Initialized with', API_BASE_URL || 'DEMO MODE (no API)');
if (!api.isAvailable) {
  console.log('[APIClient] Running in DEMO mode - API calls will be simulated');
}
