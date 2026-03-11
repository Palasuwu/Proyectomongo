from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
from datetime import datetime
from actualizaciones import actualizar_registros
from consultas import consultar_catalogo_restaurantes
from reportes import ejecutar_reportes 

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
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
            print("\n--- Módulo de Creación ---")
            print("Función en construcción...")

        elif opcion == '2':
            # Llamamos a la función dinámica
            consultar_catalogo_restaurantes(db)

        elif opcion == '3':
            actualizar_registros(db)

        elif opcion == '4':
            print("\n--- Eliminación de Datos ---")
            print("Función en construcción...")

        elif opcion == '5':
            ejecutar_reportes(db)

        elif opcion == '6':
            print("\n--- Galería GridFS ---")
            print("Función en construcción...")

        elif opcion == '7':
            print("\n--- Realizar Pedido (Transacción) ---")
            
            # --- DATOS DINÁMICOS  ---
            # 1. Buscamos el primer usuario que exista
            usuario_db = db["usuarios"].find_one()
            if not usuario_db:
                print("❌ No hay usuarios en la base de datos.")
                continue
                
            # 2. Buscamos el primer restaurante que exista
            restaurante_db = db["restaurantes"].find_one()
            if not restaurante_db:
                print("❌ No hay restaurantes en la base de datos.")
                continue
                
            # 3. Buscamos un artículo que sea de ESE restaurante
            articulo_db = db["articulosMenu"].find_one({"restauranteId": restaurante_db["_id"]})
            if not articulo_db:
                print(f"❌ El restaurante '{restaurante_db.get('nombre')}' no tiene artículos.")
                continue
            
            # Extraemos los IDs
            id_usuario_real = str(usuario_db["_id"])
            id_restaurante_real = str(restaurante_db["_id"])
            
            # Armamos el carrito dinámico
            carrito_compras = [{
                "articuloId": str(articulo_db["_id"]), 
                "nombreSnapshot": articulo_db.get("nombre", "Artículo Desconocido"),
                "precioUnitarioSnapshot": articulo_db.get("precio", 0.0),
                "cantidad": 2 # Pedimos 2 de este artículo por defecto para la prueba
            }]
            
            print(f"👤 Cliente: {usuario_db.get('nombre')}")
            print(f"🏢 Restaurante: {restaurante_db.get('nombre')}")
            print(f"🍔 Ordenando: 2x {articulo_db.get('nombre')} (Q{articulo_db.get('precio')})")
            
            # Ejecutamos
            confirmar_pedido_transaccion(client, db, id_usuario_real, id_restaurante_real, carrito_compras)
            
        elif opcion == '8':
            print("\nSaliendo del sistema... ¡Hasta pronto!")
            break
            
        else:
            print("\n❌ Opción no válida. Intenta de nuevo.")

if __name__ == "__main__":
    main()