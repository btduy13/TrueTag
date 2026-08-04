# -*- mode: python ; coding: utf-8 -*-

from version import APP_VERSION

a = Analysis(
    ['single_file_installer.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('TrueTag_Setup/TRUETAG-v4.1.2.exe', 'TrueTag_Setup'),
        ('TrueTag_Setup/install_plugin.ps1', 'TrueTag_Setup'),
        ('TrueTag_Setup/truetag_loader.lsp', 'TrueTag_Setup'),
        ('TrueTag_Setup/truetag_startup.lsp', 'TrueTag_Setup'),
        ('TrueTag_Setup/truetag_menu.mnu', 'TrueTag_Setup'),
        ('TrueTag_Setup/logo.ico', 'TrueTag_Setup'),
        ('TrueTag_Setup/README.md', 'TrueTag_Setup'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=f'TrueTag_v{APP_VERSION}_Setup',
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
    version='version_info.txt',
)
