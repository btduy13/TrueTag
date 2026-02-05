# TrueTag v4 BricsCAD Integration Guide

## Tổng quan

Tài liệu này hướng dẫn cách tích hợp TrueTag v4 vào BricsCAD để có thể launch trực tiếp từ giao diện BricsCAD.

## Cài đặt

### 1. Cài đặt thủ công (Khuyến nghị)

```bash
# Copy files vào thư mục BricsCAD Support
# Sau đó load CUI trong BricsCAD
```

### 2. Gỡ cài đặt

```bash
# Chạy script gỡ cài đặt
uninstall_bricscad_integration.bat
```

### 2. Cài đặt thủ công

1. **Copy files vào thư mục BricsCAD Support:**
   ```
   %APPDATA%\Bricsys\BricsCAD\V24\en_US\Support\
   ```

2. **Files cần copy:**
   - `bricscad_integration.lsp`
   - `TrueTag_BricsCAD.cui`
   - `logo.ico`

3. **Load CUI trong BricsCAD:**
   - Mở BricsCAD
   - Gõ lệnh: `CUILOAD`
   - Chọn file `TrueTag_BricsCAD.cui`

## Sử dụng

### Lệnh có sẵn

| Lệnh | Mô tả |
|------|-------|
| `TRUETAG` | Launch TrueTag v4 application |
| `TT` | Quick launch TrueTag v4 (shortcut) |
| `TRUETAG_PID` | Launch với PID scripts category |
| `TRUETAG_TML` | Launch với TML scripts category |
| `TRUETAG_POS` | Launch với Position scripts category |
| `TRUETAG_LICENSE` | Hiển thị thông tin license |
| `TRUETAG_HELP` | Hiển thị help |
| `TRUETAG_CHECK` | Kiểm tra trạng thái scripts |

### Cách sử dụng

#### 1. Launch từ Command Line
```
Command: TRUETAG
Enter script category (PID/TML/POS) or press Enter for default:
```

#### 2. Launch từ Ribbon
- Mở tab "TrueTag v4" trong ribbon
- Click các button tương ứng

#### 3. Launch từ Toolbar
- Sử dụng TrueTag v4 toolbar
- Click các button để launch nhanh

#### 4. Launch từ Menu
- Vào menu "TrueTag v4"
- Chọn option mong muốn

## Tính năng

### 1. Ribbon Integration
- Tab "TrueTag v4" trong BricsCAD ribbon
- Các panel: Tools, Script Categories, Utilities
- Icons chuyên nghiệp cho từng chức năng

### 2. Toolbar Integration
- TrueTag v4 toolbar với các button nhanh
- Có thể dock/undock tự do
- Customizable layout

### 3. Menu Integration
- Menu "TrueTag v4" trong main menu bar
- Tổ chức theo categories
- Shortcut keys support

### 4. Auto-load
- Tích hợp tự động load khi BricsCAD khởi động
- Không cần load manual
- Persistent across sessions

## Troubleshooting

### 1. Commands không hoạt động

**Nguyên nhân:** Files chưa được load đúng cách

**Giải pháp:**
```lisp
; Load manual trong BricsCAD
(load "bricscad_integration.lsp")
```

### 2. CUI không hiển thị

**Nguyên nhân:** CUI file chưa được load

**Giải pháp:**
```
Command: CUILOAD
Select: TrueTag_BricsCAD.cui
```

### 3. TrueTag không launch

**Nguyên nhân:** Đường dẫn không đúng

**Giải pháp:**
- Kiểm tra file `TrueTag-ver4.exe` có tồn tại
- Cập nhật đường dẫn trong file `.lsp`
- Chạy `TRUETAG_CHECK` để kiểm tra

### 4. Icons không hiển thị

**Nguyên nhân:** File icon không tìm thấy

**Giải pháp:**
- Copy `logo.ico` vào thư mục Support
- Restart BricsCAD

## Cấu trúc Files

```
ver4/
├── bricscad_integration.lsp     # Main integration script
├── bricscad_launcher.lsp        # Basic launcher
├── TrueTag_BricsCAD.cui         # CUI interface definition
├── uninstall_bricscad_integration.bat # Uninstaller
├── BRICSCAD_INTEGRATION_README.md     # This guide
└── logo.ico                     # Icons for interface
```

## Gỡ cài đặt

### Chạy script gỡ cài đặt
```bash
uninstall_bricscad_integration.bat
```

### Gỡ cài đặt thủ công
1. Xóa files từ thư mục BricsCAD Support
2. Unload CUI trong BricsCAD
3. Xóa desktop shortcut
4. Khôi phục registry settings

## Support

Nếu gặp vấn đề, vui lòng:
1. Chạy `TRUETAG_CHECK` để kiểm tra
2. Kiểm tra log files
3. Liên hệ development team

## Version History

- **v1.0**: Initial integration release
  - Basic launcher functionality
  - Ribbon, toolbar, menu integration
  - Auto-load capability
  - License and help commands

---

**TrueTag v4 BricsCAD Integration v1.0**  
© 2025 TrueTag Development Team
