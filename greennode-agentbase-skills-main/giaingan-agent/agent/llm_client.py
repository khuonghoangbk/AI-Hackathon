"""LLM client gọi GreenNode MaaS qua chuẩn OpenAI-compatible.

Một client, đổi model qua tham số:
  - MODEL_FAST      (Qwen Flash): OCR, phân loại nhanh
  - MODEL_REASONING (GLM 5.2):    đối chiếu, suy luận, diễn giải

Hai hàm tiện ích:
  - extract_json(): trả về JSON có schema (phân loại, trích xuất)
  - reason():       đối chiếu / diễn giải văn bản
"""
from __future__ import annotations

import json
import os

try:
    from openai import OpenAI
except ImportError:  # cho phép import skeleton khi chưa cài dependency
    OpenAI = None  # type: ignore


class LLMClient:
    def __init__(self) -> None:
        self.base_url = os.getenv("GREENNODE_API_BASE", "")
        self.api_key = os.getenv("GREENNODE_API_KEY", "")
        self.model_fast = os.getenv("MODEL_FAST", "qwen-flash-3.6")
        self.model_reasoning = os.getenv("MODEL_REASONING", "glm-5.2")
        self._client = None
        if OpenAI is not None and self.base_url and self.api_key:
            self._client = OpenAI(base_url=self.base_url, api_key=self.api_key)

    @property
    def san_sang(self) -> bool:
        return self._client is not None

    def extract_json(self, prompt: str, *, dung_model_manh: bool = False,
                     system: str | None = None) -> dict:
        """Gọi model, ép trả JSON. Dùng cho phân loại (bước 3) và trích xuất (bước 4)."""
        model = self.model_reasoning if dung_model_manh else self.model_fast
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        resp = self._client.chat.completions.create(  # type: ignore[union-attr]
            model=model,
            messages=messages,
            temperature=0,
            response_format={"type": "json_object"},
        )
        return json.loads(resp.choices[0].message.content or "{}")

    def reason(self, prompt: str, *, system: str | None = None) -> str:
        """Gọi model mạnh để đối chiếu / diễn giải (bước 6, 7)."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        resp = self._client.chat.completions.create(  # type: ignore[union-attr]
            model=self.model_reasoning,
            messages=messages,
            temperature=0.2,
        )
        return resp.choices[0].message.content or ""


# Singleton tiện dùng
_client: LLMClient | None = None


def get_client() -> LLMClient:
    global _client
    if _client is None:
        _client = LLMClient()
    return _client
