#!/bin/bash
echo "Iniciando configuración de SISSOT..."

# Crear entorno virtual
python -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Archivo .env creado desde .env.example"
fi

# Crear directorio de reportes
mkdir -p reports

echo "Configuración completada. Para iniciar el servidor: python main.py"
