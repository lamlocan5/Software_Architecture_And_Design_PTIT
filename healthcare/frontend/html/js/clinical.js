// ─── Appointments Page ─────────────────────────────────────
async function appointments() {
  try {
    const data = await ClinicalAPI.listAppointments();
    const list = data?.results ?? data ?? [];
    document.getElementById('content').innerHTML = `
      <div class="card">
        <div class="section-header">
          <div class="section-title">📅 Danh sách lịch hẹn</div>
          <button class="btn btn-primary" onclick="showCreateAppt()">＋ Tạo lịch hẹn</button>
        </div>
        ${list.length ? `
          <div class="table-wrap"><table>
            <thead><tr><th>#</th><th>Patient ID</th><th>Bác sĩ</th><th>Thời gian hẹn</th><th>Ghi chú</th><th>Trạng thái</th><th>Thao tác</th></tr></thead>
            <tbody>${list.map(a => `
              <tr>
                <td>${a.id}</td>
                <td>Patient #${a.patient_id}</td>
                <td><strong>${a.doctor_name}</strong></td>
                <td style="font-size:12px">${fmtDate(a.scheduled_at)}</td>
                <td style="max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${a.notes || '—'}</td>
                <td>${badge(a.status)}</td>
                <td>
                  <select class="form-control" style="width:130px;padding:4px 8px;font-size:12px" onchange="updateApptStatus(${a.id}, this.value)">
                    <option value="">-- Đổi TT --</option>
                    <option value="pending">Chờ</option>
                    <option value="confirmed">Xác nhận</option>
                    <option value="completed">Hoàn thành</option>
                    <option value="cancelled">Hủy</option>
                  </select>
                </td>
              </tr>`).join('')}
            </tbody>
          </table></div>` :
          `<div class="empty-state"><div class="empty-icon">📅</div><p>Chưa có lịch hẹn nào</p></div>`}
      </div>`;
  } catch (e) {
    document.getElementById('content').innerHTML =
      `<div class="empty-state"><div class="empty-icon">⚠️</div><p>${e.message}</p></div>`;
  }
}

async function showCreateAppt() {
  openModal('📅 Tạo lịch hẹn', `
    <form onsubmit="createAppt(event)">
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Patient ID *</label>
          <input id="a_pid" class="form-control" type="number" required placeholder="1" />
        </div>
        <div class="form-group">
          <label class="form-label">Bác sĩ *</label>
          <select id="a_doc_id" class="form-control" required>
            <option value="">Đang tải danh sách bác sĩ...</option>
          </select>
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">Thời gian hẹn *</label>
        <input id="a_time" class="form-control" type="datetime-local" required />
      </div>
      <div class="form-group">
        <label class="form-label">Ghi chú</label>
        <textarea id="a_note" class="form-control" rows="2" placeholder="Lý do khám..."></textarea>
      </div>
      <div class="form-actions">
        <button type="button" class="btn btn-ghost" onclick="closeModal()">Hủy</button>
        <button type="submit" class="btn btn-primary">💾 Lưu</button>
      </div>
    </form>`);

  try {
    const docs = await DoctorAPI.list();
    const list = docs?.results ?? docs ?? [];
    const select = document.getElementById('a_doc_id');
    if (!list.length) {
      select.innerHTML = '<option value="">Không có bác sĩ nào</option>';
    } else {
      select.innerHTML = '<option value="">-- Chọn bác sĩ --</option>' +
        list.map(d => `<option value="${d.id}">${d.full_name} (${d.specialty})</option>`).join('');
    }
  } catch (err) {
    document.getElementById('a_doc_id').innerHTML = '<option value="">Lỗi tải danh sách bác sĩ</option>';
  }
}

async function createAppt(e) {
  e.preventDefault();
  try {
    await ClinicalAPI.createAppointment({
      patient_id: parseInt(document.getElementById('a_pid').value),
      doctor_id: parseInt(document.getElementById('a_doc_id').value),
      scheduled_at: document.getElementById('a_time').value,
      notes: document.getElementById('a_note').value || null,
    });
    closeModal(); toast('Tạo lịch hẹn thành công!', 'success'); appointments();
  } catch (err) { toast('Lỗi: ' + err.message, 'error'); }
}

async function updateApptStatus(id, status) {
  if (!status) return;
  try {
    await ClinicalAPI.updateAppointment(id, { status });
    toast(`Đã cập nhật trạng thái → ${status}`, 'success'); appointments();
  } catch (e) { toast('Lỗi: ' + e.message, 'error'); }
}

// ─── Prescriptions Page ────────────────────────────────────
async function prescriptions() {
  try {
    const data = await ClinicalAPI.listPrescriptions();
    const list = data?.results ?? data ?? [];
    document.getElementById('content').innerHTML = `
      <div class="card">
        <div class="section-header">
          <div class="section-title">📋 Danh sách đơn thuốc</div>
          <button class="btn btn-primary" onclick="showCreatePrescription()">＋ Kê đơn thuốc</button>
        </div>
        ${list.length ? `
          <div class="table-wrap"><table>
            <thead><tr><th>#</th><th>Patient ID</th><th>Appointment</th><th>Chẩn đoán</th><th>Số thuốc</th><th>Tạo lúc</th><th>Thao tác</th></tr></thead>
            <tbody>${list.map(p => `
              <tr>
                <td>${p.id}</td>
                <td>Patient #${p.patient_id}</td>
                <td>Appt #${p.appointment}</td>
                <td style="max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${p.diagnosis}</td>
                <td><span class="badge badge-confirmed">${p.items?.length ?? 0} loại</span></td>
                <td style="font-size:12px">${fmtDate(p.created_at)}</td>
                <td><button class="btn btn-ghost btn-sm" onclick="viewPrescription(${p.id})">👁 Chi tiết</button></td>
              </tr>`).join('')}
            </tbody>
          </table></div>` :
          `<div class="empty-state"><div class="empty-icon">📋</div><p>Chưa có đơn thuốc nào</p></div>`}
      </div>`;
  } catch (e) {
    document.getElementById('content').innerHTML =
      `<div class="empty-state"><div class="empty-icon">⚠️</div><p>${e.message}</p></div>`;
  }
}

