(defun c:Instrument (csvPath / circles texts circle text circle_center radius text_point text_str combined_text reversed_text platformName final_combined_text final_reversed_text matches userChoice index choiceList selectedTag insPt blkRef attribs)
  (princ "\nStarting script...")

  ;; Prompt the user to enter the Platform name
  (setq nothing (strcase (getstring "\n Enter to continue ")))
  (setq platformName (strcase (getstring "\nEnter Platform name (e.g., BK14): ")))

  ;; Check if a valid CSV file path was passed
  (if (not (findfile csvPath))
    (princ "\nCSV file not found.")
    (progn
      ;; Select all circles in the drawing
      (setq circles (ssget "X" '((0 . "CIRCLE"))))

      ;; Select all text objects in the drawing
      (setq texts (ssget "X" '((0 . "TEXT,MTEXT"))))

      ;; Check if circles and texts are found
      (if (and circles texts)
        (progn
          ;; Load the CSV file
          (setq file (open csvPath "r"))
          (setq codes '())
          (read-line file) ; Skip the header line

          ;; Read CSV and store equipment codes
          (while (setq line (read-line file))
            (if (> (strlen line) 0)
              (setq codes (cons (strcase line) codes))
            )
          )
          (close file)
          (princ (strcat "\nCodes read: " (itoa (length codes))))

          ;; Loop through each circle
          (setq i 0)
          (while (< i (sslength circles))
            (setq circle (ssname circles i))
            ;; Get the circle's center and radius
            (setq circle_center (cdr (assoc 10 (entget circle))))
            (setq radius (cdr (assoc 40 (entget circle))))

            ;; Initialize text_list for each circle
            (setq text_list '())

            ;; Loop through each text object
            (setq j 0)
            (while (< j (sslength texts))
              (setq text (ssname texts j))
              ;; Get the text's insertion point
              (setq text_point (cdr (assoc 10 (entget text))))

              ;; Check if the text is inside the circle
              (if (<= (distance circle_center text_point) radius)
                (progn
                  ;; Get the text string
                  (setq text_str (strcase (cdr (assoc 1 (entget text)))))
                  ;; Add the text string to the list
                  (setq text_list (cons text_str text_list))
                )
              )
              (setq j (1+ j))
            )

            ;; Combine the text strings with a "-" between them
            (if text_list
              (progn
                ;; Combine texts in original order
                (setq combined_text (apply 'strcat (mapcar '(lambda (x) (strcat x "-")) (reverse text_list))))
                (setq combined_text (substr combined_text 1 (- (strlen combined_text) 1)))

                ;; Combine texts in reversed order
                (setq reversed_text (apply 'strcat (mapcar '(lambda (x) (strcat x "-")) text_list)))
                (setq reversed_text (substr reversed_text 1 (- (strlen reversed_text) 1)))

                ;; Prefix the Platform name to the combined texts
                (setq final_combined_text (strcat platformName "-" combined_text))
                (setq final_reversed_text (strcat platformName "-" reversed_text))

                ;; Print both combined texts
                (princ (strcat "\nCombined text inside the circle: " final_combined_text))
                (princ (strcat "\nReversed combined text inside the circle: " final_reversed_text))

                ;; Check if either the combined text or reversed text is a substring of any code
                (setq matches '())
                (foreach code codes
                  (if (and
                        (or (vl-string-search final_combined_text code) (vl-string-search final_reversed_text code))
                        (> (strlen final_combined_text) 5)  ;; New condition to check sequence length
                      )
                    (setq matches (cons code matches))
                  )
                )

                ;; Handle cases where multiple matches are found
                (cond
                  ((> (length matches) 1)
                   ;; Zoom to the circle center location
                   (command "._zoom" "C" circle_center 10) ; Adjust zoom factor for closer view
                   (princ "\nMultiple matches found. Please choose a tag, or enter 0 to skip:\n")

                   ;; Display choices to the user
                   (setq index 1 choiceList "")
                   (foreach match matches
                     (setq choiceList (strcat choiceList (itoa index) ". " match "\n"))
                     (setq index (1+ index))
                   )
                   (setq choiceList (strcat choiceList "0. None (skip)\n"))  ;; Add option to skip
                   (princ choiceList)
                   ;; Prompt user to select a tag or skip
                   (setq userChoice (atoi (getstring "\nEnter the number corresponding to the tag to use: ")))

                   ;; Validate and insert block or skip if userChoice is 0
                   (if (and (>= userChoice 1) (<= userChoice (length matches)))
                     (progn
                       (setq selectedTag (nth (1- userChoice) matches))
                       ;; Insert block at circle center
                       (setq insPt circle_center)
                       (princ (strcat "\nInsertion point: " (vl-princ-to-string insPt)))

                       ;; Insert block
                       (setq blkRef (vla-InsertBlock (vla-get-modelspace (vla-get-activedocument (vlax-get-acad-object)))
                                     (vlax-3d-point insPt) "EQ_BLOCK" 1.0 1.0 1.0 0.0))

                       ;; Set attribute
                       (vla-update blkRef)
                       (setq attribs (vlax-invoke blkRef 'getattributes))
                       (foreach attrib attribs
                         (if (= (vla-get-tagstring attrib) "EQ_TAG")
                           (vla-put-textstring attrib selectedTag)
                         )
                       )

                       (princ (strcat "\nBlock inserted for: " selectedTag))
                     )
                     (if (= userChoice 0)
                       (princ "\nNo block inserted as per user choice.")
                       (princ "\nInvalid choice. No block inserted.")
                     )
                   )
                  )
                  ((= (length matches) 1)
                   ;; Only one match found, proceed as usual
                   (setq selectedTag (car matches))
                   (setq insPt circle_center)
                   (princ (strcat "\nInsertion point: " (vl-princ-to-string insPt)))

                   ;; Insert block
                   (setq blkRef (vla-InsertBlock (vla-get-modelspace (vla-get-activedocument (vlax-get-acad-object)))
                                 (vlax-3d-point insPt) "EQ_BLOCK" 1.0 1.0 1.0 0.0))

                   ;; Set attribute
                   (vla-update blkRef)
                   (setq attribs (vlax-invoke blkRef 'getattributes))
                   (foreach attrib attribs
                     (if (= (vla-get-tagstring attrib) "EQ_TAG")
                       (vla-put-textstring attrib selectedTag)
                     )
                   )

                   (princ (strcat "\nBlock inserted for: " selectedTag))
                  )
                  (t
                   (princ (strcat "\nNo match found for: " final_combined_text " or " final_reversed_text))
                  )
                )
              )
            )
            (setq i (1+ i))
          )
        )
        (princ "\nNo circles or texts found in the drawing.")
      )
    )
  )

  (princ "\nDone.")
  (princ)
)
