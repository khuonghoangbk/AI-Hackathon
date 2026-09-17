import { extractValueFromDetail } from "../lib/constants.js";

// Modal doi chieu 2 trang tai lieu canh nhau.
// props: open, onClose, report (report tuong ung goc/thay the), ruleId
export default function CompareModal({ open, onClose, report, ruleId }) {
  const p =
    open && report ? report.phat_hien.find((x) => x.rule_id === ruleId) : null;

  if (!open || !p || !p.nguon) {
    return (
      <div className="modal" onClick={(e) => e.target.classList.contains("modal") && onClose()}>
        <div className="inner" />
      </div>
    );
  }

  const keys = Object.keys(p.nguon);

  return (
    <div
      className="modal show"
      onClick={(e) => e.target.classList.contains("modal") && onClose()}
    >
      <div className="inner">
        <div style={{ display: "flex", alignItems: "center", marginBottom: 12 }}>
          <h2 style={{ margin: 0 }}>
            Đối chiếu {ruleId} — {p.mo_ta}
          </h2>
          <button className="btn ghost sm" style={{ marginLeft: "auto" }} onClick={onClose}>
            Đóng ✕
          </button>
        </div>
        <div className="grid2">
          {keys.map((k) => {
            const src = p.nguon[k];
            return (
              <div className="doc" key={k}>
                {src ? (
                  <>
                    <h4>
                      Tài liệu {src.tai_lieu || ""} · {src.doc_id || ""}
                      {src.trang ? " · trang " + src.trang : ""}
                    </h4>
                    <div className="row">
                      <span>Trường</span>
                      <span>
                        <b>{k}</b>
                      </span>
                    </div>
                    <div className="row">
                      <span>Độ tin cậy</span>
                      <span>{src.do_tin_cay || "—"}</span>
                    </div>
                    <div className="row">
                      <span>Giá trị (trong đối chiếu)</span>
                      <span className="hl">{extractValueFromDetail(p.chi_tiet, k)}</span>
                    </div>
                  </>
                ) : (
                  <>
                    <h4>{k}</h4>
                    <div className="muted">
                      Không có nguồn (dữ liệu thiếu hoặc chưa xác thực).
                    </div>
                  </>
                )}
              </div>
            );
          })}
        </div>
        <div className="disclaimer">
          Maker tự xác nhận bằng cách nhìn đúng vị trí được khoanh, không tin trợ lý một cách mù quáng.
        </div>
      </div>
    </div>
  );
}
