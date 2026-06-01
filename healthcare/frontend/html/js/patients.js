// ─── Patients Page ─────────────────────────────────────────
async function patients() {
  try {
    const data = await PatientAPI.list();
    const list = data?.results ?? data ?? [];
    document.getElementById('content').innerHTML = `
      <div class="card">
        <div class="section-header">
          <div class="section-title">👥 Danh sách bệnh nhân</div>
          <button class="btn btn-primary" onclick="showCreatePatient()">＋ Thêm bệnh nhân</button>
        </div>
        ${list.length ? `
          <div class="table-wrap"><table>
            <thead><tr><th>#</th><th>Họ tên</th><th>Ngày sinh</th><th>Giới tính</th><th>SĐT</th><th>Email</th><th>Thao tác</th></tr></thead>
            <tbody>${list.map(p => `
              <tr>
                <td>${p.id}</td>
                <td><strong>${p.full_name}</strong></td>
                <td>${p.date_of_birth}</td>
                <td>${p.gender === 'male' ? '♂ Nam' : p.gender === 'female' ? '♀ Nữ' : '⚧ Khác'}</td>
                <td>${p.phone}</td>
                <td>${p.email || '—'}</td>
                <td>
                  <button class="btn btn-ghost btn-sm" onclick="viewPatient(${p.id})">👁 Chi tiết</button>
                  <button class="btn btn-danger btn-sm" style="margin-left:4px" onclick="deletePatient(${p.id},'${p.full_name}')">🗑</button>
                </td>
              </tr>`).join('')}
            </tbody>
          </table></div>` :
          `<div class="empty-state"><div class="empty-icon">👥</div><p>Chưa có bệnh nhân nào</p></div>`}
      </div>`;
  } catch (e) {
    document.getElementById('content').innerHTML =
      `<div class="empty-state"><div class="empty-icon">⚠️</div><p>Lỗi: ${e.message}</p></div>`;
  }
}

function showCreatePatient() {
  openModal('➕ Thêm bệnh nhân mới', `
    <form onsubmit="createPatient(event)">
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Họ tên *</label>
          <input id="p_name" class="form-control" required placeholder="Nguyễn Văn A" />
        </div>
        <div class="form-group">
          <label class="form-label">Ngày sinh *</label>
          <input id="p_dob" class="form-control" type="date" required />
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Giới tính *</label>
          <select id="p_gender" class="form-control" required>
            <option value="male">Nam</option><option value="female">Nữ</option><option value="other">Khác</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Số điện thoại *</label>
          <input id="p_phone" class="form-control" required placeholder="0901234567" />
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Email</label>
          <input id="p_email" class="form-control" type="email" placeholder="email@example.com" />
        </div>
        <div class="form-group">
          <label class="form-label">Địa chỉ</label>
          <input id="p_addr" class="form-control" placeholder="Địa chỉ..." />
        </div>
      </div>
      <div class="form-actions">
        <button type="button" class="btn btn-ghost" onclick="closeModal()">Hủy</button>
        <button type="submit" class="btn btn-primary">💾 Lưu</button>
      </div>
    </form>`);
}

async function createPatient(e) {
  e.preventDefault();
  try {
    await PatientAPI.create({
      full_name: document.getElementById('p_name').value,
      date_of_birth: document.getElementById('p_dob').value,
      gender: document.getElementById('p_gender').value,
      phone: document.getElementById('p_phone').value,
      email: document.getElementById('p_email').value || null,
      address: document.getElementById('p_addr').value || null,
    });
    closeModal(); toast('Tạo bệnh nhân thành công!', 'success'); patients();
  } catch (err) {
    toast('Lỗi: ' + err.message, 'error');
  }
}

async function viewPatient(id) {
  try {
    const p = await PatientAPI.get(id);
    openModal(`👤 ${p.full_name}`, `
      <div class="detail-grid" style="margin-bottom:16px">
        <div class="detail-item"><label>Họ tên</label><span>${p.full_name}</span></div>
        <div class="detail-item"><label>Ngày sinh</label><span>${p.date_of_birth}</span></div>
        <div class="detail-item"><label>Giới tính</label><span>${p.gender}</span></div>
        <div class="detail-item"><label>SĐT</label><span>${p.phone}</span></div>
        <div class="detail-item"><label>Email</label><span>${p.email || '—'}</span></div>
        <div class="detail-item"><label>Địa chỉ</label><span>${p.address || '—'}</span></div>
        <div class="detail-item"><label>Tạo lúc</label><span>${fmtDate(p.created_at)}</span></div>
      </div>
      <button class="btn btn-ghost" onclick="viewPatientAppts(${id})">📅 Xem lịch hẹn</button>
      <div id="appt-sub" style="margin-top:12px"></div>`);
  } catch (e) { toast('Lỗi: ' + e.message, 'error'); }
}

async function viewPatientAppts(id) {
  const el = document.getElementById('appt-sub');
  el.innerHTML = '<div class="spinner" style="margin:12px auto"></div>';
  try {
    const data = await PatientAPI.appointments(id);
    const list = data?.results ?? data ?? [];
    el.innerHTML = list.length
      ? `<div class="table-wrap"><table><thead><tr><th>Bác sĩ</th><th>Thời gian</th><th>TT</th></tr></thead><tbody>${
          list.map(a => `<tr><td>${a.doctor_name}</td><td>${fmtDate(a.scheduled_at)}</td><td>${badge(a.status)}</td></tr>`).join('')
        }</tbody></table></div>`
      : `<p style="color:var(--muted);font-size:13px">Chưa có lịch hẹn</p>`;
  } catch (e) { el.innerHTML = `<p style="color:var(--danger)">Không thể tải lịch hẹn</p>`; }
}

async function deletePatient(id, name) {
  if (!confirm(`Xóa bệnh nhân "${name}"?`)) return;
  try {
    await PatientAPI.delete(id);
    toast('Đã xóa bệnh nhân', 'success'); patients();
  } catch (e) { toast('Lỗi xóa: ' + e.message, 'error'); }
}
