"""[2] Load docs: MVP doc tu data_mock/. Truu tuong hoa qua interface DocumentSource
de sau nay thay bang ECM API ma khong doi orchestrator."""
from __future__ import annotations

from typing import Any, Protocol


class DocumentSource(Protocol):
    def load(self, ho_so: dict) -> list[dict[str, Any]]:
        ...


class MockDocumentSource:
    """Nguon tai lieu gia lap: doc thang tu JSON ho so."""

    def load(self, ho_so: dict) -> list[dict[str, Any]]:
        docs: list[dict[str, Any]] = []
        for idx, t in enumerate(ho_so.get("tai_lieu", [])):
            docs.append(
                {
                    "doc_id": f"{ho_so['ho_so_id']}_D{idx + 1}",
                    "ma_checklist_khai": t["ma_checklist"],
                    "voucher_type": t.get("voucher_type"),
                    "so_trang": t.get("so_trang"),
                    "noi_dung": t.get("noi_dung", {}),
                    "thoa_man_muc": t.get("thoa_man_muc", [t["ma_checklist"]]),
                }
            )
        return docs


# Interface ECM that (chua hien thuc trong MVP)
class EcmDocumentSource:
    def load(self, ho_so: dict) -> list[dict[str, Any]]:  # pragma: no cover
        raise NotImplementedError("Tich hop ECM API o giai doan sau MVP")


def run(ho_so: dict, source: DocumentSource | None = None) -> list[dict[str, Any]]:
    source = source or MockDocumentSource()
    return source.load(ho_so)
