"""[4] Extract: CHI chay tren cac muc 🟢 o buoc 3.
Trich cac truong nghiep vu, gan do_tin_cay theo voucher_type.
O mock: doc thang tu noi_dung tai lieu (mo phong ket qua LLM extract)."""
from __future__ import annotations

import json
from typing import Any

from .config_loader import load_doc_signatures, load_voucher_confidence
from .llm_client import MOCK, get_client

XANH = "xanh"


def _do_tin_cay(voucher_type: Any) -> str:
    vc = load_voucher_confidence().get(str(voucher_type), {})
    return vc.get("do_tin_cay", "khong_ro")


def _extract_live(noi_dung: dict, ma_checklist: str) -> dict:
    """Live: dung LLM (Qwen/GLM) trich cac truong bat buoc cua loai tai lieu tu noi_dung.
    Tra ve dict cac truong da doc. Neu that bai -> tra {} de caller fallback ve mock
    (doc thang noi_dung)."""
    sig = load_doc_signatures().get(ma_checklist, {})
    truong_can = sig.get("truong_bat_buoc", [])
    if not truong_can:
        return {}
    prompt = (
        "Ban la bo phan trich xuat thong tin tai lieu ngan hang. "
        f"Tu noi dung tai lieu (JSON) duoi day, trich cac truong: {truong_can}. "
        "Chi tra ve JSON gom dung cac truong do (gia tri so giu nguyen kieu so). "
        "Neu khong tim thay truong nao thi bo qua truong do.\n\n"
        f"Noi dung:\n{json.dumps(noi_dung, ensure_ascii=False)}"
    )
    res = get_client().extract_json(prompt, fast=True, mode="live")
    return res if isinstance(res, dict) else {}


def run(context: dict, docs: list[dict], classify: dict, mode: str = MOCK) -> dict[str, Any]:
    muc_xanh = {
        m["ma_checklist"] for m in classify["ket_qua_muc"] if m["trang_thai"] == XANH
    }
    docs_theo_muc: dict[str, list[dict]] = {}
    for d in docs:
        docs_theo_muc.setdefault(d["ma_checklist_khai"], []).append(d)

    # Live: LLM trich truong tu noi_dung, merge lai (gia tri live uu tien khi co).
    # Chi lam cho cac muc xanh. That bai -> giu nguyen noi_dung mock.
    if mode != MOCK:
        for ma, files in docs_theo_muc.items():
            if ma not in muc_xanh:
                continue
            for doc in files:
                live_fields = _extract_live(doc["noi_dung"], ma)
                for k, v in live_fields.items():
                    if v not in (None, "", 0):
                        doc["noi_dung"][k] = v

    truong: dict[str, Any] = {}
    nguon: dict[str, dict] = {}
    hoa_don_list: list[dict] = []

    def _set(ten: str, gia_tri: Any, doc: dict):
        if gia_tri in (None, "", 0):
            return
        truong[ten] = gia_tri
        nguon[ten] = {
            "tai_lieu": doc["ma_checklist_khai"],
            "doc_id": doc["doc_id"],
            "trang": doc.get("so_trang"),
            "do_tin_cay": _do_tin_cay(doc.get("voucher_type")),
        }

    # So tien de nghi lay tu context (giay nhan no)
    if context.get("so_tien_de_nghi"):
        truong["so_tien_de_nghi"] = context["so_tien_de_nghi"]
    truong["khach_hang_vay"] = context.get("khach_hang_vay")
    truong["muc_dich_su_dung"] = context.get("muc_dich_su_dung")

    # 3472 - UNC: so tien chi dan, nguoi thu huong
    for doc in docs_theo_muc.get("3472", []):
        if "3472" not in muc_xanh:
            continue
        nd = doc["noi_dung"]
        _set("so_tien_chi_dan_tt", nd.get("so_tien"), doc)
        _set("nguoi_thu_huong", nd.get("nguoi_thu_huong"), doc)

    # 34231 - Hop dong: gia tri hop dong, ben ban, noi dung hang hoa
    for doc in docs_theo_muc.get("34231", []):
        if "34231" not in muc_xanh:
            continue
        nd = doc["noi_dung"]
        _set("gia_tri_hop_dong", nd.get("gia_tri_hop_dong"), doc)
        _set("noi_dung_hang_hoa", nd.get("noi_dung_hang_hoa"), doc)

    # 3455 - Hoa don (co the nhieu): tong gia tri, ben ban/mua
    tong_hd = 0
    for doc in docs_theo_muc.get("3455", []):
        if "3455" not in muc_xanh:
            continue
        nd = doc["noi_dung"]
        hoa_don_list.append(
            {
                "so_hoa_don": nd.get("so_hoa_don"),
                "ky_hieu": nd.get("ky_hieu"),
                "tong_tien": nd.get("tong_tien_thanh_toan"),
                "ben_ban": nd.get("ben_ban"),
                "ben_mua": nd.get("ben_mua"),
                "doc_id": doc["doc_id"],
                "trang": doc.get("so_trang"),
                "do_tin_cay": _do_tin_cay(doc.get("voucher_type")),
            }
        )
        tong_hd += nd.get("tong_tien_thanh_toan", 0) or 0
        # Lay dai dien ben ban/mua tu hoa don dau
        _set("ben_ban_hoa_don", nd.get("ben_ban"), doc)
        _set("ben_mua_hoa_don", nd.get("ben_mua"), doc)

    if hoa_don_list:
        truong["tong_gia_tri_hoa_don"] = tong_hd
        truong["hoa_don_trong_ho_so"] = hoa_don_list

    return {"truong": truong, "nguon": nguon, "hoa_don": hoa_don_list}
