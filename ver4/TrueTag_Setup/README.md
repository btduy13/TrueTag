# TrueTag v4 - BricsCAD Plugin Installation

## Quick Start

### For Windows Users:
**Double-click `INSTALL.bat`** and follow the prompts.

### For Advanced Users:
Right-click `install_plugin.ps1` → Run with PowerShell

---

## What This Installer Does

1. **Copies TrueTag files** to `%APPDATA%\TrueTag` (or your chosen location)
2. **Detects BricsCAD installations** automatically
3. **Integrates with BricsCAD** by updating `on_doc_load.lsp`
4. **Loads TrueTag Menu automatically** via `truetag_menu.mnu`

---

## After Installation

1. **Open or restart BricsCAD**
2. Look for **"TrueTag v4"** in the menu bar (top of window)
3. Or type `TRUETAG` or `TT` in the command line

---

## Available Commands

| Command | Description |
|---------|-------------|
| `TRUETAG` | Launch TrueTag v4 |
| `TT` | Quick launch (shortcut) |
| `TRUETAG_PID` | Launch with PID scripts |
| `TRUETAG_TML` | Launch with TML scripts |
| `TRUETAG_POS` | Launch with Position scripts |
| `TRUETAG_HELP` | Show help |
| `TRUETAG_LICENSE` | Show license info |

---

## Troubleshooting

### Menu doesn't appear in BricsCAD

**Option 1:** Manually load the plugin:
```
Command: (load "C:/Users/YourName/AppData/Roaming/TrueTag/truetag_loader.lsp")
```

**Option 2:** Check MenuBar is visible:
```
Command: MENUBAR
New value: 1
```

**Option 3:** Manually load the menu file:
```
Command: MENULOAD
Select: %APPDATA%/TrueTag/truetag_menu.mnu
```

### BricsCAD not detected during installation

Manually specify the Support folder when prompted, typically:
```
C:\Users\YourName\AppData\Roaming\Bricsys\BricsCAD\V24x64\en_US\Support
```

---

## Uninstallation

1. Delete the TrueTag installation folder (default: `%APPDATA%\TrueTag`)
2. Remove the TrueTag line from BricsCAD's `on_doc_load.lsp`:
   - Location: `%APPDATA%\Bricsys\BricsCAD\V**x64\en_US\Support\on_doc_load.lsp`
   - Remove line: `(load "path/to/truetag_loader.lsp")`
3. Unload menu: `(command "_MENUNLOAD" "TRUETAG")`

---

**TrueTag v4 © 2025**
