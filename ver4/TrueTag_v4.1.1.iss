[Setup]
AppName=TrueTag
AppVersion=4.1.2
AppPublisher=TrueTag
DefaultDirName={userappdata}\TrueTag
DefaultGroupName=TrueTag
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputBaseFilename=TrueTag_v4.1.2_Setup
Compression=lzma
SolidCompression=yes
SetupIconFile=TrueTag_Setup\logo.ico
UninstallDisplayIcon={app}\logo.ico

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "TrueTag_Setup\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[InstallDelete]
Type: files; Name: "{app}\TRUETAG-v4.exe"
Type: files; Name: "{app}\TRUETAG-v4.1.1.exe"
Type: files; Name: "{app}\TRUETAG-v4.1.2.exe"

[Icons]
Name: "{autodesktop}\TrueTag v4.1.2"; Filename: "{app}\TRUETAG-v4.1.2.exe"; IconFilename: "{app}\logo.ico"; Tasks: desktopicon

[Run]
; Run the bat file visually so the user can see and press Enter.
Filename: "{app}\INSTALL.bat"; Description: "Run BricsCAD Integration Script (INSTALL.bat)"; Flags: shellexec waituntilterminated

[Code]
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  // Terminate any running instances of TrueTag before installation
  Exec('taskkill', '/F /IM TRUETAG-v4.exe /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Exec('taskkill', '/F /IM TRUETAG-v4.1.1.exe /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Exec('taskkill', '/F /IM TRUETAG-v4.1.2.exe /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Result := True;
end;
