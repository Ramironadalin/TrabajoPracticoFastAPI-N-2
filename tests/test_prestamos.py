"""Reglas de negocio 1 a 7: caso feliz y caso de error de cada una."""
from datetime import date, timedelta


def stock_de(client, libro_id):
    return client.get(f"/libros/{libro_id}").json()["stock"]


# ---------- Regla 1: máximo 3 préstamos activos ----------
def test_regla1_hasta_3_prestamos_activos_ok(client, crear_socio, crear_libro, prestar):
    socio, libro = crear_socio(), crear_libro(stock=10)
    for _ in range(3):
        assert prestar(socio["id"], libro["id"]).status_code == 201


def test_regla1_cuarto_prestamo_409(client, crear_socio, crear_libro, prestar):
    socio, libro = crear_socio(), crear_libro(stock=10)
    for _ in range(3):
        prestar(socio["id"], libro["id"])
    r = prestar(socio["id"], libro["id"])
    assert r.status_code == 409
    assert stock_de(client, libro["id"]) == 7  # el rechazado no descontó stock


def test_regla1_devolver_libera_cupo(client, crear_socio, crear_libro, prestar):
    socio, libro = crear_socio(), crear_libro(stock=10)
    ids = [prestar(socio["id"], libro["id"]).json()["id"] for _ in range(3)]
    client.post(f"/prestamos/{ids[0]}/devolucion")
    assert prestar(socio["id"], libro["id"]).status_code == 201


def test_regla1_el_limite_es_por_socio(crear_socio, crear_libro, prestar):
    a, b = crear_socio(email="a@m.com"), crear_socio(email="b@m.com")
    libro = crear_libro(stock=10)
    for _ in range(3):
        prestar(a["id"], libro["id"])
    assert prestar(b["id"], libro["id"]).status_code == 201


# ---------- Regla 2: stock ----------
def test_regla2_prestar_descuenta_stock(client, crear_socio, crear_libro, prestar):
    socio, libro = crear_socio(), crear_libro(stock=2)
    assert prestar(socio["id"], libro["id"]).status_code == 201
    assert stock_de(client, libro["id"]) == 1


def test_regla2_sin_stock_409(client, crear_socio, crear_libro, prestar):
    socio, libro = crear_socio(), crear_libro(stock=1)
    assert prestar(socio["id"], libro["id"]).status_code == 201
    assert prestar(socio["id"], libro["id"]).status_code == 409
    assert stock_de(client, libro["id"]) == 0


def test_regla2_libro_con_stock_cero_desde_el_alta(crear_socio, crear_libro, prestar):
    socio, libro = crear_socio(), crear_libro(stock=0)
    assert prestar(socio["id"], libro["id"]).status_code == 409


# ---------- Regla 3: socio inactivo ----------
def test_regla3_socio_inactivo_403(client, crear_socio, crear_libro, prestar):
    socio, libro = crear_socio(activo=False), crear_libro()
    assert prestar(socio["id"], libro["id"]).status_code == 403
    assert stock_de(client, libro["id"]) == 5


def test_regla3_socio_reactivado_puede_pedir(client, crear_socio, crear_libro, prestar):
    socio, libro = crear_socio(activo=False), crear_libro()
    client.patch(f"/socios/{socio['id']}", json={"activo": True})
    assert prestar(socio["id"], libro["id"]).status_code == 201


# ---------- Regla 4: plazo de 14 días ----------
def test_regla4_vencimiento_a_14_dias(crear_socio, crear_libro, prestar, reloj):
    socio, libro = crear_socio(), crear_libro()
    p = prestar(socio["id"], libro["id"]).json()
    assert p["fecha_prestamo"] == reloj["hoy"].isoformat()
    assert p["fecha_vencimiento"] == (reloj["hoy"] + timedelta(days=14)).isoformat()
    assert p["fecha_devolucion"] is None
    assert p["multa"] == 0


# ---------- Regla 5: devolución, stock y multa ----------
def test_regla5_devolucion_a_tiempo_sin_multa_y_repone_stock(
    client, crear_socio, crear_libro, prestar, reloj
):
    socio, libro = crear_socio(), crear_libro(stock=1)
    p = prestar(socio["id"], libro["id"]).json()
    reloj["hoy"] = date(2026, 1, 15)  # justo el día del vencimiento
    r = client.post(f"/prestamos/{p['id']}/devolucion")
    assert r.status_code == 200
    assert r.json()["multa"] == 0
    assert r.json()["fecha_devolucion"] == "2026-01-15"
    assert stock_de(client, libro["id"]) == 1


