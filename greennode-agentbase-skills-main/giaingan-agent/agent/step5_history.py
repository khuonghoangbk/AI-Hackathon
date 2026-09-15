"""[5] Tra lịch sử giải ngân — điểm nhấn demo.

P1: hóa đơn trong hồ sơ đã dùng ở lần giải ngân trước chưa? (DC-P1-08)
P3: kỳ lương đã được giải ngân trước chưa? (DC-P23-09)

MVP: tra file mock. Bản thật: gọi kho lịch sử giải ngân theo khoản vay.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

DATA_MOCK_DIR = Path(os.getenv("DATA_MOCK_DIR",
                               Path(__file__).resolve().parent.parent / "data_mock"))


def _load(ten: str) -> dict:
    p = Path(DATA_MOCK_DIR) / ten
    if not p.exists():
        return {}
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def run(context: dict[str, Any]) -> dict[str, Any]:
    """Trả ngữ cảnh lịch sử theo limit_id, để bước 6 dùng cho các rule nguon_ngoai=history."""
    limit_id = context.get("limit_id", "")
    hoa_don = _load("lich_su_hoa_don.json").get("theo_limit", {}).get(limit_id, {})
    ky_luong = _load("ky_luong_da_gn.json").get("theo_limit", {}).get(limit_id, {})
    return {
        "ds_hoa_don_da_dung": hoa_don.get("ds_hoa_don_da_dung", []),
        "tong_hoa_don_luy_ke": hoa_don.get("tong_hoa_don_luy_ke", 0),
        "ds_ky_luong_da_gn": ky_luong.get("ds_ky_luong_da_gn", []),
        "quy_luong_cac_ky_truoc": ky_luong.get("quy_luong_cac_ky_truoc", {}),
        "so_lao_dong_cac_ky_truoc": ky_luong.get("so_lao_dong_cac_ky_truoc", {}),
    }


def load_core(limit_id: str) -> dict[str, Any]:
    """Ngữ cảnh Core/T24 + BPM hạn mức theo limit_id (dùng cho rule nguon_ngoai=core)."""
    return _load("core_mock.json").get("khoan_vay", {}).get(limit_id, {})
