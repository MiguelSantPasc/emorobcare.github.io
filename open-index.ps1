#!/usr/bin/env pwsh
# Abre index.html en el navegador por defecto
$path = Join-Path $PSScriptRoot 'index.html'
if (Test-Path $path) {
    Start-Process $path
} else {
    Write-Host "No se encontró index.html en $PSScriptRoot"
}
