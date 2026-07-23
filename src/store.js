// Simple JSON-file settings store (avoids native modules so `npm install` stays clean).
// Settings hold API keys and the user's résumé, so the file is encrypted at rest
// with the OS keychain (DPAPI on Windows, Keychain on macOS) via safeStorage.
// Falls back to plaintext only where no system encryption exists (some Linux).
const fs = require('fs');
const path = require('path');
const { app, safeStorage } = require('electron');

const FILE = path.join(app.getPath('userData'), 'nus-data.json');

const DEFAULTS = {
  provider: 'openai',
  smart: false,
  resumeContext: '',
  shortcuts: { assist: 'CommandOrControl+Return' },
  apiKeys: { openai: '', anthropic: '', gemini: '', nvidia: '' },
  models: {
    openai: { fast: 'gpt-4o-mini', smart: 'gpt-4o' },
    anthropic: { fast: 'claude-3-5-haiku-latest', smart: 'claude-3-5-sonnet-latest' },
    gemini: { fast: 'gemini-2.5-flash', smart: 'gemini-2.5-pro' },
    nvidia: { fast: 'meta/llama-3.2-11b-vision-instruct', smart: 'meta/llama-3.2-90b-vision-instruct' }
  }
};

let data = null;

function deepMerge(base, over) {
  const out = Array.isArray(base) ? base.slice() : { ...base };
  for (const k of Object.keys(over || {})) {
    if (over[k] && typeof over[k] === 'object' && !Array.isArray(over[k]) && typeof base[k] === 'object') {
      out[k] = deepMerge(base[k], over[k]);
    } else {
      out[k] = over[k];
    }
  }
  return out;
}

function load() {
  if (data) return data;
  let legacyPlaintext = false;
  try {
    const raw = JSON.parse(fs.readFileSync(FILE, 'utf8'));
    if (raw && raw.encrypted && typeof raw.payload === 'string') {
      const plain = safeStorage.decryptString(Buffer.from(raw.payload, 'base64'));
      data = deepMerge(DEFAULTS, JSON.parse(plain));
    } else {
      data = deepMerge(DEFAULTS, raw); // legacy plaintext file
      legacyPlaintext = true;
    }
  }
  catch { data = deepMerge(DEFAULTS, {}); }

  // Auto-switch provider if the current one has no key, but another one does.
  if (!data.apiKeys[data.provider]) {
    const validProviders = ['openai', 'anthropic', 'gemini', 'nvidia'];
    const active = validProviders.find(p => data.apiKeys[p]);
    if (active) {
      data.provider = active;
      // We don't save() here so we don't spam disk, it will persist on next save.
    }
  }

  if (legacyPlaintext) save(); // re-encrypt at rest on first read
  return data;
}
function save() {
  try {
    const json = JSON.stringify(data, null, 2);
    if (safeStorage.isEncryptionAvailable()) {
      const payload = safeStorage.encryptString(json).toString('base64');
      fs.writeFileSync(FILE, JSON.stringify({ encrypted: true, payload }), { mode: 0o600 });
    } else {
      fs.writeFileSync(FILE, json, { mode: 0o600 });
    }
  } catch (e) { /* ignore */ }
}

module.exports = {
  getSettings() { return load(); },
  setSettings(patch) { load(); data = deepMerge(data, patch || {}); save(); return data; }
};
