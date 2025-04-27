!include "MUI2.nsh"  ; Use modern UI

; Define product information
!ifndef VERSION
  !define VERSION "1.0.0"
!endif
Name "Xtend - Extend any device with a web browser into a secondary screen for your computer."
OutFile "xtend-${VERSION}-windows-installer.exe"
InstallDir "$PROGRAMFILES\\Xtend"
RequestExecutionLevel user

; Pages for the installer UI
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_LANGUAGE "English"

Section "Install"
  SetOutPath "$INSTDIR"
  File "..\\dist\\xtend.exe"            ; Include the built executable in installer
  CreateShortcut "$SMPROGRAMS\\Xtend\\Xtend.lnk" "$INSTDIR\\xtend.exe" "" "$INSTDIR\\xtend.exe" 0
  CreateShortcut "$DESKTOP\\Xtend.lnk" "$INSTDIR\\xtend.exe" "" "$INSTDIR\\xtend.exe" 0
  WriteUninstaller "$INSTDIR\\Uninstall.exe"
SectionEnd

Section "Uninstall"
  Delete "$SMPROGRAMS\\Xtend\\Xtend.lnk"
  Delete "$DESKTOP\\Xtend.lnk"
  Delete "$INSTDIR\\xtend.exe"
  Delete "$INSTDIR\\Uninstall.exe"
  RMDir "$SMPROGRAMS\\Xtend"    ; remove shortcuts directory
  RMDir "$INSTDIR"
SectionEnd
