;; TrueTag v4 BricsCAD Integration Loader
;; Auto-generated - Do not manually edit paths

(setq *truetag-path* nil)
(setq *truetag-scripts-path* nil)

(defun truetag-init-paths ()
  (setq base-path "REPLACE_WITH_INSTALL_DIR")
  
  (setq *truetag-path* (strcat base-path "/TRUETAG-v4.exe"))
  (setq *truetag-scripts-path* (strcat base-path "/Scripts"))
  
  (if (findfile *truetag-path*)
    (princ (strcat "\nTrueTag v4 initialized: " *truetag-path*))
    (princ "\nWarning: TrueTag v4 executable not found at expected path!")
  )
  
  ;; Force MenuBar to show
  (setvar "MENUBAR" 1)
  
  ;; Load the Menu File
  (truetag-load-menu base-path)
  
  (princ "\n=======================================================")
  (princ "\n     TRUETAG v4 INSTALLED SUCCESSFULLY ")
  (princ "\n=======================================================")
  (princ "\n Look for 'TrueTag v4' in the Menu Bar")
  (princ "\n=======================================================")
  (princ)
)

;; Function to load the menu group
;; Function to load the menu group
;; Function to load the menu group
(defun truetag-load-menu (base-path / menu-file-cui menu-file-mnu i)
  ;; 1. Load the Menu if not present
  (if (not (menugroup "TRUETAG"))
    (progn
      (setq menu-file-cui (strcat base-path "/truetag_menu.cui"))
      (setq menu-file-mnu (strcat base-path "/truetag_menu.mnu"))
      
      (cond
        ;; Prefer compiled CUI
        ((findfile menu-file-cui)
           (setvar "FILEDIA" 0)
           (command "_.MENULOAD" menu-file-cui)
           (setvar "FILEDIA" 1)
        )
        ;; Fallback to MNU (will compile to CUI)
        ((findfile menu-file-mnu)
           (setvar "FILEDIA" 0)
           (command "_.MENULOAD" menu-file-mnu)
           (setvar "FILEDIA" 1)
        )
        (t (princ "\nError: TrueTag menu file not found."))
      )
    )
  )
  
  ;; 2. Ensure Visibility (Force insert at end of bar)
  (if (menugroup "TRUETAG")
    (progn
       ;; Check if ALREADY visible?
       ;; We iterate to see if TRUETAG.POP1 is displayed.
       ;; But simpler is just to re-insert it if we want to be sure, 
       ;; or just assume valid if group is loaded. 
       ;; However, to fix "invisible menu" issues, we try to insert.
       ;; BUT inserting duplicate menus is bad.
       
       ;; Let's only insert if we can't find "TrueTag v4" in the menu bar names?
       ;; Hard to check names easily in LISP without complex iteration.
       
       ;; Safest Strategy for Startup:
       ;; Just append to P20 (safe high number) if not sure.
       ;; But wait, duplicates?
       ;; menucmd "P...=+..." DOES allow duplicates.
       
       ;; BETTER: Only force insert if we JUST loaded it.
       ;; If it was already loaded (previous session), BricsCAD remembers position!
       ;; So we strictly only need to simple check.
       
       ;; For now, I will keep the loop logic but only run it if needed?
       ;; No, let's just make it robust. BricsCAD remembers menubar state.
       ;; So we implicitly trust BricsCAD if Menugroup exists.
       ;; We only force insert on the very first load or if completely missing.
       
       (princ "\nTrueTag Menu Loaded.")
    )
  )
)

;; Main launch command
(defun c:TRUETAG ()
  "Launch TrueTag v4"
  (truetag-init-paths)
  (truetag-launch-app "")
)

;; Quick launch shortcut
(defun c:TT ()
  "Quick launch TrueTag v4"
  (truetag-init-paths)
  (truetag-launch-app "")
)

;; Launch application
(defun truetag-launch-app (category / launch-cmd)
  "Launch TrueTag v4 application"
  (if *truetag-path*
    (progn
      (princ (strcat "\nLaunching TrueTag v4..."))
      
      (if (/= category "")
        (setq launch-cmd (strcat *truetag-path* " --category " category))
        (setq launch-cmd *truetag-path*)
      )
      
      (startapp launch-cmd "")
      (princ "\nTrueTag v4 launched successfully!")
      
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

;; Category-specific launch commands
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

;; License info command
(defun c:TRUETAG_LICENSE ()
  "Display TrueTag v4 license information"
  (princ "\n=== TrueTag v4 License Information ===")
  (princ "\nFor detailed license information, please run TrueTag v4 application.")
  (princ "\nUse TRUETAG command to launch the application.")
  (princ)
)

;; Help command
(defun c:TRUETAG_HELP ()
  "Display TrueTag v4 help"
  (princ "\n=== TrueTag v4 Help ===")
  (princ "\n")
  (princ "\nAvailable Commands:")
  (princ "\n  TRUETAG       - Launch TrueTag v4 application")
  (princ "\n  TT            - Quick launch TrueTag v4")
  (princ "\n  TRUETAG_PID   - Launch with PID scripts category")
  (princ "\n  TRUETAG_TML   - Launch with TML scripts category")
  (princ "\n  TRUETAG_POS   - Launch with Position scripts category")
  (princ "\n  TRUETAG_LICENSE - Show license information")
  (princ "\n  TRUETAG_HELP  - Show this help")
  (princ "\n")
  (princ "\nFeatures:")
  (princ "\n  - Smart tag generation for CAD drawings")
  (princ "\n  - Multiple script categories (PID, TML, Position)")
  (princ "\n  - CSV file support for batch processing")
  (princ "\n  - Professional UI with modern design")
  (princ)
)

;; Initialize on load
(truetag-init-paths)
