def actualizar_registros(db):
    """Opción 3: Actualiza uno o varios documentos cumpliendo la rúbrica."""
    print("\n" + "-"*40)
    print("   ACTUALIZACIÓN DE DATOS (UPDATE)   ")
    print("-"*40)
    print("1. Actualizar UN documento (Modificar descripción de un restaurante)")
    print("2. Actualizar VARIOS documentos (Aumentar precios de un menú en 10%)")
    
    opc = input("\nSelecciona una opción (1-2): ")
    
    if opc == '1':
        print("\n--- Actualizar UN Restaurante ---")
        # Buscamos los restaurantes disponibles para que el usuario elija
        restaurantes = list(db["restaurantes"].find({}, {"nombre": 1, "descripcion": 1}))
        if not restaurantes:
            print(" No hay restaurantes registrados.")
            return
            
        for i, rest in enumerate(restaurantes, start=1):
            print(f"{i}. {rest.get('nombre')} (Desc actual: {rest.get('descripcion', 'Sin descripción')})")
            
        seleccion = input(f"\nElige el número del restaurante a editar (1-{len(restaurantes)}): ")
        
        if seleccion.isdigit() and 1 <= int(seleccion) <= len(restaurantes):
            rest_elegido = restaurantes[int(seleccion) - 1]
            nueva_desc = input("Ingresa la nueva descripción: ")
            
            # Ejecutamos update_one
            resultado = db["restaurantes"].update_one(
                {"_id": rest_elegido["_id"]},
                {"$set": {"descripcion": nueva_desc}}
            )
            
            if resultado.modified_count > 0:
                print(" ¡Descripción actualizada correctamente!")
            else:
                print(" No se hicieron cambios (quizá ingresaste la misma descripción que ya tenía).")
        else:
            print(" Opción inválida.")

    elif opc == '2':
        print("\n--- Actualizar VARIOS Artículos (Inflación 10%) ---")
        restaurantes = list(db["restaurantes"].find({}, {"nombre": 1}))
        if not restaurantes:
            print(" No hay restaurantes registrados.")
            return
            
        for i, rest in enumerate(restaurantes, start=1):
            print(f"{i}. {rest.get('nombre')}")
            
        seleccion = input(f"\nElige el restaurante para subir sus precios (1-{len(restaurantes)}): ")
        
        if seleccion.isdigit() and 1 <= int(seleccion) <= len(restaurantes):
            rest_elegido = restaurantes[int(seleccion) - 1]
            
            print(f"⚠️ Estás a punto de aumentar en 10% el precio de TODO el menú de '{rest_elegido['nombre']}'.")
            confirmacion = input("¿Estás seguro? (s/n): ")
            
            if confirmacion.lower() == 's':
                # Ejecutamos update_many usando el operador $mul para multiplicar el precio
                resultado = db["articulosMenu"].update_many(
                    {"restauranteId": rest_elegido["_id"]},
                    {"$mul": {"precio": 1.10}} 
                )
                print(f" ¡Precios actualizados! Se modificaron {resultado.modified_count} platillos.")
            else:
                print(" Operación cancelada.")
        else:
            print(" Opción inválida.")
    else:
        print(" Opción principal no válida.")