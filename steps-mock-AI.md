# Luồng "Kiểm tra sơ bộ" (Tab 2 / Luồng 1) — Mock vs AI

Khi bấm nút **"▶ Kiểm tra sơ bộ"** ở Tab 2 "Chi tiết & Kiểm tra sơ bộ (Luồng 1)", giao diện gọi API `POST /check {ho_so_id, mode, [tai_lieu_thay_the]}`. Backend chạy orchestrator `check_one()` gồm **7 bước tuần tự** (output bước trước là input bước sau).

- **Input chung của cả luồng:** mã YCGN (`ho_so_id`) + chế độ (`mock` | `live`) + (tùy chọn) tài liệu thay thế/bổ sung do TNTD upload.
- **Output chung của cả luồng:** báo cáo kiểm tra sơ bộ ở B7 — dùng để hiển thị lên màn hình và tô màu kết quả (🟢🟡🔴⚪) cho hồ sơ.

## AI tham gia ở đâu?

AI **chỉ tham gia ở 3 bước: B3, B4 và B6**. Bốn bước còn lại (B1, B2, B5, B7) chạy logic Python thuần và **giống hệt nhau** ở cả chế độ mock và AI.

| Bước có AI | Model gọi | Chức năng của AI |
|------------|-----------|------------------|
| **B3** | Qwen Flash (`qwen-flash-3.6`) | Chấm điểm tin cậy loại tài liệu (nhận dạng đúng loại hay không) |
| **B4** | Qwen Flash (`qwen-flash-3.6`) | Bóc tách các trường bắt buộc từ nội dung tài liệu |
| **B6** | GLM reasoning (`glm-5.2`) | Suy luận mục đích vay có phù hợp nội dung hàng hóa không |

> Mọi lời gọi AI đều có **fallback an toàn** về logic mock nếu lỗi/thiếu key, nên output luôn giữ đúng cấu trúc, không vỡ giao diện.

## Bảng chi tiết 7 bước

| Bước | Tên bước | Input (dữ liệu đầu vào) | Output (dữ liệu đầu ra) | Mock thực hiện gì | AI (live) — model & chức năng |
|------|----------|--------------------------|--------------------------|-------------------|-------------------------------|
| **B1** | Lấy ngữ cảnh hồ sơ | Thông tin khoản vay của YCGN: loại giải ngân, khách hàng vay, số tiền đề nghị, mục đích sử dụng vốn, danh sách tài liệu khách khai nộp | Bức tranh ngữ cảnh của hồ sơ để các bước sau đối chiếu (số tiền đề nghị, mục đích vay, danh mục tài liệu khai báo) | Đọc trực tiếp thông tin khoản vay | **Giống mock** — không gọi AI |
| **B2** | Load tài liệu | Danh sách tài liệu trong hồ sơ (mỗi tài liệu kèm loại chứng từ, số trang, nội dung) | Bộ tài liệu đã chuẩn hóa, sẵn sàng để phân loại và trích xuất | Đọc thẳng tài liệu từ hồ sơ | **Giống mock** — không gọi AI |
| **B3** | Phân loại tài liệu (CỬA CHẶN) | Danh mục checklist hồ sơ P1, dấu hiệu nhận dạng từng loại tài liệu, độ tin cậy theo loại chứng từ (bản scan/bản mềm), và tài liệu khách nộp | Trạng thái từng mục checklist: 🟢 đã xác thực / 🟠 chưa xác thực / 🔴 thiếu file, kèm lý do | So khớp dấu hiệu nhận dạng để chấm điểm loại tài liệu | **Qwen Flash**: đọc nội dung tài liệu và tự chấm điểm tin cậy xem có đúng loại không |
| **B4** | Trích xuất thông tin | Các tài liệu đã được xác thực (🟢) ở B3 | Các trường nghiệp vụ đã bóc tách: số tiền đề nghị, người thụ hưởng, giá trị hợp đồng, tổng giá trị hóa đơn, bên bán/bên mua… kèm nguồn (tài liệu, trang, độ tin cậy) | Đọc thẳng số liệu từ nội dung tài liệu | **Qwen Flash**: tự bóc tách các trường bắt buộc từ nội dung tài liệu |
| **B5** | Tra lịch sử hóa đơn | Danh sách hóa đơn trong hồ sơ + lịch sử hóa đơn đã dùng ở các lần giải ngân trước | Danh sách hóa đơn bị trùng/tái sử dụng (nếu có) | Đối chiếu số hóa đơn với lịch sử | **Giống mock** — không gọi AI |
| **B6** | Đối chiếu chéo | Các trường đã trích xuất (B4), trạng thái phân loại (B3), kết quả lịch sử (B5) và bộ quy tắc đối chiếu P1 | Kết quả từng quy tắc: 🟢 khớp / 🟡 cần chú ý / 🔴 không khớp / ⚪ chưa kiểm tra được, kèm cảnh báo đặc thù (hóa đơn scan mờ, giải ngân một phần) | So khớp số tiền/tên/giá trị theo quy tắc; mục đích–hàng hóa chỉ cần có đủ dữ liệu | **GLM (reasoning)**: suy luận mục đích vay có phù hợp nội dung hàng hóa không |
| **B7** | Sinh báo cáo | Toàn bộ kết quả B1–B6 | Báo cáo kiểm tra sơ bộ: mức tổng thể (🟢🟡🔴⚪), tóm tắt, thống kê + % độ phủ, bảng phân loại tài liệu, danh sách phát hiện, câu chốt "không kết luận đủ điều kiện giải ngân" | Tổng hợp, đếm mức, tính độ phủ | **Giống mock** — không gọi AI |

## Điểm cần lưu ý (góc nhìn BA)

- **Cửa chặn ở B3 → B4/B6:** mục chưa xác thực (🟠) sẽ chặn không cho ra 🟢 ở đối chiếu, buộc trả ⚪ "chưa kiểm tra được" — tránh "pass ảo".
- **AI không thay thế toàn bộ quy tắc:** các đối chiếu số tiền/giá trị vẫn là logic cố định (deterministic) ở cả hai chế độ; AI chỉ hỗ trợ phần cần đọc-hiểu (nhận dạng loại, bóc tách trường, suy luận ngữ nghĩa). Thiết kế này giữ được tính giải thích được và nhất quán cho các phép tính tiền.
- **Rủi ro cho UAT:** kết quả B3/B4 ở chế độ AI phụ thuộc chất lượng model và có thể khác mock, dẫn tới mức tổng thể ở B6/B7 khác nhau giữa hai chế độ. Nên cố định `mode` khi chạy test case để đảm bảo tính tái lập.
