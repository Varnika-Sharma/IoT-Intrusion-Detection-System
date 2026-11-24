/**
 * IoT IDS — main.js
 * Shared utilities used across all pages.
 * Loaded in base.html for every page.
 */

/* ── Clock ──────────────────────────────────────────────────────────────── */
function updateClock() {
  const el = document.getElementById('topbar-time');
  if (el) {
    const now = new Date();
    el.textContent = now.toLocaleTimeString('en-IN', { hour12: false }) + '  ' +
                     now.toLocaleDateString('en-IN', { day:'2-digit', month:'short', year:'numeric' });
  }
}
updateClock();
setInterval(updateClock, 1000);

/* ── Sidebar toggle (mobile) ─────────────────────────────────────────────── */
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
}

/* ── API fetch helper ─────────────────────────────────────────────────────── */
/**
 * apiFetch(url, method='GET') → parsed JSON or null on error.
 * All API calls go through this so errors are handled uniformly.
 */
async function apiFetch(url, method = 'GET') {
  try {
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
    });
    if (!res.ok) {
      console.error(`API error ${res.status} for ${url}`);
      return null;
    }
    return await res.json();
  } catch (err) {
    console.error('Network error:', err);
    return null;
  }
}

/* ── Toast notifications ─────────────────────────────────────────────────── */
let toastTimer = null;
/**
 * showToast(message, type)
 * type: 'success' | 'danger' | 'info'
 */
function showToast(message, type = 'info') {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = message;
  toast.className = `toast ${type} visible`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.classList.remove('visible');
  }, 4000);
}

/* ── DOM helpers ─────────────────────────────────────────────────────────── */
function setInnerText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

function escHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

/** Format ISO timestamp to relative or short form */
function formatTime(ts) {
  if (!ts) return '—';
  const d = new Date(ts.replace(' ', 'T'));
  const now = new Date();
  const diff = Math.floor((now - d) / 1000); // seconds

  if (diff < 60)  return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return ts.substring(0, 16);
}

/* ── Alert badge (sidebar) ──────────────────────────────────────────────── */
async function refreshBadge() {
  const stats = await apiFetch('/api/stats');
  if (!stats) return;
  updateAlertBadge(stats.open_alerts);
  updateSystemPill(stats.system_status);
}

function updateAlertBadge(count) {
  const badge = document.getElementById('alert-badge');
  if (badge) {
    badge.textContent = count;
    badge.style.display = count > 0 ? 'inline-block' : 'none';
  }
}

function updateSystemPill(status) {
  const pill     = document.getElementById('system-status-pill');
  const dot      = pill?.querySelector('.status-dot');
  const textEl   = pill?.querySelector('.status-text');
  if (!pill) return;

  textEl.textContent = status;

  const colors = { SECURE: '#22c55e', WARNING: '#f59e0b', CRITICAL: '#ef4444' };
  const col = colors[status] || '#22c55e';
  if (dot) {
    dot.style.background  = col;
    dot.style.boxShadow   = `0 0 6px ${col}`;
  }
}

/* Initialize badge on every page load */
refreshBadge();
