(defun c:EXTRACTPOINTS (csv_path / ent entdata ptlist csvfile f ptnum pt text1 text2 combined_text found match_lines selected_match proceed)
  (setvar "CMDECHO" 0)  ; Turn off command echo
  
  (princ "\nScript Started, press enter to continue: ")
  (getstring)
  
  ; Ask user for CSV file location to save points first
  (setq csvfile (getfiled "Save Points to CSV File" "" "csv" 1))
  (if (not csvfile)
    (progn
      (princ "\nNo save location selected. Exiting.")
      (exit)
    )
  )
  
  ; Get CSV file for comparison
  (if (not csv_path)
    (progn
      (setq csv_path (getfiled "Select CSV file for comparison" "" "csv" 0))
      (if (not csv_path)
        (progn
          (princ "\nNo CSV file selected. Exiting.")
          (exit)
        )
      )
    )
  )

  (while T  ; Infinite loop, will only exit when user explicitly chooses to
    ; Loop until valid text combination is found or user chooses to proceed
    (setq proceed nil)
    (while (not proceed)
      ; Get first text
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
              (setq text1 (vl-string-translate "-" "" (cdr (assoc 1 entdata))))
              (princ "\nSelected entity is not a text. Please select a text.")
            )
          )
        )
      )
      
      ; Get second text
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
              (setq text2 (vl-string-translate "-" "" (cdr (assoc 1 entdata))))
              (princ "\nSelected entity is not a text. Please select a text.")
            )
          )
        )
      )
      
      ; Create variations of combined text
      (setq combined_text (strcat "*" text1 "*" text2 "*"))
      (setq combined_text_lower (strcat "*" (strcase text1 T) "*" (strcase text2 T) "*"))
      (setq combined_text_reverse (strcat "*" text2 "*" text1 "*"))
      (setq combined_text_reverse_lower (strcat "*" (strcase text2 T) "*" (strcase text1 T) "*"))
      
      (princ (strcat "\nOriginal texts after removing hyphens:"
                     "\nText 1: " text1
                     "\nText 2: " text2
                     "\n\nChecking variations:"
                     "\n1. " text1 "-" text2
                     "\n2. " (strcase text1 T) "-" (strcase text2 T)
                     "\n3. " text2 "-" text1
                     "\n4. " (strcase text2 T) "-" (strcase text1 T)))
      
      ; Check if any variation exists as a substring in CSV
      (setq found nil)
      (setq match_lines (list))
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
            (setq proceed nil)  ; Continue loop to select new texts
            (setq proceed T)    ; Exit loop and continue with current texts
          )
        )
        (progn
          (princ "\nFound matching sequences in CSV:")
          (setq index 1)
          (foreach line match_lines
            (princ (strcat "\n" (itoa index) ". " line))
            (setq index (1+ index))
          )
          
          ; Let user choose which sequence to use
          (setq selected_index nil)
          (while (not selected_index)
            (setq input (getstring "\nEnter the number of the sequence to use (or press Enter to use the first one): "))
            (if (= input "")
              (setq selected_index 1)
              (progn
                (setq selected_index (atoi input))
                (if (or (< selected_index 1) (> selected_index (length match_lines)))
                  (progn
                    (princ "\nInvalid selection. Please try again.")
                    (setq selected_index nil)
                  )
                )
              )
            )
          )
          
          (setq match_line (nth (1- selected_index) match_lines))
          (princ (strcat "\nSelected sequence: " match_line))
          (setq proceed T)  ; Found a match, proceed to line selection
        )
      )
    )
    
    ; Only proceed to line selection after text selection is complete
    (if proceed
      (progn
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
                (setq ent ent)  ; Keep the entity
                (progn
                  (princ "\nSelected entity is not a line or polyline. Please select a line or polyline.")
                  (setq ent nil)  ; Reset ent to allow retry
                )
              )
            )
          )
        )
        
        (setq entdata (entget ent))
        (setq ptlist nil)
        
        (cond
          ; If entity is a LINE
          ((= (cdr (assoc 0 entdata)) "LINE")
           (setq ptlist (list
                         (cdr (assoc 10 entdata)) ; Start point
                         (cdr (assoc 11 entdata)) ; End point
                       ))
          )
          
          ; If entity is a POLYLINE or LWPOLYLINE
          ((or (= (cdr (assoc 0 entdata)) "POLYLINE")
               (= (cdr (assoc 0 entdata)) "LWPOLYLINE"))
           (setq ptlist nil)
           (if (= (cdr (assoc 0 entdata)) "LWPOLYLINE")
             ; For LWPOLYLINE
             (progn
               (setq ptlist (list))
               (while (setq entdata (member (assoc 10 entdata) entdata))
                 (setq ptlist (append ptlist (list (cdr (assoc 10 entdata)))))
                 (setq entdata (cdr entdata))
               )
             )
             ; For regular POLYLINE
             (progn
               (setq ent (entnext ent))
               (while (and ent
                          (/= "SEQEND" (cdr (assoc 0 (setq entdata (entget ent))))))
                 (if (= "VERTEX" (cdr (assoc 0 entdata)))
                   (setq ptlist (append ptlist (list (cdr (assoc 10 entdata)))))
                 )
                 (setq ent (entnext ent))
               )
             )
           )
          )
        )
        
        ; Mark points with a circle and save coordinates
        (if ptlist
          (progn
            ; Create or append to CSV file
            (if (findfile csvfile)  ; If file exists
              (setq f (open csvfile "a"))  ; Append mode
              (progn  ; If file doesn't exist
                (setq f (open csvfile "w"))
                (write-line "Pipeline Code,Number,Coordinate X,Coordinate Y" f)  ; Write header only for new file
              )
            )
            
            ; Write points to CSV and mark them in drawing
            (setq ptnum 1)
            (foreach pt ptlist
              (command "_circle" "_non" pt 0.1)
              ; Write point to CSV with new format
              (write-line (strcat match_line ","
                                 (itoa ptnum) ","
                                 (rtos (car pt) 2 4) ","
                                 (rtos (cadr pt) 2 4)
                        ) f)
              (setq ptnum (1+ ptnum))
            )
            
            ; Close CSV file
            (close f)
            (princ (strcat "\nPoints saved to: " csvfile))
            (princ (strcat "\nTotal points extracted: " (rtos (length ptlist) 2 0)))
          )
          (princ "\nNo points found in the selected entity.")
        )
      )
    )
  )
  
  (setvar "CMDECHO" 1)  ; Turn command echo back on
  (princ)
) 