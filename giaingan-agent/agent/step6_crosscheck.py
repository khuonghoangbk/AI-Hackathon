"""[6] Cross-check: ap rules_P1.json, tinh ket qua tung cap, gan muc 🟢🟡🔴.
Quy tac nao co nguon A hoac B phu thuoc muc trong muc_khong_xac_thuc -> tra ⚪
'chua_kiem_tra_duoc' kem ly do, TUYET DOI khong tra 🟢."""
from __future__ import annotations

from typing import Any

from .config_loader import load_rules
from .llm_client import MOCK, get_client

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


def _op_phu_hop_live(muc_dich, noi_dung_hang) -> bool | None:
    """Live: dung GLM suy luan muc dich vay co phu hop noi dung hang hoa khong.
    Tra True/False. Neu goi that bai -> None de caller fallback ve mock."""
    prompt = (
        "Ban la chuyen vien tham dinh tin dung. Danh gia muc dich vay von co PHU HOP "
        "voi noi dung hang hoa/dich vu tren hoa don-hop dong khong.\n"
        f"- Muc dich su dung von: {muc_dich}\n"
        f"- Noi dung hang hoa: {noi_dung_hang}\n"
        "Chi tra JSON: {\"phu_hop\": true/false, \"ly_do\": \"...\"}."
    )
    res = get_client().extract_json(prompt, fast=False, mode="live")
    if not res or "phu_hop" not in res:
        return None
    return bool(res["phu_hop"])


def run(extract: dict, classify: dict, history: dict, mode: str = MOCK) -> dict[str, Any]:
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
                        "chi_tiet": f"Phát hiện {len(trung)} hóa đơn đã dùng ở lần giải ngân trước",
                        "nguon": trung,
                    }
                )
            else:
                ket_qua.append(
                    {
                        "rule_id": rid,
                        "mo_ta": rule["mo_ta"],
                        "muc": XANH,
                        "chi_tiet": "Không có hóa đơn trùng lịch sử",
                    }
                )
            continue

        if chan:
            ket_qua.append(
                {
                    "rule_id": rid,
                    "mo_ta": rule["mo_ta"],
                    "muc": TRANG,
                    "chi_tiet": f"Chưa kiểm tra được: mục {chan} chưa xác thực (bước 3)",
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
                    "chi_tiet": f"Chưa kiểm tra được: thiếu dữ liệu ({fa}={a}, {fb}={b})",
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
            # Live: GLM suy luan muc dich vay <-> noi dung hang hoa.
            # Mock (hoac live that bai): coi la phu hop neu co ca hai.
            ok = None
            if mode != MOCK:
                ok = _op_phu_hop_live(a, b)
            if ok is None:
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

    # ---- Canh bao dac thu (bo sung, chi them khi kich hoat) ----
    ket_qua.extend(_canh_bao_dac_thu(extract, truong, dung_sai))

    return {"ket_qua_rule": ket_qua}


def _canh_bao_dac_thu(extract: dict, truong: dict, dung_sai: int) -> list[dict]:
    """Sinh cac phat hien 🟡 cho tinh huong ho so dac thu.

    Chi tra ve phat hien khi that su kich hoat (khong them dong xanh),
    de khong lam loang bao cao va khong doi mau ho so sach/rui ro.

    W1 - Hoa don do tin cay thap (ban scan mo, voucher_type=2): can nguoi xac thuc.
    W2 - Giai ngan mot phan (so tien de nghi < tong gia tri hoa don ngoai dung sai):
         nhac kiem tra vi de nghi giai ngan thap hon tong hoa don.
    """
    phat_hien: list[dict] = []

    # W1: hoa don do tin cay thap
    hoa_don = extract.get("hoa_don", []) or []
    hd_thap = [h for h in hoa_don if h.get("do_tin_cay") == "thap"]
    if hd_thap:
        so_hd = ", ".join(str(h.get("so_hoa_don") or "?") for h in hd_thap)
        phat_hien.append(
            {
                "rule_id": "W1",
                "mo_ta": "Hóa đơn có độ tin cậy thấp (bản scan mờ) — cần xác thực thủ công",
                "muc": VANG,
                "chi_tiet": f"Có {len(hd_thap)} hóa đơn độ tin cậy thấp: {so_hd}",
                "nguon": {"hoa_don_tin_cay_thap": hd_thap},
            }
        )

    # W2: giai ngan mot phan
    so_de_nghi = truong.get("so_tien_de_nghi")
    tong_hd = truong.get("tong_gia_tri_hoa_don")
    if so_de_nghi is not None and tong_hd is not None and so_de_nghi < tong_hd - dung_sai:
        phat_hien.append(
            {
                "rule_id": "W2",
                "mo_ta": "Giải ngân một phần — số tiền đề nghị thấp hơn tổng giá trị hóa đơn",
                "muc": VANG,
                "chi_tiet": f"so_tien_de_nghi={so_de_nghi} < tong_gia_tri_hoa_don={tong_hd}",
            }
        )

    return phat_hien
