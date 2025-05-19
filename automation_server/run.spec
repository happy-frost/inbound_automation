# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all
datas_selenium_stealth, binaries_selenium_stealth, hiddenimports_selenium_stealth = collect_all('selenium_stealth')
datas_pandas, binaries_pandas, hiddenimports_pandas = collect_all('pandas')

a = Analysis(
    ['run.py'],
    pathex=[
        '.',                         # your current directory
        '../whatsapp_automation',   # add external package here
    ],
    binaries= binaries_selenium_stealth + binaries_pandas,
    datas= datas_selenium_stealth + datas_pandas + [
        ('app/models','app/models'),
        ('app/static','app/static'),
        ('app/templates','app/templates'),
        ('app/utils','app/utils'),
        ('app','app'),
    ],
    hiddenimports= hiddenimports_selenium_stealth + hiddenimports_pandas,
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
    [],
    exclude_binaries=True,
    name='run',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='run',
)
