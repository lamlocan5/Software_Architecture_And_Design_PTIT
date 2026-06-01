/* ============================================
   main.js - Products page logic (Quantum UI)
   ============================================ */

const API_BASE = 'http://127.0.0.1:8000/api';

// ---- State ----
let allProducts = [];
let currentCategory = '';

// ---- Khởi tạo ----
document.addEventListener('DOMContentLoaded', () => {
  loadProducts();
});

// ---- Load sản phẩm từ API ----
async function loadProducts() {
  try {
    const res = await fetch(`${API_BASE}/products/`);
    const data = await res.json();
    allProducts = data.products || [];
    renderProducts(allProducts);
    document.getElementById('productCount').textContent =
      `${allProducts.length} neural nodes indexed`;
  } catch (err) {
    console.error('[API] Lỗi load products:', err);
    document.getElementById('productsGrid').innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; padding: 4rem; color: var(--text-muted);">
        <div style="font-size: 3rem; margin-bottom: 1rem;">⚠️</div>
        <p>Quantum Link Failed.<br>Verify backend services are operational.</p>
        <button class="btn btn-glass" style="margin-top:1rem" onclick="loadProducts()">Retry Scan</button>
      </div>`;
  }
}

// ---- Render grid sản phẩm ----
function renderProducts(products) {
  const grid = document.getElementById('productsGrid');
  if (!products.length) {
    grid.innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; padding: 4rem; color: var(--text-muted);">
        <div style="font-size: 3rem; margin-bottom: 1rem;">🔍</div>
        <p>No neural patterns found matching your search.</p>
      </div>`;
    return;
  }

  grid.innerHTML = products.map(p => `
    <div class="quantum-card" onclick="showProductDetail(${p.id})">
      <div style="position: relative; overflow: hidden;">
        <img src="${p.image_url || `https://picsum.photos/seed/product${p.id}/400/300`}" 
             alt="${p.name}" 
             onerror="this.src='https://picsum.photos/seed/tech${p.id}/400/300'">
        <div style="position: absolute; top: 12px; right: 12px;" class="badge-ai">PRO</div>
      </div>
      <div class="card-body">
        <div class="card-category">${p.category}</div>
        <div class="card-name">${p.name}</div>
        <div class="card-bottom">
          <div class="card-price">${formatPrice(p.price)}</div>
          <button class="add-btn" onclick="event.stopPropagation(); addToCart(${p.id}, '${escapeHtml(p.name)}')">
            ＋
          </button>
        </div>
      </div>
    </div>
  `).join('');
}

// ---- Filter theo search ----
function filterProducts() {
  const keyword = document.getElementById('searchInput').value.toLowerCase();
  let filtered = allProducts;

  if (currentCategory) {
    filtered = filtered.filter(p => p.category === currentCategory);
  }

  if (keyword) {
    filtered = filtered.filter(p =>
      p.name.toLowerCase().includes(keyword) ||
      p.description.toLowerCase().includes(keyword)
    );
  }

  renderProducts(filtered);
  document.getElementById('productCount').textContent = `${filtered.length} patterns discovered`;
}

// ---- Filter theo category ----
function filterByCategory(category, btn) {
  currentCategory = category;
  document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
  btn.classList.add('active');
  filterProducts();
}

// ---- Gợi ý sản phẩm ----
async function openRecommendModal() {
  const userId = getUserId();
  document.getElementById('recommendUserId').textContent = `User ${userId}`;
  document.getElementById('recommendModal').classList.add('active');
  document.getElementById('recommendResults').innerHTML = '<div class="spinner-quantum"></div>';

  try {
    const res = await fetch(`${API_BASE}/recommend/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, top_n: 5 })
    });
    const data = await res.json();
    const products = data.recommendations || [];

    if (!products.length) {
      document.getElementById('recommendResults').innerHTML = 
        '<p style="color:var(--text-muted);text-align:center">No predictions available</p>';
      return;
    }

    renderRecommendations(products, userId);
  } catch (err) {
    document.getElementById('recommendResults').innerHTML = 
      `<div style="text-align:center; padding:2rem;"><p>API Link Failure</p></div>`;
  }
}

function renderRecommendations(products, userId) {
    document.getElementById('recommendResults').innerHTML = `
      <div style="display:grid; gap:1rem">
        ${products.map((p, i) => `
          <div style="display:flex; gap:16px; align-items:center; padding:16px; background:rgba(255,255,255,0.03); border-radius:18px; border:1px solid var(--border)">
            <div style="width:40px; height:40px; background:linear-gradient(135deg,var(--primary),var(--accent)); border-radius:12px; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:0.9rem; color:white; flex-shrink:0; box-shadow:0 0 10px var(--primary)">#${i+1}</div>
            <img src="${p.image_url || `https://picsum.photos/seed/product${p.id}/80/80`}" 
                 style="width:52px; height:52px; object-fit:cover; border-radius:12px; flex-shrink:0"
                 onerror="this.src='https://picsum.photos/seed/tech${p.id}/80/80'">
            <div style="flex:1; min-width:0">
              <div style="font-weight:700; font-size:1rem; color:#fff">${p.name}</div>
              <div style="font-size:0.8rem; color:var(--text-muted)">${p.category}</div>
            </div>
            <div style="font-weight:800; color:var(--primary-glow); white-space:nowrap">${formatPrice(p.price)}</div>
          </div>
        `).join('')}
      </div>`;
}

