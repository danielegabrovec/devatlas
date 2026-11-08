#ifndef AppVersion
  #define AppVersion "1.3.0"
#endif
#ifndef PayloadDir
  #define PayloadDir SourcePath + "..\dist\DevAtlas-" + AppVersion
#endif
#ifndef AppIdentifier
  #define AppIdentifier "{{5F450BB7-6CE0-4CDF-84C5-52A2911D91A3}"
#endif

[Setup]
AppId={#AppIdentifier}
AppName=DevAtlas — Atlante del Codice
AppVersion={#AppVersion}
AppPublisher=DevAtlas
DefaultDirName={localappdata}\Programs\DevAtlas
DefaultGroupName=DevAtlas
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0.17763
OutputDir=..\dist
OutputBaseFilename=DevAtlas-{#AppVersion}-Windows-x64-Setup
SetupIconFile=..\devatlas\assets\devatlas.ico
UninstallDisplayIcon={app}\DevAtlas.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
LicenseFile=..\LICENSE.txt
CloseApplications=yes
VersionInfoVersion={#AppVersion}.0

[Languages]
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"

[Tasks]
Name: "desktopicon"; Description: "Crea un collegamento sul desktop"; Flags: unchecked

[Files]
Source: "{#PayloadDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "portable.flag,dati-personali\*"

[Icons]
Name: "{group}\DevAtlas"; Filename: "{app}\DevAtlas.exe"
Name: "{autodesktop}\DevAtlas"; Filename: "{app}\DevAtlas.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\DevAtlas.exe"; Description: "Avvia DevAtlas"; Flags: nowait postinstall skipifsilent

