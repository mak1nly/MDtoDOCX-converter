#define VersionFile FileOpen(SourcePath + "\assets\VERSION")
#define AppVersion FileRead(VersionFile)
#expr FileClose(VersionFile)

[Setup]
AppId={{E9D59C97-4AAC-4E35-903B-592171F72154}
AppName=MDtoDOCX
AppVersion={#AppVersion}
AppPublisher=mak1nly
AppSupportURL=mailto:mak1nly@yandex.ru
DefaultDirName={localappdata}\Programs\MDtoDOCX
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes
WizardStyle=modern
OutputDir=dist
OutputBaseFilename=MDtoDOCX-Setup
SetupIconFile=assets\document.ico
UninstallDisplayIcon={app}\MDtoDOCX.exe
VersionInfoVersion={#AppVersion}.0
Compression=zip
SolidCompression=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Files]
Source: "dist\MDtoDOCX.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{userprograms}\MDtoDOCX"; Filename: "{app}\MDtoDOCX.exe"

[Run]
Filename: "{app}\MDtoDOCX.exe"; Description: "{cm:LaunchProgram,MDtoDOCX}"; Flags: nowait postinstall skipifsilent
