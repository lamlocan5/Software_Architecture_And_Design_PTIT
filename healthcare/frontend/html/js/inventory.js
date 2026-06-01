// ─── Inventory Page ────────────────────────────────────────
async function inventory() {
  try {
    const data = await InventoryAPI.listMedicines();
    const list = data?.results ?? data ?? [];
    const lowStock = list.filter(m => m.stock < 50).length;
    document.getElementById('content').innerHTML = `
      <div class="stats-grid" style="margin-bottom:16px">
        <div class="stat-card">
          <div class="stat-icon green">💊</div>
          <div><div class="stat-value">${list.length}</div><div class="stat-label">Loại thuốc</div></div>
        </div>
        <div class="stat-card">
          <div class="stat-icon orange">⚠️</div>
          <div><div class="stat-value">${lowStock}</div><div class="stat-label">Sắp hết hàng</div></div>
        </div>
      </div>
      <div class="card">
        <div class="section-header">
          <div class="section-title">💊 Kho thuốc</div>
          <div style="display:flex;gap:8px">
            <button class="btn btn-ghost" onclick="viewTransactions()">📜 Lịch sử</button>
            <button class="btn btn-primary" onclick="showAddMedicine()">＋ Thêm thuốc</button>
          </div>
        </div>
        ${list.length ? `
          <div class="table-wrap"><table>
            <thead><tr><th>#</th><th>Tên thuốc</th><th>Đơn vị</th><th>Tồn kho</th><th>Đơn giá</th><th>Cập nhật</th><th>Thao tác</th></tr></thead>
            <tbody>${list.map(m => `
              <tr>
                <td>${m.id}</td>
                <td><strong>${m.name}</strong></td>
                <td>${m.unit}</td>
                <td>
                  <span style="font-weight:700;color:${m.stock < 50 ? 'var(--danger)' : m.stock < 100 ? 'var(--warning)' : 'var(--success)'}">${m.stock}</span>
                  ${m.stock < 50 ? '<span style="font-size:11px;color:var(--danger)"> ⚠️ Thấp</span>' : ''}
                </td>
                <td>${fmtMoney(m.unit_price)}</td>
                <td style="font-size:12px">${fmtDate(m.updated_at)}</td>
                <td style="display:flex;gap:4px">
                  <button class="btn btn-ghost btn-sm" onclick="showImport(${m.id},'${m.name}')">📥 Nhập</button>
                  <button class="btn btn-ghost btn-sm" onclick="showExport(${m.id},'${m.name}',${m.stock})">📤 Xuất</button>
                </td>
              </tr>`).join('')}
            </tbody>
          </table></div>` :
          `<div class="empty-state"><div class="empty-icon">💊</div><p>Kho trống</p></div>`}
      </div>`;
  } catch (e) {
    document.getElementById('content').innerHTML =
      `<div class="empty-state"><div class="empty-icon">⚠️</div><p>${e.message}</p></div>`;
  }
}

function showAddMedicine() {
  openModal('➕ Thêm thuốc mới', `
    <form onsubmit="addMedicine(event)">
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Tên thuốc *</label>
          <input id="m_name" class="form-control" required placeholder="Paracetamol 500mg" />
        </div>
        <div class="form-group">
          <label class="form-label">Đơn vị *</label>
          <select id="m_unit" class="form-control" required>
            <option value="viên">viên</option>
            <option value="chai">chai</option>
            <option value="ống">ống</option>
            <option value="gói">gói</option>
            <option value="hộp">hộp</option>
          </select>
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Tồn kho ban đầu</label>
          <input id="m_stock" class="form-control" type="number" min="0" value="0" />
        </div>
        <div class="form-group">
          <label class="form-label">Đơn giá (₫) *</label>
          <input id="m_price" class="form-control" type="number" min="0" step="500" required placeholder="5000" />
        </div>
      </div>
      <div class="form-actions">
        <button type="button" class="btn btn-ghost" onclick="closeModal()">Hủy</button>
        <button type="submit" class="btn btn-primary">💾 Lưu</button>
      </div>
    </form>`);
}

