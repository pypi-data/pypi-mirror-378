param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$FueroDir = "$env:USERPROFILE\.fuero"
$BinDir = "$env:USERPROFILE\.local\bin"
$RepoUrl = "https://github.com/ogcae/fuero"

Write-Host "installing fuero" -ForegroundColor Green

# check if running as administrator
$IsAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

# check python
try {
    $PythonVersion = python --version 2>$null
    if (-not $PythonVersion) {
        throw "python not found"
    }
    Write-Host "✓ python found: $PythonVersion" -ForegroundColor Green
} catch {
    Write-Host "python is required but not installed" -ForegroundColor Red
    Write-Host "please install python from https://python.org and try again" -ForegroundColor Yellow
    exit 1
}

# check pip
try {
    $PipVersion = pip --version 2>$null
    if (-not $PipVersion) {
        throw "pip not found"
    }
    Write-Host "✓ pip found: $PipVersion" -ForegroundColor Green
} catch {
    Write-Host "pip is required but not installed" -ForegroundColor Red
    Write-Host "please install pip and try again" -ForegroundColor Yellow
    exit 1
}

# check git
try {
    $GitVersion = git --version 2>$null
    if (-not $GitVersion) {
        throw "git not found"
    }
    Write-Host "✓ git found: $GitVersion" -ForegroundColor Green
} catch {
    Write-Host "git is required but not installed" -ForegroundColor Red
    Write-Host "please install git from https://git-scm.com and try again" -ForegroundColor Yellow
    exit 1
}

# create directories
New-Item -ItemType Directory -Force -Path $BinDir | Out-Null
New-Item -ItemType Directory -Force -Path $FueroDir | Out-Null

# download or clone fuero
if (Test-Path $FueroDir\.git) {
    Write-Host "updating existing fuero" -ForegroundColor Blue
    Set-Location $FueroDir
    git pull origin main
} else {
    Write-Host "downloading fuero" -ForegroundColor Blue
    if (Test-Path $FueroDir) {
        Remove-Item -Recurse -Force $FueroDir
    }
    git clone $RepoUrl $FueroDir
    Set-Location $FueroDir
}

# install dependencies
Write-Host "installing dependencies" -ForegroundColor Blue
pip install --user -r requirements.txt

# install fuero package
Write-Host "installing fuero package" -ForegroundColor Blue
pip install --user -e .

# create batch script
$BatchScript = @"
@echo off
python -m fuero.cli %*
"@

$BatchScript | Out-File -FilePath "$BinDir\fuero.bat" -Encoding ASCII

# create powershell script
$PowerShellScript = @"
#!/usr/bin/env pwsh
python -m fuero.cli @args
"@

$PowerShellScript | Out-File -FilePath "$BinDir\fuero.ps1" -Encoding UTF8

# add to path
$UserPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($UserPath -notlike "*$BinDir*") {
    Write-Host "adding fuero to user PATH" -ForegroundColor Blue
    $NewPath = "$BinDir;$UserPath"
    [Environment]::SetEnvironmentVariable("PATH", $NewPath, "User")
    $env:PATH = "$BinDir;$env:PATH"
    Write-Host "✓ PATH updated" -ForegroundColor Green
}

Write-Host ""
Write-Host "fuero installed!" -ForegroundColor Green
Write-Host ""
Write-Host "usage:" -ForegroundColor White
Write-Host "  fuero run script.fuero   # run a fuero file" -ForegroundColor Gray
Write-Host "  fuero repl               # interactive mode" -ForegroundColor Gray
Write-Host "  fuero --version          # show version" -ForegroundColor Gray
Write-Host "  fuero --help             # show help" -ForegroundColor Gray
Write-Host ""
Write-Host "if 'fuero' command is not found, restart your terminal or run:" -ForegroundColor Yellow
Write-Host "  refreshenv" -ForegroundColor Gray
Write-Host ""
Write-Host "documentation: $FueroDir\docs\" -ForegroundColor Cyan
Write-Host "examples: $FueroDir\examples\" -ForegroundColor Cyan
