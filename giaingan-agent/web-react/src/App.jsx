import { useCallback, useEffect, useRef, useState } from "react";
import { callApi, DEFAULT_API_BASE } from "./lib/api.js";
import ListView from "./views/ListView.jsx";
import DetailView from "./views/DetailView.jsx";
import BatchView from "./views/BatchView.jsx";
import CompareModal from "./components/CompareModal.jsx";
import Toast from "./components/Toast.jsx";

export default function App() {
  const [apiBase, setApiBase] = useState(DEFAULT_API_BASE);
  const [mode, setMode] = useState("mock"); // "mock" | "live"
  const [view, setView] = useState("list"); // "list" | "detail" | "batch"

  const [requests, setRequests] = useState([]);
  const [loadingReq, setLoadingReq] = useState(true);
  const [reqError, setReqError] = useState(null);

  const [currentReq, setCurrentReq] = useState(null);
  const [ketQua, setKetQua] = useState({}); // ma_ycgn -> {muc, daThayThe}

  // Luu report goc/thay the cua ho so hien tai de modal doi chieu dung nguon.
  const reportsRef = useRef({ goc: null, thay_the: null });
  const [compare, setCompare] = useState({ open: false, ruleId: null, which: "goc" });

  const [toast, setToast] = useState("");
  const toastTimer = useRef(null);

  const showToast = useCallback((msg) => {
    setToast(msg);
    if (toastTimer.current) clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(""), 6000);
  }, []);

  // ---- Tai danh sach YCGN ----
  const loadRequests = useCallback(async () => {
    setLoadingReq(true);
    setReqError(null);
    try {
      const data = await callApi(apiBase, "/requests");
      setRequests(data.requests || []);
    } catch (e) {
      setReqError(e.message);
      showToast(
        "Không gọi được API /requests: " + e.message + " — kiểm tra backend đã chạy chưa."
      );
    } finally {
      setLoadingReq(false);
    }
  }, [apiBase, showToast]);

  useEffect(() => {
    loadRequests();
  }, [loadRequests]);

  // ---- Dong bo ket qua ve tab 1 ----
  const luuKetQua = useCallback((maYcgn, muc, daThayThe) => {
    setKetQua((prev) => ({ ...prev, [maYcgn]: { muc, daThayThe: !!daThayThe } }));
  }, []);

  // ---- Mo chi tiet ----
  const openDetail = useCallback((req) => {
    setCurrentReq(req);
    reportsRef.current = { goc: null, thay_the: null };
    setView("detail");
  }, []);

  // ---- Goi /check (dung chung cho goc va thay the) ----
  const runCheck = useCallback(
    async (req, docs) => {
      const body = { ho_so_id: req.ma_ycgn, mode };
      if (docs && docs.length) body.tai_lieu_thay_the = docs;
      const data = await callApi(apiBase, "/check", {
        method: "POST",
        body: JSON.stringify(body),
      });
      // Luu report de modal doi chieu truy cap dung nguon
      reportsRef.current[docs && docs.length ? "thay_the" : "goc"] = data.report;
      return data;
    },
    [apiBase, mode]
  );

  // ---- Goi /batch ----
  const runBatch = useCallback(async () => {
    return callApi(apiBase, "/batch", {
      method: "POST",
      body: JSON.stringify({ mode }),
    });
  }, [apiBase, mode]);

  const openCompare = useCallback((ruleId, which) => {
    setCompare({ open: true, ruleId, which });
  }, []);

  const closeCompare = useCallback(() => {
    setCompare((c) => ({ ...c, open: false }));
  }, []);

  return (
    <>
      <header>
        <div>
          <h1>🤖 Trợ lý kiểm tra hồ sơ giải ngân</h1>
          <div className="sub">
            Dashboard gọi API thật — loại giải ngân P1 (thanh toán hàng hóa/dịch vụ có hóa đơn)
          </div>
        </div>
        <div className="modewrap">
          <span className="lbl">Chế độ:</span>
          <label
            className="switch"
            title="Mock: nhanh, offline. AI thật: gọi GreenNode GLM/Qwen (chậm hơn, cần key)"
          >
            <input
              type="checkbox"
              checked={mode === "live"}
              onChange={(e) => setMode(e.target.checked ? "live" : "mock")}
            />
            <span className="slider">
              <span className="txt">Mock</span>
              <span className="txt2">AI thật</span>
            </span>
          </label>
        </div>
      </header>

      <main>
        <div className="apibar">
          API:{" "}
          <input value={apiBase} onChange={(e) => setApiBase(e.target.value)} />
          <span className="muted">
            {" "}
            · Đang dùng:{" "}
            {mode === "live" ? (
              <b style={{ color: "#7ee2a4" }}>AI thật</b>
            ) : (
              <b>mock</b>
            )}
            {mode === "live"
              ? " (gọi GreenNode GLM/Qwen — chậm hơn, cần key)"
              : " (nhanh, không gọi LLM)"}
          </span>
        </div>

        <div className="tabs">
          <div
            className={`tab ${view === "list" ? "active" : ""}`}
            onClick={() => setView("list")}
          >
            1 · Danh sách yêu cầu giải ngân
          </div>
          <div
            className={`tab ${view === "detail" ? "active" : ""}`}
            onClick={() => setView("detail")}
          >
            2 · Chi tiết & Kiểm tra sơ bộ (Luồng 1)
          </div>
          <div
            className={`tab ${view === "batch" ? "active" : ""}`}
            onClick={() => setView("batch")}
          >
            3 · Hậu kiểm theo lô (Luồng 3)
          </div>
        </div>

        {view === "list" && (
          <ListView
            requests={requests}
            loading={loadingReq}
            error={reqError}
            ketQua={ketQua}
            onOpenDetail={openDetail}
            onPrefetch={async () => {
              try {
                const data = await runBatch();
                data.bang_xep_hang.forEach((r) =>
                  luuKetQua(r.ho_so_id, r.muc_tong_the, false)
                );
              } catch (e) {
                showToast("Lỗi chạy batch: " + e.message);
              }
            }}
          />
        )}

        {view === "detail" && (
          <DetailView
            key={currentReq ? currentReq.ma_ycgn : "empty"}
            req={currentReq}
            mode={mode}
            onBack={() => setView("list")}
            runCheck={runCheck}
            onResult={luuKetQua}
            onOpenCompare={openCompare}
            onError={showToast}
          />
        )}

        {view === "batch" && (
          <BatchView
            mode={mode}
            runBatch={runBatch}
            onResult={luuKetQua}
            onOpenDetail={openDetail}
            onError={showToast}
          />
        )}
      </main>

      <CompareModal
        open={compare.open}
        onClose={closeCompare}
        report={reportsRef.current[compare.which]}
        ruleId={compare.ruleId}
      />

      <Toast message={toast} />
    </>
  );
}
