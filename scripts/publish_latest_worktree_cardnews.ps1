param(
    [string]$Date = (Get-Date).AddDays(-1).ToString("yyyy-MM-dd"),
    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [string]$WorktreesRoot = (Join-Path $env:USERPROFILE ".codex\worktrees"),
    [string]$SiteTitle = "AI News Aria",
    [string]$BaseUrl = "https://nark0-urban.github.io/ai-news-aria",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

function Write-Log {
    param([string]$Message)

    $LogDir = Join-Path $ProjectRoot "logs"
    New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
    $Line = "[{0}] {1}" -f (Get-Date).ToString("yyyy-MM-dd HH:mm:ss"), $Message
    Add-Content -Encoding UTF8 -LiteralPath (Join-Path $LogDir "startup-cardnews.log") -Value $Line
    Write-Host $Line
}

function Find-Python {
    $Python = (Get-Command python -ErrorAction SilentlyContinue).Source
    if (-not $Python) {
        $Python = (Get-Command py -ErrorAction SilentlyContinue).Source
    }
    if (-not $Python) {
        $BundledPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
        if (Test-Path -LiteralPath $BundledPython) {
            $Python = $BundledPython
        }
    }
    if (-not $Python) {
        throw "Python executable not found."
    }
    return $Python
}

function Find-Git {
    $Git = (Get-Command git -ErrorAction SilentlyContinue).Source
    if (-not $Git) {
        $Git = "C:\Program Files\Git\cmd\git.exe"
    }
    if (-not (Test-Path -LiteralPath $Git)) {
        throw "Git executable not found."
    }
    return $Git
}

function Find-GeneratedCardnews {
    param([string]$TargetDate)

    if (-not (Test-Path -LiteralPath $WorktreesRoot)) {
        return $null
    }

    $Candidates = Get-ChildItem -LiteralPath $WorktreesRoot -Directory -Recurse -ErrorAction SilentlyContinue |
        Where-Object {
            $_.Name -eq $TargetDate -and
            $_.FullName -like "*\output\cardnews\$TargetDate" -and
            (Test-Path -LiteralPath (Join-Path $_.FullName "cards.json")) -and
            ((Get-ChildItem -LiteralPath $_.FullName -Filter "card_*.png" -File -ErrorAction SilentlyContinue).Count -gt 0)
        } |
        Sort-Object LastWriteTime -Descending

    return $Candidates | Select-Object -First 1
}

Set-Location -LiteralPath $ProjectRoot

$Git = Find-Git
$Python = Find-Python

& $Git fetch origin main --quiet
if ($LASTEXITCODE -eq 0) {
    $RemoteHasDate = & $Git ls-tree -r --name-only "origin/main" -- "docs/cardnews/$Date/card_01.png" 2>$null
    if ($RemoteHasDate) {
        Write-Log "Remote already has docs/cardnews/$Date/card_01.png. Nothing to publish."
        exit 0
    }
}
else {
    Write-Log "Could not fetch origin/main before duplicate check. Continuing with local publish check."
}

$SourceDir = Find-GeneratedCardnews -TargetDate $Date

if (-not $SourceDir) {
    Write-Log "No generated cardnews found for $Date under $WorktreesRoot."
    exit 0
}

Write-Log "Found generated cardnews for $Date at $($SourceDir.FullName)."

$OutputTarget = Join-Path $ProjectRoot "output\cardnews\$Date"
New-Item -ItemType Directory -Force -Path $OutputTarget | Out-Null
Copy-Item -LiteralPath (Join-Path $SourceDir.FullName "*") -Destination $OutputTarget -Recurse -Force

if ($DryRun) {
    Write-Log "Dry run: copied generated cardnews to $OutputTarget; stopping before publish/git."
    exit 0
}

& $Python (Join-Path $ProjectRoot "scripts\publish_to_pages.py") --date $Date --base-url $BaseUrl --site-title $SiteTitle
if ($LASTEXITCODE -ne 0) {
    throw "publish_to_pages.py failed with exit code $LASTEXITCODE"
}

& $Git add "docs/index.html" "docs/cardnews/$Date"
if ($LASTEXITCODE -ne 0) {
    throw "git add failed with exit code $LASTEXITCODE"
}

& $Git diff --cached --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Log "No Git changes for $Date. Nothing to push, so Kakao will not be sent again."
    exit 0
}
elseif ($LASTEXITCODE -ne 1) {
    throw "git diff --cached failed with exit code $LASTEXITCODE"
}

& $Git commit -m "Publish $Date cardnews"
if ($LASTEXITCODE -ne 0) {
    throw "git commit failed with exit code $LASTEXITCODE"
}

& $Git push origin main
if ($LASTEXITCODE -ne 0) {
    throw "git push failed with exit code $LASTEXITCODE"
}

Write-Log "Published $Date cardnews and pushed to GitHub. Kakao notify workflow should run from the push."
