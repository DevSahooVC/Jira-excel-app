$ErrorActionPreference = "Stop"

$backendDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoDir = Split-Path -Parent $backendDir
$frontendDir = Join-Path $repoDir "frontend"

Write-Host "==> Building frontend (Vite)..." -ForegroundColor Cyan
Push-Location $frontendDir
npm install
npm run build
Pop-Location

Write-Host "==> Syncing frontend build into backend/app/static..." -ForegroundColor Cyan
$staticDir = Join-Path $backendDir "app\static"
if (Test-Path $staticDir) { Remove-Item -Recurse -Force $staticDir }
New-Item -ItemType Directory -Path $staticDir | Out-Null
Copy-Item -Recurse -Force (Join-Path $frontendDir "dist\*") $staticDir

Write-Host "==> Creating isolated build venv + installing backend deps..." -ForegroundColor Cyan
Push-Location $backendDir
$buildVenv = ".buildvenv"
if (Test-Path $buildVenv) { Remove-Item -Recurse -Force $buildVenv }
py -3.11 -m venv $buildVenv
.\.buildvenv\Scripts\python.exe -m pip install -U pip
.\.buildvenv\Scripts\python.exe -m pip install -r requirements.txt
.\.buildvenv\Scripts\python.exe -m pip install pyinstaller

Write-Host "==> Building onefile exe..." -ForegroundColor Cyan
.\.buildvenv\Scripts\python.exe -m PyInstaller `
  --noconfirm `
  --onefile `
  --name "jira-excel-reporter" `
  --clean `
  --add-data "app\static;app\static" `
  --add-data "sample_data;sample_data" `
  "run_exe.py"

if ($LASTEXITCODE -ne 0) {
  throw "PyInstaller build failed."
}

Write-Host ""
Write-Host "Done." -ForegroundColor Green
Write-Host "EXE is at: $backendDir\dist\jira-excel-reporter.exe"
Pop-Location

