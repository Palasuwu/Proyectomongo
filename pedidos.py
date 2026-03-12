from bson.objectid import ObjectId

def realizar_pedido_interactivo(client, db, confirmar_pedido_transaccion):
    print("\n--- Realizar Pedido (Transacción ACID) ---")

    # 1️⃣ Seleccionar Usuario
    usuarios = list(db["usuarios"].find({}, {"nombre": 1}))
    if not usuarios:
        print("❌ No hay usuarios disponibles.")
        return

    print("\n👤 Selecciona Usuario:")
    for i, u in enumerate(usuarios, start=1):
        print(f"{i}. {u.get('nombre')}")

    seleccion_usuario = input("Número de usuario: ")
    if not seleccion_usuario.isdigit() or not (1 <= int(seleccion_usuario) <= len(usuarios)):
        print("❌ Opción inválida.")
        return

    usuario_db = usuarios[int(seleccion_usuario) - 1]

    # 2️⃣ Seleccionar Restaurante
    restaurantes = list(db["restaurantes"].find({}, {"nombre": 1}))
    if not restaurantes:
        print("❌ No hay restaurantes disponibles.")
        return

    print("\n🏢 Selecciona Restaurante:")
    for i, r in enumerate(restaurantes, start=1):
        print(f"{i}. {r.get('nombre')}")

    seleccion_rest = input("Número de restaurante: ")
    if not seleccion_rest.isdigit() or not (1 <= int(seleccion_rest) <= len(restaurantes)):
        print("❌ Opción inválida.")
        return

    restaurante_db = restaurantes[int(seleccion_rest) - 1]

    # 3️⃣ Mostrar artículos
    articulos = list(
        db["articulosMenu"].find(
            {"restauranteId": restaurante_db["_id"]},
            {"nombre": 1, "precio": 1}
        )
    )

    if not articulos:
        print("❌ Este restaurante no tiene artículos.")
        return

    carrito_compras = []

    while True:
        print("\n🍔 Selecciona Artículo:")
        for i, a in enumerate(articulos, start=1):
            print(f"{i}. {a.get('nombre')} (Q{a.get('precio')})")

        seleccion_art = input("Número de artículo (0 para terminar): ")

        if seleccion_art == "0":
            break

        if not seleccion_art.isdigit() or not (1 <= int(seleccion_art) <= len(articulos)):
            print("❌ Opción inválida.")
            continue

        articulo_db = articulos[int(seleccion_art) - 1]

        cantidad_input = input("Cantidad: ")
        if not cantidad_input.isdigit() or int(cantidad_input) <= 0:
            print("❌ Cantidad inválida.")
            continue

        cantidad = int(cantidad_input)

        carrito_compras.append({
            "articuloId": str(articulo_db["_id"]),
            "nombreSnapshot": articulo_db["nombre"],
            "precioUnitarioSnapshot": articulo_db["precio"],
            "cantidad": cantidad
        })

    if not carrito_compras:
        print("❌ No se agregaron artículos.")
        return

    # Mostrar resumen
    print("\n📋 RESUMEN DEL PEDIDO:")
    total_estimado = 0

    for item in carrito_compras:
        subtotal = item["precioUnitarioSnapshot"] * item["cantidad"]
        total_estimado += subtotal
        print(f"{item['nombreSnapshot']} x{item['cantidad']} → Q{subtotal}")

    print(f"TOTAL ESTIMADO: Q{total_estimado}")

    confirmar = input("Confirmar pedido? (s/n): ")

    if confirmar.lower() == 's':
        confirmar_pedido_transaccion(
            client,
            db,
            str(usuario_db["_id"]),
            str(restaurante_db["_id"]),
            carrito_compras
        )
    else:
        print("❌ Pedido cancelado.")