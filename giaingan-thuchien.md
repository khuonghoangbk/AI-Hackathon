# Kế hoạch thực hiện — Trợ lý kiểm tra hồ sơ giải ngân (Hackathon GreenNode)

> Tài liệu này liệt kê **các bước phải làm để hoàn thành bài thi**, làm ở đâu, dùng skill gì, đặt file vào thư mục nào. Bám theo `giaingan.md`, `giaingan-flow.md`, `giaingan-build-guide.md` và bộ skill trong `greennode-agentbase-skills-main/`.
>
> Phạm vi MVP: **1 loại giải ngân P1** (thanh toán hàng hóa/dịch vụ có hóa đơn, checklist 16 mục). Có thể mở thêm P3 (thanh toán lương) nếu còn thời gian.

---

## 0. Ba hạng mục phải nộp và chúng đến từ đâu

| Hạng mục nộp | Là cái gì | Sinh ra ở bước nào |
|---|---|---|
| **4a — Link Demo** | URL công khai chạy được. Gồm 2 phần: (1) **public endpoint của Agent** trên GreenNode AgentBase; (2) **web dashboard** demo thao tác Maker/Checker (deploy Vercel/Firebase, hoặc chạy local khi pitch) | Endpoint: Bước D (deploy). Web: Bước C |
| **4b — GitHub repo** | Toàn bộ source: config nghiệp vụ + agent (7 bước) + api + web + README chạy lại từ đầu | Commit dần từ Bước A → E |
| **4c — Pitch deck (PDF)** | Bài trình bày: bài toán, giải pháp, kiến trúc, kết quả, hướng mở rộng. Bám tiêu chí chấm **R × I × C** | Bước F |

> Thiếu bất kỳ 1 trong 3 mục → **không được đưa vào vòng đánh giá**. Hạn nộp EOD 23/09, không gia hạn (theo `instruction.md`).

Ghi nhớ 3 ràng buộc xuyên suốt (mất điểm nếu vi phạm):
1. **Dữ liệu giả lập** — không dùng hồ sơ thật MSB.
2. **Con người quyết định** — agent chỉ ra "kết quả kiểm tra sơ bộ", không kết luận duyệt.
3. **Mọi phát hiện phải dẫn nguồn** — tài liệu + trang + vị trí.

---

## 1. Cấu trúc thư mục tổng thể (repo 4b)

Toàn bộ dự án đặt trong 1 thư mục repo, ví dụ `giaingan-agent/`. Đây là bộ khung sẽ commit lên GitHub.

```
giaingan-agent/                     ← thư mục gốc repo, git init ở đây
├── README.md                       # cách chạy lại từ đầu (BẮT BUỘC để nộp)
├── .env.example                    # mẫu biến môi trường, KHÔNG commit .env thật
├── .dockerignore                   # loại .env, .greennode.json khỏi image
├── requirements.txt
├── Dockerfile                      # do wizard sinh; runtime chạy cổng 8080, có /health
├── main.py                         # entrypoint AgentBase (GreenNodeAgentBaseApp)
│
├── config/                         # ← LUỒNG 0: quy tắc nghiệp vụ (knowledge base)
│   ├── checklist_P1.json           # 16 mục checklist theo vùng hồ sơ
│   ├── voucher_confidence.json     # 4 loại chứng từ → độ tin cậy
│   ├── doc_signatures.json         # dấu hiệu nhận dạng + trường bắt buộc từng loại tài liệu
│   └── rules_P1.json               # bộ quy tắc đối chiếu chéo DC-P1-xx + DC-C-xx
│
├── data_mock/                      # ← dữ liệu giả lập (3 nhóm)
│   ├── ho_so_sach/
│   ├── ho_so_co_sai_lech/
│   ├── ho_so_dac_thu/
│   ├── khoan_vay.json              # thông tin khoản vay mock (thay Core/T24)
│   └── lich_su_hoa_don.json        # có sẵn 1 hóa đơn trùng (điểm nhấn demo)
│
├── agent/                          # ← 7 bước Luồng 1
│   ├── llm_client.py               # gọi GreenNode MaaS (OpenAI-compatible)
│   ├── step1_context.py
│   ├── step2_load_docs.py
│   ├── step3_classify.py
│   ├── step4_extract.py
│   ├── step5_history.py
│   ├── step6_crosscheck.py
│   ├── step7_report.py
│   └── orchestrator.py             # nối 7 bước, dùng chung cho Luồng 1 và 3
│
├── api/
│   └── routes.py                   # POST /check (Luồng 1), POST /batch (Luồng 2)
│
├── web/                            # ← dashboard demo Maker/Checker
│   └── (Next.js/React hoặc index.html tĩnh gọi API)
│
├── pitch/                          # ← 4c: pitch deck
│   ├── pitch-giaingan.pdf          # bản nộp (BẮT BUỘC là PDF)
│   ├── pitch-giaingan.pptx         # bản nguồn để sửa
│   └── screenshots/                # ảnh chụp demo dùng trong slide
│
└── .agentbase-state.json           # do wizard sinh, KHÔNG sửa tay
```

### Luồng dữ liệu giữa các tầng (ai gọi ai, ai đọc gì)

Nguyên tắc phân tầng: **web không đọc thẳng `data_mock/`, cũng không gọi thẳng `agent/`**. Web chỉ nói chuyện với `api/` qua REST; `api/` gọi `orchestrator`; `orchestrator` mới đọc `data_mock/` + `config/`. Giữ đúng ranh giới này thì khi thay mock bằng API thật (Core/ECM), phần web không phải sửa.

