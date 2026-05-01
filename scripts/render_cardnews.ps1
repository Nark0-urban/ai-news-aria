param(
    [string]$ConfigPath = "config/config.json",
    [string]$CardsJson = "",
    [string]$Date = (Get-Date).ToString("yyyy-MM-dd"),
    [switch]$Sample
)

$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.Drawing

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$ConfigFullPath = Join-Path $ProjectRoot $ConfigPath
if (-not (Test-Path -LiteralPath $ConfigFullPath)) {
    $ConfigFullPath = Join-Path $ProjectRoot "config/config.example.json"
}

$Config = Get-Content -Raw -Encoding UTF8 -LiteralPath $ConfigFullPath | ConvertFrom-Json
$Width = [int]$Config.cardnews.image_width
$Height = [int]$Config.cardnews.image_height
$OutputRoot = Join-Path $ProjectRoot $Config.cardnews.output_dir
$OutputDir = Join-Path $OutputRoot $Date
$ReferenceImagePath = Join-Path $ProjectRoot $Config.cardnews.character_reference

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

function New-SampleCards {
    param([string]$TargetDate)

    return [pscustomobject]@{
        date = $TargetDate
        cards = @(
            [pscustomobject]@{
                type = "cover"
                title = "AI News Brief"
                summary = "A quick sample card for checking the renderer."
                aria_line = "I will turn today's AI flow into simple cards."
                caption = "AI News Curator Aria"
                importance = "Brief"
                sources = @()
            },
            [pscustomobject]@{
                type = "news"
                title = "Product Updates"
                summary = "Track model releases, feature changes, and pricing updates by their real workflow impact."
                aria_line = "The useful question is: what changes in my work?"
                caption = "Focus on practical impact"
                importance = "Important"
                sources = @([pscustomobject]@{ name = "Example Source"; url = "https://example.com" })
            },
            [pscustomobject]@{
                type = "point"
                title = "Tomorrow's Watch Point"
                summary = "Collect repeated signals and decide what to watch next."
                aria_line = "One day is a dot. A few days become a trend."
                caption = "Keywords to watch again"
                importance = "Check"
                sources = @()
            }
        )
    }
}

if (-not [string]::IsNullOrWhiteSpace($CardsJson)) {
    $CardsFullPath = Join-Path $ProjectRoot $CardsJson
    $Data = Get-Content -Raw -Encoding UTF8 -LiteralPath $CardsFullPath | ConvertFrom-Json
}
else {
    $DefaultCardsPath = Join-Path $OutputDir "cards.json"
    if ((-not $Sample) -and (Test-Path -LiteralPath $DefaultCardsPath)) {
        $Data = Get-Content -Raw -Encoding UTF8 -LiteralPath $DefaultCardsPath | ConvertFrom-Json
    }
    else {
        $Data = New-SampleCards -TargetDate $Date
        $Data | ConvertTo-Json -Depth 20 | Set-Content -Encoding UTF8 -LiteralPath $DefaultCardsPath
    }
}

function Get-TextValue {
    param($Value, [string]$Default)
    if ($null -eq $Value) { return $Default }
    $Text = [string]$Value
    if ([string]::IsNullOrWhiteSpace($Text)) { return $Default }
    return $Text
}

function New-Font {
    param([float]$Size, [System.Drawing.FontStyle]$Style = [System.Drawing.FontStyle]::Regular)
    return [System.Drawing.Font]::new("Malgun Gothic", $Size, $Style, [System.Drawing.GraphicsUnit]::Pixel)
}

function Split-Lines {
    param(
        [System.Drawing.Graphics]$Graphics,
        [string]$Text,
        [System.Drawing.Font]$Font,
        [int]$MaxWidth
    )

    $Lines = New-Object System.Collections.Generic.List[string]
    foreach ($Paragraph in ($Text -split "(\r?\n)+")) {
        if ([string]::IsNullOrWhiteSpace($Paragraph)) { continue }

        $Current = ""
        foreach ($Word in ($Paragraph -split "\s+")) {
            if ([string]::IsNullOrWhiteSpace($Word)) { continue }
            $Candidate = $Word
            if (-not [string]::IsNullOrWhiteSpace($Current)) {
                $Candidate = "$Current $Word"
            }

            if ($Graphics.MeasureString($Candidate, $Font).Width -le $MaxWidth) {
                $Current = $Candidate
            }
            else {
                if (-not [string]::IsNullOrWhiteSpace($Current)) {
                    $Lines.Add($Current)
                }
                $Current = $Word
            }
        }
        if (-not [string]::IsNullOrWhiteSpace($Current)) {
            $Lines.Add($Current)
        }
    }

    return $Lines
}

