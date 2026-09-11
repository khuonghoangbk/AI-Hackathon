# Hướng dẫn Bước 2 — Xây dựng sản phẩm trên GreenNode
## Trợ lý kiểm tra hồ sơ giải ngân (MVP cho Hackathon)

> Tài liệu này hướng dẫn cụ thể cách hiện thực hóa ý tưởng trong `giaingan.md` + `giaingan-flow.md` thành sản phẩm demo chạy được trên nền tảng GreenNode, đủ điều kiện nộp bài (Demo + Repo + Pitch) và tranh giải Best Use of GreenNode.

---

## 0. Khung tư duy trước khi code

Sản phẩm này **không phải chatbot**, mà là một **multi-step agent** đọc hồ sơ → trích xuất → đối chiếu chéo theo quy tắc → sinh báo cáo có dẫn nguồn. Kiến trúc phải phản ánh đúng 7 bước của Luồng 1 trong `giaingan-flow.md`.

Ba ràng buộc bắt buộc tuân thủ (từ thể lệ + tài liệu ý tưởng):
- **Dữ liệu giả lập/ẩn danh** — KHÔNG dùng hồ sơ thật của MSB. Tự sinh bộ hồ sơ mock.
- **Con người quyết định** — agent chỉ ra "kết quả kiểm tra sơ bộ", không kết luận duyệt/từ chối.
- **Mọi phát hiện phải dẫn nguồn** — mỗi điểm 🔴🟡 phải trỏ về tài liệu + trang + vị trí.

Phạm vi MVP (chốt theo `giaingan.md` mục 8): **1 loại giải ngân P1 — "Giải ngân thanh toán cho hàng hóa, dịch vụ có hóa đơn"**, checklist 16 mục, 3 vùng hồ sơ.

---

## 1. Bộ công cụ và vai trò

Ba bộ công cụ team cần chuẩn bị, và vai trò của từng cái trong các bước của guide này.

### Cách nói ngắn để nhớ
- **Claude Code / Codex / OpenCode** = người thợ viết code và bấm nút deploy (qua prompt).
- **Docker Desktop** = máy đóng gói sản phẩm để mang lên cloud.
- **GitHub** = kho lưu và nơi nộp sản phẩm.

Ba công cụ bổ sung cho nhau, không thay thế nhau: dùng coding agent để tạo ra code, Docker để đóng gói code đó, GitHub để lưu trữ và nộp code đó.

### Sơ đồ tổng thể

```
Claude Code/Codex/OpenCode  ──►  viết code + chạy skill deploy (Bước 2.2 → 2.6)
        │                              │
        │ prompt "deploy lên AgentBase"│
        ▼                              ▼
   GitHub repo  ◄── commit code    Docker Desktop ──► build & push container
   (nộp bài + README)              (Bước 2.6, nền cho AgentBase)
                                        │
                                        ▼
                              GreenNode AgentBase (public endpoint)
```

### 1.1. GitHub Account
Nơi lưu và nộp mã nguồn — là **1 trong 3 hạng mục bắt buộc** khi submit (Demo + Repo + Pitch).

| Dùng ở bước | Vai trò |
|---|---|
| Bước 2.1 (Setup) | Tạo repo theo cấu trúc ở mục 5 (`giaingan-agent/`) |
| Bước 2.2 – 2.5 | Commit từng phần: config, 7 bước agent, API, dashboard |
| Bước 2.6 | Chứa skill AgentBase import từ repo GreenNode |
| Mục 9 (Checklist) | README hướng dẫn chạy lại từ đầu; rà `git history`, dùng `.env.example` thay vì commit `.env` |

### 1.2. Docker Desktop
Engine đóng gói ứng dụng thành container — cơ chế đằng sau **Bước 2.6 (Deploy lên AgentBase)**.

| Dùng ở bước | Vai trò |
|---|---|
| Bước 2.6, ý 5 | Skill AgentBase tự "Docker build & push" Agent Service (FastAPI) thành image, push lên registry, chạy trên cloud |
| Kiểm thử local | Chạy thử agent trong container trước khi đẩy cloud, đảm bảo "tái lập được từ repo" |

