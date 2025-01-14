(defun c:ModifyCUI ()
  ;; Get the current MENUNAME system variable
  (setq menu-name (getvar "MENUNAME"))

  ;; Check if MENUNAME is a full path or just a file name
  (if (vl-string-search "\\" menu-name)
    (setq cui-path menu-name) ; Full path is already provided
    ;; Otherwise, construct the full path
    (setq cui-path (strcat (getenv "APPDATA") "\\Bricsys\\BricsCAD\\V24x64\\en_US\\Support\\" menu-name))
  )

  ;; Ensure the file has the correct extension
  (if (not (vl-string-search ".cui" cui-path))
    (setq cui-path (strcat cui-path ".cui"))
  )

  ;; Extract just the file name for CUIUNLOAD
  (setq cui-file-name (vl-filename-base cui-path))

  ;; Debug: Print the constructed CUI path
  (princ (strcat "\nConstructed CUI Path: " cui-path))

  ;; Check if the CUI file exists and proceed
  (if (and cui-path (findfile cui-path))
    (progn
      ;; Create a backup of the CUI file
      (setq backup-path (strcat cui-path "_backup"))
      (vl-file-copy cui-path backup-path)
      (princ (strcat "\nBackup created at: " backup-path))
      
      ;; Load the XML document
      (setq xml (vlax-create-object "Microsoft.XMLDOM"))
      (if (vlax-invoke-method xml 'load cui-path)
        (progn
          ;; Get the document element
          (setq document (vlax-get-property xml 'documentElement))

          ;; Find or create MenuGroup node for BRICSCAD
          (setq menu-group (vlax-invoke-method document 'selectSingleNode "MenuGroup[@name='BRICSCAD']"))
          (if (null menu-group)
            (progn
              (setq menu-group (vlax-invoke-method xml 'createElement "MenuGroup"))
              (vlax-invoke-method menu-group 'setAttribute "name" "BRICSCAD")
              (vlax-invoke-method document 'appendChild menu-group)
            )
          )
          
          ;; Create MenuMacros section if it doesn't exist
          (setq menu-macros (vlax-invoke-method menu-group 'selectSingleNode "MenuMacros"))
          (if (null menu-macros)
            (progn
              (setq menu-macros (vlax-invoke-method xml 'createElement "MenuMacros"))
              (vlax-invoke-method menu-group 'appendChild menu-macros)
            )
          )

          ;; Add truetag macro if it doesn't exist
          (setq existing-macro (vlax-invoke-method menu-macros 'selectSingleNode "MenuMacro[@name='truetag']"))
          (if (null existing-macro)
            (progn
              (setq macro (vlax-invoke-method xml 'createElement "MenuMacro"))
              (vlax-invoke-method macro 'setAttribute "name" "truetag")
              (vlax-invoke-method macro 'setAttribute "text" "True Tag")
              
              ;; Add macro content
              (setq macro-content (vlax-invoke-method xml 'createElement "Macro"))
              (vlax-invoke-method macro-content 'setAttribute "text" "^C^C_truetag")
              (vlax-invoke-method macro 'appendChild macro-content)
              
              ;; Add to MenuMacros
              (vlax-invoke-method menu-macros 'appendChild macro)
            )
          )
          
          ;; Find RibbonTabSourceCollection
          (setq tab-collection (vlax-invoke-method document 'selectSingleNode "RibbonTabSourceCollection"))
          (if (null tab-collection)
            (progn
              (setq tab-collection (vlax-invoke-method xml 'createElement "RibbonTabSourceCollection"))
              (vlax-invoke-method document 'appendChild tab-collection)
            )
          )

          ;; Create Truetag tab if it doesn't exist
          (setq tab-id "rtTruetag")
          (setq existing-tab (vlax-invoke-method tab-collection 'selectSingleNode (strcat "RibbonTabSource[@UID='" tab-id "']")))
          (if (null existing-tab)
            (progn
              ;; Create the RibbonTabSource
              (setq tab-source (vlax-invoke-method xml 'createElement "RibbonTabSource"))
              (vlax-invoke-method tab-source 'setAttribute "UID" tab-id)
              (vlax-invoke-method tab-source 'setAttribute "Text" "Truetag")
              
              ;; Add name node
              (setq name-node (vlax-invoke-method xml 'createElement "Name"))
              (setq text-node (vlax-invoke-method xml 'createTextNode "Truetag"))
              (vlax-invoke-method name-node 'appendChild text-node)
              (vlax-invoke-method tab-source 'appendChild name-node)
              
              ;; Create a panel for commands
              (setq panel-source (vlax-invoke-method xml 'createElement "RibbonPanelSource"))
              (vlax-invoke-method panel-source 'setAttribute "Text" "Commands")
              
              ;; Add a row to the panel
              (setq ribbon-row (vlax-invoke-method xml 'createElement "RibbonRow"))
              
              ;; Add command buttons
              (setq cmd-button1 (vlax-invoke-method xml 'createElement "RibbonCommandButton"))
              (vlax-invoke-method cmd-button1 'setAttribute "MenuMacroID" "truetag")
              (vlax-invoke-method cmd-button1 'setAttribute "Text" "True Tag")
              (vlax-invoke-method cmd-button1 'setAttribute "ButtonStyle" "LargeWithText")
              
              ;; Assemble the structure
              (vlax-invoke-method ribbon-row 'appendChild cmd-button1)
              (vlax-invoke-method panel-source 'appendChild ribbon-row)
              (vlax-invoke-method tab-source 'appendChild panel-source)
              
              ;; Add the tab to the collection
              (vlax-invoke-method tab-collection 'appendChild tab-source)
            )
          )

          ;; Find all workspaces
          (setq workspaces (vlax-invoke-method document 'selectNodes "//Workspace"))
          (if workspaces
            (progn
              ;; Iterate through each workspace
              (setq i 0)
              (while (< i (vlax-get-property workspaces 'length))
                (setq workspace (vlax-invoke-method workspaces 'item i))
                
                ;; Find or create RibbonRoot in workspace
                (setq ws-ribbon-root (vlax-invoke-method workspace 'selectSingleNode "WSRibbonRoot"))
                (if (null ws-ribbon-root)
                  (progn
                    (setq ws-ribbon-root (vlax-invoke-method xml 'createElement "WSRibbonRoot"))
                    (vlax-invoke-method workspace 'appendChild ws-ribbon-root)
                  )
                )
                
                ;; Add tab reference if it doesn't exist
                (setq tab-ref-xpath (strcat "WSRibbonTabSourceReference[@TabId='" tab-id "']"))
                (setq existing-ref (vlax-invoke-method ws-ribbon-root 'selectSingleNode tab-ref-xpath))
                (if (null existing-ref)
                  (progn
                    (setq tab-ref (vlax-invoke-method xml 'createElement "WSRibbonTabSourceReference"))
                    (vlax-invoke-method tab-ref 'setAttribute "MenuGroup" "BRICSCAD")
                    (vlax-invoke-method tab-ref 'setAttribute "TabId" tab-id)
                    (vlax-invoke-method ws-ribbon-root 'appendChild tab-ref)
                  )
                )
                (setq i (1+ i))
              )
            )
          )

          ;; Save the modified XML
          (vlax-invoke-method xml 'save cui-path)
          (vlax-release-object xml)

          ;; Reload the modified CUI file
          (vla-sendcommand
            (vla-get-activedocument (vlax-get-acad-object))
            (strcat "_.CUIUNLOAD \"" cui-file-name "\"\n")
          )
          (vla-sendcommand
            (vla-get-activedocument (vlax-get-acad-object))
            (strcat "_.CUILOAD \"" cui-path "\"\n")
          )
          (princ "\nRibbon tab 'Truetag' added and CUI reloaded successfully.")
        )
        (princ "\nError: Failed to load the CUI file as XML.")
      )
    )
    (princ "\nError: CUI file not found or accessible.")
  )
  (princ)
)
