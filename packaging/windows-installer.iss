; packaging/windows-installer.iss
[Setup]
AppName=Xtend
AppVersion={#VERSION}
AppPublisher=Venkata_Ramana_Pulugari
AppPublisherURL=https://itsmepvr.is-a.dev
AppSupportURL=https://support.xtend.example.com
AppUpdatesURL=https://updates.xtend.example.com
DefaultDirName={autopf}\Xtend
DefaultGroupName=Xtend
UninstallDisplayIcon={app}\xtend.exe
Compression=lzma2
SolidCompression=yes
OutputDir=dist
OutputBaseFilename=Xtend-Setup-{#VERSION}
SignTool=mysigntool

[Files]
Source: "dist\xtend.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "src\xtend\static\*"; DestDir: "{app}\static"; Flags: ignoreversion recursesubdirs
Source: "src\xtend\templates\*"; DestDir: "{app}\templates"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\Xtend"; Filename: "{app}\xtend.exe"
Name: "{commondesktop}\Xtend"; Filename: "{app}\xtend.exe"

[Run]
Filename: "{app}\xtend.exe"; Description: "Launch Xtend"; Flags: nowait postinstall