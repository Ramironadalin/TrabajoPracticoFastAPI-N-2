# Sistema de Biblioteca (FastAPI + SQLModel)

API REST para gestionar el catálogo de una biblioteca y sus préstamos.

## Estructura

```
app/
  main.py          # app FastAPI + traducción de errores de dominio a HTTP
  database.py      # engine y sesión (SQLite por defecto)
  dependencies.py  # get_hoy(): fecha actual inyectable (facilita testear multas)
  models/          # tablas SQLModel y schemas (Create / Update / Read)
  routers/         # capa HTTP: solo parsea, delega y responde
  services/        # lógica y reglas de negocio (sin dependencia de FastAPI)
tests/             # pytest con SQLite en memoria
```

## Cómo correr

```bash
python -m venv .venv && source .venv/bin/activate   # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Documentación interactiva en http://127.0.0.1:8000/docs.
La base queda en `biblioteca.db` (cambiable con la variable `DATABASE_URL`).

## Cómo testear

```bash
pytest
```

Usa una base SQLite en memoria (no toca `biblioteca.db`) y muestra la cobertura
(`--cov` está configurado en `pytest.ini`).

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| POST/GET | `/autores`, `/libros`, `/socios` | Alta y listado |
| GET/PATCH/DELETE | `/autores/{id}`, `/libros/{id}`, `/socios/{id}` | Consulta, modificación parcial y baja |
| POST | `/libros/{id}/autores/{autor_id}` | Asocia un autor a un libro |
| GET | `/libros?disponibles=true` | Libros con stock > 0 |
| POST | `/prestamos` | Registra un préstamo (`{"socio_id", "libro_id"}`) |
| GET | `/prestamos` | Lista los préstamos (solo activos si `activos=true`) |
| GET | `/prestamos/{id}` | Consulta un préstamo |
| POST | `/prestamos/{id}/devolucion` | Registra la devolución |
| GET | `/socios/{id}/prestamos?activos=true` | Préstamos del socio (solo activos si `activos=true`) |

## Reglas de negocio y códigos HTTP

| # | Regla | Código |
|---|---|---|
| 1 | Máximo 3 préstamos activos por socio | 409 |
| 2 | Sin stock no se presta; prestar descuenta 1 | 409 |
| 3 | Socio inactivo no puede pedir préstamos | 403 |
| 4 | Vencimiento = fecha de préstamo + 14 días | — |
| 5 | Al devolver se repone stock; multa = $100 × días de atraso | — |
| 6 | No se devuelve dos veces el mismo préstamo | 409 |
| 7 | Recurso inexistente | 404 |
| 8 | ISBN o email duplicado | 409 |

Orden de validación al prestar: 404 → 403 (inactivo) → 409 (límite de 3) → 409 (sin stock).

## Decisiones de diseño

- Las reglas viven en `services/`; los routers no tienen `if` de negocio.
- Los servicios lanzan errores de dominio (`NoEncontrado`, `Conflicto`, `Prohibido`) y
  `main.py` los mapea a 404 / 409 / 403.
- Las unicidades (ISBN, email) se garantizan con índices únicos en la base; el servicio
  captura `IntegrityError`, hace rollback y responde 409.
- No se puede borrar un libro o socio con préstamos asociados (409), para no perder historial.
- Un autor ya asociado a un libro devuelve 409 si se intenta asociar de nuevo.
- La fecha actual se inyecta (`get_hoy`), así los tests simulan atrasos sin esperar días.
