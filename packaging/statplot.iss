; Inno Setup Skript für StatPlot (Windows-Installer)
; Erzeugt dist\StatPlot-Setup.exe
; Aufruf:  iscc packaging\statplot.iss   (nach dem PyInstaller-Build)
; Quelle ist der PyInstaller-Ausgabeordner build\windows\dist\StatPlot.

[Setup]
AppName=StatPlot
AppVersion=1.0.0
AppPublisher=GDG Stuttgart
DefaultDirName={autopf}\StatPlot
DefaultGroupName=StatPlot
DisableProgramGroupPage=yes
OutputDir=..\dist
OutputBaseFilename=StatPlot-Setup
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "de"; MessagesFile: "compiler:Languages\German.isl"

[Files]
; der komplette PyInstaller-Ausgabeordner
Source: "..\build\windows\dist\StatPlot\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\StatPlot"; Filename: "{app}\StatPlot.exe"
Name: "{autodesktop}\StatPlot"; Filename: "{app}\StatPlot.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Desktop-Verknüpfung erstellen"; GroupDescription: "Zusätzliche Symbole:"

[Run]
Filename: "{app}\StatPlot.exe"; Description: "StatPlot starten"; Flags: nowait postinstall skipifsilent
