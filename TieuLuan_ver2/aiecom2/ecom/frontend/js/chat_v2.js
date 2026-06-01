/* ============================================
   chat_v2.js - Cyberpunk Terminal Chat Logic
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
      <div class="product-sm-card" onclick="askAboutProduct(${p.id}, '${escapeHtml(p.name)}')">
        <img src="${p.image_url || `https://picsum.photos/seed/product${p.id}/80/80`}"
             alt="${p.name}"
             onerror="this.src='https://picsum.photos/seed/tech${p.id}/80/80'">
        <div class="product-sm-info">
          <h4>${p.name}</h4>
          <p>${p.category}</p>
        </div>
      </div>
    `).join('');
  } catch(e) {
    document.getElementById('sidebarProducts').innerHTML =
      '<p class="text-pink font-mono" style="font-size:0.75rem">SYSTEM_ERR: CANNOT_LOAD_NODES</p>';
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
  document.getElementById('sendBtn').style.opacity = '0.5';

  try {
    const res = await fetch(`${API_BASE}/chat/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, user_id: userId })
    });
    const data = await res.json();

    removeTyping(typingId);
    appendMessage('ai', data.answer || 'DATA_NOT_FOUND. NEURAL_LINK_UNSTABLE.');
  } catch(err) {
    removeTyping(typingId);
    appendMessage('ai', '[CRITICAL_ERROR]: CONNECTION_LOST_TO_ORACLE.');
  } finally {
    isWaiting = false;
    document.getElementById('sendBtn').disabled = false;
    document.getElementById('sendBtn').style.opacity = '1';
  }
}

// ---- Thêm tin nhắn vào chat ----
function appendMessage(role, text) {
  const container = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = `msg-line msg-${role}`;

  // Gắn SYSTEM MSG nếu là tin nhắn hệ thống đặc biệt
  if (role === 'ai' && text.includes('CRITICAL_ERROR')) {
    div.classList.add('sys-msg');
  }

  // Format text (tạo phong cách terminal xíu)
  const formatted = text
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong class="text-cyan">$1</strong>')
    .replace(/\*(.*?)\*/g, '<em class="text-pink">$1</em>')
    .replace(/`(.*?)`/g, '<code style="color:var(--bg-dark);background:var(--primary);padding:2px 4px;">$1</code>');

  div.innerHTML = formatted;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

// ---- Typing indicator ----
function showTyping() {
  const container = document.getElementById('chatMessages');
  const id = 'typing_' + Date.now();
  const div = document.createElement('div');
  div.className = 'msg-line msg-ai sys-msg';
  div.id = id;
  div.innerHTML = `[ AWAITING_RAG_RESPONSE_..._ ]`;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  
  // Animation chữ terminal vui vui
  let dots = 0;
  div.dataset.interval = setInterval(() => {
    dots = (dots + 1) % 4;
    document.getElementById(id).innerHTML = `[ AWAITING_RAG_RESPONSE_${'.'.repeat(dots)}${'_'.repeat(3-dots)} ]`;
  }, 300);

  return id;
}

function removeTyping(id) {
  const el = document.getElementById(id);
  if (el) {
    clearInterval(el.dataset.interval);
    el.remove();
  }
}

// ---- Quick prompts ----
function sendQuickPrompt(btn) {
  document.getElementById('chatInput').value = btn.textContent.trim().replace('[ ', '').replace(' ]', '');
  sendMessage();
}

// ---- Hỏi về sản phẩm cụ thể (click sidebar) ----
function askAboutProduct(productId, productName) {
  document.getElementById('chatInput').value = `ANALYZE_NODE::[${productName}]`;
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
    <div class="msg-line msg-ai">
      <span class="text-pink font-mono" style="font-weight:800; display:block; margin-bottom:8px;">[ SYS_RST ]</span>
      BUFFER_CLEARED_SUCCESSFULLY.
      <br>
      AWAITING_NEW_INSTRUCTIONS...
    </div>
  `;
}

// ---- Utils ----
function getUserId() {
  return parseInt(document.getElementById('globalUserId').value) || 1;
}

function escapeHtml(s) {
  return String(s).replace(/'/g, "\\'").replace(/"/g, '&quot;');
}