Lưu ý thực tế: phần lớn build/push được skill AgentBase tự động hóa (không phải tự viết Dockerfile), nhưng **Docker Desktop phải đang chạy** thì lệnh Docker mới thực thi được. Trên Windows, mở Docker Desktop trước khi chạy bước deploy.

### 1.3. Claude Code / Codex / OpenCode (coding agent — vibe code)
Công cụ lập trình bằng AI: mô tả yêu cầu bằng ngôn ngữ tự nhiên, công cụ viết code. Đây là môi trường chính xuyên suốt các bước code và deploy.

| Dùng ở bước | Vai trò |
|---|---|
| Bước 2.2 – 2.5 | Sinh code cho `llm_client.py`, 7 file `step1`–`step7`, `orchestrator.py`, API FastAPI, dashboard |
| Bước 2.6 (Deploy) | Prompt "Import skill từ repo GreenNode vào folder agent" và "Triển khai agent này trên GreenNode AgentBase"; công cụ chạy skill, hỏi Client ID/Secret, chọn model + runtime, tự build & push |
| Cấu hình model | Trỏ về endpoint MaaS OpenAI-compatible để dùng model GreenNode được cấp (theo hướng dẫn "Thêm model được cấp trong sự kiện" ở WS1) |

---

## 2. Kiến trúc tổng thể trên GreenNode

```
┌─────────────────────────────────────────────────────────────┐
│  WEB DASHBOARD (Next.js/React → deploy Vercel hoặc AgentBase) │
│  - Upload bộ hồ sơ  - Xem kết quả 3 mức 🟢🟡🔴                 │
│  - Xem 2 trang tài liệu cạnh nhau, khoanh vùng số liệu        │
│  - Nút "Kiểm tra sơ bộ" + màn hình hậu kiểm theo lô           │
└───────────────────────────┬─────────────────────────────────┘
                            │ REST API
┌───────────────────────────▼─────────────────────────────────┐
│  AGENT SERVICE (Python FastAPI) — deploy GreenNode AgentBase │
│  Orchestrator chạy 7 bước Luồng 1:                            │
│  [1] Lấy ngữ cảnh hồ sơ   [2] Lấy tài liệu                    │
│  [3] Phân loại tài liệu   [4] Trích xuất thông tin            │
│  [5] Tra lịch sử hóa đơn  [6] Đối chiếu chéo                  │
│  [7] Sinh báo cáo + dẫn nguồn                                 │
└───────┬───────────────────────────────────┬─────────────────┘
        │ OpenAI-compatible API             │
┌───────▼──────────────┐          ┌─────────▼──────────────────┐
│  GreenNode MaaS       │          │  Dữ liệu mô phỏng (JSON/DB) │
│  - GLM 5.2: đối chiếu │          │  - Rule checklist (P1)      │
│    suy luận, đọc HĐ    │          │  - Danh mục loại tài liệu   │
│  - Qwen Flash: OCR,   │          │  - Thông tin khoản vay mock │
│    phân loại nhanh    │          │  - Lịch sử hóa đơn đã dùng  │
└──────────────────────┘          └─────────────────────────────┘
```

**Vì sao chọn thế này:** MVP không có API ECM/Core/BPM thật (xem ràng buộc ở `giaingan-flow.md` mục 9). Nên MVP thay các hệ thống đó bằng dữ liệu mô phỏng, còn phần agent + đối chiếu là phần lõi thật. Điều này phải nêu rõ trong pitch, đúng khuyến nghị "nêu rõ từ đầu, không để giám khảo tự phát hiện".

---

## 3. Chọn model MaaS theo từng bước

Kỹ năng AgentBase yêu cầu chọn model theo use case. Phân bổ đề xuất:

