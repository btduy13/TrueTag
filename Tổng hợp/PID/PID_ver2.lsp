(defun C:PID_VER2 (csvPath)
  (princ "\nStarting script...")

  ;; Prompt user for platform name
  (setq nothing (strcase (getstring "\nEnter to continue ")))
  (setq platformName (getstring "\nEnter Platform Name (e.g., BK14): "))

  ;; Convert platform name to uppercase
  (setq platformName (strcase platformName))

  ;; Validate the CSV path
  (if (not (findfile csvPath))
      (princ "\nCSV file not found.")
    (progn
      (setq file (open csvPath "r"))
      (setq codes '())
      (read-line file) ;; Skip the header line

      ;; Read CSV and store equipment codes
      (while (setq line (read-line file))
        (if (> (strlen line) 0)
            (setq codes (cons (strcase line) codes))
        )
      )
      (close file)
      (princ (strcat "\nCodes read: " (itoa (length codes))))

      ;; Search for text and mtext entities
      (setq ss (ssget "X" '((0 . "TEXT,MTEXT"))))
      (setq len (sslength ss))
      (princ (strcat "\nText entities found: " (itoa len)))

      (repeat len
        (setq ent (ssname ss (setq len (1- len))))
        (setq data (entget ent))
        (setq text (strcase (cdr (assoc 1 data))))
        (princ (strcat "\nEvaluating text: " text))

        ;; Process text based on pattern matching
        (cond
          ;; Handle "RISER-" pattern
          ; ((or (wcmatch text "RISER*")
          ;      (wcmatch text "R[0-9]*"))
          ;  (setq riserNum
          ;        (if (wcmatch text "RISER-*")
          ;            (substr text 7)
          ;          (substr text 2)))
          ;  (setq riserNum (strcat (if (< (atoi riserNum) 10) "0" "") (itoa (atoi riserNum))))
          ;  (setq finalSequence (strcat platformName "-R" riserNum))
          ;  (princ (strcat "\nFinal sequence to search: " finalSequence))
          ;  (process-matching-sequence finalSequence codes data)
          ; )

          ;; Handle other text patterns
          (T
           (setq extractedText (extract-first-segment text))
           (setq finalSequence (strcat platformName "-" extractedText))
           (if (and (> (strlen finalSequence) 7)
                    (>= (length (parse-split finalSequence "-")) 2))
               (progn
                 (princ (strcat "\nFinal sequence to search: " finalSequence))
                 (process-matching-sequence finalSequence codes data))
             (princ "\nFinal sequence is 7 characters or fewer, skipping evaluation."))
          )
        )
      )

      (princ "\nDone.")
      
      ;; Save the drawing
      (setq saveAsName (strcat platformName "-PID.dwg"))
      (setq savePath (getfiled "Save As" saveAsName "dwg" 1))
      (if savePath
          (command "_.SAVEAS" "" savePath))
    )
  )
  (princ)
)


; Function to process matching sequences
(defun process-matching-sequence (sequence codes data)
  (setq matchedCode (find-matching-sequence sequence codes))
  (if matchedCode
    (progn
      (princ (strcat "\nMatched sequence: " matchedCode))
      (if (vl-string-search "," matchedCode)
        (progn
          (setq splitCodes (parse-split matchedCode ","))
          (setq baseInsPt (calculate-midpoint (cdr (assoc -1 data))))
          (setq offsetX 0.5)

          (foreach code splitCodes
            (setq code (vl-string-trim " " code))
            (setq currentInsPt (list (+ (car baseInsPt) (* offsetX (length splitCodes)))
                                     (cadr baseInsPt)
                                     (caddr baseInsPt)))
            (create-block "EQ_BLOCK" currentInsPt code)
            (setq baseInsPt (list (+ (car baseInsPt) offsetX) (cadr baseInsPt) (caddr baseInsPt)))
          )
        )
        (progn
          (setq insPt (calculate-midpoint (cdr (assoc -1 data))))
          (create-block "EQ_BLOCK" insPt matchedCode)
        )
      )
    )
    (princ (strcat "\nNo match found for: " sequence))
  )
)

; Function to create a block definition and insert it
(defun create-block (blkname insertionPoint eqtag / clayerb clayer1 styname htx wdy radius)
  (setq
    clayerb "-DRN"              ; defined block layer
    clayer1 "-DRNMARK"          ; attribute def layer
    styname "STANDARD"          ; text style
    htx 0.1563                  ; attribute def height
    wdy 0.8                     ; attribute def width
    radius 0.04                 ; radius of the circle
  )

  ; Create block definition
  (entmake 
    (list 
      '(0 . "BLOCK") 
      (cons 2 blkname) ; block name
      '(70 . 2) 
      (cons 8 clayerb)  ; layer
      (cons 10 insertionPoint)  ; insertion point
      '(4 . "SRVPNOC Value")    ; comment
    )
  )
  (entmake 
    (list 
      '(0 . "CIRCLE")
      (cons 8 clayerb)          ; layer
      (cons 10 insertionPoint)  ; insertion point
      (cons 40 radius)          ; radius of the circle
    )
  )
  (entmake 
    (list 
      '(0 . "ATTDEF") 
      (cons 8 clayer1)          ; layer
      (cons 10 insertionPoint)  ; insertion point
      '(70 . 1)                 ; attribute flags (2 = invisible)
      '(3 . "NAME")             ; 3=Prompt
      '(2 . "EQ_TAG")           ; 2=Tag 
      (cons 1 eqtag)            ; 1=default value
      (cons 40 htx)             ; height
      (cons 41 wdy)             ; width
      (cons 7 styname)          ; text style
      (cons 11 insertionPoint)  ; match insertion point            
      '(72 . 0)                 ; 0=10 as insertion point
    )
  )
  (entmake '((0 . "ENDBLK")))   ; end of block with attdef

  ; Insert block
  (vla-InsertBlock (vla-get-modelspace (vla-get-activedocument (vlax-get-acad-object)))
                   (vlax-3d-point insertionPoint) blkname 1.0 1.0 1.0 0.0)
)

; Function to calculate midpoint of text/mtext
(defun calculate-midpoint (entity)
  (if (and (vlax-method-applicable-p (vlax-ename->vla-object entity) 'GetBoundingBox))
    (progn
      (setq vlaObj (vlax-ename->vla-object entity)) ; Convert to VLA object
      (vla-GetBoundingBox vlaObj 'minPt 'maxPt)    ; Get bounding box
      (setq minPt (vlax-safearray->list minPt))    ; Convert to list
      (setq maxPt (vlax-safearray->list maxPt))    ; Convert to list
      (mapcar '(lambda (a b) (/ (+ a b) 2)) minPt maxPt) ; Calculate midpoint
    )
    (cdr (assoc 10 (entget entity))) ; Fallback to insertion point if bounding box fails
  )
)


; Utility function to find a matching sequence in codes
(defun find-matching-sequence (seq codes)
  (setq found nil)
  (foreach code codes
    ; Ensure exact match after "_"
    (if (and (vl-string-search "_" code)
             (eq (strcase (substr code (+ 2 (vl-string-search "_" code)))) (strcase seq)))
      (setq found code)
    )
  )
  found
)


; Function to extract the first segment of text up to the first space
(defun extract-first-segment (txt)
  (if (vl-string-search " " txt)
    (substr txt 1 (vl-string-search " " txt))
    txt
  )
)

; Utility function to split a string by a delimiter
(defun parse-split (str delim / result pos)
  (setq result '())
  (while (setq pos (vl-string-search delim str))
    (setq result (cons (substr str 1 pos) result))
    (setq str (substr str (+ pos 2))))
  (setq result (cons str result))
  (reverse result)
)
