; Script de Inno Setup para crear el instalador de InventarioPOS
; Se compila usando el compilador de Inno Setup (Compiler IDE)

[Setup]
; Información de la aplicación
AppId={{D37E6F22-A109-4E64-A8DC-58DE17A167EE}
AppName=InventarioPOS
AppVersion=1.0.0
AppPublisher=Desarrollador
DefaultDirName={autopf}\InventarioPOS
DefaultGroupName=InventarioPOS
DisableProgramGroupPage=yes
; Directorio de salida del instalador compilado y nombre del archivo
OutputDir=dist
OutputBaseFilename=setup_inventariopos_1.0.0
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Archivo ejecutable de la aplicación compilado con PyInstaller
Source: "dist\InventarioPOS.exe"; DestDir: "{app}"; Flags: ignoreversion
; Nota: La base de datos y la carpeta de imágenes se crearán automáticamente 
; en %APPDATA%\InventarioPOS en la primera ejecución del programa por el usuario.

[Icons]
Name: "{group}\InventarioPOS"; Filename: "{app}\InventarioPOS.exe"
Name: "{autodesktop}\InventarioPOS"; Filename: "{app}\InventarioPOS.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\InventarioPOS.exe"; Description: "{cm:LaunchProgram,InventarioPOS}"; Flags: nowait postinstall skipifsilent