function Draw-WrappedText {
    param(
        [System.Drawing.Graphics]$Graphics,
        [string]$Text,
        [System.Drawing.Font]$Font,
        [System.Drawing.Brush]$Brush,
        [int]$X,
        [int]$Y,
        [int]$MaxWidth,
        [int]$LineHeight,
        [int]$MaxLines = 99
    )

    $Lines = Split-Lines -Graphics $Graphics -Text $Text -Font $Font -MaxWidth $MaxWidth
    $CurrentY = $Y
    $Count = 0
    foreach ($Line in $Lines) {
        if ($Count -ge $MaxLines) { break }
        $Graphics.DrawString($Line, $Font, $Brush, [float]$X, [float]$CurrentY)
        $CurrentY += $LineHeight
        $Count += 1
    }
    return $CurrentY
}

function New-RoundedRectanglePath {
    param(
        [System.Drawing.Rectangle]$Rect,
        [int]$Radius
    )

    $Path = [System.Drawing.Drawing2D.GraphicsPath]::new()
    $Diameter = $Radius * 2
    $Arc = [System.Drawing.Rectangle]::new($Rect.X, $Rect.Y, $Diameter, $Diameter)

    $Path.AddArc($Arc, 180, 90)
    $Arc.X = $Rect.Right - $Diameter
    $Path.AddArc($Arc, 270, 90)
    $Arc.Y = $Rect.Bottom - $Diameter
    $Path.AddArc($Arc, 0, 90)
    $Arc.X = $Rect.Left
    $Path.AddArc($Arc, 90, 90)
    $Path.CloseFigure()

    return $Path
}

function Fill-RoundedRectangle {
    param(
        [System.Drawing.Graphics]$Graphics,
        [System.Drawing.Brush]$Brush,
        [System.Drawing.Rectangle]$Rect,
        [int]$Radius
    )

    $Path = New-RoundedRectanglePath -Rect $Rect -Radius $Radius
    try {
        $Graphics.FillPath($Brush, $Path)
    }
    finally {
        $Path.Dispose()
    }
}

function Draw-RoundedRectangle {
    param(
        [System.Drawing.Graphics]$Graphics,
        [System.Drawing.Pen]$Pen,
        [System.Drawing.Rectangle]$Rect,
        [int]$Radius
    )

    $Path = New-RoundedRectanglePath -Rect $Rect -Radius $Radius
    try {
        $Graphics.DrawPath($Pen, $Path)
    }
    finally {
        $Path.Dispose()
    }
}

