"""[1] Lấy ngữ cảnh hồ sơ.

Đọc metadata: loại giải ngân, limit ID, số tiền đề nghị, ngày đề nghị,
danh sách file + mã checklist + voucherType đã khai.

MVP: đọc từ dict hồ sơ (đã nạp từ data_mock). Bản thật: đọc từ BPM/LMS.
"""
from __future__ import annotations

from typing import Any


def run(ho_so: dict[str, Any]) -> dict[str, Any]:
    context = ho_so.get("context", {})
    tai_lieu = ho_so.get("tai_lieu", [])
    return {
        "ho_so_id": ho_so.get("ho_so_id", ""),
        "loai_giai_ngan": context.get("loai_giai_ngan", ""),
        "limit_id": context.get("limit_id", ""),
        "so_tien_de_nghi": context.get("so_tien_de_nghi", 0),
        "ngay_de_nghi_gn": context.get("ngay_de_nghi_gn", ""),
        "muc_da_co_file": sorted({t.get("ma_checklist", "") for t in tai_lieu}),
        "tai_lieu": tai_lieu,
    }
