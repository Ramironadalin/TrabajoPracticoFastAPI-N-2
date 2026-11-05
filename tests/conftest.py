from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.database import get_session
from app.dependencies import get_hoy
from app.main import app

HOY_INICIAL = date(2026, 1, 1)


@pytest.fixture
def reloj():
    """Fecha 'actual' de la API; los tests la mueven para simular atrasos."""
    return {"hoy": HOY_INICIAL}


@pytest.fixture
def client(reloj):
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)

    def session_override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = session_override
    app.dependency_overrides[get_hoy] = lambda: reloj["hoy"]
    yield TestClient(app)  # sin 'with': no corre el lifespan (no toca la DB real)
    app.dependency_overrides.clear()


@pytest.fixture
def crear_socio(client):
    def _crear(email="ana@mail.com", activo=True, nombre="Ana"):
        r = client.post("/socios", json={"nombre": nombre, "email": email, "activo": activo})
        assert r.status_code == 201
        return r.json()

    return _crear


@pytest.fixture
def crear_libro(client):
    def _crear(isbn="978-0", stock=5, titulo="Rayuela"):
        r = client.post("/libros", json={"titulo": titulo, "isbn": isbn, "stock": stock, "anio": 1963})
        assert r.status_code == 201
        return r.json()

    return _crear


@pytest.fixture
def prestar(client):
    def _prestar(socio_id, libro_id):
        return client.post("/prestamos", json={"socio_id": socio_id, "libro_id": libro_id})

    return _prestar
