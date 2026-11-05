"""Alta, baja, modificación y consulta de autores, libros y socios."""
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, SQLModel, select

from ..models import Autor, Libro, Prestamo, Socio
from .errors import Conflicto, NoEncontrado

MSG_ISBN = "Ya existe un libro con ese ISBN"
MSG_EMAIL = "Ya existe un socio con ese email"


def obtener(session: Session, modelo: type[SQLModel], id: int):
    obj = session.get(modelo, id)
    if obj is None:
        raise NoEncontrado(f"{modelo.__name__} {id} no existe")
    return obj


def _guardar(session: Session, obj, mensaje_duplicado: str):
    session.add(obj)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise Conflicto(mensaje_duplicado)
    session.refresh(obj)
    return obj


def crear(session: Session, modelo, datos: SQLModel, mensaje_duplicado: str = ""):
    return _guardar(session, modelo.model_validate(datos), mensaje_duplicado)


def listar(session: Session, modelo):
    return session.exec(select(modelo).order_by(modelo.id)).all()


def actualizar(session: Session, modelo, id: int, datos: SQLModel, mensaje_duplicado: str = ""):
    obj = obtener(session, modelo, id)
    obj.sqlmodel_update(datos.model_dump(exclude_unset=True))
    return _guardar(session, obj, mensaje_duplicado)


def eliminar(session: Session, modelo, id: int) -> None:
    obj = obtener(session, modelo, id)
    if modelo in (Libro, Socio):
        campo = Prestamo.libro_id if modelo is Libro else Prestamo.socio_id
        if session.exec(select(Prestamo).where(campo == id)).first():
            raise Conflicto(f"{modelo.__name__} {id} tiene préstamos asociados")
    session.delete(obj)  # SQLAlchemy limpia la tabla intermedia
    session.commit()


def listar_libros(session: Session, disponibles: bool = False):
    consulta = select(Libro).order_by(Libro.id)
    if disponibles:
        consulta = consulta.where(Libro.stock > 0)
    return session.exec(consulta).all()


def asociar_autor(session: Session, libro_id: int, autor_id: int) -> Libro:
    libro = obtener(session, Libro, libro_id)
    autor = obtener(session, Autor, autor_id)
    if autor in libro.autores:
        raise Conflicto("El autor ya está asociado al libro")
    libro.autores.append(autor)
    session.add(libro)
    session.commit()
    session.refresh(libro)
    return libro
