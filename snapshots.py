from gridfs import GridFS
from bson.objectid import ObjectId
from datetime import datetime
import json


# -------------------------------------------------
# CONVERTIR OBJETOS A FORMATO JSON SERIALIZABLE
# -------------------------------------------------

def convertir_a_json_serializable(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, list):
        return [convertir_a_json_serializable(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: convertir_a_json_serializable(v) for k, v in obj.items()}
    else:
        return obj


# -------------------------------------------------
# SELECCIONAR ORDEN CON PAGINACION
# -------------------------------------------------

def seleccionar_orden_paginado(db):

    pagina = 0
    limite = 10

    while True:

        ordenes = list(
            db["ordenes"]
            .find()
            .sort("fechaCreacion", -1)
            .skip(pagina * limite)
            .limit(limite)
        )

        if not ordenes:
            print("No hay mas ordenes.")
            if pagina > 0:
                pagina -= 1
            continue

        print("\n--- ORDENES (pagina", pagina + 1, ") ---")

        for i, orden in enumerate(ordenes, start=1):
            print(
                f"{i}. ID: {orden['_id']} | "
                f"Estado: {orden.get('estado')} | "
                f"Total: Q{orden.get('total',0)}"
            )

        print("\nn = siguiente pagina")
        print("p = pagina anterior")
        print("0 = cancelar")

        opcion = input("Selecciona una orden: ")

        if opcion == "n":
            pagina += 1
            continue

        elif opcion == "p":
            if pagina > 0:
                pagina -= 1
            continue

        elif opcion == "0":
            return None

        elif opcion.isdigit() and 1 <= int(opcion) <= len(ordenes):
            return ordenes[int(opcion) - 1]

        else:
            print("Opcion invalida.")


# -------------------------------------------------
# CREAR SNAPSHOT
# -------------------------------------------------

def crear_snapshot_orden(db, fs):

    orden = seleccionar_orden_paginado(db)

    if not orden:
        return

    snapshot_documento = {
        "tipoSnapshot": "orden",
        "fechaSnapshot": datetime.utcnow(),
        "documentoOriginal": orden
    }

    snapshot_serializable = convertir_a_json_serializable(snapshot_documento)

    contenido_json = json.dumps(
        snapshot_serializable,
        indent=4,
        ensure_ascii=False
    )

    nombre_archivo = f"snapshot_orden_{str(orden['_id'])}.json"

    try:

        file_id = fs.put(
            contenido_json.encode("utf-8"),
            filename=nombre_archivo,
            metadata={
                "tipo": "snapshot_transaccion",
                "ordenId": str(orden["_id"]),
                "fechaSnapshot": datetime.utcnow().isoformat()
            }
        )

        db["snapshotsTransacciones"].insert_one({
            "ordenId": orden["_id"],
            "fechaSnapshot": datetime.utcnow(),
            "snapshotFileId": file_id,
            "nombreArchivo": nombre_archivo,
            "estadoOrden": orden.get("estado"),
            "totalOrden": orden.get("total")
        })

        print("\nSnapshot creado correctamente.")
        print("Archivo guardado en GridFS con ID:", file_id)

    except Exception as e:
        print("Error al crear snapshot:", e)


# -------------------------------------------------
# LISTAR SNAPSHOTS
# -------------------------------------------------

def listar_snapshots(db):

    snapshots = list(
        db["snapshotsTransacciones"]
        .find()
        .sort("fechaSnapshot", -1)
    )

    if not snapshots:
        print("No hay snapshots.")
        return

    print("\n--- SNAPSHOTS ---")

    for i, s in enumerate(snapshots, start=1):

        print(f"{i}. Orden ID: {s.get('ordenId')}")
        print(f"   Fecha: {s.get('fechaSnapshot')}")
        print(f"   Estado: {s.get('estadoOrden')}")
        print(f"   Total: Q{s.get('totalOrden')}")
        print(f"   GridFS ID: {s.get('snapshotFileId')}")
        print("-" * 40)


# -------------------------------------------------
# DESCARGAR SNAPSHOT
# -------------------------------------------------

def descargar_snapshot(db, fs):

    snapshots = list(
        db["snapshotsTransacciones"]
        .find()
        .sort("fechaSnapshot", -1)
    )

    if not snapshots:
        print("No hay snapshots.")
        return

    for i, s in enumerate(snapshots, start=1):
        print(f"{i}. {s['nombreArchivo']}")

    opcion = input("Selecciona snapshot: ")

    if not opcion.isdigit() or not (1 <= int(opcion) <= len(snapshots)):
        print("Opcion invalida")
        return

    snapshot = snapshots[int(opcion) - 1]

    ruta = input("Ruta donde guardar el JSON: ")

    try:

        archivo = fs.get(snapshot["snapshotFileId"])

        with open(ruta, "wb") as f:
            f.write(archivo.read())

        print("Snapshot descargado correctamente.")

    except Exception as e:
        print("Error:", e)


# -------------------------------------------------
# ELIMINAR SNAPSHOT
# -------------------------------------------------

def eliminar_snapshot(db, fs):

    snapshots = list(
        db["snapshotsTransacciones"]
        .find()
        .sort("fechaSnapshot", -1)
    )

    if not snapshots:
        print("No hay snapshots.")
        return

    for i, s in enumerate(snapshots, start=1):
        print(f"{i}. {s['nombreArchivo']}")

    opcion = input("Selecciona snapshot: ")

    if not opcion.isdigit() or not (1 <= int(opcion) <= len(snapshots)):
        print("Opcion invalida")
        return

    snapshot = snapshots[int(opcion) - 1]

    try:

        fs.delete(snapshot["snapshotFileId"])

        db["snapshotsTransacciones"].delete_one(
            {"_id": snapshot["_id"]}
        )

        print("Snapshot eliminado.")

    except Exception as e:
        print("Error:", e)


# -------------------------------------------------
# MENU PRINCIPAL SNAPSHOTS
# -------------------------------------------------

def manejar_snapshots_gridfs(db):

    fs = GridFS(db)

    while True:

        print("\n" + "-" * 55)
        print("SNAPSHOTS DE TRANSACCIONES (GRIDFS)")
        print("-" * 55)
        print("1. Crear snapshot de orden")
        print("2. Listar snapshots")
        print("3. Descargar snapshot")
        print("4. Eliminar snapshot")
        print("5. Volver")

        opcion = input("Selecciona una opcion: ")

        if opcion == "1":
            crear_snapshot_orden(db, fs)

        elif opcion == "2":
            listar_snapshots(db)

        elif opcion == "3":
            descargar_snapshot(db, fs)

        elif opcion == "4":
            eliminar_snapshot(db, fs)

        elif opcion == "5":
            break

        else:
            print("Opcion invalida.")