(defun c:Elevation (csvPath)
  "Place blocks based on CSV data with naming convention platform-Rxx_TML(numberfromCSV) and within an elevation range."
  (setq blkname "EQ_BLOCK"          ; Name of Block
        clayerb "-DRN"              ; Block layer
        clayer1 "-DRNMARK"          ; Attribute definition layer
        styname "STANDARD"          ; Text style
        htx 0.1563                  ; Attribute height
        wdy 0.8                     ; Attribute width
        radius 0.04                 ; Circle radius in block
        sclx 1                      ; Block insert X scale factor
        scly 1                      ; Block insert Y scale factor
        sclz 1                      ; Block insert Z scale factor
  )

  ;; Select Platform Text
  (setq null (getstring "\null"))
  (setq platformEnt (car (entsel "\nSelect Platform text: ")))
  (if (not platformEnt)
    (progn
      (princ "\nNo Platform text selected. Exiting.")
      (exit)
    )
  )
  
  ;; Get platform text (check for valid selection)
  (setq platformText (cdr (assoc 1 (entget platformEnt))))
  ; (if (null platformText)
  ;   (progn
  ;     (princ "\nError: Selected object does not contain valid text.")
  ;     (exit)
  ;   )
  ; )

  ;; Clean and format platform text
  ; (setq platformValue (formatPlatform (cleanText platformText)))

  ;; Select Riser Text
  (setq riserEnt (car (entsel "\nSelect Riser No. text: ")))
  (if (not riserEnt)
    (progn
      (princ "\nNo Riser text selected. Exiting.")
      (exit)
    )
  )
  
  ;; Get riser text (check for valid selection)
  (setq riserText (cdr (assoc 1 (entget riserEnt))))
  ; (if (null riserText)
  ;   (progn
  ;     (princ "\nError: Selected object does not contain valid text.")
  ;     (exit)
  ;   )
  ; )

  ;; Clean and format riser text
  ; (setq riserValue (formatRiser (cleanText riserText)))

  ;; Open CSV File
  (setq csvFile (open csvPath "r"))

  (if (not csvFile)
    (progn
      (princ "\nError: Unable to open the CSV file.")
      (exit)
    )
  )

  (setq csvData '())  ;; Initialize empty list for CSV values

  ;; Read each line from the CSV
  (while (setq value (read-line csvFile))
    ; (if (not (vl-string-empty-p (vl-string-trim " " value)))
      (setq csvData (cons (atof (vl-string-trim " " value)) csvData))  ;; Convert string to float and add to list
    ; )
  )
  (close csvFile)  ;; Close the file after reading
  (setq csvData (reverse csvData))  ;; Reverse to maintain original order

  ;; Validate CSV Data
  (setq totalPoints (length csvData))
  (if (= totalPoints 0)
    (progn
      (princ "\nNo valid data found in CSV file. Exiting.")
      (exit)
    )
  )
  
  ;; Loop to continuously select points and elevation values until user cancels
  (while T
    (setq pt1 (getpoint "\nSelect first point or press ESC to cancel: "))
    (if (not pt1)
      (progn
        (princ "\nUser canceled. Exiting loop.")
        (exit)
      )
    )

    (setq minElev (getreal "\nEnter point 1 elevation: "))

    (setq pt2 (getpoint "\nSelect second point or press ESC to cancel: "))
    (if (not pt2)
      (progn
        (princ "\nUser canceled. Exiting loop.")
        (exit)
      )
    )

    (setq maxElev (getreal "\nEnter point 2 elevation: "))

    ;; Calculate vector direction from point 1 to point 2
    (setq vector (mapcar '- pt2 pt1))

    ;; Create Block if not already defined
    (if (not (tblsearch "block" blkname))
      (createBlock blkname clayerb clayer1 pt1 radius htx wdy styname)
      (princ (strcat "\nBlock " blkname " already exists."))
    )

    ;; Iterate through CSV data and place blocks within the elevation range
    (foreach csvValue csvData
      ;; Check if the CSV value is within the specified elevation range
      (if (and (>= csvValue minElev) (<= csvValue maxElev))
        (progn
          ;; Calculate interpolation factor t
          (setq t (/ (- csvValue minElev) (- maxElev minElev)))

          ;; Calculate new insertion point using interpolation
          (setq newPt (mapcar '(lambda (a b) (+ a (* t b))) pt1 vector))

          ;; Format the CSV number
          (setq csvNum (rtos csvValue 2 2))  ;; Convert value to string with 2 decimal places

          ;; Construct attribute text
          (setq attrText (strcat platformText "-" riserText "_TML+" csvNum))

          ;; Insert the block
          (setq blkRef (vla-InsertBlock 
                         (vla-get-ModelSpace (vla-get-ActiveDocument (vlax-get-Acad-Object))) 
                         (vlax-3D-Point newPt) 
                         blkname 
                         sclx scly sclz 0.0))

          ;; Set the attribute
          (setq attribs (vlax-invoke blkRef 'GetAttributes))
          (foreach attrib attribs
            (if (= (strcase (vla-get-TagString attrib)) "EQ_TAG")
              (vla-put-TextString attrib attrText)
            )
          )

          ;; Provide feedback to the user
          (princ (strcat "\nBlock placed at " 
                         (rtos (car newPt) 2 2) ", " 
                         (rtos (cadr newPt) 2 2) 
                         " with tag " attrText))
        )
      )
    )
  )

  ;; Confirmation Message
  (princ "\nAll blocks have been successfully placed based on CSV data within the elevation range.")
  (princ)
)