```
┌──────────────────────────────────────────────┐
│  web/  (Next.js/React) — dashboard Maker       │
│  Tab 1 Danh sách  ── GET  /requests ──┐        │
│  Tab 2 Chi tiết   ── POST /check    ──┤        │
│  Tab 4 Hậu kiểm   ── POST /batch    ──┤        │
└───────────────────────────────────────┼────────┘
                                         │ REST (JSON)
┌────────────────────────────────────────▼───────┐
│  api/  (FastAPI) — main.py                       │
│  GET /health · GET /requests · POST /check /batch│
└───────────────────────────┬─────────────────────┘
                            │ gọi hàm Python
┌────────────────────────────▼─────────────────────┐
│  agent/orchestrator.py                            │
│  check_one() → 7 bước Luồng 1                      │
│  check_batch() → lặp Luồng 2, xếp hạng rủi ro      │
│    step1 → step2 → step3(cửa chặn) → step4         │
│      → step5 → step6 → step7                       │
└──────────┬───────────────────────────┬────────────┘
           │ đọc dữ liệu YCGN            │ đọc quy tắc nghiệp vụ
┌──────────▼──────────┐      ┌───────────▼─────────────┐
│  data_mock/         │      │  config/                 │
│  khoan_vay.json     │      │  checklist_P1.json       │
│  ho_so_*/*.json     │      │  doc_signatures.json     │
│  lich_su_hoa_don    │      │  rules_P1.json           │
│  (mock Core/ECM)    │      │  voucher_confidence.json │
└─────────────────────┘      └──────────────────────────┘
           │
           │ gọi khi RUN_MODE=live
┌──────────▼──────────────────────────┐
│  GreenNode MaaS (OpenAI-compatible)  │
│  GLM 5.2 · Qwen Flash 3.6            │
└──────────────────────────────────────┘
```

Một YCGN được ghép từ 2 nguồn qua khóa `ho_so_id` (= mã YCGN, dạng `GN-2026-xxx`): header (KH, số tiền đề nghị, loại GN, mục đích) ở `khoan_vay.json`; danh sách tài liệu + nội dung ở `ho_so_*/*.json`. `config/` KHÔNG chứa dữ liệu YCGN — nó là bộ quy tắc nghiệp vụ (knowledge base) dùng chung cho mọi hồ sơ.

> Lưu ý về `main.py` và `api/`: AgentBase Runtime yêu cầu container mở **cổng 8080** và có endpoint **`GET /health` trả 200**. `main.py` là entrypoint mà wizard tạo; ta gắn các route `/check`, `/batch` vào chính app đó (hoặc để `api/routes.py` được `main.py` import). Không tự dựng server riêng lệch chuẩn.

---

## 2. Trình tự thực hiện (A → G)

Thứ tự đề xuất: chuẩn bị nghiệp vụ trước (không cần cloud), rồi mới scaffold + code + deploy.

### Bước A — Chuẩn bị nghiệp vụ và dữ liệu (Luồng 0 + dữ liệu mock)

**Làm ở đâu:** máy local, trong `config/` và `data_mock/`. Chưa cần GreenNode.

**A1. Nạp quy tắc nghiệp vụ = tạo 4 file trong `config/`** (đây chính là "Luồng 0"):
- `checklist_P1.json` — 16 mục, **khóa theo mã checklist BPM**. Danh sách tài liệu lấy từ `GN-Danhmuc.md`; bảng đầy đủ ở `giaingan-build-guide.md` mục 3.1. Mỗi mục ghi: vùng hồ sơ, mã checklist BPM, tên, mức bắt buộc (`bat_buoc` / `dieu_kien`). Mã ECM không đưa vào config nghiệp vụ.
- `voucher_confidence.json` — 4 loại voucherType → độ tin cậy (bản số/ký số = cao; scan vật lý = thấp).
- `doc_signatures.json` — **phải xây mới**, phục vụ cửa chặn ở bước 3. Khóa theo mã checklist BPM (khớp `checklist_P1.json`). Mỗi mục ghi: dấu hiệu nhận dạng, `truong_bat_buoc`, `truong_nen_co`, ngưỡng đạt (điểm tin cậy tối thiểu + số trường bắt buộc tối thiểu), ngưỡng hạ theo voucherType. Xem `giaingan-flow.md` mục 3.7.
- `rules_P1.json` — bộ quy tắc đối chiếu chéo. Lấy các cặp DC-P1-01..08 (ít nhất 7 cặp lõi) từ `giaingan-flow.md` mục 3.3, cộng vài quy tắc chung DC-C-xx. Mỗi rule: `id`, nguồn A, nguồn B, phép so sánh, mức 🔴/🟡, ngưỡng dung sai. **Mỗi rule phải khai rõ mục checklist nguồn** để bước 6 biết khi nào phải trả ⚪ thay vì 🟢.

> "Knowledge base" của agent chính là 4 file JSON này + data_mock. Không phải vector DB — agent đọc trực tiếp file config làm bảng tra. Đơn giản, giải thích được, đúng tinh thần "dùng lại quy tắc đã ban hành".

**A2. Tạo dữ liệu mock trong `data_mock/`** — 3 nhóm (đây là phần quyết định chất lượng demo):
- `ho_so_sach/` — mọi thông tin khớp (đo tỷ lệ cảnh báo sai, phải ra 🟢).
- `ho_so_co_sai_lech/` — cài sẵn lỗi: lệch số tiền (500tr vs 450tr), sai người thụ hưởng, **hóa đơn dùng lại**, thiếu biên bản đối chiếu công nợ, và **file khai sai loại** (khai ở mục Giấy nhận nợ nhưng nội dung là loại khác) để kiểm chứng cửa chặn bước 3: mục ra 🟠, quy tắc phụ thuộc ra ⚪, **không được ra 🟢**.
- `ho_so_dac_thu/` — hồ sơ hợp lệ nhưng phức tạp: nhiều hóa đơn/1 lần GN, giải ngân một phần, làm tròn, scan mờ, 1 tài liệu cho 2 mục. Dùng đo tỷ lệ cảnh báo sai ở vùng xám.
- `khoan_vay.json` — thay Core/T24 (limit ID, số tiền, KH, điều kiện phê duyệt).
- `lich_su_hoa_don.json` — **bắt buộc có 1 case hóa đơn trùng** để demo Bước 5.

