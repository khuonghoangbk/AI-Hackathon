# ERD — Mô hình dữ liệu hệ thống Trợ lý kiểm tra Giải ngân (Giải Ngân Agent)

> Tài liệu này mô hình hóa quan hệ giữa **Yêu cầu giải ngân (YCGN)**, **Tài liệu**, **Lịch sử hóa đơn** và các thực thể liên quan (Khách hàng, Limit, cùng bộ quy tắc nghiệp vụ trong `config/`).
> Nguồn dữ liệu là các file mock trong `giaingan-agent/data_mock/` và `giaingan-agent/config/`. Đây là **mô hình logic** — dữ liệu mock đang lưu ở JSON, không phải bảng RDBMS thật; các "PK/FK" bên dưới là khóa logic dùng để ghép dữ liệu.

---

## 1. Sơ đồ ERD tổng thể

Ký hiệu quan hệ:  `1──<N` = một-nhiều · `1──1` = một-một · `N>──<M` = nhiều-nhiều
Nhãn trên đường nối = khóa dùng để ghép dữ liệu.
Đường nét đứt `- - ->` = tham chiếu lỏng (trỏ ra dữ liệu ngoài tập đang xét), KHÔNG phải mắt xích trong luồng kiểm tra.

```
        NHÓM A — DỮ LIỆU YCGN                          NHÓM B — QUY TẮC NGHIỆP VỤ (config/)

    ┌───────────────────────┐
    │      KHACH_HANG       │
    │  PK ten_khach_hang    │
    └───────────┬───────────┘
      1         │ N (tên KH)
                ▼
    ┌───────────────────────┐
    │        LIMIT          │
    │  PK limit_id          │
    │  FK khach_hang        │
    └───────────┬───────────┘
      1         │ N (limit_id)
                ▼
    ┌───────────────────────────────────┐
    │          KHOAN_VAY  (YCGN)         │
    │  PK ho_so_id  ← mã YCGN GN-2026-*  │
    │  FK limit_id, khach_hang_vay       │
    │  loai_giai_ngan, so_tien_de_nghi   │
    │  loai_tien, muc_dich_su_dung       │
    └───────────┬───────────────────────┘
      1         │ 1  (ho_so_id)
                ▼
    ┌───────────────────────┐
    │         HO_SO         │
    │  PK ho_so_id          │
    │  mo_ta                │
    └───────────┬───────────┘
      1         │ N
                ▼
    ┌───────────────────────────────────┐        ┌──────────────────────────┐
    │             TAI_LIEU              │  N     │  CHECKLIST_ITEM          │
    │  FK ho_so_id                      │◄───────┤  PK ma_checklist         │
    │  FK ma_checklist                  │  (ma_  │  FK loai_giai_ngan       │
    │  FK voucher_type                  │  check │  vung, ten, bat_buoc     │
    │  so_trang, noi_dung               │  list) │  cung_loai_voi           │
    │                                   │        └──────────▲───────────────┘
    │                                   │  N              1 │ N
    │                                   │◄───────┐          │
    │                                   │  (ma_  │  ┌───────┴────────┐
    │                                   │  check │  │  CHECKLIST_P1  │
    │                                   │  list) │  │ PK loai_giai_ngan
    │                                   │        │  │ ten, ghi_chu   │
    │                                   │  ┌─────┴──────────┐  └──────┘
    │                                   │◄─┤ DOC_SIGNATURE  │
    │                                   │N │ PK ma_checklist│
    │                                   │  │ dau_hieu / nguong_dat
    │                                   │  └────────────────┘
    │                                   │  ┌────────────────┐
    │                                   │◄─┤  VOUCHER_CONF  │
    │                                   │N │ PK voucher_type│
    │                                   │  │ do_tin_cay,    │
    │                                   │  │ canh_bao       │
    └───────────────┬───────────────────┘  └────────────────┘
                    │ N >──< M  (so_hoa_don: ĐỐI CHIẾU CHỐNG TRÙNG)
                    ▼
    ┌──────────────────────────────────────────┐
    │            LICH_SU_HOA_DON               │   (mock Core/ECM: hóa đơn ĐÃ dùng trước đó)
    │  PK so_hoa_don                           │
    │  ky_hieu, mst_ben_ban                    │
    │  tong_tien_thanh_toan, ngay_su_dung      │
    │  lan_giai_ngan_truoc  - - -> (tên YCGN cũ đã tiêu hóa đơn này)
    └──────────────────────────────────────────┘
                    ┊
                    ┊ lan_giai_ngan_truoc chỉ là NHÃN tham chiếu tới một YCGN
                    ┊ trong quá khứ (VD GN-2026-000987), dùng để HIỂN THỊ cảnh
                    ┊ báo. YCGN cũ đó thường KHÔNG có trong khoan_vay.json hiện tại.
```

