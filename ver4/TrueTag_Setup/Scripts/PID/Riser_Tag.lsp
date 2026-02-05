(defun c:Riser_Tag (csvPath)
  (princ "\nStarting script...")

  ;; Prompt user for platform name
  (setq null (getstring "\n"))
  (setq platformName (getstring "\nEnter Platform Name (e.g., BK14): "))
  (setq platformName (strcase platformName)) ;; Convert to uppercase

  ;; Let user select a reference circle
  (princ "\nSelect a reference circle: ")
  (setq selectedCircle (car (entsel "\nSelect a circle: ")))

  (if (not selectedCircle)
    (princ "\nNo circle selected. Exiting script.")
    (progn
      (setq selectedCircleData (entget selectedCircle))
      (if (not (eq (cdr (assoc 0 selectedCircleData)) "CIRCLE"))
        (princ "\nSelected entity is not a circle. Exiting script.")
        (progn
          ;; Get radius of selected circle
          (setq selectedCircleRadius (cdr (assoc 40 selectedCircleData))) 
          (princ (strcat "\nSelected circle radius: " (rtos selectedCircleRadius 2 4)))

          ;; Calculate 20% tolerance
          (setq radiusTolerance (* 0.2 selectedCircleRadius))
          (setq minRadius (- selectedCircleRadius radiusTolerance))
          (setq maxRadius (+ selectedCircleRadius radiusTolerance))
          (princ (strcat "\nRadius range for OBSET: " (rtos minRadius 2 4) " - " (rtos maxRadius 2 4)))

          ;; Check if CSV file exists
          (if (not (findfile csvPath))
            (princ "\nCSV file not found.")
            (progn
              ;; Process CSV
              (setq file (open csvPath "r"))
              (setq codes '())
              (read-line file) ;; Skip header

              ;; Read and store codes
              (while (setq line (read-line file))
                (if (> (strlen line) 0)
                  (setq codes (cons (strcase line) codes))
                )
              )
              (close file)
              (princ (strcat "\nCodes read: " (itoa (length codes))))

              ;; Get circles within OBSET that match the radius range
              (setq availableCircles (get-circles-in-radius-range minRadius maxRadius))
              (princ (strcat "\nAvailable circles within radius range: " (itoa (length availableCircles))))

              ;; Process text and mtext entities
              (setq ss (ssget "_X" '((0 . "TEXT,MTEXT"))))
              (setq len (sslength ss))
              (princ (strcat "\nText entities found: " (itoa len)))

              ;; Process each text entity
              (repeat len
                (setq ent (ssname ss (setq len (1- len))))
                (setq data (entget ent))
                (setq text (strcase (cdr (assoc 1 data))))
                (setq textInsertionPoint (cdr (assoc 10 data))) 
                (princ (strcat "\nEvaluating text: " text))

                ;; Check text patterns
                (if (or (wcmatch text "RISER-*")
                        (and (wcmatch text "R[0-9]*") (< (strlen text) 4))
                        (wcmatch text "R. *"))
                  (progn
                    ;; Extract the riser number
                    (cond
                      ((wcmatch text "RISER-*") (setq riserNum (substr text 7)))
                      ((wcmatch text "R[0-9]*") (setq riserNum (substr text 2)))
                      ((wcmatch text "R. *") (setq riserNum (vl-string-trim " " (substr text 4))))
                    )

                    ;; Format riser number
                    (setq riserNum (if (< (atoi riserNum) 10)
                                       (strcat "0" (itoa (atoi riserNum)))
                                       (itoa (atoi riserNum))))

                    ;; Build final sequence
                    (setq finalSequence (strcat platformName "-R" riserNum))
                    (princ (strcat "\nFinal sequence to search: " finalSequence))

                    ;; Find matching sequence in codes
                    (setq matchedCode (find-matching-sequence finalSequence codes))

                    ;; Check for match
                    (if matchedCode
                      (progn
                        (princ (strcat "\nMatched sequence: " matchedCode))

                        ;; Find nearest circle
                        (setq nearestCirc (find-nearest-circle textInsertionPoint availableCircles))
                        (if nearestCirc
                          (progn
                            ;; Get circle entity and position
                            (setq nearestCircEnt (car nearestCirc))
                            (setq nearestCircPos (cadr nearestCirc))
                            (princ (strcat "\nNearest circle found at: " (vl-princ-to-string nearestCircPos)))

                            ;; Remove from available circles
                            (setq availableCircles (vl-remove nearestCirc availableCircles))

                            ;; Place block
                            (create-block "EQ_BLOCK" nearestCircPos matchedCode)
                            (princ (strcat "\nBlock created and inserted for: " matchedCode))
                          )
                          (princ "\nNo available circle found.")
                        )
                      )
                      (princ (strcat "\nNo match found for: " finalSequence))
                    )
                  )
                )
              )
              (princ "\nDone.")
            )
          )
        )
      )
    )
  )
  (princ)
)

;; Get circles within radius range
(defun get-circles-in-radius-range (minRadius maxRadius / circList circEnt circData circRadius result)
  (setq result '())
  (setq circList (ssget "X" '((0 . "CIRCLE")))) ;; Get all circles
  (if circList
    (progn
      (repeat (setq i (sslength circList))
        (setq circEnt (ssname circList (setq i (1- i))))
        (setq circData (entget circEnt))
        (setq circRadius (cdr (assoc 40 circData)))
        (if (and circRadius (>= circRadius minRadius) (<= circRadius maxRadius))
          (setq result (cons (list circEnt (cdr (assoc 10 circData))) result))
        )
      )
    )
  )
  result
)

;; Find nearest circle (same as before)
(defun find-nearest-circle (txtPos availableCircles / nearestCirc minDist dist circ)
  (setq minDist nil)
  (foreach circ availableCircles
    (setq dist (distance txtPos (cadr circ))) ;; circ is a list (circEnt circPos)
    (if (or (not minDist) (< dist minDist))
      (setq minDist dist nearestCirc circ)
    )
  )
  nearestCirc
)


;; Custom function to find the matching sequence in codes
(defun find-matching-sequence (seq codes)
              (setq found nil)
              (foreach code codes
                (if (wcmatch code (strcat "*" seq "*"))
                  (setq found code)
                )
              )
              found
)

(defun create-block (blkname insertionPoint eqtag / clayerb clayer1 styname htx wdy radius)
  (setq
    clayerb "-DRN"              ;; Defined block layer
    clayer1 "-DRNMARK"          ;; Attribute def layer
    styname "STANDARD"          ;; Text style
    htx 0.1563                  ;; Attribute def height
    wdy 0.8                     ;; Attribute def width
    radius 0.04                 ;; Radius of the circle
  )

  ;; Create block definition
  (entmake 
    (list 
      '(0 . "BLOCK") 
      (cons 2 blkname)          ;; Block name
      '(70 . 2) 
      (cons 8 clayerb)          ;; Layer
      (cons 10 insertionPoint)  ;; Insertion point
      '(4 . "SRVPNOC Value")    ;; Comment
    )
  )
  (entmake 
    (list 
      '(0 . "CIRCLE")
      (cons 8 clayerb)          ;; Layer
      (cons 10 insertionPoint)  ;; Insertion point
      (cons 40 radius)          ;; Radius of the circle
    )
  )
  (entmake 
    (list 
      '(0 . "ATTDEF") 
      (cons 8 clayer1)          ;; Layer
      (cons 10 insertionPoint)  ;; Insertion point
      '(70 . 1)                 ;; Attribute flags (2 = invisible)
      '(3 . "NAME")             ;; 3 = Prompt
      '(2 . "EQ_TAG")           ;; 2 = Tag 
      (cons 1 eqtag)            ;; 1 = Default value
      (cons 40 htx)             ;; Height
      (cons 41 wdy)             ;; Width
      (cons 7 styname)          ;; Text style
      (cons 11 insertionPoint)  ;; Match insertion point            
      '(72 . 0)                 ;; 0 = 10 as insertion point
    )
  )
  (entmake '((0 . "ENDBLK")))   ;; End of block with attdef

  ;; Insert block
  (vla-InsertBlock (vla-get-modelspace (vla-get-activedocument (vlax-get-acad-object)))
                   (vlax-3d-point insertionPoint) blkname 1.0 1.0 1.0 0.0)
)

;; Utility function to split a string by a delimiter
(defun parse-split (str delim / result pos)
  (setq result '())
  (while (setq pos (vl-string-search delim str))
    (setq result (cons (substr str 1 pos) result))
    (setq str (substr str (+ pos 2))))
  (setq result (cons str result))
  (reverse result)
)