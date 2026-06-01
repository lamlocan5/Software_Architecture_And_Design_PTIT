/* ============================================
   chat.js - AI Shopping Assistant Terminal (Quantum UI)
   ============================================ */

const API_BASE = 'http://127.0.0.1:8000/api';
let isWaiting = false;

// ---- Khởi tạo ----
document.addEventListener('DOMContentLoaded', () => {
  loadSidebarProducts();
});

// ---- Load sản phẩm sidebar ----
async function loadSidebarProducts() {
  try {
    const res = await fetch(`${API_BASE}/products/?search=`);
    const data = await res.json();
    const products = (data.products || []).slice(0, 10);

    document.getElementById('sidebarProducts').innerHTML = products.map(p => `
      <div class="mini-card" onclick="askAboutProduct(${p.id}, '${escapeHtml(p.name)}')">
        <img src="${p.image_url || `https://picsum.photos/seed/product${p.id}/80/80`}"
             alt="${p.name}"
             onerror="this.src='https://picsum.photos/seed/tech${p.id}/80/80'">
        <div class="mini-info">
          <h4>${p.name}</h4>
          <p>${p.category}</p>
        </div>
      </div>
    `).join('');
  } catch(e) {
    document.getElementById('sidebarProducts').innerHTML =
      '<p style="color:var(--text-muted);font-size:0.75rem">Offline</p>';
  }
}

// ---- Gửi tin nhắn ----
async function sendMessage() {
  if (isWaiting) return;

  const input = document.getElementById('chatInput');
  const message = input.value.trim();
  if (!message) return;

  const userId = getUserId();

  // Hiển thị tin nhắn user
  appendMessage('user', message);
  input.value = '';
  input.style.height = 'auto';

  // Hiển thị typing indicator
  const typingId = showTyping();
  isWaiting = true;
  document.getElementById('sendBtn').disabled = true;

  try {
    const res = await fetch(`${API_BASE}/chat/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, user_id: userId })
    });
    const data = await res.json();

    removeTyping(typingId);
    appendMessage('ai', data.answer || 'Consultation failed. Neural link unstable.');
  } catch(err) {
    removeTyping(typingId);
    appendMessage('ai', '⚠️ CRITICAL_ERROR: Connection to Shopping Oracle lost.');
  } finally {
    isWaiting = false;
    document.getElementById('sendBtn').disabled = false;
  }
}

// ---- Thêm tin nhắn vào chat ----
function appendMessage(role, text) {
  const container = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = `msg ${role}`;

  // Format text
  const formatted = text
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong style="color:var(--accent)">$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code style="background:rgba(255,255,255,0.1);padding:2px 6px;border-radius:6px;font-size:0.85em">$1</code>');

  div.innerHTML = formatted;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

// ---- Typing indicator ----
function showTyping() {
  const container = document.getElementById('chatMessages');
  const id = 'typing_' + Date.now();
  const div = document.createElement('div');
  div.className = 'msg ai';
  div.id = id;
  div.innerHTML = `
    <div style="display:flex; gap:6px; align-items:center; opacity:0.6">
        <span style="font-size:0.7rem; font-weight:700">PROCESSING</span>
        <div style="display:flex;gap:3px">
            <span style="width:4px;height:4px;background:white;border-radius:50%;animation:pulse 1s infinite"></span>
            <span style="width:4px;height:4px;background:white;border-radius:50%;animation:pulse 1s infinite 0.2s"></span>
            <span style="width:4px;height:4px;background:white;border-radius:50%;animation:pulse 1s infinite 0.4s"></span>
        </div>
    </div>`;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return id;
}

function removeTyping(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

// ---- Quick prompts ----
function sendQuickPrompt(btn) {
  document.getElementById('chatInput').value = btn.textContent.trim();
  sendMessage();
}

// ---- Hỏi về sản phẩm cụ thể (click sidebar) ----
function askAboutProduct(productId, productName) {
  document.getElementById('chatInput').value =
    `Provide analysis for node "${productName}".`;
  sendMessage();
}

// ---- Enter để gửi ----
function handleKeyDown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 150) + 'px';
}

// ---- Reset Buffer ----
function clearChat() {
  document.getElementById('chatMessages').innerHTML = `
    <div class="msg ai">
      <div style="font-weight:700; margin-bottom: 8px; color: var(--primary-glow)">QUANTUM_SYS: BUFFER_RESET</div>
      Neural buffer cleared. System ready for new queries.
    </div>`;
}

// ---- Utils ----
function getUserId() {
  return parseInt(document.getElementById('chatUserId').value) || 1;
}

function escapeHtml(s) {
  return String(s).replace(/'/g, "\\'").replace(/"/g, '&quot;');
}
