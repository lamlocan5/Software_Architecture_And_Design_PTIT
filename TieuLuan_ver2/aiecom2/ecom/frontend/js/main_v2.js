/* ============================================
   main_v2.js - Cyberpunk Neon Logic
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
  const grid = document.getElementById('productsGrid');
  grid.innerHTML = '<div class="spinner"></div>';

  try {
    const res = await fetch(`${API_BASE}/products/`);
    const data = await res.json();
    allProducts = data.products || [];
    renderProducts(allProducts);
    
    const countEl = document.getElementById('productCount');
    if (countEl) countEl.textContent = `[ ${allProducts.length} SYSTEM_NODES_LOADED ]`;
  } catch (err) {
    console.error('[CYBER_LINK] Error:', err);
    grid.innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; padding: 4rem;">
        <div style="font-size: 4rem; color: var(--secondary); margin-bottom: 1rem;">ERR_LINK_FAILED</div>
        <p class="text-pink font-mono">CONNECTION TO NEURAL BACKEND LOST.</p>
        <button class="cyber-btn" style="margin-top:2rem" onclick="loadProducts()">RE-INITIALIZE</button>
      </div>`;
  }
}

// ---- Render grid sản phẩm ----
function renderProducts(products) {
  const grid = document.getElementById('productsGrid');
  if (!products.length) {
    grid.innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; padding: 4rem;">
        <p class="text-muted font-mono">NO RESULTS IN CURRENT SUBNET.</p>
      </div>`;
    return;
  }

  grid.innerHTML = products.map(p => `
    <div class="cyber-card" onclick="showProductDetail(${p.id})">
      <div class="card-img-wrapper">
        <img src="${p.image_url || `https://picsum.photos/seed/product${p.id}/400/300`}" 
             alt="${p.name}" 
             onerror="this.src='https://picsum.photos/seed/tech${p.id}/400/300'">
        <div class="card-badge">SECURED</div>
      </div>
      <div class="card-content">
        <div class="card-category">${p.category}</div>
        <div class="card-title">${p.name}</div>
        <div class="card-footer">
          <div class="card-price">${formatPrice(p.price)}</div>
          <button class="card-action" onclick="event.stopPropagation(); addToCart(${p.id}, '${escapeHtml(p.name)}')">
            +
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
  const countEl = document.getElementById('productCount');
  if (countEl) countEl.textContent = `[ ${filtered.length} NODES_FILTERED ]`;
}

// ---- Filter theo category ----
function filterByCategory(category, btn) {
  currentCategory = category;
  document.querySelectorAll('.cyber-btn').forEach(c => c.classList.remove('active'));
  btn.classList.add('active');
  filterProducts();
}

// ---- Gợi ý sản phẩm ----
async function openRecommendModal() {
  const userId = getUserId();
  const modal = document.getElementById('recommendModal');
  const results = document.getElementById('recommendResults');
  
  document.getElementById('recommendUserId').textContent = `USER_ID::${userId.toString().padStart(3, '0')}`;
  modal.classList.add('active');
  results.innerHTML = '<div class="spinner"></div>';

  try {
    const res = await fetch(`${API_BASE}/recommend/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, top_n: 5 })
    });
    const data = await res.json();
    const products = data.recommendations || [];

    if (!products.length) {
      results.innerHTML = '<p class="text-muted font-mono">NULL_PREDICTIONS_RETURNED</p>';
      return;
    }

    renderRecommendations(products);
  } catch (err) {
    results.innerHTML = '<p class="text-pink font-mono">API_TIMEOUT_ERR</p>';
  }
}

function renderRecommendations(products) {
    document.getElementById('recommendResults').innerHTML = `
      <div style="display:grid; gap:1rem">
        ${products.map((p, i) => `
          <div style="display:flex; gap:16px; align-items:center; padding:16px; background:rgba(255,255,255,0.02); border:1px solid var(--border); position:relative; overflow:hidden">
            <div style="width:40px; height:40px; border:1px solid var(--primary); display:flex; align-items:center; justify-content:center; font-family:var(--font-mono); font-weight:800; color:var(--primary); box-shadow: 0 0 5px var(--primary)">${i+1}</div>
            <img src="${p.image_url || `https://picsum.photos/seed/product${p.id}/80/80`}" 
                 style="width:50px; height:50px; object-fit:cover; border:1px solid var(--border)"
                 onerror="this.src='https://picsum.photos/seed/tech${p.id}/80/80'">
            <div style="flex:1">
              <div style="font-weight:700; color:var(--primary)">${p.name}</div>
              <div style="font-size:0.8rem; color:var(--text-muted); font-family:var(--font-mono)">${p.category}</div>
            </div>
            <div style="font-family:var(--font-mono); color:var(--accent)">${formatPrice(p.price)}</div>
          </div>
        `).join('')}
      </div>`;
}

// ---- Xem chi tiết sản phẩm ----
async function showProductDetail(productId) {
  const product = allProducts.find(p => p.id === productId);
  if (!product) return;

  const modal = document.getElementById('productModal');
  const body = document.getElementById('productModalBody');
  
  modal.classList.add('active');
  recordBehavior(getUserId(), productId, 'click');

  body.innerHTML = `
    <div style="display:flex; gap:2rem; flex-wrap:wrap">
      <div style="flex: 1; min-width: 250px;">
        <img src="${product.image_url || `https://picsum.photos/seed/product${productId}/400/300`}" 
             style="width:100%; border:1px solid var(--primary); box-shadow: 0 0 15px rgba(0,243,255,0.2)"
             onerror="this.src='https://picsum.photos/seed/tech${productId}/400/300'">
      </div>
      <div style="flex:1.2; min-width:250px">
        <div class="card-category" style="margin-bottom: 10px">${product.category}</div>
        <div style="font-size:2rem; font-weight:900; margin-bottom:10px; color:#fff; text-transform:uppercase">${product.name}</div>
        <div style="font-size:1.8rem; font-family:var(--font-mono); color:var(--accent); margin-bottom:20px">${formatPrice(product.price)}</div>
        <div style="color: var(--text-muted); margin-bottom:30px; border-left: 2px solid var(--primary); padding-left: 15px">${product.description}</div>
        <div style="display:flex; gap:15px">
          <button class="cyber-btn" onclick="addToCart(${product.id},'${escapeHtml(product.name)}')">BUY_EXECUTE</button>
          <button class="cyber-btn btn-secondary" onclick="closeModal('productModal');openRecommendModal()">SIMILAR_NODES</button>
        </div>
      </div>
    </div>
    <div style="margin-top:2.5rem" id="similarSection"></div>`;
}

// ---- Add to cart ----
async function addToCart(productId, productName) {
  await recordBehavior(getUserId(), productId, 'add_to_cart');
  showToast(`[OBJECT_LOGGED]: ${productName}`);
}

async function recordBehavior(userId, productId, action) {
  try {
    await fetch(`${API_BASE}/behavior/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, product_id: productId, action })
    });
  } catch(e) {}
}

const getUserId = () => parseInt(document.getElementById('globalUserId').value) || 1;

const formatPrice = (price) => new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(price);

const escapeHtml = (s) => String(s).replace(/'/g, "\\'").replace(/"/g, '&quot;');

const closeModal = (id) => document.getElementById(id).classList.remove('active');

function showToast(msg) {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = 'cyber-toast';
  toast.innerHTML = `<span class="text-cyan">>></span> <span>${msg}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 500);
  }, 3000);
}

// Close modal on click outside
document.querySelectorAll('.modal-overlay').forEach(overlay => {
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) overlay.classList.remove('active');
  });
});
