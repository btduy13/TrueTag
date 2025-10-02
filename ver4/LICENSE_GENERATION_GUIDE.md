# TRUETAG v4.0 - Hướng Dẫn Tạo License

## Tổng Quan

Hệ thống tạo license của TRUETAG v4.0 cho phép bạn tạo, quản lý và phân phối license keys cho khách hàng. Hệ thống bao gồm:

- **License Generator**: Tạo license keys với các loại khác nhau
- **License Server**: Mô phỏng server validation (cho testing)
- **License Manager UI**: Giao diện quản lý license
- **Database Management**: Lưu trữ và quản lý license

## Cấu Trúc Files

```
ver4/
├── license_generator.py       # Module tạo license chính
├── license_server.py          # Server mô phỏng validation
├── license_manager_ui.py      # Giao diện quản lý license
├── test_license_generation.py # Script test hệ thống
├── license_database.json      # Database license (tự động tạo)
├── license_config.json        # Cấu hình license generator
└── server_config.json         # Cấu hình server (tự động tạo)
```

## Các Loại License

### 1. Trial License
- **Thời gian**: 30 ngày
- **Tính năng**: Basic scripts + CSV import
- **Mục đích**: Dùng thử miễn phí
- **Số lần sử dụng**: 1

### 2. Basic License
- **Thời gian**: 365 ngày
- **Tính năng**: Basic scripts + CSV import
- **Mục đích**: Khách hàng cơ bản
- **Số lần sử dụng**: 1

### 3. Professional License
- **Thời gian**: 365 ngày
- **Tính năng**: Basic + Advanced scripts + Batch processing
- **Mục đích**: Khách hàng chuyên nghiệp
- **Số lần sử dụng**: 1

### 4. Enterprise License
- **Thời gian**: 365 ngày
- **Tính năng**: Tất cả tính năng + API access + Priority support + Cloud sync
- **Mục đích**: Khách hàng doanh nghiệp
- **Số lần sử dụng**: 1

### 5. Demo License
- **Thời gian**: 7 ngày
- **Tính năng**: Basic scripts + CSV import
- **Mục đích**: Demo ngắn hạn
- **Số lần sử dụng**: 1

### 6. Developer License
- **Thời gian**: 30 ngày
- **Tính năng**: Professional + API access
- **Mục đích**: Nhà phát triển
- **Số lần sử dụng**: 3

## Cách Sử Dụng

### 1. Chạy License Manager UI

```bash
cd ver4
python license_manager_ui.py
```

### 2. Tạo License Mới

#### Qua UI:
1. Mở tab "Tạo License"
2. Chọn loại license
3. Nhập thông tin khách hàng (tùy chọn)
4. Thêm ghi chú (tùy chọn)
5. Nhấn "Tạo License"

#### Qua Code:
```python
from license_generator import LicenseGenerator

generator = LicenseGenerator(data_dir)

# Tạo license cơ bản
success, message, license_data = generator.create_license(
    "basic",
    {"name": "John Doe", "email": "john@example.com"},
    notes="Customer purchase"
)

if success:
    print(f"License created: {license_data['license_key']}")
```

### 3. Tạo License Hàng Loạt

```python
# Tạo 10 license basic
bulk_licenses = generator.create_bulk_licenses(
    "basic", 
    10, 
    {"name": "Bulk Customer"},
    "Bulk purchase"
)

for license_data in bulk_licenses:
    print(f"License: {license_data['license_key']}")
```

### 4. Quản Lý License

#### Xem danh sách license:
```python
# Tất cả license
all_licenses = generator.list_licenses()

# Filter theo type
basic_licenses = generator.list_licenses("basic")

# Filter theo status
active_licenses = generator.list_licenses(status="active")
```

#### Thay đổi trạng thái:
```python
success, message = generator.update_license_status(
    "TRUETAG-1234-5678-9ABC", 
    "inactive"
)
```

#### Xem thông tin chi tiết:
```python
license_info = generator.get_license_info("TRUETAG-1234-5678-9ABC")
print(f"Type: {license_info['license_type']}")
print(f"Status: {license_info['status']}")
print(f"Expires: {license_info['expiry_date']}")
```

### 5. Xuất/Nhập License

#### Xuất license:
```python
# Xuất tất cả license
export_path = generator.export_licenses()

# Xuất với tên file cụ thể
export_path = generator.export_licenses("my_licenses.json")
```

#### Nhập license:
```python
success, message = generator.import_licenses("my_licenses.json")
print(message)
```

### 6. Server Validation

#### Khởi tạo server:
```python
from license_server import LicenseServer

server = LicenseServer(data_dir)
```

