import json
import random
from datetime import datetime, timedelta
from pathlib import Path

BASE = Path(".")

USUARIOS_FILE = BASE / "proyectoBD2.usuarios.json"
ARTICULOS_FILE = BASE / "proyectoBD2.articulosMenu.json"
ORDENES_EXISTENTES_FILE = BASE / "proyectoBD2.ordenes.json"
SALIDA_FILE = BASE / "proyectoBD2.ordenes.generadas.json"

CANTIDAD_NUEVA = 49849

ESTADOS = ["PENDIENTE", "CONFIRMADA", "ENTREGADA", "CANCELADA"]
PESOS_ESTADO = [0.20, 0.25, 0.45, 0.10]

FECHA_INICIO = datetime(2025, 1, 1)
FECHA_FIN = datetime(2026, 3, 31)

random.seed(42)


def cargar_json(ruta):
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def generar_oid_hex():
    caracteres = "0123456789abcdef"
    return "".join(random.choice(caracteres) for _ in range(24))


def fecha_random(inicio, fin):
    delta = fin - inicio
    segundos = int(delta.total_seconds())
    offset = random.randint(0, segundos)
    dt = inicio + timedelta(seconds=offset)
    return dt.replace(microsecond=0).isoformat() + ".000Z"


def round2(valor):
    return round(valor + 1e-9, 2)


usuarios = cargar_json(USUARIOS_FILE)
articulos = cargar_json(ARTICULOS_FILE)
ordenes_existentes = cargar_json(ORDENES_EXISTENTES_FILE)

usuario_ids = [u["_id"]["$oid"] for u in usuarios]

# Agrupar articulos por restaurante
articulos_por_restaurante = {}
for art in articulos:
    rest_id = art["restauranteId"]["$oid"]
    articulos_por_restaurante.setdefault(rest_id, []).append(art)

restaurante_ids = list(articulos_por_restaurante.keys())

nuevas_ordenes = []

for _ in range(CANTIDAD_NUEVA):
    restaurante_id = random.choice(restaurante_ids)
    usuario_id = random.choice(usuario_ids)

    catalogo = articulos_por_restaurante[restaurante_id]
    max_items = min(4, len(catalogo))
    cantidad_items = random.randint(1, max_items)

    articulos_elegidos = random.sample(catalogo, cantidad_items)

    items = []
    total = 0.0

    for art in articulos_elegidos:
        cantidad = random.randint(1, 3)
        precio = float(art["precio"])
        subtotal = round2(precio * cantidad)

        item = {
            "articuloId": {"$oid": art["_id"]["$oid"]},
            "nombreSnapshot": art["nombre"],
            "precioUnitarioSnapshot": round2(precio),
            "cantidad": cantidad,
            "subtotal": subtotal
        }

        items.append(item)
        total += subtotal

    orden = {
        "_id": {"$oid": generar_oid_hex()},
        "usuarioId": {"$oid": usuario_id},
        "restauranteId": {"$oid": restaurante_id},
        "estado": random.choices(ESTADOS, weights=PESOS_ESTADO, k=1)[0],
        "total": round2(total),
        "fechaCreacion": {"$date": fecha_random(FECHA_INICIO, FECHA_FIN)},
        "items": items
    }

    nuevas_ordenes.append(orden)

with open(SALIDA_FILE, "w", encoding="utf-8") as f:
    json.dump(nuevas_ordenes, f, ensure_ascii=False, indent=2)

print(f"Se generaron {len(nuevas_ordenes)} órdenes en: {SALIDA_FILE}")