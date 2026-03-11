def consultar_catalogo_restaurantes(db):
    """
    Realiza una consulta multi-colección (lookup) con:
    Filtros dinámicos, Proyecciones ($size), Sort, Skip y Límite dinámicos.
    """
    print("\n" + "-"*40)
    print("   CATÁLOGO DE RESTAURANTES   ")
    print("-"*40)

    try:
        # --- 1. FILTRO DINÁMICO (Categoría) ---
        categorias_unicas = db["restaurantes"].distinct("categorias")
        categoria_filtro = None
        
        if categorias_unicas:
            print("\nCategorías disponibles:")
            print("0. 🌟 Mostrar TODOS (Sin filtro)")
            for i, categoria in enumerate(categorias_unicas, start=1):
                print(f"{i}. 🍔 {categoria}")

            seleccion = input(f"\nSelecciona una categoría (0-{len(categorias_unicas)}): ")
            if seleccion.isdigit() and 1 <= int(seleccion) <= len(categorias_unicas):
                categoria_filtro = categorias_unicas[int(seleccion) - 1]
                print(f"\nFiltro aplicado: '{categoria_filtro}'")
            else:
                print("\nBuscando todos por defecto...")

        # --- 2. PAGINACIÓN DINÁMICA (Limit y Skip) ---
        try:
            limite_input = input("\n¿Cuántos restaurantes deseas ver por página? (Default 5): ")
            limite = int(limite_input) if limite_input.strip() else 5
        except ValueError:
            limite = 5
            
        try:
            pagina_input = input("¿Qué página deseas ver? (Default 1): ")
            pagina = int(pagina_input) if pagina_input.strip() else 1
        except ValueError:
            pagina = 1

        # Cálculo matemático del skip
        skip = (pagina - 1) * limite

        # --- 3. CONSTRUCCIÓN DEL PIPELINE ---
        pipeline = []

        if categoria_filtro:
            pipeline.append({"$match": {"categorias": categoria_filtro}})

        pipeline.append({
            "$lookup": {
                "from": "articulosMenu",       
                "localField": "_id",           
                "foreignField": "restauranteId", 
                "as": "platillos"              
            }
        })

        pipeline.append({"$sort": {"nombre": 1}})
        pipeline.append({"$skip": skip})
        pipeline.append({"$limit": limite})

        pipeline.append({
            "$project": {
                "_id": 0,                      
                "nombre": 1,                   
                "categorias": 1, 
                "total_platillos": {"$size": "$platillos"}, # Proyección avanzada: Cuenta el arreglo
                "platillos.nombre": 1,         
                "platillos.precio": 1          
            }
        })

        # --- 4. EJECUCIÓN ---
        resultados = list(db["restaurantes"].aggregate(pipeline))

        if not resultados:
            print(f"\nNo se encontraron resultados en la página {pagina}.")
            return

        print(f"\n--- Resultados (Página {pagina} | Mostrando hasta {limite} restaurantes) ---")
        for rest in resultados:
            print(f"\n🏢 Restaurante: {rest.get('nombre')}")
            print(f"   Categorías: {', '.join(rest.get('categorias', []))}")
            print(f"   Cantidad de platillos en menú: {rest.get('total_platillos', 0)}")
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