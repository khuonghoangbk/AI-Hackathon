# web/ — Dashboard demo Maker/Checker

Dashboard cho trợ lý kiểm tra hồ sơ giải ngân, viết bằng **HTML/CSS/JS thuần** (không cần
build, không cần npm). Web KHÔNG đọc thẳng `data_mock/`, cũng KHÔNG gọi thẳng `agent/` —
chỉ nói chuyện với `api/` qua REST.

## File
- `index.html` — layout + CSS (3 tab, toggle Mock/AI thật, khu vực upload hồ sơ thay thế, 2 cột kết quả gốc/thay thế, modal 2 trang).
- `app.js` — logic gọi API và render (không hardcode dữ liệu); merge tài liệu thay thế phía client trước khi gửi, đồng bộ kết quả về Tab 1.

## Luồng dữ liệu

```
web/ (index.html + app.js)  ──REST──►  api/main.py (FastAPI)  ──►  agent/orchestrator  ──►  data_mock/ + config/
```

## Ba tab và các tương tác

Giao diện có **3 tab**: (1) Danh sách yêu cầu giải ngân, (2) Chi tiết & Kiểm tra sơ bộ, (3) Hậu kiểm theo lô. Bảng dưới liệt kê từng tương tác trong mỗi tab.

| Tab | Tương tác | Gọi API | Hiển thị |
|---|---|---|---|
| **1 · Danh sách** | Mở tab | `GET /requests` | Bảng mã YCGN, KH, loại GN, số tiền, số tài liệu; cột "Kết quả trợ lý" |
| **1 · Danh sách** | Nút "Chạy nhanh cả danh sách (batch) để hiện màu" | `POST /batch {mode}` | Điền màu 🟢🟡🔴 vào cột "Kết quả trợ lý" cho cả danh sách |
| **1 · Danh sách** | Click một dòng | (đổi tab, chưa gọi agent) | Mở Tab 2 cho hồ sơ đó |
| **2 · Chi tiết** | Nút "▶ Kiểm tra sơ bộ" | `POST /check {ho_so_id, mode}` | Bảng phân loại tài liệu + kết quả 7 bước ở cột **Hồ sơ gốc** |
| **2 · Chi tiết** | Chọn file `.json` + "▶ Kiểm tra sơ bộ trên hồ sơ thay thế" | `POST /check {ho_so_id, mode, tai_lieu_thay_the}` | Kết quả ở cột **Hồ sơ sau thay thế**, cạnh cột gốc để so sánh 🔴→🟢 |
| **2 · Chi tiết** | Click điểm 🔴/🟡 | (client-side, đọc `nguon`) | Modal 2 trang tài liệu cạnh nhau, khoanh số liệu |
| **3 · Hậu kiểm lô** | Nút "▶ Chạy hậu kiểm lô" | `POST /batch {mode}` | KPI + bảng xếp hạng rủi ro |
| **3 · Hậu kiểm lô** | Click một dòng | `POST /check {ho_so_id, mode}` | Mở lại chi tiết hồ sơ đó (Tab 2) |

> Kết quả chạy `/check` (gốc hoặc sau thay thế) và `/batch` được đồng bộ ngược về cột "Kết quả trợ lý" ở Tab 1, giữ trong suốt phiên làm việc.

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
