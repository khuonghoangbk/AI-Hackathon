"""[1] Lay ngu canh ho so: loai GN, limit ID, so tien de nghi, danh sach file khai bao."""
from __future__ import annotations

from typing import Any

from .config_loader import load_khoan_vay


def run(ho_so: dict) -> dict[str, Any]:
    ho_so_id = ho_so["ho_so_id"]
    khoan_vay = load_khoan_vay().get(ho_so_id, {})

    tai_lieu_khai_bao = [
        {
            "ma_checklist": t["ma_checklist"],
            "voucher_type": t.get("voucher_type"),
            "so_trang": t.get("so_trang"),
        }
        for t in ho_so.get("tai_lieu", [])
    ]

    return {
        "ho_so_id": ho_so_id,
        "loai_giai_ngan": khoan_vay.get("loai_giai_ngan", "P1"),
        "limit_id": khoan_vay.get("limit_id"),
        "khach_hang_vay": khoan_vay.get("khach_hang_vay"),
        "so_tien_de_nghi": khoan_vay.get("so_tien_de_nghi"),
        "muc_dich_su_dung": khoan_vay.get("muc_dich_su_dung"),
        "loai_tien": khoan_vay.get("loai_tien", "VND"),
        "tai_lieu_khai_bao": tai_lieu_khai_bao,
    }
