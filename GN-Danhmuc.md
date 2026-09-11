# Checklist hồ sơ giải ngân — phạm vi demo (P1, P3)

> Nguồn: `GIẢI NGÂN CHECKLIST Hồ sơ .xlsx`. Khóa nghiệp vụ dùng trong demo là mã checklist BPM. Bản đầy đủ (18 loại giải ngân, mã checklist BPM, mã tài liệu ECM để tra cứu, đặc tả API, danh mục 7.11) lưu tại `GN-Danhmuc-full.md`.

Hai loại giải ngân dùng cho demo:

| Mã | Loại giải ngân | Trọng tâm kiểm tra |
|---|---|---|
| P1 | Giải ngân thanh toán cho hàng hóa, dịch vụ **có hóa đơn** (trong nước) | Đối chiếu hóa đơn ↔ hợp đồng ↔ công nợ ↔ UNC |
| P3 | Thanh toán **lương chuyển khoản** | Đối chiếu từng dòng danh sách người hưởng |

Checklist chia theo ba vùng hồ sơ:

- **Hồ sơ chung** — bắt buộc với mọi loại giải ngân.
- **Hồ sơ mục đích vay** — khác nhau theo từng loại giải ngân, đây là phần tạo ra khác biệt giữa P1 và P3.
- **Hồ sơ nguồn thu** — danh mục dùng chung, xuất trình theo phê duyệt tín dụng của từng khoản vay.

---

## 1. Ma trận checklist P1 và P3

Đọc theo cột: cột `P1` là toàn bộ checklist của loại P1, cột `P3` là của loại P3. `✔` = tài liệu bắt buộc với loại đó. Cột `Vùng` để lọc nhanh theo nhóm hồ sơ.

| Vùng | Tài liệu | P1 | P3 |
|---|---|:-:|:-:|
| Hồ sơ chung | Giấy nhận nợ | ✔ | ✔ |
| Hồ sơ chung | UNC/Chứng từ thể hiện thanh toán | ✔ | ✔ |
| Hồ sơ chung | Hồ sơ chung khác | ✔ | ✔ |
| Mục đích vay | Hồ sơ khác | ✔ | ✔ |
| Mục đích vay | Hợp đồng kinh tế/Đơn đặt hàng/Văn bản pháp lý tương đương có xác nhận của bên bán | ✔ |  |
| Mục đích vay | Hóa đơn | ✔ |  |
| Mục đích vay | Biên bản đối chiếu công nợ/Giấy đề nghị thanh toán của bên bán | ✔ |  |
| Mục đích vay | Bảng lương |  | ✔ |
| Mục đích vay | Hợp đồng chuyển khoản theo lô |  | ✔ |
| Nguồn thu | Hợp đồng trong nước/Hợp đồng ngoại thương | ✔ | ✔ |
| Nguồn thu | BCT xuất khẩu | ✔ | ✔ |
| Nguồn thu | Biên bản đối chiếu công nợ | ✔ | ✔ |
| Nguồn thu | Biên bản giao nhận hàng hóa | ✔ | ✔ |
| Nguồn thu | Phương án kinh doanh | ✔ | ✔ |
| Nguồn thu | Cam kết chuyển tiền về | ✔ | ✔ |
| Nguồn thu | Ủy quyền thu nợ | ✔ | ✔ |
| Nguồn thu | Đề nghị tài trợ | ✔ | ✔ |
| Nguồn thu | Hồ sơ nguồn thu khác | ✔ | ✔ |
| | **Tổng số mục** | **16** | **15** |

---

## 2. Khác biệt giữa P1 và P3

Hồ sơ chung (3 mục) và Hồ sơ nguồn thu (9 mục) giống nhau. Chỉ khác ở vùng Hồ sơ mục đích vay:

| Hồ sơ mục đích vay của P1 | Hồ sơ mục đích vay của P3 |
|---|---|
| Hợp đồng kinh tế/Đơn đặt hàng có xác nhận bên bán | Bảng lương |
| Hóa đơn | Hợp đồng chuyển khoản theo lô |
| Biên bản đối chiếu công nợ/Giấy đề nghị thanh toán | — |

Hai ghi chú nghiệp vụ:

- P1: ở checklist V2, **Hóa đơn được tách thành mục riêng**. Trước đây hóa đơn nằm chung một mục với hợp đồng kinh tế nên không kiểm soát được trường hợp thiếu hóa đơn.
- P3: chuyển khoản toàn bộ nên **không** yêu cầu "Cam kết bổ sung chứng từ nhận tiền, chuyển tiền của người hưởng". Mục này chỉ áp dụng cho P2 (thanh toán lương có cấu phần tiền mặt).

---

## 4. Loại chứng từ — căn cứ đánh giá độ tin cậy tài liệu

| Loại chứng từ | Ý nghĩa | Độ tin cậy |
|---|---|---|
| Bản số | Hệ thống tự sinh, không có chữ ký số | Cao |
| Bản ký số attach | Hệ thống tự sinh, có chữ ký số | Cao |
| Bản attach vật lý | User upload bản giấy có chữ ký | Cần kiểm tra kỹ |
| Bản mềm attach | User upload, không có chữ ký | Cần kiểm tra kỹ |
