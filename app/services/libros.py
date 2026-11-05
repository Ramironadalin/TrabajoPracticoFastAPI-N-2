"""Lógica de negocio y CRUD de libros."""
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from ..exceptions import Conflicto, NoEncontrado
from ..models import Libro, LibroCreate, LibroUpdate, Prestamo
from .autores import obtener_autor

MSG_ISBN = "Ya existe un libro con ese ISBN"


def _guardar_libro(session: Session, libro: Libro) -> Libro:
    session.add(libro)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise Conflicto(MSG_ISBN)
    session.refresh(libro)
    return libro


def obtener_libro(session: Session, libro_id: int) -> Libro:
    libro = session.get(Libro, libro_id)
    if libro is None:
        raise NoEncontrado(f"Libro {libro_id} no existe")
    return libro


def crear_libro(session: Session, datos: LibroCreate) -> Libro:
    return _guardar_libro(session, Libro.model_validate(datos))


def listar_libros(session: Session, disponibles: bool | None = None) -> list[Libro]:
    consulta = select(Libro).order_by(Libro.id)
    if disponibles is True:
        consulta = consulta.where(Libro.stock > 0)
    elif disponibles is False:
        consulta = consulta.where(Libro.stock == 0)
    return list(session.exec(consulta).all())


def actualizar_libro(session: Session, libro_id: int, datos: LibroUpdate) -> Libro:
    libro = obtener_libro(session, libro_id)
    libro.sqlmodel_update(datos.model_dump(exclude_unset=True))
    return _guardar_libro(session, libro)


def eliminar_libro(session: Session, libro_id: int) -> None:
    libro = obtener_libro(session, libro_id)
    if session.exec(select(Prestamo).where(Prestamo.libro_id == libro_id)).first():
        raise Conflicto(f"Libro {libro_id} tiene préstamos asociados")
    session.delete(libro)  # SQLAlchemy limpia la tabla intermedia
    session.commit()


def asociar_autor(session: Session, libro_id: int, autor_id: int) -> Libro:
    libro = obtener_libro(session, libro_id)
    autor = obtener_autor(session, autor_id)
    if autor in libro.autores:
        raise Conflicto("El autor ya está asociado al libro")
    libro.autores.append(autor)
    session.add(libro)
    session.commit()
    session.refresh(libro)
    return libro

