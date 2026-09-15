"""[6] Cross-check: ap rules_P1.json, tinh ket qua tung cap, gan muc 🟢🟡🔴.
Quy tac nao co nguon A hoac B phu thuoc muc trong muc_khong_xac_thuc -> tra ⚪
'chua_kiem_tra_duoc' kem ly do, TUYET DOI khong tra 🟢."""
from __future__ import annotations

from typing import Any

from .config_loader import load_rules

XANH = "xanh"
VANG = "vang"
DO = "do"
TRANG = "chua_kiem_tra_duoc"  # ⚪

# Ban do: truong nghiep vu -> muc checklist cung cap truong do
_TRUONG_TO_MUC = {
    "so_tien_de_nghi": "3471",
    "so_tien_chi_dan_tt": "3472",
    "nguoi_thu_huong": "3472",
    "tong_gia_tri_hoa_don": "3455",
    "ben_ban_hoa_don": "3455",
    "ben_mua_hoa_don": "3455",
    "hoa_don_trong_ho_so": "3455",
    "gia_tri_hop_dong": "34231",
    "noi_dung_hang_hoa": "34231",
    "khach_hang_vay": "3471",
    "muc_dich_su_dung": "3471",
}


def _muc_nguon(truong: str) -> str | None:
    return _TRUONG_TO_MUC.get(truong)


def _op_bang(a, b, dung_sai) -> bool:
    if a is None or b is None:
        return False
    return abs(a - b) <= dung_sai


def _op_khong_vuot(a, b, dung_sai) -> bool:
    if a is None or b is None:
        return False
    return a <= b + dung_sai


def _op_trung(a, b) -> bool:
    if not a or not b:
        return False
    return str(a).strip().lower() == str(b).strip().lower()


def run(extract: dict, classify: dict, history: dict) -> dict[str, Any]:
    rules_cfg = load_rules()
    dung_sai = rules_cfg.get("dung_sai_lam_tron_vnd", 0)
    truong = extract["truong"]
    nguon = extract["nguon"]
    khong_xac_thuc = set(classify["muc_khong_xac_thuc"])

    ket_qua: list[dict] = []

    for rule in rules_cfg["rules"]:
        rid = rule["id"]
        fa, fb = rule["a"], rule["b"]

        # Kiem tra cua chan: nguon phu thuoc co bi 🟠 khong
        muc_a = _muc_nguon(fa)
        muc_b = _muc_nguon(fb)
        chan = [m for m in (muc_a, muc_b) if m in khong_xac_thuc]

        # R7 dac biet: doi chieu voi lich su, khong phu thuoc cap truong thong thuong
        if rule["op"] == "khong_trung":
            if history.get("co_trung"):
                trung = history["hoa_don_trung_lich_su"]
                ket_qua.append(
                    {
                        "rule_id": rid,
                        "mo_ta": rule["mo_ta"],
                        "muc": DO,
                        "chi_tiet": f"Phat hien {len(trung)} hoa don da dung o lan giai ngan truoc",
                        "nguon": trung,
                    }
                )
            else:
                ket_qua.append(
                    {
                        "rule_id": rid,
                        "mo_ta": rule["mo_ta"],
                        "muc": XANH,
                        "chi_tiet": "Khong co hoa don trung lich su",
                    }
                )
            continue

        if chan:
            ket_qua.append(
                {
                    "rule_id": rid,
                    "mo_ta": rule["mo_ta"],
                    "muc": TRANG,
                    "chi_tiet": f"Chua kiem tra duoc: muc {chan} chua xac thuc (buoc 3)",
                    "muc_gay_ra": chan,
                }
            )
            continue

        a = truong.get(fa)
        b = truong.get(fb)

        # Neu thieu du lieu (khong do 🟠 chan) -> cung ⚪
        if a is None or b is None:
            ket_qua.append(
                {
                    "rule_id": rid,
                    "mo_ta": rule["mo_ta"],
                    "muc": TRANG,
                    "chi_tiet": f"Chua kiem tra duoc: thieu du lieu ({fa}={a}, {fb}={b})",
                }
            )
            continue

        op = rule["op"]
        if op == "bang":
            ok = _op_bang(a, b, dung_sai)
        elif op == "khong_vuot":
            ok = _op_khong_vuot(a, b, dung_sai)
        elif op == "trung":
            ok = _op_trung(a, b)
        elif op == "hoa_don_khong_vuot_hd":
            ok = _op_khong_vuot(b, a, dung_sai)  # tong hoa don (b) khong vuot gia tri HD (a)
        elif op == "phu_hop":
            # Mock: coi la phu hop neu co ca hai (reasoning that dung GLM)
            ok = bool(a) and bool(b)
        else:
            ok = False

        muc = XANH if ok else rule["muc_khi_sai"]
        ket_qua.append(
            {
                "rule_id": rid,
                "mo_ta": rule["mo_ta"],
                "muc": muc,
                "chi_tiet": f"{fa}={a} vs {fb}={b}",
                "nguon": {fa: nguon.get(fa), fb: nguon.get(fb)},
            }
        )

    return {"ket_qua_rule": ket_qua}
