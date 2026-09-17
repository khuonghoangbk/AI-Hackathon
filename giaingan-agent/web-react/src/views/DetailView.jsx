import { useRef, useState } from "react";
import { fmtVND, extractTaiLieu } from "../lib/constants.js";
import ReportColumn from "../components/ReportColumn.jsx";

// Tab 2: chi tiet + kiem tra so bo (Luong 1).
// props:
//  - req: YCGN dang xem (null neu chua chon)
//  - mode: "mock" | "live"
//  - onBack()
//  - runCheck(req, docs|null) -> tra ve response /check (throw neu loi)
//  - onResult(maYcgn, muc, daThayThe): dong bo ket qua ve tab 1
//  - onOpenCompare(ruleId, which)
//  - onError(msg)
export default function DetailView({
  req,
  mode,
  onBack,
  runCheck,
  onResult,
  onOpenCompare,
  onError,
}) {
  const [reportGoc, setReportGoc] = useState(null);
  const [reportThayThe, setReportThayThe] = useState(null);
  const [replDocs, setReplDocs] = useState([]); // [{ten_file, doc}|{ten_file, loi}]
  const [runningGoc, setRunningGoc] = useState(false);
  const [runningRepl, setRunningRepl] = useState(false);
  const [replHint, setReplHint] = useState("");
  const fileRef = useRef(null);

  // Reset khi doi ho so (key tren component o App se remount, nhung phong ho)
  const validDocs = replDocs.filter((x) => x.doc);

  async function handleRunGoc() {
    setRunningGoc(true);
    try {
      const data = await runCheck(req, null);
      setReportGoc(data);
      onResult(req.ma_ycgn, data.report.muc_tong_the, false);
    } catch (e) {
      onError("Lỗi /check: " + e.message);
    } finally {
      setRunningGoc(false);
    }
  }

  async function handleFiles(e) {
    const files = Array.from(e.target.files || []);
    if (!files.length) return;
    const next = [...replDocs];
    for (const f of files) {
      try {
        const text = await f.text();
        const parsed = JSON.parse(text);
        const docs = extractTaiLieu(parsed);
        if (!docs.length) {
          next.push({
            ten_file: f.name,
            loi: "Không tìm thấy tài liệu (thiếu 'ma_checklist' hoặc 'tai_lieu').",
          });
        } else {
          docs.forEach((d) => next.push({ ten_file: f.name, doc: d }));
        }
      } catch (err) {
        next.push({ ten_file: f.name, loi: "File JSON không hợp lệ: " + err.message });
      }
    }
    setReplDocs(next);
    e.target.value = ""; // cho phep chon lai cung file
  }

  function clearRepl() {
    setReplDocs([]);
    setReportThayThe(null);
  }

  async function handleRunRepl() {
    const docs = replDocs.filter((x) => x.doc).map((x) => x.doc);
    if (!docs.length) return;
    setRunningRepl(true);
    try {
      const data = await runCheck(req, docs);
      setReportThayThe(data);
      onResult(req.ma_ycgn, data.report.muc_tong_the, true);
      if (!reportGoc) {
        setReplHint('Gợi ý: bấm "Kiểm tra sơ bộ" trên hồ sơ gốc để so sánh trước/sau.');
      }
    } catch (e) {
      onError("Lỗi /check (thay thế): " + e.message);
    } finally {
      setRunningRepl(false);
    }
  }

  const showReport = reportGoc || reportThayThe;

  return (
    <section className="view active">
      <span className="back" onClick={onBack}>
        ← Quay lại danh sách
      </span>

      <div className="card">
        {req ? (
          <>
            <h2>
              {req.ma_ycgn} — {req.khach_hang || ""}
            </h2>
            <div className="desc">
              Loại: {req.loai_giai_ngan} · Số tiền đề nghị: <b>{fmtVND(req.so_tien_de_nghi)}</b> · Số
              tài liệu: {req.so_tai_lieu}
            </div>
          </>
        ) : (
          <div className="muted">Chọn một hồ sơ ở tab 1.</div>
        )}
      </div>

      {req && (
        <div className="card">
          <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
            <button className="btn" disabled={runningGoc} onClick={handleRunGoc}>
              {runningGoc ? (
                <>
                  <span className="spinner" />
                  Đang chạy ({mode})…
                </>
              ) : (
                "▶ Kiểm tra sơ bộ"
              )}
            </button>
            <span className="muted">
              {runningGoc && mode === "live"
                ? "Chế độ AI thật có thể mất 1-2 phút, vui lòng đợi…"
                : `Bấm để trợ lý chạy 7 bước (chế độ: ${mode}).`}
            </span>
          </div>

          <div className="repl">
            <div className="repl-head">
              <b>Hồ sơ thay thế / bổ sung (TNTD)</b>
              <span className="muted">
                {" "}
                · Chọn file <code>.json</code> để thay thế hoặc bổ sung tài liệu, ghép theo{" "}
                <code>mã checklist</code>. Hồ sơ gốc của KH không bị thay đổi.
              </span>
            </div>
            <div className="repl-actions">
              <label className="btn ghost sm" onClick={() => fileRef.current?.click()}>
                📎 Chọn file .json…
              </label>
              <input
                ref={fileRef}
                type="file"
                accept=".json,application/json"
                multiple
                style={{ display: "none" }}
                onChange={handleFiles}
              />
              <button className="btn sm" disabled={validDocs.length === 0 || runningRepl} onClick={handleRunRepl}>
                {runningRepl ? (
                  <>
                    <span className="spinner" />
                    Đang chạy ({mode})…
                  </>
                ) : (
                  "▶ Kiểm tra sơ bộ trên hồ sơ thay thế"
                )}
              </button>
              {replDocs.length > 0 && (
                <button className="btn ghost sm" onClick={clearRepl}>
                  Xóa file đã chọn
                </button>
              )}
            </div>

            <div className={replDocs.length ? "repl-list" : "repl-list muted"}>
              {replDocs.length === 0 ? (
                "Chưa có file thay thế nào được chọn."
              ) : (
                replDocs.map((x, i) =>
                  x.loi ? (
                    <div className="fitem bad" key={i}>
                      ⚠️ <span>{x.ten_file}</span> — {x.loi}
                    </div>
                  ) : (
                    <div className="fitem" key={i}>
                      📎 <span>{x.ten_file}</span> · <span className="ma">mã {x.doc.ma_checklist}</span>{" "}
                      · {(x.doc.noi_dung && x.doc.noi_dung.tieu_de) || "(không rõ tiêu đề)"}
                    </div>
                  )
                )
              )}
            </div>
            <span className="muted">{replHint}</span>
          </div>
        </div>
      )}

      {req && showReport && (
        <div className="card">
          <h2>Kết quả kiểm tra sơ bộ</h2>
          <div className="desc">
            So sánh kết quả trên hồ sơ gốc (KH đẩy lên) và hồ sơ sau khi TNTD thay thế/bổ sung.
          </div>
          <div className="report-cols">
            <ReportColumn
              title="📄 Hồ sơ gốc (KH đẩy lên)"
              data={reportGoc}
              placeholder="Bấm “Kiểm tra sơ bộ” để chạy trên hồ sơ gốc."
              which="goc"
              onOpenCompare={onOpenCompare}
            />
            <ReportColumn
              title="🔁 Hồ sơ sau thay thế (TNTD)"
              data={reportThayThe}
              placeholder="Chọn file .json rồi bấm “Kiểm tra sơ bộ trên hồ sơ thay thế”."
              which="thay_the"
              onOpenCompare={onOpenCompare}
            />
          </div>
        </div>
      )}
    </section>
  );
}
