"""[7] Sinh kết quả kiểm tra sơ bộ.

- Phân 4 mức 🟢🟡🔴⚪, mỗi điểm kèm dẫn nguồn.
- ĐẾM RIÊNG số quy tắc ⚪ và nêu lý do → cho biết độ phủ của lần kiểm tra.
- Phân loại mức độ cần chú ý của cả hồ sơ.
- Luôn kèm câu chốt: trợ lý không kết luận đủ điều kiện giải ngân.
"""
from __future__ import annotations

from .models import KetQuaHoSo, KetQuaQuyTac, KetQuaXacThuc, Muc, TrangThaiMuc


def _muc_tong_hop(quy_tac: list[KetQuaQuyTac]) -> Muc:
    mucs = {q.muc for q in quy_tac}
    if Muc.LECH in mucs:
        return Muc.LECH
    if Muc.CHU_Y in mucs:
        return Muc.CHU_Y
    if Muc.CHUA_KIEM in mucs and Muc.KHOP not in mucs:
        return Muc.CHUA_KIEM
    return Muc.KHOP


def run(ho_so_id: str, loai_giai_ngan: str, xac_thuc: list[KetQuaXacThuc],
        quy_tac: list[KetQuaQuyTac]) -> KetQuaHoSo:
    thieu = [k.ma_checklist for k in xac_thuc if k.trang_thai == TrangThaiMuc.THIEU]

    dem = {m.name: 0 for m in Muc}
    for q in quy_tac:
        dem[q.muc.name] += 1

    tong = len(quy_tac)
    khop = dem["KHOP"]
    chu_y = dem["CHU_Y"]
    lech = dem["LECH"]
    chua = dem["CHUA_KIEM"]

    dien_giai = (
        f"{tong} nội dung được đối chiếu. "
        f"{khop} khớp, {chu_y} cần chú ý, {lech} lệch, "
        f"{chua} chưa đối chiếu được."
    )
    if chua:
        ly_do_chua = sorted({q.ly_do for q in quy_tac if q.muc == Muc.CHUA_KIEM})
        dien_giai += " Lý do chưa đối chiếu được: " + "; ".join(ly_do_chua)

    return KetQuaHoSo(
        ho_so_id=ho_so_id,
        loai_giai_ngan=loai_giai_ngan,
        muc_tong_hop=_muc_tong_hop(quy_tac),
        xac_thuc=xac_thuc,
        quy_tac=quy_tac,
        thieu_tai_lieu=thieu,
        do_phu={"tong": tong, "khop": khop, "chu_y": chu_y, "lech": lech, "chua_kiem": chua},
        dien_giai=dien_giai,
    )
