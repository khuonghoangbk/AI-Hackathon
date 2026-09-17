// Anh xa muc -> class pill / icon / text (giu nguyen tu ban vanilla)
export const MUC_PILL = { xanh: "clean", vang: "warn", do: "risk", chua_kiem_tra_duoc: "trang", loi: "risk" };
export const MUC_ICON = { xanh: "🟢", vang: "🟡", do: "🔴", chua_kiem_tra_duoc: "⚪", loi: "⚠️" };
export const MUC_TEXT = { xanh: "Sạch", vang: "Cần chú ý", do: "Có rủi ro", chua_kiem_tra_duoc: "Chưa đủ độ phủ", loi: "Lỗi" };
export const TT_ICON = { xanh: "🟢", cam: "🟠", do: "🔴", khong_ap_dung: "—" };

export function fmtVND(n) {
  if (n == null) return "—";
  return n.toLocaleString("vi-VN") + " VND";
}

// Tach gia tri tu chuoi chi_tiet dang "fa=... vs fb=..."
export function extractValueFromDetail(detail, key) {
  if (!detail) return "—";
  const re = new RegExp(key + "=([^\\s]+(?:\\s[^=]*?)?)(?:\\svs\\s|$)");
  const m = detail.match(re);
  return m ? m[1].trim() : detail;
}

// Chuan hoa moi dang file upload -> mang tai lieu {ma_checklist, ...}
export function extractTaiLieu(parsed) {
  if (Array.isArray(parsed)) {
    return parsed.filter((x) => x && x.ma_checklist != null);
  }
  if (parsed && Array.isArray(parsed.tai_lieu)) {
    return parsed.tai_lieu.filter((x) => x && x.ma_checklist != null);
  }
  if (parsed && parsed.ma_checklist != null) {
    return [parsed];
  }
  return [];
}