Định dạng file tài liệu mock: PDF/ảnh tự tạo, hoặc JSON mô phỏng nội dung kèm số trang. Tất cả số liệu/tên là giả.

**Commit:** `config/` + `data_mock/` lên GitHub.

---

### Bước B — Setup GreenNode + LLM client

**B1. Setup môi trường (build-guide Bước 2.1):**
- Đăng nhập GreenNode AI Portal, đổi mật khẩu.
- Lấy **Client ID + Client Secret** (IAM) và **API Key MaaS** (BTC gửi email).
- Đặt vào biến môi trường / `.env` (dùng `.env.example` làm mẫu, không commit `.env`):
  ```
  GREENNODE_CLIENT_ID=...
  GREENNODE_CLIENT_SECRET=...
  LLM_BASE_URL=https://maas-llm-aiplatform-hcm.api.vngcloud.vn/v1
  LLM_API_KEY=...
  MODEL_REASONING=glm-5.2
  MODEL_FAST=qwen-flash-3.6
  ```
  > `GREENNODE_CLIENT_ID/SECRET` khi deploy sẽ được runtime **tự inject** vào container — trong `.env` chỉ cần cho lúc chạy local. LLM key thì cấu hình qua skill ở Bước D.

**B2. Dựng LLM client (`agent/llm_client.py`, build-guide Bước 2.2):**
- Dùng thư viện `openai`, trỏ `base_url` về `LLM_BASE_URL`.
- 2 hàm tiện ích: `extract_json()` (trích xuất có schema, dùng Qwen Flash) và `reason()` (đối chiếu/diễn giải, dùng GLM 5.2).
- Model phân bổ: phân loại/trích xuất → Qwen Flash; đối chiếu/báo cáo → GLM 5.2 (build-guide mục 3).

---

### Bước C — Code agent (2 luồng) + web

Đây là phần lõi. Hai luồng cần agent (Luồng 1 và Luồng 2) dùng chung 7 bước ở `orchestrator.py`; vai trò Checker và vòng phản hồi nằm ở web (xem C2).

**C1. Bảy bước Luồng 1 (`agent/step1..7` + `orchestrator.py`):**

**Phạm vi dữ liệu — điểm quan trọng cần nắm trước:** cả hai chế độ đều làm việc trên **dữ liệu chứng từ đã số hóa dạng JSON** (trường `noi_dung` của từng tài liệu trong hồ sơ — mô phỏng kết quả sau khi hệ thống nguồn/ECM đã trích xuất). **Pipeline không đọc file ảnh/PDF gốc ở bất kỳ bước nào.** Kể cả `mode="live"`, LLM cũng chỉ đọc phần `noi_dung` JSON này, không phải nhận diện ảnh. OCR/Vision đọc ảnh gốc là hướng mở rộng, chưa nằm trong phạm vi bản này.

Mỗi bước dùng AI (Qwen/GLM) đều có **2 nhánh chọn theo tham số `mode`** truyền vào lúc gọi:
- `mode="mock"` — **không gọi LLM.** Dùng logic Python thuần trên dữ liệu `data_mock` (so khớp chuỗi, đếm trường, so sánh số) — vẫn đọc chính các trường `noi_dung` số hóa như trên. Chạy offline, không cần key, kết quả ổn định và tái lập được — dùng để dựng luồng, test, quay demo dự phòng.
- `mode="live"` — **gọi LLM thật** trên GreenNode MaaS để đọc-hiểu/suy luận trên cùng phần `noi_dung` số hóa đó (không phải đọc ảnh). Nếu LLM lỗi/không parse được thì tự **fallback về logic mock** cho bước đó (trừ trường hợp thiếu key/endpoint thì báo lỗi rõ ràng, không âm thầm chạy mock).

**Khác biệt mock ↔ live nằm ở đâu:** AI (live) chỉ tham gia đúng 3 chỗ cần đọc-hiểu/suy luận — nhận dạng loại tài liệu (b3), trích trường từ nội dung (b4), đánh giá "mục đích vốn có phù hợp hàng hóa không" (b6-R6). Toàn bộ **đối chiếu số học/so khớp (R1–R5, R7)** và các bước tra bảng (b1, b2, b5, `do_tin_cay`) **luôn là logic xác định bằng Python ở cả hai chế độ** — cùng data, cùng kết quả, không phụ thuộc AI.

Bảng dưới tách rõ **mock làm gì**, **AI (live) làm gì**, và **input** của từng bước. Chỉ có **3 bước dùng AI** (đánh dấu 🤖); còn lại là Python xác định ở cả hai chế độ. Input của mọi bước là **dữ liệu đã số hóa** (JSON), không có bước nào đọc ảnh/PDF.