Đọc sơ đồ:
- **Luồng chính (Nhóm A):** KHACH_HANG → LIMIT → KHOAN_VAY(YCGN) → HO_SO → TAI_LIEU. Khoản vay **chỉ nối tới tài liệu** (qua HO_SO), rồi **tài liệu mới nối tới LICH_SU_HOA_DON** qua `so_hoa_don` để chống trùng. Khoản vay hiện tại KHÔNG nối trực tiếp tới lịch sử hóa đơn.
- **`lan_giai_ngan_truoc`** nằm trong LICH_SU_HOA_DON, là tham chiếu lỏng (nét đứt) tới một YCGN quá khứ — chỉ để hiển thị, không phải quan hệ trong luồng.
- **Nhóm B (quy tắc, `config/`):** CHECKLIST_P1 → CHECKLIST_ITEM; và CHECKLIST_ITEM, DOC_SIGNATURE, VOUCHER_CONF cùng áp quy tắc lên TAI_LIEU.

---

## 2. Mô tả thực thể

### Nhóm A — Dữ liệu YCGN (nghiệp vụ, thay đổi theo từng hồ sơ)

| Thực thể | Nguồn | Vai trò |
|---|---|---|
| **KHOAN_VAY** | `data_mock/khoan_vay.json` | Header của YCGN: khách hàng, số tiền đề nghị, loại giải ngân, mục đích. Key = `ho_so_id` (mã YCGN). |
| **HO_SO** | `data_mock/ho_so_*/{ho_so_id}.json` | Bộ hồ sơ tài liệu của một YCGN. Nối 1-1 với KHOAN_VAY qua `ho_so_id`. |
| **TAI_LIEU** | mảng `tai_lieu[]` trong file `HO_SO` | Từng chứng từ trong hồ sơ (giấy nhận nợ, UNC, hợp đồng, hóa đơn, biên bản đối chiếu...). |
| **LICH_SU_HOA_DON** | `data_mock/lich_su_hoa_don.json` | Mock Core/ECM: các hóa đơn đã dùng ở lần giải ngân trước, để phát hiện trùng. |
| **KHACH_HANG**, **LIMIT** | suy ra từ trường trong `khoan_vay.json` (`khach_hang_vay`, `limit_id`) | Thực thể logic; chưa có bảng riêng trong mock nhưng tồn tại qua khóa. |

### Nhóm B — Quy tắc nghiệp vụ (knowledge base, dùng chung mọi hồ sơ)

| Thực thể | Nguồn | Vai trò |
|---|---|---|
| **CHECKLIST_P1** | `config/checklist_P1.json` | Bộ checklist cho loại giải ngân P1. |
| **CHECKLIST_ITEM** | mảng `muc[]` trong `checklist_P1.json` | Từng mục checklist (mã, vùng, bắt buộc/điều kiện). |
| **DOC_SIGNATURE** | `config/doc_signatures.json` | Dấu hiệu nhận dạng + trường bắt buộc + ngưỡng đạt cho từng loại tài liệu. |
| **VOUCHER_CONF** | `config/voucher_confidence.json` | Bảng độ tin cậy theo `voucher_type` (1/2/3/4). |

> `config/` **không** chứa dữ liệu của YCGN cụ thể — nó là bộ luật dùng chung. Vì vậy nó nối tới `TAI_LIEU` theo kiểu "1 quy tắc áp cho N tài liệu".

---

## 3. Các quan hệ khóa (cardinality)

