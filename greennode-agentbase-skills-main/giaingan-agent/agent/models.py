"""Kiểu dữ liệu dùng chung giữa các bước.

Bốn mức kết quả (mục 3.2 giaingan-flow.md):
  🟢 khop        - đã đối chiếu khớp
  🟡 chu_y       - cần chú ý, có thể có lý do hợp lệ
  🔴 lech        - lệch chắc chắn, phải xử lý
  ⚪ chua_kiem   - chưa kiểm tra được (nguồn chưa xác thực / thiếu trường)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Muc(str, Enum):
    """Mức cảnh báo của một quy tắc / một điểm phát hiện."""
    KHOP = "🟢"
    CHU_Y = "🟡"
    LECH = "🔴"
    CHUA_KIEM = "⚪"


class TrangThaiMuc(str, Enum):
    """Ba trạng thái của một mục checklist sau bước 3 (mục 3.7.1)."""
    XAC_THUC = "🟢"        # có file, đã xác thực đúng loại
    CHUA_XAC_THUC = "🟠"   # có file, chưa xác thực được đúng loại
    THIEU = "🔴"           # chưa có tài liệu


@dataclass
class NguonDan:
    """Dẫn nguồn cho một phát hiện: tài liệu + trang + vị trí."""
    ma_checklist: str
    ten_file: str = ""
    trang: int | None = None
    vi_tri: str = ""


@dataclass
class KetQuaXacThuc:
    """Kết quả xác thực loại tài liệu của một mục (bước 3)."""
    ma_checklist: str
    trang_thai: TrangThaiMuc
    diem_tin_cay: float = 0.0
    loai_nhan_dang: str = ""
    can_cu: list[str] = field(default_factory=list)
    truong_thieu: list[str] = field(default_factory=list)
    ly_do: str = ""


@dataclass
class KetQuaQuyTac:
    """Kết quả áp một quy tắc đối chiếu chéo (bước 6)."""
    rule_id: str
    ten: str
    muc: Muc
    gia_tri_a: Any = None
    gia_tri_b: Any = None
    ly_do: str = ""
    nguon: list[NguonDan] = field(default_factory=list)


@dataclass
class KetQuaHoSo:
    """Kết quả kiểm tra sơ bộ toàn hồ sơ (bước 7)."""
    ho_so_id: str
    loai_giai_ngan: str
    muc_tong_hop: Muc = Muc.KHOP
    xac_thuc: list[KetQuaXacThuc] = field(default_factory=list)
    quy_tac: list[KetQuaQuyTac] = field(default_factory=list)
    thieu_tai_lieu: list[str] = field(default_factory=list)
    do_phu: dict[str, int] = field(default_factory=dict)
    dien_giai: str = ""
    cau_chot: str = "Trợ lý không kết luận hồ sơ đủ điều kiện giải ngân."
