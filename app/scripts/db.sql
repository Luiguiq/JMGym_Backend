-- =====================================================
-- JMGym Database v2.0
-- Sistema de Reservas de Clases de Gimnasio
-- =====================================================

CREATE DATABASE IF NOT EXISTS JMGym
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE JMGym;

-- =====================================================
-- ADMINISTRADORES
-- =====================================================

CREATE TABLE administradores (
    id_admin            INT AUTO_INCREMENT PRIMARY KEY,
    nombre              VARCHAR(100)  NOT NULL,
    correo_institucional VARCHAR(120) UNIQUE NOT NULL,
    password_hash       VARCHAR(255)  NOT NULL,
    estado              ENUM('ACTIVO','INACTIVO') DEFAULT 'ACTIVO',
    fecha_creacion      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- USUARIOS CLIENTES
-- =====================================================

CREATE TABLE usuarios (
    id_usuario      INT AUTO_INCREMENT PRIMARY KEY,
    nombre_completo VARCHAR(150) NOT NULL,
    dni             VARCHAR(15)  UNIQUE NOT NULL,
    correo          VARCHAR(120) UNIQUE NOT NULL,
    telefono        VARCHAR(20),
    foto_perfil     VARCHAR(255),
    password_hash   VARCHAR(255) NOT NULL,
    estado          ENUM('ACTIVO','BLOQUEADO') DEFAULT 'ACTIVO',
    fecha_registro  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- AUDITORÍA DE USUARIOS
-- =====================================================

CREATE TABLE usuarios_auditoria (
    id_auditoria    INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario      INT NOT NULL,
    id_admin        INT NOT NULL,
    accion          ENUM('BLOQUEO','DESBLOQUEO','EDICION_PERFIL','RESET_PASSWORD') NOT NULL,
    motivo          TEXT,
    detalle         TEXT,
    fecha           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_admin)   REFERENCES administradores(id_admin)
);

-- =====================================================
-- GÉNEROS / TIPOS DE CLASES
-- =====================================================

CREATE TABLE generos_clase (
    id_genero       INT AUTO_INCREMENT PRIMARY KEY,
    nombre_genero   VARCHAR(100) NOT NULL UNIQUE,
    descripcion     TEXT,
    imagen          VARCHAR(255),
    estado          ENUM('ACTIVO','INACTIVO') DEFAULT 'ACTIVO'
);

-- =====================================================
-- INSTRUCTORES
-- =====================================================

CREATE TABLE instructores (
    id_instructor       INT AUTO_INCREMENT PRIMARY KEY,
    nombre_completo     VARCHAR(150) NOT NULL,
    telefono            VARCHAR(20),
    especialidad        VARCHAR(120),
    biografia           TEXT,
    foto                VARCHAR(255),
    video_presentacion  VARCHAR(255),
    estado              ENUM('ACTIVO','INACTIVO') DEFAULT 'ACTIVO',
    fecha_registro      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- GÉNEROS POR INSTRUCTOR (muchos a muchos)
-- =====================================================

CREATE TABLE instructor_generos (
    id_instructor   INT NOT NULL,
    id_genero       INT NOT NULL,
    PRIMARY KEY (id_instructor, id_genero),
    FOREIGN KEY (id_instructor) REFERENCES instructores(id_instructor) ON DELETE CASCADE,
    FOREIGN KEY (id_genero)     REFERENCES generos_clase(id_genero)    ON DELETE CASCADE
);

-- =====================================================
-- HORARIOS DE INSTRUCTORES
-- =====================================================

CREATE TABLE instructor_horarios (
    id_horario      INT AUTO_INCREMENT PRIMARY KEY,
    id_instructor   INT NOT NULL,
    dia_semana      ENUM('LUNES','MARTES','MIERCOLES','JUEVES','VIERNES','SABADO','DOMINGO') NOT NULL,
    hora_inicio     TIME,
    hora_fin        TIME,
    disponible      BOOLEAN DEFAULT TRUE,
    UNIQUE KEY uq_instructor_dia (id_instructor, dia_semana),
    FOREIGN KEY (id_instructor) REFERENCES instructores(id_instructor) ON DELETE CASCADE
);

-- =====================================================
-- CLASES
-- =====================================================

CREATE TABLE clases (
    id_clase                    INT AUTO_INCREMENT PRIMARY KEY,
    nombre_clase                VARCHAR(120) NOT NULL,
    id_genero                   INT NOT NULL,
    id_instructor               INT NOT NULL,
    descripcion                 TEXT,
    intensidad                  ENUM('BAJA','MEDIA','ALTA') DEFAULT 'MEDIA',
    reglas_vestimenta           TEXT,
    duracion_minutos            INT  NOT NULL,
    fecha                       DATE NOT NULL,
    hora_inicio                 TIME NOT NULL,
    hora_fin                    TIME NOT NULL,
    precio                      DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    cupos_totales               INT DEFAULT 40,
    cupos_disponibles           INT DEFAULT 40,
    alumnos_minimos             INT DEFAULT 5,
    fecha_limite_cancelacion    DATETIME,
    imagen_clase                VARCHAR(255),
    estado                      ENUM('ACTIVA','CANCELADA','COMPLETA','FINALIZADA') DEFAULT 'ACTIVA',
    motivo_cancelacion          TEXT,
    fecha_creacion              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_genero)     REFERENCES generos_clase(id_genero),
    FOREIGN KEY (id_instructor) REFERENCES instructores(id_instructor)
);

-- =====================================================
-- ESPACIOS / ASIENTOS
-- =====================================================

CREATE TABLE espacios (
    id_espacio      INT AUTO_INCREMENT PRIMARY KEY,
    id_clase        INT NOT NULL,
    codigo_espacio  VARCHAR(10) NOT NULL,
    estado          ENUM('DISPONIBLE','OCUPADO','RESERVADO','EN_ESPERA') DEFAULT 'DISPONIBLE',
    UNIQUE KEY uq_clase_espacio (id_clase, codigo_espacio),
    FOREIGN KEY (id_clase) REFERENCES clases(id_clase) ON DELETE CASCADE
);

-- =====================================================
-- RESERVAS
-- =====================================================

CREATE TABLE reservas (
    id_reserva          INT AUTO_INCREMENT PRIMARY KEY,
    codigo_reserva      VARCHAR(30) UNIQUE NOT NULL,
    id_usuario          INT NOT NULL,
    id_clase            INT NOT NULL,
    id_espacio          INT NOT NULL,
    metodo_pago         ENUM('YAPE','EFECTIVO') NOT NULL,
    estado_pago         ENUM('PENDIENTE','PAGADO','VENCIDO','REEMBOLSADO') DEFAULT 'PENDIENTE',
    estado_reserva      ENUM('ACTIVA','CANCELADA','FINALIZADA') DEFAULT 'ACTIVA',
    monto               DECIMAL(10,2) NOT NULL,
    fecha_reserva       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_limite_pago   DATETIME,
    fecha_clase         DATE NOT NULL,
    qr_checkin          VARCHAR(255),
    FOREIGN KEY (id_usuario)  REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_clase)    REFERENCES clases(id_clase),
    FOREIGN KEY (id_espacio)  REFERENCES espacios(id_espacio),
    UNIQUE KEY uq_usuario_dia_activa (id_usuario, fecha_clase, estado_reserva)
);

