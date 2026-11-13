# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

datas = [('assets', 'assets')]
datas += collect_data_files('docx')


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'numpy', 'PIL'],
    noarchive=False,
    optimize=0,
)
# On Windows 10/11 Qt uses the operating system ICU and universal CRT.
# SDK forwarders from a build environment can shadow those system libraries.
a.binaries = [entry for entry in a.binaries
              if not entry[0].lower().startswith(('icu', 'api-ms-win-', 'ext-ms-win-'))
              and entry[0].lower() != 'ucrtbase.dll']
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='MDtoDOCX',
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
    icon=['assets/document.ico'],
)
