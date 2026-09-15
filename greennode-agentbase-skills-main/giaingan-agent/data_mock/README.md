# Dữ liệu mô phỏng (data_mock)

Toàn bộ dữ liệu ở đây là **giả lập hoàn toàn**, không phải hồ sơ thật của MSB.

## Dữ liệu ngoài bộ hồ sơ (thay hệ thống thật)

| File | Thay cho | Dùng ở quy tắc |
|---|---|---|
| `core_mock.json` | Core/T24 + BPM hạn mức | DC-C-02/03/04/10, DC-P1-05, DC-P23-08/15 |
| `lich_su_hoa_don.json` | Kho lịch sử giải ngân (P1) | DC-P1-07/08 |
| `ky_luong_da_gn.json` | Kho lịch sử kỳ lương (P3) | DC-P23-09/11/12 |

## Ba nhóm hồ sơ mẫu

| Thư mục | Mục đích | File mẫu |
|---|---|---|
| `ho_so_sach/` | Mọi thông tin khớp → đo tỷ lệ cảnh báo sai (kỳ vọng 🟢) | `P1_CLEAN001.json` |
| `ho_so_co_sai_lech/` | Lỗi cài sẵn biết trước → đo tỷ lệ phát hiện đúng | `P1_HS001.json`, `P3_HS001.json` |
| `ho_so_bien/` | Sai loại tài liệu, scan mờ, biên → đo cơ chế cửa chặn (🟠 → ⚪) | `P1_SAILOAI001.json` |

## Định dạng file hồ sơ

Mỗi hồ sơ là 1 JSON mô phỏng nội dung tài liệu (thay cho PDF/ảnh thật để demo nhanh). Trường `noi_dung_mo_phong` đại diện cho kết quả OCR/trích xuất mà model sẽ đọc được từ file thật.

```json
{
  "ho_so_id": "...",
  "context": { "loai_giai_ngan": "P1|P3", "limit_id": "...", "so_tien_de_nghi": 0, "ngay_de_nghi_gn": "YYYY-MM-DD" },
  "tai_lieu": [
    { "ma_checklist": "3471", "voucher_type": "1", "ten_file": "...", "so_trang": 1, "noi_dung_mo_phong": { } }
  ]
}
```

> Khi tích hợp thật: thay lớp đọc bằng `DocumentSource` trỏ về ECM API; `noi_dung_mo_phong` sẽ được thay bằng kết quả OCR/LLM trên file thật.
