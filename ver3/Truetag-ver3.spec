# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['Truetag-ver3.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\\\Users\\\\PC\\\\Desktop\\\\Auto App\\\\Tổng hợp\\\\PID', 'Tổng hợp\\\\PID'), ('C:\\\\Users\\\\PC\\\\Desktop\\\\Auto App\\\\Tổng hợp\\\\TML', 'Tổng hợp\\\\TML'), ('C:\\\\Users\\\\PC\\\\Desktop\\\\Auto App\\\\Tổng hợp\\\\Position', 'Tổng hợp\\\\Position'), ('logo.ico', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Truetag-ver3',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['logo.ico'],
)
