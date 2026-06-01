// ─── Dashboard ─────────────────────────────────────────────
async function dashboard() {
  try {
    const [pts, appts, bills_data, meds] = await Promise.allSettled([
      PatientAPI.list(), ClinicalAPI.listAppointments(),
      BillingAPI.list(), InventoryAPI.listMedicines(),
    ]);

    const pc = pts.value?.count ?? pts.value?.results?.length ?? '—';
    const ac = appts.value?.count ?? appts.value?.results?.length ?? '—';
    const bc = bills_data.value?.count ?? bills_data.value?.results?.length ?? '—';
    const mc = meds.value?.count ?? meds.value?.results?.length ?? '—';

    const recentAppts = (appts.value?.results ?? appts.value ?? []).slice(0, 5);
    const pendingBills = (bills_data.value?.results ?? bills_data.value ?? []).filter(b => b.status !== 'paid').slice(0, 5);

    document.getElementById('content').innerHTML = `
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon blue">👥</div>
          <div><div class="stat-value">${pc}</div><div class="stat-label">Bệnh nhân</div></div>
        </div>
        <div class="stat-card">
          <div class="stat-icon cyan">📅</div>
          <div><div class="stat-value">${ac}</div><div class="stat-label">Lịch hẹn</div></div>
        </div>
        <div class="stat-card">
          <div class="stat-icon orange">🧾</div>
          <div><div class="stat-value">${bc}</div><div class="stat-label">Hóa đơn</div></div>
        </div>
        <div class="stat-card">
          <div class="stat-icon green">💊</div>
          <div><div class="stat-value">${mc}</div><div class="stat-label">Loại thuốc</div></div>
        </div>
      </div>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
        <div class="card">
          <div class="section-header">
            <div class="section-title">📅 Lịch hẹn gần đây</div>
            <a href="#appointments" class="btn btn-ghost btn-sm">Xem tất cả</a>
          </div>
          ${recentAppts.length ? `
            <div class="table-wrap"><table>
              <thead><tr><th>Bệnh nhân</th><th>Bác sĩ</th><th>Thời gian</th><th>Trạng thái</th></tr></thead>
              <tbody>${recentAppts.map(a => `
                <tr>
                  <td>Patient #${a.patient_id}</td>
                  <td>${a.doctor_name}</td>
                  <td style="font-size:12px">${fmtDate(a.scheduled_at)}</td>
                  <td>${badge(a.status)}</td>
                </tr>`).join('')}
              </tbody>
            </table></div>` :
            `<div class="empty-state"><div class="empty-icon">📅</div><p>Chưa có lịch hẹn</p></div>`}
        </div>

        <div class="card">
          <div class="section-header">
            <div class="section-title">🧾 Hóa đơn chưa thanh toán</div>
            <a href="#bills" class="btn btn-ghost btn-sm">Xem tất cả</a>
          </div>
          ${pendingBills.length ? `
            <div class="table-wrap"><table>
              <thead><tr><th>ID</th><th>Patient</th><th>Tổng tiền</th><th>TT</th></tr></thead>
              <tbody>${pendingBills.map(b => `
                <tr>
                  <td>#${b.id}</td>
                  <td>Patient #${b.patient_id}</td>
                  <td style="color:var(--warning);font-weight:600">${fmtMoney(b.total_amount)}</td>
                  <td>${badge(b.status)}</td>
                </tr>`).join('')}
              </tbody>
            </table></div>` :
            `<div class="empty-state"><div class="empty-icon">✅</div><p>Không có hóa đơn tồn đọng</p></div>`}
        </div>
      </div>`;
  } catch (e) {
    document.getElementById('content').innerHTML =
      `<div class="empty-state"><div class="empty-icon">⚠️</div><p>Không thể tải dashboard. Kiểm tra các services đã chạy chưa.</p></div>`;
  }
}
