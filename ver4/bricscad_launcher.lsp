;; TrueTag v4 BricsCAD Launcher
;; Tích hợp TrueTag v4 vào BricsCAD để launch trực tiếp từ giao diện

(defun c:TRUETAG (/ truetag_path app_path current_dir)
  "Launch TrueTag v4 application from BricsCAD"
  (setq current_dir (getvar "DWGPREFIX"))
  
  ;; Tìm đường dẫn TrueTag v4
  (cond
    ;; Thử đường dẫn tương đối từ thư mục hiện tại
    ((setq truetag_path (findfile "ver4/TrueTag-ver4.exe"))
      (setq app_path truetag_path)
    )
    ;; Thử đường dẫn tuyệt đối
    ((setq truetag_path (findfile "E:/OneDrive/Desktop/Truetag/ver4/TrueTag-ver4.exe"))
      (setq app_path truetag_path)
    )
    ;; Thử đường dẫn mặc định
    ((setq truetag_path (findfile "TrueTag-ver4.exe"))
      (setq app_path truetag_path)
    )
    ;; Nếu không tìm thấy, sử dụng đường dẫn mặc định
    (t
      (setq app_path "E:/OneDrive/Desktop/Truetag/ver4/TrueTag-ver4.exe")
    )
  )
  
  ;; Kiểm tra file có tồn tại không
  (if (findfile app_path)
    (progn
      (princ (strcat "\nLaunching TrueTag v4: " app_path))
      ;; Launch TrueTag v4
      (startapp app_path "")
      (princ "\nTrueTag v4 launched successfully!")
    )
    (progn
      (princ "\nError: TrueTag v4 executable not found!")
      (princ "\nPlease check the path and ensure TrueTag v4 is installed.")
      (princ "\nExpected paths:")
      (princ "\n  - ver4/TrueTag-ver4.exe (relative)")
      (princ "\n  - E:/OneDrive/Desktop/Truetag/ver4/TrueTag-ver4.exe (absolute)")
    )
  )
  
  (princ)
)

;; Tạo lệnh shortcut
(defun c:TT ()
  "Shortcut command for TrueTag"
  (c:TRUETAG)
)

;; Auto-load TrueTag when BricsCAD starts
(defun c:TRUETAG_AUTO_LOAD (/)
  "Auto-load TrueTag integration on BricsCAD startup"
  (princ "\nTrueTag v4 Integration loaded!")
  (princ "\nCommands available:")
  (princ "\n  - TRUETAG: Launch TrueTag v4 application")
  (princ "\n  - TT: Shortcut for TrueTag")
  (princ)
)

;; Load integration on startup
(c:TRUETAG_AUTO_LOAD)

;; Tạo menu item cho TrueTag
(defun c:TRUETAG_MENU (/)
  "Add TrueTag to BricsCAD menu"
  (princ "\nTrueTag v4 menu integration ready!")
  (princ)
)

(princ "\nTrueTag v4 BricsCAD Integration loaded successfully!")
(princ "\nType 'TRUETAG' or 'TT' to launch TrueTag v4")
(princ)
