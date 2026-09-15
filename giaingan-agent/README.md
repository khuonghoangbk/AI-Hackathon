# Trợ lý kiểm tra hồ sơ giải ngân (MVP — MSB AI Hackathon 2026)

Multi-step AI agent đọc hồ sơ giải ngân → phân loại → trích xuất → đối chiếu chéo theo quy tắc → sinh báo cáo 3 mức 🟢🟡🔴 có dẫn nguồn.

> Phạm vi MVP: 1 loại giải ngân **P1 — "Giải ngân thanh toán cho hàng hóa, dịch vụ có hóa đơn"**, checklist 16 mục, 3 vùng hồ sơ.

## Ba ràng buộc bắt buộc
- **Dữ liệu giả lập/ẩn danh** — KHÔNG dùng hồ sơ thật của MSB. Toàn bộ dữ liệu trong `data_mock/` là mock.
- **Con người quyết định** — agent chỉ đưa ra "kết quả kiểm tra sơ bộ", không kết luận duyệt/từ chối.
- **Mọi phát hiện phải dẫn nguồn** — mỗi điểm 🔴🟡 trỏ về tài liệu + trang + vị trí.

## Kiến trúc

```
WEB DASHBOARD (web/)  ──REST──►  AGENT SERVICE (api/ + agent/)  ──►  GreenNode MaaS
                                        │                              (GLM 5.2 / Qwen Flash)
                                        └──►  Dữ liệu mô phỏng (config/ + data_mock/)
```

Orchestrator chạy 7 bước Luồng 1:
1. Lấy ngữ cảnh hồ sơ
2. Lấy tài liệu (mock ECM)
3. Phân loại tài liệu — **cửa chặn**
4. Trích xuất thông tin
5. Tra lịch sử hóa đơn
6. Đối chiếu chéo theo `rules_P1.json`
7. Sinh báo cáo + dẫn nguồn

## Cấu trúc thư mục

```
giaingan-agent/
├── README.md
├── .env.example              # KHÔNG commit key thật
├── requirements.txt
├── config/                   # cấu hình nghiệp vụ (Luồng 0)
├── data_mock/                # dữ liệu giả lập 3 nhóm
├── agent/                    # 7 bước + orchestrator + llm_client
├── api/                      # FastAPI: POST /check, POST /batch
├── web/                      # dashboard (Next.js/React)
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

### 2. Cấu hình key
```bash
cp .env.example .env
# Điền GREENNODE_API_BASE, GREENNODE_API_KEY, model vào .env
```

### 3. Chạy API
```bash
uvicorn api.main:app --reload --port 8000
```

### 4. Thử nghiệm
```bash
# Kiểm tra 1 hồ sơ mock
curl -X POST http://localhost:8000/check -H "Content-Type: application/json" \
  -d '{"ho_so_id": "HS_SACH_001"}'

# Hậu kiểm theo lô
curl -X POST http://localhost:8000/batch -H "Content-Type: application/json" -d '{}'
```

## Lưu ý
- Chưa cấu hình `.env` thì agent chạy ở **chế độ mock** (không gọi LLM thật) để demo luồng end-to-end.
- Phần thay thế hệ thống thật (ECM/Core/BPM) bằng dữ liệu mô phỏng phải nêu rõ trong pitch.
