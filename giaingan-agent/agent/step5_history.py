"""[5] History: tra lich_su_hoa_don.json — diem nhan demo (phat hien hoa don dung lai)."""
from __future__ import annotations

from typing import Any

from .config_loader import load_lich_su_hoa_don


def run(extract: dict) -> dict[str, Any]:
    lich_su = load_lich_su_hoa_don().get("hoa_don_da_dung", [])
    da_dung_index = {hd["so_hoa_don"]: hd for hd in lich_su}

    trung: list[dict] = []
    for hd in extract.get("hoa_don", []):
        so = hd.get("so_hoa_don")
        if so in da_dung_index:
            info = da_dung_index[so]
            trung.append(
                {
                    "so_hoa_don": so,
                    "doc_id": hd.get("doc_id"),
                    "trang": hd.get("trang"),
                    "lan_giai_ngan_truoc": info.get("lan_giai_ngan_truoc"),
                    "ngay_su_dung": info.get("ngay_su_dung"),
                }
            )

    return {"hoa_don_trung_lich_su": trung, "co_trung": bool(trung)}
