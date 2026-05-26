# TerraVal — Instalador para Windows (PowerShell)
# Uso: iwr https://raw.githubusercontent.com/leandropitol/terraval/main/install.ps1 | iex

Write-Host ""
Write-Host "🌾  Instalando TerraVal..." -ForegroundColor Green
Write-Host ""

# Verificar Python
$python = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python (\d+)\.(\d+)") {
            $major = [int]$Matches[1]
            $minor = [int]$Matches[2]
            if ($major -ge 3 -and $minor -ge 10) {
                $python = $cmd
                Write-Host "   $ver encontrado ✓" -ForegroundColor Cyan
                break
            }
        }
    } catch {}
}

if (-not $python) {
    Write-Host "❌  Python 3.10+ não encontrado." -ForegroundColor Red
    Write-Host "   Instale em: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Instalar
$uvAvailable = $null -ne (Get-Command uv -ErrorAction SilentlyContinue)

if ($uvAvailable) {
    Write-Host "📦  Instalando via uv..." -ForegroundColor Yellow
    uv pip install git+https://github.com/leandropitol/terraval.git
} else {
    Write-Host "📦  Instalando via pip..." -ForegroundColor Yellow
    & $python -m pip install git+https://github.com/leandropitol/terraval.git
}

Write-Host ""
Write-Host "✅  TerraVal instalado com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "   Configurar:  " -NoNewline; Write-Host "terraval setup" -ForegroundColor Yellow
Write-Host "   Iniciar:     " -NoNewline; Write-Host "terraval" -ForegroundColor Yellow
Write-Host ""
