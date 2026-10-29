from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import sqlite3

app = FastAPI(title="Deber Sistema de Matriculación - UCE", version="1.0")


def conectar_db():
    conexion = sqlite3.connect("matriculacion.db")
    # Configura para que las filas devueltas se puedan leer como diccionarios
    conexion.row_factory = sqlite3.Row
    return conexion

# Función para inicializar y crear las tres tablas requeridas con sus relaciones
def inicializar_base_datos():
    # Abrimos la conexión con la base de datos local
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    # 1. Tabla de Paralelos (3 paralelos: 001, 002, 003)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS paralelos (
            id_paralelo INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_paralelo TEXT NOT NULL UNIQUE
        )
    """)
    
    # 2. Tabla de Materias (Las 6 materias solicitadas)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS materias (
            id_materia INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_materia TEXT NOT NULL UNIQUE
        )
    """)
    
    # 3. Tabla de Usuarios (Con relación a un paralelo mediante Llave Foránea FK)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            edad INTEGER NOT NULL,
            cedula TEXT NOT NULL UNIQUE,
            fecha_nacimiento TEXT NOT NULL,
            id_paralelo INTEGER,
            FOREIGN KEY (id_paralelo) REFERENCES paralelos(id_paralelo)
        )
    """)
    
    # Insertar los 3 paralelos por defecto si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM paralelos")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO paralelos (nombre_paralelo) VALUES (?)", [("001",), ("002",), ("003",)])
        
    # Insertar las 6 materias obligatorias por defecto si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM materias")
    if cursor.fetchone()[0] == 0:
        materias_default = [
            ("programacion 1",),
            ("base de datos",),
            ("historia de la IA",),
            ("analisis matematico",),
            ("algebra lineal",),
            ("estadistica y probabilidad",)
        ]
        cursor.executemany("INSERT INTO materias (nombre_materia) VALUES (?)", materias_default)

    # Insertar los 20 usuarios inventados por defecto si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        usuarios_default = [
            ("Juan", "Pérez", 20, "1710000001", "2004-01-15", 1),
            ("María", "Gómez", 21, "1710000002", "2003-05-20", 2),
            ("Carlos", "López", 22, "1710000003", "2002-11-10", 3),
            ("Ana", "Torres", 19, "1710000004", "2005-03-08", 1),
            ("Luis", "Andrade", 23, "1710000005", "2001-09-25", 2),
            ("Sofía", "Ramírez", 20, "1710000006", "2004-02-14", 3),
            ("Diego", "Castro", 21, "1710000007", "2003-07-30", 1),
            ("Elena", "Morales", 22, "1710000008", "2002-04-18", 2),
            ("Javier", "Ortiz", 20, "1710000009", "2004-12-05", 3),
            ("Paula", "Sánchez", 19, "1710000010", "2005-08-22", 1),
            ("Mateo", "Vargas", 21, "1710000011", "2003-10-11", 2),
            ("Valeria", "Mendoza", 22, "1710000012", "2002-06-01", 3),
            ("Gabriel", "Espinoza", 20, "1710000013", "2004-03-17", 1),
            ("Camila", "Flores", 21, "1710000014", "2003-01-09", 2),
            ("Daniel", "Castillo", 23, "1710000015", "2001-11-30", 3),
            ("Lucía", "Romero", 19, "1710000016", "2005-05-14", 1),
            ("Ariel", "Suárez", 20, "1710000017", "2004-09-03", 2),
            ("Martina", "Ríos", 22, "1710000018", "2002-12-28", 3),
            ("Emilio", "Salazar", 21, "1710000019", "2003-04-07", 1),
            ("Renata", "Guerrero", 20, "1710000020", "2004-07-19", 2)
        ]
        cursor.executemany("""
            INSERT INTO usuarios (nombre, apellido, edad, cedula, fecha_nacimiento, id_paralelo)
            VALUES (?, ?, ?, ?, ?, ?)
        """, usuarios_default)

    # Guardamos los cambios permanentemente (commit) y cerramos la conexión
    conexion.commit()
    conexion.close()

# Ejecutamos la función de inicialización de la base de datos al arrancar el script
inicializar_base_datos()

# -----------------------------------------------------------------
# MODELOS DE VALIDACIÓN (Pydantic)
# -----------------------------------------------------------------

# Modelo para validar la estructura de datos al registrar un usuario nuevo
class UsuarioCreate(BaseModel):
    nombre: str
    apellido: str
    edad: int
    cedula: str
    fecha_nacimiento: str
    id_paralelo: int  # Un usuario pertenece a un solo paralelo

# Modelo para validar la estructura de datos al actualizar un usuario existente
class UsuarioUpdate(BaseModel):
    nombre: str
    apellido: str
    edad: int
    cedula: str
    fecha_nacimiento: str
    id_paralelo: int

# -----------------------------------------------------------------
# RUTAS O ENDPOINTS DE LA API (CRUD)
# -----------------------------------------------------------------

# Ruta de bienvenida
@app.get("/")
def bienvenida():
    return {"mensaje": "Servidor FastAPI activo para el deber de matriculación"}

# 1. RUTA CONSULTAR (GET): Ver todos los paralelos creados (001, 002, 003)
@app.get("/paralelos")
def ver_paralelos():
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM paralelos")
    resultados = cursor.fetchall()
    conexion.close()
    return {"paralelos": [dict(fila) for fila in resultados]}

# 2. RUTA CONSULTAR (GET): Ver las 6 materias registradas
@app.get("/materias")
def ver_materias():
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM materias")
    resultados = cursor.fetchall()
    conexion.close()
    return {"materias": [dict(fila) for fila in resultados]}

# 3. RUTA CONSULTAR (GET): Ver todos los usuarios (los 20 estudiantes con su respectivo paralelo)
@app.get("/usuarios")
def ver_usuarios():
    conexion = conectar_db()
    cursor = conexion.cursor()
    # Consulta uniendo la tabla de usuarios con la tabla de paralelos mediante JOIN
    cursor.execute("""
        SELECT u.id_usuario, u.nombre, u.apellido, u.edad, u.cedula, u.fecha_nacimiento, p.nombre_paralelo 
        FROM usuarios u
        LEFT JOIN paralelos p ON u.id_paralelo = p.id_paralelo
    """)
    resultados = cursor.fetchall()
    conexion.close()
    return {"usuarios": [dict(fila) for fila in resultados]}

# 4. RUTA CREAR (POST): Permite agregar un nuevo usuario desde el Swagger
@app.post("/usuarios")
def crear_usuario(usuario: UsuarioCreate):
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO usuarios (nombre, apellido, edad, cedula, fecha_nacimiento, id_paralelo)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (usuario.nombre, usuario.apellido, usuario.edad, usuario.cedula, usuario.fecha_nacimiento, usuario.id_paralelo))
        conexion.commit()
        nuevo_id = cursor.lastrowid
        conexion.close()
        return {
            "mensaje": "Usuario registrado exitosamente",
            "id_asignado": nuevo_id,
            "datos": usuario
        }
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Error: La cédula ya está registrada o el ID de paralelo no es válido.")

# 5. RUTA ACTUALIZAR (PUT): Permite modificar los datos de un usuario existente por su ID
@app.put("/usuarios/{id_usuario}", status_code=status.HTTP_200_OK)
def actualizar_usuario(id_usuario: int, usuario: UsuarioUpdate):
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    # 1. Verificar si el usuario realmente existe antes de actualizar
    cursor.execute("SELECT * FROM usuarios WHERE id_usuario = ?", (id_usuario,))
    usuario_existente = cursor.fetchone()
    
    if not usuario_existente:
        conexion.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"El usuario con ID {id_usuario} no existe."
        )
    
    try:
        # 2. Ejecutar la sentencia UPDATE en SQL
        cursor.execute("""
            UPDATE usuarios 
            SET nombre = ?, apellido = ?, edad = ?, cedula = ?, fecha_nacimiento = ?, id_paralelo = ?
            WHERE id_usuario = ?
        """, (usuario.nombre, usuario.apellido, usuario.edad, usuario.cedula, usuario.fecha_nacimiento, usuario.id_paralelo, id_usuario))
        
        # 3. Guardar cambios (commit) y cerrar conexión
        conexion.commit()
        conexion.close()
        
        return {
            "mensaje": f"El usuario con ID {id_usuario} ha sido actualizado exitosamente.",
            "datos_nuevos": usuario
        }
    except sqlite3.IntegrityError:
        conexion.close()
        raise HTTPException(
            status_code=400, 
            detail="Error: La cédula ya pertenece a otro usuario o el ID de paralelo no es válido."
        )

# 6. RUTA ELIMINAR (DELETE): Permite borrar un usuario existente según su ID
@app.delete("/usuarios/{id_usuario}", status_code=status.HTTP_200_OK)
def eliminar_usuario(id_usuario: int):
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    # Verificamos si el usuario existe antes de intentar eliminarlo
    cursor.execute("SELECT * FROM usuarios WHERE id_usuario = ?", (id_usuario,))
    usuario = cursor.fetchone()
    
    if not usuario:
        conexion.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"El usuario con ID {id_usuario} no existe."
        )
    
    # Ejecutamos la sentencia DELETE en la base de datos
    cursor.execute("DELETE FROM usuarios WHERE id_usuario = ?", (id_usuario,))
    
    # Confirmamos los cambios permanentemente con commit y cerramos la conexión
    conexion.commit()
    conexion.close()
    
    return {
        "mensaje": f"El usuario {usuario['nombre']} {usuario['apellido']} con ID {id_usuario} ha sido eliminado correctamente."
    }