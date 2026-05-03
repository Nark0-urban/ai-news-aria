param(
    [string]$TaskName = "AI News Aria Publish On Login",
    [int]$DelayMinutes = 3,
    [int]$WaitMinutes = 90,
    [int]$IntervalSeconds = 180
)

$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$StartupScript = Join-Path $ProjectRoot "scripts\startup_publish_cardnews.ps1"

if (-not (Test-Path -LiteralPath $StartupScript)) {
    throw "Missing startup script: $StartupScript"
}

$Argument = @(
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-File", ('"{0}"' -f $StartupScript),
    "-WaitMinutes", $WaitMinutes,
    "-IntervalSeconds", $IntervalSeconds
) -join " "

$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $Argument -WorkingDirectory $ProjectRoot
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Trigger.Delay = "PT${DelayMinutes}M"
$Settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -MultipleInstances IgnoreNew
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal `
    -Description "Publish generated AI News Aria cardnews from Codex worktrees after Windows logon." `
    -Force | Out-Null

Write-Host "Registered scheduled task: $TaskName"
Write-Host "It runs $DelayMinutes minutes after Windows logon and watches for generated cardnews for up to $WaitMinutes minutes."
