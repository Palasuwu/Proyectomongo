from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN A LA BASE DE DATOS
# ==========================================
uri = "mongodb+srv://gon23152_db_ikeel:MGECARG10@cluster0.uqhzj8v.mongodb.net/"
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
# 2. FUNCIONES DE LÓGICA DE NEGOCIO (TRANSACCIÓN ACID)
# ==========================================
def confirmar_pedido_transaccion(client, db, usuario_id_str, restaurante_id_str, items_input):
    """Ejecuta la creación de un pedido y la actualización de métricas bajo una transacción ACID."""
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
                
                orden_insertada = db["ordenes"].insert_one(nueva_orden, session=session)
                print(f"-> Orden creada temporalmente con ID: {orden_insertada.inserted_id}")
                
                for item in items_pedido:
                    db["articulosMenu"].update_one(
                        {"_id": ObjectId(item['articuloId'])},
                        {"$inc": {"cantidadVendida": item['cantidad']}}, 
                        session=session
                    )
                print("-> Inventario de artículos actualizado.")
                
                db["restaurantes"].update_one(
                    {"_id": ObjectId(restaurante_id_str)},
                    {"$inc": {"totalPedidosHistoricos": 1}},
                    session=session
                )
                print("-> Estadísticas del restaurante actualizadas.")
                
                print("¡Transacción exitosa! Todos los cambios guardados.")
                return orden_insertada.inserted_id
                
        except Exception as e:
            print(f"Error detectado. Haciendo ROLLBACK de la transacción. Detalle: {e}")
            return None

# ==========================================
# 3. INTERFAZ DE USUARIO (EL MENÚ PRINCIPAL)
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
            print("\n--- Módulo de Creación ---")
            print("Función en construcción...")

        elif opcion == '2':
            print("\n--- Catálogo y Consultas Avanzadas ---")
            print("Función en construcción...")

        elif opcion == '3':
            print("\n--- Actualización de Datos ---")
            print("Función en construcción...")

        elif opcion == '4':
            print("\n--- Eliminación de Datos ---")
            print("Función en construcción...")

        elif opcion == '5':
            print("\n--- Reportes (Aggregation Framework) ---")
            print("Función en construcción...")

        elif opcion == '6':
            print("\n--- Galería GridFS ---")
            print("Función en construcción...")

        elif opcion == '7':
            print("\n--- Realizar Pedido (Transacción) ---")
            # Datos quemados
            id_usuario = "69ac7acf39b76d2a3370e5ab"      
            id_restaurante = "69ac7daa39b76d2a3370e5bc"  
            carrito_compras = [{
                "articuloId": "69ac7f1339b76d2a3370e5c7", 
                "nombreSnapshot": "Hamburguesa Doble Queso",
                "precioUnitarioSnapshot": 45.5,
                "cantidad": 2
            }]
            confirmar_pedido_transaccion(client, db, id_usuario, id_restaurante, carrito_compras)
            
        elif opcion == '8':
            print("\nSaliendo del sistema... ¡Hasta pronto!")
            break
            
        else:
            print("\n Opción no válida. Intenta de nuevo.")

if __name__ == "__main__":
    main()