| Bước | Tác vụ | Model đề xuất | Lý do |
|---|---|---|---|
| [3] Phân loại tài liệu | Xác định file có đúng loại đã khai | Qwen Flash 3.6 | Nhanh, phân loại/OCR tốt, rẻ token |
| [4] Trích xuất thông tin | Đọc số tiền, bên bán/mua, số HĐ, hóa đơn | Qwen Flash 3.6 (bản số) / GLM 5.2 (bản scan khó) | Bản số dễ đọc; scan mờ cần model mạnh hơn |
| [6] Đối chiếu chéo | Suy luận quan hệ giữa các tài liệu, phù hợp mục đích | GLM 5.2 | Cần reasoning, ngữ cảnh dài |
| [7] Sinh báo cáo | Diễn giải kết quả, viết điểm cần chú ý | GLM 5.2 | Chất lượng ngôn ngữ, mạch lạc |

Gọi qua chuẩn OpenAI-compatible. Đổi model chỉ bằng 1 dòng config — tận dụng để so sánh chất lượng khi demo.

---

## 4. Chuẩn bị dữ liệu nghiệp vụ (Luồng 0)

Ba nhóm dữ liệu đã có sẵn từ file nghiệp vụ, chỉ cần chuyển thành file cấu hình. Nhóm thứ tư phải xây mới.

### 3.1. Checklist cho P1 (16 mục)

Danh sách tài liệu xem `GN-Danhmuc.md` mục 1. Bảng dưới đây dùng để tạo `config/checklist_P1.json`, **khóa theo mã checklist BPM** — đây là khóa nghiệp vụ duy nhất trợ lý dùng để phân loại, trích xuất và đối chiếu:

| Vùng hồ sơ | Mã checklist BPM | Tên tài liệu | Bắt buộc |
|---|---|---|---|
| Hồ sơ chung | 3471 | Giấy nhận nợ (*) | Có |
| Hồ sơ chung | 3472 | UNC/Chứng từ thể hiện thanh toán | Có |
| Hồ sơ chung | 34250 | Hồ sơ chung khác | Điều kiện |
| Hồ sơ mục đích vay | 34245 | Hồ sơ khác | Điều kiện |
| Hồ sơ mục đích vay | 34231 | Hợp đồng kinh tế/Đơn đặt hàng... có xác nhận bên bán (*) | Có |
| Hồ sơ mục đích vay | 3455 | Hóa đơn | Có |
| Hồ sơ mục đích vay | 3458 | Biên bản đối chiếu công nợ/Giấy đề nghị thanh toán bên bán | Có |
| Hồ sơ nguồn thu | 34246 | Hợp đồng trong nước/Hợp đồng ngoại thương | Điều kiện |
| Hồ sơ nguồn thu | 34247 | BCT xuất khẩu | Điều kiện |
| Hồ sơ nguồn thu | 34248 | Biên bản đối chiếu công nợ | Điều kiện (cùng loại với 3458) |
| Hồ sơ nguồn thu | 34249 | Biên bản giao nhận hàng hóa | Điều kiện |
| Hồ sơ nguồn thu | 3475 | Phương án kinh doanh | Điều kiện |
| Hồ sơ nguồn thu | 3476 | Cam kết chuyển tiền về | Điều kiện |
| Hồ sơ nguồn thu | 3477 | Ủy quyền thu nợ | Điều kiện |
| Hồ sơ nguồn thu | 3478 | Đề nghị tài trợ | Điều kiện |
| Hồ sơ nguồn thu | 3479 | Hồ sơ nguồn thu khác | Điều kiện |

> Mã loại tài liệu ECM (`documentType`) không đưa vào config nghiệp vụ. Nó chỉ là định danh trong kho lưu trữ, dùng khi tích hợp đọc/đẩy file thật với ECM. Mapping đầy đủ mã checklist ↔ V1 ↔ ECM tra ở `GN-Danhmuc-full.md`.
>
> Lưu ý nghiệp vụ quan trọng (từ 4 điểm cần xác minh): các mục vùng Nguồn thu đánh `x` cho cả 18 loại giải ngân — MVP xử lý theo hướng **"theo điều kiện phê duyệt"**, KHÔNG báo thiếu hàng loạt. Đây là điểm dễ làm cảnh báo mất giá trị nếu làm sai.
>
> Mục cùng loại tài liệu (ví dụ Biên bản đối chiếu công nợ ở cả vùng mục đích vay `3458` và vùng nguồn thu `34248`) → nhận diện là "một tài liệu có thể thỏa mãn cả hai mục", không tính thiếu.

