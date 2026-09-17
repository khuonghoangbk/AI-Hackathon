import { MUC_PILL, MUC_ICON, MUC_TEXT, TT_ICON } from "../lib/constants.js";

// Mot cot ket qua (ho so goc hoac ho so thay the).
// props:
//  - title: tieu de cot
//  - data: response tu /check (co .report, .mode, .so_tai_lieu) hoac null
//  - placeholder: text khi chua co du lieu
//  - which: "goc" | "thay_the" (de biet mo modal cho report nao)
//  - onOpenCompare(ruleId, which)
export default function ReportColumn({ title, data, placeholder, which, onOpenCompare }) {
  if (!data) {
    return (
      <div className="report-col">
        <div className="col-title">{title}</div>
        <div className="col-body muted">{placeholder}</div>
      </div>
    );
  }

  const rep = data.report;
  const tk = rep.thong_ke;
  const soTaiLieu = data.so_tai_lieu != null ? ` · ${data.so_tai_lieu} tài liệu` : "";

  return (
    <div className="report-col">
      <div className="col-title">{title}</div>
      <div className="col-body">
        <div className="desc">
          <span className={`pill ${MUC_PILL[rep.muc_tong_the]}`}>
            {MUC_ICON[rep.muc_tong_the]} {MUC_TEXT[rep.muc_tong_the]}
          </span>
          &nbsp; {rep.tom_tat}
          <div style={{ marginTop: 8 }} className="muted">
            🟢 {tk.xanh} · 🟡 {tk.vang} · 🔴 {tk.do} · ⚪ {tk.chua_kiem_tra_duoc} · Độ phủ:{" "}
            <b>{tk.do_phu_phan_tram}%</b> · Chế độ: <b>{data.mode}</b>
            {soTaiLieu}
          </div>
        </div>

        <table style={{ margin: "10px 0" }}>
          <thead>
            <tr>
              <th>Mã</th>
              <th>Tài liệu</th>
              <th>Trạng thái</th>
              <th>Lý do</th>
            </tr>
          </thead>
          <tbody>
            {rep.tai_lieu.map((m, i) => (
              <tr key={i}>
                <td>{m.ma_checklist}</td>
                <td>{m.ten}</td>
                <td>
                  {TT_ICON[m.trang_thai] || ""} {m.trang_thai}
                </td>
                <td className="muted">{m.ly_do || ""}</td>
              </tr>
            ))}
          </tbody>
        </table>

        <div className="findings-box">
          {rep.phat_hien.map((p, i) => {
            const canClick =
              p.nguon && typeof p.nguon === "object" && ["do", "vang"].includes(p.muc);
            return (
              <div className={`finding ${p.muc}`} key={i}>
                <div className="h">
                  {MUC_ICON[p.muc]} [{p.rule_id}] {p.mo_ta}
                </div>
                <div className="muted">{p.chi_tiet || ""}</div>
                {p.nguon && typeof p.nguon === "object" && (
                  <div className="src">
                    Nguồn: {p.rule_id}
                    {canClick && (
                      <>
                        {" "}
                        ·{" "}
                        <a onClick={() => onOpenCompare(p.rule_id, which)}>
                          Mở 2 trang tài liệu cạnh nhau
                        </a>
                      </>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        <div className="disclaimer">{rep.cau_chot || ""}</div>
      </div>
    </div>
  );
}
