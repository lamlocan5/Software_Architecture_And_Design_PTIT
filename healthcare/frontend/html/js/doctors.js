// ─── Doctors Page ───────────────────────────────────────────
async function doctors() {
  try {
    const data = await DoctorAPI.list();
    const list = data?.results ?? data ?? [];
    document.getElementById('content').innerHTML = `
      <div class="card">
        <div class="section-header">
          <div class="section-title">🩺 Danh sách bác sĩ</div>
          <button class="btn btn-primary" onclick="showCreateDoctor()">＋ Thêm bác sĩ</button>
        </div>
        ${list.length ? `
          <div class="table-wrap"><table>
            <thead><tr><th>#</th><th>Họ tên</th><th>Chuyên khoa</th><th>SĐT</th><th>Email</th><th>Thao tác</th></tr></thead>
            <tbody>${list.map(d => `
              <tr>
                <td>${d.id}</td>
                <td><strong>${d.full_name}</strong></td>
                <td><span class="badge badge-draft">${d.specialty}</span></td>
                <td>${d.phone}</td>
                <td>${d.email || '—'}</td>
                <td>
                  <button class="btn btn-ghost btn-sm" onclick="viewDoctor(${d.id})">👁 Chi tiết</button>
                  <button class="btn btn-danger btn-sm" style="margin-left:4px" onclick="deleteDoctor(${d.id},'${d.full_name}')">🗑</button>
                </td>
              </tr>`).join('')}
            </tbody>
          </table></div>` :
          `<div class="empty-state"><div class="empty-icon">🩺</div><p>Chưa có bác sĩ nào</p></div>`}
      </div>`;
  } catch (e) {
    document.getElementById('content').innerHTML =
      `<div class="empty-state"><div class="empty-icon">⚠️</div><p>Lỗi: ${e.message}</p></div>`;
  }
}

function showCreateDoctor() {
  openModal('➕ Thêm bác sĩ mới', `
    <form onsubmit="createDoctor(event)">
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Họ tên *</label>
          <input id="d_name" class="form-control" required placeholder="BS. Nguyễn Văn A" />
        </div>
        <div class="form-group">
          <label class="form-label">Chuyên khoa *</label>
          <input id="d_spec" class="form-control" required placeholder="Tai Mũi Họng" />
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Số điện thoại *</label>
          <input id="d_phone" class="form-control" required placeholder="0911223344" />
        </div>
        <div class="form-group">
          <label class="form-label">Email</label>
          <input id="d_email" class="form-control" type="email" placeholder="email@example.com" />
        </div>
      </div>
      <div class="form-actions">
        <button type="button" class="btn btn-ghost" onclick="closeModal()">Hủy</button>
        <button type="submit" class="btn btn-primary">💾 Lưu</button>
      </div>
    </form>`);
}

async function createDoctor(e) {
  e.preventDefault();
  try {
    await DoctorAPI.create({
      full_name: document.getElementById('d_name').value,
      specialty: document.getElementById('d_spec').value,
      phone: document.getElementById('d_phone').value,
      email: document.getElementById('d_email').value || null,
    });
    closeModal(); toast('Tạo bác sĩ thành công!', 'success'); doctors();
  } catch (err) {
    toast('Lỗi: ' + err.message, 'error');
  }
}

async function viewDoctor(id) {
  try {
    const d = await DoctorAPI.get(id);
    openModal(`🩺 ${d.full_name}`, `
      <div class="detail-grid" style="margin-bottom:16px">
        <div class="detail-item"><label>Họ tên</label><span>${d.full_name}</span></div>
        <div class="detail-item"><label>Chuyên khoa</label><span>${d.specialty}</span></div>
        <div class="detail-item"><label>SĐT</label><span>${d.phone}</span></div>
        <div class="detail-item"><label>Email</label><span>${d.email || '—'}</span></div>
        <div class="detail-item"><label>Tạo lúc</label><span>${fmtDate(d.created_at)}</span></div>
      </div>
      <button class="btn btn-ghost" onclick="viewDoctorAppts(${id})">📅 Xem lịch hẹn</button>
      <div id="appt-sub-doc" style="margin-top:12px"></div>`);
  } catch (e) { toast('Lỗi: ' + e.message, 'error'); }
}

async function viewDoctorAppts(id) {
  const el = document.getElementById('appt-sub-doc');
  el.innerHTML = '<div class="spinner" style="margin:12px auto"></div>';
  try {
    const data = await DoctorAPI.appointments(id);
    const list = data?.results ?? data ?? [];
    el.innerHTML = list.length
      ? `<div class="table-wrap"><table><thead><tr><th>Patient ID</th><th>Thời gian</th><th>TT</th></tr></thead><tbody>${
          list.map(a => `<tr><td>Patient #${a.patient_id}</td><td>${fmtDate(a.scheduled_at)}</td><td>${badge(a.status)}</td></tr>`).join('')
        }</tbody></table></div>`
      : `<p style="color:var(--muted);font-size:13px">Chưa có lịch hẹn</p>`;
  } catch (e) { el.innerHTML = `<p style="color:var(--danger)">Không thể tải lịch hẹn</p>`; }
}

async function deleteDoctor(id, name) {
  if (!confirm(`Xóa bác sĩ "${name}"?`)) return;
  try {
    await DoctorAPI.delete(id);
    toast('Đã xóa bác sĩ', 'success'); doctors();
  } catch (e) { toast('Lỗi xóa: ' + e.message, 'error'); }
}
