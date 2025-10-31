# Deploy FastAPI API to Hugging Face Spaces (Docker)
# Usage (PowerShell):
#   $env:HF_TOKEN = "<hf_token>"
#   $env:HF_USERNAME = "<hf_username>"
#   $env:HF_SPACE = "samarth-api"   # or any name you like
#   .\deploy\deploy_hf.ps1

param()

function Fail($msg) {
  Write-Error $msg
  exit 1
}

if (-not $env:HF_TOKEN) { Fail "HF_TOKEN env var is required." }
if (-not $env:HF_USERNAME) { Fail "HF_USERNAME env var is required." }
if (-not $env:HF_SPACE) { Fail "HF_SPACE env var is required." }

# Ensure venv is active or python is on PATH
Write-Host "[1/6] Checking huggingface-cli..."
$hfCli = Join-Path (Get-Location) ".venv\Scripts\huggingface-cli.exe"
if (-not (Test-Path $hfCli)) { $hfCli = "huggingface-cli" }

Write-Host "[2/6] Logging into Hugging Face non-interactively..."
& $hfCli login --token $env:HF_TOKEN --add-to-git-credential | Out-Null
if ($LASTEXITCODE -ne 0) { Fail "Hugging Face login failed." }

Write-Host "[3/6] Creating Space (if not exists): $($env:HF_USERNAME)/$($env:HF_SPACE)"
& $hfCli repo create "$env:HF_USERNAME/$env:HF_SPACE" --type space --space-sdk docker -y | Out-Null

Write-Host "[4/6] Ensuring git repository is initialized..."
if (-not (Test-Path ".git")) {
  git init | Out-Null
  git checkout -b main | Out-Null
}

Write-Host "[5/6] Adding HF remote..."
$remoteUrl = "https://huggingface.co/spaces/$($env:HF_USERNAME)/$($env:HF_SPACE)"
$remotes = git remote
if ($remotes -notmatch "^hf$") {
  git remote add hf $remoteUrl
} else {
  git remote set-url hf $remoteUrl
}

Write-Host "[6/6] Committing and pushing to HF Spaces..."
git add -A
git commit -m "Deploy to HF Spaces" | Out-Null
git push hf HEAD:main -f

Write-Host "\nDone. Space URL: https://$($env:HF_USERNAME)-$($env:HF_SPACE).hf.space"
Write-Host "Test endpoints: /, /db/ping, /query"
