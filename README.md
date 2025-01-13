# TrueTag - BricsCAD Plugin

TrueTag is a BricsCAD plugin that automates drawing tasks through a convenient ribbon interface. It provides easy access to various AutoLISP scripts for PID, TML, and Position drawings.

## Features

- Integrated ribbon interface in BricsCAD
- Support for multiple drawing types (PID, TML, Position)
- CSV file integration for automated drawing
- Easy script selection through dialog interface
- Organized script management

## Installation

1. Copy the entire TrueTag folder to BricsCAD's application plugins directory:
   ```
   C:\Program Files\Bricsys\BricsCAD\Vxx\en_US\Applications\TrueTag
   ```

2. Start BricsCAD. The TrueTag tab should appear in the ribbon interface.

## Directory Structure

```
TrueTag/
├── Application/
│   ├── resources/
│   │   ├── logo.ico
│   │   ├── logo.png
│   │   └── script_selector.dcl
│   ├── utils/
│   │   └── script_utils.lsp
│   ├── TrueTag.py
│   ├── config.py
│   └── TrueTag.brx
├── Scripts/
│   ├── PID/
│   ├── TML/
│   └── Position/
└── README.md
```

## Usage

1. Click the TrueTag tab in BricsCAD's ribbon interface
2. Select the drawing type (PID, TML, or Position)
3. Choose a script from the dialog
4. If needed, select a CSV file using the CSV button
5. The script will run with the selected options

## Adding New Scripts

To add new scripts:
1. Place the .lsp file in the appropriate category folder under `Scripts/`
2. The script will automatically appear in the selection dialog
3. Ensure the script follows the naming convention: `c:functionname`

## Requirements

- BricsCAD V21 or later
- Windows 64-bit

## Support

For support or bug reports, please contact the TrueTag team. 