def test_regla5_devolucion_antes_de_tiempo_sin_multa(client, crear_socio, crear_libro, prestar, reloj):
    socio, libro = crear_socio(), crear_libro()
    p = prestar(socio["id"], libro["id"]).json()
    reloj["hoy"] = date(2026, 1, 3)
    assert client.post(f"/prestamos/{p['id']}/devolucion").json()["multa"] == 0


def test_regla5_multa_100_por_dia_de_atraso(client, crear_socio, crear_libro, prestar, reloj):
    socio, libro = crear_socio(), crear_libro()
    p = prestar(socio["id"], libro["id"]).json()
    reloj["hoy"] = date(2026, 1, 18)  # vence el 15 → 3 días de atraso
    r = client.post(f"/prestamos/{p['id']}/devolucion")
    assert r.status_code == 200
    assert r.json()["multa"] == 300


def test_regla5_un_dia_de_atraso(client, crear_socio, crear_libro, prestar, reloj):
    socio, libro = crear_socio(), crear_libro()
    p = prestar(socio["id"], libro["id"]).json()
    reloj["hoy"] = date(2026, 1, 16)
    assert client.post(f"/prestamos/{p['id']}/devolucion").json()["multa"] == 100


# ---------- Regla 6: no devolver dos veces ----------
def test_regla6_doble_devolucion_409(client, crear_socio, crear_libro, prestar):
    socio, libro = crear_socio(), crear_libro(stock=1)
    p = prestar(socio["id"], libro["id"]).json()
    assert client.post(f"/prestamos/{p['id']}/devolucion").status_code == 200
    assert client.post(f"/prestamos/{p['id']}/devolucion").status_code == 409
    assert stock_de(client, libro["id"]) == 1  # no se repuso dos veces


# ---------- Regla 7: inexistentes ----------
def test_regla7_prestamo_con_socio_inexistente_404(crear_libro, prestar):
    libro = crear_libro()
    assert prestar(999, libro["id"]).status_code == 404


def test_regla7_prestamo_con_libro_inexistente_404(crear_socio, prestar):
    socio = crear_socio()
    assert prestar(socio["id"], 999).status_code == 404


def test_regla7_devolucion_de_prestamo_inexistente_404(client):
    assert client.post("/prestamos/999/devolucion").status_code == 404
    assert client.get("/prestamos/999").status_code == 404


# ---------- Consultas ----------
def test_listar_prestamos(client, crear_socio, crear_libro, prestar):
    a, b = crear_socio(email="a@m.com"), crear_socio(email="b@m.com")
    libro = crear_libro(stock=10)
    p1 = prestar(a["id"], libro["id"]).json()
    p2 = prestar(b["id"], libro["id"]).json()
    client.post(f"/prestamos/{p1['id']}/devolucion")

    todos = client.get("/prestamos").json()
    activos = client.get("/prestamos?activos=true").json()
    assert [p["id"] for p in todos] == [p1["id"], p2["id"]]
    assert [p["id"] for p in activos] == [p2["id"]]


def test_obtener_prestamo(client, crear_socio, crear_libro, prestar):
    socio, libro = crear_socio(), crear_libro()
    p = prestar(socio["id"], libro["id"]).json()
    assert client.get(f"/prestamos/{p['id']}").json()["id"] == p["id"]


def test_prestamos_activos_del_socio(client, crear_socio, crear_libro, prestar):
    socio, libro = crear_socio(), crear_libro(stock=10)
    p1 = prestar(socio["id"], libro["id"]).json()
    prestar(socio["id"], libro["id"])
    client.post(f"/prestamos/{p1['id']}/devolucion")

    todos = client.get(f"/socios/{socio['id']}/prestamos").json()
    activos = client.get(f"/socios/{socio['id']}/prestamos?activos=true").json()
    assert len(todos) == 2
    assert len(activos) == 1
    assert activos[0]["fecha_devolucion"] is None


def test_prestamos_activos_no_mezcla_socios(client, crear_socio, crear_libro, prestar):
    a, b = crear_socio(email="a@m.com"), crear_socio(email="b@m.com")
    libro = crear_libro(stock=10)
    prestar(a["id"], libro["id"])
    assert client.get(f"/socios/{b['id']}/prestamos?activos=true").json() == []
