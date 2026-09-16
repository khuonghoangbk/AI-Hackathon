"""Nap cau hinh nghiep vu (Luong 0) va du lieu mock."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
DATA_DIR = ROOT / "data_mock"

_HO_SO_DIRS = ["ho_so_sach", "ho_so_co_sai_lech", "ho_so_dac_thu"]


def _read_json(path: Path) -> dict | list:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=None)
def load_checklist() -> dict:
    return _read_json(CONFIG_DIR / "checklist_P1.json")


@lru_cache(maxsize=None)
def load_voucher_confidence() -> dict:
    return _read_json(CONFIG_DIR / "voucher_confidence.json")


@lru_cache(maxsize=None)
def load_doc_signatures() -> dict:
    return _read_json(CONFIG_DIR / "doc_signatures.json")


@lru_cache(maxsize=None)
def load_rules() -> dict:
    return _read_json(CONFIG_DIR / "rules_P1.json")


@lru_cache(maxsize=None)
def load_khoan_vay() -> dict:
    return _read_json(DATA_DIR / "khoan_vay.json")


@lru_cache(maxsize=None)
def load_lich_su_hoa_don() -> dict:
    return _read_json(DATA_DIR / "lich_su_hoa_don.json")


def load_ho_so(ho_so_id: str) -> dict:
    """Tim file ho so theo id trong ca 3 nhom."""
    for d in _HO_SO_DIRS:
        path = DATA_DIR / d / f"{ho_so_id}.json"
        if path.exists():
            return _read_json(path)
    raise FileNotFoundError(f"Khong tim thay ho so: {ho_so_id}")


def list_ho_so_ids() -> list[str]:
    ids: list[str] = []
    for d in _HO_SO_DIRS:
        folder = DATA_DIR / d
        if folder.exists():
            ids.extend(p.stem for p in folder.glob("*.json"))
    return sorted(ids)