| Quan hệ | Loại | Khóa nối | Ghi chú |
|---|---|---|---|
| KHOAN_VAY — HO_SO | 1 : 1 | `ho_so_id` | Mỗi YCGN có đúng 1 bộ hồ sơ. |
| HO_SO — TAI_LIEU | 1 : N | `ho_so_id` | Một hồ sơ gồm nhiều tài liệu. |
| CHECKLIST_ITEM — TAI_LIEU | 1 : N | `ma_checklist` | Một mục checklist có thể ứng với nhiều tài liệu (VD nhiều hóa đơn cùng mã 3455). |
| DOC_SIGNATURE — TAI_LIEU | 1 : N | `ma_checklist` | Quy tắc trích xuất/nhận dạng áp cho các tài liệu cùng mã. |
| VOUCHER_CONF — TAI_LIEU | 1 : N | `voucher_type` | Gán độ tin cậy (cao/thấp) theo dạng chứng từ. |
| TAI_LIEU — LICH_SU_HOA_DON | N : M | `so_hoa_don` | **Quan hệ đối chiếu chính.** Lấy `so_hoa_don` của tài liệu hóa đơn (mã 3455) đem so với danh sách hóa đơn đã dùng để chống trùng. Đây là cầu nối DUY NHẤT giữa YCGN hiện tại và lịch sử hóa đơn. |
| LICH_SU_HOA_DON · `lan_giai_ngan_truoc` | tham chiếu lỏng | trỏ tới mã một YCGN quá khứ | KHÔNG phải quan hệ trong luồng. Chỉ là nhãn ghi "hóa đơn này trước đây bị YCGN nào tiêu" (VD `GN-2026-000987`), dùng để hiển thị cảnh báo. YCGN cũ đó thường không có trong `khoan_vay.json` hiện tại. |
| LIMIT — KHOAN_VAY | 1 : N | `limit_id` | Một hạn mức phát sinh nhiều lần giải ngân. |
| KHACH_HANG — LIMIT / KHOAN_VAY | 1 : N | tên KH | Một KH có nhiều limit / nhiều YCGN. |

---

## 4. Trường hợp đặc thù ảnh hưởng mô hình

Từ hồ sơ `GN-2026-000476` (nhóm đặc thù):

- **Nhiều hóa đơn / 1 YCGN:** nhiều bản ghi `TAI_LIEU` cùng `ma_checklist = 3455` trong một `HO_SO` → khẳng định quan hệ CHECKLIST_ITEM 1:N TAI_LIEU.
- **1 tài liệu thỏa 2 mục checklist:** biên bản đối chiếu công nợ có `thoa_man_muc = ["3458","34248"]`. Trong checklist, mục `34248` khai báo `cung_loai_voi = "3458"` → quan hệ tự tham chiếu giữa các CHECKLIST_ITEM (chỉ cần 1 tài liệu thỏa cả hai).
- **Voucher scan mờ:** `voucher_type = 2` → tra VOUCHER_CONF ra `do_tin_cay = thap`, `canh_bao = true` → hạ ngưỡng đạt của DOC_SIGNATURE.

---

## 5. Khóa nối cốt lõi (tóm tắt nhanh)

```
ho_so_id       : KHOAN_VAY ─ HO_SO ─ TAI_LIEU        (mã YCGN, GN-2026-xxx)
ma_checklist   : CHECKLIST_ITEM / DOC_SIGNATURE ─ TAI_LIEU
voucher_type   : VOUCHER_CONF ─ TAI_LIEU             (1/2/3/4)
so_hoa_don     : TAI_LIEU ─ LICH_SU_HOA_DON          (cầu nối DUY NHẤT tới lịch sử — chống trùng)
limit_id       : LIMIT ─ KHOAN_VAY
```

> Lưu ý luồng: KHOAN_VAY (YCGN) → HO_SO → TAI_LIEU → LICH_SU_HOA_DON. Khoản vay hiện tại **không** nối trực tiếp tới lịch sử hóa đơn; nó đi qua tài liệu (`so_hoa_don`).
> `lan_giai_ngan_truoc` **không** phải khóa nối trong luồng — chỉ là nhãn tham chiếu tới YCGN quá khứ để hiển thị cảnh báo trùng.