| Bước | Mock làm gì (Python) | AI (live) làm gì | Input |
|---|---|---|---|
| `step1_context.py`<br>**Lấy ngữ cảnh hồ sơ** | Đọc `khoan_vay.json` lấy ngữ cảnh: loại GN, checklist, số tiền đề nghị, điều kiện PD | — không dùng AI | `khoan_vay.json` |
| `step2_load_docs.py`<br>**Nạp danh sách tài liệu** | Nạp tài liệu từ `data_mock/` qua interface `DocumentSource` (sau thay bằng ECM API) | — không dùng AI | Record hồ sơ (JSON) |
| 🤖 `step3_classify.py`<br>**Phân loại tài liệu (cửa chặn)** | **Cửa chặn.** Nhận dạng loại tài liệu bằng **so khớp chuỗi dấu hiệu** (`_diem_nhan_dang`) + đếm `truong_bat_buoc` theo `doc_signatures.json` → 3 trạng thái + `muc_khong_xac_thuc[]` | **Qwen Flash đọc `noi_dung` chấm điểm tin cậy 0–1 "đây có đúng loại tài liệu X không"** (`_diem_nhan_dang_live`). Lỗi → fallback mock | `noi_dung` (JSON) đã số hóa |
| 🤖 `step4_extract.py`<br>**Trích trường nghiệp vụ** | Đọc thẳng các trường nghiệp vụ từ `noi_dung` JSON (số tiền, số HĐ, bên bán/mua…). Gắn `do_tin_cay` bằng **tra `voucher_type` → `voucher_confidence.json`** (đây là tra bảng, **không phải AI**) | **Qwen/GLM trích các trường bắt buộc từ `noi_dung`** (`_extract_live`) rồi merge. Lỗi → fallback mock | `noi_dung` (JSON) đã số hóa |
| `step5_history.py`<br>**Tra lịch sử hóa đơn** | Tra `lich_su_hoa_don.json` bằng khóa `so_hoa_don` → phát hiện hóa đơn dùng lại (điểm nhấn) | — không dùng AI | `so_hoa_don` + `lich_su_hoa_don.json` |
| 🤖 `step6_crosscheck.py`<br>**Đối chiếu chéo + gắn màu** | Áp `rules_P1.json`, tính từng cặp, gắn 🟢🟡🔴; nguồn thuộc `muc_khong_xac_thuc[]` → ⚪. **R1–R5, R7 là so sánh số/chuỗi thuần Python.** Thêm cảnh báo đặc thù 🟡: **W1** hóa đơn `do_tin_cay="thap"`, **W2** giải ngân một phần | **Chỉ R6:** GLM suy luận "mục đích vốn có phù hợp nội dung hàng hóa không". Lỗi → fallback mock. R1–R5/R7 và W1/W2 **không dùng AI** | Trường đã trích (b4) + rules |
| `step7_report.py`<br>**Sinh báo cáo kết quả** | Tổng hợp kết quả 7 bước → JSON 3 mức, mỗi điểm kèm `nguon`, đếm ⚪ làm độ phủ + câu chốt "không kết luận đủ điều kiện" | — không dùng AI (diễn giải văn xuôi có thể thêm GLM sau) | Kết quả các bước |
| `orchestrator.py`<br>**Điều phối 7 bước** | Nối 7 bước, nhận `(ho_so_id, mode)` → trả kết quả. `mode=None` → mặc định từ `RUN_MODE` | — điều phối, không dùng AI | — |

> Vì sao chỉ vài chỗ dùng AI: các phép so khớp số/chuỗi (số tiền, tên bên bán/mua, hóa đơn trùng) là **logic xác định** — dùng Python vừa chính xác vừa giải thích được, tái lập được, có dẫn nguồn (đúng yêu cầu kiểm toán ngân hàng), không nên giao cho LLM. AI chỉ dùng ở chỗ cần đọc-hiểu/suy luận: nhận dạng loại tài liệu (b3), đọc trường từ nội dung tự do (b4), đánh giá "mục đích vốn có phù hợp hàng hóa không" (b6-R6).
>
> **Ranh giới cần nói rõ khi demo:** trợ lý làm việc trên **chứng từ đã số hóa**, không đọc ảnh/PDF gốc. Việc nhận biết chứng từ scan độ tin cậy thấp là do hệ thống nguồn đã phân loại `voucher_type`, trợ lý tra bảng để cảnh báo "loại rủi ro cao, cần người xác thực" — **không phải AI nhìn ảnh phán đoán độ mờ**. Trợ lý **hỗ trợ Maker/Checker, không tự kết luận** hồ sơ đủ điều kiện giải ngân. OCR/Vision đọc ảnh gốc + đấu nối core banking/e-invoice là **hướng mở rộng** ngoài phạm vi bản này.

**C2. Hai luồng cần agent — làm ở đâu:**

| Luồng | Bản chất | Hiện thực ở đâu | MVP làm gì |
|---|---|---|---|
| **Luồng 1** — kiểm tra sơ bộ 1 hồ sơ | Chạy 7 bước trên | `orchestrator.py` + `POST /check` | Bắt buộc, đầy đủ 7 bước |
| **Luồng 2** — hậu kiểm theo lô | Chạy lại bước 1–6 cho N hồ sơ, cho điểm rủi ro, xếp hạng | `POST /batch` gọi `orchestrator` vòng lặp | Chạy 100–200 hồ sơ mock → bảng xếp hạng |

> Chỉ **hai luồng này cần logic agent**. Không cần dựng nhiều service riêng — cả hai dùng chung `orchestrator`.
>
> **Vai trò Checker (kiểm soát kép Maker/Checker):** không phải một luồng agent riêng, mà là **lớp phê duyệt trên web** — Checker xem lại kết quả kiểm tra sơ bộ (Luồng 1) cùng vết Maker đã xử lý (đã xác nhận / bổ sung / bỏ qua). Chỉ là UI + lưu trạng thái, **không cần code agent mới**. Vẫn giữ đúng nguyên tắc phân tách chức năng của ngân hàng, nhưng không nâng thành luồng ngang hàng Luồng 1/2.
>
> **Luồng 3 — vòng phản hồi cập nhật quy tắc:** không phải một luồng agent và không demo được — nó cần dữ liệu thật từ pilot. Ở MVP chỉ cần nút đánh dấu đúng/sai/không rõ trên mỗi phát hiện, ghi vào log để làm đầu vào điều chỉnh quy tắc về sau.

**C3. API (`api/main.py`, build-guide Bước 2.5):**
- `POST /check` — body `{ "ho_so_id": "GN-2026-xxx", "mode": "mock"|"live"|null }` → trả kết quả 7 bước (JSON 3 mức + dẫn nguồn) kèm `mode` đã dùng.
- `POST /batch` — body `{ "ho_so_ids": [...]|null, "mode": ... }` → chạy lô → trả bảng xếp hạng rủi ro.
- `GET /requests` — danh sách YCGN cho Tab 1 (metadata, không chạy agent).
- `GET /health` — trả 200 (bắt buộc cho AgentBase runtime).
- Các route này gắn vào app trong `main.py`.

