param(
    [string]$ConfigPath = "config/config.json",
    [string]$Text = "Aria card news is ready.",
    [string]$Title = "AI News Aria",
    [string]$Description = "",
    [string]$ImageUrl = "",
    [string]$LinkUrl = "https://example.com",
    [switch]$DryRun
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
$TokenPath = Join-Path $ProjectRoot $Config.kakao.token_file

if ([string]::IsNullOrWhiteSpace($RestApiKey) -or $RestApiKey -eq "YOUR_KAKAO_REST_API_KEY") {
    throw "Set kakao.rest_api_key in config/config.json before sending Kakao messages."
}

if (-not (Test-Path -LiteralPath $TokenPath)) {
    throw "Missing Kakao token file: $TokenPath. Run scripts/kakao_auth.ps1 first."
}

function Save-Token {
    param([object]$Token)
    $Token | ConvertTo-Json -Depth 10 | Set-Content -Encoding UTF8 -LiteralPath $TokenPath
}

function Refresh-TokenIfNeeded {
    param([object]$Token)

    if (-not $Token.expires_at) {
        return $Token
    }

    $ExpiresAt = [DateTime]::Parse($Token.expires_at)
    if ($ExpiresAt -gt (Get-Date).AddMinutes(5)) {
        return $Token
    }

    if ([string]::IsNullOrWhiteSpace($Token.refresh_token)) {
        throw "Access token expired and no refresh_token exists. Run scripts/kakao_auth.ps1 again."
    }

    Write-Host "Refreshing Kakao access token..."
    $Body = @{
        grant_type    = "refresh_token"
        client_id     = $RestApiKey
        refresh_token = $Token.refresh_token
    }
    if (-not [string]::IsNullOrWhiteSpace($ClientSecret)) {
        $Body.client_secret = $ClientSecret
    }

    $NewToken = Invoke-RestMethod -Method Post -Uri "https://kauth.kakao.com/oauth/token" -Body $Body
    $Now = Get-Date
    $NewToken | Add-Member -NotePropertyName obtained_at -NotePropertyValue $Now.ToString("o") -Force
    if ($NewToken.expires_in) {
        $NewToken | Add-Member -NotePropertyName expires_at -NotePropertyValue $Now.AddSeconds([int]$NewToken.expires_in).ToString("o") -Force
    }
    if (-not $NewToken.refresh_token) {
        $NewToken | Add-Member -NotePropertyName refresh_token -NotePropertyValue $Token.refresh_token -Force
    }

    Save-Token -Token $NewToken
    return $NewToken
}

$Token = Get-Content -Raw -Encoding UTF8 -LiteralPath $TokenPath | ConvertFrom-Json
$Token = Refresh-TokenIfNeeded -Token $Token

if ([string]::IsNullOrWhiteSpace($ImageUrl)) {
    $TemplateObject = @{
        object_type  = "text"
        text         = $Text
        link         = @{
            web_url        = $LinkUrl
            mobile_web_url = $LinkUrl
        }
        button_title = "Open"
    }
}
else {
    if ([string]::IsNullOrWhiteSpace($Description)) {
        $Description = $Text
    }

    $TemplateObject = @{
        object_type = "feed"
        content     = @{
            title       = $Title
            description = $Description
            image_url   = $ImageUrl
            link        = @{
                web_url        = $LinkUrl
                mobile_web_url = $LinkUrl
            }
        }
        buttons     = @(
            @{
                title = "카드뉴스 보기"
                link  = @{
                    web_url        = $LinkUrl
                    mobile_web_url = $LinkUrl
                }
            }
        )
    }
}

$TemplateJson = $TemplateObject | ConvertTo-Json -Depth 20 -Compress

if ($DryRun) {
    Write-Host $TemplateJson
    exit 0
}

$Headers = @{
    Authorization = "Bearer $($Token.access_token)"
}

$Body = @{
    template_object = $TemplateJson
}

$Response = Invoke-RestMethod -Method Post -Uri "https://kapi.kakao.com/v2/api/talk/memo/default/send" -Headers $Headers -Body $Body
$Response | ConvertTo-Json -Depth 10
