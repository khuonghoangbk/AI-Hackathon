# web-react/ — Dashboard Maker/Checker (React + Vite)

Phiên bản React của dashboard trợ lý kiểm tra hồ sơ giải ngân. Giữ nguyên chức năng và giao
diện của bản `web/` (HTML/JS thuần), nhưng tách thành component để dễ bảo trì. Vẫn chỉ nói
chuyện với `api/` qua REST — không đọc thẳng `data_mock/` hay `agent/`.

## Cấu trúc

```
web-react/
├── index.html            # entry cua Vite
├── vite.config.js        # dev server cong 5500
├── package.json
├── .env.example          # VITE_API_BASE
└── src/
    ├── main.jsx          # mount React
    ├── App.jsx           # state chung, header, tabs, goi API
    ├── styles.css        # toan bo CSS (giu nguyen tu ban vanilla)
    ├── lib/
    │   ├── api.js        # callApi, DEFAULT_API_BASE
    │   └── constants.js  # mapping muc/pill/icon, helper parse
    ├── components/
    │   ├── Pill.jsx      # KetQuaPill, MucPill
    │   ├── Toast.jsx
    │   ├── ReportColumn.jsx   # 1 cot ket qua (goc / thay the)
    │   └── CompareModal.jsx   # modal doi chieu 2 trang
    └── views/
        ├── ListView.jsx  # Tab 1
        ├── DetailView.jsx# Tab 2 (upload .json thay the)
        └── BatchView.jsx # Tab 3
```

## Luồng dữ liệu

```
web-react/ ──REST──► api/main.py (FastAPI) ──► agent/orchestrator ──► data_mock/ + config/
```

Ba tab và các API gọi vào (`/requests`, `/check`, `/batch`) giữ y hệt bản `web/`.

## Chạy local

**1. Backend API** (thư mục `giaingan-agent/`):
```bash
python -m uvicorn api.main:app --port 8000
```

**2. Dashboard React** (thư mục `giaingan-agent/web-react/`):
```bash
npm install
npm run dev
```
Vite mở `http://localhost:5500`. Ô "API" mặc định trỏ `http://localhost:8000`
(đổi được trên UI, hoặc set `VITE_API_BASE` trong `.env`).

Backend đã bật CORS `*` nên web cổng 5500 gọi API cổng 8000 không bị chặn.

## Build production

```bash
npm run build      # xuat ra dist/
npm run preview    # xem thu ban build
```

`dist/` là file tĩnh, deploy len Vercel/Firebase/GitHub Pages. Nhớ set `VITE_API_BASE`
tro vao public endpoint agent tren GreenNode AgentBase truoc khi build.
