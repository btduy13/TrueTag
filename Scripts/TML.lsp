
(defun cleanText (text)
  ;; Remove the formatting tags from the text
  (setq cleanedText (vl-string-right-trim "}" (vl-string-left-trim "{\\fTimes New Roman|b1|i0|c0|p18;" text)))
  cleanedText
)

(defun formatPlatform (platform)
  ;; Remove the hyphen from the platform name
  (setq platform (vl-string-subst "" "-" platform))
  platform
)

(defun formatRiser (riser)
  ;; Remove "No." and any leading/trailing spaces or periods, then format with leading zero if necessary
  (setq riser (vl-string-subst "" "No." riser))
  (setq riser (vl-string-subst "" "." riser))  ;; Remove any periods
  (setq riser (vl-string-subst "" " " riser))
  (setq riser (strcat "R" (if (< (strlen riser) 2) (strcat "0" riser) riser)))
  riser
)

(defun formatNumber (num)
  ;; Ensure the number is in 2-digit format
  (if (< (strlen num) 2)
    (setq num (strcat "0" num))
  )
  num
)

(defun createBlock (blkname clayerb clayer1 insertionPoint radius htx wdy styname)
  ;; Create a block with a circle and an attribute definition
  (entmake 
    (list 
      '(0 . "BLOCK") 
      (cons 2 blkname)           ; block name
      '(70 . 2) 
      (cons 8 clayerb)           ; layer
      (cons 10 insertionPoint)   ; insertion point
      '(4 . "SRVPNOC Value")     ; comment
    )
  )
  (entmake 
    (list 
      '(0 . "CIRCLE")
      (cons 8 clayerb)           ; layer
      (cons 10 insertionPoint)   ; insertion point
      (cons 40 0.05)             ; radius of the circle
    )
  )
  (entmake 
    (list 
      '(0 . "ATTDEF") 
      (cons 8 clayer1)           ; layer
      (cons 10 insertionPoint)   ; insertion point
      '(70 . 1)                  ; attribute flags (2 = invisible)
      '(3 . "NAME")              ; 3=Prompt
      '(2 . "EQ_TAG")            ; 2=Tag 
      '(1 . "+")                 ; 1=default value
      (cons 40 htx)              ; height
      (cons 41 wdy)              ; width
      (cons 7 styname)           ; text style
      (cons 11 insertionPoint)   ; match insertion point            
      '(72 . 0)                  ; 0=10 as insertion point
    )
  )
  (entmake '((0 . "ENDBLK")))   ; end of block with attdef
)

(defun c:TML()
  (setq blkname "EQ_BLOCK"       ; name of Block
        clayerb "-DRN"           ; defined block layer
        clayer1 "-DRNMARK"       ; attribute def layer
        clayeri "-DRN"           ; inserted block layer preferably same as defined block
        styname "STANDARD"       ; text style
        htx 0.1563               ; attribute def height
        wdy 0.8                  ; attribute def width
        radius 0.04              ; radius of the circle
        sclx 1                   ; block insert x scale factor
        scly 1                   ; block insert y scale factor
        sclz 1                   ; block insert z scale factor
  )
  (setq null (car (entsel "\n ")))
  (setq platformText (car (entsel "\nSelect Platform text: ")))
  (setq riserText (car (entsel "\nSelect Riser No. text: ")))

  (setq platformValue (formatPlatform (cleanText (cdr (assoc 1 (entget platformText))))))
  (setq riserValue (formatRiser (cleanText (cdr (assoc 1 (entget riserText))))))

  ;; Initialize finalText as empty
  (setq finalText "")

  ;; Select all TEXT and MTEXT objects in the drawing
  (setq texts (ssget "X" '((0 . "TEXT,MTEXT"))))

  ;; Check for specific phrases in the text objects
  (setq j 0)
  (while (< j (sslength texts))
    (setq text (ssname texts j))
    ;; Check if it's TEXT or MTEXT and get the text string accordingly
    (setq text_str 
      (cond 
        ((= (cdr (assoc 0 (entget text))) "TEXT")
         (cdr (assoc 1 (entget text))))
        ((= (cdr (assoc 0 (entget text))) "MTEXT")
         (cdr (assoc 1 (entget text))))
      )
    )

        ;; Check for "AT FIXED CONTROLLED POINTS" first
    (if (wcmatch (strcase text_str) "*FIXED CONTROLLED POINTS*")
      (setq finalText (strcat platformValue "-" riserValue "_FCP"))
    )
    ;; Only check for "THICKNESS MEASUREMENT" if "FIXED CONTROLLED POINTS" is not found
    (if (and (not (wcmatch finalText "*_FCP")) 
             (wcmatch (strcase text_str) "*THICKNESS MEASUREMENT*"))
      (setq finalText (strcat platformValue "-" riserValue "_TML"))
    )


    (setq j (1+ j))
  )

  ;; Select all circles in the drawing
  (setq circles (ssget "X" '((0 . "CIRCLE"))))

  ;; Check if circles are found
  (if circles
    (progn
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
          ;; Get the text's bounds (center point)
          (setq text_extents (vla-getboundingbox (vlax-ename->vla-object text) 'minPt 'maxPt))
          (setq text_center (mapcar '(lambda (a b) (/ (+ a b) 2.0)) (vlax-safearray->list minPt) (vlax-safearray->list maxPt)))

          ;; Check if the text's center is inside the circle
          (if (<= (distance circle_center text_center) radius)
            (progn
              ;; Get the text string
              (setq text_str 
                (cond 
                  ((= (cdr (assoc 0 (entget text))) "TEXT")
                   (cdr (assoc 1 (entget text))))
                  ((= (cdr (assoc 0 (entget text))) "MTEXT")
                   (cdr (assoc 1 (entget text))))
                )
              )
              ;; Add the text string to the list
              (setq text_list (cons text_str text_list))
            )
          )
          (setq j (1+ j))
        )

        ;; Combine the text strings (there should only be one number)
        (if (/= text_list nil)
          (progn
            (setq combined_text (formatNumber (car text_list))) ;; Format number as 2 digits

            ;; Print the combined text
            (princ (strcat "\nText inside the circle: " combined_text))

            ;; Insert block at circle center
            (setq insPt circle_center)
            (princ (strcat "\nInsertion point: " (vl-princ-to-string insPt)))

            ;; Create the block
            (createBlock blkname clayerb clayer1 insPt radius htx wdy styname)

            ;; Insert the block with attributes
            (setq blkRef (vla-InsertBlock (vla-get-modelspace (vla-get-activedocument (vlax-get-acad-object)))
                          (vlax-3d-point insPt) blkname sclx scly sclz 0.0))

            ;; Set attribute
            (vla-update blkRef)
            (setq attribs (vlax-invoke blkRef 'getattributes))
            (foreach attrib attribs
              (if (= (vla-get-tagstring attrib) "EQ_TAG")
                (vla-put-textstring attrib (strcat finalText combined_text))
              )
            )

            (princ (strcat "\nBlock inserted with attribute: " finalText combined_text))
          )
        )
        (setq i (1+ i))
      )
    )
    (princ "\nNo circles found in the drawing.")
  )

  ;; Determine save file name based on finalText
  (setq saveFileName 
    (cond
      ((wcmatch finalText "*_FCP") (strcat platformValue "-IA-FCP.dwg"))
      ((wcmatch finalText "*_TML") (strcat platformValue "-IA-WT.dwg"))
      (t (strcat platformValue "-IA-UNKNOWN.dwg"))
    )
  )

  ;; Open the "Save As" dialog box
  (setq saveFileName (getfiled "Save Drawing As" saveFileName "dwg" 1))
  (if saveFileName
    (command "_.SAVEAS" "" saveFileName)
  )

  (princ "\nDone.")
  (princ)
)

