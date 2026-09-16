# web/ — Dashboard demo Maker/Checker

Dashboard cho trợ lý kiểm tra hồ sơ giải ngân, viết bằng **HTML/CSS/JS thuần** (không cần
build, không cần npm). Web KHÔNG đọc thẳng `data_mock/`, cũng KHÔNG gọi thẳng `agent/` —
chỉ nói chuyện với `api/` qua REST.

## File
- `index.html` — layout + CSS (3 tab, toggle Mock/AI thật, modal 2 trang).
- `app.js` — logic gọi API và render (không hardcode dữ liệu).

## Luồng dữ liệu

```
web/ (index.html + app.js)  ──REST──►  api/main.py (FastAPI)  ──►  agent/orchestrator  ──►  data_mock/ + config/
```

## Bốn màn hình

| Màn hình | Gọi API | Hiển thị |
|---|---|---|
| Tab 1 — Danh sách YCGN | `GET /requests` | Bảng mã YCGN, KH, loại GN, số tiền, số tài liệu |
| Tab 1 — nút "Chạy nhanh" | `POST /batch` | Điền màu 🟢🟡🔴 vào cột kết quả |
| Tab 2 — Chi tiết + nút Kiểm tra sơ bộ | `POST /check {ho_so_id, mode}` | Bảng phân loại tài liệu + kết quả 7 bước |
| Tab 2 — click điểm 🔴/🟡 | (client-side) | Modal 2 trang tài liệu cạnh nhau, đọc `nguon` |
| Tab 3 — Hậu kiểm theo lô | `POST /batch {mode}` | KPI + bảng xếp hạng rủi ro |

## Toggle Mock / AI thật
Switch ở góc trên. Trạng thái được đính vào mọi lời gọi `/check`, `/batch` qua tham số `mode`
(`mock` hoặc `live`). Ô "API" cho phép đổi base URL (mặc định `http://localhost:8000`).

## Chạy local (2 bước)

**1. Chạy backend API** (thư mục `giaingan-agent/`):
```bash
python -m uvicorn api.main:app --port 8000
```

**2. Phục vụ web qua HTTP** (thư mục `giaingan-agent/web/`) — KHÔNG mở file trực tiếp vì
`fetch` bị chặn với `file://`:
```bash
python -m http.server 5500
```
Mở trình duyệt: `http://localhost:5500`

> Backend đã bật CORS (`Access-Control-Allow-Origin: *`) nên web ở cổng 5500 gọi API cổng 8000 không bị chặn.

## Deploy
Là file tĩnh nên deploy dễ (Vercel/Firebase/GitHub Pages). Sau khi deploy, sửa ô "API" (hoặc
giá trị mặc định trong `index.html`) trỏ vào **public endpoint agent** trên GreenNode AgentBase.

## Tham khảo
Giao diện tái dùng phong cách từ `demo-giaingan - Copy.html` (bản demo tĩnh ở thư mục gốc),
nhưng thay toàn bộ dữ liệu hardcode bằng `fetch` gọi API thật.
