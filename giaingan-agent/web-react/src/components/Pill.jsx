import { MUC_PILL, MUC_ICON, MUC_TEXT } from "../lib/constants.js";

// Pill ket qua cho cot "Ket qua tro ly"
export function KetQuaPill({ kq }) {
  if (!kq) return <span className="pill idle">Chưa kiểm tra</span>;
  const hau = kq.daThayThe ? " (sau thay thế)" : "";
  return (
    <span className={`pill ${MUC_PILL[kq.muc]}`}>
      {MUC_ICON[kq.muc]} {MUC_TEXT[kq.muc]}
      {hau}
    </span>
  );
}

export function MucPill({ muc }) {
  return (
    <span className={`pill ${MUC_PILL[muc]}`}>
      {MUC_ICON[muc]} {MUC_TEXT[muc]}
    </span>
  );
}
