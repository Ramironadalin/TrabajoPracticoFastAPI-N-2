from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from ..database import get_session
from ..models import Autor, AutorCreate, AutorRead, AutorUpdate
from ..services import catalogo

router = APIRouter(prefix="/autores", tags=["autores"])


@router.post("", response_model=AutorRead, status_code=status.HTTP_201_CREATED)
def crear_autor(datos: AutorCreate, session: Session = Depends(get_session)):
    return catalogo.crear(session, Autor, datos)


@router.get("", response_model=list[AutorRead])
def listar_autores(session: Session = Depends(get_session)):
    return catalogo.listar(session, Autor)


@router.get("/{autor_id}", response_model=AutorRead)
def obtener_autor(autor_id: int, session: Session = Depends(get_session)):
    return catalogo.obtener(session, Autor, autor_id)


@router.patch("/{autor_id}", response_model=AutorRead)
def actualizar_autor(autor_id: int, datos: AutorUpdate, session: Session = Depends(get_session)):
    return catalogo.actualizar(session, Autor, autor_id, datos)


@router.delete("/{autor_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_autor(autor_id: int, session: Session = Depends(get_session)):
    catalogo.eliminar(session, Autor, autor_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
