# Bộ hồ sơ thay thế mẫu (demo)

Dùng cho tab **Chi tiết & Kiểm tra sơ bộ** → khu vực "Hồ sơ thay thế / bổ sung (TNTD)".

## Mục đích
Mô phỏng TNTD upload chứng từ thay thế/bổ sung để sửa các lỗi của hồ sơ gốc
**GN-2026-000481** (nhóm có sai lệch), rồi chạy lại "Kiểm tra sơ bộ trên hồ sơ thay thế"
→ kết quả chuyển từ 🔴 **Có rủi ro** sang 🟢 **Sạch**.

## Danh sách file

| File | Mã checklist | Loại | Sửa lỗi gì |
|---|---|---|---|
| `GN-2026-000481_3471_giay_nhan_no.json` | 3471 | Thay thế | R1 — số tiền 500tr khớp đề nghị |
| `GN-2026-000481_3472_uy_nhiem_chi.json` | 3472 | Thay thế | R1 (số tiền) + R3 (người thụ hưởng) |
| `GN-2026-000481_34231_hop_dong_kinh_te.json` | 34231 | Thay thế | Khai đúng loại (gốc khai sai) + R5 |
| `GN-2026-000481_3455_hoa_don.json` | 3455 | Thay thế | R2 (số tiền) + R7 (hóa đơn mới, chưa dùng lại) |
| `GN-2026-000481_3458_bien_ban_doi_chieu_cong_no.json` | 3458 | Bổ sung | Bổ sung tài liệu đang thiếu |
| `GN-2026-000481_bo_day_du.json` | (cả 5) | Gộp | Chọn 1 file thay cho 5 file lẻ |

## Cách demo
1. Mở hồ sơ **GN-2026-000481** ở tab 1 → tab Chi tiết.
2. Bấm **▶ Kiểm tra sơ bộ** → cột trái hiện 🔴 (4 đỏ).
3. Bấm **📎 Chọn file .json** → chọn **5 file lẻ** (hoặc chỉ 1 file `_bo_day_du.json`).
4. Bấm **▶ Kiểm tra sơ bộ trên hồ sơ thay thế** → cột phải hiện 🟢 (7/7 xanh, độ phủ 100%).

> Lưu ý: hồ sơ gốc trên đĩa không bị thay đổi. Việc merge chỉ diễn ra trong bộ nhớ khi chạy kiểm tra.
