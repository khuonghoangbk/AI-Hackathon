"""[3] Classify — CUA CHAN, khong phai ghi chu.

Hai lop:
- Lop 1 (nhan dang loai): tap ung vien la 16 muc checklist P1 + nhan 'ngoai_checklist'.
  Khong dung ten file lam can cu. O che do mock, dung dau hieu nhan dang tren noi_dung.
- Lop 2 (kiem cau truc): co tim duoc truong_bat_buoc cua loai do theo doc_signatures khong.

Ket qua 3 trang thai cho tung MUC checklist:
- 🟢 da_xac_thuc      -> sang buoc 4
- 🟠 chua_xac_thuc    -> bo qua buoc 4 cho muc do, buoc 6 dung lam dieu kien chan
- 🔴 thieu_file       -> chua co file

Ha nguong theo voucher_type: ban scan (2)/ban mem (4) doc kem hon.
"""
from __future__ import annotations

import unicodedata
from typing import Any

from .config_loader import load_checklist, load_doc_signatures, load_voucher_confidence

XANH = "xanh"
CAM = "cam"
DO = "do"

_HA_NGUONG_VOUCHER = {"2": 0.10, "4": 0.05}  # tru bot nguong tin cay


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.lower()


def _diem_nhan_dang(noi_dung: dict, dau_hieu: list[str]) -> float:
    """Diem tin cay mock: ty le dau hieu xuat hien trong noi_dung."""
    blob = _norm(" ".join(str(v) for v in noi_dung.values()))
    if not dau_hieu:
        return 0.0
    hit = sum(1 for d in dau_hieu if _norm(d) in blob)
    return round(hit / len(dau_hieu), 2)


def _dem_truong_bat_buoc(noi_dung: dict, truong: list[str]) -> int:
    return sum(1 for t in truong if noi_dung.get(t) not in (None, "", 0))


def run(context: dict, docs: list[dict]) -> dict[str, Any]:
    checklist = load_checklist()
    signatures = load_doc_signatures()

    ket_qua_muc: list[dict] = []
    muc_khong_xac_thuc: list[str] = []
    docs_theo_muc: dict[str, list[dict]] = {}

    # Gom file theo muc checklist da khai
    for d in docs:
        docs_theo_muc.setdefault(d["ma_checklist_khai"], []).append(d)

    for muc in checklist["muc"]:
        ma = muc["ma_checklist"]
        files = docs_theo_muc.get(ma, [])

        # 🔴 chua co file
        if not files:
            trang_thai = DO if muc["bat_buoc"] == "co" else "khong_ap_dung"
            if trang_thai == DO:
                muc_khong_xac_thuc.append(ma)
            ket_qua_muc.append(
                {
                    "ma_checklist": ma,
                    "ten": muc["ten"],
                    "bat_buoc": muc["bat_buoc"],
                    "trang_thai": trang_thai,
                    "ly_do": "Chua co file" if trang_thai == DO else "Muc dieu kien, chua nop - khong tinh thieu",
                }
            )
            continue

        sig = signatures.get(ma)
        doc = files[0]
        noi_dung = doc["noi_dung"]

        # Loai chua co signature -> chap nhan theo khai bao (chua kiem sau)
        if not sig:
            ket_qua_muc.append(
                {
                    "ma_checklist": ma,
                    "ten": muc["ten"],
                    "bat_buoc": muc["bat_buoc"],
                    "trang_thai": XANH,
                    "diem_tin_cay": None,
                    "ly_do": "Khong co signature cau hinh, chap nhan theo khai bao",
                    "doc_id": doc["doc_id"],
                }
            )
            continue

        nguong = sig["nguong_dat"]
        diem = _diem_nhan_dang(noi_dung, sig["dau_hieu_nhan_dang"])
        so_truong = _dem_truong_bat_buoc(noi_dung, sig["truong_bat_buoc"])

        # Ha nguong theo voucher_type
        giam = _HA_NGUONG_VOUCHER.get(str(doc.get("voucher_type")), 0.0)
        nguong_diem = max(0.0, nguong["diem_tin_cay_toi_thieu"] - giam)

        dat_nhan_dang = diem >= nguong_diem
        dat_cau_truc = so_truong >= nguong["so_truong_bat_buoc_toi_thieu"]

        if dat_nhan_dang and dat_cau_truc:
            trang_thai = XANH
            ly_do = "Da xac thuc loai va cau truc"
        else:
            trang_thai = CAM
            muc_khong_xac_thuc.append(ma)
            ly_do_parts = []
            if not dat_nhan_dang:
                ly_do_parts.append(
                    f"khai la '{sig['ten']}' nhung dau hieu khong khop (diem {diem} < nguong {nguong_diem})"
                )
            if not dat_cau_truc:
                ly_do_parts.append(
                    f"thieu truong bat buoc ({so_truong}/{nguong['so_truong_bat_buoc_toi_thieu']})"
                )
            ly_do = "; ".join(ly_do_parts)

        ket_qua_muc.append(
            {
                "ma_checklist": ma,
                "ten": muc["ten"],
                "bat_buoc": muc["bat_buoc"],
                "trang_thai": trang_thai,
                "diem_tin_cay": diem,
                "so_truong_dat": so_truong,
                "voucher_type": doc.get("voucher_type"),
                "ly_do": ly_do,
                "doc_id": doc["doc_id"],
            }
        )

    return {
        "ket_qua_muc": ket_qua_muc,
        "muc_khong_xac_thuc": muc_khong_xac_thuc,
    }
