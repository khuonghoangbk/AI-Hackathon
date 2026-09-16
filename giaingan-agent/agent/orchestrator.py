"""Orchestrator: noi 7 buoc, nhan 1 ho so -> tra ket qua.
Dung chung cho Luong 1 (1 ho so) va Luong 3 (goi lap cho nhieu ho so)."""
from __future__ import annotations

from typing import Any

from . import (
    step1_context,
    step2_load_docs,
    step3_classify,
    step4_extract,
    step5_history,
    step6_crosscheck,
    step7_report,
)
from .config_loader import load_ho_so
from .llm_client import default_mode


def _merge_tai_lieu(goc: list[dict], thay_the: list[dict]) -> list[dict]:
    """Merge tai lieu thay the/bo sung vao ho so goc theo ma_checklist.

    - Neu ma_checklist da ton tai trong ho so goc -> thay the tai lieu do.
    - Neu ma_checklist chua co -> bo sung tai lieu moi.
    Ho so goc khong bi thay doi (tra ve list moi).
    """
    ket_qua = [dict(t) for t in goc]
    index_theo_ma = {
        str(t.get("ma_checklist")): i
        for i, t in enumerate(ket_qua)
        if t.get("ma_checklist") is not None
    }
    for tl in thay_the:
        ma = str(tl.get("ma_checklist")) if tl.get("ma_checklist") is not None else None
        if ma is not None and ma in index_theo_ma:
            ket_qua[index_theo_ma[ma]] = tl  # thay the
        else:
            ket_qua.append(tl)  # bo sung
            if ma is not None:
                index_theo_ma[ma] = len(ket_qua) - 1
    return ket_qua


def check_one(
    ho_so_id: str,
    mode: str | None = None,
    tai_lieu_thay_the: list[dict] | None = None,
) -> dict[str, Any]:
    """Chay 7 buoc Luong 1 cho 1 ho so.

    Args:
        ho_so_id: ma YCGN (GN-2026-xxx).
        mode: 'mock' hoac 'live'. None -> lay mac dinh tu RUN_MODE trong .env.
              Step3/4/6 goi LLM that khi mode='live', nguoc lai dung logic Python.
        tai_lieu_thay_the: danh sach tai lieu do TNTD upload (bo sung/thay the).
              Neu co -> merge vao ho so goc theo ma_checklist truoc khi chay.
              Ho so goc tren dia khong bi thay doi.

    Returns:
        dict chua ket qua toan bo 7 buoc + bao cao tong hop.
    """
    if mode is None:
        mode = default_mode()

    # Load ho so tu data_mock
    ho_so = load_ho_so(ho_so_id)

    # Neu co tai lieu thay the -> merge vao ban sao ho so goc (khong sua file goc)
    da_thay_the = bool(tai_lieu_thay_the)
    if da_thay_the:
        ho_so = dict(ho_so)
        ho_so["tai_lieu"] = _merge_tai_lieu(ho_so.get("tai_lieu", []), tai_lieu_thay_the)

    # ---- Buoc 1: Lay ngu canh ----
    ctx = step1_context.run(ho_so)

    # ---- Buoc 2: Load tai lieu ----
    docs = step2_load_docs.run(ho_so)

    # ---- Buoc 3: Phan loai (CUA CHAN) ----
    classify = step3_classify.run(ctx, docs, mode)

    # ---- Buoc 4: Trich xuat (chi muc xanh) ----
    extract = step4_extract.run(ctx, docs, classify, mode)

    # ---- Buoc 5: Tra lich su hoa don ----
    history = step5_history.run(extract)

    # ---- Buoc 6: Doi chieu cheo ----
    crosscheck = step6_crosscheck.run(extract, classify, history, mode)

    # ---- Buoc 7: Sinh bao cao ----
    report = step7_report.run(ctx, classify, extract, history, crosscheck)

    return {
        "ho_so_id": ho_so_id,
        "mode": mode,
        "da_thay_the": da_thay_the,
        "so_tai_lieu": len(ho_so.get("tai_lieu", [])),
        "buoc": {
            "b1_context": ctx,
            "b2_docs_count": len(docs),
            "b3_classify": classify,
            "b4_extract": extract,
            "b5_history": history,
            "b6_crosscheck": crosscheck,
        },
        "report": report,
    }


def check_batch(ho_so_ids: list[str] | None = None, mode: str | None = None) -> dict[str, Any]:
    """Luong 3: Hau kiem theo lo. Chay check_one cho nhieu ho so,
    tra bang xep hang rui ro."""
    from .config_loader import list_ho_so_ids

    if mode is None:
        mode = default_mode()
    if not ho_so_ids:
        ho_so_ids = list_ho_so_ids()

    results: list[dict] = []
    for hid in ho_so_ids:
        try:
            res = check_one(hid, mode)
            report = res["report"]
            # Tinh diem rui ro don gian: do x30 + vang x10 + trang x5
            stats = report["thong_ke"]
            diem = stats["do"] * 30 + stats["vang"] * 10 + stats["chua_kiem_tra_duoc"] * 5
            results.append(
                {
                    "ho_so_id": hid,
                    "muc_tong_the": report["muc_tong_the"],
                    "tom_tat": report["tom_tat"],
                    "diem_rui_ro": diem,
                    "thong_ke": stats,
                }
            )
        except Exception as e:
            results.append(
                {
                    "ho_so_id": hid,
                    "muc_tong_the": "loi",
                    "tom_tat": str(e),
                    "diem_rui_ro": -1,
                    "thong_ke": {},
                }
            )

    # Xep hang theo diem rui ro giam dan
    results.sort(key=lambda x: x.get("diem_rui_ro", 0), reverse=True)
    for idx, r in enumerate(results, 1):
        r["xep_hang"] = idx

    return {
        "tong_ho_so": len(results),
        "mode": mode,
        "bang_xep_hang": results,
    }
