$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    python -m PyInstaller --noconfirm --distpath dist MDtoDOCX.spec
    if ($LASTEXITCODE -ne 0) { throw 'Build failed' }
} finally {
    Pop-Location
}
