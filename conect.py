from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Cadena de conexión a tu clúster
uri = "mongodb+srv://gon23152_db_ikeel:MGECARG10@cluster0.uqhzj8v.mongodb.net/"
client = MongoClient(uri, server_api=ServerApi('1'))

def conectar_bd():
    try:
        client.admin.command('ping')
        print("¡Conexión exitosa a MongoDB Atlas!")
        
        # Conectando a la base de datos específica de tu captura
        db = client['proyectoBD2']
        
        # Mapeando las colecciones con los nombres exactos que creaste
        colecciones = {
            "usuarios": db['usuarios'],
            "restaurantes": db['restaurantes'],
            "articulos_menu": db['articulosMenu'],
            "ordenes": db['ordenes'],
            "resenas": db['resenas'] # Usando la versión sin caracteres especiales
        }
        
        print("Colecciones mapeadas y listas para usar.")
        return db, colecciones

    except Exception as e:
        print(f"Error al conectar: {e}")
        return None, None

db_activa, mis_colecciones = conectar_bd()