> **Tham số `mode` (per-request):** truyền theo từng lời gọi để bật/tắt AI thật mà không phải restart server. `mode=null` → lấy mặc định từ biến `RUN_MODE` trong `.env`. Khi `mode="live"` mà chưa cấu hình `GREENNODE_API_KEY/API_BASE` → API trả **HTTP 400** với thông báo rõ ("chưa cấu hình key"), không âm thầm chạy mock. Đây là cơ chế backend cho toggle "Chế độ AI thật" ở web (xem C4).

**C4. Web dashboard (`web/`, build-guide Bước 2.5):**
Web gọi 4 endpoint đã dựng ở C3. Base URL lấy từ biến `NEXT_PUBLIC_API_BASE` (local `http://localhost:8000`, khi deploy trỏ vào endpoint agent). Mô tả từng màn hình theo góc **"vào màn hình gọi gì / bấm gì gọi gì"**:

**Toggle "Chế độ AI thật" (áp cho mọi màn hình):**
- Một switch ở thanh trên (ví dụ: `○ Mock (nhanh, offline) │ ● AI thật (GreenNode)`). Lưu vào state chung của app.
- Mỗi lần gọi `POST /check` hoặc `POST /batch`, đính kèm `mode` theo trạng thái toggle: bật → `"live"`, tắt → `"mock"`.
- Khi bật AI thật, nên hiện chú thích nhẹ (tốn token · cần mạng · chậm hơn) để giám khảo không nhầm mock là kết quả AI. Nếu API trả HTTP 400 (chưa cấu hình key) thì hiện thông báo lỗi thay vì kết quả.
- Dùng khi pitch: chạy `mock` để trình luồng nhanh, gạt sang `live` cho 1 hồ sơ để chứng minh GLM/Qwen làm việc thật (ăn điểm Best Use of GreenNode), có thể so sánh kết quả 2 chế độ ngay trên màn hình.

**Màn hình 1 — Danh sách yêu cầu giải ngân (Tab 1)**
- *Khi vào màn hình:* gọi `GET /requests`. Nhận về mảng YCGN, mỗi dòng gồm: `ma_ycgn` (GN-2026-xxx), `khach_hang`, `loai_giai_ngan`, `so_tien_de_nghi`, `so_tai_lieu`. Render thành bảng "Hàng đợi giải ngân".
- *Cột "Kết quả trợ lý":* lần đầu để trạng thái "Chưa kiểm tra" (endpoint `/requests` không chạy agent, chỉ trả metadata — nhẹ và nhanh). Nếu muốn hiển thị sẵn màu 🟢🟡🔴 cho cả danh sách thì gọi `POST /batch` một lần rồi map `muc_tong_the` theo `ho_so_id` vào từng dòng.
- *Khi bấm vào một dòng:* lấy `ma_ycgn` của dòng đó, chuyển sang Màn hình 2 (truyền `ma_ycgn` qua route param / state). Chưa gọi agent ở bước click này — việc chạy 7 bước để dành cho nút "Kiểm tra sơ bộ" ở Màn hình 2, tránh chạy nhầm cả loạt.

**Màn hình 2 — Chi tiết yêu cầu + Kiểm tra sơ bộ (Tab 2)**
- *Khi vào màn hình:* đã có `ma_ycgn` từ Màn hình 1. Hiển thị header hồ sơ + bộ tài liệu theo checklist. (MVP có thể dựng danh sách tài liệu từ chính response `/check`; nếu muốn hiện checklist trước khi chạy agent thì bổ sung một endpoint đọc-hồ-sơ riêng — không bắt buộc cho MVP.)
- *Khi bấm nút "Kiểm tra sơ bộ":* gọi `POST /check` với body `{ "ho_so_id": "<ma_ycgn>" }`. Trong lúc chờ, hiện trạng thái loading (agent chạy 7 bước). Nhận response gồm `report` (kết quả tổng hợp) + `buoc` (chi tiết từng bước) → chuyển/mở Màn hình 3 để render kết quả.
- *Cơ chế:* một hồ sơ = một lần `POST /check`. Kết quả nên cache theo `ho_so_id` để bấm lại không phải chạy lại agent.

**Màn hình 3 — Kết quả 3 mức + dẫn nguồn (Tab 3)**
- *Nguồn dữ liệu:* dùng lại `report` từ `POST /check` ở Màn hình 2, **không gọi API mới**. Đọc `report.muc_tong_the`, `report.thong_ke` (đếm 🟢🟡🔴 + số ⚪ + độ phủ), `report.phat_hien[]` (từng quy tắc kèm `muc`, `mo_ta`, `chi_tiet`, `nguon`), `report.hoa_don_trung_lich_su[]`, `report.tai_lieu[]` (trạng thái phân loại từng mục), `report.cau_chot`.
- *Khi bấm vào một điểm 🔴/🟡:* đọc trường `nguon` của phát hiện đó (`{tài liệu, doc_id, trang}`) để mở modal **2 trang tài liệu cạnh nhau** và khoanh số liệu. Dữ liệu trang lấy từ nội dung tài liệu đã có trong response (hoặc từ `data_mock` nếu render tĩnh). Thao tác này thuần client-side, không gọi lại agent.
- *Nút đánh dấu Đúng/Sai/Không rõ trên mỗi phát hiện (Luồng 3):* MVP chỉ lưu client-side hoặc ghi log, chưa cần endpoint riêng.

**Màn hình 4 — Hậu kiểm theo lô (Tab 3 - Luồng 2)**
- *Khi vào màn hình (hoặc bấm "Chạy hậu kiểm"):* gọi `POST /batch` với body `{}` (chạy toàn bộ hồ sơ) hoặc `{ "ho_so_ids": [...] }` (chạy tập chọn). Nhận `bang_xep_hang[]` đã sắp theo `diem_rui_ro` giảm dần, mỗi dòng có `xep_hang`, `ho_so_id`, `muc_tong_the`, `tom_tat`, `diem_rui_ro`, `thong_ke`.
- *Khi bấm vào một dòng trong bảng xếp hạng:* mở lại Màn hình 2/3 cho `ho_so_id` đó (gọi `POST /check` để xem chi tiết 7 bước), giống luồng từ Màn hình 1.

