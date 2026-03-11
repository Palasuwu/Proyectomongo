from bson.objectid import ObjectId
from datetime import datetime

def crear_documentos(db):
    print("\n" + "-"*50)
    print("📌 CREACIÓN DE DOCUMENTOS")
    print("-"*50)
    print("1. Crear usuario")
    print("2. Crear restaurante")
    print("3. Crear artículo de menú")
    print("4. Crear orden (documento embebido)")
    print("5. Crear reseña")
    print("6. Crear múltiples usuarios")

    opcion = input("\nSelecciona opción (1-6): ")

    # 1️⃣ Crear usuario
    if opcion == '1':
        nombre = input("Nombre: ")
        email = input("Email: ")
        password = input("Password: ")

        usuario = {
            "nombre": nombre,
            "email": email,
            "passwordHash": password,
            "fechaRegistro": datetime.utcnow()
        }

        resultado = db["usuarios"].insert_one(usuario)
        print(f"✅ Usuario creado con ID: {resultado.inserted_id}")

    # 2️⃣ Crear restaurante
    elif opcion == '2':
        nombre = input("Nombre restaurante: ")
        descripcion = input("Descripción: ")
        categoria = input("Categoría: ")

        restaurante = {
            "nombre": nombre,
            "descripcion": descripcion,
            "categorias": [categoria],
            "location": {
                "type": "Point",
                "coordinates": [-90.50, 14.60]
            }
        }

        resultado = db["restaurantes"].insert_one(restaurante)
        print(f"✅ Restaurante creado con ID: {resultado.inserted_id}")

    # 3️⃣ Crear artículo
    elif opcion == '3':
        restaurante_id = input("ID del restaurante: ")
        nombre = input("Nombre del platillo: ")
        precio = float(input("Precio: "))

        articulo = {
            "restauranteId": ObjectId(restaurante_id),
            "nombre": nombre,
            "descripcion": f"{nombre} preparado con ingredientes frescos.",
            "precio": precio,
            "disponible": True,
            "imagenId": None
        }

        resultado = db["articulosMenu"].insert_one(articulo)
        print(f"✅ Artículo creado con ID: {resultado.inserted_id}")

    # 4️⃣ Crear orden embebida
    elif opcion == '4':
        usuario_id = input("ID usuario: ")
        restaurante_id = input("ID restaurante: ")
        articulo_id = input("ID artículo: ")
        cantidad = int(input("Cantidad: "))

        articulo = db["articulosMenu"].find_one({"_id": ObjectId(articulo_id)})

        if not articulo:
            print("❌ Artículo no encontrado.")
            return

        subtotal = articulo["precio"] * cantidad

        orden = {
            "usuarioId": ObjectId(usuario_id),
            "restauranteId": ObjectId(restaurante_id),
            "estado": "CONFIRMADA",
            "total": subtotal,
            "fechaCreacion": datetime.utcnow(),
            "items": [{
                "articuloId": articulo["_id"],
                "nombreSnapshot": articulo["nombre"],
                "precioUnitarioSnapshot": articulo["precio"],
                "cantidad": cantidad,
                "subtotal": subtotal
            }]
        }

        resultado = db["ordenes"].insert_one(orden)
        print(f"✅ Orden creada con ID: {resultado.inserted_id}")

    # 5️⃣ Crear reseña
    elif opcion == '5':
        usuario_id = input("ID usuario: ")
        restaurante_id = input("ID restaurante: ")
        orden_id = input("ID orden: ")
        calificacion = int(input("Calificación (1-5): "))
        comentario = input("Comentario: ")

        resena = {
            "usuarioId": ObjectId(usuario_id),
            "restauranteId": ObjectId(restaurante_id),
            "ordenId": ObjectId(orden_id),
            "calificacion": calificacion,
            "comentario": comentario,
            "fecha": datetime.utcnow()
        }

        resultado = db["resenas"].insert_one(resena)
        print(f"✅ Reseña creada con ID: {resultado.inserted_id}")

    # 6️⃣ Insertar múltiples usuarios
    elif opcion == '6':
        cantidad = int(input("¿Cuántos usuarios crear?: "))
        usuarios = []

        for i in range(cantidad):
            usuarios.append({
                "nombre": f"Usuario_{i}",
                "email": f"user{i}@mail.com",
                "passwordHash": "123456",
                "fechaRegistro": datetime.utcnow()
            })

        db["usuarios"].insert_many(usuarios)
        print(f"✅ {cantidad} usuarios creados.")

    else:
        print("❌ Opción inválida.")