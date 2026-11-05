"""CRUD, relaciones N-N y reglas 7 y 8."""


# ---------- Autores ----------
def test_crud_autor(client):
    r = client.post("/autores", json={"nombre": "Cortázar", "nacionalidad": "Argentina"})
    assert r.status_code == 201
    id_ = r.json()["id"]

    assert client.get(f"/autores/{id_}").json()["nombre"] == "Cortázar"
    assert len(client.get("/autores").json()) == 1

    r = client.patch(f"/autores/{id_}", json={"nacionalidad": "Belga"})
    assert r.status_code == 200 and r.json()["nacionalidad"] == "Belga"
    assert r.json()["nombre"] == "Cortázar"  # el parcial no pisa lo demás

    assert client.delete(f"/autores/{id_}").status_code == 204
    assert client.get(f"/autores/{id_}").status_code == 404


def test_autor_inexistente_404(client):
    assert client.get("/autores/99").status_code == 404
    assert client.patch("/autores/99", json={"nombre": "x"}).status_code == 404
    assert client.delete("/autores/99").status_code == 404


# ---------- Libros ----------
def test_crud_libro(client):
    r = client.post("/libros", json={"titulo": "Rayuela", "isbn": "1", "stock": 2, "anio": 1963})
    assert r.status_code == 201
    id_ = r.json()["id"]
    assert r.json()["autores"] == []

    assert client.get(f"/libros/{id_}").json()["titulo"] == "Rayuela"
    r = client.patch(f"/libros/{id_}", json={"stock": 7})
    assert r.status_code == 200 and r.json()["stock"] == 7
    assert client.delete(f"/libros/{id_}").status_code == 204
    assert client.get(f"/libros/{id_}").status_code == 404


def test_libro_inexistente_404(client):
    assert client.get("/libros/99").status_code == 404
    assert client.patch("/libros/99", json={"stock": 1}).status_code == 404
    assert client.delete("/libros/99").status_code == 404


def test_stock_negativo_es_422(client):
    r = client.post("/libros", json={"titulo": "X", "isbn": "1", "stock": -1})
    assert r.status_code == 422
    libro = client.post("/libros", json={"titulo": "X", "isbn": "2", "stock": 1}).json()
    assert client.patch(f"/libros/{libro['id']}", json={"stock": -5}).status_code == 422


def test_isbn_duplicado_409(client, crear_libro):
    crear_libro(isbn="DUP")
    r = client.post("/libros", json={"titulo": "Otro", "isbn": "DUP", "stock": 1})
    assert r.status_code == 409


def test_actualizar_isbn_a_uno_existente_409(client, crear_libro):
    crear_libro(isbn="A")
    b = crear_libro(isbn="B")
    assert client.patch(f"/libros/{b['id']}", json={"isbn": "A"}).status_code == 409
    # y la sesión sigue usable tras el rollback
    assert client.get(f"/libros/{b['id']}").json()["isbn"] == "B"


def test_listar_libros_disponibles(client, crear_libro):
    crear_libro(isbn="1", stock=3)
    crear_libro(isbn="2", stock=0)
    todos = client.get("/libros").json()
    disponibles = client.get("/libros?disponibles=true").json()
    no_disponibles = client.get("/libros?disponibles=false").json()
    assert len(todos) == 2
    assert [l["isbn"] for l in disponibles] == ["1"]
    assert [l["isbn"] for l in no_disponibles] == ["2"]


# ---------- Socios ----------
def test_crud_socio(client):
    r = client.post("/socios", json={"nombre": "Ana", "email": "ana@mail.com"})
    assert r.status_code == 201 and r.json()["activo"] is True
    id_ = r.json()["id"]

    assert client.get(f"/socios/{id_}").json()["email"] == "ana@mail.com"
    assert len(client.get("/socios").json()) == 1
    r = client.patch(f"/socios/{id_}", json={"activo": False})
    assert r.json()["activo"] is False
    assert client.delete(f"/socios/{id_}").status_code == 204
    assert client.get(f"/socios/{id_}").status_code == 404


