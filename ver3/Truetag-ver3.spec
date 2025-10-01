# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['TrueTag-ver3.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('E:\\OneDrive\\Desktop\\Truetag\\Scripts\\PID', 'PID'),
        ('E:\\OneDrive\\Desktop\\Truetag\\Scripts\\TML', 'TML'),
        ('E:\\OneDrive\\Desktop\\Truetag\\Scripts\\Position', 'Position'),
        ('logo.ico', '.')
    ],
    hiddenimports=[
        'win32com.client',
        'win32com.client.gencache',
        'win32com.client.dynamic',
        'win32com.shell.shell',
        'win32com.shell',
        'win32wnet',
        'win32api',
        'win32con'
    ],
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
