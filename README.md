# SISSOT - Sistema de Salud Sotillo

Sistema integral de gestión de salud municipal para la Dirección de Salud de la Alcaldía del Municipio Sotillo. Permite el registro de pacientes, seguimiento clínico y monitoreo epidemiológico en tiempo real.

## Características

- 🏥 **Registro de Pacientes**: Gestión completa de fichas médicas.
- 📊 **Dashboard Epidemiológico**: Visualización de estadísticas y tendencias de patologías.
- 🗺️ **Mapa de Incidencia**: Monitoreo geográfico por comunas.
- ⚠️ **Alertas Inteligentes**: Detección automática de brotes epidemiológicos.
- 📄 **Reportes PDF**: Generación de fichas técnicas descargables.
- 🌓 **Modo Oscuro**: Interfaz moderna y adaptable.

## Requisitos

- Python 3.9+
- SQLite (incluido por defecto)

## Instalación

1. Clonar el repositorio:
   ```bash
   git clone <url-del-repositorio>
   cd salud1
   ```

2. Crear un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Ejecución

Para iniciar el servidor en modo desarrollo:
```bash
python main.py
```
El sistema estará disponible en `http://localhost:8000`.

## Despliegue con Docker

1. Construir la imagen:
   ```bash
   docker build -t sissot-app .
   ```

2. Ejecutar el contenedor:
   ```bash
   docker run -d -p 8000:8000 --name sissot sissot-app
   ```

## Estructura del Proyecto

- `main.py`: Punto de entrada de la API (FastAPI).
- `database.py`: Modelos de base de datos y configuración de SQLAlchemy.
- `static/`: Frontend (HTML, CSS, JS).
- `reports/`: Directorio temporal para la generación de PDFs.
- `salud_sotillo.db`: Base de datos SQLite.

---
© 2026 Dirección de Salud - Alcaldía de Sotillo
