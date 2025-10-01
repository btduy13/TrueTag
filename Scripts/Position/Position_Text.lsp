(defun c:Position_Text (csvPath)
  (princ "\nStarting script...")

  ;; Prompt user for platform name
  (setq null (getstring "\n"))
  (setq platformName (getstring "\nEnter Platform Name (e.g., BK14): "))

  ;; Prompt user for riser number format
  (princ "\nSelect Riser Number Format:")
  (princ "\n1. RISER-XX")
  (princ "\n2. RXX")
  (princ "\n3. R. XX")
  (princ "\n4. NO.XX")
  (princ "\n5. RISER NO.XX")
  (princ "\n6. R.XX")
  (setq formatChoice (getstring "\nEnter choice (1-6): "))

  ;; Convert platform name to uppercase
  (setq platformName (strcase platformName))

  ;; Path to the CSV file
  ; (setq csvPath "C:/Users/USER/Desktop/AUTOCAD_test/Riser_list.csv")

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

        ;; Check if the text matches the selected format
        (if (cond 
              ((= formatChoice "1") (wcmatch text "RISER-*"))
              ((= formatChoice "2") (wcmatch text "R[0-9]*"))
              ((= formatChoice "3") (wcmatch text "R. *"))
              ((= formatChoice "4") (wcmatch text "NO.*"))
              ((= formatChoice "5") (wcmatch text "RISER NO.*"))
              ((= formatChoice "6") (wcmatch text "R.*"))
            )
          (progn
            ;; Extract the riser number based on the selected format
            (setq riserNum
              (cond
                ((= formatChoice "1") (substr text 7))
                ((= formatChoice "2") (substr text 2))
                ((= formatChoice "3") (vl-string-trim " " (substr text 4)))
                ((= formatChoice "4") (substr text 4))
                ((= formatChoice "5") (substr text 10))
                ((= formatChoice "6") (substr text 3))
              )
            )

            ;; Convert to "R01" format if needed
            (if (< (atoi riserNum) 10)
              (setq riserNum (strcat "0" (itoa (atoi riserNum))))
              (setq riserNum (itoa (atoi riserNum)))
            )

            ;; Build the final sequence in the "R01" format
            (setq finalSequence (strcat platformName "-R" riserNum))
            (princ (strcat "\nFinal sequence to search: " finalSequence))

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

            ;; Find the actual sequence from the CSV
            (setq matchedCode (find-matching-sequence finalSequence codes))

            ;; Check if a match is found
            (if matchedCode
              (progn
                (princ (strcat "\nMatched sequence: " matchedCode))

                ;; Use the text's insertion point as the insertion point for the block
                (setq insPt textInsertionPoint)
                (princ (strcat "\nInsertion point: " (vl-princ-to-string insPt)))

                ;; Check if there's a comma in the matched code
                (if (vl-string-search "," matchedCode)
                  (progn
                    ;; Split the matched code by comma
                    (setq splitCodes (parse-split matchedCode ","))

                    ;; Initialize starting insertion point
                    (setq baseInsPt insPt)
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
                    (create-block "EQ_BLOCK" insPt matchedCode)

                    (princ (strcat "\nBlock created and inserted for: " matchedCode))
                  )
                )
              )
              (princ (strcat "\nNo match found for: " finalSequence))
            )
          )
        )
      )
      (princ "\nDone.")

      ;; Open the Save As dialog and suggest the file name
      (setq saveAsName (strcat platformName "-IARP.dwg"))
      (setq savePath (getfiled "Save As" saveAsName "dwg" 1))

      ;; Save the drawing if the user selected a path
      (if savePath
        (command "_.SAVEAS" "" savePath)
      )

    )
  )
  (princ)
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
