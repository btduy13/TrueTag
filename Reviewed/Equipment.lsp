(defun CreateBlock (insertionPoint blkname clayerb clayer1 styname htx wdy radius)
  (entmake 
    (list 
      '(0 . "BLOCK") 
      (cons 2 blkname)  ; block name
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
      '(1 . "+")                ; 1=default value
      (cons 40 htx)             ; height
      (cons 41 wdy)             ; width
      (cons 7 styname)          ; text style
      (cons 11 insertionPoint)  ; match insertion point            
      '(72 . 0)                 ; 0=10 as insertion point
    )
  )
  (entmake '((0 . "ENDBLK")))       ; end of block with attdef
)

(defun c:Equipment (csvPath)
  (princ "\nStarting script...")

  ; Function to strip formatting codes
  (defun stripFormatting (text)
    (vl-string-subst "" "%%U" text)
  )

  ; Function to count occurrences of a character in a string
  (defun countOccurrences (str char)
    (if str
      (progn
        (setq count 0)
        (foreach c (vl-string->list str)
          (if (= c (ascii char))
            (setq count (1+ count))
          )
        )
        count
      )
      0
    )
  )

  ; Search for text and mtext entities
  (setq ss (ssget "X" '((0 . "TEXT,MTEXT"))))
  (setq len (sslength ss))
  (princ (strcat "\nText entities found: " (itoa len)))

  (repeat len
    (setq ent (ssname ss (setq len (1- len))))
    (setq data (entget ent))
    (setq text (strcase (cdr (assoc 1 data))))
    (setq strippedText (stripFormatting text)) ; Strip formatting
    (princ (strcat "\nEvaluating text: " strippedText))

    ; Case 1: Check if text has a specific length (8 or 9) and contains at least two hyphens
    (if (and (>= (countOccurrences strippedText "-") 2)
             (or (= (strlen strippedText) 8) (= (strlen strippedText) 9)))
      (progn
        (princ (strcat "\nValid text found: " strippedText))

        ; Open CSV file and search for the text
        (if (not (findfile csvPath))
          (princ "\nCSV file not found.")
          (progn
            (setq file (open csvPath "r"))
            (read-line file) ; Skip the header line

            (setq matchFound nil)

            (while (and (setq line (read-line file)) (not matchFound))
              (setq code (strcase line))
              (if (= strippedText (substr code 4))
                (progn
                  (setq matchFound t)
                  ; Get insertion point
                  (setq insPt (cdr (assoc 10 data)))
                  (princ (strcat "\nInsertion point: " (vl-princ-to-string insPt)))

                  ; Create block
                  (CreateBlock insPt "EQ_BLOCK" "-DRN" "-DRNMARK" "STANDARD" 0.1563 0.8 0.04)

                  ; Insert block
                  (setq blkRef (vla-InsertBlock
                                 (vla-get-modelspace
                                   (vla-get-activedocument (vlax-get-acad-object)))
                                 (vlax-3d-point insPt) "EQ_BLOCK" 1.0 1.0 1.0 0.0))

                  ; Set attribute
                  (vla-update blkRef)
                  (setq attribs (vlax-invoke blkRef 'getattributes))
                  (foreach attrib attribs
                    (if (= (vla-get-tagstring attrib) "EQ_TAG")
                      (vla-put-textstring attrib code)
                    )
                  )

                  (princ (strcat "\nBlock inserted for: " code))
                )
              )
            )
            (close file)

            (if (not matchFound)
              (princ (strcat "\nNo match found for: " strippedText))
            )
          )
        )
      )
    )

    ; Case 2: Check if text starts with "SV" and contains at least two hyphens
    (if (and (>= (countOccurrences strippedText "-") 2)
             (wcmatch strippedText "SV*"))
      (progn
        (princ (strcat "\nValid text found by prefix: " strippedText))

        ; Open CSV file and search for the stripped text
        (if (not (findfile csvPath))
          (princ "\nCSV file not found.")
          (progn
            (setq file (open csvPath "r"))
            (read-line file) ; Skip the header line

            (setq matchFound nil)

            (while (and (setq line (read-line file)) (not matchFound))
              (setq code (strcase line))
              (if (= strippedText code)
                (progn
                  (setq matchFound t)
                  ; Get insertion point
                  (setq insPt (cdr (assoc 10 data)))
                  (princ (strcat "\nInsertion point: " (vl-princ-to-string insPt)))

                  ; Create block
                  (CreateBlock insPt "EQ_BLOCK" "-DRN" "-DRNMARK" "STANDARD" 0.1563 0.8 0.04)

                  ; Insert block
                  (setq blkRef (vla-InsertBlock
                                 (vla-get-modelspace
                                   (vla-get-activedocument (vlax-get-acad-object)))
                                 (vlax-3d-point insPt) "EQ_BLOCK" 1.0 1.0 1.0 0.0))

                  ; Set attribute
                  (vla-update blkRef)
                  (setq attribs (vlax-invoke blkRef 'getattributes))
                  (foreach attrib attribs
                    (if (= (vla-get-tagstring attrib) "EQ_TAG")
                      (vla-put-textstring attrib strippedText)
                    )
                  )

                  (princ (strcat "\nBlock inserted for: " strippedText))
                )
              )
            )
            (close file)

            (if (not matchFound)
              (princ (strcat "\nNo match found for: " strippedText))
            )
          )
        )
      )
    )
  )

  (princ "\nDone.")
  (princ)
)
