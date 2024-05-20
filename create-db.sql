

-- Crear la tabla de estudiantes
CREATE TABLE IF NOT EXISTS estudiantes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombres TEXT,
    apellidos TEXT,
    carrera TEXT,
    curso TEXT,
    cedula TEXT UNIQUE,
    clave_unica TEXT,
    voto_realizado BOOLEAN DEFAULT 0 ,
    presidente BOOLEAN DEFAULT 0
);

-- Crear la tabla de opciones
CREATE TABLE IF NOT EXISTS opciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    opcion TEXT UNIQUE NOT NULL,
    imagen_url TEXT
);

-- Crear la base de datos de votación
CREATE TABLE IF NOT EXISTS votos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    opcion_id INTEGER,
    FOREIGN KEY(opcion_id) REFERENCES opciones(id)
);


