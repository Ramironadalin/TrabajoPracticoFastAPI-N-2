from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from ..database import get_session
from ..models import LibroCreate, LibroRead, LibroUpdate
from ..services import libros

router = APIRouter(prefix="/libros", tags=["libros"])


@router.post("", response_model=LibroRead, status_code=status.HTTP_201_CREATED)
def crear_libro(datos: LibroCreate, session: Session = Depends(get_session)):
    libro = libros.crear_libro(session, datos)
    return LibroRead.model_validate(libro)


@router.get("", response_model=list[LibroRead])
def listar_libros(disponibles: bool | None = None, session: Session = Depends(get_session)):
    return [LibroRead.model_validate(l) for l in libros.listar_libros(session, disponibles)]


@router.get("/{libro_id}", response_model=LibroRead)
def obtener_libro(libro_id: int, session: Session = Depends(get_session)):
    return LibroRead.model_validate(libros.obtener_libro(session, libro_id))


@router.patch("/{libro_id}", response_model=LibroRead)
def actualizar_libro(libro_id: int, datos: LibroUpdate, session: Session = Depends(get_session)):
    libro = libros.actualizar_libro(session, libro_id, datos)
    return LibroRead.model_validate(libro)


@router.delete("/{libro_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_libro(libro_id: int, session: Session = Depends(get_session)):
    libros.eliminar_libro(session, libro_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{libro_id}/autores/{autor_id}", response_model=LibroRead)
def asociar_autor(libro_id: int, autor_id: int, session: Session = Depends(get_session)):
    return LibroRead.model_validate(libros.asociar_autor(session, libro_id, autor_id))