async function addMedicine(e) {
  e.preventDefault();
  try {
    await InventoryAPI.createMedicine({
      name: document.getElementById('m_name').value,
      unit: document.getElementById('m_unit').value,
      stock: parseInt(document.getElementById('m_stock').value) || 0,
      unit_price: document.getElementById('m_price').value,
    });
    closeModal(); toast('Thêm thuốc thành công!', 'success'); inventory();
  } catch (err) { toast('Lỗi: ' + err.message, 'error'); }
}

function showImport(id, name) {
  openModal(`📥 Nhập kho: ${name}`, `
    <form onsubmit="doStock(event,${id},'import')">
      <div class="form-group">
        <label class="form-label">Số lượng nhập *</label>
        <input id="s_qty" class="form-control" type="number" min="1" required placeholder="100" />
      </div>
      <div class="form-actions">
        <button type="button" class="btn btn-ghost" onclick="closeModal()">Hủy</button>
        <button type="submit" class="btn btn-success">📥 Nhập kho</button>
      </div>
    </form>`);
}

function showExport(id, name, stock) {
  openModal(`📤 Xuất kho: ${name} (Tồn: ${stock})`, `
    <form onsubmit="doStock(event,${id},'export')">
      <div class="form-group">
        <label class="form-label">Số lượng xuất * (tối đa ${stock})</label>
        <input id="s_qty" class="form-control" type="number" min="1" max="${stock}" required placeholder="10" />
      </div>
      <div class="form-group">
        <label class="form-label">Mã tham chiếu</label>
        <input id="s_ref" class="form-control" placeholder="Prescription ID..." />
      </div>
      <div class="form-actions">
        <button type="button" class="btn btn-ghost" onclick="closeModal()">Hủy</button>
        <button type="submit" class="btn btn-danger">📤 Xuất kho</button>
      </div>
    </form>`);
}

async function doStock(e, id, type) {
  e.preventDefault();
  try {
    await InventoryAPI.updateStock(id, {
      quantity: parseInt(document.getElementById('s_qty').value),
      transaction_type: type,
      reference_id: document.getElementById('s_ref')?.value || '',
    });
    closeModal();
    toast(`${type === 'import' ? 'Nhập' : 'Xuất'} kho thành công!`, 'success');
    inventory();
  } catch (err) { toast('Lỗi: ' + err.message, 'error'); }
}

async function viewTransactions() {
  openModal('📜 Lịch sử xuất nhập kho', `<div class="spinner" style="margin:20px auto"></div>`);
  try {
    const data = await InventoryAPI.listTransactions();
    const list = data?.results ?? data ?? [];
    document.getElementById('modalBody').innerHTML = list.length ? `
      <div class="table-wrap"><table>
        <thead><tr><th>Thuốc</th><th>Loại</th><th>SL</th><th>Tham chiếu</th><th>Thời gian</th></tr></thead>
        <tbody>${list.map(t => `
          <tr>
            <td>${t.medicine_name}</td>
            <td>${t.transaction_type === 'import'
              ? '<span class="badge badge-confirmed">📥 Nhập</span>'
              : '<span class="badge badge-cancelled">📤 Xuất</span>'}</td>
            <td>${t.quantity}</td>
            <td>${t.reference_id || '—'}</td>
            <td style="font-size:12px">${fmtDate(t.created_at)}</td>
          </tr>`).join('')}
        </tbody>
      </table></div>` :
      `<div class="empty-state"><div class="empty-icon">📜</div><p>Chưa có giao dịch nào</p></div>`;
  } catch (e) {
    document.getElementById('modalBody').innerHTML = `<p style="color:var(--danger)">${e.message}</p>`;
  }
}
