// Dashboard tối giản gọi REST API của Agent Service.
// Đổi API_BASE sang public endpoint AgentBase khi deploy.
const API_BASE = window.API_BASE || "http://localhost:8000";

const MUC_CLASS = { "🟢": "khop", "🟡": "chu-y", "🔴": "lech", "⚪": "chua" };

async function loadHoSo() {
  const sel = document.getElementById("hoSoSelect");
  try {
    const res = await fetch(`${API_BASE}/ho-so`);
    const data = await res.json();
    sel.innerHTML = data.ho_so_ids.map((id) => `<option>${id}</option>`).join("");
  } catch (e) {
    sel.innerHTML = `<option>Không kết nối được API (${API_BASE})</option>`;
  }
}

function badge(muc) {
  return `<span class="badge ${MUC_CLASS[muc] || "chua"}">${muc}</span>`;
}

async function check() {
  const ho_so_id = document.getElementById("hoSoSelect").value;
  const res = await fetch(`${API_BASE}/check`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ho_so_id }),
  });
  if (!res.ok) {
    document.getElementById("ketQua").innerHTML = `<p>Lỗi: ${res.status}</p>`;
    return;
  }
  const kq = await res.json();
  renderKetQua(kq);
}

function renderKetQua(kq) {
  const dp = kq.do_phu || {};
  document.getElementById("tongHop").innerHTML =
    `${badge(kq.muc_tong_hop)} <strong>${kq.ho_so_id}</strong> (${kq.loai_giai_ngan})` +
    `<p>${kq.dien_giai || ""}</p>` +
    `<p>Độ phủ: ${dp.khop || 0} 🟢 &middot; ${dp.chu_y || 0} 🟡 &middot; ${dp.lech || 0} 🔴 &middot; ${dp.chua_kiem || 0} ⚪</p>`;

  const rows = (kq.quy_tac || [])
    .map(
      (q) => `<tr>
        <td>${q.rule_id}</td>
        <td>${q.ten}</td>
        <td class="rule-muc">${badge(q.muc)}</td>
        <td>${q.ly_do || ""}</td>
      </tr>`
    )
    .join("");
  document.getElementById("ketQua").innerHTML =
    `<table><thead><tr><th>Rule</th><th>Nội dung</th><th>Mức</th><th>Lý do / dẫn nguồn</th></tr></thead>` +
    `<tbody>${rows}</tbody></table>`;
}

async function batch() {
  const res = await fetch(`${API_BASE}/batch`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({}),
  });
  const data = await res.json();
  const rows = (data.xep_hang || [])
    .map(
      (r) => `<tr>
        <td>${r.ho_so_id}</td>
        <td>${r.loai_giai_ngan || ""}</td>
        <td>${r.muc_tong_hop || ""}</td>
        <td>${r.diem_rui_ro}</td>
      </tr>`
    )
    .join("");
  document.getElementById("bangXepHang").innerHTML =
    `<table><thead><tr><th>Hồ sơ</th><th>Loại</th><th>Mức</th><th>Điểm rủi ro</th></tr></thead>` +
    `<tbody>${rows}</tbody></table>`;
}

document.getElementById("btnCheck").addEventListener("click", check);
document.getElementById("btnBatch").addEventListener("click", batch);
loadHoSo();
