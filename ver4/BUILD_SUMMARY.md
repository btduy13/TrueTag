# License Manager UI - Build Setup Summary

## Tổng Quan
Đã thiết lập đầy đủ để build ứng dụng License Manager UI thành file thực thi (.exe) độc lập.

## Các File Đã Tạo

### 1. `license_manager_ui.spec`
- File cấu hình PyInstaller cho License Manager UI
- Bao gồm tất cả dependencies cần thiết
- Cấu hình để tạo file .exe không có console (windowed app)
- Sử dụng icon từ `logo.ico`

### 2. `build_license_manager.bat`
- Batch script để build ứng dụng trên Windows
- Tự động kiểm tra và cài đặt dependencies
- Tự động clean build cũ trước khi build mới

### 3. `build_license_manager.py`
- Python script để build ứng dụng (cross-platform)
- Kiểm tra dependencies
- Clean build cũ
- Build application
- Verify build kết quả

### 4. `test_build.py`
- Script test để kiểm tra build setup
- Kiểm tra các file cần thiết
- Kiểm tra dependencies đã cài đặt

### 5. `BUILD_LICENSE_MANAGER.md`
- Tài liệu hướng dẫn build chi tiết
- Hướng dẫn troubleshooting
- Cấu trúc file và dependencies

## Các File Đã Sửa

### 1. `license_manager_ui.py`
- Đã sửa import `tkinter.simpledialog` (di chuyển lên đầu file)
- Đã sửa các chỗ sử dụng `tk.simpledialog` thành `simpledialog`

## Cách Build

### Phương Pháp 1: Sử dụng Batch Script (Windows)
```bash
build_license_manager.bat
```

### Phương Pháp 2: Sử dụng Python Script
```bash
python build_license_manager.py
```

### Phương Pháp 3: Sử dụng PyInstaller trực tiếp
```bash
pyinstaller license_manager_ui.spec --clean --noconfirm
```

## Kết Quả Build

Sau khi build thành công, file thực thi sẽ được tạo trong thư mục `dist/`:
- `dist/LicenseManager.exe` - File thực thi chính

## Dependencies

### Python Packages
- `PyInstaller >= 6.0.0` - Build tool
- `ttkbootstrap >= 1.10.1` - GUI framework

### Local Modules
- `license_generator.py` - Tạo và quản lý license keys
- `license_server.py` - Mô phỏng server validation

### Data Files
- `logo.ico` - Icon cho ứng dụng
- `license_config.json` - File cấu hình (tự động tạo nếu không có)
- `server_config.json` - File cấu hình server (tự động tạo nếu không có)
- `license_database.json` - Database license (tự động tạo nếu không có)

## Kiểm Tra Build Setup

Chạy script test để kiểm tra:
```bash
python test_build.py
```

Nếu tất cả checks passed, bạn có thể build ứng dụng.

## Lưu Ý

1. **Icon File**: Đảm bảo file `logo.ico` tồn tại trong thư mục `ver4/`
2. **Dependencies**: Đảm bảo đã cài đặt đầy đủ dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. **Build Output**: File thực thi sẽ được tạo trong thư mục `dist/`
4. **Config Files**: Các file cấu hình sẽ được tạo tự động khi chạy ứng dụng lần đầu
5. **Data Directory**: Ứng dụng sẽ sử dụng thư mục chứa file .exe làm data directory

## Next Steps

1. Chạy `python test_build.py` để kiểm tra setup
2. Chạy `build_license_manager.bat` hoặc `python build_license_manager.py` để build
3. Kiểm tra file `dist/LicenseManager.exe` sau khi build
4. Chạy thử ứng dụng để đảm bảo hoạt động đúng

## Version
- License Manager UI: v1.0
- Build Date: 2025-01-XX








