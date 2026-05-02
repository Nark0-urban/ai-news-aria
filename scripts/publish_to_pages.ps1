param(
    [string]$ConfigPath = "config/config.json",
    [string]$Date = (Get-Date).ToString("yyyy-MM-dd"),
    [string]$BaseUrl = "https://nark0-urban.github.io/ai-news-aria",
    [string]$SiteTitle = "AI News Aria"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$PythonScript = Join-Path $ProjectRoot "scripts/publish_to_pages.py"

$Python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $Python) {
    $Python = (Get-Command py -ErrorAction SilentlyContinue).Source
}
if (-not $Python) {
    $BundledPython = Join-Path $env:USERPROFILE ".cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe"
    if (Test-Path -LiteralPath $BundledPython) {
        $Python = $BundledPython
    }
}
if (-not $Python) {
    throw "Python executable not found. Install Python or run with the Codex bundled runtime."
}

& $Python $PythonScript --config $ConfigPath --date $Date --base-url $BaseUrl --site-title $SiteTitle
if ($LASTEXITCODE -ne 0) {
    throw "publish_to_pages.py failed with exit code $LASTEXITCODE"
}
