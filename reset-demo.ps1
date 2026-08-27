$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
& .\.venv\Scripts\python.exe .\scripts\init_demo_db.py --reset
Write-Host "Demo runtime state reset."
