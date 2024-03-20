# -*- mode: python ; coding: utf-8 -*-

conda_site_packages_path = os.path.abspath(r"C:\Users\86156\.conda\envs\tmp\Lib\site-packages")


a = Analysis(
    ['main.py', 'encode.py', 'send_msg.py', 'select_curriculum.py'],
    datas=[('./onnxruntime_providers_shared.dll','onnxruntime\\capi'),('./common.onnx','ddddocr'),('./common_old.onnx','ddddocr')],
    # pathex=[os.curdir, conda_site_packages_path],
    pathex=[],
    binaries=[],
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
    icon='helper-like.ico'
)
