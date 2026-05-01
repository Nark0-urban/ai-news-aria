param(
    [string]$ConfigPath = "config/config.json",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$ExamplePath = Join-Path $ProjectRoot "config/config.example.json"
$TargetPath = Join-Path $ProjectRoot $ConfigPath

if (-not (Test-Path -LiteralPath $ExamplePath)) {
    throw "Missing config example: $ExamplePath"
}

if ((Test-Path -LiteralPath $TargetPath) -and (-not $Force)) {
    Write-Host "Config already exists: $TargetPath"
    Write-Host "Use -Force only if you want to overwrite it."
    exit 0
}

$TargetDir = Split-Path -Parent $TargetPath
New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
Copy-Item -LiteralPath $ExamplePath -Destination $TargetPath -Force

Write-Host "Created local config: $TargetPath"
Write-Host "Open it and replace YOUR_KAKAO_REST_API_KEY with the REST API key from Kakao Developers."
