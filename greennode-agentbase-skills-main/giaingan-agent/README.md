# Trợ lý kiểm tra hồ sơ giải ngân (MVP Hackathon)

Multi-step agent đọc bộ hồ sơ giải ngân → xác thực loại tài liệu → trích xuất → đối chiếu chéo theo quy tắc → sinh báo cáo có dẫn nguồn. Phạm vi demo: **2 loại giải ngân P1 và P3**.

- **P1** — Giải ngân thanh toán hàng hóa, dịch vụ có hóa đơn (16 mục checklist). Trọng tâm: so khớp giá trị chứng từ (hóa đơn ↔ hợp đồng ↔ công nợ ↔ UNC).
- **P3** — Thanh toán lương chuyển khoản (15 mục checklist). Trọng tâm: đối chiếu tập hợp (bảng lương ↔ lô chuyển khoản, từng dòng người hưởng).

> Tài liệu thiết kế gốc: `../../giaingan-flow.md`, `../../giaingan-build-guide.md`, `../../GN-Danhmuc.md`.

## Ba ràng buộc bắt buộc

1. **Dữ liệu giả lập/ẩn danh** — không dùng hồ sơ thật của MSB. Mọi dữ liệu trong `data_mock/` là mô phỏng.
2. **Con người quyết định** — agent chỉ ra "kết quả kiểm tra sơ bộ", không kết luận duyệt/từ chối.
3. **Mọi phát hiện phải dẫn nguồn** — mỗi điểm 🔴🟡 trỏ về tài liệu + trang + vị trí.

## Kiến trúc

```
web/ (Next.js dashboard) ──REST──> api/main.py (FastAPI)
                                        │
                                   agent/orchestrator.py
                                   [1]context [2]load [3]classify(CỬA CHẶN)
                                   [4]extract [5]history [6]crosscheck [7]report
                                        │                    │
                              llm_client (GreenNode MaaS)   config/ + data_mock/
```

Ánh xạ 4 tầng kiến trúc:
- `web/` = WEB DASHBOARD
- `api/` = REST API
- `agent/` = AGENT SERVICE (orchestrator 7 bước)
- `agent/llm_client.py` = cầu nối GreenNode MaaS (GLM 5.2 + Qwen Flash)
- `config/` + `data_mock/` = tầng dữ liệu mô phỏng (thay ECM/Core/BPM)
- `agentbase/` = skill deploy lên GreenNode AgentBase

## Bốn trạng thái kết quả

| Ký hiệu | Nghĩa |
|---|---|
| 🟢 | Đã đối chiếu khớp |
| 🟡 | Cần chú ý, có thể có lý do hợp lệ |
| 🔴 | Lệch chắc chắn, phải xử lý trước khi submit |
| ⚪ | Chưa kiểm tra được (tài liệu nguồn chưa xác thực được đúng loại / thiếu trường) |

## Chạy local

```bash
cp .env.example .env        # điền GREENNODE_API_KEY, endpoint MaaS
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000
```

- `POST /check` — kiểm tra 1 hồ sơ (Luồng 1).
- `POST /batch` — hậu kiểm theo lô (Luồng 3), trả bảng xếp hạng rủi ro.

## Deploy lên AgentBase

Xem `agentbase/README.md`. Dùng các skill GreenNode ở repo cha (`/agentbase-wizard`, `/agentbase-deploy`).

## Cấu trúc thư mục

```
giaingan-agent/
├── config/          # quy tắc nghiệp vụ (Luồng 0) cho P1 + P3
├── data_mock/       # dữ liệu giả lập: hồ sơ, khoản vay, lịch sử
├── agent/           # 7 bước Luồng 1 + orchestrator + llm_client
├── api/             # FastAPI: /check, /batch
├── web/             # dashboard (Next.js/React)
└── agentbase/       # hướng dẫn deploy qua skill GreenNode
```
