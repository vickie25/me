<#
.SYNOPSIS
    PowerShell wrapper to activate a Conda environment and run a Python script.

.DESCRIPTION
    Tries to run `conda activate <env>` and execute the script with the activated environment.
    If activation is not available (Conda not initialized in PowerShell), it falls back to
    `conda run -n <env> python <script>` which works without `conda init`.

.EXAMPLE
    .\run_with_conda.ps1 -EnvName myenv

.PARAMETER EnvName
    Name of the conda environment to use. Defaults to 'base'.

.PARAMETER Script
    Path (relative to this wrapper) of the Python script to run. Defaults to '.\backdate_script.py'.
#>

param(
    [string]$EnvName = "base",
    [string]$Script = ".\backdate_script.py"
)

# Resolve script path relative to this wrapper
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$scriptPath = Join-Path $scriptDir $Script

Write-Host "Running '$scriptPath' with conda environment '$EnvName'..." -ForegroundColor Cyan

# Try to locate conda.exe (common user install locations) otherwise fall back to 'conda' in PATH
$condaCmd = 'conda'
$possible = @("$env:USERPROFILE\anaconda3\Scripts\conda.exe", "$env:USERPROFILE\miniconda3\Scripts\conda.exe")
foreach ($p in $possible) { if (Test-Path $p) { $condaCmd = $p; break } }

# First try: activate (works when conda is initialized for PowerShell)
try {
    Write-Host "Attempting 'conda activate $EnvName' using '$condaCmd'..." -ForegroundColor Yellow
    & $condaCmd activate $EnvName 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Activated '$EnvName'. Running python..." -ForegroundColor Green
        python $scriptPath
        exit $LASTEXITCODE
    }
    else {
        Write-Host "Activation failed or not initialised. Falling back to 'conda run'..." -ForegroundColor Yellow
        & $condaCmd run -n $EnvName --no-capture-output python $scriptPath
        exit $LASTEXITCODE
    }
}
catch {
    Write-Host "Error while trying 'conda activate' (or command not available). Using 'conda run' fallback..." -ForegroundColor Yellow
    & $condaCmd run -n $EnvName --no-capture-output python $scriptPath
    exit $LASTEXITCODE
}