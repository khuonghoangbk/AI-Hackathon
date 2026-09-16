"""[2] Lấy tài liệu.

MVP đọc file từ data_mock/. Trừu tượng hóa qua interface DocumentSource
để sau này thay bằng ECM API mà không sửa các bước khác.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Protocol


class DocumentSource(Protocol):
    """Nguồn tài liệu. Bản thật: ECM API. Bản MVP: file JSON."""

    def load_ho_so(self, ho_so_id: str) -> dict[str, Any]:
        ...


class MockDocumentSource:
    """Đọc hồ sơ mô phỏng từ data_mock/. Tìm trong cả 3 nhóm thư mục."""

    def __init__(self, data_dir: str | Path) -> None:
        self.data_dir = Path(data_dir)
        self._nhom = ["ho_so_sach", "ho_so_co_sai_lech", "ho_so_bien"]

    def load_ho_so(self, ho_so_id: str) -> dict[str, Any]:
        for nhom in self._nhom:
            p = self.data_dir / nhom / f"{ho_so_id}.json"
            if p.exists():
                with open(p, encoding="utf-8") as f:
                    return json.load(f)
        raise FileNotFoundError(f"Không tìm thấy hồ sơ {ho_so_id} trong data_mock/")

    def list_ho_so(self) -> list[str]:
        """Liệt kê toàn bộ hồ sơ (dùng cho Luồng 3 hậu kiểm theo lô)."""
        ids: list[str] = []
        for nhom in self._nhom:
            d = self.data_dir / nhom
            if d.exists():
                ids += [p.stem for p in d.glob("*.json")]
        return sorted(ids)


def run(source: DocumentSource, ho_so_id: str) -> dict[str, Any]:
    return source.load_ho_so(ho_so_id)
