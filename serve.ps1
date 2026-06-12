#!/usr/bin/env pwsh
# Intenta servir la carpeta con Python: `python -m http.server 8000`.
if (Get-Command python -ErrorAction SilentlyContinue) {
    Push-Location $PSScriptRoot
    python -m http.server 8000
    Pop-Location
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    Push-Location $PSScriptRoot
    py -m http.server 8000
    Pop-Location
} else {
    Write-Host "Python no encontrado. Abriendo index.html directamente..."
    Start-Process (Join-Path $PSScriptRoot 'index.html')
}