**Sơ đồ gọi API theo tương tác:**

```
Toggle AI        → set mode = "live" | "mock" (đính vào /check, /batch)
Tab 1 (mount)         → GET  /requests                   → bảng YCGN
Tab 1 (click dòng)    → (đổi màn, chưa gọi agent)         → Tab 2
Tab 2 (nút Kiểm tra)  → POST /check {ho_so_id, mode}      → report → Tab 3
Tab 3 (click 🔴/🟡)   → (client-side, đọc nguon)          → modal 2 trang
Tab 4 (mount/nút)     → POST /batch {mode}                → bảng xếp hạng rủi ro
Tab 4 (click dòng)    → POST /check {ho_so_id, mode}      → chi tiết
```

- Công nghệ: Next.js/React, hoặc `index.html` tĩnh + fetch nếu muốn nhẹ. Web gọi vào **public endpoint của agent** (xem Bước D).

---

### Bước D — Deploy agent lên AgentBase (sinh Link Demo 4a)

**Làm ở đâu:** trong vibe code (Claude Code/Codex/OpenCode) đã cài bộ skill `greennode-agentbase-skills`, mở tại thư mục `giaingan-agent/`.

**D0. Cài skill (một lần):**
```
claude plugin marketplace add vngcloud/greennode-agentbase-skills
/plugin install greennode-agentbase@greennode-agentbase
```
Đặt trước biến môi trường: `GREENNODE_CLIENT_ID`, `GREENNODE_CLIENT_SECRET`.

**D1. Chạy wizard (skill `/agentbase-wizard`) — 9 bước, đây là đường xương sống:**

| Wizard step | Việc | Ghi chú cho dự án này |
|---|---|---|
| 1. Prerequisites | Kiểm tra IAM credential | Cần Client ID/Secret đã export |
| 2. Scaffold | Sinh khung project (`main.py`, `Dockerfile`, `requirements.txt`) ngay trong CWD | Chọn framework **Basic** (agent xử lý theo request, không cần chat) |
| 3. Memory | Bộ nhớ hội thoại | **Bỏ qua** — không cần |
| 4. Identity/Auth | Auth dịch vụ ngoài | **Bỏ qua** — chỉ gọi MaaS nội bộ |
| 5. Customize code | Viết logic agent | Chỗ đưa 7 bước + `/check` `/batch` vào `main.py`/`agent/` |
| 6. Environment | Cấu hình biến môi trường | Chọn **GreenNode AI Platform** làm LLM (skill `/agentbase-llm`), tạo/chọn API key, set `LLM_MODEL`, `LLM_BASE_URL` |
| 7. Local test | `test validate` → `local` → `docker` | Test 7 bước end-to-end bằng file mock trước khi đẩy cloud |
| 8. Deploy | Build & push image, tạo runtime | Skill `/agentbase-deploy` lo Docker build/push (dùng Container Registry của AgentBase, `--from-cr`) |
| 9. Verify | Lấy endpoint URL, curl `/health` | **URL này = Link Demo 4a (phần agent)** |

**D2. Yêu cầu Docker Desktop đang chạy** trên Windows trước khi tới step 8 (skill tự chạy `docker build`).

**D3. Sau khi có endpoint ACTIVE:** cấu hình `web/` trỏ vào endpoint đó. Deploy web lên Vercel/Firebase (được thể lệ cho phép) → **Link Demo 4a hoàn chỉnh** = web + agent.

> Muốn deploy lại sau khi sửa code: chạy lại `/agentbase-deploy` (tạo version mới, endpoint DEFAULT tự trỏ sang).

---

### Bước E — Hoàn thiện để nộp

**E1. README.md** (bắt buộc): mô tả kiến trúc, cách chạy lại từ đầu (setup env → chạy local → deploy), nêu rõ phần nào là mock (Core/ECM/BPM đều mô phỏng).

**E2. Rà bảo mật:** `.env` không commit; kiểm tra `git history` không lộ key; `.dockerignore` loại `.env`, `.greennode.json`.

**E3. Chuẩn bị kịch bản demo (build-guide mục 8):**
1. Upload hồ sơ có sai lệch → agent ra kết quả < 1 phút.
2. Mở điểm 🔴 chênh số tiền → 2 trang cạnh nhau, khoanh 2 con số.
3. Trình diễn **hóa đơn dùng lại** (wow-moment).
4. Chuyển hậu kiểm theo lô → bảng xếp hạng độ phủ 100%.
5. Trình số đo trên tập có sai lệch: phát hiện đúng / bỏ sót / cảnh báo sai.

---

### Bước F — Pitch deck (hạng mục 4c)

**Làm ở đâu:** thư mục `pitch/`. Soạn bằng PowerPoint/Google Slides, **xuất PDF** để nộp. Làm sau khi có demo chạy được để chụp ảnh thật đưa vào slide.

**F1. Nguyên tắc: bám tiêu chí chấm R × I × C (tích số)**

Điểm tổng = Reach × Impact × Confident, mỗi trục thang 1–3. Vì là **tích số**, một trục yếu kéo tụt toàn bộ. Deck phải trả lời rõ cả 3 trục, không dồn hết vào phần kỹ thuật.

| Trục | BGK đánh giá | Ta lấy bằng chứng ở đâu |
|---|---|---|
| **Reach** | Ai hưởng lợi, quy mô, tần suất | 102 nhân sự Maker/Checker · 486 hồ sơ/ngày · ~121.500 hồ sơ/năm · phát sinh hằng ngày (`giaingan.md` mục 1) |
| **Impact** | AEV (giá trị kinh tế/năm), trải nghiệm, phù hợp chiến lược | Bảng tiết kiệm giờ 20/30/40% + bảng giảm tỷ lệ trả lại (`giaingan.md` mục 7) |
| **Confident** | Pain point đã xác thực, chất lượng demo, hàm lượng AI, chất lượng trình bày | Số liệu hiện trạng có thật + demo chạy trên AgentBase + số đo trên tập hồ sơ có sai lệch biết trước |

