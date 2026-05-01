param(
    [string]$ConfigPath = "config/config.json",
    [switch]$Refresh
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$ConfigFullPath = Join-Path $ProjectRoot $ConfigPath

if (-not (Test-Path -LiteralPath $ConfigFullPath)) {
    throw "Missing config file: $ConfigFullPath. Copy config/config.example.json to config/config.json and set kakao.rest_api_key first."
}

$Config = Get-Content -Raw -Encoding UTF8 -LiteralPath $ConfigFullPath | ConvertFrom-Json
$RestApiKey = $Config.kakao.rest_api_key
$ClientSecret = $Config.kakao.client_secret
$RedirectUri = $Config.kakao.redirect_uri
$TokenPath = Join-Path $ProjectRoot $Config.kakao.token_file

if ([string]::IsNullOrWhiteSpace($RestApiKey) -or $RestApiKey -eq "YOUR_KAKAO_REST_API_KEY") {
    throw "Set kakao.rest_api_key in config/config.json before running OAuth."
}

function Save-Token {
    param([object]$Token)

    $Now = Get-Date
    $Token | Add-Member -NotePropertyName obtained_at -NotePropertyValue $Now.ToString("o") -Force

    if ($Token.expires_in) {
        $Token | Add-Member -NotePropertyName expires_at -NotePropertyValue $Now.AddSeconds([int]$Token.expires_in).ToString("o") -Force
    }

    if ($Token.refresh_token_expires_in) {
        $Token | Add-Member -NotePropertyName refresh_token_expires_at -NotePropertyValue $Now.AddSeconds([int]$Token.refresh_token_expires_in).ToString("o") -Force
    }

    $TokenDir = Split-Path -Parent $TokenPath
    New-Item -ItemType Directory -Force -Path $TokenDir | Out-Null
    $Token | ConvertTo-Json -Depth 10 | Set-Content -Encoding UTF8 -LiteralPath $TokenPath
    Write-Host "Saved Kakao token: $TokenPath"
}

if ($Refresh) {
    if (-not (Test-Path -LiteralPath $TokenPath)) {
        throw "No token file found to refresh: $TokenPath"
    }

    $SavedToken = Get-Content -Raw -Encoding UTF8 -LiteralPath $TokenPath | ConvertFrom-Json
    if ([string]::IsNullOrWhiteSpace($SavedToken.refresh_token)) {
        throw "Token file has no refresh_token. Run OAuth again without -Refresh."
    }

    $Body = @{
        grant_type    = "refresh_token"
        client_id     = $RestApiKey
        refresh_token = $SavedToken.refresh_token
    }
    if (-not [string]::IsNullOrWhiteSpace($ClientSecret)) {
        $Body.client_secret = $ClientSecret
    }

    $NewToken = Invoke-RestMethod -Method Post -Uri "https://kauth.kakao.com/oauth/token" -Body $Body

    if (-not $NewToken.refresh_token) {
        $NewToken | Add-Member -NotePropertyName refresh_token -NotePropertyValue $SavedToken.refresh_token -Force
    }

    Save-Token -Token $NewToken
    exit 0
}

$Redirect = [Uri]$RedirectUri
$Prefix = "{0}://{1}:{2}{3}" -f $Redirect.Scheme, $Redirect.Host, $Redirect.Port, $Redirect.AbsolutePath
if (-not $Prefix.EndsWith("/")) {
    $Prefix = "$Prefix/"
}

$Query = @{
    response_type = "code"
    client_id     = $RestApiKey
    redirect_uri  = $RedirectUri
    scope         = "talk_message"
}

$QueryString = ($Query.GetEnumerator() | ForEach-Object {
    "{0}={1}" -f [Uri]::EscapeDataString($_.Key), [Uri]::EscapeDataString([string]$_.Value)
}) -join "&"

$AuthUrl = "https://kauth.kakao.com/oauth/authorize?$QueryString"

Write-Host ""
Write-Host "Open this URL in your browser, approve Kakao login, then keep this window open:"
Write-Host $AuthUrl
Write-Host ""
Write-Host "Waiting for callback on $Prefix"

$Listener = [System.Net.HttpListener]::new()
$Listener.Prefixes.Add($Prefix)

try {
    $Listener.Start()
    $Context = $Listener.GetContext()
    $Code = $Context.Request.QueryString["code"]
    $ErrorMessage = $Context.Request.QueryString["error_description"]

    $ResponseText = "Kakao OAuth complete. You can close this browser tab."
    if (-not [string]::IsNullOrWhiteSpace($ErrorMessage)) {
        $ResponseText = "Kakao OAuth failed: $ErrorMessage"
    }

    $Buffer = [System.Text.Encoding]::UTF8.GetBytes($ResponseText)
    $Context.Response.ContentType = "text/plain; charset=utf-8"
    $Context.Response.OutputStream.Write($Buffer, 0, $Buffer.Length)
    $Context.Response.Close()

    if ([string]::IsNullOrWhiteSpace($Code)) {
        throw "No authorization code received. $ErrorMessage"
    }

    $Body = @{
        grant_type   = "authorization_code"
        client_id    = $RestApiKey
        redirect_uri = $RedirectUri
        code         = $Code
    }
    if (-not [string]::IsNullOrWhiteSpace($ClientSecret)) {
        $Body.client_secret = $ClientSecret
    }

    $Token = Invoke-RestMethod -Method Post -Uri "https://kauth.kakao.com/oauth/token" -Body $Body
    Save-Token -Token $Token
}
finally {
    if ($Listener.IsListening) {
        $Listener.Stop()
    }
    $Listener.Close()
}
