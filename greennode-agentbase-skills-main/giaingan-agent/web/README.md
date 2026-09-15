# Web Dashboard

Bản MVP là trang tĩnh (`index.html` + `app.js` + `styles.css`), gọi thẳng REST API của Agent Service. Không cần build tool — mở file hoặc serve tĩnh là chạy.

## Chạy nhanh

1. Khởi động API (ở thư mục `giaingan-agent/`):
   ```bash
   uvicorn api.main:app --reload --port 8000
   ```
2. Serve dashboard (thư mục `web/`):
   ```bash
   python -m http.server 5173
   ```
   Mở http://localhost:5173

## Trỏ về endpoint khác

Mặc định gọi `http://localhost:8000`. Khi deploy Agent lên AgentBase, đặt biến trước khi load `app.js`:

```html
<script>window.API_BASE = "https://<agent-endpoint>";</script>
<script src="app.js"></script>
```

## Nâng cấp lên Next.js (bản đầy đủ)

Dashboard bản đầy đủ dự kiến dùng Next.js/React để bổ sung:
- Upload bộ hồ sơ (gọi `POST /check-inline`).
- Xem 2 trang tài liệu cạnh nhau, khoanh vùng số liệu tại điểm 🔴 (dẫn nguồn).
- Màn hình hậu kiểm theo lô với lọc/sắp xếp.

Khi chuyển, giữ nguyên hợp đồng REST API hiện tại; chỉ thay tầng trình bày.
