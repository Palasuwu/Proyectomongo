def ejecutar_reportes(db):
    print("\n" + "-"*50)
    print("📊 REPORTES Y ESTADÍSTICAS")
    print("-"*50)
    print("1. Conteo de órdenes por estado")
    print("2. Estados distintos de órdenes")
    print("3. Platillos más vendidos")
    print("4. Promedio de calificación por restaurante")
    print("5. Top usuarios que más ordenan")
    print("6. Restaurante con mayor facturación")
    print("7. Reporte completo (Orden + Usuario + Restaurante)")

    subop = input("\nSelecciona un reporte (1-7): ")

    if subop == '1':
        pipeline = [
            {"$group": {"_id": "$estado", "total": {"$sum": 1}}},
            {"$sort": {"total": -1}}
        ]
        resultados = list(db["ordenes"].aggregate(pipeline))
        for r in resultados:
            print(f"{r['_id']} → {r['total']} órdenes")

    elif subop == '2':
        estados = db["ordenes"].distinct("estado")
        for e in estados:
            print(f"- {e}")

    elif subop == '3':
        pipeline = [
            {"$unwind": "$items"},
            {"$group": {
                "_id": "$items.articuloId",
                "nombre": {"$first": "$items.nombreSnapshot"},
                "totalVendidos": {"$sum": "$items.cantidad"}
            }},
            {"$sort": {"totalVendidos": -1}},
            {"$limit": 10}
        ]
        resultados = list(db["ordenes"].aggregate(pipeline))
        for r in resultados:
            print(f"{r['nombre']} → {r['totalVendidos']} vendidos")

    elif subop == '4':
        pipeline = [
            {"$group": {
                "_id": "$restauranteId",
                "promedio": {"$avg": "$calificacion"},
                "totalResenas": {"$sum": 1}
            }},
            {"$lookup": {
                "from": "restaurantes",
                "localField": "_id",
                "foreignField": "_id",
                "as": "restaurante"
            }},
            {"$unwind": "$restaurante"},
            {"$sort": {"promedio": -1}}
        ]
        resultados = list(db["resenas"].aggregate(pipeline))
        for r in resultados:
            print(f"{r['restaurante']['nombre']} → {round(r['promedio'],2)}")

    elif subop == '5':
        pipeline = [
            {"$group": {"_id": "$usuarioId", "totalOrdenes": {"$sum": 1}}},
            {"$lookup": {
                "from": "usuarios",
                "localField": "_id",
                "foreignField": "_id",
                "as": "usuario"
            }},
            {"$unwind": "$usuario"},
            {"$sort": {"totalOrdenes": -1}},
            {"$limit": 5}
        ]
        resultados = list(db["ordenes"].aggregate(pipeline))
        for r in resultados:
            print(f"{r['usuario']['nombre']} → {r['totalOrdenes']} órdenes")

    elif subop == '6':
        pipeline = [
            {"$group": {"_id": "$restauranteId", "totalFacturado": {"$sum": "$total"}}},
            {"$lookup": {
                "from": "restaurantes",
                "localField": "_id",
                "foreignField": "_id",
                "as": "restaurante"
            }},
            {"$unwind": "$restaurante"},
            {"$sort": {"totalFacturado": -1}},
            {"$limit": 1}
        ]
        resultado = list(db["ordenes"].aggregate(pipeline))
        if resultado:
            r = resultado[0]
            print(f"{r['restaurante']['nombre']} → Q{round(r['totalFacturado'],2)}")

    elif subop == '7':
        usuarios = list(
            db["usuarios"]
            .find({}, {"nombre": 1})
            .sort("nombre", 1)
        )

        if not usuarios:
            print("No hay usuarios registrados.")
            return

        print("\n--- USUARIOS DISPONIBLES ---")
        for i, u in enumerate(usuarios, start=1):
            print(f"{i}. {u.get('nombre')}")

        seleccion = input(f"\nSelecciona un usuario (1-{len(usuarios)}): ")

        if not seleccion.isdigit() or not (1 <= int(seleccion) <= len(usuarios)):
            print("Opcion invalida.")
            return

        usuario_elegido = usuarios[int(seleccion) - 1]

        pagina = 0
        limite = 10

        while True:
            pipeline = [
                {"$match": {"usuarioId": usuario_elegido["_id"]}},
                {"$lookup": {
                    "from": "usuarios",
                    "localField": "usuarioId",
                    "foreignField": "_id",
                    "as": "usuario"
                }},
                {"$unwind": "$usuario"},
                {"$lookup": {
                    "from": "restaurantes",
                    "localField": "restauranteId",
                    "foreignField": "_id",
                    "as": "restaurante"
                }},
                {"$unwind": "$restaurante"},
                {"$project": {
                    "_id": 0,
                    "ordenId": "$_id",
                    "usuario": "$usuario.nombre",
                    "restaurante": "$restaurante.nombre",
                    "estado": 1,
                    "total": 1,
                    "fechaCreacion": 1
                }},
                {"$sort": {"fechaCreacion": -1}},
                {"$skip": pagina * limite},
                {"$limit": limite}
            ]

            resultados = list(db["ordenes"].aggregate(pipeline))

            if not resultados:
                if pagina > 0:
                    print("No hay mas ordenes.")
                    pagina -= 1
                    continue
                else:
                    print("Este usuario no tiene ordenes.")
                    break

            print(f"\n--- ORDENES DE {usuario_elegido.get('nombre')} | Pagina {pagina + 1} ---")
            for r in resultados:
                print(r)

            print("\nOpciones:")
            print("n = siguiente pagina")
            print("p = pagina anterior")
            print("m = volver al menu de reportes")

            opcion_pagina = input("Selecciona una opcion: ").lower()

            if opcion_pagina == 'n':
                pagina += 1
            elif opcion_pagina == 'p':
                if pagina > 0:
                    pagina -= 1
                else:
                    print("Ya estas en la primera pagina.")
            elif opcion_pagina == 'm':
                break
            else:
                print("Opcion invalida.")

    else:
        print("❌ Opción inválida.")