let medItemCount = 0;

function showCreatePrescription() {
  medItemCount = 1;
  openModal('📋 Kê đơn thuốc mới', `
    <form onsubmit="createPrescription(event)">
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Appointment ID *</label>
          <input id="rx_appt" class="form-control" type="number" required placeholder="1" />
        </div>
        <div class="form-group">
          <label class="form-label">Patient ID *</label>
          <input id="rx_pid" class="form-control" type="number" required placeholder="1" />
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">Chẩn đoán *</label>
        <textarea id="rx_diag" class="form-control" rows="2" required placeholder="Cảm cúm thông thường..."></textarea>
      </div>
      <div class="form-group">
        <label class="form-label">Thuốc kê đơn *</label>
        <div class="medicine-items" id="medItems">
          ${medItemRow(0)}
        </div>
        <button type="button" class="btn btn-ghost btn-sm" style="margin-top:8px" onclick="addMedItem()">＋ Thêm thuốc</button>
      </div>
      <p style="font-size:11px;color:var(--muted);margin-top:4px">⚡ Sau khi kê đơn, hệ thống sẽ tự động trừ kho và tạo hóa đơn</p>
      <div class="form-actions">
        <button type="button" class="btn btn-ghost" onclick="closeModal()">Hủy</button>
        <button type="submit" class="btn btn-primary">💊 Kê đơn</button>
      </div>
    </form>`);
}

function medItemRow(i) {
  return `<div class="medicine-item" id="med_${i}">
    <div class="form-group" style="margin:0">
      <input class="form-control" id="med_name_${i}" placeholder="Tên thuốc (vd: Paracetamol 500mg)" required />
    </div>
    <div class="form-group" style="margin:0">
      <input class="form-control" id="med_qty_${i}" type="number" min="1" placeholder="SL" required style="width:70px" />
    </div>
    <div class="form-group" style="margin:0">
      <input class="form-control" id="med_dos_${i}" placeholder="Liều dùng" style="width:130px" />
    </div>
    ${i > 0 ? `<button type="button" class="remove-item-btn" onclick="document.getElementById('med_${i}').remove()">✕</button>` : '<div></div>'}
  </div>`;
}

function addMedItem() {
  const container = document.getElementById('medItems');
  const div = document.createElement('div');
  div.innerHTML = medItemRow(++medItemCount);
  container.appendChild(div.firstElementChild);
}

async function createPrescription(e) {
  e.preventDefault();
  const items = [];
  document.querySelectorAll('[id^="med_name_"]').forEach(el => {
    const i = el.id.split('_')[2];
    if (el.value) items.push({
      medicine_name: el.value,
      quantity: parseInt(document.getElementById(`med_qty_${i}`).value),
      dosage: document.getElementById(`med_dos_${i}`).value || null,
    });
  });
  if (!items.length) { toast('Cần ít nhất 1 loại thuốc', 'error'); return; }
  try {
    await ClinicalAPI.createPrescription({
      appointment: parseInt(document.getElementById('rx_appt').value),
      patient_id: parseInt(document.getElementById('rx_pid').value),
      diagnosis: document.getElementById('rx_diag').value,
      items,
    });
    closeModal();
    toast('Kê đơn thành công! Kho đã trừ & hóa đơn đã tạo 🎉', 'success');
    prescriptions();
  } catch (err) { toast('Lỗi: ' + err.message, 'error'); }
}

async function viewPrescription(id) {
  try {
    const p = await ClinicalAPI.getPrescription(id);
    openModal(`📋 Đơn thuốc #${id}`, `
      <div class="detail-grid" style="margin-bottom:16px">
        <div class="detail-item"><label>Appointment</label><span>#${p.appointment}</span></div>
        <div class="detail-item"><label>Patient ID</label><span>#${p.patient_id}</span></div>
        <div class="detail-item"><label>Tạo lúc</label><span>${fmtDate(p.created_at)}</span></div>
      </div>
      <div class="form-group">
        <label class="form-label">Chẩn đoán</label>
        <p style="font-size:14px;color:var(--text)">${p.diagnosis}</p>
      </div>
      <label class="form-label">Danh sách thuốc</label>
      <div class="table-wrap"><table>
        <thead><tr><th>Tên thuốc</th><th>SL</th><th>Liều dùng</th></tr></thead>
        <tbody>${(p.items||[]).map(it => `
          <tr><td>${it.medicine_name}</td><td>${it.quantity}</td><td>${it.dosage||'—'}</td></tr>`).join('')}
        </tbody>
      </table></div>`);
  } catch (e) { toast('Lỗi: ' + e.message, 'error'); }
}
