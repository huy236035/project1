# PowerShell script to run backend
Write-Host "Starting Backend Server..." -ForegroundColor Green
Set-Location $PSScriptRoot
py -3 app.py

