"""FastAPI cho Trợ lý kiểm tra hồ sơ giải ngân.

Endpoints:
  GET  /health                 - healthcheck (dùng cho AgentBase runtime contract)
  GET  /ho-so                  - liệt kê hồ sơ mock có sẵn
  POST /check                  - kiểm tra 1 hồ sơ (Luồng 1)
  POST /batch                  - hậu kiểm theo lô (Luồng 3), trả bảng xếp hạng rủi ro
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent.orchestrator import (
    check_by_id,
    check_ho_so,
    hau_kiem_lo,
    ket_qua_to_dict,
)
from agent.step2_load_docs import MockDocumentSource

load_dotenv()

DATA_MOCK_DIR = os.getenv(
    "DATA_MOCK_DIR",
    str(Path(__file__).resolve().parent.parent / "data_mock"),
)

app = FastAPI(
    title="Trợ lý kiểm tra hồ sơ giải ngân",
    description="MVP Hackathon — P1 (hàng hóa có hóa đơn) + P3 (lương chuyển khoản).",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class CheckByIdRequest(BaseModel):
    ho_so_id: str


class CheckInlineRequest(BaseModel):
    """Gửi trực tiếp nội dung hồ sơ (khi upload từ dashboard)."""
    ho_so: dict


class BatchRequest(BaseModel):
    ho_so_ids: list[str] | None = None


@app.get("/health")
def health() -> dict:
    return {"status": "HEALTHY"}


@app.get("/ho-so")
def list_ho_so() -> dict:
    source = MockDocumentSource(DATA_MOCK_DIR)
    return {"ho_so_ids": source.list_ho_so()}


@app.post("/check")
def check(req: CheckByIdRequest) -> dict:
    """Luồng 1 — kiểm tra một hồ sơ theo id (mock)."""
    try:
        kq = check_by_id(req.ho_so_id, DATA_MOCK_DIR)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return ket_qua_to_dict(kq)


@app.post("/check-inline")
def check_inline(req: CheckInlineRequest) -> dict:
    """Luồng 1 — kiểm tra hồ sơ gửi kèm nội dung (dùng khi upload)."""
    kq = check_ho_so(req.ho_so)
    return ket_qua_to_dict(kq)


@app.post("/batch")
def batch(req: BatchRequest) -> dict:
    """Luồng 3 — hậu kiểm theo lô, trả bảng xếp hạng rủi ro."""
    bang = hau_kiem_lo(DATA_MOCK_DIR, req.ho_so_ids)
    return {"tong_so": len(bang), "xep_hang": bang}
