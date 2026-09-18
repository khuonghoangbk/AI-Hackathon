# Trợ lý kiểm tra hồ sơ giải ngân (MVP — MSB AI Hackathon 2026)

Multi-step AI agent đọc hồ sơ giải ngân → phân loại → trích xuất → đối chiếu chéo theo quy tắc → sinh báo cáo 3 mức 🟢🟡🔴 có dẫn nguồn.

> Phạm vi MVP: 1 loại giải ngân **P1 — "Giải ngân thanh toán cho hàng hóa, dịch vụ có hóa đơn"**, checklist 16 mục, 3 vùng hồ sơ.

## AI Usage — Dùng model nào, ở nghiệp vụ nào

Sản phẩm là **multi-step AI agent 7 bước**. LLM được gọi qua **GreenNode MaaS** (API tương thích OpenAI) tại **3 điểm nghiệp vụ cần đọc-hiểu/suy luận**; các bước còn lại dùng rule engine (logic Python + quy tắc JSON) để đảm bảo tính giải thích được và dẫn nguồn.

**Model sử dụng:**
- `z-ai/glm-5.2-hackathon` (**GLM 5.2** — reasoning): suy luận/đối chiếu ngữ nghĩa.
- `qwen/qwen3.6-flash` (**Qwen3 Flash** — fast): phân loại + trích xuất trường có schema JSON.

**Bản đồ AI theo từng bước (Luồng 1):**

| Bước nghiệp vụ | Dùng AI? | Model / Agent | Vai trò của AI |
|---|---|---|---|
| B1. Lấy ngữ cảnh khoản vay | Không | — | Đọc dữ liệu có cấu trúc |
| B2. Load tài liệu (mock ECM) | Không | — | Truy xuất chứng từ |
| **B3. Phân loại tài liệu** (cửa chặn) | **Có** | Qwen3 Flash | Nhận diện loại chứng từ từ nội dung |
| **B4. Trích xuất thông tin** | **Có** | Qwen3 Flash | Bóc tách trường: số tiền, người thụ hưởng, số/ngày hóa đơn… |
| B5. Tra lịch sử hóa đơn | Không | — | Đối chiếu DB phát hiện hóa đơn dùng lại |
| **B6. Đối chiếu mục đích ↔ hàng hóa (R6)** | **Có** | GLM 5.2 | Suy luận ngữ nghĩa: mục đích vay có khớp hàng hóa/dịch vụ không |
| B7. Sinh báo cáo 3 mức + dẫn nguồn | Không | — | Tổng hợp kết quả theo rule |

**Hai chế độ chạy — lưu ý khi chấm/verify:**
- `mode=live` → **gọi LLM thật** tại B3/B4/B6. Lỗi tại bước nào thì fallback về logic Python cho bước đó. Cần cấu hình key trong `.env`.
- `mode=mock` (mặc định) → **không gọi LLM**, chạy hoàn toàn bằng rule engine để demo luồng end-to-end offline, ổn định, không cần key.

> Điểm gọi LLM nằm ở `agent/llm_client.py` (`extract_json()` dùng model fast, `reason()` dùng model reasoning) và được các bước `step3_classify.py`, `step4_extract.py`, `step6_crosscheck.py` sử dụng khi `mode=live`.

## Ba ràng buộc bắt buộc
- **Dữ liệu giả lập/ẩn danh** — KHÔNG dùng hồ sơ thật của MSB. Toàn bộ dữ liệu trong `data_mock/` là mock.
- **Con người quyết định** — agent chỉ đưa ra "kết quả kiểm tra sơ bộ", không kết luận duyệt/từ chối.
- **Mọi phát hiện phải dẫn nguồn** — mỗi điểm 🔴🟡 trỏ về tài liệu + trang + vị trí.

## Kiến trúc

```
WEB DASHBOARD (web/)  ──REST──►  AGENT SERVICE (main.py → api/ + agent/)  ──►  GreenNode MaaS
                                        │                                       (GLM 5.2 / Qwen Flash)
                                        └──►  Dữ liệu mô phỏng (config/ + data_mock/)
```

Orchestrator chạy 7 bước Luồng 1:
1. Lấy ngữ cảnh hồ sơ (đọc `khoan_vay.json`)
2. Lấy tài liệu (mock ECM)
3. Phân loại tài liệu — **cửa chặn**
4. Trích xuất thông tin
5. Tra lịch sử hóa đơn (phát hiện hóa đơn dùng lại)
6. Đối chiếu chéo theo `rules_P1.json` (R1–R7) + cảnh báo đặc thù (W1/W2)
7. Sinh báo cáo + dẫn nguồn

### Hai chế độ chạy (`mode`)
Truyền theo từng request; không cần restart server để đổi:
- **`mock`** — không gọi LLM. Logic Python thuần trên dữ liệu đã số hóa (`noi_dung` JSON). Chạy offline, không cần key, kết quả ổn định. Mặc định.
- **`live`** — gọi LLM thật trên GreenNode MaaS ở 3 chỗ cần đọc-hiểu/suy luận (phân loại b3, trích trường b4, đánh giá "mục đích ↔ hàng hóa" b6-R6); lỗi thì fallback về mock cho bước đó. Thiếu key khi `live` → API trả HTTP 400 rõ ràng.

> Pipeline làm việc trên **chứng từ đã số hóa (JSON)**, không đọc ảnh/PDF gốc. Nhận biết chứng từ scan độ tin cậy thấp dựa vào `voucher_type` (tra bảng), không phải AI nhìn ảnh. OCR/Vision là hướng mở rộng.

