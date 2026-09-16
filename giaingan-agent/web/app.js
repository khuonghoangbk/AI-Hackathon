/* Dashboard tro ly kiem tra ho so giai ngan — goi API that.
   Khong hardcode du lieu: moi thu lay tu /requests, /check, /batch. */

const $ = (id) => document.getElementById(id);

// ---- Trang thai chung ----
const state = {
  mode: "mock",          // theo toggle
  currentReq: null,      // YCGN dang xem
  reportGoc: null,       // report ho so goc (de modal doi chieu)
  reportThayThe: null,   // report ho so sau thay the
  replDocs: [],          // tai lieu thay the/bo sung da chon tu file .json
  ketQua: {},            // map ma_ycgn -> muc_tong_the (dong bo ve cot ket qua tab 1)
};

function apiBase() {
  return $("apiBase").value.replace(/\/+$/, "");
}

function fmtVND(n) {
  if (n == null) return "—";
  return n.toLocaleString("vi-VN") + " VND";
}

function showToast(msg) {
  const t = $("toast");
  t.textContent = msg;
  t.style.display = "block";
  setTimeout(() => (t.style.display = "none"), 6000);
}

async function callApi(path, opts = {}) {
  const res = await fetch(apiBase() + path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      detail = (await res.json()).detail || detail;
    } catch (_) {}
    throw new Error(`(${res.status}) ${detail}`);
  }
  return res.json();
}

// ---- Anh xa muc -> class pill ----
const MUC_PILL = { xanh: "clean", vang: "warn", do: "risk", chua_kiem_tra_duoc: "trang", loi: "risk" };
const MUC_ICON = { xanh: "🟢", vang: "🟡", do: "🔴", chua_kiem_tra_duoc: "⚪", loi: "⚠️" };
const MUC_TEXT = { xanh: "Sạch", vang: "Cần chú ý", do: "Có rủi ro", chua_kiem_tra_duoc: "Chưa đủ độ phủ", loi: "Lỗi" };
const TT_ICON = { xanh: "🟢", cam: "🟠", do: "🔴", khong_ap_dung: "—" };

// ---- Tabs ----
document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => switchView(tab.dataset.view));
});
function switchView(name) {
  document.querySelectorAll(".tab").forEach((t) => t.classList.toggle("active", t.dataset.view === name));
  document.querySelectorAll(".view").forEach((v) => v.classList.remove("active"));
  $("view-" + name).classList.add("active");
}

// ---- Toggle mode ----
$("modeToggle").addEventListener("change", (e) => {
  state.mode = e.target.checked ? "live" : "mock";
  $("modeHint").innerHTML =
    state.mode === "live"
      ? ' · Đang dùng: <b style="color:#7ee2a4">AI thật</b> (gọi GreenNode GLM/Qwen — chậm hơn, cần key)'
      : " · Đang dùng: <b>mock</b> (nhanh, không gọi LLM)";
});

