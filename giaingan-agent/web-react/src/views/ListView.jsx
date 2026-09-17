import { useState } from "react";
import { fmtVND } from "../lib/constants.js";
import { KetQuaPill } from "../components/Pill.jsx";

// Tab 1: danh sach yeu cau giai ngan.
// props:
//  - requests: mang YCGN, loading, error
//  - ketQua: map ma_ycgn -> {muc, daThayThe}
//  - onOpenDetail(req)
//  - onPrefetch(): chay batch de dien mau (tra ve promise)
export default function ListView({ requests, loading, error, ketQua, onOpenDetail, onPrefetch }) {
  const [prefetching, setPrefetching] = useState(false);

  async function handlePrefetch() {
    setPrefetching(true);
    try {
      await onPrefetch();
    } finally {
      setPrefetching(false);
    }
  }

  return (
    <section className="view active">
      <div className="card">
        <h2>Hàng đợi giải ngân — TNTD (Maker/Checker)</h2>
        <div className="desc">
          Mỗi dòng là một yêu cầu giải ngân. Bấm vào một dòng để mở chi tiết và chạy trợ lý.
        </div>
        <table>
          <thead>
            <tr>
              <th>Mã YCGN</th>
              <th>Khách hàng</th>
              <th>Loại giải ngân</th>
              <th>Số tiền đề nghị</th>
              <th>Số tài liệu</th>
              <th>Kết quả trợ lý</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={6} className="muted">
                  Đang tải…
                </td>
              </tr>
            )}
            {!loading && error && (
              <tr>
                <td colSpan={6} className="muted">
                  Lỗi tải danh sách: {error}
                </td>
              </tr>
            )}
            {!loading && !error && requests.length === 0 && (
              <tr>
                <td colSpan={6} className="muted">
                  Không có hồ sơ.
                </td>
              </tr>
            )}
            {!loading &&
              !error &&
              requests.map((r) => (
                <tr className="req" key={r.ma_ycgn} onClick={() => onOpenDetail(r)}>
                  <td>
                    <b>{r.ma_ycgn}</b>
                  </td>
                  <td>{r.khach_hang || "—"}</td>
                  <td>{r.loai_giai_ngan || "—"}</td>
                  <td>{fmtVND(r.so_tien_de_nghi)}</td>
                  <td>{r.so_tai_lieu}</td>
                  <td>
                    <KetQuaPill kq={ketQua[r.ma_ycgn]} />
                  </td>
                </tr>
              ))}
          </tbody>
        </table>

        <div style={{ marginTop: 12 }}>
          <button className="btn ghost sm" disabled={prefetching} onClick={handlePrefetch}>
            {prefetching ? (
              <>
                <span className="spinner" />
                Đang chạy…
              </>
            ) : (
              "Chạy nhanh cả danh sách (batch) để hiện màu"
            )}
          </button>
        </div>
        <div className="disclaimer">
          Trợ lý chạy bất đồng bộ, không phải mắt xích bắt buộc. Trợ lý lỗi/chậm thì Maker vẫn xử lý
          hồ sơ như quy trình hiện tại.
        </div>
      </div>
    </section>
  );
}
