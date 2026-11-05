from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse

from .database import crear_tablas
from .exceptions import Conflicto, ErrorDominio, NoEncontrado, Prohibido
from .routers import autores, libros, prestamos, socios

CODIGOS = {NoEncontrado: 404, Conflicto: 409, Prohibido: 403}


@asynccontextmanager
async def lifespan(app: FastAPI):
    crear_tablas()
    yield


app = FastAPI(title="Biblioteca", lifespan=lifespan)

@app.get("/", include_in_schema=False)
def raiz():  # pragma: no cover
    return RedirectResponse(url="/docs")

@app.exception_handler(ErrorDominio)
async def manejar_error_dominio(request: Request, exc: ErrorDominio):
    return JSONResponse(status_code=CODIGOS[type(exc)], content={"detail": exc.detalle})


for r in (autores.router, libros.router, socios.router, prestamos.router):
    app.include_router(r)
