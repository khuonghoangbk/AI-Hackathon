# ============================================================================
# Multi-stage build: FE (React/Vite) + BE (FastAPI) trong 1 image, chay 1 cong.
#
# Stage 1 (web-build): build dashboard React -> web-react/dist (file tinh)
# Stage 2 (runtime):   Python + FastAPI, copy dist vao de FastAPI serve chung.
#
# Runtime yeu cau: lang nghe cong 8080, co GET /health tra 200.
# ============================================================================

# ---- Stage 1: build frontend ----
FROM node:20-slim AS web-build
WORKDIR /web

# Cai deps truoc (tan dung cache khi chi doi source)
COPY web-react/package*.json ./
RUN npm ci

# Copy source va build -> /web/dist
COPY web-react/ ./
# Same-origin: FE goi API cung cong -> khong set VITE_API_BASE (mac dinh "")
RUN npm run build


# ---- Stage 2: runtime Python ----
FROM python:3.12-slim

# Khong ghi .pyc, log ra ngay (khong buffer) de xem tren AgentBase monitor.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

# Cai dependency Python truoc (tan dung layer cache).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source backend. .dockerignore da loai .env/.venv/state files/node_modules.
COPY . .

# Copy frontend da build tu stage 1 vao dung cho FastAPI mount (web-react/dist).
COPY --from=web-build /web/dist ./web-react/dist

EXPOSE 8080

# Chay app FastAPI (app tai su dung tu api/main.py qua main.py).
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
