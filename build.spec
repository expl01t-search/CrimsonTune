# -*- mode: python ; coding: utf-8 -*-

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(SPEC).parent
sys.path.insert(0, str(ROOT))
subprocess.run([sys.executable, str(ROOT / "tools" / "gen_version_info.py")], check=True)

os.environ.setdefault("PYTHONOPTIMIZE", "1")

from tools.pyi_excludes import all_excludes, filter_binaries, filter_datas

a = Analysis(
    ['main.py'],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('locales', 'locales'),
        ('ui/assets', 'ui/assets'),
        ('icon.ico', '.'),
    ],
    hiddenimports=[
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
        'tweaks.backlog',
        'tweaks.backlog_catalog',
        'core.updater',
        'core.update_installer',
        'http.client',
        'email.parser',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=all_excludes(),
    noarchive=False,
    optimize=1,
)

a.binaries = filter_binaries(a.binaries)
a.datas = filter_datas(a.datas)

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
