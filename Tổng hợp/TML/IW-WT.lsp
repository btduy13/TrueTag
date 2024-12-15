(defun c:IW-WT (csvPath)
  "Place blocks based on CSV data with naming convention platform-Rxx_TML(numberfromCSV) and within an elevation range."
  
  ;; Initialize Variables
  (setq blkname "EQ_BLOCK"          ; Name of Block
        clayerb "-DRN"              ; Block layer
        clayer1 "-DRNMARK"          ; Attribute definition layer
        styname "STANDARD"           ; Text style
        htx 0.1563                   ; Attribute height
        wdy 0.8                      ; Attribute width
        radius 0.2                  ; Circle radius in block
        sclx 1                       ; Block insert X scale factor
        scly 1                       ; Block insert Y scale factor
        sclz 1                       ; Block insert Z scale factor
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

  ;; Get Riser Text and Format
  (setq riserText (cdr (assoc 1 (entget riserEnt))))
  (setq riserValue (formatRiser riserText))

  ;; Get Platform Text and Format
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

  ;; Read Each Line from the CSV
  (while (setq value (read-line csvFile))
    (setq trimmedValue (vl-string-trim " " value))          ;; Trim spaces
    (setq csvNumber (atof trimmedValue))                   ;; Convert to float
    (princ (strcat "\nRead CSV Value: " (rtos csvNumber 2 4))) ;; Debug: Print CSV value
    (setq csvData (cons csvNumber csvData))                ;; Add to list
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

  ;; Loop to Continuously Select Points and Elevation Values Until User Cancels
  (while T
    ;; Select First Point
    (setq pt1 (getpoint "\nSelect first point or press ESC to cancel: "))
    (if (not pt1)
      (progn
        (princ "\nUser canceled. Exiting loop.")
        (exit)
      )
    )

    ;; Enter First Elevation
    (setq elev1 (getreal "\nEnter elevation for first point: "))
    (princ (strcat "\nElevation of First Point: " (rtos elev1 2 4)))

    ;; Select Second Point
    (setq pt2 (getpoint "\nSelect second point or press ESC to cancel: "))
    (if (not pt2)
      (progn
        (princ "\nUser canceled. Exiting loop.")
        (exit)
      )
    )

    ;; Enter Second Elevation
    (setq elev2 (getreal "\nEnter elevation for second point: "))
    (princ (strcat "\nElevation of Second Point: " (rtos elev2 2 4)))

    ;; Determine Lower and Upper Elevations and Corresponding Points
    (if (< elev1 elev2)
      (progn
        (setq lowerElev elev1)
        (setq upperElev elev2)
        (setq lowerPt pt1)
        (setq upperPt pt2)
        (princ "\nElevation Range: Ascending")
      )
      (progn
        (setq lowerElev elev2)
        (setq upperElev elev1)
        (setq lowerPt pt2)
        (setq upperPt pt1)
        (princ "\nElevation Range: Descending")
      )
    )
    (princ (strcat "\nElevation Range: [" 
                   (rtos lowerElev 2 4) ", " 
                   (rtos upperElev 2 4) "]"))

    ;; Calculate Vector Direction from Lower Point to Upper Point
    (setq vector (mapcar '- upperPt lowerPt))
    (princ (strcat "\nVector: " 
                   (rtos (car vector) 2 4) ", " 
                   (rtos (cadr vector) 2 4) ", " 
                   (rtos (caddr vector) 2 4)))

    ;; Create Block if Not Already Defined
    (if (not (tblsearch "block" blkname))
      (progn
        (createBlock blkname clayerb clayer1 lowerPt radius htx wdy styname)
        (princ (strcat "\nBlock " blkname " created."))
      )
      (princ (strcat "\nBlock " blkname " already exists."))
    )

    ;; Iterate Through CSV Data and Place Blocks Within the Elevation Range
    (foreach csvValue csvData
      ;; Debug: Print CSV Value and Elevation Range
      (princ (strcat "\nProcessing CSV Value: " (rtos csvValue 2 4)))
      (princ (strcat "\nElevation Range: [" (rtos lowerElev 2 4) ", " (rtos upperElev 2 4) "]"))

      ;; Check if the CSV value is within the specified elevation range
      (if (and (>= csvValue lowerElev) (<= csvValue upperElev))
        (progn
          ;; Calculate Interpolation Factor
          (setq elevRange (- upperElev lowerElev))
          (if (= elevRange 0)
            (progn
              (princ "\nError: Elevation range cannot be zero. Skipping this CSV value.")
              (setq interpFactor 0)
            )
            (setq interpFactor (/ (- csvValue lowerElev) elevRange))
          )
          (princ (strcat "\nInterpolation Factor: " (rtos interpFactor 2 4)))

          ;; Calculate New Insertion Point Using Interpolation
          (setq newPt (mapcar '(lambda (a b) (+ a (* interpFactor b))) lowerPt vector))
          (princ (strcat "\nNew Insertion Point: " 
                         (rtos (car newPt) 2 4) ", " 
                         (rtos (cadr newPt) 2 4) ", " 
                         (rtos (caddr newPt) 2 4)))

          ;; Format the CSV Number to Two Decimal Places

          (setq csvNum (formatTwoDecimal csvValue)) 
          (princ (strcat "\nFormatted CSV Number: " csvNum))

          ;; Construct Attribute Text
          (setq attrText (strcat platformValue "-" riserValue "_TML" csvNum))
          (princ (strcat "\nAttribute Text: " attrText))

          ;; Insert the Block
          (setq blkRef (vla-InsertBlock 
                        (vla-get-ModelSpace (vla-get-ActiveDocument (vlax-get-Acad-Object))) 
                        (vlax-3D-Point newPt) 
                        blkname 
                        sclx scly sclz 0.0))
          
          ;; Check if Block Reference was Successfully Created
          (if blkRef
            (progn
              ;; Set the Attribute
              (setq attribs (vlax-invoke blkRef 'GetAttributes))
              (foreach attrib attribs
                (if (= (strcase (vla-get-TagString attrib)) "EQ_TAG")
                  (vla-put-TextString attrib attrText)
                )
              )

              ;; Provide Feedback to the User
              (princ (strcat "\nBlock placed at (" 
                             (rtos (car newPt) 2 2) ", " 
                             (rtos (cadr newPt) 2 2) ", " 
                             (rtos (caddr newPt) 2 2) 
                             ") with tag " attrText))
            )
            (princ "\nError: Block reference could not be created.")
          )
        )
        (princ "\nCSV Value is out of the specified elevation range. Skipping.")
      )
    )

  ;; Confirmation Message
  (princ "\nAll blocks have been successfully placed based on CSV data within the elevation range.")
  (princ)
))

;; Helper Function to Format Platform Name
(defun formatPlatform (platform)
  "Format the platform name by removing hyphens."
  ;; Remove all hyphens from the platform name
  (setq platform (vl-string-subst "" "-" platform))

  ;; Debug: Print the formatted platform
  (princ (strcat "\nFormatted Platform: " platform))

  platform
)

;; Helper Function to Format Riser Text
(defun formatRiser (riser)
  "Format the riser text by removing 'No.', periods, and adding leading zero if necessary."
  ;; Remove "No." and any periods from the riser text
  (setq riser (vl-string-subst "" "No." riser))
  (setq riser (vl-string-subst "" "." riser))  ;; Remove any periods
  (setq riser (vl-string-subst "" " " riser))  ;;Remove any space

  ;; Add leading zero if necessary and prepend 'R'
  (setq riser (strcat "R" (if (< (strlen riser) 2) (strcat "0" riser) riser)))

  ;; Debug: Print the formatted riser
  (princ (strcat "\nFormatted Riser: " riser))

  riser
)

;; Helper Function to Ensure Two Decimal Places
(defun formatTwoDecimal (num)
  "Format a number to two decimal places as a string (e.g., 0 becomes 0.00)."
  (if (numberp num)
    (let ((formattedNum (rtos num 2 2)))  ;; Mode 2: Decimal, Precision 2
      ;; Find the position of the decimal point
      (if (vl-string-search "." formattedNum)
        (progn
          ;; Split the string at the decimal point
          (setq parts (vl-string-split "." formattedNum))
          (setq integerPart (car parts))
          (setq decimalPart (cadr parts))
          ;; Append a '0' if only one decimal place exists
          (if (= (strlen decimalPart) 1)
            (setq formattedNum (strcat integerPart "." decimalPart "0"))
          )
        )
        ;; If no decimal point, append ".00"
        (setq formattedNum (strcat formattedNum ".00"))
      )
      formattedNum
    )
    (progn
      (princ "\nError: Input is not a number.")
      nil
    )
  )
)




;; Helper Function to Create a Block Definition
(defun createBlock (blkname clayerb clayer1 insertionPoint radius htx wdy styname)
  "Create a block with a circle and an attribute definition."
  ;; Start a new block definition
  (command "_.-block" blkname insertionPoint "")

  ;; Add a CIRCLE to the BLOCK
  (command "_.circle" insertionPoint radius)

  ;; Add an ATTDEF to the BLOCK
  (command "_.attdef" 
           "_Invisible"                 ;; Invisible flag
           "_Bottom Left"               ;; Alignment
           (rtos htx 2 4)               ;; Height
           "_Left"                      ;; Text direction
           "NAME"                       ;; Prompt
           "EQ_TAG"                     ;; Tag
           "_Yes"                       ;; Lock position
           (rtos wdy 2 4)               ;; Width factor
           styname                      ;; Text style
  )

  ;; End the BLOCK definition
  (command "_.-endblock")
)

;; Ensure the script is loaded without errors
(princ "\nIW-WT script loaded successfully. Type IW-WT to run.")
(princ)
