# JMGym Backend

API REST para el sistema de reservas de clases de gimnasio.

## Requisitos

- Python 3.10+
- MySQL 8.0+

## Instalación

```bash
# 1. Clonar el repositorio
git clone <repo-url>
cd JMGym_Backend

# 2. Crear y activar entorno virtual
python -m venv venv

# Windows
.\venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
# Copiar .env.example a .env y editar con tus datos:
#   DB_HOST=localhost
#   DB_PORT=3306
#   DB_USER=root
#   DB_PASSWORD=tu_contraseña
#   DB_NAME=JMGym

# 5. Crear la base de datos
# Opción A: Copiar y pegar el contenido de app/scripts/db.sql en tu cliente MySQL
# Opción B: Ejecutar directamente:
mysql -u root -p < app/scripts/db.sql

# 6. (Opcional) Insertar datos de prueba con seed.py
python seed.py

# 7. Iniciar el servidor
uvicorn app.main:app --reload
```

> **IMPORTANTE:** El `password_hash` del admin en `db.sql` usa el formato `pbkdf2-sha256`. No lo reemplaces con `SHA2()` plano o el login de administradores fallará con error 500.

## Documentación interactiva

Una vez iniciado el servidor, abre:

- Swagger UI: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

## Endpoints principales

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| POST | /auth/register | Registrar usuario | No |
| POST | /auth/login | Iniciar sesión usuario | No |
| POST | /auth/admin/login | Iniciar sesión administrador | No |
| POST | /auth/admin/register | Registrar administrador | No |
| GET | /classes/today | Clases de hoy | No |
| GET | /classes | Todas las clases activas | No |
| GET | /classes/{id} | Detalle de clase | No |
| POST | /classes | Crear clase | No |
| PUT | /classes/{id} | Actualizar clase | No |
| DELETE | /classes/{id} | Eliminar clase | No |
| POST | /reservations | Crear reserva | Sí |
| GET | /reservations/me | Mis reservas | Sí |
| GET | /reservations | Todas las reservas | No |
| DELETE | /reservations/{id} | Cancelar reserva | No |
| POST | /payments | Crear pago | No |
| GET | /payments/pending | Pagos pendientes | No |
| PATCH | /payments/{id}/confirm | Confirmar pago | No |
| GET | /admin/stats | Estadísticas del panel | No |

## Credenciales por defecto

| Rol | Email | Contraseña |
|-----|-------|------------|
| Administrador | admin@jmgym.com | admin123 |
| Usuario (seed) | juan@email.com | 123456 |
