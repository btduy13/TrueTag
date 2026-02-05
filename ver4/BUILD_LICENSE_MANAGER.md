# License Manager UI - Build Instructions

## Tổng Quan
Hướng dẫn build ứng dụng License Manager UI thành file thực thi (.exe) độc lập trên Windows.

## Yêu Cầu Hệ Thống
- Python 3.7 trở lên
- Windows 10/11
- PyInstaller 6.0 trở lên
- ttkbootstrap 1.10.1 trở lên

## Cài Đặt Dependencies

### Cách 1: Sử dụng requirements.txt
```bash
pip install -r requirements.txt
```

### Cách 2: Cài đặt thủ công
```bash
pip install pyinstaller>=6.0.0
pip install ttkbootstrap>=1.10.1
```

## Build Application

### Cách 1: Sử dụng Batch Script (Windows)
```bash
build_license_manager.bat
```

### Cách 2: Sử dụng Python Script
```bash
python build_license_manager.py
```

### Cách 3: Sử dụng PyInstaller trực tiếp
```bash
pyinstaller license_manager_ui.spec --clean --noconfirm
```

## Kết Quả Build
Sau khi build thành công, file thực thi sẽ được tạo trong thư mục `dist/`:
- `dist/LicenseManager.exe` - File thực thi chính

## Cấu Trúc File
```
ver4/
├── license_manager_ui.py          # File chính
├── license_generator.py           # Module tạo license
├── license_server.py              # Module server
├── license_manager_ui.spec        # PyInstaller spec file
├── build_license_manager.bat      # Batch build script
├── build_license_manager.py       # Python build script
├── logo.ico                       # Icon file
└── dist/
    └── LicenseManager.exe         # File thực thi (sau khi build)
```

## Dependencies
- `license_generator.py` - Tạo và quản lý license keys
- `license_server.py` - Mô phỏng server validation
- `logo.ico` - Icon cho ứng dụng
- `license_config.json` - File cấu hình (tự động tạo nếu không có)
- `server_config.json` - File cấu hình server (tự động tạo nếu không có)
- `license_database.json` - Database license (tự động tạo nếu không có)

## Troubleshooting

### Lỗi: ModuleNotFoundError
- Kiểm tra xem đã cài đặt đầy đủ dependencies chưa
- Chạy lại: `pip install -r requirements.txt`

### Lỗi: FileNotFoundError (logo.ico)
- Đảm bảo file `logo.ico` tồn tại trong thư mục `ver4/`
- Hoặc chỉnh sửa `license_manager_ui.spec` để bỏ icon nếu không cần

### Lỗi: Build failed
- Xóa thư mục `build/` và `dist/` rồi build lại
- Kiểm tra log trong thư mục `build/` để xem chi tiết lỗi

### Ứng dụng chạy chậm
- Thử build với `--onefile` để tạo file đơn lẻ (nhưng sẽ chậm hơn khi khởi động)
- Hoặc giữ nguyên build hiện tại (--onedir) để khởi động nhanh hơn

## Chạy Ứng Dụng
Sau khi build thành công, bạn có thể chạy ứng dụng bằng cách:
1. Double-click vào `dist/LicenseManager.exe`
2. Hoặc chạy từ command line: `dist\LicenseManager.exe`

## Ghi Chú
- Ứng dụng sẽ tự động tạo các file cấu hình và database nếu chúng không tồn tại
- Các file cấu hình sẽ được lưu trong thư mục chứa file .exe
- Để phân phối ứng dụng, chỉ cần copy file `LicenseManager.exe` và các file cấu hình (nếu cần)

## Version
- License Manager UI: v1.0
- Build Date: 2025








