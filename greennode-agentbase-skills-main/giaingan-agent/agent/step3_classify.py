"""[3] Xác thực loại tài liệu — CỬA CHẶN (mục 3.7).

Hai lớp:
  Lớp 1 - Nhận dạng loại: tập ứng viên = các mục checklist đang xét + 'ngoai_checklist'.
  Lớp 2 - Kiểm cấu trúc: có tìm được truong_bat_buoc của loại đó không?

Ba trạng thái đầu ra: 🟢 XAC_THUC / 🟠 CHUA_XAC_THUC / 🔴 THIEU.
Mục 🟠 sẽ chặn bước 4 và làm quy tắc phụ thuộc trả ⚪ ở bước 6.

Ngưỡng hạ theo voucherType (scan/bản mềm → ngưỡng thấp hơn).
KHÔNG dùng tên file làm căn cứ phân loại.
"""
from __future__ import annotations

from typing import Any

from .llm_client import LLMClient
from .models import KetQuaXacThuc, TrangThaiMuc

_SYSTEM = (
    "Bạn là trợ lý nghiệp vụ ngân hàng. Nhiệm vụ: xác định nội dung tài liệu có "
    "đúng loại đã khai hay không, chỉ chọn trong tập ứng viên được cung cấp. "
    "Trả JSON: {loai_phu_hop_nhat, diem_tin_cay(0..1), can_cu[]}."
)


def _nguong_theo_voucher(nguong_goc: float, voucher_type: str,
                         voucher_conf: dict) -> float:
    he_so = voucher_conf.get(voucher_type, {}).get("he_so_nguong", 1.0)
    return nguong_goc * he_so


def _lop1_nhan_dang(llm: LLMClient, noi_dung: dict, ung_vien: list[str]) -> dict:
    """Gọi model phân loại. Trả {loai_phu_hop_nhat, diem_tin_cay, can_cu}."""
    if not llm.san_sang:
        # Fallback offline: suy đoán thô từ khóa nội dung (chỉ để skeleton chạy được).
        return {"loai_phu_hop_nhat": "", "diem_tin_cay": 0.0, "can_cu": []}
    prompt = (
        f"Tập ứng viên loại tài liệu (mã checklist): {ung_vien + ['ngoai_checklist']}\n"
        f"Nội dung tài liệu (đã trích/OCR): {noi_dung}\n"
        "Xác định loại phù hợp nhất."
    )
    return llm.extract_json(prompt, system=_SYSTEM)


def _lop2_kiem_cau_truc(noi_dung: dict, sig: dict) -> list[str]:
    """Trả danh sách trường bắt buộc KHÔNG tìm được."""
    bat_buoc = sig.get("truong_bat_buoc", [])
    return [t for t in bat_buoc if t not in noi_dung or noi_dung.get(t) in (None, "", "N/A")]


def run(llm: LLMClient, context: dict[str, Any], bang_tra: dict) -> list[KetQuaXacThuc]:
    checklist = bang_tra["checklist"]
    doc_sig = bang_tra["doc_signatures"]
    voucher_conf = bang_tra["voucher_confidence"]

    ma_trong_checklist = [m["ma_checklist"] for m in checklist["muc"]]
    tai_lieu_theo_ma = {t["ma_checklist"]: t for t in context["tai_lieu"]}

    ket_qua: list[KetQuaXacThuc] = []
    for muc in checklist["muc"]:
        ma = muc["ma_checklist"]
        tl = tai_lieu_theo_ma.get(ma)

        # 🔴 chưa có tài liệu — báo thiếu theo phân tầng bắt buộc/điều kiện ở bước 7
        if tl is None:
            if muc.get("bat_buoc") == "co":
                ket_qua.append(KetQuaXacThuc(ma, TrangThaiMuc.THIEU, ly_do="Chưa có tài liệu"))
            continue

        noi_dung = tl.get("noi_dung_mo_phong", {})
        sig = doc_sig.get(ma, {})
        nguong = sig.get("nguong_dat", {})
        nguong_diem = _nguong_theo_voucher(
            nguong.get("diem_tin_cay_toi_thieu", 0.75),
            tl.get("voucher_type", "1"), voucher_conf,
        )

        lop1 = _lop1_nhan_dang(llm, noi_dung, ma_trong_checklist)
        diem = float(lop1.get("diem_tin_cay", 0.0))
        loai_nhan = str(lop1.get("loai_phu_hop_nhat", ""))
        truong_thieu = _lop2_kiem_cau_truc(noi_dung, sig)
        so_bb_toi_thieu = nguong.get("so_truong_bat_buoc_toi_thieu", 0)
        du_truong = (len(sig.get("truong_bat_buoc", [])) - len(truong_thieu)) >= so_bb_toi_thieu

        # đúng loại + đủ trường + đạt ngưỡng → 🟢
        if loai_nhan == ma and diem >= nguong_diem and du_truong:
            ket_qua.append(KetQuaXacThuc(ma, TrangThaiMuc.XAC_THUC, diem, loai_nhan,
                                         lop1.get("can_cu", [])))
        else:
            ly_do = "Chưa xác thực được đúng loại"
            if loai_nhan and loai_nhan != ma and loai_nhan != "ngoai_checklist":
                ly_do = f"Nội dung có vẻ là loại {loai_nhan}, không phải {ma}"
            elif not du_truong:
                ly_do = f"Thiếu trường bắt buộc: {truong_thieu}"
            ket_qua.append(KetQuaXacThuc(ma, TrangThaiMuc.CHUA_XAC_THUC, diem, loai_nhan,
                                         lop1.get("can_cu", []), truong_thieu, ly_do))
    return ket_qua


def ds_muc_khong_xac_thuc(ket_qua: list[KetQuaXacThuc]) -> list[str]:
    """Danh sách mã checklist ở trạng thái 🟠 — dùng làm điều kiện chặn ở bước 6."""
    return [k.ma_checklist for k in ket_qua if k.trang_thai == TrangThaiMuc.CHUA_XAC_THUC]
