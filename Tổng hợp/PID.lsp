(defun c:PID (csvPath)
  (princ "\nStarting script...")

  ; Prompt user for platform name
  (setq null (getstring "\null"))
  (setq platformName (getstring "\nEnter Platform Name (e.g., BK14): "))

  ; Convert platform name to uppercase
  (setq platformName (strcase platformName))

  ; Use the CSV path passed from the Python program
  (if (not (findfile csvPath))
    (princ "\nCSV file not found.")
    (progn
      (setq file (open csvPath "r"))
      (setq codes '())
      (read-line file) ; Skip the header line

      ; Read CSV and store equipment codes
      (while (setq line (read-line file))
        (if (> (strlen line) 0)
          (setq codes (cons (strcase line) codes))
        )
      )
      (close file)
      (princ (strcat "\nCodes read: " (itoa (length codes))))

      ; Search for text and mtext entities
      (setq ss (ssget "X" '((0 . "TEXT,MTEXT"))))
      (setq len (sslength ss))
      (princ (strcat "\nText entities found: " (itoa len)))

      (repeat len
        (setq ent (ssname ss (setq len (1- len))))
        (setq data (entget ent))
        (setq text (strcase (cdr (assoc 1 data))))
        (princ (strcat "\nEvaluating text: " text))

        ; Check if the text starts with "RISER-" or "R"
        (if (or (wcmatch text "RISER-*")
                (wcmatch text "R[0-9]*"))
          (progn
            ; Extract the riser number based on the text format
            (if (wcmatch text "RISER-*")
              (setq riserNum (substr text 7))
              (setq riserNum (substr text 2))
            )

            ; Convert to "R01" format if needed
            (if (< (atoi riserNum) 10)
              (setq riserNum (strcat "0" (itoa (atoi riserNum))))
              (setq riserNum (itoa (atoi riserNum)))
            )

            ; Build the final sequence in the "R01" format
            (setq finalSequence (strcat platformName "-R" riserNum))
            (princ (strcat "\nFinal sequence to search: " finalSequence))

            ; Custom function to find the matching sequence in codes
            (defun find-matching-sequence (seq codes)
              (setq found nil)
              (foreach code codes
                (if (wcmatch code (strcat "*" seq "*"))
                  (setq found code)
                )
              )
              found
            )

            ; Find the actual sequence from the CSV
            (setq matchedCode (find-matching-sequence finalSequence codes))

            ; Check if a match is found
            (if matchedCode
              (progn
                (princ (strcat "\nMatched sequence: " matchedCode))

                ; Check if there's a comma in the matched code
                (if (vl-string-search "," matchedCode)
                  (progn
                    ; Split the matched code by comma
                    (setq splitCodes (parse-split matchedCode ","))

                    ; Initialize starting insertion point
                    (setq baseInsPt (cdr (assoc 10 data)))
                    (setq offsetX 0.5) ; Define offset distance for placement

                    (foreach code splitCodes
                      (setq code (vl-string-trim " " code)) ; Trim any whitespace
                      (princ (strcat "\nSplit sequence: " code))

                      ; Calculate the insertion point for this block
                      (setq currentInsPt (list (+ (car baseInsPt) (* offsetX (length splitCodes)))
                                               (cadr baseInsPt)
                                               (caddr baseInsPt)))
                      
                      (princ (strcat "\nInsertion point: " (vl-princ-to-string currentInsPt)))

                      ; Call block creation function to create and insert block for each split code
                      (create-block "EQ_BLOCK" currentInsPt code)

                      (princ (strcat "\nBlock created and inserted for: " code))

                      ; Update base insertion point for next block
                      (setq baseInsPt (list (+ (car baseInsPt) offsetX) (cadr baseInsPt) (caddr baseInsPt)))
                    )
                  )
                  ; If no comma, proceed as usual
                  (progn
                    ; Get insertion point
                    (setq insPt (cdr (assoc 10 data)))
                    (princ (strcat "\nInsertion point: " (vl-princ-to-string insPt)))

                    ; Call block creation function to create and insert block
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

; Utility function to split a string by a delimiter
(defun parse-split (str delim / result pos)
  (setq result '())
  (while (setq pos (vl-string-search delim str))
    (setq result (cons (substr str 1 pos) result))
    (setq str (substr str (+ pos 2))))
  (setq result (cons str result))
  (reverse result)
)
