param(
    [int]$WaitMinutes = 120,
    [int]$IntervalSeconds = 180
)

$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$StartupScript = Join-Path $ProjectRoot "scripts\startup_publish_cardnews.ps1"
$StartupFolder = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup"
$CommandPath = Join-Path $StartupFolder "AI-News-Aria-Startup-Publisher.cmd"

if (-not (Test-Path -LiteralPath $StartupScript)) {
    throw "Missing startup script: $StartupScript"
}

New-Item -ItemType Directory -Force -Path $StartupFolder | Out-Null

$InnerCommand = @"
Set-Location -LiteralPath '$ProjectRoot'
& '$StartupScript' -WaitMinutes $WaitMinutes -IntervalSeconds $IntervalSeconds
"@
$EncodedCommand = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($InnerCommand))
$Command = @"
@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -EncodedCommand $EncodedCommand
"@

Set-Content -Encoding ASCII -LiteralPath $CommandPath -Value $Command

Write-Host "Installed startup publisher command:"
Write-Host $CommandPath
Write-Host "It will run after Windows logon and watch for generated cardnews for up to $WaitMinutes minutes."
