param(
    [string]$PagesRepoPath = (Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) "mlb-the-show-progress")
)

$ErrorActionPreference = "Stop"
$PagesRepoPath = [System.IO.Path]::GetFullPath($PagesRepoPath)
$GitDirectory = Join-Path $PagesRepoPath ".git"
if (-not (Test-Path -LiteralPath $GitDirectory)) {
    throw "Pages repository not found at $PagesRepoPath. Clone ib6897976-cloud/MLBTheShow26-Decomp there first."
}

$Remote = (& git -C $PagesRepoPath remote get-url origin).Trim()
if ($LASTEXITCODE -ne 0 -or $Remote -notmatch "github\.com[:/]ib6897976-cloud/MLBTheShow26-Decomp(?:\.git)?$") {
    throw "Refusing to publish: origin is not the public dashboard repository (ib6897976-cloud/MLBTheShow26-Decomp): $Remote"
}

& python (Join-Path $PSScriptRoot "export_progress_site.py")
if ($LASTEXITCODE -ne 0) { throw "Dashboard export failed." }

$Source = Join-Path $PSScriptRoot "progress_site"
Copy-Item -LiteralPath (Join-Path $Source "index.html") -Destination (Join-Path $PagesRepoPath "index.html") -Force
Copy-Item -LiteralPath (Join-Path $Source ".nojekyll") -Destination (Join-Path $PagesRepoPath ".nojekyll") -Force
Copy-Item -LiteralPath (Join-Path $Source "progress.svg") -Destination (Join-Path $PagesRepoPath "progress.svg") -Force
$DataDestination = Join-Path $PagesRepoPath "data"
New-Item -ItemType Directory -Force -Path $DataDestination | Out-Null
Get-ChildItem -LiteralPath (Join-Path $Source "data") -File -Filter "*.json" |
    Copy-Item -Destination $DataDestination -Force

& git -C $PagesRepoPath add -A
if ($LASTEXITCODE -ne 0) { throw "Could not stage dashboard files." }
& git -C $PagesRepoPath diff --cached --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Output "Dashboard snapshot is already current."
    exit 0
}
if ($LASTEXITCODE -ne 1) { throw "Could not inspect staged dashboard changes." }

& git -C $PagesRepoPath -c user.name="Codex" -c user.email="codex@users.noreply.github.com" commit -m "Update progress dashboard snapshot"
if ($LASTEXITCODE -ne 0) { throw "Could not commit dashboard snapshot." }
& git -C $PagesRepoPath push origin main
if ($LASTEXITCODE -ne 0) { throw "Could not publish dashboard snapshot." }