**F2. Outline đề xuất (~12 slide)**

| # | Slide | Nội dung chốt | Trục |
|---|---|---|---|
| 1 | Tiêu đề + một câu | "Để trợ lý đọc và đối chiếu hồ sơ. Để Maker/Checker tập trung vào những gì thực sự cần nghiệp vụ và phán đoán." | — |
| 2 | Bài toán | 486 hồ sơ/ngày × 45 phút = **364 giờ/ngày**; 102 nhân sự; mỗi hồ sơ 14–19 mục tài liệu; **44% hồ sơ phải trả lại/bổ sung** | R, C |
| 3 | Reach | Người hưởng lợi trực tiếp: 102 Maker/Checker TNTD. Gián tiếp: khách hàng (thời gian chờ), đơn vị kinh doanh. Tần suất: hằng ngày, ~121.500 hồ sơ/năm | **R** |
| 4 | Vì sao chưa giải quyết được | Quy tắc checklist đã có nhưng hệ thống **chỉ biết có file hay không**, không kiểm tra nội dung; đối chiếu chéo vẫn thủ công | C |
| 5 | Giải pháp | Trợ lý đọc trước, làm 5 việc: đối chiếu checklist → trích xuất → đối chiếu chéo → nêu điểm cần chú ý → phân loại mức độ | — |
| 6 | Điểm khác biệt | **Không phải công cụ OCR.** Giá trị ở bước đối chiếu chéo. Phát hiện được thứ Maker khó thấy bằng mắt: **hóa đơn đã dùng ở lần giải ngân trước** | C |
| 7 | Kiến trúc | Web dashboard → REST API → **Agent trên GreenNode AgentBase** (7 bước Luồng 1) → **GreenNode MaaS**: GLM 5.2 (đối chiếu/suy luận) + Qwen Flash 3.6 (phân loại/OCR). Nêu rõ Core/ECM/BPM là **dữ liệu mô phỏng** | C |
| 8 | Demo (ảnh thật) | Kết quả 3 mức 🟢🟡🔴 + **dẫn nguồn** + 2 trang tài liệu cạnh nhau khoanh số liệu | C |
| 9 | Impact / AEV | Giảm 30% thời gian → ~109 giờ/ngày, **~27.000 giờ/năm**; giảm trả lại 44%→30% → thêm ~51 giờ/ngày. Trình theo hướng **tăng năng lực xử lý** (486 → ~694 hồ sơ/ngày), không phải giảm nhân sự | **I** |
| 10 | Số đo độ tin cậy | Trên tập hồ sơ có sai lệch biết trước: tỷ lệ phát hiện đúng / bỏ sót / **cảnh báo sai** | **C** |
| 11 | Nguyên tắc vận hành | Con người quyết định · mọi phát hiện dẫn nguồn · không tạo cảm giác an toàn giả · dữ liệu giả lập | C |
| 12 | Lộ trình + mở rộng | GĐ1 một loại GN chạy song song → GĐ2 12 loại trong nước, đưa vào màn hình tác nghiệp → GĐ3 quốc tế + nghiệp vụ chứng từ khác. Tầm nhìn: đẩy kiểm tra lên phía trước để loại hẳn một vòng xử lý | I |

**F3. Cách trình bày phần Impact (dễ bị hỏi lại)**

- Số giờ tiết kiệm là **ước tính theo kịch bản**, phải nói rõ là kịch bản, không nói như kết quả đã đo. Mức thực tế phải đo bằng chạy song song ở Giai đoạn 1.
- Muốn ra AEV bằng tiền: `AEV = số giờ tiết kiệm/năm × đơn giá giờ công`. **Đơn giá giờ công cần lấy từ đơn vị**, không tự đặt số. Nếu chưa có, trình bày bằng **giờ công + năng lực xử lý tăng thêm** là an toàn hơn.
- Phần giá trị lớn nhất không phải tiết kiệm thời gian đọc, mà là **giảm tỷ lệ trả lại 44%** — mỗi hồ sơ đúng ngay lần đầu loại bỏ cả một vòng kiểm tra.

**F4. Ba điều phải nói rõ trong deck (nếu không, giám khảo tự phát hiện sẽ mất điểm Confident)**

1. **Phần nào là mock:** Core/T24, ECM, BPM hạn mức, kho lịch sử giải ngân đều là dữ liệu mô phỏng. Phần agent + bộ quy tắc đối chiếu là phần lõi thật.
2. **Agent không kết luận duyệt/từ chối** — chỉ ra kết quả kiểm tra sơ bộ, thẩm quyền không thay đổi.
3. **Dữ liệu hoàn toàn giả lập**, không dùng hồ sơ thật MSB.

**F5. Chuẩn bị Q&A trước (Hackday 25/09 có phần Q&A)**