#### Test validation:
```python
response = server.validate_license_request(
    "TRUETAG-1234-5678-9ABC",
    "MACHINE-ID-123"
)

if response['success']:
    print("License valid!")
else:
    print(f"Error: {response['error']}")
```

#### Test activation:
```python
response = server.activate_license_request(
    "TRUETAG-1234-5678-9ABC",
    "MACHINE-ID-123",
    "Customer Name"
)

if response['success']:
    print("License activated!")
```

## Cấu Hình

### license_config.json
```json
{
  "product_key": "TRUETAG-V4",
  "version": "4.0",
  "secret_key": "TRUETAG-SECRET-2025",
  "license_prefix": "TRUETAG",
  "key_length": 4,
  "key_count": 5,
  "encryption_salt": "TRUETAG-SALT-2025"
}
```

### server_config.json
```json
{
  "server_name": "TRUETAG License Server",
  "version": "1.0",
  "security": {
    "api_key": "TRUETAG-API-KEY-2025",
    "rate_limit": {
      "requests_per_minute": 60,
      "requests_per_hour": 1000
    }
  }
}
```

## Testing

### Chạy Test Script
```bash
cd ver4
python test_license_generation.py
```

### Test Cases Bao Gồm:
1. License key generation
2. License creation (tất cả types)
3. License validation
4. License activation
5. Bulk license creation
6. License listing và filtering
7. Status updates
8. Statistics
9. Export/import
10. Server validation
11. Integration testing

## Workflow Tạo License

### 1. Workflow Cơ Bản
```
1. Mở License Manager UI
2. Chọn tab "Tạo License"
3. Chọn loại license
4. Nhập thông tin khách hàng
5. Tạo license
6. Copy license key cho khách hàng
```

### 2. Workflow Hàng Loạt
```
1. Chuẩn bị danh sách khách hàng
2. Sử dụng bulk creation
3. Xuất license ra file
4. Gửi license cho khách hàng
5. Theo dõi activation status
```

### 3. Workflow Quản Lý
```
1. Xem danh sách license
2. Filter theo type/status
3. Xem chi tiết license
4. Thay đổi status nếu cần
5. Export backup định kỳ
```

## Bảo Mật

### License Key Format
- Format: `TRUETAG-XXXX-XXXX-XXXX-XXXX`
- Mỗi segment: 4 ký tự (A-Z, 0-9)
- Tổng cộng: 25 ký tự
- Checksum: SHA256 (16 ký tự đầu)

### Machine Binding
- License được bind với Machine ID
- Machine ID được tạo từ:
  - Windows Machine GUID (ưu tiên)
  - CPU ID + Motherboard Serial
  - Random UUID (fallback)

### Validation
- Server-side validation (simulation)
- Checksum verification
- Expiry date checking
- Usage limit enforcement

## Troubleshooting

### License Không Tạo Được
1. Kiểm tra quyền ghi file
2. Kiểm tra format license type
3. Kiểm tra database corruption
4. Reset database nếu cần

### Validation Thất Bại
1. Kiểm tra license key format
2. Kiểm tra expiry date
3. Kiểm tra machine ID
4. Kiểm tra server configuration

### UI Không Hoạt Động
1. Kiểm tra dependencies (ttkbootstrap)
2. Kiểm tra Python version
3. Kiểm tra file paths
4. Restart application

## Best Practices

### 1. Backup
- Export license database định kỳ
- Backup configuration files
- Test restore process

### 2. Security
- Bảo vệ secret keys
- Sử dụng HTTPS cho server
- Implement rate limiting
- Log tất cả activities

### 3. Monitoring
- Theo dõi license usage
- Monitor activation rates
- Track expiry dates
- Alert khi có vấn đề

### 4. Customer Support
- Cung cấp license key rõ ràng
- Hướng dẫn activation
- Support khi có lỗi
- Grace period handling

## API Reference

### LicenseGenerator Class

#### Methods:
- `create_license(type, customer_info, custom_duration, notes)`
- `create_bulk_licenses(type, count, customer_info, notes)`
- `validate_license(key, machine_id)`
- `activate_license(key, machine_id, customer_name)`
- `list_licenses(type, status)`
- `get_license_info(key)`
- `update_license_status(key, status)`
- `export_licenses(filename)`
- `import_licenses(filepath)`
- `get_statistics()`

### LicenseServer Class

#### Methods:
- `validate_license_request(key, machine_id, api_key)`
- `activate_license_request(key, machine_id, customer_name, api_key)`
- `get_license_info_request(key, api_key)`
- `get_server_status()`
- `simulate_client_request(type, **kwargs)`

---

**Lưu ý**: Hệ thống này được thiết kế cho môi trường development và testing. Trong production, cần tích hợp với license server thực tế và thêm các biện pháp bảo mật nâng cao.
