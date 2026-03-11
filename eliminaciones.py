from bson.objectid import ObjectId

def eliminar_registros(db):
    print("\n" + "-"*50)
    print("🗑️ ELIMINACIÓN DE DOCUMENTOS")
    print("-"*50)
    print("1. Eliminar UN usuario")
    print("2. Eliminar VARIAS órdenes por estado")
    print("3. Eliminar UN restaurante")
    print("4. Eliminar VARIAS reseñas por restaurante")

    opcion = input("\nSelecciona opción (1-4): ")

    # 1️⃣ delete_one usuario
    if opcion == '1':
        usuario_id = input("ID del usuario a eliminar: ")

        confirm = input("⚠️ ¿Seguro que deseas eliminar este usuario? (s/n): ")
        if confirm.lower() == 's':
            resultado = db["usuarios"].delete_one({"_id": ObjectId(usuario_id)})

            if resultado.deleted_count > 0:
                print("✅ Usuario eliminado correctamente.")
            else:
                print("❌ Usuario no encontrado.")

    # 2️⃣ delete_many órdenes por estado
    elif opcion == '2':
        estado = input("Estado de órdenes a eliminar (PENDIENTE, CANCELADA, etc.): ")

        confirm = input(f"⚠️ ¿Eliminar todas las órdenes con estado '{estado}'? (s/n): ")
        if confirm.lower() == 's':
            resultado = db["ordenes"].delete_many({"estado": estado})
            print(f"✅ {resultado.deleted_count} órdenes eliminadas.")

    # 3️⃣ delete_one restaurante
    elif opcion == '3':
        restaurante_id = input("ID del restaurante a eliminar: ")

        confirm = input("⚠️ ¿Seguro que deseas eliminar este restaurante? (s/n): ")
        if confirm.lower() == 's':
            resultado = db["restaurantes"].delete_one({"_id": ObjectId(restaurante_id)})

            if resultado.deleted_count > 0:
                print("✅ Restaurante eliminado.")
            else:
                print("❌ Restaurante no encontrado.")

    # 4️⃣ delete_many reseñas por restaurante
    elif opcion == '4':
        restaurante_id = input("ID del restaurante: ")

        confirm = input("⚠️ ¿Eliminar todas las reseñas de este restaurante? (s/n): ")
        if confirm.lower() == 's':
            resultado = db["resenas"].delete_many({"restauranteId": ObjectId(restaurante_id)})
            print(f"✅ {resultado.deleted_count} reseñas eliminadas.")

    else:
        print("❌ Opción inválida.")