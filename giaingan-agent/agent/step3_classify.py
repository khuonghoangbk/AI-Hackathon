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

import json
import unicodedata
from typing import Any

from .config_loader import load_checklist, load_doc_signatures, load_voucher_confidence
from .llm_client import MOCK, get_client

XANH = "xanh"
CAM = "cam"
DO = "do"

_HA_NGUONG_VOUCHER = {"2": 0.10, "4": 0.05}  # tru bot nguong tin cay


def _norm(s: str) -> str:
    # Chu 'd/D' khong duoc NFD tach dau (khong phai d + dau ket hop),
    # nen phai thay thu cong truoc khi bo dau -> tranh 'hoa don' != 'hoa don'.
    s = s.replace("đ", "d").replace("Đ", "D")
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.lower()


def _diem_nhan_dang_live(noi_dung: dict, ten_loai: str, dau_hieu: list[str]) -> float:
    """Nhan dang loai bang LLM (Qwen Flash). Tra ve diem tin cay 0..1.

    Model doc noi dung tai lieu va cham diem xem co dung la loai '{ten_loai}' khong.
    Neu goi that that bai / mode!=live -> tra -1 de caller fallback ve mock.
    """
    prompt = (
        "Ban la bo phan hau kiem ho so ngan hang. Cho noi dung tai lieu (JSON) va "
        f"loai ky vong '{ten_loai}' voi cac dau hieu nhan dang: {dau_hieu}.\n"
        "Cham diem tin cay tu 0.0 den 1.0 the hien tai lieu co DUNG la loai nay khong. "
        "Chi tra JSON dang {\"diem_tin_cay\": <so>, \"can_cu\": [\"...\"]}.\n\n"
        f"Noi dung tai lieu:\n{json.dumps(noi_dung, ensure_ascii=False)}"
    )
    res = get_client().extract_json(prompt, fast=True, mode="live")
    if not res or "diem_tin_cay" not in res:
        return -1.0
    try:
        return float(res["diem_tin_cay"])
    except (TypeError, ValueError):
        return -1.0


def _diem_nhan_dang(noi_dung: dict, dau_hieu: list[str]) -> float:
    """Diem tin cay mock cho nhan dang loai tai lieu.

    Nhan dang loai chi can khop MOT dau hieu dac trung (vd tieu de 'GIAY NHAN NO'
    du de biet la Giay nhan no), khong doi khop het moi dau hieu. Vi vay:
    - 1 dau hieu khop   -> 0.85 (dat nguong)
    - >=2 dau hieu khop  -> 1.0
    - 0 dau hieu khop    -> 0.0
    So khop tren TOAN BO noi_dung (ke ca tieu_de).
    """
    blob = _norm(" ".join(str(v) for v in noi_dung.values()))
    if not dau_hieu:
        return 0.0
    hit = sum(1 for d in dau_hieu if _norm(d) in blob)
    if hit == 0:
        return 0.0
    if hit == 1:
        return 0.85
    return 1.0


def _dem_truong_bat_buoc(noi_dung: dict, truong: list[str]) -> int:
    return sum(1 for t in truong if noi_dung.get(t) not in (None, "", 0))


def run(context: dict, docs: list[dict], mode: str = MOCK) -> dict[str, Any]:
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
                    "ly_do": "Chưa có file" if trang_thai == DO else "Mục điều kiện, chưa nộp - không tính thiếu",
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
                    "ly_do": "Không có cấu hình nhận dạng, chấp nhận theo khai báo",
                    "doc_id": doc["doc_id"],
                }
            )
            continue

        nguong = sig["nguong_dat"]
        # Nhan dang loai: live dung LLM cham diem; mock (hoac live that bai) dung so khop chuoi
        diem = -1.0
        if mode != MOCK:
            diem = _diem_nhan_dang_live(noi_dung, sig["ten"], sig["dau_hieu_nhan_dang"])
        if diem < 0:
            diem = _diem_nhan_dang(noi_dung, sig["dau_hieu_nhan_dang"])
        so_truong = _dem_truong_bat_buoc(noi_dung, sig["truong_bat_buoc"])

        # Ha nguong theo voucher_type
        giam = _HA_NGUONG_VOUCHER.get(str(doc.get("voucher_type")), 0.0)
        nguong_diem = max(0.0, nguong["diem_tin_cay_toi_thieu"] - giam)

        dat_nhan_dang = diem >= nguong_diem
        dat_cau_truc = so_truong >= nguong["so_truong_bat_buoc_toi_thieu"]

        if dat_nhan_dang and dat_cau_truc:
            trang_thai = XANH
            ly_do = "Đã xác thực loại và cấu trúc"
        else:
            trang_thai = CAM
            muc_khong_xac_thuc.append(ma)
            ly_do_parts = []
            if not dat_nhan_dang:
                ly_do_parts.append(
                    f"khai là '{sig['ten']}' nhưng dấu hiệu không khớp (điểm {diem} < ngưỡng {nguong_diem})"
                )
            if not dat_cau_truc:
                ly_do_parts.append(
                    f"thiếu trường bắt buộc ({so_truong}/{nguong['so_truong_bat_buoc_toi_thieu']})"
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
