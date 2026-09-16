"""[7] Report: sinh JSON ket qua + dien giai, moi diem kem nguon = {tai_lieu, trang, vi_tri}.
Phan tong hop dem rieng so quy tac ⚪ va neu ly do (chi so do phu cua lan kiem tra).
Kem cau chot: 'Tro ly khong ket luan ho so du dieu kien giai ngan.'"""
from __future__ import annotations

from typing import Any

XANH = "xanh"
VANG = "vang"
DO = "do"
TRANG = "chua_kiem_tra_duoc"


def run(
    context: dict,
    classify: dict,
    extract: dict,
    history: dict,
    crosscheck: dict,
) -> dict[str, Any]:
    rules = crosscheck["ket_qua_rule"]

    # Dem theo muc
    dem = {XANH: 0, VANG: 0, DO: 0, TRANG: 0}
    for r in rules:
        dem[r.get("muc", TRANG)] += 1

    tong = len(rules)
    do_phu = round((tong - dem[TRANG]) / tong * 100, 1) if tong else 0

    # Danh sach phat hien theo muc (do truoc, vang, trang, xanh cuoi)
    phat_hien: list[dict] = []

    for r in rules:
        muc = r.get("muc", TRANG)
        phat_hien.append(
            {
                "rule_id": r["rule_id"],
                "muc": muc,
                "mo_ta": r["mo_ta"],
                "chi_tiet": r.get("chi_tiet", ""),
                "nguon": r.get("nguon"),
            }
        )

    # Sap xep: do > vang > trang > xanh
    muc_order = {DO: 0, VANG: 1, TRANG: 2, XANH: 3}
    phat_hien.sort(key=lambda x: muc_order.get(x["muc"], 9))

    # Phan loai tai lieu (tu classify)
    tai_lieu_summary: list[dict] = []
    for m in classify.get("ket_qua_muc", []):
        tai_lieu_summary.append(
            {
                "ma_checklist": m["ma_checklist"],
                "ten": m["ten"],
                "trang_thai": m["trang_thai"],
                "ly_do": m.get("ly_do", ""),
            }
        )

    # Muc do tong the
    if dem[DO] > 0:
        muc_tong_the = DO
        tom_tat = f"Phát hiện {dem[DO]} nội dung KHÔNG KHỚP (đỏ)"
    elif dem[VANG] > 0:
        muc_tong_the = VANG
        tom_tat = f"Có {dem[VANG]} nội dung CẦN CHÚ Ý (vàng)"
    elif dem[TRANG] > 0:
        muc_tong_the = TRANG
        tom_tat = f"Toàn bộ các nội dung kiểm tra được đều khớp, nhưng có {dem[TRANG]} nội dung CHƯA KIỂM TRA ĐƯỢC"
    else:
        muc_tong_the = XANH
        tom_tat = "Tất cả nội dung đối chiếu đều khớp"

    if dem[TRANG] > 0:
        tom_tat += f". Độ phủ kiểm tra: {do_phu}% ({tong - dem[TRANG]}/{tong} quy tắc)."

    return {
        "ho_so_id": context.get("ho_so_id"),
        "muc_tong_the": muc_tong_the,
        "tom_tat": tom_tat,
        "thong_ke": {
            "xanh": dem[XANH],
            "vang": dem[VANG],
            "do": dem[DO],
            "chua_kiem_tra_duoc": dem[TRANG],
            "tong_quy_tac": tong,
            "do_phu_phan_tram": do_phu,
        },
        "tai_lieu": tai_lieu_summary,
        "phat_hien": phat_hien,
        "hoa_don_trung_lich_su": history.get("hoa_don_trung_lich_su", []),
        "cau_chot": "Trợ lý không kết luận hồ sơ đủ điều kiện giải ngân. "
                    "Đây là kết quả kiểm tra sơ bộ để hỗ trợ Maker/Checker.",
    }
