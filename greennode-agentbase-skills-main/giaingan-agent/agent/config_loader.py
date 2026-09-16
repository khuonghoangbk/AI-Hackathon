"""Nạp cấu hình nghiệp vụ (Luồng 0).

Dựng bảng tra theo loại giải ngân:
  loai_giai_ngan -> checklist (mã checklist BPM)
                 -> dấu hiệu nhận dạng + trường bắt buộc
                 -> quy tắc chung + quy tắc riêng
"""
from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path

CONFIG_DIR = Path(os.getenv("CONFIG_DIR", Path(__file__).resolve().parent.parent / "config"))


def _doc(ten: str) -> dict:
    with open(Path(CONFIG_DIR) / ten, encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=None)
def load_checklist(loai: str) -> dict:
    """checklist_P1.json / checklist_P3.json."""
    return _doc(f"checklist_{loai}.json")


@lru_cache(maxsize=None)
def load_voucher_confidence() -> dict:
    return _doc("voucher_confidence.json")


@lru_cache(maxsize=None)
def load_doc_signatures() -> dict:
    return _doc("doc_signatures.json")


@lru_cache(maxsize=None)
def load_rules(loai: str) -> list[dict]:
    """Gộp quy tắc chung + quy tắc riêng theo loại giải ngân."""
    chung = _doc("rules_common.json")["rules"]
    rieng = _doc(f"rules_{loai}.json")["rules"]
    return chung + rieng


def tolerance_vnd() -> int:
    return int(os.getenv("TOLERANCE_VND", "1000"))


def bang_tra(loai: str) -> dict:
    """Bảng tra tổng hợp cho một loại giải ngân."""
    return {
        "loai": loai,
        "checklist": load_checklist(loai),
        "doc_signatures": load_doc_signatures(),
        "voucher_confidence": load_voucher_confidence(),
        "rules": load_rules(loai),
        "tolerance_vnd": tolerance_vnd(),
    }
