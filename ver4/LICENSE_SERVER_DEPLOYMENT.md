# TrueTag License Server - Deployment Guide

## Overview
Hệ thống license server mới cho phép kiểm soát licenses từ xa, bao gồm:
- Validate licenses realtime
- Thu hồi licenses từ xa (remote revoke)
- Offline fallback mode
- Automatic revoke detection

## Architecture

```
┌─────────────────┐         ┌──────────────────┐
│  TrueTag Client │◄───────►│  License Server  │
│ (BricsCAD App)  │  HTTP   │   (Flask API)    │
└─────────────────┘         └──────────────────┘
         │                            │
         │                            │
         ▼                            ▼
  license.json                 license_db.json
  (Local Cache)                (Master Database)
```

## Files Created

### 1. `license_server_api.py`
Flask API server với các endpoints:
- `/health` - Health check
- `/api/validate` - Validate license key
- `/api/activate` - Activate license
- `/api/check-revoked` - Check revoke status
- `/api/license-info` - Get license details
- `/api/statistics` - Get statistics

### 2. `bulk_revoke_licenses.py`
Script để thu hồi hàng loạt licenses:
- Liệt kê tất cả active licenses
- Confirm trước khi revoke
- Tạo revocation report
- Ghi lại admin name và lý do

### 3. Modified: `licensing_manager.py`
Client-side licensing với server validation:
- Real API calls thay vì simulation
- Automatic revoke detection
- Offline fallback mode
- Timeout handling (5 seconds)

### 4. Modified: `requirements.txt`
Added dependencies:
- Flask >= 3.0.0
- Flask-CORS >= 4.0.0
- requests >= 2.31.0

## Quick Start

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Start License Server

```bash
cd e:\OneDrive\Desktop\Truetag\ver4
python license_server_api.py
```

Server sẽ chạy tại: `http://localhost:5000`

### Step 3: Thu Hồi Licenses Hiện Tại

```bash
python bulk_revoke_licenses.py
```

Follow the prompts:
1. Review danh sách licenses
2. Confirm revocation
3. Nhập admin name
4. Nhập lý do thu hồi

### Step 4: Rebuild Application

```bash
build_auto.bat
```

### Step 5: Create New Installer

```bash
python create_installer.py
```

## How It Works

### License Validation Flow

1. **Client khởi động**:
   - Đọc `license.json` local
   - Gọi `/api/check-revoked` để kiểm tra status
   - Nếu revoked → reject và update local status

2. **Server unreachable**:
   - Timeout sau 5 seconds
   - Fallback to offline mode
   - Tiếp tục hoạt động với local license

3. **Server validates**:
   - Check license trong database
   - Return status (active/revoked/expired)
   - Update license info

### Remote Revocation

1. **Admin revokes license**:
   ```bash
   python bulk_revoke_licenses.py
   ```

2. **Database updated**:
   - Status → "revoked"
   - Revoke info saved (reason, admin, timestamp)

3. **Client checks**:
   - Next app launch
   - Calls `/api/check-revoked`
   - Receives revoke status

4. **App blocks**:
   - Local license updated to "revoked"
   - App shows error message
   - User cannot continue

## Server Deployment Options

### Option A: Local Server (Development)
```bash
python license_server_api.py
```
- Chạy tại localhost:5000
- Dùng cho testing
- Không cần config gì thêm

### Option B: Production Server
1. Deploy lên server (VPS, cloud, etc.)
2. Update config trong client:
   ```python
   # licensing_config.json
   {
     "license_server": "https://license.truetag.com",
     "enable_server_validation": true,
     "server_timeout": 5
   }
   ```
3. Rebuild application
4. Distribute new version

### Option C: Hybrid Mode
- Enable server validation: `true`
- Server offline → automatic fallback
- Best of both worlds

## Configuration

### Client Config (`licensing_config.json`)

```json
{
  "trial_days": 30,
  "grace_period_days": 7,
  "license_server": "http://localhost:5000",
  "enable_server_validation": true,
  "server_timeout": 5,
  "product_key": "TRUETAG-V4",
  "version": "4.0"
}
```

### Server Config
Trong `license_server_api.py`, line 260:
```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

Production mode:
```python
app.run(host='0.0.0.0', port=5000, debug=False)
```

## Testing

### Test 1: Check Server Health
```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "ok",
  "message": "License server is running",
  "timestamp": "2026-02-10T10:00:00"
}
```

### Test 2: Validate License
```powershell
$body = @{
    license_key = "YOUR-LICENSE-KEY"
    machine_id = "test-machine"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/validate" -Method POST -Body $body -ContentType "application/json"
```

### Test 3: Check Revoked Status
```powershell
$body = @{
    license_key = "YOUR-LICENSE-KEY"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/check-revoked" -Method POST -Body $body -ContentType "application/json"
```

## Next Steps

1. **Thu hồi licenses hiện tại**:
   ```bash
   python bulk_revoke_licenses.py
   ```

2. **Start license server**:
   ```bash
   python license_server_api.py
   ```

3. **Test validation**:
   - Run TrueTag application
   - Should detect revoked license
   - Should block access

4. **Create new licenses**:
   - Use License Manager UI
   - Generate new keys for BricsCAD-only version

5. **Contact customers**:
   - Email notification
   - Provide new license keys
   - Provide new installer

## Troubleshooting

### Server không start
- Check Python version >= 3.8
- Install dependencies: `pip install Flask Flask-CORS requests`
- Check port 5000 không bị chiếm

### Client không kết nối được server
- Check server đang chạy
- Check firewall settings
- Check `license_server` URL trong config

### Licenses không bị revoke
- Check server database có license chưa
- Check `enable_server_validation` = true
- Check client có internet connection

### Offline mode
- Normal behavior nếu server unreachable
- Client sẽ continue với local license
- Deploy server để enable remote control

## Security Notes

> [!IMPORTANT]
> - Server API chưa có authentication
> - Nên thêm API key hoặc token authentication
> - Deploy server behind firewall/VPN
> - Use HTTPS trong production

> [!WARNING]
> - Database `license_db.json` chứa tất cả licenses
> - Backup file này thường xuyên
> - Không commit lên Git public repo
