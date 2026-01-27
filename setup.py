"""
setup.py for py2app
Packages APKM Repackager as a macOS application
"""

from setuptools import setup

APP = ['main.py']
DATA_FILES = [
    ('configs', ['configs/default.json', 'configs/xiaomi-tv.json']),
]

OPTIONS = {
    'argv_emulation': True,
    'packages': ['PyQt6', 'pyaxmlparser'],
    'includes': ['lib', 'ui'],
    'iconfile': None,  # Add your .icns file here if you have one
    'plist': {
        'CFBundleName': 'APKM Repackager',
        'CFBundleDisplayName': 'APKM Repackager',
        'CFBundleIdentifier': 'com.apkmrepackager.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': '© 2026 APKM Repackager Project',
        'LSMinimumSystemVersion': '10.14.0',
    }
}

setup(
    name='APKM Repackager',
    version='1.0.0',
    description='Convert APKM files to APK files for Android TV',
    author='APKM Repackager Project',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