-- =====================================================
-- HISTORIAL DE ESTADOS DE RESERVAS
-- =====================================================

CREATE TABLE reservas_historial_estados (
    id_historial             INT AUTO_INCREMENT PRIMARY KEY,
    id_reserva               INT NOT NULL,
    tipo_evento              VARCHAR(50) NOT NULL,
    estado_reserva_anterior  VARCHAR(50),
    estado_reserva_nuevo     VARCHAR(50),
    estado_pago_anterior     VARCHAR(50),
    estado_pago_nuevo        VARCHAR(50),
    descripcion              TEXT,
    fecha_hora               DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actor_tipo               VARCHAR(30),
    actor_id                 INT,
    INDEX idx_historial_reserva (id_reserva),
    INDEX idx_historial_fecha (fecha_hora),
    FOREIGN KEY (id_reserva) REFERENCES reservas(id_reserva) ON DELETE CASCADE
);

-- =====================================================
-- PAGOS
-- =====================================================

CREATE TABLE pagos (
    id_pago             INT AUTO_INCREMENT PRIMARY KEY,
    id_reserva          INT NOT NULL,
    metodo_pago         ENUM('YAPE','EFECTIVO') NOT NULL,
    estado              ENUM('PENDIENTE','CONFIRMADO','RECHAZADO','REEMBOLSADO') DEFAULT 'PENDIENTE',
    monto               DECIMAL(10,2) NOT NULL,
    codigo_operacion    VARCHAR(100),
    fecha_pago          DATETIME,
    qr_yape             VARCHAR(255),
    confirmado_por_admin INT,
    FOREIGN KEY (id_reserva)           REFERENCES reservas(id_reserva),
    FOREIGN KEY (confirmado_por_admin) REFERENCES administradores(id_admin)
);

