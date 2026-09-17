// Client goi API backend. Base URL lay tu tham so (cho phep sua o thanh API tren UI).
export function normalizeBase(base) {
  return (base || "").replace(/\/+$/, "");
}

export async function callApi(base, path, opts = {}) {
  const res = await fetch(normalizeBase(base) + path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      detail = (await res.json()).detail || detail;
    } catch (_) {}
    throw new Error(`(${res.status}) ${detail}`);
  }
  return res.json();
}

// Base mac dinh cho API:
//  - Neu build co dat VITE_API_BASE -> dung gia tri do.
//  - Neu dang chay dev (vite dev server) -> tro sang backend cong 8000.
//  - Neu chay production (FE duoc FastAPI serve chung cong) -> dung same-origin ("").
export const DEFAULT_API_BASE =
  import.meta.env.VITE_API_BASE ??
  (import.meta.env.DEV ? "http://localhost:8000" : "");
