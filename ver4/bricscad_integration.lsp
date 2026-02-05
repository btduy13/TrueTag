;; TrueTag v4 Advanced BricsCAD Integration
;; Tích hợp nâng cao TrueTag v4 vào BricsCAD với các tính năng mở rộng

;; Biến toàn cục để lưu trữ thông tin TrueTag
(setq *truetag-path* nil)
(setq *truetag-scripts-path* nil)

;; Khởi tạo đường dẫn TrueTag
(defun truetag-init-paths (/ base-path)
  "Khởi tạo đường dẫn TrueTag v4"
  (setq base-path "E:/OneDrive/Desktop/Truetag")
  
  ;; Kiểm tra các đường dẫn có thể
  (cond
    ;; Đường dẫn tuyệt đối
    ((and (setq *truetag-path* (findfile (strcat base-path "/ver4/TrueTag-ver4.exe"))))
      (setq *truetag-scripts-path* (strcat base-path "/ver4/Scripts"))
    )
    ;; Đường dẫn tương đối
    ((setq *truetag-path* (findfile "ver4/TrueTag-ver4.exe"))
      (setq *truetag-scripts-path* "ver4/Scripts")
    )
    ;; Đường dẫn mặc định
    (t
      (setq *truetag-path* (strcat base-path "/ver4/TrueTag-ver4.exe"))
      (setq *truetag-scripts-path* (strcat base-path "/ver4/Scripts"))
    )
  )
  
  (if *truetag-path*
    (princ (strcat "\nTrueTag v4 initialized: " *truetag-path*))
    (princ "\nWarning: TrueTag v4 path not found!")
  )
)

;; Lệnh chính để launch TrueTag
(defun c:TRUETAG (/ category)
  "Launch TrueTag v4 với tùy chọn category"
  (truetag-init-paths)
  
  ;; Kiểm tra tham số category
  (setq category (getstring "\nEnter script category (PID/TML/POS) or press Enter for default: "))
  
  (if (or (= category "") (= category " "))
    (setq category "")
  )
  
  (truetag-launch-app category)
)

;; Shortcut command
(defun c:TT ()
  "Quick launch TrueTag v4"
  (c:TRUETAG)
)

;; Launch TrueTag với category cụ thể
(defun truetag-launch-app (category / launch-cmd)
  "Launch TrueTag v4 application"
  (if *truetag-path*
    (progn
      (princ (strcat "\nLaunching TrueTag v4: " *truetag-path*))
      
      ;; Tạo command line với category nếu có
      (if (/= category "")
        (setq launch-cmd (strcat *truetag-path* " --category " category))
        (setq launch-cmd *truetag-path*)
      )
      
      ;; Launch application
      (startapp launch-cmd "")
      (princ "\nTrueTag v4 launched successfully!")
      
      ;; Hiển thị thông tin category nếu có
      (if (/= category "")
        (princ (strcat "\nCategory: " (strcase category)))
      )
    )
    (progn
      (princ "\nError: TrueTag v4 executable not found!")
      (princ "\nPlease ensure TrueTag v4 is properly installed.")
    )
  )
  (princ)
)

;; Lệnh cho từng category
(defun c:TRUETAG_PID ()
  "Launch TrueTag v4 with PID scripts"
  (truetag-init-paths)
  (truetag-launch-app "PID")
)

(defun c:TRUETAG_TML ()
  "Launch TrueTag v4 with TML scripts"
  (truetag-init-paths)
  (truetag-launch-app "TML")
)

(defun c:TRUETAG_POS ()
  "Launch TrueTag v4 with Position scripts"
  (truetag-init-paths)
  (truetag-launch-app "POS")
)

;; Hiển thị thông tin license
(defun c:TRUETAG_LICENSE (/ license-file license-content)
  "Hiển thị thông tin license TrueTag v4"
  (princ "\n=== TrueTag v4 License Information ===")
  
  ;; Tìm file license
  (setq license-file (findfile "ver4/license.json"))
  (if (not license-file)
    (setq license-file (findfile "E:/OneDrive/Desktop/Truetag/ver4/license.json"))
  )
  
  (if license-file
    (progn
      (princ (strcat "\nLicense file found: " license-file))
      ;; Đọc và hiển thị thông tin license cơ bản
      (princ "\nFor detailed license information, please run TrueTag v4 application.")
    )
    (princ "\nLicense file not found. Please check TrueTag v4 installation.")
  )
  
  (princ "\nUse TRUETAG command to launch the application and check license details.")
  (princ)
)

;; Hiển thị help
(defun c:TRUETAG_HELP ()
  "Hiển thị help cho TrueTag v4"
  (princ "\n=== TrueTag v4 Help ===")
  (princ "\n")
  (princ "\nAvailable Commands:")
  (princ "\n  TRUETAG    - Launch TrueTag v4 application")
  (princ "\n  TT         - Quick launch TrueTag v4")
  (princ "\n  TRUETAG_PID - Launch with PID scripts category")
  (princ "\n  TRUETAG_TML - Launch with TML scripts category")
  (princ "\n  TRUETAG_POS - Launch with Position scripts category")
  (princ "\n  TRUETAG_LICENSE - Show license information")
  (princ "\n  TRUETAG_HELP - Show this help")
  (princ "\n")
  (princ "\nFeatures:")
  (princ "\n  - Smart tag generation for CAD drawings")
  (princ "\n  - Multiple script categories (PID, TML, Position)")
  (princ "\n  - CSV file support for batch processing")
  (princ "\n  - License management and usage tracking")
  (princ "\n  - Professional UI with modern design")
  (princ "\n")
  (princ "\nFor more information, visit the TrueTag documentation.")
  (princ)
)

;; Kiểm tra script availability
(defun truetag-check-scripts (/ script-dirs available-scripts)
  "Kiểm tra các script có sẵn"
  (truetag-init-paths)
  
  (if *truetag-scripts-path*
    (progn
      (princ "\n=== TrueTag v4 Scripts Status ===")
      (setq script-dirs '("PID" "TML" "Position"))
      
      (foreach dir script-dirs
        (setq script-path (strcat *truetag-scripts-path* "/" dir))
        (princ (strcat "\n" dir " Scripts: "))
        (if (vl-file-directory-p script-path)
          (princ "Available")
          (princ "Not Found")
        )
      )
    )
    (princ "\nScripts path not initialized!")
  )
  (princ)
)

;; Lệnh kiểm tra scripts
(defun c:TRUETAG_CHECK ()
  "Kiểm tra trạng thái scripts TrueTag v4"
  (truetag-check-scripts)
)

;; Auto-load khi BricsCAD khởi động
(defun c:TRUETAG_AUTO_LOAD (/)
  "Auto-load TrueTag v4 integration"
  (princ "\n=== TrueTag v4 Integration ===")
  (princ "\nIntegration loaded successfully!")
  (princ "\n")
  (princ "\nQuick Commands:")
  (princ "\n  TRUETAG or TT - Launch TrueTag v4")
  (princ "\n  TRUETAG_HELP - Show help")
  (princ "\n  TRUETAG_CHECK - Check scripts status")
  (princ)
)

;; Khởi tạo integration
(c:TRUETAG_AUTO_LOAD)

;; Thông báo load thành công
(princ "\n")
(princ "==========================================")
(princ "\nTrueTag v4 BricsCAD Integration v1.0")
(princ "\n==========================================")
(princ "\nReady to use! Type 'TRUETAG' to launch.")
(princ)
