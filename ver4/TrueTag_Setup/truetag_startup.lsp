;;; TrueTag v4.1.1 Startup Integration
;;; This file is automatically added to BricsCAD's on_doc_load.lsp

;; Load TrueTag plugin
(defun truetag-load-plugin (/ install-path)
  (setq install-path "REPLACE_WITH_INSTALL_DIR")
  
  ;; Only load once per session
  (if (not (boundp 'TRUETAG-LOADED))
    (progn
      (setq TRUETAG-LOADED T)
      (load (strcat install-path "/truetag_loader.lsp"))
      (princ "\nTrueTag v4 plugin loaded successfully!")
    )
  )
  (princ)
)

;; Auto-load TrueTag
(truetag-load-plugin)
