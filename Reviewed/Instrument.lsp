(defun c:Instrument (csvPath)
  (princ "\nStarting script...")

  ;; Ensure CreateBlock function is defined
  ;; Parameters for CreateBlock can be adjusted as needed
  (defun CreateBlockWrapper (insertionPoint)
    (CreateBlock insertionPoint "EQ_BLOCK" "-DRN" "-DRNMARK" "STANDARD" 0.1563 0.8 0.1)
  )

  ;; Select all circles in the drawing
  (setq circles (ssget "X" '((0 . "CIRCLE"))))

  ;; Select all TEXT and MTEXT objects in the drawing
  (setq texts (ssget "X" '((0 . "TEXT,MTEXT"))))

  ;; Check if circles and texts are found
  (if (and circles texts)
    (progn
      ;; Load the CSV file
      (if (not (findfile csvPath))
        (princ "\nCSV file not found.")
        (progn
          (setq file (open csvPath "r"))
          (setq codes '())
          (read-line file) ; Skip the header line

          ;; Read CSV and store equipment codes
          (while (setq line (read-line file))
            (if (> (strlen line) 0)
              (setq codes (cons (strcase (vl-string-trim " \t\n\r" line)) codes))
            )
          )
          (close file)
          (princ (strcat "\nCodes read: " (itoa (length codes))))

          ;; Check if EQ_BLOCK exists, if not, create it using the first circle's insertion point
          (if (not (tblsearch "block" "EQ_BLOCK"))
            (progn
              (princ "\nEQ_BLOCK does not exist. Creating EQ_BLOCK...")
              (if (> (sslength circles) 0)
                (progn
                  (setq first_circle (ssname circles 0))
                  (setq insertion_point (cdr (assoc 10 (entget first_circle))))
                  (CreateBlockWrapper insertion_point)
                )
                (princ "\nNo circles found to determine insertion point for EQ_BLOCK.")
              )
            )
            (princ "\nEQ_BLOCK already exists.")
          )

          ;; Loop through each circle
          (setq i 0)
          (while (< i (sslength circles))
            (setq circle (ssname circles i))
            ;; Get the circle's center and radius
            (setq circle_center (cdr (assoc 10 (entget circle))))
            (setq radius (cdr (assoc 40 (entget circle))))

            ;; Print information about the circle
            (princ (strcat "\n\nCircle " (itoa (1+ i)) " found with center: " 
                           (rtos (car circle_center) 2 2) "," 
                           (rtos (cadr circle_center) 2 2)))
            (princ (strcat "\nRadius: " (rtos radius 2 2)))

            ;; Define a buffer distance
            (setq buffer 5) ;; Adjust as needed

            ;; Initialize a list to store found texts
            (setq text_list '())

            ;; Loop through each text object to find texts within buffer and on the left side
            (setq j 0)
            (while (< j (sslength texts))
              (setq text (ssname texts j))
              ;; Get the text's insertion point
              (setq text_point (cdr (assoc 10 (entget text))))

              ;; Ensure text_point is valid
              (if (and (listp text_point) (>= (length text_point) 2))
                (progn
                  ;; Define 2D points by ignoring Z-coordinate (if any)
                  (setq circle_center_2d (list (car circle_center) (cadr circle_center)))
                  (setq text_position_2d (list (car text_point) (cadr text_point)))

                  ;; Calculate the distance between text position and circle center
                  (setq dist (distance circle_center_2d text_position_2d))

                  ;; Check if text is within (radius + buffer)
                  (if (<= dist (+ radius buffer))
                    (progn
                      ;; Check if text is on the left side of the circle
                      (if (< (car text_position_2d) (car circle_center_2d))
                        (progn
                          ;; Get the text string
                          (setq text_str (strcase (cdr (assoc 1 (entget text)))))

                          ;; **New Condition**: Only consider texts with length < 5
                          (if (< (strlen text_str) 5)
                            (progn
                              ;; Add the text string to the list
                              (setq text_list (cons text_str text_list))
                            )
                            ;; Optional: Notify about skipped texts
                            (princ (strcat "\n  Skipping text \"" text_str "\" as its length is >= 4."))
                          )
                        )
                      )
                    )
                  )
                )
                (princ "\n  Warning: Invalid text position data.")
              )
              (setq j (1+ j))
            )

            ;; If texts were found on the left side, join them into sequences
            (if text_list
              (progn
                ;; Generate all permutations of the text list
                (setq permutations_list (permutations (reverse text_list))) ; Reverse to maintain original order before permutations

                ;; Initialize a list to store combined text sequences
                (setq combined_texts '())

                ;; Loop through each permutation and combine texts with hyphens
                (foreach perm permutations_list
                  (setq combined_text (apply 'strcat (intersperse "-" perm)))
                  (setq combined_texts (cons combined_text combined_texts))
                )

                ;; Print all combined text sequences
                (princ "\n  Combined Text Sequences:")
                (foreach ct combined_texts
                  (princ (strcat "\n    " ct))
                )

                ;; Initialize found flag
                (setq found nil)

                ;; Loop through each combined text sequence
                (foreach ct combined_texts
                  ;; Check if the combined_text is a substring of any code and has sufficient length
                  (foreach code codes
                    (if (and
                          (vl-string-search ct code) ; Check if ct is a substring of code
                          (> (strlen ct) 5)         ; Ensure sequence length is sufficient
                        )
                      (progn
                        ;; Insert block at circle center
                        (setq insPt circle_center)
                        (princ (strcat "\n  Insertion point: " (vl-princ-to-string insPt)))

                        ;; Insert block
                        (setq blkRef (vla-InsertBlock
                                       (vla-get-ModelSpace (vla-get-ActiveDocument (vlax-get-acad-object)))
                                       (vlax-3D-point insPt)
                                       "EQ_BLOCK" ; Ensure this block exists or has been created
                                       1.0 1.0 1.0 0.0))

                        ;; Set attribute if block has attributes
                        (if blkRef
                          (progn
                            (vla-Update blkRef)
                            (setq attribs (vlax-invoke blkRef 'GetAttributes))
                            (foreach attrib attribs
                              (if (= (strcase (vla-get-TagString attrib)) "EQ_TAG")
                                (vla-put-TextString attrib code)
                              )
                            )
                          )
                          (princ "\n  Warning: Block reference could not be created.")
                        )

                        (princ (strcat "\n  Block inserted for: " code))
                        (setq found T)
                      )
                    )
                  )
                )

                ;; Notify if no matches were found for any permutation
                (if (not found)
                  (princ "\n  No match found for any text sequence permutations.")
                )
              )
              (princ "\n  No valid text found on the left side within the buffer distance for this circle.")
            )

            ;; Move to the next circle
            (setq i (1+ i))
          )
        )
      )
    )
    (princ "\nNo circles or texts found in the drawing.")
  )

  (princ "\nDone.")
  (princ)
)

;; Helper function to intersperse a separator between list elements
(defun intersperse (separator lst / acc)
  (if (null lst)
    nil
    (progn
      (setq acc (list (car lst))) ; Start with the first element
      (setq lst (cdr lst))        ; Remaining list
      (while lst
        (setq acc (cons separator acc)) ; Add separator
        (setq acc (cons (car lst) acc)) ; Add next element
        (setq lst (cdr lst))              ; Move to next
      )
      (reverse acc) ; Reverse to maintain original order
    )
  )
)

;; Helper function to generate all permutations of a list
(defun permutations (lst / result rest elem perms)
  (if (null lst)
    '(nil)
    (progn
      (setq result '())
      (foreach elem lst
        ;; Use vl-remove instead of remove
        (setq rest (vl-remove elem lst))
        (setq perms (permutations rest))
        (foreach p perms
          (setq result (cons (cons elem p) result))
        )
      )
      result
    )
  )
)

;; Function to create the EQ_BLOCK automatically
(defun CreateBlock (insertionPoint blkname clayerb clayer1 styname htx wdy radius)
  (if (tblsearch "block" blkname)
    (princ (strcat "\nBlock \"" blkname "\" already exists."))
    (progn
      ;; Create BLOCK definition
      (entmake 
        (list 
          '(0 . "BLOCK") 
          (cons 2 blkname)          ; Block name
          '(70 . 2)                 ; Block flags
          (cons 8 clayerb)          ; Layer for block
          (cons 10 insertionPoint)  ; Insertion point
          '(4 . "EQ_BLOCK Definition") ; Block comment
        )
      )
      ;; Create CIRCLE within the block
      (entmake 
        (list 
          '(0 . "CIRCLE")
          (cons 8 clayerb)          ; Layer for circle
          (cons 10 insertionPoint)  ; Center point
          (cons 40 radius)          ; Radius of the circle
        )
      )
      ;; Create ATTDEF within the block
      (entmake 
        (list 
          '(0 . "ATTDEF") 
          (cons 8 clayer1)          ; Layer for attribute
          (cons 10 insertionPoint)  ; Insertion point
          '(70 . 1)                 ; Attribute flags (1 = Visible)
          '(3 . "NAME")             ; Prompt
          '(2 . "EQ_TAG")           ; Tag 
          '(1 . "+")                ; Default value
          (cons 40 htx)             ; Height
          (cons 41 wdy)             ; Width factor
          (cons 7 styname)          ; Text style
          (cons 11 insertionPoint)  ; Alignment point
          '(72 . 0)                 ; Text generation flags
        )
      )
      ;; End BLOCK definition
      (entmake '((0 . "ENDBLK")))
      (princ (strcat "\nBlock \"" blkname "\" created successfully."))
    )
  )
)