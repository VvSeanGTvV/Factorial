@ECHO OFF
if exist dist RMDIR /S /Q dist 
goto MAIN


:MAIN
if exist dist/assets goto FINISH
if exist dist/main.exe goto OPFINISH else goto PKG

:PKG
pyinstaller --onefile main.pyw
goto MAIN

:MKASSETS
cd dist
mkdir assets
cd ..
goto MOVASSETS

:OPFINISH
echo [PYINSTALLER] FINISHED PACKAGE
echo [PACKAGER] checking files
if exist dist/assets goto MAIN
if NOT exist dist/assets goto MKASSETS
goto MOVASSETS

:MOVASSETS
robocopy assets dist/assets /E
echo [PACKAGER] copied necessary files
goto MAIN

:FINISH
echo [PACKAGER] finishing up
cd dist/
if exist main.exe rename main.exe Factorial.exe
echo [PACKAGER] package complete
pause