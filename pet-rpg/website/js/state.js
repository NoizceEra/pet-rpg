/**
 * MoltGotchi Game State Management
 * Tracks current user, pet, and game state
 */

class GameState {
  constructor() {
    this.userId = this.loadOrGenerateUserId();
    this.currentPet = null;
    this.isLoading = false;
    this.notifications = [];
    this.lastError = null;
    this.selectedOpponent = null;
    this.isOnline = true;
  }

  /**
   * Load user ID from localStorage or generate a new one
   */
  loadOrGenerateUserId() {
    let userId = localStorage.getItem(STORAGE_KEYS.USER_ID);
    
    if (!userId) {
      // Generate unique user ID
      const timestamp = Date.now().toString(36);
      const random = Math.random().toString(36).substring(2, 9);
      userId = `player_${timestamp}_${random}`;
      localStorage.setItem(STORAGE_KEYS.USER_ID, userId);
      console.log(`[GameState] Generated new user ID: ${userId}`);
    }
    
    return userId;
  }

  /**
   * Set current pet
   */
  setPet(pet) {
    this.currentPet = pet;
    if (pet) {
      localStorage.setItem(STORAGE_KEYS.CURRENT_PET, JSON.stringify(pet));
    }
  }

  /**
   * Get current pet
   */
  getPet() {
    return this.currentPet;
  }

  /**
   * Clear current pet
   */
  clearPet() {
    this.currentPet = null;
    localStorage.removeItem(STORAGE_KEYS.CURRENT_PET);
  }

  /**
   * Set loading state
   */
  setLoading(isLoading) {
    this.isLoading = isLoading;
  }

  /**
   * Add notification to queue
   */
  addNotification(message, type = 'info') {
    const notification = {
      id: Date.now(),
      message,
      type, // 'success', 'error', 'info', 'warning'
      timestamp: new Date(),
    };
    this.notifications.push(notification);
    
    // Auto-remove after duration
    setTimeout(() => {
      this.notifications = this.notifications.filter(n => n.id !== notification.id);
    }, UI_CONFIG.NOTIFICATION_DURATION);
    
    return notification;
  }

  /**
   * Get all notifications
   */
  getNotifications() {
    return this.notifications;
  }

  /**
   * Clear all notifications
   */
  clearNotifications() {
    this.notifications = [];
  }

  /**
   * Set last error
   */
  setError(error) {
    this.lastError = error;
    this.addNotification(error.message || String(error), 'error');
  }

  /**
   * Set online/offline status
   */
  setOnline(isOnline) {
    this.isOnline = isOnline;
    if (!isOnline) {
      this.addNotification('Offline - some features unavailable', 'warning');
    }
  }

  /**
   * Get online status
   */
  getOnline() {
    return this.isOnline;
  }

  /**
   * Reset to initial state (on logout/reset)
   */
  reset() {
    this.currentPet = null;
    this.isLoading = false;
    this.notifications = [];
    this.lastError = null;
    this.selectedOpponent = null;
    localStorage.removeItem(STORAGE_KEYS.CURRENT_PET);
  }
}

// Initialize global game state
const gameState = new GameState();

console.log(`[GameState] Initialized for user: ${gameState.userId}`);
