"""
LLM client goi GreenNode MaaS (OpenAI-compatible).

Mot client, doi model qua tham so. Hai ham tien ich:
- extract_json(): tra ve JSON co schema (dung cho phan loai/trich xuat)
- reason():       di...en giai/doi chieu (tra ve text)

Ho tro RUN_MODE=mock: khong goi LLM that, dung cho demo luong end-to-end.
Khi RUN_MODE=live: goi endpoint MaaS theo cau hinh .env.
"""
from __future__ import annotations

import json
import os
from typing import Any


class LLMClient:
    def __init__(self) -> None:
        self.run_mode = os.getenv("RUN_MODE", "mock").lower()
        self.api_base = os.getenv("GREENNODE_API_BASE", "")
        self.api_key = os.getenv("GREENNODE_API_KEY", "")
        self.model_reasoning = os.getenv("MODEL_REASONING", "glm-5.2")
        self.model_fast = os.getenv("MODEL_FAST", "qwen-flash-3.6")
        self._client = None

        if self.run_mode == "live":
            # Import tre de moi truong mock khong bat buoc cai openai
            from openai import OpenAI

            self._client = OpenAI(base_url=self.api_base, api_key=self.api_key)

    # ---- API cong khai -------------------------------------------------
    def extract_json(self, prompt: str, *, fast: bool = True) -> dict[str, Any]:
        """Goi model tra ve JSON. O mock tra {} de caller tu fallback."""
        if self.run_mode == "mock" or self._client is None:
            return {}
        model = self.model_fast if fast else self.model_reasoning
        resp = self._client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Ban tra ve DUY NHAT mot JSON hop le, khong giai thich."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
        content = resp.choices[0].message.content or "{}"
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {}

    def reason(self, prompt: str) -> str:
        """Goi model reasoning (GLM) de dien giai. O mock tra chuoi rong."""
        if self.run_mode == "mock" or self._client is None:
            return ""
        resp = self._client.chat.completions.create(
            model=self.model_reasoning,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return resp.choices[0].message.content or ""


# Singleton tien dung
_client: LLMClient | None = None


def get_client() -> LLMClient:
    global _client
    if _client is None:
        _client = LLMClient()
    return _client
