# TRUETAG v4.0 - Hệ Thống Licensing

## Tổng Quan

Hệ thống licensing của TRUETAG v4.0 được thiết kế để quản lý bản quyền phần mềm một cách an toàn và linh hoạt. Hệ thống hỗ trợ:

- **Trial License**: 30 ngày dùng thử miễn phí
- **Grace Period**: 7 ngày gia hạn sau khi hết hạn
- **Machine Binding**: Liên kết license với máy tính cụ thể
- **Feature Control**: Kiểm soát tính năng theo loại license
- **Secure Validation**: Xác thực license an toàn

## Cấu Trúc Files

```
ver4/
├── licensing_manager.py      # Module quản lý licensing chính
├── license_config.json       # Cấu hình hệ thống licensing
├── license.json             # File license của người dùng (tự động tạo)
└── test_licensing.py        # Script test hệ thống
```

## Tính Năng Chính

### 1. Trial License
- **Thời gian**: 30 ngày miễn phí
- **Tính năng**: Basic scripts + CSV import
- **Tự động khởi tạo**: Khi chạy lần đầu
- **Grace period**: 7 ngày sau khi hết hạn

### 2. License Activation
- **Format key**: `TRUETAG-XXXX-XXXX-XXXX-XXXX`
- **Machine binding**: License chỉ hoạt động trên máy đã kích hoạt
- **Feature unlock**: Mở khóa tất cả tính năng

### 3. Feature Control
- **Basic Scripts**: PID, TML, Position scripts (trial + licensed)
- **CSV Import**: Import file CSV (trial + licensed)
- **Advanced Scripts**: Tính năng nâng cao (chỉ licensed)
- **Batch Processing**: Xử lý hàng loạt (chỉ licensed)
- **API Access**: Truy cập API (chỉ licensed)

## Cách Sử Dụng

### 1. Kiểm Tra License
```python
from licensing_manager import LicensingManager

license_manager = LicensingManager(data_dir)
is_valid, message = license_manager.is_license_valid()
print(f"License valid: {is_valid}, Message: {message}")
```

### 2. Kích Hoạt License
```python
success, message = license_manager.activate_license("TRUETAG-1234-5678-9ABC")
if success:
    print("License activated successfully!")
else:
    print(f"Activation failed: {message}")
```

### 3. Kiểm Tra Tính Năng
```python
if license_manager.is_feature_enabled("advanced_scripts"):
    # Chạy tính năng nâng cao
    pass
else:
    # Hiển thị thông báo cần license
    pass
```

### 4. Lấy Thông Tin License
```python
license_info = license_manager.get_license_info()
print(f"Status: {license_info['status']}")
print(f"Days remaining: {license_info['days_remaining']}")
print(f"Features: {license_info['features']}")
```

## Cấu Hình

### license_config.json
```json
{
  "trial_days": 30,
  "grace_period_days": 7,
  "license_server": "https://api.truetag.com/license",
  "product_key": "TRUETAG-V4",
  "version": "4.0",
  "features": {
    "basic_scripts": {
      "enabled": true,
      "description": "Basic AutoLISP scripts",
      "trial_allowed": true
    }
  },
  "license_types": {
    "trial": {
      "duration_days": 30,
      "features": ["basic_scripts", "csv_import"],
      "description": "30-day trial"
    }
  }
}
```

## UI Integration

### Menu License
- **License Information**: Hiển thị thông tin license hiện tại
- **Activate License**: Cửa sổ kích hoạt license
- **Reset Trial**: Reset trial (chỉ dùng cho testing)

### Status Bar
- Hiển thị trạng thái license
- Số ngày còn lại
- Grace period countdown

### License Validation
- Kiểm tra khi khởi động ứng dụng
- Kiểm tra trước khi chạy script
- Hiển thị cảnh báo nếu license không hợp lệ

## Bảo Mật

### Machine Binding
- Sử dụng Machine GUID từ Windows Registry
- Fallback: CPU ID + Motherboard Serial
- Final fallback: Random UUID

### License Integrity
- SHA256 checksum để bảo vệ license file
- Xác thực machine ID
- Kiểm tra expiry date

### Key Format
- Format: `TRUETAG-XXXX-XXXX-XXXX-XXXX`
- Validation trước khi kích hoạt
- Server-side validation (simulation)

## Testing

### Chạy Test Script
```bash
cd ver4
python test_licensing.py
```

### Test Cases
1. Trial license initialization
2. License validation
3. Feature checking
4. License activation
5. Key format validation
6. Machine ID generation
7. License integrity
8. Trial reset

## Troubleshooting

### License Không Hợp Lệ
1. Kiểm tra Machine ID có đúng không
2. Kiểm tra expiry date
3. Kiểm tra license file integrity
4. Reset trial nếu cần (chỉ dùng cho testing)

### Activation Thất Bại
1. Kiểm tra format license key
2. Kiểm tra kết nối mạng
3. Kiểm tra license server
4. Thử lại sau vài phút

### Feature Không Hoạt Động
1. Kiểm tra license status
2. Kiểm tra feature configuration
3. Kiểm tra trial/licensed mode
4. Kích hoạt license nếu cần

## API Reference

### LicensingManager Class

#### Methods
- `__init__(data_dir)`: Khởi tạo licensing manager
- `is_license_valid()`: Kiểm tra license hợp lệ
- `activate_license(key)`: Kích hoạt license
- `is_feature_enabled(feature)`: Kiểm tra tính năng
- `get_license_info()`: Lấy thông tin license
- `get_trial_info()`: Lấy thông tin trial
- `reset_trial()`: Reset trial license

#### Properties
- `config`: Cấu hình licensing
- `license_data`: Dữ liệu license hiện tại
- `data_dir`: Thư mục lưu trữ license

## Tương Lai

### Planned Features
- Online license validation
- License transfer giữa các máy
- Multi-user licensing
- Enterprise license management
- Cloud-based license server

### Security Enhancements
- License encryption
- Code obfuscation
- Anti-tampering protection
- Hardware fingerprinting

---

**Lưu ý**: Hệ thống licensing này được thiết kế cho môi trường development và testing. Trong production, cần tích hợp với license server thực tế và thêm các biện pháp bảo mật nâng cao.