// ==================== TAB 1: DANH SACH ====================
async function loadRequests() {
  const tbody = $("reqTable");
  tbody.innerHTML = `<tr><td colspan="6" class="muted">Đang tải…</td></tr>`;
  try {
    const data = await callApi("/requests");
    if (!data.requests.length) {
      tbody.innerHTML = `<tr><td colspan="6" class="muted">Không có hồ sơ.</td></tr>`;
      return;
    }
    tbody.innerHTML = "";
    data.requests.forEach((r) => {
      const tr = document.createElement("tr");
      tr.className = "req";
      tr.innerHTML = `
        <td><b>${r.ma_ycgn}</b></td>
        <td>${r.khach_hang || "—"}</td>
        <td>${r.loai_giai_ngan || "—"}</td>
        <td>${fmtVND(r.so_tien_de_nghi)}</td>
        <td>${r.so_tai_lieu}</td>
        <td id="kq-${r.ma_ycgn}">${ketQuaPill(state.ketQua[r.ma_ycgn])}</td>`;
      tr.addEventListener("click", () => openDetail(r));
      tbody.appendChild(tr);
    });
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="6" class="muted">Lỗi tải danh sách: ${e.message}</td></tr>`;
    showToast("Không gọi được API /requests: " + e.message + " — kiểm tra backend đã chạy chưa.");
  }
}

// Sinh pill ket qua cho cot "Ket qua tro ly" (tab 1)
function ketQuaPill(kq) {
  if (!kq) return `<span class="pill idle">Chưa kiểm tra</span>`;
  const hau = kq.daThayThe ? " (sau thay thế)" : "";
  return `<span class="pill ${MUC_PILL[kq.muc]}">${MUC_ICON[kq.muc]} ${MUC_TEXT[kq.muc]}${hau}</span>`;
}

// Luu ket qua 1 ho so vao state va cap nhat ngay cell o tab 1 (neu dang hien thi)
function luuKetQua(maYcgn, muc, daThayThe) {
  state.ketQua[maYcgn] = { muc, daThayThe: !!daThayThe };
  const cell = $("kq-" + maYcgn);
  if (cell) cell.innerHTML = ketQuaPill(state.ketQua[maYcgn]);
}

// Chay batch de dien mau vao cot ket qua cua tab 1
$("prefetchBtn").addEventListener("click", async () => {
  const btn = $("prefetchBtn");
  btn.disabled = true;
  btn.innerHTML = `<span class="spinner"></span>Đang chạy…`;
  try {
    const data = await callApi("/batch", { method: "POST", body: JSON.stringify({ mode: state.mode }) });
    data.bang_xep_hang.forEach((r) => luuKetQua(r.ho_so_id, r.muc_tong_the, false));
  } catch (e) {
    showToast("Lỗi chạy batch: " + e.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "Chạy nhanh cả danh sách (batch) để hiện màu";
  }
});

// ==================== TAB 2: CHI TIET ====================
function openDetail(req) {
  switchView("detail");
  state.currentReq = req;
  state.replDocs = [];           // tai lieu thay the da chon (parse tu file .json)
  state.reportGoc = null;        // luu report goc de modal doi chieu
  state.reportThayThe = null;
  $("reqHeader").innerHTML = `
    <h2>${req.ma_ycgn} — ${req.khach_hang || ""}</h2>
    <div class="desc">Loại: ${req.loai_giai_ngan} · Số tiền đề nghị: <b>${fmtVND(req.so_tien_de_nghi)}</b> · Số tài liệu: ${req.so_tai_lieu}</div>`;
  $("runCard").style.display = "block";
  $("reportCard").style.display = "none";
  $("runHint").textContent = `Bấm để trợ lý chạy 7 bước (chế độ: ${state.mode}).`;
  // Reset khu vuc upload + 2 cot ket qua
  renderReplList();
  resetCol("colGoc", "📄 Hồ sơ gốc (KH đẩy lên)", "Bấm “Kiểm tra sơ bộ” để chạy trên hồ sơ gốc.");
  resetCol("colThayThe", "🔁 Hồ sơ sau thay thế (TNTD)", "Chọn file .json rồi bấm “Kiểm tra sơ bộ trên hồ sơ thay thế”.");
}

$("backToList").addEventListener("click", () => switchView("list"));

$("runBtn").addEventListener("click", async () => {
  const req = state.currentReq;
  if (!req) return;
  const btn = $("runBtn");
  btn.disabled = true;
  btn.innerHTML = `<span class="spinner"></span>Đang chạy (${state.mode})…`;
  if (state.mode === "live") $("runHint").textContent = "Chế độ AI thật có thể mất 1-2 phút, vui lòng đợi…";
  try {
    const data = await callApi("/check", {
      method: "POST",
      body: JSON.stringify({ ho_so_id: req.ma_ycgn, mode: state.mode }),
    });
    state.reportGoc = data.report;
    renderReportInto("colGoc", "📄 Hồ sơ gốc (KH đẩy lên)", data, "goc");
    $("reportCard").style.display = "block";
    luuKetQua(req.ma_ycgn, data.report.muc_tong_the, false);
  } catch (e) {
    showToast("Lỗi /check: " + e.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "▶ Kiểm tra sơ bộ";
    $("runHint").textContent = `Bấm để trợ lý chạy 7 bước (chế độ: ${state.mode}).`;
  }
});

// ---- Upload ho so thay the (.json) ----
$("replFile").addEventListener("change", async (e) => {
  const files = Array.from(e.target.files || []);
  if (!files.length) return;
  for (const f of files) {
    try {
      const text = await f.text();
      const parsed = JSON.parse(text);
      const docs = extractTaiLieu(parsed);
      if (!docs.length) {
        state.replDocs.push({ ten_file: f.name, loi: "Không tìm thấy tài liệu (thiếu 'ma_checklist' hoặc 'tai_lieu')." });
      } else {
        docs.forEach((d) => state.replDocs.push({ ten_file: f.name, doc: d }));
      }
    } catch (err) {
      state.replDocs.push({ ten_file: f.name, loi: "File JSON không hợp lệ: " + err.message });
    }
  }
  e.target.value = ""; // cho phep chon lai cung file
  renderReplList();
});

// Chuan hoa moi dang file upload -> mang tai lieu {ma_checklist, ...}
function extractTaiLieu(parsed) {
  if (Array.isArray(parsed)) {
    return parsed.filter((x) => x && x.ma_checklist != null);
  }
  if (parsed && Array.isArray(parsed.tai_lieu)) {
    return parsed.tai_lieu.filter((x) => x && x.ma_checklist != null);
  }
  if (parsed && parsed.ma_checklist != null) {
    return [parsed];
  }
  return [];
}

function renderReplList() {
  const list = $("replList");
  const validDocs = (state.replDocs || []).filter((x) => x.doc);
  const hasAny = (state.replDocs || []).length > 0;
  $("runReplBtn").disabled = validDocs.length === 0;
  $("clearReplBtn").style.display = hasAny ? "inline-block" : "none";
  if (!hasAny) {
    list.className = "repl-list muted";
    list.textContent = "Chưa có file thay thế nào được chọn.";
    return;
  }
  list.className = "repl-list";
  list.innerHTML = state.replDocs
    .map((x) => {
      if (x.loi) {
        return `<div class="fitem bad">⚠️ <span>${x.ten_file}</span> — ${x.loi}</div>`;
      }
      const ma = x.doc.ma_checklist;
      const td = (x.doc.noi_dung && x.doc.noi_dung.tieu_de) || "(không rõ tiêu đề)";
      return `<div class="fitem">📎 <span>${x.ten_file}</span> · <span class="ma">mã ${ma}</span> · ${td}</div>`;
    })
    .join("");
}

$("clearReplBtn").addEventListener("click", () => {
  state.replDocs = [];
  renderReplList();
  resetCol("colThayThe", "🔁 Hồ sơ sau thay thế (TNTD)", "Chọn file .json rồi bấm “Kiểm tra sơ bộ trên hồ sơ thay thế”.");
});

$("runReplBtn").addEventListener("click", async () => {
  const req = state.currentReq;
  if (!req) return;
  const docs = (state.replDocs || []).filter((x) => x.doc).map((x) => x.doc);
  if (!docs.length) return;
  const btn = $("runReplBtn");
  btn.disabled = true;
  btn.innerHTML = `<span class="spinner"></span>Đang chạy (${state.mode})…`;
  try {
    const data = await callApi("/check", {
      method: "POST",
      body: JSON.stringify({ ho_so_id: req.ma_ycgn, mode: state.mode, tai_lieu_thay_the: docs }),
    });
    state.reportThayThe = data.report;
    renderReportInto("colThayThe", "🔁 Hồ sơ sau thay thế (TNTD)", data, "thay_the");
    $("reportCard").style.display = "block";
    luuKetQua(req.ma_ycgn, data.report.muc_tong_the, true);
    if (!state.reportGoc) {
      $("runReplHint").textContent = "Gợi ý: bấm “Kiểm tra sơ bộ” trên hồ sơ gốc để so sánh trước/sau.";
    }
  } catch (e) {
    showToast("Lỗi /check (thay thế): " + e.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "▶ Kiểm tra sơ bộ trên hồ sơ thay thế";
  }
});

function resetCol(colId, title, placeholder) {
  const col = $(colId);
  if (!col) return;
  col.innerHTML = `<div class="col-title">${title}</div><div class="col-body muted">${placeholder}</div>`;
}

// Render toan bo bao cao (phan loai + tom tat + phat hien + cau chot) vao 1 cot
function renderReportInto(colId, title, data, which) {
  const rep = data.report;
  const tk = rep.thong_ke;

  const soTaiLieu = data.so_tai_lieu != null ? ` · ${data.so_tai_lieu} tài liệu` : "";

  const docRows = rep.tai_lieu
    .map(
      (m) => `<tr>
        <td>${m.ma_checklist}</td>
        <td>${m.ten}</td>
        <td>${TT_ICON[m.trang_thai] || ""} ${m.trang_thai}</td>
        <td class="muted">${m.ly_do || ""}</td></tr>`
    )
    .join("");

  const findingsHtml = rep.phat_hien
    .map((p) => {
      let srcHtml = "";
      if (p.nguon && typeof p.nguon === "object") {
        const canClick = ["do", "vang"].includes(p.muc);
        srcHtml = `<div class="src">Nguồn: ${p.rule_id}${
          canClick ? ` · <a data-rule="${p.rule_id}" data-which="${which}">Mở 2 trang tài liệu cạnh nhau</a>` : ""
        }</div>`;
      }
      return `<div class="finding ${p.muc}">
        <div class="h">${MUC_ICON[p.muc]} [${p.rule_id}] ${p.mo_ta}</div>
        <div class="muted">${p.chi_tiet || ""}</div>
        ${srcHtml}</div>`;
    })
    .join("");

  const col = $(colId);
  col.innerHTML = `
    <div class="col-title">${title}</div>
    <div class="col-body">
      <div class="desc">
        <span class="pill ${MUC_PILL[rep.muc_tong_the]}">${MUC_ICON[rep.muc_tong_the]} ${MUC_TEXT[rep.muc_tong_the]}</span>
        &nbsp; ${rep.tom_tat}
        <div style="margin-top:8px" class="muted">
          🟢 ${tk.xanh} · 🟡 ${tk.vang} · 🔴 ${tk.do} · ⚪ ${tk.chua_kiem_tra_duoc}
          · Độ phủ: <b>${tk.do_phu_phan_tram}%</b> · Chế độ: <b>${data.mode}</b>${soTaiLieu}
        </div>
      </div>
      <table style="margin:10px 0">
        <thead><tr><th>Mã</th><th>Tài liệu</th><th>Trạng thái</th><th>Lý do</th></tr></thead>
        <tbody>${docRows}</tbody>
      </table>
      <div class="findings-box">${findingsHtml}</div>
      <div class="disclaimer">${rep.cau_chot || ""}</div>
    </div>`;

  // Gan su kien mo modal doi chieu
  col.querySelectorAll("a[data-rule]").forEach((a) => {
    a.addEventListener("click", () => openCompare(a.dataset.rule, a.dataset.which));
  });
}

// ==================== MODAL 2 TRANG ====================
function openCompare(ruleId, which) {
  const rep = which === "thay_the" ? state.reportThayThe : state.reportGoc;
  if (!rep) return;
  const p = rep.phat_hien.find((x) => x.rule_id === ruleId);
  if (!p || !p.nguon) return;

  const keys = Object.keys(p.nguon);
  const body = $("modalBody");
  body.innerHTML = "";
  $("modalTitle").textContent = `Đối chiếu ${ruleId} — ${p.mo_ta}`;

  keys.forEach((k) => {
    const src = p.nguon[k];
    const panel = document.createElement("div");
    panel.className = "doc";
    if (src) {
      panel.innerHTML = `
        <h4>Tài liệu ${src.tai_lieu || ""} · ${src.doc_id || ""}${src.trang ? " · trang " + src.trang : ""}</h4>
        <div class="row"><span>Trường</span><span><b>${k}</b></span></div>
        <div class="row"><span>Độ tin cậy</span><span>${src.do_tin_cay || "—"}</span></div>
        <div class="row"><span>Giá trị (trong đối chiếu)</span><span class="hl">${extractValueFromDetail(p.chi_tiet, k)}</span></div>`;
    } else {
      panel.innerHTML = `<h4>${k}</h4><div class="muted">Không có nguồn (dữ liệu thiếu hoặc chưa xác thực).</div>`;
    }
    body.appendChild(panel);
  });
  $("modal").classList.add("show");
}

// Tach gia tri tu chuoi chi_tiet dang "fa=... vs fb=..."
function extractValueFromDetail(detail, key) {
  if (!detail) return "—";
  const re = new RegExp(key + "=([^\\s]+(?:\\s[^=]*?)?)(?:\\svs\\s|$)");
  const m = detail.match(re);
  return m ? m[1].trim() : detail;
}

$("modalClose").addEventListener("click", () => $("modal").classList.remove("show"));
$("modal").addEventListener("click", (e) => {
  if (e.target.id === "modal") $("modal").classList.remove("show");
});

// ==================== TAB 3: BATCH ====================
$("batchBtn").addEventListener("click", async () => {
  const btn = $("batchBtn");
  btn.disabled = true;
  btn.innerHTML = `<span class="spinner"></span>Đang chạy (${state.mode})…`;
  try {
    const data = await callApi("/batch", { method: "POST", body: JSON.stringify({ mode: state.mode }) });
    renderBatch(data);
  } catch (e) {
    showToast("Lỗi /batch: " + e.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "▶ Chạy hậu kiểm lô";
  }
});

function renderBatch(data) {
  const rows = data.bang_xep_hang;
  const dem = { xanh: 0, vang: 0, do: 0 };
  rows.forEach((r) => {
    if (r.muc_tong_the in dem) dem[r.muc_tong_the]++;
  });
  $("batchKpi").innerHTML = `
    <div class="box"><div class="v">${data.tong_ho_so}</div><div class="lb">Hồ sơ đã quét</div></div>
    <div class="box"><div class="v" style="color:var(--red)">${dem.do}</div><div class="lb">🔴 Rủi ro cao</div></div>
    <div class="box"><div class="v" style="color:var(--amber)">${dem.vang}</div><div class="lb">🟡 Cần chú ý</div></div>
    <div class="box"><div class="v" style="color:var(--green)">${dem.xanh}</div><div class="lb">🟢 Không bất thường</div></div>`;

  const tbody = $("batchTable");
  tbody.innerHTML = "";
  rows.forEach((r) => {
    // Dong bo ket qua ve cot o tab 1
    if (MUC_PILL[r.muc_tong_the]) luuKetQua(r.ho_so_id, r.muc_tong_the, false);
    const tr = document.createElement("tr");
    tr.className = "req";
    tr.innerHTML = `
      <td>#${r.xep_hang}</td>
      <td><b>${r.ho_so_id}</b></td>
      <td>${r.diem_rui_ro}</td>
      <td class="muted">${r.tom_tat || ""}</td>
      <td><span class="pill ${MUC_PILL[r.muc_tong_the]}">${MUC_ICON[r.muc_tong_the]} ${MUC_TEXT[r.muc_tong_the]}</span></td>`;
    tr.addEventListener("click", () => {
      const req = { ma_ycgn: r.ho_so_id, khach_hang: "", loai_giai_ngan: "P1", so_tien_de_nghi: null, so_tai_lieu: "—" };
      openDetail(req);
    });
    tbody.appendChild(tr);
  });
  $("batchResult").style.display = "block";
}

// ---- Khoi dong ----
loadRequests();
