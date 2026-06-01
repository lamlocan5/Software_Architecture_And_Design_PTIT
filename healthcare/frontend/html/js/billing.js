// ─── Bills Page ────────────────────────────────────────────
async function bills() {
  try {
    const data = await BillingAPI.list();
    const list = data?.results ?? data ?? [];
    const total = list.filter(b => b.status === 'paid').reduce((s, b) => s + Number(b.total_amount), 0);
    document.getElementById('content').innerHTML = `
      <div class="stats-grid" style="margin-bottom:16px">
        <div class="stat-card">
          <div class="stat-icon orange">🧾</div>
          <div><div class="stat-value">${list.length}</div><div class="stat-label">Tổng hóa đơn</div></div>
        </div>
        <div class="stat-card">
          <div class="stat-icon green">💰</div>
          <div><div class="stat-value" style="font-size:18px">${fmtMoney(total)}</div><div class="stat-label">Đã thu</div></div>
        </div>
        <div class="stat-card">
          <div class="stat-icon cyan">⏳</div>
          <div><div class="stat-value">${list.filter(b=>b.status!=='paid'&&b.status!=='cancelled').length}</div><div class="stat-label">Chờ thanh toán</div></div>
        </div>
      </div>
      <div class="card">
        <div class="section-header">
          <div class="section-title">🧾 Danh sách hóa đơn</div>
        </div>
        ${list.length ? `
          <div class="table-wrap"><table>
            <thead><tr><th>#</th><th>Patient</th><th>Prescription</th><th>Tổng tiền</th><th>Trạng thái</th><th>Tạo lúc</th><th>Thanh toán lúc</th><th>Thao tác</th></tr></thead>
            <tbody>${list.map(b => `
              <tr>
                <td>${b.id}</td>
                <td>Patient #${b.patient_id}</td>
                <td>${b.prescription_id ? `Rx #${b.prescription_id}` : '—'}</td>
                <td style="font-weight:600;color:${b.status==='paid'?'var(--success)':'var(--warning)'}">${fmtMoney(b.total_amount)}</td>
                <td>${badge(b.status)}</td>
                <td style="font-size:12px">${fmtDate(b.created_at)}</td>
                <td style="font-size:12px">${b.paid_at ? fmtDate(b.paid_at) : '—'}</td>
                <td style="display:flex;gap:4px">
                  <button class="btn btn-ghost btn-sm" onclick="viewBill(${b.id})">👁</button>
                  ${b.status !== 'paid' && b.status !== 'cancelled'
                    ? `<button class="btn btn-success btn-sm" onclick="payBill(${b.id})">💳 Thanh toán</button>`
                    : ''}
                </td>
              </tr>`).join('')}
            </tbody>
          </table></div>` :
          `<div class="empty-state"><div class="empty-icon">🧾</div><p>Chưa có hóa đơn</p></div>`}
      </div>`;
  } catch (e) {
    document.getElementById('content').innerHTML =
      `<div class="empty-state"><div class="empty-icon">⚠️</div><p>${e.message}</p></div>`;
  }
}

async function viewBill(id) {
  try {
    const b = await BillingAPI.get(id);
    openModal(`🧾 Hóa đơn #${id}`, `
      <div class="detail-grid" style="margin-bottom:16px">
        <div class="detail-item"><label>Patient ID</label><span>#${b.patient_id}</span></div>
        <div class="detail-item"><label>Prescription</label><span>${b.prescription_id ? '#'+b.prescription_id : '—'}</span></div>
        <div class="detail-item"><label>Trạng thái</label><span>${badge(b.status)}</span></div>
        <div class="detail-item"><label>Tổng tiền</label><span style="color:var(--warning);font-size:18px;font-weight:700">${fmtMoney(b.total_amount)}</span></div>
        <div class="detail-item"><label>Tạo lúc</label><span>${fmtDate(b.created_at)}</span></div>
        <div class="detail-item"><label>Thanh toán lúc</label><span>${b.paid_at ? fmtDate(b.paid_at) : '—'}</span></div>
      </div>
      <label class="form-label">Chi tiết hóa đơn</label>
      <div class="table-wrap"><table>
        <thead><tr><th>Mô tả</th><th>Đơn giá</th><th>SL</th><th>Thành tiền</th></tr></thead>
        <tbody>${(b.items||[]).map(it => `
          <tr>
            <td>${it.description}</td>
            <td>${fmtMoney(it.unit_price)}</td>
            <td>${it.quantity}</td>
            <td style="font-weight:600">${fmtMoney(it.unit_price * it.quantity)}</td>
          </tr>`).join('')}
          <tr style="background:rgba(99,102,241,0.1)">
            <td colspan="3" style="text-align:right;font-weight:600">Tổng cộng:</td>
            <td style="font-weight:700;color:var(--warning);font-size:15px">${fmtMoney(b.total_amount)}</td>
          </tr>
        </tbody>
      </table></div>
      ${b.status !== 'paid' && b.status !== 'cancelled'
        ? `<div class="form-actions"><button class="btn btn-success" onclick="payBill(${b.id})">💳 Thanh toán ngay</button></div>`
        : ''}`);
  } catch (e) { toast('Lỗi: ' + e.message, 'error'); }
}

async function payBill(id) {
  if (!confirm(`Xác nhận thanh toán hóa đơn #${id}?`)) return;
  try {
    await BillingAPI.pay(id);
    toast(`Hóa đơn #${id} đã thanh toán thành công! 🎉`, 'success');
    closeModal(); bills();
  } catch (e) { toast('Lỗi: ' + e.message, 'error'); }
}
