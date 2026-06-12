// ─── Utilities & Core ──────────────────────────────────────

function toast(msg, type = 'info') {
  const c = document.getElementById('toastContainer');
  const t = document.createElement('div');
  const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
  t.className = `toast ${type}`;
  t.innerHTML = `<span>${icon}</span><span>${msg}</span>`;
  c.appendChild(t);
  setTimeout(() => { t.style.animation = 'fadeOut .3s ease forwards'; setTimeout(() => t.remove(), 300); }, 3500);
}

function openModal(title, bodyHtml) {
  document.getElementById('modalTitle').textContent = title;
  document.getElementById('modalBody').innerHTML = bodyHtml;
  document.getElementById('modalOverlay').classList.add('open');
}

function closeModal() {
  document.getElementById('modalOverlay').classList.remove('open');
}

function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('collapsed');
}

function badge(status) {
  const cls = { pending:'badge-pending', confirmed:'badge-confirmed', completed:'badge-completed',
    cancelled:'badge-cancelled', draft:'badge-draft', paid:'badge-paid' };
  return `<span class="badge ${cls[status]||'badge-draft'}">${status}</span>`;
}

function fmtDate(d) { return d ? new Date(d).toLocaleString('vi-VN') : '—'; }
function fmtMoney(n) { return Number(n).toLocaleString('vi-VN') + ' ₫'; }

function setLoading() {
  document.getElementById('content').innerHTML =
    `<div class="loading-screen"><div class="spinner"></div><p>Đang tải...</p></div>`;
}

// ─── Router ────────────────────────────────────────────────
const routes = { dashboard, patients, doctors, appointments, prescriptions, bills, inventory };

function navigate(page) {
  document.querySelectorAll('.nav-item').forEach(el => {
    el.classList.toggle('active', el.dataset.page === page);
  });
  document.getElementById('breadcrumb').textContent = PAGES[page] || page;
  setLoading();
  (routes[page] || dashboard)();
}

window.addEventListener('hashchange', () => {
  const page = location.hash.replace('#', '') || 'dashboard';
  navigate(page);
});

// ─── Clock ─────────────────────────────────────────────────
function startClock() {
  const el = document.getElementById('clock');
  setInterval(() => {
    el.textContent = new Date().toLocaleString('vi-VN', { hour:'2-digit', minute:'2-digit', second:'2-digit', day:'2-digit', month:'2-digit', year:'numeric' });
  }, 1000);
}

// ─── Init ──────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  startClock();
  checkAllServices();
  setInterval(checkAllServices, 15000);
  const page = location.hash.replace('#', '') || 'dashboard';
  navigate(page);
});
