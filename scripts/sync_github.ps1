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
$secretPatterns = @(
  '(?<![A-Za-z0-9_])["'']?(AppSecret|OPENAI_API_KEY|WECHAT_APP_SECRET|WECHAT_ACCESS_TOKEN|api_key|password|secret|token)["'']?\s*[:=]\s*["''][^"'']{8,}["'']',
  '(?<![A-Za-z0-9_])(AppSecret|OPENAI_API_KEY|WECHAT_APP_SECRET|WECHAT_ACCESS_TOKEN|api_key|password|secret|token)\s*=\s*\S{8,}'
)
$secretScan = git diff --cached | Select-String -Pattern $secretPatterns -CaseSensitive:$false
if ($secretScan) {
  git reset
  Write-Error "Potential secret found in staged diff. Review before committing."
}

if (-not $Message) {
  $Message = "chore: add daily AI draft pipeline update"
}

git commit -m $Message
git push origin main