// ---- Xem chi tiết sản phẩm ----
async function showProductDetail(productId) {
  const product = allProducts.find(p => p.id === productId);
  if (!product) return;

  document.getElementById('productModalTitle').textContent = "Neural Scan: " + product.name;
  document.getElementById('productModal').classList.add('active');

  recordBehavior(getUserId(), productId, 'click');

  document.getElementById('productModalBody').innerHTML = `
    <div style="display:flex; gap:2rem; flex-wrap:wrap">
      <div style="flex: 1; min-width: 280px;">
        <img src="${product.image_url || `https://picsum.photos/seed/product${productId}/400/300`}" 
             style="width:100%; height:300px; object-fit:cover; border-radius:24px; border:1px solid var(--border)"
             onerror="this.src='https://picsum.photos/seed/tech${productId}/400/300'">
      </div>
      <div style="flex:1.2; min-width:280px">
        <div class="badge-ai" style="margin-bottom: 12px; display: inline-block">${product.category}</div>
        <div style="font-size:1.8rem; font-weight:700; margin-bottom:12px; line-height:1.2; color:#fff">${product.name}</div>
        <div style="font-size:2rem; font-weight:800; color:var(--primary-glow); margin-bottom:20px">${formatPrice(product.price)}</div>
        <div style="font-size:1rem; color:var(--text-muted); line-height:1.7; margin-bottom:24px">${product.description}</div>
        <div style="display:flex; gap:12px">
          <button class="btn btn-primary" onclick="addToCart(${product.id},'${escapeHtml(product.name)}')">🛒 Add to Cart</button>
          <button class="btn btn-glass" onclick="showSimilar(${product.id});closeModal('productModal')">🔗 Similars</button>
        </div>
      </div>
    </div>
    <div style="margin-top:2.5rem" id="similarSection">
      <div class="spinner-quantum"></div>
    </div>`;

  loadSimilarInModal(productId);
}

async function loadSimilarInModal(productId) {
  try {
    const res = await fetch(`${API_BASE}/recommend/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: getUserId(), product_id: productId, top_n: 3 })
    });
    const data = await res.json();
    const products = data.recommendations || [];

    document.getElementById('similarSection').innerHTML = products.length ? `
      <div style="font-weight:700; margin-bottom:15px; font-size:1.1rem; color:#fff">🔗 Relevant Neural Nodes</div>
      <div style="display:flex; gap:15px; flex-wrap:wrap">
        ${products.map(p => `
          <div style="flex:1; min-width:180px; padding:18px; background:rgba(255,255,255,0.02); border:1px solid var(--border); border-radius:18px; cursor:pointer; transition:var(--transition)"
               onmouseover="this.style.borderColor='var(--primary)'" onmouseout="this.style.borderColor='var(--border)'"
               onclick="showProductDetail(${p.id})">
            <div style="font-size:0.95rem; font-weight:700; color:#fff; margin-bottom:8px">${p.name}</div>
            <div style="font-size:1rem; color:var(--primary-glow); font-weight:800">${formatPrice(p.price)}</div>
          </div>`).join('')}
      </div>` : '';
  } catch(e) {
    document.getElementById('similarSection').innerHTML = '';
  }
}

// ---- Xem sản phẩm tương tự (mở modal gợi ý) ----
async function showSimilar(productId) {
  const userId = getUserId();
  document.getElementById('recommendUserId').textContent = `Node Reference #${productId}`;
  document.getElementById('recommendModal').classList.add('active');
  document.getElementById('recommendResults').innerHTML = '<div class="spinner-quantum"></div>';

  try {
    const res = await fetch(`${API_BASE}/recommend/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, product_id: productId, top_n: 5 })
    });
    const data = await res.json();
    renderRecommendations(data.recommendations || [], userId);
  } catch(e) {
    document.getElementById('recommendResults').innerHTML = '<p>Search Failure</p>';
  }
}

// ---- Add to cart (ghi hành vi) ----
async function addToCart(productId, productName) {
  await recordBehavior(getUserId(), productId, 'add_to_cart');
  showToast(`Added "${productName}" to neural cart!`, 'success');
}

// ---- Ghi hành vi ----
async function recordBehavior(userId, productId, action) {
  try {
    await fetch(`${API_BASE}/behavior/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, product_id: productId, action })
    });
  } catch(e) {}
}

// ---- Utils ----
function getUserId() {
  return parseInt(document.getElementById('globalUserId').value) || 1;
}

function formatPrice(price) {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(price);
}

function escapeHtml(s) {
  return String(s).replace(/'/g, "\\'").replace(/"/g, '&quot;');
}

function closeModal(id) {
  document.getElementById(id).classList.remove('active');
}

function showToast(msg, type = '') {
  const tc = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `quantum-toast`;
  toast.innerHTML = `<div style="display:flex; align-items:center; gap:12px"><span>⚡</span> ${msg}</div>`;
  tc.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(20px)';
    setTimeout(() => toast.remove(), 500);
  }, 3500);
}

// Đóng modal khi click ngoài
document.querySelectorAll('.modal-backdrop').forEach(overlay => {
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) overlay.classList.remove('active');
  });
});
