"""Smoke test offline: stub LLM phân loại 'đúng loại đã khai' để kiểm tra
logic đối chiếu chéo và cơ chế cửa chặn mà không cần gọi MaaS thật.

Chạy: python smoke_test.py
"""
from __future__ import annotations

from agent import llm_client
from agent.orchestrator import check_by_id, ket_qua_to_dict


class StubLLM:
    """Giả lập: luôn nhận dạng đúng mã đã khai, trừ khi nội dung có cờ _tieu_de_thuc_te."""
    san_sang = True

    def extract_json(self, prompt: str, **kwargs) -> dict:
        # Nếu nội dung là loại khác (case sai loại), trả điểm thấp + loại khác.
        if "_tieu_de_thuc_te" in prompt:
            return {"loai_phu_hop_nhat": "ngoai_checklist", "diem_tin_cay": 0.2, "can_cu": []}
        # Lấy mã checklist đầu tiên trong tập ứng viên làm "loại phù hợp nhất".
        # Prompt chứa list mã; ta suy ra mã của tài liệu hiện tại từ trường bắt buộc.
        return {"loai_phu_hop_nhat": _doan_ma(prompt), "diem_tin_cay": 0.95, "can_cu": ["stub"]}

    def reason(self, prompt: str, **kwargs) -> str:
        return ""


def _doan_ma(prompt: str) -> str:
    # Heuristic đơn giản cho stub: match theo trường đặc trưng trong nội dung.
    if "so_hoa_don" in prompt:
        return "3455"
    if "so_cong_no_phai_tra" in prompt or "ky_doi_chieu" in prompt:
        return "3458"
    if "gia_tri_hop_dong" in prompt or "so_hop_dong" in prompt:
        return "34231"
    if "ky_luong" in prompt or "tong_thuc_nhan" in prompt:
        return "3451"
    if "tong_so_tien_lo" in prompt or "so_luong_lenh" in prompt:
        return "3453"
    if "ten_nguoi_thu_huong" in prompt or "so_tk_thu_huong" in prompt:
        return "3472"
    if "ngay_nhan_no" in prompt or "limit_id" in prompt:
        return "3471"
    return "ngoai_checklist"


def _in_ket_qua(ho_so_id: str) -> None:
    kq = check_by_id(ho_so_id, "data_mock")
    d = ket_qua_to_dict(kq)
    print(f"\n=== {ho_so_id} ({d['loai_giai_ngan']}) — tổng: {d['muc_tong_hop']} ===")
    print("  do_phu:", d["do_phu"])
    for q in d["quy_tac"]:
        if q["muc"] in ("🔴", "⚪"):
            print(f"  {q['muc']} {q['rule_id']}: {q['ten']} — {q['ly_do']}")


if __name__ == "__main__":
    # Cắm stub thay cho client thật
    llm_client._client = StubLLM()  # type: ignore[assignment]

    for hid in ["P1_CLEAN001", "P1_HS001", "P3_HS001", "P1_SAILOAI001"]:
        _in_ket_qua(hid)
