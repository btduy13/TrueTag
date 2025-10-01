(defun c:EXTRACTPOINTS (csv_path / ent entdata ptlist csvfile f ptnum pt text1 text2 combined_text found match_lines selected_match proceed raw_text1 raw_text2 input match_line index selected_index combined_text_lower combined_text_reverse combined_text_reverse_lower)

  (defun clean-text (txt)
    (if txt
      (vl-string-subst "" "-" txt)
      ""
    )
  )

  (setvar "CMDECHO" 0)  ; Turn off command echo
  
  (princ "\nScript Started, press enter to continue: ")
  (setq input (getstring))
  
  ; Get CSV file path from user if not provided
  (if (not csv_path)
    (progn
      (princ "\nEnter CSV file path (or press Enter to use default): ")
      (setq input (getstring))
      (if (= input "")
        (setq csvfile "extracted_points.csv")
        (setq csvfile input)
      )
    )
    (setq csvfile csv_path)
  )

  (while T  ; Infinite loop, will only exit when user explicitly chooses to
    (setq proceed nil)
    (while (not proceed)
      ; Get first text and clean it
      (setq text1 nil)
      (while (not text1)
        (princ "\nSelect first text (or press Enter to exit): ")
        (setq ent (car (entsel)))
        (if (not ent)
          (progn
            (princ "\nNo text selected. Exiting.")
            (exit)
          )
          (progn
            (setq entdata (entget ent))
            (if (= (cdr (assoc 0 entdata)) "TEXT")
              (progn
                (setq raw_text1 (cdr (assoc 1 entdata)))
                (setq text1 (clean-text raw_text1))
              )
              (princ "\nSelected entity is not a text. Please select a text.")
            )
          )
        )
      )
      
      ; Get second text and clean it
      (setq text2 nil)
      (while (not text2)
        (princ "\nSelect second text (or press Enter to exit): ")
        (setq ent (car (entsel)))
        (if (not ent)
          (progn
            (princ "\nNo text selected. Exiting.")
            (exit)
          )
          (progn
            (setq entdata (entget ent))
            (if (= (cdr (assoc 0 entdata)) "TEXT")
              (progn
                (setq raw_text2 (cdr (assoc 1 entdata)))
                (setq text2 (clean-text raw_text2))
              )
              (princ "\nSelected entity is not a text. Please select a text.")
            )
          )
        )
      )
      
      ; Clean texts
      (setq text1_clean (strcase (clean-text text1)))
      (setq text2_clean (strcase (clean-text text2)))
      
      ; Debug output to verify hyphen removal
      (princ (strcat "\nOriginal texts after removing hyphens:"
                     "\nText 1: " text1_clean
                     "\nText 2: " text2_clean
                     "\n\nChecking variations:"
                     "\n1. " text1_clean "-" text2_clean
                     "\n2. " text1_clean "-" text2_clean
                     "\n3. " text2_clean "-" text1_clean
                     "\n4. " text2_clean "-" text1_clean))
      
      ; Create variations with cleaned text (all uppercase)
      (setq combined_text (strcat "*" text1_clean "*" text2_clean "*"))
      (setq combined_text_lower (strcat "*" text1_clean "*" text2_clean "*"))
      (setq combined_text_reverse (strcat "*" text2_clean "*" text1_clean "*"))
      (setq combined_text_reverse_lower (strcat "*" text2_clean "*" text1_clean "*"))
      
      ; Check if any variation exists as a substring in CSV
      (setq found nil match_lines '())
      (setq f (open csv_path "r"))
      (while (setq line (read-line f))
        (if (or (wcmatch line combined_text)
                (wcmatch line combined_text_lower)
                (wcmatch line combined_text_reverse)
                (wcmatch line combined_text_reverse_lower))
          (progn
            (setq found T)
            (setq match_lines (append match_lines (list line)))
          )
        )
      )
      (close f)
      
      (if (not found)
        (progn
          (princ "\nNone of the text variations were found in CSV file.")
          (if (not (getstring "\nPress Enter to select new texts or any key to continue anyway: "))
            (setq proceed nil)
            (setq proceed T)
          )
        )
        (progn
          (if (= (length match_lines) 1)
            (progn
              (princ (strcat "\nFound matching sequence: " (car match_lines)))
              (setq match_line (car match_lines))
              (setq proceed T)
            )
            (progn
              (princ "\nMultiple matching sequences found:")
              (setq index 1)
              (foreach line match_lines
                (princ (strcat "\n" (itoa index) ". " line))
                (setq index (1+ index))
              )
              (princ "\nEnter the number of the sequence to use: ")
              (setq selected_index (getint))
              (if (and (>= selected_index 1) (<= selected_index (length match_lines)))
                (progn
                  (setq match_line (nth (1- selected_index) match_lines))
                  (princ (strcat "\nSelected sequence: " match_line))
                  (setq proceed T)
                )
                (progn
                  (princ "\nInvalid selection. Please try again.")
                  (setq proceed nil)
                )
              )
            )
          )
        )
      )
    )
    
    ; Get line or polyline
    (setq ent nil)
    (while (not ent)
      (princ "\nSelect line or polyline (or press Enter to exit): ")
      (setq ent (car (entsel)))
      (if (not ent)
        (progn
          (princ "\nNo entity selected. Exiting.")
          (exit)
        )
        (progn
          (setq entdata (entget ent))
          (if (or (= (cdr (assoc 0 entdata)) "LINE")
                  (= (cdr (assoc 0 entdata)) "POLYLINE")
                  (= (cdr (assoc 0 entdata)) "LWPOLYLINE"))
            (setq ent ent)
            (progn
              (princ "\nSelected entity is not a line or polyline. Please select a line or polyline.")
              (setq ent nil)
            )
          )
        )
      )
    )
    
    (setq entdata (entget ent))
    (setq ptlist nil)
    
    (cond
      ((= (cdr (assoc 0 entdata)) "LINE")
       (setq ptlist (list (cdr (assoc 10 entdata)) (cdr (assoc 11 entdata))))
      )
      ((or (= (cdr (assoc 0 entdata)) "POLYLINE") (= (cdr (assoc 0 entdata)) "LWPOLYLINE"))
       (setq ptlist '())
       (if (= (cdr (assoc 0 entdata)) "LWPOLYLINE")
         (progn
           (while (setq entdata (member (assoc 10 entdata) entdata))
             (setq ptlist (append ptlist (list (cdr (assoc 10 entdata)))))
             (setq entdata (cdr entdata))
           )
         )
         (progn
           (setq ent (entnext ent))
           (while (and ent (/= "SEQEND" (cdr (assoc 0 (setq entdata (entget ent))))))
             (if (= "VERTEX" (cdr (assoc 0 entdata)))
               (setq ptlist (append ptlist (list (cdr (assoc 10 entdata)))))
             )
             (setq ent (entnext ent))
           )
         )
       )
      )
    )
    
    (if ptlist
      (progn
        (if (findfile csvfile)
          (setq f (open csvfile "a"))
          (progn
            (setq f (open csvfile "w"))
            (write-line "Pipeline Code,Number,Coordinate X,Coordinate Y" f)
          )
        )
        
        (setq ptnum 1)
        (foreach pt ptlist
          (command "_circle" "_non" pt 0.1)
          (write-line (strcat match_line "," (itoa ptnum) "," (rtos (car pt) 2 4) "," (rtos (cadr pt) 2 4)) f)
          (setq ptnum (1+ ptnum))
        )
        
        (close f)
        (princ (strcat "\nPoints saved to: " csvfile))
        (princ (strcat "\nTotal points extracted: " (rtos (length ptlist) 2 0)))
      )
      (princ "\nNo points found in the selected entity.")
    )
  )

  (setvar "CMDECHO" 1)
  (princ)
)
