"""Orchestrator — nối 7 bước Luồng 1.

check_ho_so(): chạy 1 hồ sơ (Luồng 1).
hau_kiem_lo():  chạy nhiều hồ sơ, xếp hạng rủi ro (Luồng 3).
"""
from __future__ import annotations

from dataclasses import asdict
from typing import Any

from . import (
    step1_context,
    step3_classify,
    step4_extract,
    step5_history,
    step6_crosscheck,
    step7_report,
)
from .config_loader import bang_tra
from .llm_client import get_client
from .models import KetQuaHoSo, Muc
from .step2_load_docs import MockDocumentSource

# điểm rủi ro theo mức, dùng xếp hạng ở Luồng 3
_DIEM_RUI_RO = {Muc.LECH: 10, Muc.CHU_Y: 3, Muc.CHUA_KIEM: 1, Muc.KHOP: 0}


def check_ho_so(ho_so: dict[str, Any]) -> KetQuaHoSo:
    """Chạy đầy đủ 7 bước trên một hồ sơ đã nạp."""
    llm = get_client()

    # [1] ngữ cảnh
    context = step1_context.run(ho_so)
    loai = context["loai_giai_ngan"]
    bt = bang_tra(loai)

    # [2] tài liệu đã nằm trong ho_so (MVP). Bản thật: load qua DocumentSource.

    # [3] xác thực loại — CỬA CHẶN
    xac_thuc = step3_classify.run(llm, context, bt)
    muc_khong_xt = step3_classify.ds_muc_khong_xac_thuc(xac_thuc)

    # [4] trích xuất (chỉ mục 🟢)
    du_lieu = step4_extract.run(llm, context, xac_thuc, bt)

    # [5] lịch sử + core
    lich_su = step5_history.run(context)
    core = step5_history.load_core(context["limit_id"])

    # [6] đối chiếu chéo
    quy_tac = step6_crosscheck.run(
        bt["rules"], du_lieu, xac_thuc, muc_khong_xt,
        context, lich_su, core, bt["tolerance_vnd"],
    )

    # [7] báo cáo
    return step7_report.run(context["ho_so_id"], loai, xac_thuc, quy_tac)


def check_by_id(ho_so_id: str, data_dir: str) -> KetQuaHoSo:
    source = MockDocumentSource(data_dir)
    return check_ho_so(source.load_ho_so(ho_so_id))


def diem_rui_ro(kq: KetQuaHoSo) -> int:
    return sum(_DIEM_RUI_RO.get(q.muc, 0) for q in kq.quy_tac)


def hau_kiem_lo(data_dir: str, ho_so_ids: list[str] | None = None) -> list[dict[str, Any]]:
    """Luồng 3: chạy lô, trả bảng xếp hạng rủi ro (giảm dần)."""
    source = MockDocumentSource(data_dir)
    ids = ho_so_ids or source.list_ho_so()
    bang: list[dict[str, Any]] = []
    for hid in ids:
        try:
            kq = check_ho_so(source.load_ho_so(hid))
        except Exception as e:  # noqa: BLE001 - hồ sơ lỗi thì ghi nhận, không chặn lô
            bang.append({"ho_so_id": hid, "loi": str(e), "diem_rui_ro": -1})
            continue
        bang.append({
            "ho_so_id": hid,
            "loai_giai_ngan": kq.loai_giai_ngan,
            "muc_tong_hop": kq.muc_tong_hop.value,
            "diem_rui_ro": diem_rui_ro(kq),
            "do_phu": kq.do_phu,
        })
    bang.sort(key=lambda r: r["diem_rui_ro"], reverse=True)
    return bang


def ket_qua_to_dict(kq: KetQuaHoSo) -> dict[str, Any]:
    """Chuyển KetQuaHoSo thành dict JSON-serializable (Enum -> value)."""
    d = asdict(kq)
    d["muc_tong_hop"] = kq.muc_tong_hop.value
    for x in d["xac_thuc"]:
        x["trang_thai"] = x["trang_thai"].value if hasattr(x["trang_thai"], "value") else x["trang_thai"]
    for q in d["quy_tac"]:
        q["muc"] = q["muc"].value if hasattr(q["muc"], "value") else q["muc"]
    return d
