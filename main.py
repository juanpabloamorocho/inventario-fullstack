from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import mysql.connector


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite peticiones desde Vercel o cualquier dominio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()  # Cargar variables de entorno desde el archivo .env

def get_db_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST"),          # Tu host de MySQL
            user=os.getenv("DB_USER"),          # Tu usuario de MySQL
            password=os.getenv("DB_PASSWORD"),          # Pon tu contraseña si configuraste una
            database=os.getenv("DB_NAME"),
            port= int(os.getenv("DB_PORT"))
        )
    except Exception as e:
        print(f"❌ Error conectando a MySQL: {e}")
        raise e

class Producto(BaseModel):
    nombre: str
    descripcion: str
    precio: float
    stock: int
    categoria: str

@app.get("/api/productos")
def obtener_productos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    cursor.close()
    conn.close()
    return productos

@app.post("/api/productos")
def crear_producto(producto: Producto):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO productos (nombre, descripcion, precio, stock, categoria)
        VALUES (%s, %s, %s, %s, %s)
    """
    valores = (producto.nombre, producto.descripcion, producto.precio, producto.stock, producto.categoria)
    cursor.execute(query, valores)
    conn.commit()
    nuevo_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return {"mensaje": "Producto creado con éxito", "id": nuevo_id}

@app.delete("/api/productos/{producto_id}")
def eliminar_producto(producto_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM productos WHERE id_producto = %s", (producto_id,))
        conn.commit()
        
        filas_afectadas = cursor.rowcount
        cursor.close()
        conn.close()

        if filas_afectadas == 0:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        return {"mensaje": f"Producto {producto_id} eliminado correctamente"}
    except Exception as e:
        print(f"\n❌ ERROR AL ELIMINAR: {e}\n")
        raise HTTPException(status_code=500, detail=str(e))