-- =====================================================
-- CHECK-IN QR
-- =====================================================

CREATE TABLE checkin (
    id_checkin          INT AUTO_INCREMENT PRIMARY KEY,
    id_reserva          INT NOT NULL,
    fecha_checkin       DATETIME,
    estado              ENUM('PENDIENTE','VALIDADO') DEFAULT 'PENDIENTE',
    validado_por_admin  INT,
    FOREIGN KEY (id_reserva)           REFERENCES reservas(id_reserva),
    FOREIGN KEY (validado_por_admin)   REFERENCES administradores(id_admin)
);

-- =====================================================
-- NOTIFICACIONES
-- =====================================================

CREATE TABLE notificaciones (
    id_notificacion     INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario          INT NOT NULL,
    titulo              VARCHAR(150),
    mensaje             TEXT,
    tipo                ENUM(
        'RECORDATORIO','PAGO','PAGO_CONFIRMADO','CAMBIO_HORARIO',
        'CAMBIO_INSTRUCTOR','NUEVA_CLASE','CANCELACION','REEMBOLSO',
        'BLOQUEO_CUENTA','RESERVA_CONFIRMADA','RESERVA_CANCELADA',
        'CAMBIO_ESPACIO','NOTIFICACION_GENERAL'
    ),
    requiere_respuesta  BOOLEAN DEFAULT FALSE,
    respuesta_usuario   ENUM('ACEPTADO','CANCELADO') DEFAULT NULL,
    fecha_respuesta     DATETIME DEFAULT NULL,
    leido               BOOLEAN DEFAULT FALSE,
    fecha_envio         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id_reserva          INT DEFAULT NULL,
    id_clase            INT DEFAULT NULL,
    FOREIGN KEY (id_usuario)  REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_reserva)  REFERENCES reservas(id_reserva),
    FOREIGN KEY (id_clase)    REFERENCES clases(id_clase)
);

-- =====================================================
-- CANCELACIONES
-- =====================================================

CREATE TABLE cancelaciones (
    id_cancelacion      INT AUTO_INCREMENT PRIMARY KEY,
    id_reserva          INT NOT NULL,
    motivo              ENUM('CAMBIO_HORARIO','SALUD','ECONOMICO','CAMBIO_SECTOR','CLASE_CANCELADA','VENCIMIENTO_PAGO','OTRO'),
    detalle             TEXT,
    cancelado_por       ENUM('USUARIO','ADMIN','SISTEMA') DEFAULT 'USUARIO',
    id_admin            INT DEFAULT NULL,
    fecha_cancelacion   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_reserva) REFERENCES reservas(id_reserva),
    FOREIGN KEY (id_admin)   REFERENCES administradores(id_admin)
);

-- =====================================================
-- REEMBOLSOS
-- =====================================================

CREATE TABLE reembolsos (
    id_reembolso        INT AUTO_INCREMENT PRIMARY KEY,
    id_pago             INT NOT NULL,
    monto               DECIMAL(10,2),
    motivo              TEXT,
    fecha_reembolso     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado              ENUM('PENDIENTE','COMPLETADO','RECHAZADO') DEFAULT 'PENDIENTE',
    procesado_por_admin INT DEFAULT NULL,
    FOREIGN KEY (id_pago)               REFERENCES pagos(id_pago),
    FOREIGN KEY (procesado_por_admin)   REFERENCES administradores(id_admin)
);

-- =====================================================
-- PAGOS YAPE
-- =====================================================

CREATE TABLE yape_pagos (
    id_yape_pago        INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario          INT NOT NULL,
    id_reserva          INT,
    id_clase            INT NOT NULL,
    id_espacio          INT NOT NULL,
    celular             VARCHAR(15) NOT NULL,
    codigo_confirmacion VARCHAR(6),
    estado              VARCHAR(20) DEFAULT 'PENDIENTE',
    monto               DECIMAL(10,2) NOT NULL,
    fecha_creacion      DATETIME,
    fecha_confirmacion  DATETIME,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_reserva) REFERENCES reservas(id_reserva),
    FOREIGN KEY (id_clase)   REFERENCES clases(id_clase),
    FOREIGN KEY (id_espacio) REFERENCES espacios(id_espacio)
);