def test_socio_inexistente_404(client):
    assert client.get("/socios/99").status_code == 404
    assert client.patch("/socios/99", json={"activo": False}).status_code == 404
    assert client.delete("/socios/99").status_code == 404
    assert client.get("/socios/99/prestamos").status_code == 404


def test_email_duplicado_409(client, crear_socio):
    crear_socio(email="dup@mail.com")
    r = client.post("/socios", json={"nombre": "Otra", "email": "dup@mail.com"})
    assert r.status_code == 409


def test_actualizar_email_a_uno_existente_409(client, crear_socio):
    crear_socio(email="a@mail.com")
    b = crear_socio(email="b@mail.com")
    assert client.patch(f"/socios/{b['id']}", json={"email": "a@mail.com"}).status_code == 409


# ---------- Relación N-N ----------
def test_asociar_autor_y_ver_autores_en_libro(client, crear_libro):
    libro = crear_libro()
    a1 = client.post("/autores", json={"nombre": "A1"}).json()
    a2 = client.post("/autores", json={"nombre": "A2"}).json()

    r = client.post(f"/libros/{libro['id']}/autores/{a1['id']}")
    assert r.status_code == 200
    client.post(f"/libros/{libro['id']}/autores/{a2['id']}")

    autores = client.get(f"/libros/{libro['id']}").json()["autores"]
    assert {a["nombre"] for a in autores} == {"A1", "A2"}
    # el listado también incluye autores
    assert len(client.get("/libros").json()[0]["autores"]) == 2


def test_un_autor_en_varios_libros(client, crear_libro):
    l1, l2 = crear_libro(isbn="1"), crear_libro(isbn="2")
    a = client.post("/autores", json={"nombre": "A"}).json()
    client.post(f"/libros/{l1['id']}/autores/{a['id']}")
    client.post(f"/libros/{l2['id']}/autores/{a['id']}")
    assert len(client.get(f"/libros/{l1['id']}").json()["autores"]) == 1
    assert len(client.get(f"/libros/{l2['id']}").json()["autores"]) == 1


def test_asociar_autor_duplicado_409(client, crear_libro):
    libro = crear_libro()
    a = client.post("/autores", json={"nombre": "A"}).json()
    assert client.post(f"/libros/{libro['id']}/autores/{a['id']}").status_code == 200
    assert client.post(f"/libros/{libro['id']}/autores/{a['id']}").status_code == 409


def test_asociar_autor_inexistente_404(client, crear_libro):
    libro = crear_libro()
    a = client.post("/autores", json={"nombre": "A"}).json()
    assert client.post(f"/libros/99/autores/{a['id']}").status_code == 404
    assert client.post(f"/libros/{libro['id']}/autores/99").status_code == 404


def test_borrar_autor_asociado_no_rompe_el_libro(client, crear_libro):
    libro = crear_libro()
    a = client.post("/autores", json={"nombre": "A"}).json()
    client.post(f"/libros/{libro['id']}/autores/{a['id']}")
    assert client.delete(f"/autores/{a['id']}").status_code == 204
    assert client.get(f"/libros/{libro['id']}").json()["autores"] == []


def test_borrar_libro_con_autores(client, crear_libro):
    libro = crear_libro()
    a = client.post("/autores", json={"nombre": "A"}).json()
    client.post(f"/libros/{libro['id']}/autores/{a['id']}")
    assert client.delete(f"/libros/{libro['id']}").status_code == 204
    assert client.get(f"/autores/{a['id']}").status_code == 200


# ---------- Integridad ----------
def test_no_se_borra_libro_ni_socio_con_prestamos(client, crear_socio, crear_libro, prestar):
    socio, libro = crear_socio(), crear_libro()
    assert prestar(socio["id"], libro["id"]).status_code == 201
    assert client.delete(f"/libros/{libro['id']}").status_code == 409
    assert client.delete(f"/socios/{socio['id']}").status_code == 409
