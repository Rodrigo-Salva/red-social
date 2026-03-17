# 🚀 Red Social API - Backend Elite (Enterprise Edition)

Una API de red social extremadamente robusta, segura y escalable construida con **FastAPI**. Diseñada para soportar flujos de trabajo profesionales, seguridad de nivel enterprise y una arquitectura modular fácil de mantener.

## ✨ Características Destacadas

### 🔒 Seguridad Avanzada
- **Autenticación Multi-factor (2FA):** Soporte completo para TOTP (Google Authenticator) con generación de códigos QR.
- **Gestión de Sesiones Activas:** Rastreo de dispositivos por JTI y capacidad de revocar sesiones remotamente.
- **Rate Limiting:** Protección inteligente contra fuerza bruta y spam.
- **JWT Robusto:** Hashing de contraseñas con Bcrypt y tokens de acceso con tiempos de expiración configurables.

### 📱 Core de Red Social
- **Mensajería Privada (DMs):** Sistema de chat persistente con soporte para historial.
- **Feed dinámico:** Sistema de publicaciones, comentarios y seguidos.
- **Multimedia:** Gestión de imágenes de perfil y fotos en publicaciones (Storage local/S3 ready).
- **Notificaciones:** Historial persistente de interacciones.

### 🛠️ Administración y Datos
- **Borrado Lógico (Soft Deletes):** Integridad referencial protegida; los datos no desaparecen, se archivan.
- **Moderación:** Sistema de reportes de contenido con Dashboard para administradores.
- **Búsqueda Avanzada:** Filtros por popularidad, fechas y tipos de contenido.
- **Paginación Pro:** Respuestas estandarizadas para integración fácil con Next.js/Angular.

---

## 🏗️ Arquitectura del Proyecto

El proyecto utiliza una **Arquitectura Modular (Clean-ish)** para garantizar la escalabilidad:

```text
app/
├── core/      # Configuración (.env), Seguridad (JWT), Rate Limit.
├── api/       # Endpoints (Rutas) divididos por versiones y módulos.
├── models/    # Modelos de SQLAlchemy (Base de Datos).
├── schemas/   # Esquemas de Pydantic (Validación y Serialización).
├── crud/      # Lógica de acceso a datos (Create, Read, Update, Delete).
└── db/        # Conexión y sesión de Base de Datos.
```

---

## 🚀 Instalación y Uso

### 🐳 Opción A: Docker (Recomendado)
Ideal para producción o si no quieres configurar bases de datos locales.

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/Rodrigo-Salva/red-social.git
    cd red-social
    ```
2.  **Levanta el stack:**
    ```bash
    docker-compose up --build
    ```
    La API estará en `http://localhost:8000` y la documentación interactiva en `http://localhost:8000/docs`.

### 🐍 Opción B: Local (Manual)
1.  **Crea un entorno virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # o venv\Scripts\activate en Windows
    ```
2.  **Instala dependencias:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configura el `.env`:**
    Copia el archivo de ejemplo y rellena tus credenciales (DB, Email, etc.).
4.  **Inicia el servidor:**
    ```bash
    fastapi dev main.py
    ```

---

## 🧪 Pruebas Automatizadas

Mantenemos una alta cobertura para asegurar que los cambios no rompan la seguridad.

```bash
# Ejecutar todos los tests
PYTHONPATH=. venv/bin/pytest

# Test específicos de seguridad
PYTHONPATH=. venv/bin/pytest tests/test_2fa.py tests/test_sessions.py
```

---

## 📝 Documentación de la API
Una vez iniciada la aplicación, puedes acceder a:
-   **Swagger UI:** `http://localhost:8000/docs` (Interactiva)
-   **ReDoc:** `http://localhost:8000/redoc` (Detallada)

---

## 🤝 Contribuir
¡Las contribuciones son bienvenidas! Siéntete libre de abrir un Issue o enviar un Pull Request.

---
**Desarrollado con ❤️ para Rodrigo-Salva**
