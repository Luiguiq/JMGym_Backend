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
#   SECRET_KEY=tu_secreto_jwt
#   ALGORITHM=HS256
#   ACCESS_TOKEN_EXPIRE_MINUTES=60

# 5. Crear la base de datos
mysql -u root -p < app/scripts/db.sql

# 6. (Opcional) Insertar datos de prueba
python seed.py

# 7. (Opcional) Insertar datos de prueba para fidelización (Bronce/Plata/Oro)
python insertar_test_fidelizacion.py

# 8. Iniciar el servidor
uvicorn app.main:app --reload
```

> **IMPORTANTE:** El `password_hash` usa el formato `pbkdf2-sha256`. No uses `SHA2()` plano.

## Migraciones manuales

Cuando se agregan nuevas columnas a los modelos, ejecutar:

```bash
python -c "
from app.core.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    conn.execute(text('ALTER TABLE reservas ADD COLUMN es_clase_gratis BOOLEAN DEFAULT FALSE'))
    conn.commit()
"
```

## Documentación interactiva

Una vez iniciado el servidor:

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
| POST | /classes | Crear clase | Sí (admin) |
| PUT | /classes/{id} | Actualizar clase | Sí (admin) |
| DELETE | /classes/{id} | Eliminar clase | Sí (admin) |
| POST | /reservations | Crear reserva | Sí |
| GET | /reservations/me | Mis reservas | Sí |
| GET | /reservations | Todas las reservas | Sí (admin) |
| PATCH | /reservations/{id}/cancel | Cancelar reserva | Sí |
| PATCH | /reservations/{id}/pay | Marcar como pagada | Sí (admin) |
| POST | /reservations/{id}/refund | Solicitar reembolso | Sí |
| POST | /reservations/{id}/refund/cancel | Cancelar solicitud reembolso | Sí |
| PATCH | /reservations/{id}/refund/approve | Aprobar reembolso | Sí (admin) |
| GET | /fidelizacion/me | Mi información de fidelización | Sí |
| POST | /payments/yape/initiate | Iniciar pago Yape | Sí |
| POST | /payments/yape/confirm | Confirmar pago Yape | Sí |
| GET | /payments/yape/admin | Listar pagos Yape | Sí (admin) |
| GET | /admin/stats | Estadísticas del panel | Sí (admin) |

### Fidelización - Campos de respuesta

```json
{
  "horas_mes": 24.0,
  "horas_base": 20.0,
  "horas_bono": 4.0,
  "nivel": "ORO",
  "descuento_porcentaje": 20,
  "acompanante_gratis": true,
  "clases_gratis_restantes": 2,
  "siguiente_nivel": null,
  "horas_restantes": 0
}
```

- `horas_base`: horas del mes actual
- `horas_bono`: excedente del mes anterior (>30h se arrastran)
- `horas_mes`: total (base + bono)
- `clases_gratis_restantes`: clases gratis disponibles para nivel Oro (máx 2/mes)

### Crear reserva - Campos adicionales

```json
{
  "classId": 1,
  "seatId": 1,
  "paymentMethod": "EFECTIVO",
  "aplicaClaseGratis": true
}
```

## Estructura del proyecto

```
app/
├── core/              # Configuración, BD
├── enum/              # Enumeraciones (estados, métodos, etc.)
├── models/            # SQLAlchemy models (14 tablas)
├── repositories/      # Capa de acceso a datos
├── routes/            # FastAPI routers
├── schemas/           # Pydantic schemas
├── services/          # Lógica de negocio
│   ├── fidelizacion_service.py   # Cálculo de niveles, bono de horas, clases gratis
│   ├── reservation_service.py    # Creación/cancelación de reservas
│   ├── notification_service.py   # Notificaciones + WebSocket
│   └── ...
├── security.py        # JWT, hash de contraseñas
└── main.py            # Punto de entrada
```

## Credenciales por defecto

| Rol | Email | Contraseña | Nivel fidelización |
|-----|-------|------------|-------------------|
| Administrador | admin@jmgym.com | admin123 | - |
| Usuario (seed) | erick@gmail.com | 123456 | BRONCE |
| Usuario (seed) | maria@gmail.com | 123456 | BRONCE |
| Usuario (seed) | carlos@gmail.com | 123456 | BRONCE |
| Usuario (seed) | lucia@gmail.com | 123456 | BRONCE |
| **Test Bronce** | **bronce@test.com** | **test123** | **BRONCE (0% dto)** |
| **Test Plata** | **plata@test.com** | **test123** | **PLATA (10% dto)** |
| **Test Oro** | **oro@test.com** | **test123** | **ORO (20% dto + 2 clases gratis)** |

## Sistema de fidelización

### Niveles

| Nivel | Horas/mes | Descuento | Beneficios |
|-------|-----------|-----------|------------|
| BRONCE | 0-7h | 0% | Sorteos mensuales |
| PLATA | 8-20h | 10% | Sorteos exclusivos, regalo sorpresa |
| ORO | 21h+ | 20% | **2 clases gratis/mes**, regalo premium, sorteos oro |

### Bono de horas

Si un usuario acumula **más de 30 horas** en un mes, el excedente se arrastra al mes siguiente:

```
Ejemplo:
- Julio: 35h → se muestra 30h + 5h de bono
- Agosto: 10h + 5h bono = 15h → Nivel PLATA
```

## Notas

- Las tablas se crean automáticamente al iniciar (`Base.metadata.create_all`).
- Las nuevas columnas (ej: `es_clase_gratis`) deben agregarse manualmente con ALTER TABLE.
- El WebSocket (socket.io) está en el puerto 8000 junto con la API HTTP.
- Los hash de contraseña usan `pbkdf2_sha256`.