function Draw-Card {
    param(
        [object]$Card,
        [int]$Index,
        [string]$Path
    )

    $Bitmap = [System.Drawing.Bitmap]::new($Width, $Height)
    $Graphics = [System.Drawing.Graphics]::FromImage($Bitmap)
    $Graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $Graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit

    $Background = [System.Drawing.Drawing2D.LinearGradientBrush]::new(
        [System.Drawing.Rectangle]::new(0, 0, $Width, $Height),
        [System.Drawing.Color]::FromArgb(245, 250, 255),
        [System.Drawing.Color]::FromArgb(218, 236, 255),
        90
    )
    $Graphics.FillRectangle($Background, 0, 0, $Width, $Height)

    if (Test-Path -LiteralPath $ReferenceImagePath) {
        $Ref = [System.Drawing.Image]::FromFile($ReferenceImagePath)
        try {
            $TargetW = 560
            $TargetH = [int]($Ref.Height * ($TargetW / $Ref.Width))
            $TargetX = $Width - $TargetW + 20
            $TargetY = $Height - $TargetH + 40
            $Graphics.DrawImage($Ref, $TargetX, $TargetY, $TargetW, $TargetH)
        }
        finally {
            $Ref.Dispose()
        }
    }

    $PanelBrush = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(238, 255, 255, 255))
    $PanelPen = [System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(255, 26, 66, 118), 5)
    $PanelRect = [System.Drawing.Rectangle]::new(64, 82, 720, 910)
    Fill-RoundedRectangle -Graphics $Graphics -Brush $PanelBrush -Rect $PanelRect -Radius 34
    Draw-RoundedRectangle -Graphics $Graphics -Pen $PanelPen -Rect $PanelRect -Radius 34

    $Navy = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(255, 12, 38, 82))
    $Blue = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(255, 0, 166, 230))
    $Gold = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(255, 247, 190, 55))
    $Gray = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(255, 74, 88, 112))

    $SmallFont = New-Font 30
    $MetaFont = New-Font 28 ([System.Drawing.FontStyle]::Bold)
    $TitleFont = New-Font 72 ([System.Drawing.FontStyle]::Bold)
    $BodyFont = New-Font 39
    $SpeechFont = New-Font 38 ([System.Drawing.FontStyle]::Bold)

    $Badge = "CARD {0:00} / {1}" -f $Index, $Data.cards.Count
    $Graphics.DrawString($Badge, $MetaFont, $Blue, 92, 120)
    $Graphics.DrawString((Get-TextValue $Card.importance "News"), $MetaFont, $Gold, 92, 164)

    $Title = Get-TextValue $Card.title "AI News Aria"
    $Summary = Get-TextValue $Card.summary "No summary yet."
    $AriaLine = Get-TextValue $Card.aria_line "I will keep this simple."
    $Caption = Get-TextValue $Card.caption "AI News Curator Aria"

    Draw-WrappedText -Graphics $Graphics -Text $Title -Font $TitleFont -Brush $Navy -X 92 -Y 235 -MaxWidth 620 -LineHeight 84 -MaxLines 3 | Out-Null
    Draw-WrappedText -Graphics $Graphics -Text ([string]$Summary) -Font $BodyFont -Brush $Gray -X 96 -Y 410 -MaxWidth 610 -LineHeight 55 -MaxLines 4 | Out-Null

    $SpeechRect = [System.Drawing.Rectangle]::new(92, 690, 640, 230)
    $SpeechBrush = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(255, 255, 255, 255))
    $SpeechPen = [System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(255, 10, 47, 100), 4)
    Fill-RoundedRectangle -Graphics $Graphics -Brush $SpeechBrush -Rect $SpeechRect -Radius 32
    Draw-RoundedRectangle -Graphics $Graphics -Pen $SpeechPen -Rect $SpeechRect -Radius 32
    Draw-WrappedText -Graphics $Graphics -Text ([string]$AriaLine) -Font $SpeechFont -Brush $Navy -X 126 -Y 728 -MaxWidth 570 -LineHeight 52 -MaxLines 3 | Out-Null

    $FooterRect = [System.Drawing.Rectangle]::new(64, 1086, 952, 150)
    $FooterBrush = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(230, 9, 32, 70))
    Fill-RoundedRectangle -Graphics $Graphics -Brush $FooterBrush -Rect $FooterRect -Radius 28
    Draw-WrappedText -Graphics $Graphics -Text ([string]$Caption) -Font $SmallFont -Brush ([System.Drawing.Brushes]::White) -X 100 -Y 1125 -MaxWidth 850 -LineHeight 42 -MaxLines 2 | Out-Null

    $SourceText = ""
    if ($Card.sources) {
        $Names = @()
        foreach ($Source in $Card.sources) {
            if ($Source.name) { $Names += [string]$Source.name }
        }
        if ($Names.Count -gt 0) {
            $SourceText = "Sources: " + ($Names -join ", ")
            Draw-WrappedText -Graphics $Graphics -Text $SourceText -Font (New-Font 24) -Brush $Gray -X 92 -Y 1012 -MaxWidth 900 -LineHeight 34 -MaxLines 2 | Out-Null
        }
    }

    $Bitmap.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png)

    $Background.Dispose()
    $PanelBrush.Dispose()
    $PanelPen.Dispose()
    $Navy.Dispose()
    $Blue.Dispose()
    $Gold.Dispose()
    $Gray.Dispose()
    $SmallFont.Dispose()
    $MetaFont.Dispose()
    $TitleFont.Dispose()
    $BodyFont.Dispose()
    $SpeechFont.Dispose()
    $Graphics.Dispose()
    $Bitmap.Dispose()
}

$Index = 1
foreach ($Card in $Data.cards) {
    $FileName = "card_{0:00}.png" -f $Index
    $Path = Join-Path $OutputDir $FileName
    Draw-Card -Card $Card -Index $Index -Path $Path
    Write-Host "Rendered: $Path"
    $Index += 1
}

Write-Host "Done: $OutputDir"
