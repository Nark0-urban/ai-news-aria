param(
    [string]$Date = (Get-Date).AddDays(-1).ToString("yyyy-MM-dd"),
    [int]$WaitMinutes = 90,
    [int]$IntervalSeconds = 180
)

$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Publisher = Join-Path $ProjectRoot "scripts\publish_latest_worktree_cardnews.ps1"
$Deadline = (Get-Date).AddMinutes($WaitMinutes)

function Write-StartupLog {
    param([string]$Message)

    $LogDir = Join-Path $ProjectRoot "logs"
    New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
    $Line = "[{0}] {1}" -f (Get-Date).ToString("yyyy-MM-dd HH:mm:ss"), $Message
    Add-Content -Encoding UTF8 -LiteralPath (Join-Path $LogDir "startup-cardnews.log") -Value $Line
    Write-Host $Line
}

Write-StartupLog "Startup publisher began for $Date. It will watch for up to $WaitMinutes minutes."

while ((Get-Date) -le $Deadline) {
    & powershell -NoProfile -ExecutionPolicy Bypass -File $Publisher -Date $Date
    if ($LASTEXITCODE -ne 0) {
        Write-StartupLog "Publisher exited with code $LASTEXITCODE. Will retry if time remains."
    }

    $Git = (Get-Command git -ErrorAction SilentlyContinue).Source
    if (-not $Git) { $Git = "C:\Program Files\Git\cmd\git.exe" }
    if (Test-Path -LiteralPath $Git) {
        Set-Location -LiteralPath $ProjectRoot
        $RemoteHasDate = & $Git ls-tree -r --name-only "origin/main" -- "docs/cardnews/$Date/card_01.png" 2>$null
        if ($RemoteHasDate) {
            Write-StartupLog "Remote already has docs/cardnews/$Date/card_01.png. Startup publisher is done."
            exit 0
        }
    }

    Start-Sleep -Seconds $IntervalSeconds
}

Write-StartupLog "Startup publisher timed out for $Date. No publishable generated result was found."
