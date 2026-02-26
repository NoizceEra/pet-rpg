/**
 * Configuration for MoltGotchi Web Client
 * Handles environment detection, API endpoints, and constants
 */

// ─────────────────────────────────────────────────────────────────
// API Configuration
// ─────────────────────────────────────────────────────────────────

// Auto-detect if running locally or in production
const isLocalhost = window.location.hostname === 'localhost' || 
                   window.location.hostname === '127.0.0.1' ||
                   window.location.hostname === '::1';

// ─────────────────────────────────────────────────────────────────
// API Endpoint Configuration
// ─────────────────────────────────────────────────────────────────
// 
// Local:      http://localhost:5000/api
// Production: Set via environment variable or window object
//
// To set in production:
// 1. Via Vercel environment variable: VITE_API_URL
// 2. Via window object before scripts load:
//    window.MOLTGOTCHI_API_URL = 'https://...'
// 3. Via meta tag:
//    <meta name="moltgotchi:api-url" content="https://...">
//
// OFFLINE MODE ENABLED - No external API calls
// All gameplay runs locally via localStorage
const API_BASE_URL = null; // null = localStorage demo mode (no external API)

console.log(`[MoltGotchi] Running in ${isLocalhost ? 'LOCAL' : 'PRODUCTION'} mode`);
console.log(`[MoltGotchi] API URL: ${API_BASE_URL}`);

// ─────────────────────────────────────────────────────────────────
// Storage Keys (localStorage)
// ─────────────────────────────────────────────────────────────────

const STORAGE_KEYS = {
  USER_ID: 'moltgotchi_user_id',
  CURRENT_PET: 'moltgotchi_current_pet',
  LAST_LEADERBOARD: 'moltgotchi_last_leaderboard',
  THEME: 'moltgotchi_theme',
};

// ─────────────────────────────────────────────────────────────────
// UI Constants
// ─────────────────────────────────────────────────────────────────

const UI_CONFIG = {
  // Auto-refresh intervals (milliseconds)
  LEADERBOARD_REFRESH: 30000,      // 30 seconds
  BATTLE_REFRESH: 10000,            // 10 seconds
  PET_STATUS_REFRESH: 5000,         // 5 seconds
  
  // Loading/timeout
  API_TIMEOUT: 8000,                // 8 seconds
  NOTIFICATION_DURATION: 3000,      // 3 seconds
  
  // Pagination
  BATTLES_PER_PAGE: 10,
  LEADERBOARD_LIMIT: 10,
  
  // Species limits
  MAX_PETS_PER_USER: 1,
};

// ─────────────────────────────────────────────────────────────────
// Stat Types
// ─────────────────────────────────────────────────────────────────

const STAT_TYPES = {
  STR: 'strength',
  SPD: 'speed',
  INT: 'intelligence',
};

const STAT_LABELS = {
  strength: 'Strength',
  speed: 'Speed',
  intelligence: 'Intelligence',
};

// ─────────────────────────────────────────────────────────────────
// Species with ASCII Art
// ─────────────────────────────────────────────────────────────────

const SPECIES = ['MoltCrab', 'Dragon', 'Phoenix', 'Titan', 'Mystic', 'Shadow', 'Gleam', 'Nova'];

const SPECIES_ASCII = {
  'MoltCrab': `
    ╔════════════════════╗
    ║                    ║
    ║   🦀 MoltCrab 🦀   ║
    ║                    ║
    ║   /\\_/\\_/\\        ║
    ║  ( o.o ) 🦀        ║
    ║   > ^ <             ║
    ║   / | \\             ║
    ║  /_____\\            ║
    ║                    ║
    ╚════════════════════╝
  `,
  'Dragon': `
    ╔════════════════════╗
    ║                    ║
    ║   🐉 Dragon 🐉     ║
    ║                    ║
    ║      /\\___/\\       ║
    ║     ( o   o )      ║
    ║      \\ ^ /         ║
    ║       |||||        ║
    ║      /|||||\\       ║
    ║                    ║
    ╚════════════════════╝
  `,
  'Phoenix': `
    ╔════════════════════╗
    ║                    ║
    ║   🔥 Phoenix 🔥    ║
    ║                    ║
    ║        (★)         ║
    ║       /o o\\        ║
    ║      ( ^ ^ )       ║
    ║       \\ ~ /        ║
    ║      (/|\\\\)        ║
    ║                    ║
    ╚════════════════════╝
  `,
  'Titan': `
    ╔════════════════════╗
    ║                    ║
    ║   💪 Titan 💪      ║
    ║                    ║
    ║       __           ║
    ║      /  \\          ║
    ║     | UU |         ║
    ║      \\ T /         ║
    ║      /   \\         ║
    ║                    ║
    ╚════════════════════╝
  `,
  'Mystic': `
    ╔════════════════════╗
    ║                    ║
    ║   ✨ Mystic ✨     ║
    ║                    ║
    ║       / o \\        ║
    ║      ( ∞ ∞ )       ║
    ║       \\ u /        ║
    ║       *||*         ║
    ║      * || *        ║
    ║                    ║
    ╚════════════════════╝
  `,
  'Shadow': `
    ╔════════════════════╗
    ║                    ║
    ║   👤 Shadow 👤     ║
    ║                    ║
    ║      ▓▓▓▓▓         ║
    ║     ▓ ◕ ◕ ▓        ║
    ║     ▓  >  ▓        ║
    ║      ▓▓▓▓▓         ║
    ║       ▓▓▓▓         ║
    ║                    ║
    ╚════════════════════╝
  `,
  'Gleam': `
    ╔════════════════════╗
    ║                    ║
    ║   ⭐ Gleam ⭐      ║
    ║                    ║
    ║       ★★★          ║
    ║      ★ o o ★      ║
    ║       ★ ◡ ★        ║
    ║      ★★★★★        ║
    ║       ★★★         ║
    ║                    ║
    ╚════════════════════╝
  `,
  'Nova': `
    ╔════════════════════╗
    ║                    ║
    ║   🌟 Nova 🌟       ║
    ║                    ║
    ║      ✦ ◉ ✦        ║
    ║     ◉ (◕◕) ◉      ║
    ║      ✦ ◡ ✦        ║
    ║       ✦✦✦         ║
    ║      ✦ ◉ ✦        ║
    ║                    ║
    ╚════════════════════╝
  `,
};

// ─────────────────────────────────────────────────────────────────
// Evolution Stages
// ─────────────────────────────────────────────────────────────────

const EVOLUTION_STAGES = ['EGG', 'BABY', 'TEEN', 'ADULT', 'LEGENDARY'];
const EVOLUTION_PATHS = ['GUARDIAN', 'WARRIOR', 'BALANCED'];

// ─────────────────────────────────────────────────────────────────
// Messages & Emojis
// ─────────────────────────────────────────────────────────────────

const MESSAGES = {
  LOADING: '⏳ Loading...',
  ERROR: '❌ Error',
  SUCCESS: '✅ Success',
  WELCOME: '🎉 Welcome!',
  NO_PET: '❌ No pet found. Create one!',
  OFFLINE: '📡 Connection error. Check API URL.',
};

const EMOJIS = {
  PET: '🐾',
  BATTLE: '⚔️',
  LEVEL_UP: '⬆️',
  EVOLUTION: '✨',
  FEED: '🍖',
  PLAY: '🎾',
  TRAIN: '💪',
  REST: '😴',
  LEADERBOARD: '🏆',
  ERROR: '❌',
  SUCCESS: '✅',
};
