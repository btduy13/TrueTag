;; MasterLoader.lsp
;;
;; This AutoLISP program serves as a master loader to include
;; Equipment_Block.lsp and Instrument_Full.lsp into your AutoCAD session
;; and provides a master command to run both scripts.

;; Define the directory where your LISP files are located
(setq *lisp-directory* "C:/Users/User/Desktop/AutoCAD_Test/Idemitsu_Tool/Reviewed/")

;; Ensure the directory path ends with a slash
(if (not (equal (substr *lisp-directory* (strlen *lisp-directory*)) "/"))
  (setq *lisp-directory* (strcat *lisp-directory* "/"))
)

;; Define the LoadLispFile function first
(defun LoadLispFile (filepath)
  "Loads a specified LISP file if it exists."
  (if (findfile filepath)
    (progn
      (load filepath)
      (princ (strcat "\nLoaded: " filepath))
    )
    (princ (strcat "\nError: File not found - " filepath))
  )
)

;; Load Equipment_Block.lsp
(LoadLispFile (strcat *lisp-directory* "Equipment.lsp"))

;; Load Instrument_Full.lsp
(LoadLispFile (strcat *lisp-directory* "Instrument.lsp"))

;; Define the master function to run both scripts
(defun c:MasterLoader (csvPath)
  "Runs both Equipment_Block and Instrument_Full scripts."
  (if (not csvPath)
    (setq csvPath (getfiled "Select CSV File" "" "csv" 0))
  )
  (if csvPath
    (progn
      (princ "\nRunning Equipment_Block...")
      (c:Equipment csvPath) ; Call the Equipment_Block function

      (princ "\nRunning Instrument_Full...")
      (c:Instrument csvPath) ; Call the Instrument_Full function

      (princ "\nAll scripts have been executed successfully.")
    )
    (princ "\nNo CSV file selected. Operation canceled.")
  )
)

;; Provide feedback when the MasterLoader.lsp is loaded
(princ "\nMasterLoader.lsp loaded. Type MasterLoader(*path to CSV file) to execute both scripts.")
(princ)
