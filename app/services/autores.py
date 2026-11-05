"""Lógica de negocio y CRUD de autores."""
from sqlmodel import Session, select

from ..exceptions import NoEncontrado
from ..models import Autor, AutorCreate, AutorUpdate


def obtener_autor(session: Session, autor_id: int) -> Autor:
    autor = session.get(Autor, autor_id)
    if autor is None:
        raise NoEncontrado(f"Autor {autor_id} no existe")
    return autor


def crear_autor(session: Session, datos: AutorCreate) -> Autor:
    autor = Autor.model_validate(datos)
    session.add(autor)
    session.commit()
    session.refresh(autor)
    return autor


def listar_autores(session: Session) -> list[Autor]:
    return list(session.exec(select(Autor).order_by(Autor.id)).all())


def actualizar_autor(session: Session, autor_id: int, datos: AutorUpdate) -> Autor:
    autor = obtener_autor(session, autor_id)
    autor.sqlmodel_update(datos.model_dump(exclude_unset=True))
    session.add(autor)
    session.commit()
    session.refresh(autor)
    return autor


def eliminar_autor(session: Session, autor_id: int) -> None:
    autor = obtener_autor(session, autor_id)
    session.delete(autor)  # SQLAlchemy limpia la tabla intermedia
    session.commit()

