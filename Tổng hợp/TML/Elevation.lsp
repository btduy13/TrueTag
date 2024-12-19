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
  (setq null (getstring "null"))
  (setq platformEnt (car (entsel "\nSelect Platform text: ")))
  (if (not platformEnt)
    (progn
      (princ "\nNo Platform text selected. Exiting.")
      (exit)
    )
  )

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
  ; Format riser text
  (setq riserValue (formatRiser riserText))

  ;; Get platform text
  (setq platformText (cdr (assoc 1 (entget platformEnt))))
  (setq platformValue (formatPlatform platformText))

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
    (setq csvData (cons (atof (vl-string-trim " " value)) csvData))  ;; Convert string to float and add to list
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

  ;; Initialize list to store points and elevations
  (setq pointList '())
  (setq continue T)  ; Thêm biến điều khiển vòng lặp
  
  ;; Loop to collect points and elevations until user cancels
  (while continue
    (setq pt (getpoint "\nSelect point or press ESC to finish: "))
    (if (not pt)
      (progn
        (if (< (length pointList) 2)
          (progn
            (princ "\nAt least 2 points are required. Exiting.")
            (exit)
          )
          (progn
            (princ "\nPoint selection completed.")
            (setq continue nil)  ; Thoát vòng lặp
          )
        )
      )
      (progn  ; Nếu có điểm được chọn
        (setq elev (getreal (strcat "\nEnter elevation for point " (itoa (+ 1 (length pointList))) ": ")))
        (setq pointList (append pointList (list (list pt elev))))
      )
    )
  )

  ;; Process segments between consecutive points
  (if (> (length pointList) 1)  ; Kiểm tra có đủ điểm không
    (progn
      (setq i 0)
      (repeat (1- (length pointList))
        (setq pt1 (car (nth i pointList)))
        (setq minElev (cadr (nth i pointList)))
        (setq pt2 (car (nth (1+ i) pointList)))
        (setq maxElev (cadr (nth (1+ i) pointList)))
        
        ;; Calculate vector direction for this segment
        (setq vector (mapcar '- pt2 pt1))
        
        ;; Create Block if not already defined
        (if (not (tblsearch "block" blkname))
          (createBlock blkname clayerb clayer1 pt1 radius htx wdy styname)
          (princ (strcat "\nBlock " blkname " already exists."))
        )

        ;; Process CSV data for this segment
        (foreach csvValue csvData
          ;; Check if the CSV value is within the elevation range of this segment
          (if (and (>= csvValue (min minElev maxElev)) 
                   (<= csvValue (max minElev maxElev)))
            (progn
              ;; Calculate interpolation factor
              (setq interpFactor (/ (- csvValue minElev) (- maxElev minElev)))
              
              ;; Calculate new insertion point using interpolation
              (setq newPt (mapcar '(lambda (a b) (+ a (* interpFactor b))) pt1 vector))
              
              ;; Format the CSV number
              (setq csvNum (rtos csvValue 2 2))
              
              ;; Construct attribute text
              (setq attrText (strcat platformValue "-" riserValue "_TML" csvNum))
              
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
              
              ;; Provide feedback
              (princ (strcat "\nBlock placed at " 
                            (rtos (car newPt) 2 2) ", " 
                            (rtos (cadr newPt) 2 2) 
                            " with tag " attrText))
            )
          )
        )
        (setq i (1+ i))
      )
    )
  )

  ;; Confirmation Message
  (princ "\nAll blocks have been successfully placed based on CSV data along the selected points.")
  (princ)
)

(defun formatPlatform (platform)
  "Format the platform name by removing hyphens."
  ;; Remove all hyphens from the platform name
  (setq platform (vl-string-subst "" "-" platform))

  ;; Debug: Print the formatted platform
  (princ (strcat "\nFormatted Platform: " platform))

  platform
)

(defun formatRiser (riser)
  "Format the riser text by removing 'No.', periods, and adding leading zero if necessary."
  ;; Remove "No." and any periods from the riser text
  (setq riser (vl-string-subst "" "No." riser))
  (setq riser (vl-string-subst "" "." riser))  ;; Remove any periods

  ;; Add leading zero if necessary and prepend 'R'
  (setq riser (strcat "R" (if (< (strlen riser) 2) (strcat "0" riser) riser)))

  ;; Debug: Print the formatted riser
  (princ (strcat "\nFormatted Riser: " riser))

  riser
)

(defun formatNumber (num)
  "Ensure the number is in 2-digit format."
  (if (< (strlen num) 2)
    (setq num (strcat "0" num))
  )
  num
)

(defun createBlock (blkname clayerb clayer1 insertionPoint radius htx wdy styname)
  "Create a block with a circle and an attribute definition."
  ;; Create the BLOCK definition
  (entmake 
    (list 
      '(0 . "BLOCK") 
      (cons 2 blkname)           ; Block name
      '(70 . 2) 
      (cons 8 clayerb)           ; Layer
      (cons 10 insertionPoint)   ; Insertion point
      '(4 . "SRVPNOC Value")     ; Comment
    )
  )

  ;; Add a CIRCLE to the BLOCK
  (entmake 
    (list 
      '(0 . "CIRCLE")
      (cons 8 clayerb)           ; Layer
      (cons 10 insertionPoint)   ; Insertion point
      (cons 40 radius)           ; Radius of the circle
    )
  )

  ;; Add an ATTDEF to the BLOCK
  (entmake 
    (list 
      '(0 . "ATTDEF") 
      (cons 8 clayer1)           ; Layer
      (cons 10 insertionPoint)   ; Insertion point
      '(70 . 1)                  ; Attribute flags (1 = Locked)
      '(3 . "NAME")              ; Prompt
      '(2 . "EQ_TAG")            ; Tag 
      '(1 . "+")                 ; Default value
      (cons 40 htx)              ; Height
      (cons 41 wdy)              ; Width
      (cons 7 styname)           ; Text style
      (cons 11 insertionPoint)   ; Alignment point           
      '(72 . 0)                  ; Text generation flags
    )
  )

  ;; End the BLOCK definition
  (entmake '((0 . "ENDBLK")))   
)
