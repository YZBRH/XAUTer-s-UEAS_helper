# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py', 'encode.py', 'select_curriculum.py'],
    pathex=[],
    binaries=[],
    datas=[('./onnxruntime_providers_shared.dll','onnxruntime\capi'),('./common_old.onnx','ddddocr')],
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
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['logo.ico'],
)
