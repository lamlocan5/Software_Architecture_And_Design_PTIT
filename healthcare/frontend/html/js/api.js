// ─── Generic fetch wrapper ─────────────────────────────────
async function apiFetch(url, options = {}) {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(JSON.stringify(err));
  }
  // 204 No Content
  if (res.status === 204) return null;
  return res.json();
}

// ─── Patient Service ───────────────────────────────────────
const PatientAPI = {
  list:   ()       => apiFetch(`${API.patient}/patients/`),
  get:    (id)     => apiFetch(`${API.patient}/patients/${id}/`),
  create: (data)   => apiFetch(`${API.patient}/patients/`,   { method: 'POST',   body: JSON.stringify(data) }),
  update: (id, d)  => apiFetch(`${API.patient}/patients/${id}/`, { method: 'PUT', body: JSON.stringify(d) }),
  delete: (id)     => apiFetch(`${API.patient}/patients/${id}/`, { method: 'DELETE' }),
  appointments: (id) => apiFetch(`${API.patient}/patients/${id}/appointments/`),
};

// ─── Clinical Service ──────────────────────────────────────
const ClinicalAPI = {
  listAppointments:   ()      => apiFetch(`${API.clinical}/appointments/`),
  createAppointment:  (data)  => apiFetch(`${API.clinical}/appointments/`,  { method: 'POST', body: JSON.stringify(data) }),
  updateAppointment:  (id, d) => apiFetch(`${API.clinical}/appointments/${id}/`, { method: 'PATCH', body: JSON.stringify(d) }),
  listPrescriptions:  ()      => apiFetch(`${API.clinical}/prescriptions/`),
  getPrescription:    (id)    => apiFetch(`${API.clinical}/prescriptions/${id}/`),
  createPrescription: (data)  => apiFetch(`${API.clinical}/prescriptions/`, { method: 'POST', body: JSON.stringify(data) }),
};

// ─── Billing Service ───────────────────────────────────────
const BillingAPI = {
  list:  ()    => apiFetch(`${API.billing}/bills/`),
  get:   (id)  => apiFetch(`${API.billing}/bills/${id}/`),
  pay:   (id)  => apiFetch(`${API.billing}/bills/${id}/pay/`, { method: 'PUT' }),
};

// ─── Inventory Service ─────────────────────────────────────
const InventoryAPI = {
  listMedicines:    ()      => apiFetch(`${API.inventory}/medicines/`),
  createMedicine:   (data)  => apiFetch(`${API.inventory}/medicines/`, { method: 'POST', body: JSON.stringify(data) }),
  updateStock:      (id, d) => apiFetch(`${API.inventory}/medicines/${id}/stock/`, { method: 'PATCH', body: JSON.stringify(d) }),
  listTransactions: ()      => apiFetch(`${API.inventory}/stock-transactions/`),
};

// ─── Health check ──────────────────────────────────────────
async function checkService(name, url, dotId) {
  const dot = document.getElementById(dotId);
  try {
    const r = await fetch(url, { signal: AbortSignal.timeout(3000) });
    dot.className = r.ok ? 'dot online' : 'dot offline';
  } catch { dot.className = 'dot offline'; }
}

function checkAllServices() {
  checkService('patient',   `${API.patient}/patients/?page=1`,          'dot-patient');
  checkService('clinical',  `${API.clinical}/appointments/?page=1`,     'dot-clinical');
  checkService('billing',   `${API.billing}/bills/?page=1`,             'dot-billing');
  checkService('inventory', `${API.inventory}/medicines/?page=1`,       'dot-inventory');
}