| Câu hỏi khả năng cao | Hướng trả lời |
|---|---|
| "Đây có phải chỉ là OCR không?" | Không. OCR chỉ chuyển tài liệu thành dữ liệu. Giá trị nằm ở bộ quy tắc đối chiếu chéo và phát hiện hóa đơn dùng lại — thứ hiện làm thủ công |
| "Model đọc sai thì sao?" | Gắn độ tin cậy theo voucherType, bản scan → hạ mức tin cậy; báo "chưa kiểm tra được" thay vì suy đoán; mọi phát hiện có dẫn nguồn để Maker tự xác nhận |
| **"Nếu file khai là Giấy nhận nợ nhưng nội dung linh tinh thì có pass checklist không?"** | Không pass. Mục chuyển sang trạng thái thứ ba: *có file nhưng chưa xác thực được đúng loại*. Trợ lý **không trích xuất** trên mục đó, và mọi nội dung đối chiếu cần đến nó báo ⚪ chưa kiểm tra được, không báo khớp. Phần tổng hợp nêu rõ độ phủ chỉ đạt một phần. Maker có thể ghi đè nếu cho rằng trợ lý phân loại sai, và việc ghi đè được lưu vết. Có case demo cho tình huống này |
| "Vì sao không dựa vào tên file?" | Tên file không đáng tin và không được đưa vào logic. Căn cứ là mục checklist mà file được tải lên (mã checklist BPM), đối chiếu với dấu hiệu nhận dạng và trường bắt buộc của loại tài liệu đó |
| "Cảnh báo sai nhiều thì Maker bỏ qua hết?" | Đúng, đó là chỉ số theo dõi sát nhất. Xử lý bằng phân tầng bắt buộc/điều kiện, ngưỡng dung sai làm tròn, và Luồng 3 (vòng phản hồi) để điều chỉnh quy tắc |
| "Chưa có API đọc từ ECM thì triển khai kiểu gì?" | MVP dùng bộ file tải lên, trừu tượng hóa qua interface `DocumentSource` để thay bằng ECM API khi có. Đây là ràng buộc đã biết, nêu từ đầu |
| "Trách nhiệm khi agent bỏ sót?" | Trợ lý không phải mắt xích bắt buộc, không thay đổi trạng thái hồ sơ. Thẩm quyền và trách nhiệm của Maker/Checker không đổi |
| "Mở rộng sang 18 loại giải ngân mất bao lâu?" | Ba nhóm quy tắc checklist/danh mục loại tài liệu/loại chứng từ đã chuẩn hóa sẵn. Việc thêm mỗi loại chủ yếu là xây bộ quy tắc đối chiếu chéo, cần nghiệp vụ tham gia |

**F6. Xuất bản:** lưu `pitch/pitch-giaingan.pptx` (nguồn) và **xuất `pitch/pitch-giaingan.pdf`** (bản nộp). Commit cả hai lên repo để giám khảo truy được.

---

### Bước G — Nộp bài

- Nộp đủ **3 link/file**: Link Demo (4a) + GitHub repo (4b) + Pitch deck PDF (4c).
- Link nộp bài theo kênh chính thức của BTC.
- **Test link demo từ mạng ngoài** (không phải mạng nội bộ) để chắc chắn giám khảo truy cập được. Chuẩn bị tài khoản demo + hướng dẫn truy cập nếu có login.
- Nộp sớm trước hạn, không đợi phút chót.

---

## 3. Checklist hoàn thành (đối chiếu trước khi nộp)

- [ ] `config/` có 4 file: checklist_P1, voucher_confidence, doc_signatures, rules_P1 (≥7 cặp đối chiếu)
- [ ] `data_mock/` có 4 nhóm + `lich_su_hoa_don.json` có case hóa đơn trùng
- [ ] Cửa chặn bước 3 kiểm chứng được: file khai sai loại → mục 🟠, quy tắc phụ thuộc ⚪, không có 🟢 giả
- [ ] `agent/` chạy 7 bước Luồng 1 end-to-end (test local pass)
- [ ] `POST /check` và `POST /batch` hoạt động; `GET /health` trả 200
- [ ] Web hiển thị 3 mức + dẫn nguồn + xem 2 trang cạnh nhau + hậu kiểm lô
- [ ] Agent deploy trên AgentBase, có **public endpoint** (Link Demo 4a phần agent)
- [ ] Web deploy công khai, trỏ vào endpoint agent (Link Demo 4a hoàn chỉnh)
- [ ] Đã test link demo **từ mạng ngoài**, có tài khoản + hướng dẫn truy cập nếu cần login
- [ ] Repo GitHub đầy đủ + README chạy lại từ đầu (4b)
- [ ] **Pitch deck xuất PDF** trong `pitch/`, bám R × I × C, có ảnh demo thật (4c)
- [ ] Deck nêu rõ: phần nào là mock · agent không kết luận duyệt · dữ liệu giả lập
- [ ] Đã chuẩn bị Q&A cho Hackday 25/09
- [ ] Báo cáo có câu "Trợ lý không kết luận hồ sơ đủ điều kiện giải ngân"
- [ ] Không lộ key; không có dữ liệu thật MSB
- [ ] **Nộp đủ 3 hạng mục trước EOD 23/09**

---

## 4. Ánh xạ nhanh: skill nào dùng ở đâu

| Việc | Skill | Bước |
|---|---|---|
| Scaffold + test + điều phối cả vòng đời | `/agentbase-wizard` | D1 (toàn bộ) |
| Tạo/chọn LLM API key, chọn model MaaS | `/agentbase-llm` | D1 step 6 |
| Build & push Docker, tạo runtime, cấp endpoint | `/agentbase-deploy` | D1 step 8 |
| Xem log lỗi khi deploy/demo hỏng | `/agentbase-monitor` | Khi cần debug |
| (Không dùng cho MVP) memory, identity, gateway, policy | — | — |

---

## 5. Những chỗ dễ sai (nhắc lại)

- **Không báo thiếu hàng loạt:** 9 mục vùng "Hồ sơ nguồn thu" mặc định `dieu_kien`, không tính thiếu. Sai chỗ này → mọi hồ sơ đỏ lòm, cảnh báo mất giá trị.
- **Mục cùng loại tài liệu** (vd Biên bản đối chiếu công nợ ở 2 vùng: 3458 và 34248) → 1 tài liệu thỏa cả 2 mục, không tính thiếu 2 lần.
- **Dẫn nguồn mọi phát hiện** — không có phát hiện nào thiếu tài liệu+trang+vị trí.
- **Ngưỡng dung sai làm tròn** (vd ±1.000 VND) để tránh cảnh báo sai với chênh lệch nhỏ.
- **Bản scan → độ tin cậy thấp**, đề nghị Maker xác nhận, không tự tin kết luận.
- **Nêu rõ phần mock trong pitch** (Core/ECM/BPM mô phỏng), không để giám khảo tự phát hiện.
```

