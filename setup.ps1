Write-Host "Iniciando configuración de SISSOT..." -ForegroundColor Cyan

# Crear entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env si no existe
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host "Archivo .env creado desde .env.example" -ForegroundColor Yellow
}

# Crear directorio de reportes
if (-not (Test-Path reports)) {
    New-Item -ItemType Directory -Path reports
}

Write-Host "Configuración completada. Para iniciar el servidor: python main.py" -ForegroundColor Green
