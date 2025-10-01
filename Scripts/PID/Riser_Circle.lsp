(defun c:Riser_Circle (csvPath)
  (princ "\nStarting script...")

  ;; Prompt user for platform name
  (setq null (getstring "\n"))
  (setq platformName (getstring "\nEnter Platform Name (e.g., BK14): "))

  ;; Convert platform name to uppercase
  (setq platformName (strcase platformName))

  ;; Get geometry type once at the start
  (princ "\nSelect a sample geometry type on screen: ")
  (setq sample-ent (car (entsel)))
  (if (not sample-ent)
    (progn
      (princ "\nNo geometry selected. Script terminated.")
      (exit)
    )
  )
  (setq target-type (cdr (assoc 0 (entget sample-ent))))
  (princ (strcat "\nSelected geometry type: " target-type))

  ;; Check if CSV file exists
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

      ;; Get available geometries without blocks
      (setq availableGeoms (get-available-geometries target-type))
      (princ (strcat "\nAvailable geometries: " (itoa (length availableGeoms))))

      ;; Search for text and mtext entities
      (setq ss (ssget "X" '((0 . "TEXT,MTEXT"))))
      (setq len (sslength ss))
      (princ (strcat "\nText entities found: " (itoa len)))

      ;; Process each text entity
      (repeat len
        (setq ent (ssname ss (setq len (1- len))))
        (setq data (entget ent))
        (setq text (strcase (cdr (assoc 1 data))))
        (setq textInsertionPoint (cdr (assoc 10 data))) ;; Get the insertion point of the text
        (princ (strcat "\nEvaluating text: " text))

        ;; Check if the text starts with "RISER-", "R", "R. ", or "No."
        (if (or (wcmatch text "RISER-*")
                (and (wcmatch text "R[0-9]*")(< (strlen text) 4))
                (wcmatch text "R. *"))
          (progn
            ;; Extract the riser number based on the text format
            (cond
              ((wcmatch text "RISER-*")
               (setq riserNum (substr text 7)))
              ((wcmatch text "R[0-9]*")
               (setq riserNum (substr text 2)))
              ((wcmatch text "R. *")
               (setq riserNum (vl-string-trim " " (substr text 4))))
            )

            ;; Convert to "R01" format if needed
            (if (< (atoi riserNum) 10)
              (setq riserNum (strcat "0" (itoa (atoi riserNum))))
              (setq riserNum (itoa (atoi riserNum)))
            )

            ;; Build the final sequence in the "R01" format
            (setq finalSequence (strcat platformName "-R" riserNum))
            (princ (strcat "\nFinal sequence to search: " finalSequence))

            ;; Find the actual sequence from the CSV
            (setq matchedCode (find-matching-sequence finalSequence codes))

            ;; Check if a match is found
            (if matchedCode
              (progn
                (princ (strcat "\nMatched sequence: " matchedCode))

                ;; Use the text's insertion point to find the nearest available geometry
                (setq nearestGeom (find-nearest-geometry textInsertionPoint availableGeoms))
                (if nearestGeom
                  (progn
                    ;; Get the geometry entity and position
                    (setq nearestGeomEnt (car nearestGeom))
                    (setq nearestGeomPos (cadr nearestGeom))
                    (princ (strcat "\nNearest geometry found at: " (vl-princ-to-string nearestGeomPos)))

                    ;; Remove the geometry from availableGeoms
                    (setq availableGeoms (vl-remove nearestGeom availableGeoms))

                    ;; Check if there's a comma in the matched code
                    (if (vl-string-search "," matchedCode)
                      (progn
                        ;; Split the matched code by comma
                        (setq splitCodes (parse-split matchedCode ","))

                        ;; Initialize starting insertion point
                        (setq baseInsPt nearestGeomPos)
                        (setq offsetX 0.05) ;; Define offset distance for placement

                        ;; Place blocks based on the number of codes split by comma
                        (foreach code splitCodes
                          (setq code (vl-string-trim " " code)) ;; Trim any whitespace

                          ;; Only insert block if code is not empty
                          (if (not (eq code ""))
                            (progn
                              (princ (strcat "\nSplit sequence: " code))

                              ;; Calculate the insertion point for this block
                              (setq currentInsPt baseInsPt)

                              ;; Call block creation function to create and insert block for each split code
                              (create-block "EQ_BLOCK" currentInsPt code)

                              (princ (strcat "\nBlock created and inserted for: " code))

                              ;; Update base insertion point for next block
                              (setq baseInsPt (list (+ (car baseInsPt) offsetX) (cadr baseInsPt) (caddr baseInsPt)))
                            )
                          )
                        )
                      )
                      ;; If no comma, proceed as usual
                      (progn
                        ;; Call block creation function to create and insert block
                        (create-block "EQ_BLOCK" nearestGeomPos matchedCode)

                        (princ (strcat "\nBlock created and inserted for: " matchedCode))
                      )
                    )
                  )
                  (princ "\nNo available geometry found.")
                )
              )
              (princ (strcat "\nNo match found for: " finalSequence))
            )
          )
        )
      )
      (princ "\nDone.")

      ;; Open the Save As dialog and suggest the file name
      (setq saveAsName (strcat platformName "-PID.dwg"))
      (setq savePath (getfiled "Save As" saveAsName "dwg" 1))

      ;; Save the drawing if the user selected a path
      (if savePath
        (command "_.SAVEAS" "" savePath)
      )
    )
  )
  (princ)
)

