"""Lógica de negocio y CRUD de socios."""
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from ..exceptions import Conflicto, NoEncontrado
from ..models import Prestamo, Socio, SocioCreate, SocioUpdate

MSG_EMAIL = "Ya existe un socio con ese email"


def _guardar_socio(session: Session, socio: Socio) -> Socio:
    session.add(socio)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise Conflicto(MSG_EMAIL)
    session.refresh(socio)
    return socio


def obtener_socio(session: Session, socio_id: int) -> Socio:
    socio = session.get(Socio, socio_id)
    if socio is None:
        raise NoEncontrado(f"Socio {socio_id} no existe")
    return socio


def crear_socio(session: Session, datos: SocioCreate) -> Socio:
    return _guardar_socio(session, Socio.model_validate(datos))


def listar_socios(session: Session) -> list[Socio]:
    return list(session.exec(select(Socio).order_by(Socio.id)).all())


def actualizar_socio(session: Session, socio_id: int, datos: SocioUpdate) -> Socio:
    socio = obtener_socio(session, socio_id)
    socio.sqlmodel_update(datos.model_dump(exclude_unset=True))
    return _guardar_socio(session, socio)


def eliminar_socio(session: Session, socio_id: int) -> None:
    socio = obtener_socio(session, socio_id)
    if session.exec(select(Prestamo).where(Prestamo.socio_id == socio_id)).first():
        raise Conflicto(f"Socio {socio_id} tiene préstamos asociados")
    session.delete(socio)
    session.commit()

