def consultar_catalogo_restaurantes(db):
    """
    Realiza una consulta multi-colección (lookup) cumpliendo con:
    Filtros, Proyecciones, Sort, Skip y Límite[cite: 131].
    Incluye un submenú dinámico de categorías usando distinct().
    """
    print("\n" + "-"*40)
    print("   CATÁLOGO DE RESTAURANTES   ")
    print("-"*40)

    try:
        # 1. Obtener todas las categorías únicas de la base de datos
        categorias_unicas = db["restaurantes"].distinct("categorias")
        
        if not categorias_unicas:
            print("No hay categorías registradas en la base de datos.")
            return

        # 2. Generar el submenú dinámico
        print("\nCategorías disponibles:")
        print("0. 🌟 Mostrar TODOS (Sin filtro)")
        for i, categoria in enumerate(categorias_unicas, start=1):
            print(f"{i}.  {categoria}")

        # 3. Capturar y validar la selección del usuario
        seleccion = input(f"\nSelecciona una opción (0-{len(categorias_unicas)}): ")
        
        categoria_filtro = None
        if seleccion.isdigit():
            opc = int(seleccion)
            if 1 <= opc <= len(categorias_unicas):
                categoria_filtro = categorias_unicas[opc - 1]
                print(f"\nBuscando restaurantes en la categoría: '{categoria_filtro}'...")
            elif opc == 0:
                print("\nBuscando todos los restaurantes...")
            else:
                print("\nOpción fuera de rango. Buscando todos por defecto...")
        else:
            print("\nEntrada inválida. Buscando todos por defecto...")

        # 4. Construir el pipeline de agregación [cite: 131]
        pipeline = []

        # Filtro ($match) - Solo se agrega si el usuario eligió una categoría específica
        if categoria_filtro:
            pipeline.append({"$match": {"categorias": categoria_filtro}})

        # Multi-colección ($lookup) -> Unir Restaurantes con ArticulosMenu [cite: 131]
        pipeline.append({
            "$lookup": {
                "from": "articulosMenu",       
                "localField": "_id",           
                "foreignField": "restauranteId", 
                "as": "platillos"              
            }
        })

        # Ordenamiento ($sort) -> Alfabético por nombre del restaurante [cite: 131]
        pipeline.append({"$sort": {"nombre": 1}})

        # Skip y Límite ($skip, $limit) -> Paginación [cite: 131]
        pipeline.append({"$skip": 0})
        pipeline.append({"$limit": 5})

        # Proyección ($project) -> Mostrar solo la información necesaria [cite: 131]
        pipeline.append({
            "$project": {
                "_id": 0,                      
                "nombre": 1,                   
                "categorias": 1,               
                "platillos.nombre": 1,         
                "platillos.precio": 1          
            }
        })

        # 5. Ejecutar la consulta
        resultados = list(db["restaurantes"].aggregate(pipeline))

        if not resultados:
            print("No se encontraron restaurantes con esos criterios.")
            return

        # 6. Imprimir los resultados de forma amigable
        print(f"\nSe encontraron {len(resultados)} restaurante(s) (Mostrando máx 5):")
        for rest in resultados:
            print(f"\n Restaurante: {rest.get('nombre')}")
            print(f"   Categorías: {', '.join(rest.get('categorias', []))}")
            print("   Menú:")
            platillos = rest.get('platillos', [])
            if platillos:
                for platillo in platillos:
                    print(f"     - {platillo.get('nombre')} (Q{platillo.get('precio')})")
            else:
                print("     - No hay platillos registrados aún.")
        print("-"*40)

    except Exception as e:
        print(f"Error al realizar la consulta: {e}")