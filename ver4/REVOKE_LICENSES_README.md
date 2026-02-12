# How to Revoke Licenses and Deploy Server

## Quick Start Guide

### Step 1: Thu hồi tất cả licenses hiện tại

```bash
cd e:\OneDrive\Desktop\Truetag\ver4
python bulk_revoke_licenses.py
```

**Lưu ý**: Script này sẽ:
- Hiển thị danh sách tất cả active licenses
- Yêu cầu xác nhận trước khi thu hồi
- Ghi lại admin name và lý do thu hồi
- Tạo báo cáo chi tiết về licenses đã thu hồi

### Step 2: Start License Server (Optional - cho testing)

```bash
python license_server_api.py
```

Server sẽ chạy tại: `http://localhost:5000`

**Endpoints**:
- `GET /health` - Kiểm tra server
- `POST /api/validate` - Validate license
- `POST /api/check-revoked` - Kiểm tra revoke status

### Step 3: Test Validation

Run TrueTag application:
```bash
dist\TRUETAG-v4.exe
```

Application sẽ:
- Kiểm tra license local
- Gọi server để check revoke status
- Nếu license bị revoke → hiển thị lỗi và block

### Step 4: Rebuild với Server Validation

```bash
build_auto.bat
```

### Step 5: Tạo installer mới

```bash
python create_installer.py
```

## Configuration

### Enable/Disable Server Validation

Trong `licensing_config.json`:
```json
{
  "enable_server_validation": true,
  "license_server": "http://localhost:5000",
  "server_timeout": 5
}
```

Set `enable_server_validation` to `false` để tắt server validation.

## Detailed Documentation

Xem file `LICENSE_SERVER_DEPLOYMENT.md` để biết thêm chi tiết về:
- Architecture
- Deployment options
- Testing procedures
- Troubleshooting
