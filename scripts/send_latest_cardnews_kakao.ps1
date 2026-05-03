param(
    [string]$Date = "",
    [string]$ConfigPath = "config/config.json",
    [string]$BaseUrl = "https://nark0-urban.github.io/ai-news-aria",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$PythonScript = Join-Path $ProjectRoot "scripts/send_latest_cardnews_kakao.py"

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
    throw "Python executable not found."
}

$ArgsList = @($PythonScript, "--config", $ConfigPath, "--base-url", $BaseUrl)
if (-not [string]::IsNullOrWhiteSpace($Date)) {
    $ArgsList += @("--date", $Date)
}
if ($DryRun) {
    $ArgsList += "--dry-run"
}

& $Python @ArgsList
if ($LASTEXITCODE -ne 0) {
    throw "send_latest_cardnews_kakao.py failed with exit code $LASTEXITCODE"
}
