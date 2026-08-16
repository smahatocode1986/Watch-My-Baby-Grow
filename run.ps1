$ErrorActionPreference = "Stop"
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPython = Join-Path $ProjectDir ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $VenvPython)) {
    $Python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $Python -or $Python.Source -like "*WindowsApps*") {
        Write-Host "Python is not installed (the Windows Store alias does not count)." -ForegroundColor Yellow
        Write-Host "Install Python 3.11+ from https://www.python.org/downloads/windows/"
        Write-Host "During setup, enable 'Add python.exe to PATH', then run this script again."
        exit 1
    }
    & $Python.Source -m venv (Join-Path $ProjectDir ".venv")
}

& $VenvPython -m pip install --disable-pip-version-check -r (Join-Path $ProjectDir "requirements.txt")
& $VenvPython -m streamlit run (Join-Path $ProjectDir "app.py")
