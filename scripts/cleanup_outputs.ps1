param(
    [int]$KeepDays = 30,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$CardnewsRoot = Join-Path $ProjectRoot "output\cardnews"

if (-not (Test-Path -LiteralPath $CardnewsRoot)) {
    Write-Host "No cardnews output directory found: $CardnewsRoot"
    exit 0
}

$Cutoff = (Get-Date).AddDays(-$KeepDays)
$Targets = Get-ChildItem -LiteralPath $CardnewsRoot -Directory |
    Where-Object {
        $_.Name -match "^\d{4}-\d{2}-\d{2}$" -and $_.LastWriteTime -lt $Cutoff
    }

if (-not $Targets) {
    Write-Host "No cardnews folders older than $KeepDays days."
    exit 0
}

foreach ($Target in $Targets) {
    if ($DryRun) {
        Write-Host "[DRY RUN] Would remove: $($Target.FullName)"
    }
    else {
        Write-Host "Removing: $($Target.FullName)"
        Remove-Item -LiteralPath $Target.FullName -Recurse -Force
    }
}
