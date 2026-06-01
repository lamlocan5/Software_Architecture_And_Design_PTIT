
let staffToken = localStorage.getItem('staff_token');
let laptops = [], mobiles = [];

// ── Toast ─────────────────────────────────────────────────────────────────────
function toast(msg, type='ok') {
    const c = document.getElementById('toasts');
    const t = document.createElement('div');
    t.className = `toast ${type}`;
    t.innerHTML = `<span>${type==='ok'?'✅':'❌'}</span><span>${msg}</span>`;
    c.appendChild(t);
    setTimeout(() => t.remove(), 3500);
}

// ── Auth ──────────────────────────────────────────────────────────────────────
async function login() {
    const u = document.getElementById('loginUser').value;
    const p = document.getElementById('loginPass').value;
    if(!u||!p) { toast('Nhập đầy đủ thông tin','err'); return; }
    try {
        const res = await fetch(`${STAFF_API}/login/`, {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({username:u, password:p})
        });
        const d = await res.json();
        if(res.ok) {
            staffToken = d.token;
            localStorage.setItem('staff_token', staffToken);
            document.getElementById('sidebarUser').textContent = d.staff.username;
            showDashboard();
            toast(`Chào mừng ${d.staff.username}! 🎉`);
            loadAll();
        } else { toast(d.error||'Sai thông tin đăng nhập', 'err'); }
    } catch(e) { toast('Lỗi kết nối', 'err'); }
}

function logout() {
    staffToken = null; localStorage.removeItem('staff_token');
    document.getElementById('appShell').style.display = 'none';
    document.getElementById('loginScreen').style.display = 'flex';
}

function showDashboard() {
    document.getElementById('loginScreen').style.display = 'none';
    document.getElementById('appShell').style.display = 'flex';
}

// ── Navigation ────────────────────────────────────────────────────────────────
const pageTitles = { overview:'Tổng quan', add:'Thêm sản phẩm', laptop:'Kho Laptop', mobile:'Kho Mobile' };
function showPage(name) {
    ['overview','add','laptop','mobile'].forEach(p => {
        document.getElementById(`page-${p}`).classList.toggle('hidden', p!==name);
        document.getElementById(`nav-${p}`).classList.toggle('active', p===name);
    });
    document.getElementById('topbarTitle').textContent = pageTitles[name];
    if(name==='laptop') loadInventory('laptop');
    if(name==='mobile') loadInventory('mobile');
}

// ── Data Loading ──────────────────────────────────────────────────────────────
async function loadAll() {
    const [l, m] = await Promise.all([fetchItems('laptop'), fetchItems('mobile')]);
    laptops = l; mobiles = m;
    updateStats();
    renderOverview();
}

async function fetchItems(type) {
    try {
        const res = await fetch(`${STAFF_API}/items/${type}/`);
        return res.ok ? await res.json() : [];
    } catch(e) { return []; }
}

function updateStats() {
    document.getElementById('statLaptopCount').textContent = laptops.length;
    document.getElementById('statMobileCount').textContent = mobiles.length;
    const ts = [...laptops,...mobiles].reduce((a,i)=>a+(i.stock||0),0);
    document.getElementById('statTotalStock').textContent = ts;
    document.getElementById('statProducts').textContent = laptops.length + mobiles.length;
}

function renderOverview() {
    const all = [
        ...laptops.map(i=>({...i, _type:'laptop'})),
        ...mobiles.map(i=>({...i, _type:'mobile'}))
    ];
    const tbody = document.getElementById('overviewTbody');
    if(!all.length) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:32px;color:var(--text-muted)">Chưa có sản phẩm</td></tr>';
        return;
    }
    tbody.innerHTML = all.map(p=>`
        <tr>
            <td><strong>${p.name}</strong></td>
            <td><span class="badge ${p._type==='laptop'?'badge-l':'badge-m'}">${p._type==='laptop'?'💻 Laptop':'📱 Mobile'}</span></td>
            <td>${p.brand}</td>
            <td class="price-cell">$${parseFloat(p.price).toFixed(2)}</td>
            <td class="${p.stock>5?'stock-ok':'stock-low'}">${p.stock} cái</td>
            <td style="color:var(--text-muted);font-size:0.8rem">${p.cpu||'—'}</td>
        </tr>`).join('');
}

async function loadInventory(type) {
    const data = await fetchItems(type);
    const tbody = document.getElementById(`${type}Tbody`);
    if(!data.length) {
        tbody.innerHTML = '<tr class="empty-row"><td colspan="8">Chưa có sản phẩm nào</td></tr>';
        return;
    }
    tbody.innerHTML = data.map((p,i)=>`
        <tr>
            <td style="color:var(--text-muted)">${p.id}</td>
            <td><strong>${p.name}</strong></td>
            <td>${p.brand}</td>
            <td style="font-size:0.82rem;color:var(--text-sub)">${p.cpu||'—'}</td>
            <td>${p.ram||'—'}</td>
            <td>${type==='laptop'?(p.storage||'—'):(p.camera||'—')}</td>
            <td class="price-cell">$${parseFloat(p.price).toFixed(2)}</td>
            <td class="${p.stock>5?'stock-ok':'stock-low'}">${p.stock}</td>
        </tr>`).join('');
}

// ── Add Product ───────────────────────────────────────────────────────────────
function toggleMobile() {
    const isMobile = document.getElementById('prodType').value === 'mobile';
    ['camera','battery','os'].forEach(f => {
        document.getElementById(`${f}Grp`).classList.toggle('hidden', !isMobile);
    });
}

async function addProduct() {
    if(!staffToken) { toast('Phiên đã hết hạn, vui lòng đăng nhập lại','err'); logout(); return; }
    const type = document.getElementById('prodType').value;
    const payload = {
        token: staffToken, type,
        name: document.getElementById('prodName').value,
        brand: document.getElementById('prodBrand').value,
        price: document.getElementById('prodPrice').value,
        stock: document.getElementById('prodStock').value || 10,
        cpu: document.getElementById('prodCPU').value,
        ram: document.getElementById('prodRAM').value,
        storage: document.getElementById('prodStorage').value,
        display: document.getElementById('prodDisplay').value,
        description: document.getElementById('prodDesc').value,
    };
    if(!payload.name || !payload.price) { toast('Tên và giá sản phẩm là bắt buộc','err'); return; }
    if(type==='mobile') {
        payload.camera = document.getElementById('prodCamera').value;
        payload.battery = document.getElementById('prodBattery').value;
        payload.os = document.getElementById('prodOS').value;
    }
    try {
        const res = await fetch(`${STAFF_API}/items/add/`, {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify(payload)
        });
        if(res.ok) {
            toast(`✅ Đã thêm "${payload.name}" vào kho!`);
            ['prodName','prodBrand','prodPrice','prodCPU','prodRAM','prodStorage','prodDisplay','prodDesc'].forEach(id=>document.getElementById(id).value='');
            document.getElementById('prodStock').value = '10';
            loadAll();
        } else {
            const d = await res.json();
            toast(JSON.stringify(d).substring(0,80), 'err');
        }
    } catch(e) { toast('Lỗi server', 'err'); }
}

// ── Init ──────────────────────────────────────────────────────────────────────
if(staffToken) {
    showDashboard();
    loadAll();
}
