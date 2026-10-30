# Verifies the provenance of every photograph the public website hotlinks.
#
# For each Wikimedia Commons page id below it asks the Commons API for the author,
# licence, description and file-page URL, then requests every thumbnail width the
# site uses and records the HTTP status.  The result is written to
# docs/evidence/images/provenance.json, which frontend/app/utils/images.ts and
# docs/product/image-manifest.md are written from.  Nothing is invented: a value the
# API does not return stays empty and fails the check.
#
#   powershell -File scripts/verify-image-provenance.ps1
[CmdletBinding()]
param(
    [int[]]$Widths = @(500, 960, 1280)
)

$ErrorActionPreference = 'Stop'
$headers = @{ 'User-Agent' = 'JjengaCodeSite/0.1 (hello@jengacode.tech)' }
$images = [ordered]@{
    hero           = 56792625
    school_term    = 184429425
    saturday_club  = 64277626
    holiday_camp   = 57424557
    robot          = 3494929
}

function Get-Plain([string]$html) {
    return (($html -replace '<[^>]+>', '') -replace '\s+', ' ').Trim()
}

$results = [ordered]@{}
foreach ($key in $images.Keys) {
    $id = $images[$key]
    $uri = "https://commons.wikimedia.org/w/api.php?action=query&pageids=$id&prop=imageinfo|info&inprop=url&iiprop=url|size|mime|extmetadata&format=json"
    $response = Invoke-RestMethod -Uri $uri -Headers $headers -TimeoutSec 60
    $page = $response.query.pages.$id
    $info = $page.imageinfo[0]
    $meta = $info.extmetadata
    $original = ($info.url -split '\?')[0]
    # thumb path: .../commons/<a>/<ab>/<name>  ->  .../commons/thumb/<a>/<ab>/<name>/<w>px-<name>
    $match = [regex]::Match($original, '^(https://upload\.wikimedia\.org/wikipedia/commons)/(\w/\w\w)/(.+)$')
    $thumbs = [ordered]@{}
    foreach ($width in $Widths) {
        $name = $match.Groups[3].Value
        $thumbUrl = "$($match.Groups[1].Value)/thumb/$($match.Groups[2].Value)/$name/${width}px-$name"
        try {
            $request = Invoke-WebRequest -Uri $thumbUrl -Headers $headers -UseBasicParsing -TimeoutSec 60
            $status = [int]$request.StatusCode
            $bytes = $request.RawContentLength
        } catch {
            $status = [int]$_.Exception.Response.StatusCode
            $bytes = 0
        }
        $thumbs["$width"] = [ordered]@{ url = $thumbUrl; status = $status; bytes = $bytes }
        Start-Sleep -Milliseconds 400
    }
    $results[$key] = [ordered]@{
        pageId      = $id
        title       = $page.title
        filePage    = $page.canonicalurl
        author      = Get-Plain $meta.Artist.value
        license     = $meta.LicenseShortName.value
        licenseUrl  = $meta.LicenseUrl.value
        description = Get-Plain $meta.ImageDescription.value
        width       = $info.width
        height      = $info.height
        mime        = $info.mime
        original    = $original
        thumbnails  = $thumbs
    }
    Write-Host ("{0,-14} {1} | {2} | {3}" -f $key, $page.title, $meta.LicenseShortName.value, (Get-Plain $meta.Artist.value))
}

$target = Join-Path (Split-Path $PSScriptRoot -Parent) 'docs\evidence\images'
New-Item -ItemType Directory -Force $target | Out-Null
$json = $results | ConvertTo-Json -Depth 6
[System.IO.File]::WriteAllText((Join-Path $target 'provenance.json'), $json, (New-Object System.Text.UTF8Encoding($false)))
$bad = $results.Values | ForEach-Object { $_.thumbnails.Values } | Where-Object { $_.status -ne 200 }
if ($bad) { throw "Some thumbnails did not return HTTP 200." }
Write-Host "All thumbnails returned HTTP 200. Wrote provenance.json"
