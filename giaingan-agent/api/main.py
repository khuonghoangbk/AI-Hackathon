"""FastAPI entrypoint cho Tro ly kiem tra ho so giai ngan.

Endpoints:
- GET  /health           -> 200 (bat buoc cho AgentBase runtime)
- GET  /requests         -> danh sach YCGN (Tab 1 dashboard)
- POST /check            -> chay 7 buoc Luong 1 cho 1 ho so
- POST /batch            -> Luong 3 hau kiem theo lo -> bang xep hang rui ro

Chay local:
    uvicorn api.main:app --reload --port 8000
"""
from __future__ import annotations

import sys
from pathlib import Path

# Cho phep chay 'uvicorn api.main:app' tu thu muc goc repo
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from agent import orchestrator  # noqa: E402
from agent.config_loader import (  # noqa: E402
    load_ho_so,
    load_khoan_vay,
    list_ho_so_ids,
)
from agent.llm_client import LLMConfigError  # noqa: E402

app = FastAPI(
    title="Tro ly kiem tra ho so giai ngan",
    description="Multi-step agent kiem tra ho so giai ngan P1 (MSB AI Hackathon 2026)",
    version="0.1.0",
)

# Cho phep dashboard (Next.js) goi API khi dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---- Schema ----
class CheckRequest(BaseModel):
    ho_so_id: str
    mode: str | None = None  # 'mock' | 'live'; None -> mac dinh tu RUN_MODE
    # Tai lieu do TNTD upload (bo sung/thay the). Neu co -> merge theo ma_checklist.
    tai_lieu_thay_the: list[dict] | None = None


class BatchRequest(BaseModel):
    ho_so_ids: list[str] | None = None
    mode: str | None = None  # 'mock' | 'live'; None -> mac dinh tu RUN_MODE


# ---- Endpoints ----
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/requests")
def list_requests():
    """Danh sach YCGN cho Tab 1: ghep header (khoan_vay) + so tai lieu (ho so)."""
    khoan_vay = load_khoan_vay()
    items = []
    for hid in list_ho_so_ids():
        kv = khoan_vay.get(hid, {})
        try:
            ho_so = load_ho_so(hid)
            so_tai_lieu = len(ho_so.get("tai_lieu", []))
        except FileNotFoundError:
            so_tai_lieu = 0
        items.append(
            {
                "ma_ycgn": hid,
                "khach_hang": kv.get("khach_hang_vay"),
                "loai_giai_ngan": kv.get("loai_giai_ngan"),
                "so_tien_de_nghi": kv.get("so_tien_de_nghi"),
                "so_tai_lieu": so_tai_lieu,
            }
        )
    return {"requests": items}


@app.post("/check")
def check(req: CheckRequest):
    """Luong 1: chay 7 buoc cho 1 ho so. mode='live' -> goi AI that."""
    try:
        return orchestrator.check_one(req.ho_so_id, req.mode, req.tai_lieu_thay_the)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Khong tim thay ho so: {req.ho_so_id}")
    except LLMConfigError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/batch")
def batch(req: BatchRequest):
    """Luong 3: hau kiem theo lo, tra bang xep hang rui ro. mode='live' -> goi AI that."""
    try:
        return orchestrator.check_batch(req.ho_so_ids, req.mode)
    except LLMConfigError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---- Phuc vu frontend da build (React/Vite) ----
# Neu co thu muc web build (web-react/dist), mount tai "/" de FE + BE chay chung 1 cong.
# Dat SAU cac route API o tren nen /health, /requests, /check, /batch khong bi che.
# html=True -> tu tra index.html cho cac path khong khop file tinh (SPA fallback).
_DIST_DIR = Path(__file__).resolve().parent.parent / "web-react" / "dist"
if _DIST_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(_DIST_DIR), html=True), name="frontend")
