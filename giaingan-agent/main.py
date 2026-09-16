"""Entrypoint cho GreenNode AgentBase.

Runtime AgentBase yeu cau container:
- Lang nghe tren cong 8080
- Co GET /health tra 200

App FastAPI (voi day du route /health, /requests, /check, /batch + CORS) da duoc
dinh nghia san trong api/main.py. File nay chi tai su dung app do va chay uvicorn
tren cong 8080 (hoac lay tu bien moi truong PORT neu runtime cung cap).

Chay local:
    python main.py
Hoac:
    uvicorn main:app --host 0.0.0.0 --port 8080
"""
from __future__ import annotations

import os

# Tai su dung app FastAPI da co san (khong dinh nghia lai route).
from api.main import app  # noqa: F401  (app duoc uvicorn/ASGI server dung)

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
