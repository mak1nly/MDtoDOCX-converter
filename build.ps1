param([string]$InstallerCompiler)
$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    python -m PyInstaller --noconfirm --distpath dist MDtoDOCX.spec
    if ($LASTEXITCODE -ne 0) { throw 'Build failed' }
    if ($InstallerCompiler) {
        & $InstallerCompiler installer.iss
        if ($LASTEXITCODE -ne 0) { throw 'Installer build failed' }
    }
} finally {
    Pop-Location
}
