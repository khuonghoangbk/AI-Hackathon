"""
LLM client goi GreenNode MaaS (OpenAI-compatible).

Mot client, doi model qua tham so. Hai ham tien ich:
- extract_json(): tra ve JSON co schema (dung cho phan loai/trich xuat)
- reason():       di...en giai/doi chieu (tra ve text)

Che do (mode) truyen theo TUNG LOI GOI (per-request), khong doc env mot lan:
- mode='mock': KHONG goi LLM that. Tra ve gia tri rong de caller tu fallback
               ve logic Python / du lieu mock.
- mode='live': goi endpoint MaaS that theo cau hinh .env. Neu thieu key -> loi ro rang.

RUN_MODE trong .env chi con la GIA TRI MAC DINH khi request khong truyen mode.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

# Tu nap file .env o thu muc goc repo (giaingan-agent/.env) neu co python-dotenv.
try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

MOCK = "mock"
LIVE = "live"


def default_mode() -> str:
    return os.getenv("RUN_MODE", MOCK).lower()


class LLMConfigError(RuntimeError):
    """Bat khi mode=live nhung thieu cau hinh key/endpoint."""


class LLMClient:
    def __init__(self) -> None:
        self.api_base = os.getenv("GREENNODE_API_BASE", "")
        self.api_key = os.getenv("GREENNODE_API_KEY", "")
        self.model_reasoning = os.getenv("MODEL_REASONING", "glm-5.2")
        self.model_fast = os.getenv("MODEL_FAST", "qwen-flash-3.6")
        self._client = None

    def _ensure_live_client(self):
        """Khoi tao client that (chi khi live). Import tre de moi truong mock
        khong bat buoc cai thu vien openai."""
        if not self.api_base or not self.api_key or "<" in self.api_base:
            raise LLMConfigError(
                "RUN_MODE=live nhung chua cau hinh GREENNODE_API_BASE/GREENNODE_API_KEY trong .env"
            )
        if self._client is None:
            try:
                from openai import OpenAI
            except ImportError as e:
                raise LLMConfigError(
                    "Thieu thu vien 'openai'. Cai bang: pip install openai"
                ) from e
            self._client = OpenAI(base_url=self.api_base, api_key=self.api_key)
        return self._client

    # ---- API cong khai -------------------------------------------------
    def extract_json(self, prompt: str, *, fast: bool = True, mode: str = MOCK) -> dict[str, Any]:
        """Goi model tra ve JSON. O mock tra {} de caller tu fallback."""
        if mode != LIVE:
            return {}
        client = self._ensure_live_client()
        model = self.model_fast if fast else self.model_reasoning
        resp = client.chat.completions.create(
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

    def reason(self, prompt: str, *, mode: str = MOCK) -> str:
        """Goi model reasoning (GLM) de dien giai. O mock tra chuoi rong."""
        if mode != LIVE:
            return ""
        client = self._ensure_live_client()
        resp = client.chat.completions.create(
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