### 3.2. Từ điển loại chứng từ (voucherType) → độ tin cậy

Tạo `config/voucher_confidence.json`:

```json
{
  "1": {"ten": "Bản số",            "do_tin_cay": "cao"},
  "3": {"ten": "Bản ký số attach",  "do_tin_cay": "cao"},
  "2": {"ten": "Bản attach vật lý", "do_tin_cay": "thap", "canh_bao": true},
  "4": {"ten": "Bản mềm attach",    "do_tin_cay": "tuy_chat_luong"}
}
```

### 3.3. Bộ quy tắc đối chiếu chéo (PHẢI XÂY MỚI) — cho P1

Tạo `config/rules_P1.json`. Đây là phần lõi tạo giá trị, lấy trực tiếp từ bảng trong `giaingan-flow.md` mục 3:

```json
[
  {"id": "R1", "a": "so_tien_de_nghi",   "b": "so_tien_chi_dan_tt",  "op": "bang",         "muc_khi_sai": "do"},
  {"id": "R2", "a": "so_tien_de_nghi",   "b": "tong_gia_tri_hoa_don","op": "khong_vuot",   "muc_khi_sai": "do"},
  {"id": "R3", "a": "nguoi_thu_huong",   "b": "ben_ban_hoa_don",     "op": "trung",        "muc_khi_sai": "do"},
  {"id": "R4", "a": "khach_hang_vay",    "b": "ben_mua_hoa_don",     "op": "trung",        "muc_khi_sai": "do"},
  {"id": "R5", "a": "gia_tri_hop_dong",  "b": "tong_gia_tri_hoa_don","op": "hoa_don_khong_vuot_hd", "muc_khi_sai": "vang"},
  {"id": "R6", "a": "muc_dich_su_dung",  "b": "noi_dung_hang_hoa",   "op": "phu_hop",      "muc_khi_sai": "vang"},
  {"id": "R7", "a": "hoa_don_trong_ho_so","b": "lich_su_giai_ngan",  "op": "khong_trung",  "muc_khi_sai": "do"}
]
```

Thêm ngưỡng dung sai làm tròn (ví dụ ±1.000 VND) để không báo cảnh báo sai với chênh lệch nhỏ.

### 3.4. Dấu hiệu nhận dạng tài liệu (PHẢI XÂY MỚI) — phục vụ cửa chặn ở bước 3

Tạo `config/doc_signatures.json`. Đây là cấu hình để trả lời "file này có đúng loại đã khai hay không" — chi tiết thiết kế ở `giaingan-flow.md` mục 3.7.

```json
{
  "3471": {
    "ten": "Giấy nhận nợ",
    "dau_hieu_nhan_dang": ["giấy nhận nợ", "khế ước nhận nợ", "hợp đồng tín dụng cụ thể"],
    "truong_bat_buoc": ["so_tien", "loai_tien", "ngay_nhan_no", "ten_khach_hang", "limit_id"],
    "nguong_dat": { "diem_tin_cay_toi_thieu": 0.75, "so_truong_bat_buoc_toi_thieu": 4 }
  },
  "3455": {
    "ten": "Hóa đơn",
    "dau_hieu_nhan_dang": ["hóa đơn giá trị gia tăng", "hóa đơn bán hàng", "mẫu số", "ký hiệu"],
    "truong_bat_buoc": ["so_hoa_don", "ngay_lap", "mst_ben_ban", "mst_ben_mua", "tong_tien_thanh_toan"],
    "nguong_dat": { "diem_tin_cay_toi_thieu": 0.80, "so_truong_bat_buoc_toi_thieu": 4 }
  }
}
```

