param(
  [string]$Message = ""
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $repoRoot

$status = git status --short
if (-not $status) {
  Write-Host "No changes to sync."
  exit 0
}

git add .

$staged = git diff --cached --name-only
$secretScan = git diff --cached | Select-String -Pattern "(AppSecret|OPENAI_API_KEY|api_key|password|secret|token)\s*[:=]" -CaseSensitive:$false
if ($secretScan) {
  git reset
  Write-Error "Potential secret found in staged diff. Review before committing."
}

if (-not $Message) {
  $Message = "chore: add daily AI draft pipeline update"
}

git commit -m $Message
git push origin main
