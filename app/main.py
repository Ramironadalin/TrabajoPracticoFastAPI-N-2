from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .database import crear_tablas
from .routers import autores, libros, prestamos, socios
from .services.errors import Conflicto, ErrorDominio, NoEncontrado, Prohibido

CODIGOS = {NoEncontrado: 404, Conflicto: 409, Prohibido: 403}


@asynccontextmanager
async def lifespan(app: FastAPI):
    crear_tablas()
    yield


app = FastAPI(title="Biblioteca", lifespan=lifespan)


@app.exception_handler(ErrorDominio)
async def manejar_error_dominio(request: Request, exc: ErrorDominio):
    return JSONResponse(status_code=CODIGOS[type(exc)], content={"detail": exc.detalle})


for r in (autores.router, libros.router, socios.router, prestamos.router):
    app.include_router(r)