Khóa của `doc_signatures.json` là **mã checklist BPM**, khớp với khóa của `checklist_P1.json`.

Hai điều bắt buộc khi hiện thực:
- **Không dùng tên file** làm căn cứ phân loại. Nhãn khai báo là mục checklist mà file được tải lên.
- **Hạ ngưỡng theo `voucherType`**: file scan vật lý (2) và bản mềm (4) đọc kém hơn, áp cùng ngưỡng với bản số sẽ sinh cảnh báo sai hàng loạt.

---

## 5. Cấu trúc repo đề xuất

```
giaingan-agent/
├── README.md                      # cách chạy lại từ đầu (bắt buộc để nộp)
├── .env.example                   # KHÔNG commit key thật
├── requirements.txt
├── config/
│   ├── checklist_P1.json
│   ├── voucher_confidence.json
│   ├── doc_signatures.json        # dấu hiệu nhận dạng + trường bắt buộc từng loại
│   └── rules_P1.json
├── data_mock/                     # dữ liệu giả lập
│   ├── ho_so_sach/                # nhóm 1: không lỗi
│   ├── ho_so_co_sai_lech/         # nhóm 2: lỗi cài sẵn
│   ├── ho_so_bien/                # nhóm 3: tình huống biên
│   ├── khoan_vay.json             # thông tin khoản vay mock
│   └── lich_su_hoa_don.json       # có sẵn 1 hóa đơn trùng
├── agent/
│   ├── llm_client.py              # gọi GreenNode MaaS (OpenAI-compatible)
│   ├── step1_context.py           # lấy ngữ cảnh hồ sơ
│   ├── step2_load_docs.py         # đọc file (mock ECM)
│   ├── step3_classify.py          # phân loại tài liệu (Qwen)
│   ├── step4_extract.py           # trích xuất thông tin (Qwen/GLM)
│   ├── step5_history.py           # tra lịch sử hóa đơn
│   ├── step6_crosscheck.py        # đối chiếu chéo theo rules_P1
│   ├── step7_report.py            # sinh báo cáo 3 mức + dẫn nguồn
│   └── orchestrator.py            # nối 7 bước
├── api/
│   └── main.py                    # FastAPI: POST /check, POST /batch
├── web/                           # dashboard (Next.js/React)
└── agentbase/                     # skill deploy (import từ repo GreenNode)
```

---

## 6. Các bước thực hiện tuần tự

### Bước 2.1 — Setup môi trường GreenNode
1. Đăng nhập GreenNode AI Portal (`https://aiplatform.console.greennode.ai/`), đổi mật khẩu.
2. Lấy API Key MaaS + Client ID/Client Secret (BTC gửi qua email).
3. Lưu vào `.env` (dùng `.env.example` làm mẫu, không commit key):
   ```
   GREENNODE_API_BASE=https://<maas-endpoint>/v1
   GREENNODE_API_KEY=sk-...
   MODEL_REASONING=glm-5.2
   MODEL_FAST=qwen-flash-3.6
   ```

### Bước 2.2 — Dựng LLM client (OpenAI-compatible)
Dùng thư viện `openai` trỏ `base_url` về endpoint MaaS. Một client, đổi model qua tham số. Viết 2 hàm tiện ích: `extract_json()` (trả về JSON có schema) và `reason()` (đối chiếu/diễn giải).

### Bước 2.3 — Nạp cấu hình nghiệp vụ (Luồng 0)
Load 3 file config ở mục 4. Dựng bảng tra: `loại giải ngân → checklist (mã checklist BPM) → trường cần trích → cặp đối chiếu`.

