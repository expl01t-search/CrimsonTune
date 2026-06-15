# -*- mode: python ; coding: utf-8 -*-

import subprocess
import sys
from pathlib import Path

ROOT = Path(SPEC).parent
subprocess.run([sys.executable, str(ROOT / "tools" / "gen_version_info.py")], check=True)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('locales', 'locales'),
        ('ui/assets', 'ui/assets'),
        ('icon.ico', '.'),
    ],
    hiddenimports=[
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'tweaks.performance',
        'tweaks.gaming',
        'tweaks.nvidia',
        'tweaks.amd',
        'tweaks.directx',
        'tweaks.opengl',
        'tweaks.network',
        'tweaks.privacy',
        'tweaks.visual',
        'tweaks.system',
        'tweaks.expert',
        'tweaks.exploit_extras',
        'tweaks.extended',
        'tweaks.optimize_pack',
        'tweaks.opensource',
        'tweaks.msi_mode',
        'tweaks.community',
        'tweaks.ssd',
        'tweaks.supplemental_catalog',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['customtkinter', 'tkinter'],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CrimsonTune',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    icon='icon.ico',
    version=str(ROOT / 'version_info.txt'),
)
