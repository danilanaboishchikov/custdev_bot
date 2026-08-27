param([switch]$Telegram)
function Import-DotEnv($Path) {
    if (!(Test-Path $Path)) { return }
    Get-Content $Path | ForEach-Object {
        $line = $_.Trim()
        if ($line -eq '' -or $line.StartsWith('#') -or !$line.Contains('=')) { return }
        $parts = $line.Split('=', 2)
        $name = $parts[0].Trim()
        $value = $parts[1].Trim().Trim('"').Trim("'")
        [Environment]::SetEnvironmentVariable($name, $value, 'Process')
    }
}

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
Import-DotEnv ".env"
if (!(Test-Path ".venv")) { throw "Run .\setup.ps1 first." }
& .\.venv\Scripts\python.exe .\main.py