## Cấu trúc thư mục

```
giaingan-agent/
├── README.md
├── main.py                   # entrypoint AgentBase (cổng 8080) — tái dùng app trong api/
├── Dockerfile                # build image deploy
├── .dockerignore             # loại .env, state files khỏi image
├── .env.example              # KHÔNG commit key thật
├── requirements.txt
├── config/                   # cấu hình nghiệp vụ (Luồng 0)
│   ├── checklist_P1.json         # 16 mục checklist theo vùng hồ sơ
│   ├── voucher_confidence.json   # loại chứng từ → độ tin cậy
│   ├── doc_signatures.json       # dấu hiệu nhận dạng + trường bắt buộc từng loại
│   └── rules_P1.json             # quy tắc đối chiếu chéo R1–R7
├── data_mock/                # dữ liệu giả lập
│   ├── ho_so_sach/               # GN-2026-000479 (kỳ vọng 🟢 sạch)
│   ├── ho_so_co_sai_lech/        # GN-2026-000481 (kỳ vọng 🔴 rủi ro)
│   ├── ho_so_dac_thu/            # GN-2026-000476 (kỳ vọng 🟡 cần chú ý)
│   ├── ho_so_thay_the/           # bộ chứng từ thay thế/bổ sung cho demo luồng thay thế
│   ├── khoan_vay.json            # header khoản vay (số tiền đề nghị, khách hàng...)
│   └── lich_su_hoa_don.json      # có sẵn hóa đơn trùng (điểm nhấn demo)
├── agent/                    # 7 bước + orchestrator + llm_client
├── api/                      # FastAPI: /health /requests /check /batch
├── web/                      # dashboard (index.html + app.js, gọi API)
└── agentbase/                # skill deploy lên GreenNode AgentBase
```

## Chạy lại từ đầu

### 1. Chuẩn bị môi trường
```bash
cd giaingan-agent
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Cấu hình key (chỉ cần khi chạy `live`)
```bash
cp .env.example .env
# Điền GREENNODE_API_BASE, GREENNODE_API_KEY, model vào .env
# Để RUN_MODE=mock nếu chỉ demo luồng, không cần key.
```

### 3. Chạy API (local)
```bash
uvicorn api.main:app --reload --port 8000
```
> Deploy AgentBase dùng `main.py` (cổng 8080): `python main.py` hoặc `uvicorn main:app --host 0.0.0.0 --port 8080`.

### 4. Thử nghiệm
```bash
# Kiểm tra 1 hồ sơ (mock)
curl -X POST http://localhost:8000/check -H "Content-Type: application/json" \
  -d '{"ho_so_id": "GN-2026-000481", "mode": "mock"}'

# Chạy AI thật (cần key trong .env)
curl -X POST http://localhost:8000/check -H "Content-Type: application/json" \
  -d '{"ho_so_id": "GN-2026-000481", "mode": "live"}'

# Hậu kiểm theo lô → bảng xếp hạng rủi ro
curl -X POST http://localhost:8000/batch -H "Content-Type: application/json" -d '{"mode":"mock"}'
```

Kết quả kỳ vọng (mock):

| Hồ sơ | Nhóm | Mức tổng thể |
|---|---|---|
| GN-2026-000479 | sạch | 🟢 sạch (7 xanh) |
| GN-2026-000476 | đặc thù | 🟡 cần chú ý (W1 hóa đơn scan mờ, W2 giải ngân một phần) |
| GN-2026-000481 | có sai lệch | 🔴 rủi ro (lệch số tiền, sai người thụ hưởng, hóa đơn dùng lại...) |

## Endpoints

| Method | Path | Việc |
|---|---|---|
| GET | `/health` | Trả 200 (bắt buộc cho AgentBase runtime) |
| GET | `/requests` | Danh sách YCGN cho dashboard (metadata, không chạy agent) |
| POST | `/check` | Chạy 7 bước cho 1 hồ sơ. Body: `{ "ho_so_id", "mode", "tai_lieu_thay_the"? }` |
| POST | `/batch` | Hậu kiểm theo lô. Body: `{ "ho_so_ids"?, "mode" }` |

### Luồng thay thế/bổ sung chứng từ
`POST /check` nhận thêm `tai_lieu_thay_the` (danh sách tài liệu TNTD upload). Nếu có, agent merge vào hồ sơ gốc **theo `ma_checklist`** (trùng mã = thay thế, mã mới = bổ sung) rồi chạy lại 7 bước. Hồ sơ gốc trên đĩa **không bị thay đổi**. Web hiển thị kết quả gốc và kết quả sau thay thế cạnh nhau để so sánh 🔴 → 🟢. Bộ file mẫu ở `data_mock/ho_so_thay_the/`.

## Deploy lên GreenNode AgentBase
Xem `agentbase/README.md`. Tóm tắt: mở Docker Desktop → export `GREENNODE_CLIENT_ID/SECRET` → chạy `/agentbase-wizard` (framework Basic) → deploy → lấy endpoint. Container chạy cổng 8080, có `GET /health`. Artifact deploy (`main.py`, `Dockerfile`, `.dockerignore`) đã có sẵn trong repo.

## Lưu ý
- Chưa cấu hình `.env` thì agent chạy ở **chế độ mock** để demo luồng end-to-end.
- Việc thay hệ thống thật (ECM/Core/BPM) bằng dữ liệu mô phỏng phải nêu rõ trong pitch.
- `.env`, `.agentbase-state.json`, `.greennode.json` không commit và không đóng vào image.
