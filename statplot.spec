# PyInstaller-Spezifikation fuer StatPlot (Desktop-Huelle um web/static).
# Aufruf:  pyinstaller statplot.spec
import os
import sys

block_cipher = None

# Die komplette Web-Oberflaeche wird mitgepackt, inklusive der Beispieldaten
# (ohne den Ordner downloads/ und ohne .htaccess).
datas = []
for name in os.listdir(os.path.join("web", "static")):
    full = os.path.join("web", "static", name)
    if os.path.isfile(full) and name != ".htaccess":
        datas.append((full, "static"))
datas.append((os.path.join("web", "static", "beispiele"), os.path.join("static", "beispiele")))

_default_icon = "assets/icon.icns" if sys.platform == "darwin" else "assets/icon.ico"
APP_ICON = os.environ.get("STATPLOT_ICON") or (_default_icon if os.path.isfile(_default_icon) else None)

a = Analysis(
    ["desktop/statplot_desktop.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="StatPlot",
    debug=False,
    strip=False,
    upx=False,
    console=False,
    icon=APP_ICON,
)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="StatPlot")

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="StatPlot.app",
        icon=APP_ICON,
        bundle_identifier="de.gdg-stuttgart.statplot",
        info_plist={
            "CFBundleName": "StatPlot",
            "CFBundleDisplayName": "StatPlot",
            "CFBundleShortVersionString": "1.0.0",
            "NSHighResolutionCapable": True,
        },
    )
