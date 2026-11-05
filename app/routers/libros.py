from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from ..database import get_session
from ..models import Libro, LibroCreate, LibroRead, LibroUpdate
from ..services import catalogo

router = APIRouter(prefix="/libros", tags=["libros"])


@router.post("", response_model=LibroRead, status_code=status.HTTP_201_CREATED)
def crear_libro(datos: LibroCreate, session: Session = Depends(get_session)):
    libro = catalogo.crear(session, Libro, datos, catalogo.MSG_ISBN)
    return LibroRead.model_validate(libro)


@router.get("", response_model=list[LibroRead])
def listar_libros(disponibles: bool = False, session: Session = Depends(get_session)):
    return [LibroRead.model_validate(l) for l in catalogo.listar_libros(session, disponibles)]


@router.get("/{libro_id}", response_model=LibroRead)
def obtener_libro(libro_id: int, session: Session = Depends(get_session)):
    return LibroRead.model_validate(catalogo.obtener(session, Libro, libro_id))


@router.patch("/{libro_id}", response_model=LibroRead)
def actualizar_libro(libro_id: int, datos: LibroUpdate, session: Session = Depends(get_session)):
    libro = catalogo.actualizar(session, Libro, libro_id, datos, catalogo.MSG_ISBN)
    return LibroRead.model_validate(libro)


@router.delete("/{libro_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_libro(libro_id: int, session: Session = Depends(get_session)):
    catalogo.eliminar(session, Libro, libro_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{libro_id}/autores/{autor_id}", response_model=LibroRead)
def asociar_autor(libro_id: int, autor_id: int, session: Session = Depends(get_session)):
    return LibroRead.model_validate(catalogo.asociar_autor(session, libro_id, autor_id))
