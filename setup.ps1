$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (!(Test-Path ".venv")) { python -m venv .venv }
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (!(Test-Path ".env")) { Copy-Item ".env.example" ".env" }
& .\.venv\Scripts\python.exe .\scripts\init_demo_db.py
Write-Host "Setup complete. Fill .env credentials before running a real Telegram bot. DEMO_MODE=1 disables real external side effects."
