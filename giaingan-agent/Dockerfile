# Image cho GreenNode AgentBase — agent kiem tra ho so giai ngan.
# Runtime yeu cau: lang nghe cong 8080, co GET /health tra 200.
FROM python:3.12-slim

# Khong ghi .pyc, log ra ngay (khong buffer) de xem tren AgentBase monitor.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

# Cai dependency truoc (tan dung layer cache khi code doi ma deps khong doi).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source. .dockerignore da loai .env/.venv/state files.
COPY . .

EXPOSE 8080

# Chay app FastAPI (app tai su dung tu api/main.py qua main.py).
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