-- =====================================================
-- HISTORIAL DE RESERVAS
-- =====================================================

CREATE TABLE historial_reservas (
    id_historial    INT AUTO_INCREMENT PRIMARY KEY,
    id_reserva      INT NOT NULL,
    accion          VARCHAR(150),
    descripcion     TEXT,
    realizado_por   ENUM('USUARIO','ADMIN','SISTEMA') DEFAULT 'SISTEMA',
    id_admin        INT DEFAULT NULL,
    fecha           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_reserva) REFERENCES reservas(id_reserva),
    FOREIGN KEY (id_admin)   REFERENCES administradores(id_admin)
);

-- =====================================================
-- CAMBIOS DE ESPACIO
-- =====================================================

CREATE TABLE cambios_espacio (
    id_cambio           INT AUTO_INCREMENT PRIMARY KEY,
    id_reserva          INT NOT NULL,
    id_espacio_anterior INT NOT NULL,
    id_espacio_nuevo    INT NOT NULL,
    fecha_cambio        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_reserva)          REFERENCES reservas(id_reserva),
    FOREIGN KEY (id_espacio_anterior) REFERENCES espacios(id_espacio),
    FOREIGN KEY (id_espacio_nuevo)    REFERENCES espacios(id_espacio)
);

-- =====================================================
-- CAMBIOS DE HORARIO DE CLASE
-- =====================================================

CREATE TABLE cambios_clase (
    id_cambio               INT AUTO_INCREMENT PRIMARY KEY,
    id_clase                INT NOT NULL,
    id_admin                INT NOT NULL,
    campo_modificado        ENUM('HORARIO','INSTRUCTOR','CUPOS','PRECIO','FECHA','OTRO') NOT NULL,
    valor_anterior          VARCHAR(255),
    valor_nuevo             VARCHAR(255),
    motivo                  TEXT,
    fecha_cambio            TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_clase) REFERENCES clases(id_clase),
    FOREIGN KEY (id_admin) REFERENCES administradores(id_admin)
);

-- =====================================================
-- ÍNDICES ADICIONALES
-- =====================================================

CREATE INDEX idx_clases_fecha       ON clases (fecha, estado);
CREATE INDEX idx_clases_genero      ON clases (id_genero, estado);
CREATE INDEX idx_reservas_usuario   ON reservas (id_usuario, estado_reserva);
CREATE INDEX idx_pagos_estado       ON pagos (estado, metodo_pago);
CREATE INDEX idx_notif_usuario      ON notificaciones (id_usuario, leido);
CREATE INDEX idx_espacios_clase     ON espacios (id_clase, estado);

-- =====================================================
-- VISTAS
-- =====================================================

CREATE OR REPLACE VIEW vista_resumen_dia AS
SELECT
    COUNT(DISTINCT r.id_reserva)                                  AS reservas_hoy,
    SUM(r.estado_pago = 'PENDIENTE')                              AS pagos_pendientes,
    SUM(r.estado_pago = 'PAGADO')                                 AS pagos_confirmados,
    COUNT(DISTINCT CASE WHEN c.estado = 'CANCELADA' AND DATE(c.fecha) = CURDATE() THEN c.id_clase END) AS clases_canceladas_hoy,
    COUNT(DISTINCT CASE WHEN c.estado = 'ACTIVA' AND c.fecha = CURDATE() THEN c.id_clase END)         AS clases_activas_hoy,
    SUM(e.estado = 'OCUPADO')                                     AS espacios_ocupados
FROM reservas r
JOIN clases c    ON r.id_clase   = c.id_clase
JOIN espacios e  ON r.id_espacio = e.id_espacio
WHERE r.fecha_clase = CURDATE();

CREATE OR REPLACE VIEW vista_clases_completas AS
SELECT
    c.id_clase, c.nombre_clase, c.descripcion, c.intensidad, c.reglas_vestimenta,
    c.duracion_minutos, c.fecha, c.hora_inicio, c.hora_fin, c.precio,
    c.cupos_totales, c.cupos_disponibles, c.alumnos_minimos, c.fecha_limite_cancelacion,
    c.imagen_clase, c.estado,
    g.id_genero, g.nombre_genero, g.imagen AS imagen_genero,
    i.id_instructor, i.nombre_completo AS nombre_instructor, i.especialidad,
    i.foto AS foto_instructor, i.video_presentacion
