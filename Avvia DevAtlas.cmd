@echo off
cd /d "%~dp0"
if exist "dist\DevAtlas-1.3.0\DevAtlas.exe" (
  start "" "dist\DevAtlas-1.3.0\DevAtlas.exe"
) else if exist "dist\DevAtlas-1.2.0\DevAtlas.exe" (
  start "" "dist\DevAtlas-1.2.0\DevAtlas.exe"
) else if exist "dist\DevAtlas-1.1.0\DevAtlas.exe" (
  start "" "dist\DevAtlas-1.1.0\DevAtlas.exe"
) else if exist "dist\DevAtlas\DevAtlas.exe" (
  start "" "dist\DevAtlas\DevAtlas.exe"
) else if exist ".venv\Scripts\pythonw.exe" (
  start "" ".venv\Scripts\pythonw.exe" "run_devatlas.py"
) else (
  echo Eseguire prima la preparazione descritta nel README.
  pause
)

