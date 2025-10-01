# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['TrueTag-ver4.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('logo.ico', '.'),
        ('config.json', '.'),
        ('runtime_settings.json', '.'),
        ('usage_reporting.py', '.'),
        ('config_manager.py', '.'),
        ('Scripts', 'Scripts'),
    ],
    hiddenimports=[
        'win32com.client',
        'ttkbootstrap',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'json',
        'os',
        'sys',
        'datetime',
        'time',
        'smtplib',
        'email.mime.text',
        'email.mime.multipart',
        'email.mime.base',
        'csv',
        'glob',
        'shutil'
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
    name='TRUETAG-v4',
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
    icon='logo.ico',
    version='version_info.txt'
)
