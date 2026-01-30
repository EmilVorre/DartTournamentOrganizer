# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

# Prepare data files - include dartboard.png if it exists
datas = []
if os.path.exists('dartboard.png'):
    datas.append(('dartboard.png', '.'))

a = Analysis(
    ['DartTournament.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
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

# For Mac .app bundles, use onedir mode (not onefile)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,  # This enables onedir mode
    name='DartTournament',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to False for GUI app (no console window)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DartTournament',
)

# Only create .app bundle on macOS
import sys
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='DartTournament.app',
        icon='Icons/icon.ico',  # Note: Mac prefers .icns format, but .ico might work
        bundle_identifier='com.darttournament.app',
        version='1.0.0',
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSHighResolutionCapable': 'True',
        },
    )