### Bước 2.4 — Hiện thực 7 bước (Luồng 1)
- **[1] Context**: đọc metadata hồ sơ (loại GN, limit ID, số tiền đề nghị, danh sách file + mã checklist + voucherType đã khai).
- **[2] Load docs**: MVP đọc từ `data_mock/`; trừu tượng hóa qua interface `DocumentSource` để sau này thay bằng ECM API.
- **[3] Classify — CỬA CHẶN, không phải một ghi chú.** Hai lớp:
  - *Lớp 1* nhận dạng loại: tập ứng viên là 16 mục checklist P1 cộng nhãn `ngoai_checklist`, không phân loại trên toàn bộ danh mục. Model trả JSON có schema `{loai_phu_hop_nhat, diem_tin_cay, can_cu[]}`.
  - *Lớp 2* kiểm cấu trúc: có tìm được `truong_bat_buoc` của loại đó theo `doc_signatures.json` hay không.
  - Kết quả là **ba trạng thái**: 🟢 đã xác thực → sang bước 4; 🟠 chưa xác thực được (sai loại / ngoài checklist / không đọc được / thiếu trường) → **bỏ qua bước 4 cho mục đó**; 🔴 chưa có file.
  - Hàm phải trả về danh sách `muc_khong_xac_thuc[]` để bước 6 dùng làm điều kiện chặn. Không được để bước 4 và 6 tự quyết định.
- **[4] Extract**: chỉ chạy trên các mục 🟢 ở bước 3. Trích các trường: số tiền đề nghị, khách hàng vay, người thụ hưởng, số/ngày/giá trị hóa đơn, bên bán, số/giá trị hợp đồng, mục đích vốn. Gắn `do_tin_cay` theo voucherType.
- **[5] History**: tra `lich_su_hoa_don.json` — đây là **điểm nhấn demo** (phát hiện hóa đơn dùng lại). Bắt buộc chuẩn bị 1 case trùng.
- **[6] Cross-check**: áp `rules_P1.json`, tính kết quả từng cặp, gắn mức 🟢🟡🔴. Quy tắc nào có nguồn A hoặc B thuộc `muc_khong_xac_thuc[]` thì **trả ⚪ `chua_kiem_tra_duoc` kèm lý do và mục gây ra**, tuyệt đối không trả 🟢.
- **[7] Report**: sinh JSON kết quả + diễn giải, mỗi điểm kèm `nguồn = {tài liệu, trang, vị trí}`. Phần tổng hợp **đếm riêng số quy tắc ⚪** và nêu lý do, vì đó là chỉ số độ phủ của lần kiểm tra. Kèm câu chốt "Trợ lý không kết luận hồ sơ đủ điều kiện giải ngân."

### Bước 2.5 — API + Dashboard
- `POST /check` (1 hồ sơ) → trả kết quả 7 bước.
- `POST /batch` (Luồng 3 hậu kiểm) → chạy 100–200 hồ sơ mock, trả bảng xếp hạng rủi ro.
- Dashboard: upload → hiển thị 3 mức, click điểm 🔴 mở 2 trang tài liệu cạnh nhau + khoanh số liệu.

### Bước 2.6 — Deploy lên AgentBase
1. Import skill: prompt trong vibe code — "Import skill từ repo `https://github.com/vngcloud/greennode-agentbase-skills` vào folder agent".
2. Prompt: "Triển khai agent này trên GreenNode AgentBase".
3. Nhập Client ID + Client Secret.
4. Chọn API Key + model + runtime (2x4 hoặc 4x4 GB — chọn Recommended).
5. Skill tự Docker build & push → cấp public endpoint.

Dashboard có thể deploy Vercel/Firebase, gọi vào endpoint agent (được thể lệ cho phép).

---

## 7. Dữ liệu mô phỏng cần chuẩn bị (quyết định chất lượng demo)

Đúng 3 nhóm theo `giaingan-flow.md` mục 11:

| Nhóm | Nội dung cài sẵn | Mục đích |
|---|---|---|
| Hồ sơ sạch | Mọi thông tin khớp | Đo tỷ lệ cảnh báo sai (phải ra 🟢) |
| Hồ sơ có sai lệch biết trước | Lệch số tiền (500tr vs 450tr), sai người thụ hưởng, **hóa đơn dùng lại**, thiếu biên bản đối chiếu công nợ, file khai sai loại | Chứng minh giá trị phát hiện |
| Hồ sơ tình huống biên | Nhiều hóa đơn/1 lần GN, giải ngân một phần, làm tròn số, scan mờ, 1 tài liệu cho 2 mục checklist | Kiểm tra độ bền quy tắc |

