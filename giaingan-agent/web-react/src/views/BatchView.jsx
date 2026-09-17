import { useState } from "react";
import { MUC_PILL } from "../lib/constants.js";
import { MucPill } from "../components/Pill.jsx";

// Tab 3: hau kiem theo lo (Luong 3).
// props:
//  - mode
//  - runBatch() -> response /batch
//  - onResult(maYcgn, muc, daThayThe): dong bo ve tab 1
//  - onOpenDetail(req)
//  - onError(msg)
export default function BatchView({ mode, runBatch, onResult, onOpenDetail, onError }) {
  const [running, setRunning] = useState(false);
  const [data, setData] = useState(null);

  async function handleRun() {
    setRunning(true);
    try {
      const res = await runBatch();
      setData(res);
      res.bang_xep_hang.forEach((r) => {
        if (MUC_PILL[r.muc_tong_the]) onResult(r.ho_so_id, r.muc_tong_the, false);
      });
    } catch (e) {
      onError("Lỗi /batch: " + e.message);
    } finally {
      setRunning(false);
    }
  }

  const dem = { xanh: 0, vang: 0, do: 0 };
  if (data) {
    data.bang_xep_hang.forEach((r) => {
      if (r.muc_tong_the in dem) dem[r.muc_tong_the]++;
    });
  }

  return (
    <section className="view active">
      <div className="card">
        <h2>Hậu kiểm theo lô — độ phủ 100%</h2>
        <div className="desc">
          Chạy lại 7 bước trên toàn bộ hồ sơ, cho điểm rủi ro và xếp hạng.
        </div>
        <button className="btn" disabled={running} onClick={handleRun}>
          {running ? (
            <>
              <span className="spinner" />
              Đang chạy ({mode})…
            </>
          ) : (
            "▶ Chạy hậu kiểm lô"
          )}
        </button>

        {data && (
          <div style={{ marginTop: 16 }}>
            <div className="kpi">
              <div className="box">
                <div className="v">{data.tong_ho_so}</div>
                <div className="lb">Hồ sơ đã quét</div>
              </div>
              <div className="box">
                <div className="v" style={{ color: "var(--red)" }}>
                  {dem.do}
                </div>
                <div className="lb">🔴 Rủi ro cao</div>
              </div>
              <div className="box">
                <div className="v" style={{ color: "var(--amber)" }}>
                  {dem.vang}
                </div>
                <div className="lb">🟡 Cần chú ý</div>
              </div>
              <div className="box">
                <div className="v" style={{ color: "var(--green)" }}>
                  {dem.xanh}
                </div>
                <div className="lb">🟢 Không bất thường</div>
              </div>
            </div>

            <table>
              <thead>
                <tr>
                  <th>Hạng</th>
                  <th>Mã YCGN</th>
                  <th>Điểm rủi ro</th>
                  <th>Tóm tắt</th>
                  <th>Mức</th>
                </tr>
              </thead>
              <tbody>
                {data.bang_xep_hang.map((r) => (
                  <tr
                    className="req"
                    key={r.ho_so_id}
                    onClick={() =>
                      onOpenDetail({
                        ma_ycgn: r.ho_so_id,
                        khach_hang: "",
                        loai_giai_ngan: "P1",
                        so_tien_de_nghi: null,
                        so_tai_lieu: "—",
                      })
                    }
                  >
                    <td>#{r.xep_hang}</td>
                    <td>
                      <b>{r.ho_so_id}</b>
                    </td>
                    <td>{r.diem_rui_ro}</td>
                    <td className="muted">{r.tom_tat || ""}</td>
                    <td>
                      <MucPill muc={r.muc_tong_the} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="disclaimer">
              Công cụ mở rộng độ phủ hậu kiểm, không phải công cụ tìm lỗi nhân viên.
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
