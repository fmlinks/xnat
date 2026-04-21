@echo off
setlocal

REM One-click runner for Windows.
REM - Creates a local venv (.venv) if missing
REM - Installs requirements
REM - Runs uploader (defaults to config/config.yaml)

cd /d "%~dp0\.."

if not exist ".venv\Scripts\python.exe" (
  echo [INFO] Creating venv...
  python -m venv .venv || exit /b 1
  echo [INFO] Installing dependencies...
  .venv\Scripts\python.exe -m pip install --upgrade pip || exit /b 1
  .venv\Scripts\python.exe -m pip install -r requirements.txt || exit /b 1
)

.venv\Scripts\python.exe run.py %*

endlocal