;; Function to get geometry size (area or radius)
(defun get-geometry-size (ent)
  (cond 
    ((= (cdr (assoc 0 (entget ent))) "CIRCLE")
     (cdr (assoc 40 (entget ent)))) ; Return radius for circle
    ((= (cdr (assoc 0 (entget ent))) "ELLIPSE")
     (vlax-curve-getArea (vlax-ename->vla-object ent))) ; Return area for ellipse
    ((= (cdr (assoc 0 (entget ent))) "LWPOLYLINE")
     (vlax-curve-getArea (vlax-ename->vla-object ent))) ; Return area for polyline
    (T nil)
  )
)

;; Function to get available geometries without blocks at their centers
(defun get-available-geometries (geom-type / geomList geomEnt geomPos blockAtGeom tol availableGeoms sampleSize)
  (setq geomList (ssget "X" (list (cons 0 geom-type)))) ;; Get all geometries of specified type
  (setq tol 0.001) ;; Define a tolerance for position matching
  (setq availableGeoms '())
  
  ;; Get the size of the sample geometry
  (setq sampleSize (get-geometry-size sample-ent))
  
  (if geomList
    (progn
      (repeat (setq i (sslength geomList))
        (setq geomEnt (ssname geomList (setq i (1- i))))
        (setq geomPos (get-entity-center geomEnt))
        (setq currentSize (get-geometry-size geomEnt))
        
        ;; Calculate size difference percentage
        (if (and currentSize sampleSize)
          (setq sizeDiff (abs (/ (- currentSize sampleSize) sampleSize)))
          (setq sizeDiff nil)
        )
        
        ;; Check if there is an INSERT at the geometry's center point within a small tolerance
        ;; AND check if the size is within 20% difference
        (setq blockAtGeom (ssget "_C"
                                (mapcar '- geomPos (list tol tol 0))
                                (mapcar '+ geomPos (list tol tol 0))
                                '((0 . "INSERT"))))
        
        (if (and (not blockAtGeom) 
                 sizeDiff 
                 (<= sizeDiff 0.2)) ; 20% threshold
          (setq availableGeoms (cons (list geomEnt geomPos) availableGeoms))
        )
      )
    )
  )
  availableGeoms
)

;; Function to find the nearest available geometry to a given point
(defun find-nearest-geometry (txtPos availableGeoms / nearestGeom minDist dist geom)
  (setq minDist nil)
  (foreach geom availableGeoms
    (setq dist (distance txtPos (cadr geom))) ;; geom is a list (geomEnt geomPos)
    (if (or (not minDist) (< dist minDist))
      (setq minDist dist nearestGeom geom)
    )
  )
  nearestGeom
)

;; Function to get center point of an entity
(defun get-entity-center (ent)
  (cond 
    ((= (cdr (assoc 0 (entget ent))) "CIRCLE")
     (cdr (assoc 10 (entget ent))))
    ((= (cdr (assoc 0 (entget ent))) "ELLIPSE")
     (cdr (assoc 10 (entget ent))))
    ((= (cdr (assoc 0 (entget ent))) "LWPOLYLINE")
     (get-polyline-center ent))
    (T nil)
  )
)

;; Function to get center of a polyline
(defun get-polyline-center (ent)
  (setq bbox (get-bounding-box ent))
  (if bbox
    (list (/ (+ (car (car bbox)) (car (cadr bbox))) 2.0)
          (/ (+ (cadr (car bbox)) (cadr (cadr bbox))) 2.0)
          0.0)
    nil
  )
)

;; Function to get bounding box of an entity
(defun get-bounding-box (ent)
  (if (and (vlax-method-applicable-p (vlax-ename->vla-object ent) 'GetBoundingBox))
    (progn
      (setq vlaObj (vlax-ename->vla-object ent))
      (vla-GetBoundingBox vlaObj 'minPt 'maxPt)
      (list (vlax-safearray->list minPt)
            (vlax-safearray->list maxPt))
    )
    nil
  )
)

;; Function to create a block definition and insert it
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

;; Function to find matching sequence in codes list
(defun find-matching-sequence (sequence codes / result)
  (setq result nil)
  (foreach code codes
    (if (and (not result) (vl-string-search sequence code))
      (setq result code)
    )
  )
  result
)