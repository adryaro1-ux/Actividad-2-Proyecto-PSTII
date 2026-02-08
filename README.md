# DolarSync - Sistema de Monitoreo y Gestion de Siniestros AMP (PST)

Este proyecto es una herramienta de gestión financiera diseñada para el **Proyecto Socio Tecnológico (PST)**, enfocada en la centralización y auditoría de tasas cambiarias para el sector seguros (**Seguros Horizonte S.A**).

# Características principales
* **Arquitectura:** Flask (Python) con SQLAlchemy (ORM).
* **Base de Datos:** MySQL con 6 campos maestros (Auditoría completa).
* **Seguridad:** Protección de rutas mediante `@login_required` y manejo de variables de entorno.
* **Interfaz:** Diseño moderno con Glassmorphism y Jinja2, optimizado con Bootstrap 5.
* **Lógica de Auditoría:** Inmutabilidad de datos históricos (los registros de tasas no se eliminan para preservar la trazabilidad financiera).

## 🛠️ Instalación y Configuración

Sigue estos pasos para correr el proyecto localmente:

1. **Clonar el repositorio:**
   ```bash
   git clone [TU_URL_DE_GITHUB]
   cd dolar-sync
