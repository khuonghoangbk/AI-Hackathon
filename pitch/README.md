# Pitch deck — DisburseCheck (hạng mục 4c) · Đội Plutus

- Nguồn: `pitch-giaingan.html` (12 slide, khổ 16:9, sửa trực tiếp bằng text editor).
- Bản nộp: **xuất ra `pitch-giaingan.pdf`** rồi commit cả hai file lên repo.

## Cách xuất PDF (không cần cài gì)
1. Mở `pitch-giaingan.html` bằng Chrome hoặc Edge.
2. Nhấn **Ctrl+P** (Print).
3. Cấu hình:
   - Destination / Máy in: **Save as PDF**
   - Layout: **Landscape** (ngang)
   - Margins / Lề: **None**
   - Bật **Background graphics / In hình nền** (để giữ màu nền tối)
4. Save → đặt tên `pitch-giaingan.pdf` trong thư mục `pitch/`.

> CSS đã set mỗi slide = 1 trang khi in. Nếu bị tràn/lệch trang, thử để Scale = 100% hoặc "Fit to page width".

## Việc cần bổ sung trước khi nộp
- **Slide 8 (Demo):** thay 2 ô placeholder bằng ảnh chụp màn hình thật sau khi deploy
  (kết quả 🟢🟡🔴 có dẫn nguồn + modal 2 trang tài liệu cạnh nhau).
- **Slide 8 (footer) & lời thoại:** điền **link endpoint demo** thật sau khi deploy AgentBase + web.
- **Slide 9 (Impact):** nếu đơn vị cấp **đơn giá giờ công**, bổ sung dòng AEV bằng tiền = giờ tiết kiệm/năm × đơn giá. Chưa có thì giữ nguyên cách trình bằng giờ công + năng lực xử lý.
- **Tên sản phẩm:** **DisburseCheck** (Plutus là tên đội, để ở dòng thành viên). Muốn đổi thì sửa ở slide 1 (`<h1>` + `<title>`) và các footer.

## Số liệu trong deck lấy từ đâu
Toàn bộ số (486 hồ sơ/ngày, 364 giờ/ngày, 102 nhân sự, 44% trả lại, ~121.500 hồ sơ/năm,
~27.000 giờ/năm, 486→694) trích từ `giaingan-thuchien.md` mục F2 (bám tiêu chí R × I × C).
Số giờ tiết kiệm là **ước tính theo kịch bản giảm 30%**, không phải kết quả đã đo — deck đã ghi rõ.
