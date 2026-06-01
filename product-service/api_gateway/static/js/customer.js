
        const ORDER_API = '/api/order';
        const ADVISORY_API = '/api/advisory';
        let token = localStorage.getItem('customer_token');
        let username = localStorage.getItem('customer_username');
        let currentFilter = 'all';
        let allProducts = [];
        let currentDetailProduct = null;  // sản phẩm đang xem chi tiết
        let cartItemsForCheckout = [];    // giỏ hàng để checkout

        // ── Toasts ────────────────────────────────────────────────────────────────────
        function toast(msg, type = 'success') {
            const c = document.getElementById('toastContainer');
            const t = document.createElement('div');
            t.className = `toast ${type}`;
            t.innerHTML = `<span>${type === 'success' ? '✅' : '❌'}</span><span>${msg}</span>`;
            c.appendChild(t);
            setTimeout(() => {
                t.style.animation = 'fadeOut 0.3s ease forwards';
                setTimeout(() => t.remove(), 300);
            }, 3000);
        }

        // ── Nav ───────────────────────────────────────────────────────────────────────
        function updateNav() {
            const hasToken = !!token;
            document.getElementById('linkLogin').classList.toggle('hidden', hasToken);
            document.getElementById('linkCart').classList.toggle('hidden', !hasToken);
            document.getElementById('linkLogout').classList.toggle('hidden', !hasToken);
            document.getElementById('btnOrderHistory').classList.toggle('hidden', !hasToken);
            const chip = document.getElementById('userChip');
            if (hasToken) {
                chip.classList.remove('hidden');
                chip.textContent = `👤 ${username}`;
            } else {
                chip.classList.add('hidden');
            }
        }

        // ── Auth ──────────────────────────────────────────────────────────────────────
        function openAuth() { document.getElementById('authModal').classList.remove('hidden'); }
        function closeAuth() { document.getElementById('authModal').classList.add('hidden'); }
        function switchTab(tab) {
            document.getElementById('loginForm').classList.toggle('hidden', tab !== 'login');
            document.getElementById('registerForm').classList.toggle('hidden', tab !== 'register');
            document.getElementById('tabLogin').classList.toggle('active', tab === 'login');
            document.getElementById('tabRegister').classList.toggle('active', tab !== 'login');
            document.getElementById('authTitle').textContent = tab === 'login' ? 'Chào mừng trở lại' : 'Tạo tài khoản mới';
            document.getElementById('authSubtitle').textContent = tab === 'login'
                ? 'Đăng nhập để mua sắm và quản lý giỏ hàng'
                : 'Điền thông tin bên dưới để bắt đầu mua sắm';
        }

        async function login() {
            const u = document.getElementById('loginUsername').value;
            const p = document.getElementById('loginPassword').value;
            if (!u || !p) { toast('Vui lòng điền đầy đủ thông tin', 'error'); return; }
            try {
                const res = await fetch(`${CUSTOMER_API}/login/`, {
                    method: 'POST', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username: u, password: p })
                });
                const data = await res.json();
                if (res.ok) {
                    token = data.token; username = data.customer.username;
                    localStorage.setItem('customer_token', token);
                    localStorage.setItem('customer_username', username);
                    toast(`Chào mừng, ${username}! 🎉`);
                    updateNav(); closeAuth(); updateCartCount();
                } else { toast(data.error || 'Đăng nhập thất bại', 'error'); }
            } catch (e) { toast('Lỗi kết nối server', 'error'); }
        }

        async function register() {
            const payload = {
                username: document.getElementById('regUsername').value,
                email: document.getElementById('regEmail').value,
                password: document.getElementById('regPassword').value,
                full_name: document.getElementById('regFullName').value
            };
            if (!payload.username || !payload.email || !payload.password) { toast('Vui lòng điền đầy đủ thông tin bắt buộc', 'error'); return; }
            try {
                const res = await fetch(`${CUSTOMER_API}/register/`, {
                    method: 'POST', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (res.ok) {
                    toast('Đăng ký thành công! Đang đăng nhập...');
                    document.getElementById('loginUsername').value = payload.username;
                    document.getElementById('loginPassword').value = payload.password;
                    switchTab('login');
                    setTimeout(login, 500);
                } else { toast(JSON.stringify(data).substring(0, 80), 'error'); }
            } catch (e) { toast('Lỗi kết nối server', 'error'); }
        }

        function logout(showToast) {
            token = null; username = null;
            localStorage.removeItem('customer_token');
            localStorage.removeItem('customer_username');
            updateNav();
            document.getElementById('cartCount').textContent = '0';
            if (showToast !== false) toast('Đã đăng xuất');
        }

        // ── Products ──────────────────────────────────────────────────────────────────
        async function search() {
            const q = document.getElementById('searchInput').value;
            const grid = document.getElementById('productGrid');
            grid.innerHTML = '<div class="loading-state"><div class="loading-spinner"></div></div>';
            try {
                const res = await fetch(`${CUSTOMER_API}/search/?q=${encodeURIComponent(q)}`);
                const data = await res.json();
                allProducts = data.results || [];
                renderProducts(allProducts);
            } catch (e) {
                grid.innerHTML = '<div class="empty-state"><div class="icon">⚠️</div><p>Không thể tải sản phẩm</p></div>';
            }
        }

        function filterProducts(type) {
            currentFilter = type;
            ['all', 'laptop', 'mobile'].forEach(t => {
                document.getElementById('pill' + t.charAt(0).toUpperCase() + t.slice(1))?.classList.toggle('active', t === type);
            });
            const titles = { all: 'Tất cả sản phẩm', laptop: '💻 Laptop', mobile: '📱 Điện thoại' };
            document.getElementById('sectionTitle').textContent = titles[type];
            const filtered = type === 'all' ? allProducts : allProducts.filter(p => p.product_type === type);
            renderProducts(filtered);
        }

        const ICONS = { laptop: '💻', mobile: '📱' };

        function renderProducts(products) {
            const grid = document.getElementById('productGrid');
            document.getElementById('productCount').textContent = `${products.length} sản phẩm`;
            if (!products.length) {
                grid.innerHTML = '<div class="empty-state"><div class="icon">🔍</div><p>Không tìm thấy sản phẩm nào</p></div>';
                return;
            }
            grid.innerHTML = products.map(p => {
                const icon = ICONS[p.product_type] || '📦';
                const badge = p.product_type === 'laptop' ? 'badge-laptop' : 'badge-mobile';
                const typeName = p.product_type === 'laptop' ? '💻 Laptop' : '📱 Mobile';
                const specs = [p.cpu, p.ram, p.storage, p.display, p.camera].filter(Boolean);
                const price = parseFloat(p.price).toLocaleString('en-US', { style: 'currency', currency: 'USD' });
                const pData = encodeURIComponent(JSON.stringify(p));
                return `
        <div class="product-card">
            <div class="product-img" style="cursor:pointer" onclick="openDetail(${p.id},'${p.product_type}')">${icon}</div>
            <div class="product-body">
                <span class="product-type-badge ${badge}">${typeName}</span>
                <div class="product-name" style="cursor:pointer" onclick="openDetail(${p.id},'${p.product_type}')">${p.name}</div>
                <div class="product-brand">${p.brand}</div>
                <div class="product-specs">
                    ${specs.slice(0, 3).map(s => `<div class="spec-row"><div class="spec-dot"></div>${s}</div>`).join('')}
                </div>
                <div class="product-footer">
                    <span class="product-price">${price}</span>
                    <div style="display:flex;gap:6px;">
                        <button style="background:rgba(255,255,255,0.06);border:1px solid var(--border);color:var(--text-secondary);border-radius:8px;padding:8px 10px;cursor:pointer;font-size:0.78rem;transition:all 0.2s;" onclick="openDetail(${p.id},'${p.product_type}')" title="Xem chi tiết">🔍
                        </button>
                        <button class="add-cart-btn" id="btn-${p.product_type}-${p.id}"
                            onclick="addToCart(${p.id},'${p.product_type}','${p.brand} ${p.name}',${p.price},this)">
                            + Thêm
                        </button>
                    </div>
                </div>
            </div>
        </div>`;
            }).join('');
        }

        // ── Cart ──────────────────────────────────────────────────────────────────────
        async function addToCart(id, type, name, price, btn) {
            if (!token) { toast('Hãy đăng nhập để mua hàng', 'error'); openAuth(); return; }
            const orig = btn.innerHTML;
            btn.innerHTML = '✓ Đã thêm'; btn.classList.add('added'); btn.disabled = true;
            try {
                const res = await fetch(`${CUSTOMER_API}/cart/add/`, {
                    method: 'POST', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ token, product_id: id, product_type: type, product_name: name, price, quantity: 1 })
                });
                if (res.ok) {
                    toast(`${name} đã vào giỏ hàng 🛒`);
                    updateCartCount();
                } else {
                    if (res.status === 401) logout(false);
                    toast('Thêm vào giỏ thất bại', 'error');
                    btn.innerHTML = orig; btn.classList.remove('added'); btn.disabled = false;
                }
            } catch (e) {
                btn.innerHTML = orig; btn.classList.remove('added'); btn.disabled = false;
                toast('Lỗi kết nối', 'error');
            }
            setTimeout(() => { btn.innerHTML = '+ Thêm'; btn.classList.remove('added'); btn.disabled = false; }, 2000);
        }

        async function updateCartCount() {
            if (!token) return;
            try {
                const res = await fetch(`${CUSTOMER_API}/cart/?token=${encodeURIComponent(token)}`);
                if (res.ok) {
                    const data = await res.json();
                    const count = (data.items || []).reduce((a, c) => a + c.quantity, 0);
                    document.getElementById('cartCount').textContent = count;
                } else if (res.status === 401) logout(false);
            } catch (e) { }
        }

        async function openCart() {
            document.getElementById('cartDrawer').classList.add('open');
            document.getElementById('cartOverlay').classList.add('open');
            document.body.style.overflow = 'hidden';
            if (!token) { renderCartEmpty(); return; }
            document.getElementById('cartBody').innerHTML = '<div style="text-align:center;padding:40px"><div class="loading-spinner"></div></div>';
            try {
                const res = await fetch(`${CUSTOMER_API}/cart/?token=${encodeURIComponent(token)}`);
                if (res.ok) renderCartData(await res.json());
                else if (res.status === 401) logout(false);
            } catch (e) { }
        }

        function closeCart() {
            document.getElementById('cartDrawer').classList.remove('open');
            document.getElementById('cartOverlay').classList.remove('open');
            document.body.style.overflow = '';
        }

        function renderCartEmpty() {
            document.getElementById('cartBody').innerHTML = `
        <div class="cart-empty-state">
            <div class="icon">🛒</div>
            <p style="margin-bottom:8px; font-weight:600;">Giỏ hàng trống</p>
            <p style="font-size:0.85rem;">Hãy thêm sản phẩm vào giỏ hàng</p>
        </div>`;
            document.getElementById('cartFooter').style.display = 'none';
        }

        function renderCartData(cart) {
            const items = cart.items || [];
            if (!items.length) { renderCartEmpty(); return; }
            document.getElementById('cartFooter').style.display = 'block';
            document.getElementById('cartTotalPrice').textContent = `$${cart.total_price}`;
            document.getElementById('cartBody').innerHTML = items.map(item => `
        <div class="cart-item">
            <div class="cart-item-icon">${item.product_type === 'laptop' ? '💻' : '📱'}</div>
            <div class="cart-item-info">
                <div class="cart-item-name">${item.product_name}</div>
                <div class="cart-item-meta">${item.product_type} • Số lượng: ${item.quantity}</div>
            </div>
            <div style="display:flex;flex-direction:column;align-items:flex-end;gap:8px">
                <span class="cart-item-price">$${item.subtotal}</span>
                <button class="btn-remove-cart" onclick="removeItem(${item.id})">Xóa</button>
            </div>
        </div>`).join('');
        }

        async function removeItem(id) {
            try {
                const res = await fetch(`${CUSTOMER_API}/cart/remove/${id}/?token=${encodeURIComponent(token)}`, { method: 'DELETE' });
                if (res.ok) { toast('Đã xóa sản phẩm'); openCart(); updateCartCount(); }
            } catch (e) { }
        }

        async function clearCart() {
            if (!confirm('Xóa toàn bộ giỏ hàng?')) return;
            try {
                const res = await fetch(`${CUSTOMER_API}/cart/clear/?token=${encodeURIComponent(token)}`, { method: 'DELETE' });
                if (res.ok) { toast('Đã xóa giỏ hàng'); renderCartEmpty(); updateCartCount(); }
            } catch (e) { }
        }

        // ── Product Detail ────────────────────────────────────────────────────────────
        async function openDetail(productId, productType) {
            document.getElementById('detailModal').classList.remove('hidden');
            document.getElementById('detailSpecGrid').innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:20px;"><div class="loading-spinner"></div></div>';
            document.getElementById('detailName').textContent = '';
            document.getElementById('detailBrand').textContent = '';
            document.getElementById('detailPrice').textContent = '';
            document.getElementById('detailIcon').textContent = productType === 'laptop' ? '💻' : '📱';

            try {
                const apiBase = productType === 'laptop' ? '/api/laptop' : '/api/mobile';
                const endpoint = productType === 'laptop' ? `${apiBase}/${productId}/` : `${apiBase}/${productId}/`;
                const res = await fetch(endpoint);
                if (!res.ok) throw new Error('Not found');
                const p = await res.json();
                currentDetailProduct = { ...p, product_type: productType };
                showProductDetail(p, productType);
            } catch (e) {
                document.getElementById('detailSpecGrid').innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:20px;color:var(--error);">⚠️ Không thể tải chi tiết sản phẩm</div>`;
            }
        }

        function showProductDetail(p, productType) {
            const icon = productType === 'laptop' ? '💻' : '📱';
            const badge = productType === 'laptop' ? 'badge-laptop' : 'badge-mobile';
            const typeName = productType === 'laptop' ? '💻 Laptop' : '📱 Mobile';
            const price = parseFloat(p.price).toLocaleString('en-US', { style: 'currency', currency: 'USD' });

            document.getElementById('detailIcon').textContent = icon;
            document.getElementById('detailBadge').className = `product-type-badge ${badge}`;
            document.getElementById('detailBadge').textContent = typeName;
            document.getElementById('detailName').textContent = p.name;
            document.getElementById('detailBrand').textContent = `Thương hiệu: ${p.brand}`;
            document.getElementById('detailPrice').textContent = price;

            // Build spec chips
            const specFields = [];
            if (productType === 'laptop') {
                if (p.cpu) specFields.push({ label: 'CPU', value: p.cpu });
                if (p.ram) specFields.push({ label: 'RAM', value: p.ram });
                if (p.storage) specFields.push({ label: 'Ổ cứng', value: p.storage });
                if (p.display) specFields.push({ label: 'Màn hình', value: p.display });
                if (p.gpu) specFields.push({ label: 'GPU', value: p.gpu });
                if (p.battery) specFields.push({ label: 'Pin', value: p.battery });
                if (p.weight) specFields.push({ label: 'Trọng lượng', value: p.weight });
                if (p.os) specFields.push({ label: 'Hệ điều hành', value: p.os });
            } else {
                if (p.cpu) specFields.push({ label: 'Chip', value: p.cpu });
                if (p.ram) specFields.push({ label: 'RAM', value: p.ram });
                if (p.storage) specFields.push({ label: 'Bộ nhớ', value: p.storage });
                if (p.display) specFields.push({ label: 'Màn hình', value: p.display });
                if (p.camera) specFields.push({ label: 'Camera', value: p.camera });
                if (p.battery) specFields.push({ label: 'Pin', value: p.battery });
                if (p.os) specFields.push({ label: 'Hệ điều hành', value: p.os });
                if (p.sim) specFields.push({ label: 'SIM', value: p.sim });
            }

            if (specFields.length) {
                document.getElementById('detailSpecGrid').innerHTML = specFields.map(s => `
            <div class="spec-chip">
                <div class="spec-chip-label">${s.label}</div>
                <div class="spec-chip-value">${s.value}</div>
            </div>`).join('');
            } else {
                document.getElementById('detailSpecGrid').innerHTML = '<div style="grid-column:1/-1;color:var(--text-muted);">Không có thông số chi tiết</div>';
            }

            if (p.description) {
                document.getElementById('detailDescription').innerHTML = `<p style="margin-top:8px;">${p.description}</p>`;
            } else {
                document.getElementById('detailDescription').innerHTML = '';
            }
        }

        function closeDetail() {
            document.getElementById('detailModal').classList.add('hidden');
        }

        async function addToCartFromDetail() {
            if (!currentDetailProduct) return;
            const p = currentDetailProduct;
            const btn = document.getElementById('detailCartBtn');
            const orig = btn.innerHTML;
            btn.innerHTML = '✓ Đã thêm'; btn.disabled = true;
            await addToCart(p.id, p.product_type, `${p.brand} ${p.name}`, p.price, btn);
            setTimeout(() => { btn.innerHTML = orig; btn.disabled = false; }, 2000);
        }

        function orderFromDetail() {
            if (!currentDetailProduct) return;
            const p = currentDetailProduct;
            // Tạo đơn hàng trực tiếp từ product detail (không cần qua giỏ)
            cartItemsForCheckout = [{
                product_id: p.id,
                product_type: p.product_type,
                product_name: `${p.brand} ${p.name}`,
                price: p.price,
                quantity: 1
            }];
            closeDetail();
            prepareCheckoutModal();
        }

        // ── Checkout ──────────────────────────────────────────────────────────────────
        async function openCheckoutModal() {
            if (!token) { toast('Hãy đăng nhập để đặt hàng', 'error'); openAuth(); return; }
            // Lấy giỏ hàng hiện tại
            try {
                const res = await fetch(`${CUSTOMER_API}/cart/?token=${encodeURIComponent(token)}`);
                if (!res.ok) { toast('Không thể tải giỏ hàng', 'error'); return; }
                const cart = await res.json();
                const items = cart.items || [];
                if (!items.length) { toast('Giỏ hàng trống!', 'error'); return; }
                cartItemsForCheckout = items.map(item => ({
                    product_id: item.product_id,
                    product_type: item.product_type,
                    product_name: item.product_name,
                    price: parseFloat(item.price),
                    quantity: item.quantity
                }));
                closeCart();
                prepareCheckoutModal();
            } catch (e) { toast('Lỗi kết nối', 'error'); }
        }

        function prepareCheckoutModal() {
            const total = cartItemsForCheckout.reduce((sum, i) => sum + i.price * i.quantity, 0);
            document.getElementById('ckTotal').textContent = `$${total.toFixed(2)}`;
            document.getElementById('ckName').value = username || '';
            document.getElementById('ckEmail').value = '';
            document.getElementById('ckAddress').value = '';
            document.getElementById('ckNote').value = '';
            document.getElementById('checkoutModal').classList.remove('hidden');
        }

        function closeCheckout() {
            document.getElementById('checkoutModal').classList.add('hidden');
        }

        async function submitOrder() {
            if (!token) { toast('Hãy đăng nhập', 'error'); return; }
            const name = document.getElementById('ckName').value.trim();
            if (!name) { toast('Vui lòng nhập họ tên người nhận', 'error'); return; }

            const btn = document.getElementById('ckSubmitBtn');
            btn.textContent = '⏳ Đang xử lý...'; btn.disabled = true;

            const payload = {
                token,
                customer_name: name,
                customer_email: document.getElementById('ckEmail').value.trim(),
                shipping_address: document.getElementById('ckAddress').value.trim(),
                note: document.getElementById('ckNote').value.trim(),
                items: cartItemsForCheckout
            };

            try {
                const res = await fetch(`${ORDER_API}/create/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (res.ok) {
                    closeCheckout();
                    // Xóa giỏ hàng sau khi đặt hàng
                    await fetch(`${CUSTOMER_API}/cart/clear/?token=${encodeURIComponent(token)}`, { method: 'DELETE' });
                    updateCartCount();
                    // Hiện modal thành công chi tiết
                    showOrderSuccessModal(data.order);
                } else {
                    toast(data.error || 'Đặt hàng thất bại', 'error');
                }
            } catch (e) {
                toast('Lỗi kết nối đến order service', 'error');
            } finally {
                btn.textContent = '🎉 Xác nhận đặt hàng'; btn.disabled = false;
            }
        }

        function showOrderSuccessModal(order) {
            document.getElementById('successOrderId').textContent = `Mã đơn hàng: #${order.id} | Ngày: ${new Date(order.created_at).toLocaleString('vi-VN')}`;
            const items = order.items || [];
            const addr = order.shipping_address ? `Địa chỉ: ${order.shipping_address}` : '';
            const note = order.note ? `Ghi chú: ${order.note}` : '';
            const summaryRows = [
                ...items.map(i => `
            <div class="success-summary-row">
                <span class="success-summary-label">${i.product_type === 'laptop' ? '💻' : '📱'} ${i.product_name}</span>
                <span class="success-summary-value">x${i.quantity} &nbsp;&nbsp; $${parseFloat(i.price * i.quantity).toFixed(2)}</span>
            </div>`),
                `<div class="success-summary-row" style="border-top:1px solid rgba(255,255,255,0.1);margin-top:4px;padding-top:12px;">
            <span class="success-summary-label" style="font-weight:700;color:var(--text-secondary);">Tổng cộng</span>
            <span class="success-summary-value" style="font-size:1.1rem;color:var(--gold);">$${parseFloat(order.total_price).toFixed(2)}</span>
        </div>`,
                addr ? `<div class="success-summary-row"><span class="success-summary-label">${addr}</span></div>` : '',
                note ? `<div class="success-summary-row"><span class="success-summary-label">${note}</span></div>` : '',
            ].filter(Boolean);
            document.getElementById('successOrderSummary').innerHTML = summaryRows.join('');
            document.getElementById('orderSuccessModal').classList.remove('hidden');
        }

        function closeSuccessModal() {
            document.getElementById('orderSuccessModal').classList.add('hidden');
        }

        // ── Order History ─────────────────────────────────────────────────────────────
        async function openOrderHistory() {
            if (!token) { toast('Hãy đăng nhập', 'error'); return; }
            document.getElementById('orderHistoryModal').classList.remove('hidden');
            document.getElementById('orderHistoryBody').innerHTML = '<div style="text-align:center;padding:40px;"><div class="loading-spinner"></div></div>';

            try {
                const res = await fetch(`${ORDER_API}/?token=${encodeURIComponent(token)}`);
                if (!res.ok) throw new Error('Lỗi tải đơn hàng');
                const data = await res.json();
                renderOrderHistory(data.orders || []);
            } catch (e) {
                document.getElementById('orderHistoryBody').innerHTML = `<div style="text-align:center;padding:40px;color:var(--error);">⚠️ Không thể tải lịch sử đơn hàng</div>`;
            }
        }

        function closeOrderHistory() {
            document.getElementById('orderHistoryModal').classList.add('hidden');
        }

        const STATUS_LABELS = {
            pending: 'Chờ xác nhận', confirmed: 'Đã xác nhận',
            shipping: 'Đang giao', delivered: 'Đã giao', cancelled: 'Đã hủy'
        };

        function renderOrderHistory(orders) {
            const body = document.getElementById('orderHistoryBody');
            if (!orders.length) {
                body.innerHTML = `
            <div style="text-align:center;padding:60px;color:var(--text-muted);">
                <div style="font-size:3rem;margin-bottom:12px;">📦</div>
                <p style="font-weight:600;margin-bottom:6px;">Chưa có đơn hàng nào</p>
                <p style="font-size:0.85rem;">Hãy thêm sản phẩm vào giỏ và đặt hàng!</p>
            </div>`;
                return;
            }
            body.innerHTML = orders.map(o => {
                const statusCls = `status-${o.status}`;
                const statusLabel = STATUS_LABELS[o.status] || o.status;
                const date = new Date(o.created_at).toLocaleString('vi-VN');
                const itemsHTML = (o.items || []).map(i => `
            <div class="order-item-row">
                <span class="order-item-name">${i.product_type === 'laptop' ? '💻' : '📱'} ${i.product_name}</span>
                <span class="order-item-qty">x${i.quantity}</span>
                <span class="order-item-price">$${parseFloat(i.subtotal).toFixed(2)}</span>
            </div>`).join('');
                const addrHtml = o.shipping_address ? `<div style="color:var(--text-muted);font-size:0.8rem;margin-top:6px;">📍 ${o.shipping_address}</div>` : '';
                const noteHtml = o.note ? `<div style="color:var(--text-muted);font-size:0.8rem;margin-top:2px;">📝 ${o.note}</div>` : '';
                return `
            <div class="order-card">
                <div class="order-card-header">
                    <span class="order-id">🧻 Đơn #${o.id}</span>
                    <span class="order-status-badge ${statusCls}">${statusLabel}</span>
                </div>
                <div class="order-items-list">${itemsHTML}</div>
                ${addrHtml}${noteHtml}
                <div class="order-card-footer" style="margin-top:12px;padding-top:10px;border-top:1px solid rgba(255,255,255,0.05);">
                    <span class="order-total">Tổng: $${parseFloat(o.total_price).toFixed(2)}</span>
                    <span class="order-date">${date}</span>
                </div>
            </div>`;
            }).join('');
        }

        // ── Advisor RAG chat ─────────────────────────────────────────────────────────
        function toggleAdvisor() {
            const p = document.getElementById('advisorPanel');
            const open = !p.classList.contains('advisor-open');
            p.classList.toggle('advisor-open', open);
            p.setAttribute('aria-hidden', open ? 'false' : 'true');
            if (open) setTimeout(() => document.getElementById('advisorInput').focus(), 100);
        }
        function closeAdvisor() {
            const p = document.getElementById('advisorPanel');
            p.classList.remove('advisor-open');
            p.setAttribute('aria-hidden', 'true');
        }

        function appendAdvisorMsg(text, who, extraHtml) {
            const box = document.getElementById('advisorMessages');
            const d = document.createElement('div');
            d.className = 'advisor-msg ' + (who === 'user' ? 'user' : 'bot');
            d.textContent = text;
            if (who === 'bot' && extraHtml) {
                const s = document.createElement('div');
                s.className = 'src';
                s.innerHTML = extraHtml;
                d.appendChild(s);
            }
            box.appendChild(d);
            box.scrollTop = box.scrollHeight;
        }

        async function sendAdvisorMessage() {
            const input = document.getElementById('advisorInput');
            const btn = document.getElementById('advisorSendBtn');
            const msg = (input.value || '').trim();
            if (!msg) return;
            appendAdvisorMsg(msg, 'user');
            input.value = '';
            btn.disabled = true;
            try {
                const res = await fetch(`${ADVISORY_API}/chat`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: msg, token: token || null }),
                });
                let data = {};
                try { data = await res.json(); } catch (e) { /* ignore */ }
                if (!res.ok) {
                    const err = data.error || (typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail || ''));
                    appendAdvisorMsg(err || 'Lỗi tư vấn', 'bot');
                    return;
                }
                let extra = '';
                if (data.behavior_label) {
                    extra = 'Gợi ý nhóm hành vi: <strong>' + escapeHtml(data.behavior_label) + '</strong>';
                }
                if (data.sources && data.sources.length) {
                    const names = [...new Set(data.sources.map(function (s) { return s.source; }).filter(Boolean))];
                    if (names.length) extra += (extra ? '<br>' : '') + 'KB: ' + names.map(escapeHtml).join(', ');
                }
                appendAdvisorMsg(data.answer || '(Không có nội dung)', 'bot', extra);
            } catch (e) {
                appendAdvisorMsg('Không kết nối được dịch vụ tư vấn.', 'bot');
            } finally {
                btn.disabled = false;
            }
        }

        function escapeHtml(s) {
            if (!s) return '';
            const d = document.createElement('div');
            d.textContent = s;
            return d.innerHTML;
        }

        // ── Init ──────────────────────────────────────────────────────────────────────
        /** Tránh hiện "đã đăng nhập" khi token trong localStorage đã hết (sau restart container). */
        async function bootstrapCustomerSession() {
            if (token) {
                try {
                    const res = await fetch(`${CUSTOMER_API}/cart/?token=${encodeURIComponent(token)}`);
                    if (res.status === 401) {
                        token = null;
                        username = null;
                        localStorage.removeItem('customer_token');
                        localStorage.removeItem('customer_username');
                    }
                } catch (e) { /* ignore */ }
            }
            updateNav();
            await search();
            await updateCartCount();
        }
        bootstrapCustomerSession();
