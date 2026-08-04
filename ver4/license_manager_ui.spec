# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for License Manager UI

from version import APP_VERSION

block_cipher = None

a = Analysis(
    ['license_manager_ui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('logo.ico', '.'),  # Icon file
        # Config files (optional - will be created if not exist)
        # ('license_config.json', '.'),
        # ('server_config.json', '.'),
    ],
    hiddenimports=[
        'license_generator',
        'license_server',
        'ttkbootstrap',
        'ttkbootstrap.constants',
        'ttkbootstrap.tooltip',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'tkinter.simpledialog',
        'tkinter.constants',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'json',
        'os',
        'sys',
        'datetime',
        'hashlib',
        'random',
        'string',
        'uuid',
        'base64',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=f'LicenseManager-v{APP_VERSION}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windowed application (no console)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='logo.ico',  # Application icon
    version='version_info.txt',
)