Chỉ demo hồ sơ sạch thì không chứng minh được gì. Nhóm 2 và 3 là phần ăn điểm.

Định dạng file mock: dùng PDF/ảnh tự tạo (hoặc JSON mô phỏng nội dung tài liệu kèm số trang), tên/số liệu là giả lập hoàn toàn.

---

## 8. Kịch bản demo (bám tiêu chí R × I × C)

1. Upload 1 bộ hồ sơ có sai lệch → agent ra kết quả trong dưới 1 phút.
2. Mở điểm 🔴 chênh lệch số tiền → 2 trang tài liệu hiện cạnh nhau, khoanh đúng 2 con số (Maker tự xác nhận, không phải tin agent).
3. Trình diễn phát hiện **hóa đơn đã dùng ở lần giải ngân trước** — wow-moment, thứ Maker khó thấy bằng mắt.
4. Chuyển sang hậu kiểm theo lô → bảng xếp hạng rủi ro trên toàn bộ hồ sơ trong kỳ (độ phủ 100%).
5. Trình bày số đo trên tập có sai lệch biết trước: tỷ lệ phát hiện đúng / bỏ sót / cảnh báo sai.

---

## 9. Checklist hoàn thành Bước 2

- [ ] Có API Key MaaS + Client ID/Secret, lưu trong `.env` (không commit)
- [ ] 4 file config nghiệp vụ (checklist_P1, voucher_confidence, doc_signatures, rules_P1)
- [ ] Bộ quy tắc đối chiếu chéo cho P1 đã xây (7 cặp)
- [ ] 3 nhóm dữ liệu mock đã chuẩn bị, có case hóa đơn trùng
- [ ] Có case file khai sai loại; kiểm chứng mục ra 🟠 và quy tắc phụ thuộc ra ⚪, không ra 🟢
- [ ] 7 bước Luồng 1 chạy end-to-end
- [ ] Luồng 3 hậu kiểm theo lô ra bảng xếp hạng
- [ ] Dashboard hiển thị 3 mức + dẫn nguồn + xem 2 trang cạnh nhau
- [ ] Agent deploy trên GreenNode AgentBase, có public endpoint
- [ ] README hướng dẫn chạy lại từ đầu
- [ ] Không có dữ liệu thật MSB; đã ghi rõ phần nào là mock

---

## 10. Rủi ro cần lưu ý khi build

| Rủi ro | Xử lý |
|---|---|
| Báo thiếu tài liệu hàng loạt do hiểu sai mục "theo điều kiện phê duyệt" | Phân tầng bắt buộc/điều kiện trong checklist_P1, mặc định vùng nguồn thu là "điều kiện" |
| Cảnh báo sai nhiều → mất niềm tin | Thêm ngưỡng dung sai làm tròn; luôn "báo chưa kiểm tra được" thay vì đoán |
| Model đọc sai bản scan | Gắn cờ độ tin cậy thấp, đề nghị Maker xác nhận, không tự tin kết luận |
| Bị coi là "công cụ OCR" | Nhấn phần đối chiếu chéo + phát hiện hóa đơn dùng lại, không dừng ở nhận dạng |
| **Trích xuất trên tài liệu sai loại rồi kết luận khớp** | Bước 3 là cửa chặn: mục 🟠 thì không chạy bước 4, quy tắc phụ thuộc trả ⚪. Đây là rủi ro lớn nhất của chính công cụ (`giaingan-flow.md` mục 3.7) |
| Kết luận "sai loại" cho bản scan mờ | Phân biệt *sai loại* (🔴) và *không đọc được* (🟡). Bản mờ báo "chưa kiểm tra được", không báo sai loại |
| Lộ key trong repo | Dùng `.env`, rà git history trước khi public |
```
