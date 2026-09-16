"""[4] Trích xuất thông tin — chỉ chạy trên các mục 🟢 ở bước 3.

Trích các trường cần đối chiếu theo từng loại tài liệu, gắn độ tin cậy
theo voucherType. MVP: nội dung đã có sẵn trong 'noi_dung_mo_phong'
(mô phỏng kết quả OCR/LLM). Bản thật: gọi llm.extract_json trên file.
"""
from __future__ import annotations

from typing import Any

from .llm_client import LLMClient
from .models import KetQuaXacThuc, TrangThaiMuc


def run(llm: LLMClient, context: dict[str, Any], xac_thuc: list[KetQuaXacThuc],
        bang_tra: dict) -> dict[str, dict[str, Any]]:
    """Trả dict: {ma_checklist: {trường đã trích, kèm _do_tin_cay, _voucher_type}}."""
    voucher_conf = bang_tra["voucher_confidence"]
    ma_xac_thuc = {k.ma_checklist for k in xac_thuc if k.trang_thai == TrangThaiMuc.XAC_THUC}
    tai_lieu_theo_ma = {t["ma_checklist"]: t for t in context["tai_lieu"]}

    du_lieu: dict[str, dict[str, Any]] = {}
    for ma in ma_xac_thuc:
        tl = tai_lieu_theo_ma.get(ma, {})
        noi_dung = dict(tl.get("noi_dung_mo_phong", {}))
        vt = tl.get("voucher_type", "1")
        noi_dung["_voucher_type"] = vt
        noi_dung["_do_tin_cay"] = voucher_conf.get(vt, {}).get("do_tin_cay", "cao")
        noi_dung["_ten_file"] = tl.get("ten_file", "")
        noi_dung["_trang"] = tl.get("so_trang")
        du_lieu[ma] = noi_dung
    return du_lieu