FROM clases c
JOIN generos_clase  g ON c.id_genero    = g.id_genero
JOIN instructores   i ON c.id_instructor = i.id_instructor;

CREATE OR REPLACE VIEW vista_reservas_detalle AS
SELECT
    r.id_reserva, r.codigo_reserva, r.id_usuario,
    u.nombre_completo AS nombre_usuario,
    r.fecha_clase, r.fecha_reserva, r.fecha_limite_pago,
    r.metodo_pago, r.estado_pago, r.estado_reserva, r.monto, r.qr_checkin,
    e.codigo_espacio, c.nombre_clase, c.hora_inicio, c.hora_fin, c.duracion_minutos,
    i.nombre_completo AS nombre_instructor, g.nombre_genero
FROM reservas r
JOIN usuarios     u ON r.id_usuario   = u.id_usuario
JOIN clases       c ON r.id_clase     = c.id_clase
JOIN espacios     e ON r.id_espacio   = e.id_espacio
JOIN instructores i ON c.id_instructor = i.id_instructor
JOIN generos_clase g ON c.id_genero   = g.id_genero;

-- =====================================================
-- DATA DE PRUEBA
-- =====================================================

INSERT INTO administradores (nombre, correo_institucional, password_hash, estado) VALUES
('Admin JMGym', 'admin@jmgym.com', '$pbkdf2-sha256$29000$9x5D6N27dy7l/P.fU2oNgQ$GFidVEw.oMQfTDLBV41SwLtWBzQhEgabxSGCgn2VhSg', 'ACTIVO');

INSERT INTO generos_clase (nombre_genero, descripcion, estado) VALUES
('Baile',   'Clases de ritmo y coordinación con música', 'ACTIVO'),
('Cardio',  'Entrenamientos para mejorar resistencia y quemar calorías', 'ACTIVO'),
('Fuerza',  'Trabajo muscular con pesas, bandas y peso corporal', 'ACTIVO');

INSERT INTO instructores (nombre_completo, telefono, especialidad, estado) VALUES
('Ana Torres',  '999111001', 'Zumba y baile latino',        'ACTIVO'),
('Luis Bizarro', '999111002', 'Cardio y entrenamiento HIIT', 'ACTIVO'),
('María Ramos', '999111003', 'Fuerza y musculación',        'ACTIVO');

INSERT INTO clases (
  nombre_clase, id_genero, id_instructor, descripcion,
  intensidad, duracion_minutos, fecha, hora_inicio, hora_fin,
  precio, cupos_totales, cupos_disponibles, alumnos_minimos, estado
) VALUES
('Zumba',       1, 1, 'Clase de baile fitness con ritmos latinos.',  'MEDIA', 60, CURDATE() + INTERVAL 1 DAY, '08:00:00', '09:00:00', 25.00, 40, 40, 5, 'ACTIVA'),
('CardioFit',   2, 2, 'Entrenamiento cardiovascular de alta intensidad.', 'ALTA', 45, CURDATE() + INTERVAL 2 DAY, '07:00:00', '07:45:00', 30.00, 30, 30, 5, 'ACTIVA'),
('Tren Superior', 3, 3, 'Trabajo de fuerza enfocado en brazos, pecho, hombros y espalda.', 'ALTA', 50, CURDATE() + INTERVAL 3 DAY, '18:00:00', '18:50:00', 35.00, 20, 20, 5, 'ACTIVA');

-- =====================================================
-- MODIFICACIONES AL ESQUEMA
-- =====================================================

ALTER TABLE reservas
MODIFY COLUMN estado_pago ENUM(
'PENDIENTE',
'PAGADO',
'REEMBOLSO_PENDIENTE',
'REEMBOLSADO'
) NOT NULL;

ALTER TABLE notificaciones
MODIFY COLUMN tipo ENUM(
    'RECORDATORIO','PAGO','PAGO_CONFIRMADO','CAMBIO_HORARIO',
    'CAMBIO_INSTRUCTOR','NUEVA_CLASE','CANCELACION','REEMBOLSO',
    'BLOQUEO_CUENTA','RESERVA_CONFIRMADA','RESERVA_CANCELADA',
    'CAMBIO_ESPACIO','NOTIFICACION_GENERAL'
) NOT NULL;

