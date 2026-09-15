"""[6] Đối chiếu chéo — áp bộ quy tắc (chung + riêng theo loại).

CƠ CHẾ CỬA CHẶN (mục 3.7.5): quy tắc có 'phu_thuoc' chứa mã checklist đang ở
trạng thái 🟠 (chua_xac_thuc) sẽ trả ⚪ (CHUA_KIEM), tuyệt đối không trả 🟢.

Skeleton hiện thực một tập phép so sánh cơ bản. Các phép cần suy luận ngôn ngữ
(phu_hop, dan_nguon, khop_tung_dong) để placeholder trả ⚪ kèm ghi chú "cần LLM".
"""
from __future__ import annotations

from typing import Any

from .models import KetQuaQuyTac, KetQuaXacThuc, Muc, NguonDan


def _muc_khi_sai(rule: dict) -> Muc:
    return Muc.LECH if rule.get("muc_khi_sai") == "do" else Muc.CHU_Y


def _lay_gia_tri(khoa: str | None, du_lieu: dict, ngoai: dict, context: dict):
    """Phân giải 'nguon' dạng '<ma>.<truong>' hoặc 'core./history./context.<truong>'."""
    if not khoa:
        return None
    prefix, _, truong = khoa.partition(".")
    if prefix == "core":
        return ngoai.get("core", {}).get(truong)
    if prefix == "history":
        return ngoai.get("history", {}).get(truong)
    if prefix == "context":
        return context.get(truong)
    # dạng <ma_checklist>.<truong>, bỏ hậu tố kiểu .cong_don nếu chưa hỗ trợ
    return du_lieu.get(prefix, {}).get(truong)


def _so_sanh(op: str, a: Any, b: Any, dung_sai: int) -> tuple[bool, str]:
    """Trả (dat, ly_do). dat=True nghĩa là khớp/hợp lệ."""
    if op == "bang":
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            ok = abs(a - b) <= dung_sai
            return ok, "" if ok else f"Lệch {a} vs {b}"
        return (a == b), "" if a == b else f"Khác nhau: {a} vs {b}"
    if op == "khong_vuot":
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            ok = a <= b + dung_sai
            return ok, "" if ok else f"{a} vượt {b}"
    if op in ("trung", "thuoc_tap"):
        if op == "thuoc_tap" and isinstance(b, list):
            ok = a in b
            return ok, "" if ok else f"{a} không thuộc {b}"
        return (a == b), "" if a == b else f"Không trùng: {a} vs {b}"
    if op == "trung_ten":
        na, nb = _chuan_hoa_ten(a), _chuan_hoa_ten(b)
        if na == nb:
            return True, ""
        return False, f"Tên khác: '{a}' vs '{b}'"
    if op == "khong_trung":
        if isinstance(b, list):
            ok = a not in b and not any(_trung_hoa_don(a, x) for x in b)
            return ok, "" if ok else f"{a} đã tồn tại trong lịch sử"
        return (a != b), "" if a != b else f"Trùng: {a}"
    # phép chưa hiện thực trong skeleton
    return None, f"Phép '{op}' cần hiện thực (LLM/logic tập hợp)"  # type: ignore[return-value]


def _chuan_hoa_ten(s: Any) -> str:
    if not isinstance(s, str):
        return str(s)
    return " ".join(s.upper().replace(",", " ").split())


def _trung_hoa_don(a: Any, x: Any) -> bool:
    if isinstance(x, dict):
        return str(a) in (str(x.get("so_hoa_don", "")), str(x.get("ky_hieu", "")))
    return False


def run(rules: list[dict], du_lieu: dict[str, dict], xac_thuc: list[KetQuaXacThuc],
        muc_khong_xac_thuc: list[str], context: dict, lich_su: dict,
        core: dict, tolerance_vnd: int) -> list[KetQuaQuyTac]:
    ngoai = {"history": lich_su, "core": core}
    ket_qua: list[KetQuaQuyTac] = []

    for rule in rules:
        phu_thuoc = rule.get("phu_thuoc", [])
        # CỬA CHẶN: có nguồn phụ thuộc chưa xác thực -> ⚪
        chan = [m for m in phu_thuoc if m in muc_khong_xac_thuc]
        if chan:
            ket_qua.append(KetQuaQuyTac(
                rule["id"], rule["ten"], Muc.CHUA_KIEM,
                ly_do=f"Chưa kiểm tra được: mục {chan} chưa xác thực được đúng loại",
                nguon=[NguonDan(m) for m in chan],
            ))
            continue

        a = _lay_gia_tri(rule.get("nguon_a"), du_lieu, ngoai, context)
        b = _lay_gia_tri(rule.get("nguon_b"), du_lieu, ngoai, context)
        op = rule.get("op", "")

        # nguồn ngoài chưa có dữ liệu (MVP không tích hợp) -> ⚪ nhắc Maker tự tra
        if rule.get("nguon_ngoai") and (b is None):
            ket_qua.append(KetQuaQuyTac(
                rule["id"], rule["ten"], Muc.CHUA_KIEM,
                gia_tri_a=a,
                ly_do="Chưa kiểm tra được: cần dữ liệu ngoài hồ sơ (Core/BPM/lịch sử). Maker tự tra.",
            ))
            continue

        dat, ly_do = _so_sanh(op, a, b, tolerance_vnd)
        if dat is None:
            muc = Muc.CHUA_KIEM
        elif dat:
            muc = Muc.KHOP
        else:
            muc = _muc_khi_sai(rule)
        ket_qua.append(KetQuaQuyTac(rule["id"], rule["ten"], muc, a, b, ly_do,
                                    [NguonDan(m) for m in phu_thuoc]))
    return ket_qua
