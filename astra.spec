# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Coletar todos os arquivos de dados
datas = [
    ('jarvis/config', 'config'),
    ('jarvis/assets', 'assets'),
    ('jarvis/data', 'data'),
    ('jarvis/neural_models', 'neural_models'),
]

# Módulos hidden que PyInstaller pode não detectar
hiddenimports = [
    'PyQt6',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'PyQt6.QtWebEngineWidgets',
    'pyttsx3',
    'pyttsx3.drivers',
    'pyttsx3.drivers.sapi5',
    'speech_recognition',
    'comtypes',
    'numpy',
    'sklearn',
    'joblib',
    'requests',
    'nltk',
    'PIL',
    'modules.audio.audio_manager',
    'modules.speech.speech_engine',
    'modules.speech.hotword_detector',
    'modules.personality_engine',
    'modules.memory_system',
    'modules.companion_engine',
    'api.api_integration_hub',
]

# Análise do executável principal
a = Analysis(
    ['jarvis/main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'pandas',
        'scipy',
        'jupyter',
        'IPython',
        'pytest',
        'sphinx',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Jarvis',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Sem console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='jarvis/assets/icon.ico' if os.path.exists('jarvis/assets/icon.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Jarvis',
)
