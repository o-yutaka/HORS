# HROS — GitHub push flow
# Run from repository root: .\scripts\github-push.ps1
# Optional: .\scripts\github-push.ps1 -Owner "your-github-username" -Repo "HROS" -Visibility "private"

param(
    [string]$Owner = "",
    [string]$Repo = "HROS",
    [ValidateSet("public", "private")]
    [string]$Visibility = "private"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

function Require-Git {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        throw "git is not installed or not on PATH."
    }
}

function Require-Gh {
    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        return $false
    }
    return $true
}

Require-Git

$branch = git branch --show-current
if (-not $branch) {
    throw "No current branch. Create a commit before pushing."
}

Write-Host "Repository: $Root"
Write-Host "Branch: $branch"

if (-not $Owner) {
    $Owner = Read-Host "GitHub owner (username or org)"
}

$remoteUrl = "https://github.com/$Owner/$Repo.git"
$remoteSsh = "git@github.com:$Owner/$Repo.git"

$existingRemote = git remote get-url origin 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Adding origin: $remoteUrl"
    git remote add origin $remoteUrl
} else {
    Write-Host "origin already set: $existingRemote"
    $useExisting = Read-Host "Use existing origin? [Y/n]"
    if ($useExisting -match "^[Nn]") {
        git remote set-url origin $remoteUrl
        Write-Host "Updated origin to $remoteUrl"
    }
}

if (Require-Gh) {
  Write-Host "GitHub CLI detected."
  $create = Read-Host "Create GitHub repo '$Owner/$Repo' via gh? [Y/n]"
  if ($create -notmatch "^[Nn]") {
    gh auth status
  if ($LASTEXITCODE -ne 0) { throw "Run: gh auth login" }
    gh repo create "$Owner/$Repo" --$Visibility --source=. --remote=origin --push
    Write-Host "Done. Remote: https://github.com/$Owner/$Repo"
    exit 0
  }
}

Write-Host ""
Write-Host "Manual push flow:"
Write-Host "  1. Create empty repo on GitHub: https://github.com/new"
Write-Host "     Name: $Repo"
Write-Host "     Do NOT add README, .gitignore, or license (this repo already has them)."
Write-Host "  2. Push:"
Write-Host "     git push -u origin $branch"
Write-Host ""
Write-Host "SSH alternative remote:"
Write-Host "  git remote set-url origin $remoteSsh"
Write-Host "  git push -u origin $branch"

$pushNow = Read-Host "Push now to origin/$branch? [Y/n]"
if ($pushNow -notmatch "^[Nn]") {
    git push -u origin $branch
    Write-Host "Pushed to origin/$branch"
}
