(defun point-inside-circle (center radius point)
  (<= (distance center point) radius)
)

(defun point-inside-ellipse (center major minor point)
  ;; Calculate relative coordinates
  (setq x (- (car point) (car center)))
  (setq y (- (cadr point) (cadr center)))
  
  ;; Calculate semi-major and semi-minor axes
  (setq a (/ major 2.0))  ; Semi-major axis length
  (setq b (/ minor 2.0))  ; Semi-minor axis length
  
  ;; Standard ellipse equation
  (<= (+ (/ (* x x) (* a a)) (/ (* y y) (* b b))) 1.0)
)

(defun c:Instrument-v2 (csvPath)
  (princ "\nStarting script...")
  
  ;; Prompt the user to press Enter to continue
  (getstring "\nPress Enter to continue ")
  
  ;; Prompt the user to enter the Platform name
  (setq platformName (strcase (getstring "\nEnter Platform name (e.g., BK14): ")))
  
  ;; Prompt the user to select the CSV file
  (setq csvPath (getfiled "Select CSV File" "" "csv" 0))
  
  ;; Check if a valid CSV file path was selected
  (if (not csvPath)
    (princ "\nNo CSV file selected. Script terminated.")
    (progn
      ;; Verify the CSV file exists
      (if (not (findfile csvPath))
        (princ "\nCSV file not found.")
        (progn
          ;; Select all circles and ellipses in the drawing
          (setq shapes (ssget "X" '((0 . "CIRCLE,ELLIPSE"))))
          
          ;; Select all text objects in the drawing
          (setq texts (ssget "X" '((0 . "TEXT,MTEXT"))))
          
          ;; Check if shapes and texts are found
          (if (and shapes texts)
            (progn
              ;; Load the CSV file
              (setq file (open csvPath "r"))
              (setq codes '())
              (read-line file) ; Skip the header line
              
              ;; Read CSV and store equipment codes
              (while (setq line (read-line file))
                (if (> (strlen line) 0)
                  (progn
                    ;; Assuming codes are in the first column separated by commas
                    (setq code (car (vl-string-split "," line)))
                    (setq codes (cons (strcase code) codes))
                  )
                )
              )
              (close file)
              (princ (strcat "\nCodes read: " (itoa (length codes))))
              
              ;; Store initial counts to prevent infinite loops
              (setq numShapes (sslength shapes))
              (setq numTexts (sslength texts))
              
              ;; Loop through each shape (circle or ellipse)
              (setq i 0)
              (while (< i numShapes)
                (setq shape (ssname shapes i)
                      shapeData (entget shape)
                      shapeType (cdr (assoc 0 shapeData))
                )
                
                ;; Initialize variables based on shape type
                (if (equal shapeType "CIRCLE")
                  (progn
                    (setq shapeCenter (cdr (assoc 10 shapeData)))
                    (setq shapeRadius (cdr (assoc 40 shapeData)))
                  )
                  (if (equal shapeType "ELLIPSE")
                    (progn
                      (setq shapeCenter (cdr (assoc 10 shapeData)))
                      (setq majorAxis (cdr (assoc 11 shapeData))) ; Endpoint of major axis
                      (setq minorRatio (cdr (assoc 40 shapeData))) ; Ratio (b/a)
                      
                      ;; Calculate major and minor axis lengths
                      (setq majorLength (distance shapeCenter majorAxis))
                      ;; Assuming the ellipse is axis-aligned; if rotated, more complex calculation is needed
                      (setq minorLength (* majorLength minorRatio)) ; b = a * (b/a)
                    )
                  )
                )
                
                ;; Initialize text_list for each shape
                (setq text_list '())
                
                ;; Loop through each text object
                (setq j 0)
                (while (< j numTexts)
                  (setq text (ssname texts j)
                        textData (entget text)
                        textPoint (cdr (assoc 10 textData))
                  )
                  
                  ;; Check if the text is inside the shape
                  (if (equal shapeType "CIRCLE")
                    (if (point-inside-circle shapeCenter shapeRadius textPoint)
                      (progn
                        ;; Get the text string
                        (setq text_str (strcase (cdr (assoc 1 textData))))
                        ;; Add the text string to the list
                        (setq text_list (cons text_str text_list))
                      )
                    )
                    (if (equal shapeType "ELLIPSE")
                      (if (point-inside-ellipse shapeCenter majorLength minorLength textPoint)
                        (progn
                          ;; Get the text string
                          (setq text_str (strcase (cdr (assoc 1 textData))))
                          ;; Add the text string to the list
                          (setq text_list (cons text_str text_list))
                        )
                      )
                    )
                  )
                  (setq j (1+ j))
                )
                
                ;; Combine the text strings with a "-" between them
                (if text_list
                  (progn
                    ;; Initialize combined_text and reversed_text
                    (setq combined_text "")
                    (setq reversed_text "")
                    
                    ;; Combine texts in original order (reversed list)
                    (foreach x (reverse text_list)
                      (setq combined_text (strcat combined_text x "-"))
                    )
                    ;; Remove trailing "-"
                    (if (> (strlen combined_text) 0)
                      (setq combined_text (substr combined_text 1 (- (strlen combined_text) 1)))
                      (setq combined_text "")
                    )
                    
                    ;; Combine texts in reversed order
                    (foreach x text_list
                      (setq reversed_text (strcat reversed_text x "-"))
                    )
                    ;; Remove trailing "-"
                    (if (> (strlen reversed_text) 0)
                      (setq reversed_text (substr reversed_text 1 (- (strlen reversed_text) 1)))
                      (setq reversed_text "")
                    )
                    
                    ;; Prefix the Platform name to the combined texts
                    (setq final_combined_text (strcat platformName "-" combined_text))
                    (setq final_reversed_text (strcat platformName "-" reversed_text))
                    
                    ;; Print both combined texts
                    (princ (strcat "\nCombined text inside the shape: " final_combined_text))
                    (princ (strcat "\nReversed combined text inside the shape: " final_reversed_text))
                    
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
                        ;; Zoom to the shape center location
                        (command "._zoom" "C" shapeCenter 10) ; Adjust zoom factor for closer view
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
                            ;; Insert block at shape center
                            (setq insPt shapeCenter)
                            (princ (strcat "\nInsertion point: " (vl-princ-to-string insPt)))
                            
                            ;; Insert block
                            (setq blkRef (vla-InsertBlock
                                            (vla-get-ModelSpace (vla-get-ActiveDocument (vlax-get-acad-object)))
                                            (vlax-3D-Point insPt) "EQ_BLOCK" 1.0 1.0 1.0 0.0))
                            
                            ;; Set attribute
                            (vla-update blkRef)
                            (setq attribs (vlax-invoke blkRef 'GetAttributes))
                            (foreach attrib attribs
                              (if (= (strcase (vla-get-TagString attrib)) "EQ_TAG")
                                (vla-put-TextString attrib selectedTag)
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
                        (setq insPt shapeCenter)
                        (princ (strcat "\nInsertion point: " (vl-princ-to-string insPt)))
                        
                        ;; Insert block
                        (setq blkRef (vla-InsertBlock
                                        (vla-get-ModelSpace (vla-get-ActiveDocument (vlax-get-acad-object)))
                                        (vlax-3D-Point insPt) "EQ_BLOCK" 1.0 1.0 1.0 0.0))
                        
                        ;; Set attribute
                        (vla-update blkRef)
                        (setq attribs (vlax-invoke blkRef 'GetAttributes))
                        (foreach attrib attribs
                          (if (= (strcase (vla-get-TagString attrib)) "EQ_TAG")
                            (vla-put-TextString attrib selectedTag)
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
            (princ "\nNo circles or ellipses, or texts found in the drawing.")
          )
        )
      )
    )
    
    (princ "\nDone.")
    (princ)
)
