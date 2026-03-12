from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
from datetime import datetime
from actualizaciones import actualizar_registros
from consultas import consultar_catalogo_restaurantes
from reportes import ejecutar_reportes
from creacion import crear_documentos
from eliminaciones import eliminar_registros
from snapshots import manejar_snapshots_gridfs
from pedidos import realizar_pedido_interactivo

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
# ==========================================
# uri = "mongodb+srv://gon23152_db_ikeel:MGECARG10@cluster0.uqhzj8v.mongodb.net/"
uri = "mongodb://gon23152_db_ikeel:<db_password>@ac-dnpa0km-shard-00-00.uqhzj8v.mongodb.net:27017,ac-dnpa0km-shard-00-01.uqhzj8v.mongodb.net:27017,ac-dnpa0km-shard-00-02.uqhzj8v.mongodb.net:27017/?ssl=true&replicaSet=atlas-tg4y69-shard-0&authSource=admin&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))

def conectar_bd():
    try:
        client.admin.command('ping')
        db = client['proyectoBD2']
        return db
    except Exception as e:
        print(f"Error al conectar: {e}")
        return None

# ==========================================
# 2. FUNCIONES DE LÓGICA (QUERYS Y TRANSACCIONES)
# ==========================================


def confirmar_pedido_transaccion(client, db, usuario_id_str, restaurante_id_str, items_input):
    """Opción 7: Ejecuta la creación de un pedido sin romper el JSON Schema estricto."""
    with client.start_session() as session:
        try:
            with session.start_transaction():
                print("\nIniciando transacción ACID...")
                items_pedido = []
                total_orden = 0
                
                for item in items_input:
                    subtotal = item['precioUnitarioSnapshot'] * item['cantidad']
                    total_orden += subtotal
                    items_pedido.append({
                        "articuloId": ObjectId(item['articuloId']),
                        "nombreSnapshot": item['nombreSnapshot'],
                        "precioUnitarioSnapshot": item['precioUnitarioSnapshot'],
                        "cantidad": item['cantidad'],
                        "subtotal": subtotal
                    })
                
                nueva_orden = {
                    "usuarioId": ObjectId(usuario_id_str),
                    "restauranteId": ObjectId(restaurante_id_str),
                    "estado": "CONFIRMADA",
                    "total": total_orden,
                    "fechaCreacion": datetime.utcnow(),
                    "items": items_pedido
                }
                
                # Paso 1: Crear e insertar la orden
                orden_insertada = db["ordenes"].insert_one(nueva_orden, session=session)
                print(f"-> Orden creada exitosamente con ID: {orden_insertada.inserted_id}")
                
                # OMITIMOS el $inc de inventario para respetar el JSON Schema (additionalProperties: False)
                
                print("¡Transacción exitosa! La orden ha hecho commit en la base de datos.")
                return orden_insertada.inserted_id
                
        except Exception as e:
            print(f"Error detectado. Haciendo ROLLBACK de la transacción. Detalle: {e}")
            return None


# ==========================================
# 3. INTERFAZ DE USUARIO (MENÚ PRINCIPAL)
# ==========================================
def mostrar_menu():
    print("\n" + "="*50)
    print("🍔 SISTEMA DE GESTIÓN DE RESTAURANTES UVG 🍔")
    print("="*50)
    print("1. Insertar datos (Documentos embebidos/referenciados)")
    print("2. Consultar catálogo (Filtros, Proyección, Sort, Límite)")
    print("3. Actualizar registros (1 o varios)")
    print("4. Eliminar registros (1 o varios)")
    print("5. Reportes y Estadísticas (Agregaciones)")
    print("6. Manejo de Imágenes de Menú (GridFS)")
    print("7. Realizar un Pedido (Transacción ACID)")
    print("8. Salir del sistema")
    print("="*50)

def main():
    print("Conectando a MongoDB Atlas...")
    db = conectar_bd()
    if db is None:
        print("No se pudo iniciar el sistema. Revisa tu conexión.")
        return
    print("¡Conexión exitosa y colecciones listas!")

    while True:
        mostrar_menu()
        opcion = input("Selecciona una opción de la rúbrica (1-8): ")

        if opcion == '1':
            crear_documentos(db)

        elif opcion == '2':
            # Llamamos a la función dinámica
            consultar_catalogo_restaurantes(db)

        elif opcion == '3':
            actualizar_registros(db)

        elif opcion == '4':
            eliminar_registros(db)

        elif opcion == '5':
            ejecutar_reportes(db)

        elif opcion == '6':
            # Eliminar si no funciona bien
            manejar_snapshots_gridfs(db)

        elif opcion == '7':
            realizar_pedido_interactivo(client, db, confirmar_pedido_transaccion)
            
        elif opcion == '8':
            print("\nSaliendo del sistema... ¡Hasta pronto!")
            break
            
        else:
            print("\n❌ Opción no válida. Intenta de nuevo.")

if __name__ == "__main__":
    main()
