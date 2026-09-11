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
│   ├── ho_so_bien/
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
│   └── routes.py                   # POST /check (Luồng 1), POST /batch (Luồng 3)
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
- `ho_so_co_sai_lech/` — cài sẵn lỗi: lệch số tiền (500tr vs 450tr), sai người thụ hưởng, **hóa đơn dùng lại**, thiếu biên bản đối chiếu công nợ, file khai sai loại.
- `ho_so_sai_loai/` — **bắt buộc có**: 1 file khai ở mục Giấy nhận nợ nhưng nội dung là loại khác, 1 file đúng loại nhưng thiếu trang và thiếu trường bắt buộc, 1 file ngoài checklist. Dùng để kiểm chứng cửa chặn ở bước 3: mục ra 🟠, quy tắc phụ thuộc ra ⚪, **không được ra 🟢**.
- `ho_so_bien/` — nhiều hóa đơn/1 lần GN, giải ngân một phần, làm tròn, scan mờ, 1 tài liệu cho 2 mục.
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

### Bước C — Code agent + 4 luồng + web

Đây là phần lõi. Chia rõ theo từng luồng của `giaingan-flow.md`.

**C1. Bảy bước Luồng 1 (`agent/step1..7` + `orchestrator.py`):**

| File | Vai trò | Model |
|---|---|---|
| `step1_context.py` | Lấy ngữ cảnh: loại GN, checklist đã sinh, file đã có, số tiền, điều kiện PD (đọc `khoan_vay.json`) | — |
| `step2_load_docs.py` | Đọc file từ `data_mock/` qua interface `DocumentSource` (sau này thay bằng ECM API) | — |
| `step3_classify.py` | **Cửa chặn.** Lớp 1 nhận dạng loại (16 mục P1 + `ngoai_checklist`), lớp 2 kiểm `truong_bat_buoc` theo `doc_signatures.json`. Trả về 3 trạng thái + danh sách `muc_khong_xac_thuc[]` | Qwen Flash |
| `step4_extract.py` | Chỉ chạy trên mục 🟢 ở bước 3. Trích trường cần đối chiếu, gắn `do_tin_cay` theo voucherType | Qwen/GLM |
| `step5_history.py` | Tra `lich_su_hoa_don.json` — phát hiện hóa đơn dùng lại (điểm nhấn) | — |
| `step6_crosscheck.py` | Áp `rules_P1.json`, tính từng cặp, gắn 🟢🟡🔴. Rule có nguồn thuộc `muc_khong_xac_thuc[]` → trả ⚪ kèm lý do | GLM |
| `step7_report.py` | Sinh JSON kết quả + diễn giải, mỗi điểm kèm `nguon={tài liệu,trang,vị trí}`, **đếm riêng số nội dung ⚪** làm chỉ số độ phủ + câu chốt "không kết luận đủ điều kiện" | GLM |
| `orchestrator.py` | Nối 7 bước, nhận 1 hồ sơ → trả kết quả | — |

**C2. Ba luồng — làm ở đâu:**

| Luồng | Bản chất | Hiện thực ở đâu | MVP làm gì |
|---|---|---|---|
| **Luồng 1** — kiểm tra sơ bộ 1 hồ sơ | Chạy 7 bước trên | `orchestrator.py` + `POST /check` | Bắt buộc, đầy đủ 7 bước |
| **Luồng 2** — Checker rà soát | Hiển thị lại kết quả gốc + Maker đã xử lý gì | Ở **web** (không cần code agent mới) | Mức hiển thị vết xử lý (đánh dấu đã xác nhận/bổ sung/bỏ qua) |
| **Luồng 3** — hậu kiểm theo lô | Chạy lại bước 1–6 cho N hồ sơ, cho điểm rủi ro, xếp hạng | `POST /batch` gọi `orchestrator` vòng lặp | Chạy 100–200 hồ sơ mock → bảng xếp hạng |

> Chỉ Luồng 1 và Luồng 3 cần logic agent. Luồng 2 chủ yếu là UI + lưu trạng thái. Không cần dựng 3 service riêng.
>
> Vòng cập nhật quy tắc (flow mục 3.6) không phải một luồng và không demo được — nó cần dữ liệu thật từ pilot. Ở MVP chỉ cần nút đánh dấu đúng/sai/không rõ trên mỗi phát hiện, ghi vào log để làm đầu vào về sau.

**C3. API (`api/routes.py`, build-guide Bước 2.5):**
- `POST /check` — body: id hồ sơ (hoặc bộ file) → trả kết quả 7 bước (JSON 3 mức + dẫn nguồn).
- `POST /batch` — chạy lô → trả bảng xếp hạng rủi ro.
- `GET /health` — trả 200 (bắt buộc cho AgentBase runtime).
- Các route này gắn vào app trong `main.py`.

**C4. Web dashboard (`web/`, build-guide Bước 2.5):**
- Màn hình 1: danh sách yêu cầu giải ngân (đọc từ mock).
- Màn hình 2: chi tiết 1 yêu cầu → bộ hồ sơ theo checklist + nút **"Kiểm tra sơ bộ"** → gọi `POST /check`.
- Màn hình 3: kết quả 3 mức 🟢🟡🔴, click điểm 🔴 mở **2 trang tài liệu cạnh nhau** + khoanh số liệu.
- Màn hình 4: hậu kiểm theo lô → bảng xếp hạng (gọi `POST /batch`).
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
| "Cảnh báo sai nhiều thì Maker bỏ qua hết?" | Đúng, đó là chỉ số theo dõi sát nhất. Xử lý bằng phân tầng bắt buộc/điều kiện, ngưỡng dung sai làm tròn, và Luồng 4 phản hồi để điều chỉnh quy tắc |
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

