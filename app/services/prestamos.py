"""Lógica de negocio y consultas de préstamos y devoluciones."""
from datetime import date, timedelta

from sqlmodel import Session, select

from ..exceptions import Conflicto, NoEncontrado, Prohibido
from ..models import Prestamo
from .libros import obtener_libro
from .socios import obtener_socio

MAX_PRESTAMOS_ACTIVOS = 3
PLAZO_DIAS = 14
MULTA_POR_DIA = 100


def obtener_prestamo(session: Session, prestamo_id: int) -> Prestamo:
    prestamo = session.get(Prestamo, prestamo_id)
    if prestamo is None:
        raise NoEncontrado(f"Prestamo {prestamo_id} no existe")
    return prestamo


def prestamos_activos_de(session: Session, socio_id: int) -> list[Prestamo]:
    consulta = select(Prestamo).where(
        Prestamo.socio_id == socio_id, Prestamo.fecha_devolucion == None  # noqa: E711
    )
    return list(session.exec(consulta.order_by(Prestamo.id)).all())


def listar_prestamos(session: Session, activos: bool = False) -> list[Prestamo]:
    consulta = select(Prestamo).order_by(Prestamo.id)
    if activos:
        consulta = consulta.where(Prestamo.fecha_devolucion == None)  # noqa: E711
    return list(session.exec(consulta).all())


def listar_prestamos_socio(session: Session, socio_id: int, activos: bool = False) -> list[Prestamo]:
    obtener_socio(session, socio_id)  # 404 si no existe
    if activos:
        return prestamos_activos_de(session, socio_id)
    consulta = select(Prestamo).where(Prestamo.socio_id == socio_id).order_by(Prestamo.id)
    return list(session.exec(consulta).all())


def crear_prestamo(session: Session, socio_id: int, libro_id: int, hoy: date) -> Prestamo:
    socio = obtener_socio(session, socio_id)  # regla 7
    libro = obtener_libro(session, libro_id)  # regla 7

    if not socio.activo:  # regla 3
        raise Prohibido("El socio está inactivo")
    if len(prestamos_activos_de(session, socio_id)) >= MAX_PRESTAMOS_ACTIVOS:  # regla 1
        raise Conflicto(f"El socio ya tiene {MAX_PRESTAMOS_ACTIVOS} préstamos activos")
    if libro.stock <= 0:  # regla 2
        raise Conflicto("No hay stock del libro")

    libro.stock -= 1
    prestamo = Prestamo(
        socio_id=socio_id,
        libro_id=libro_id,
        fecha_prestamo=hoy,
        fecha_vencimiento=hoy + timedelta(days=PLAZO_DIAS),  # regla 4
    )
    session.add(libro)
    session.add(prestamo)
    session.commit()
    session.refresh(prestamo)
    return prestamo


def calcular_multa(fecha_vencimiento: date, fecha_devolucion: date) -> int:
    dias_atraso = max(0, (fecha_devolucion - fecha_vencimiento).days)
    return MULTA_POR_DIA * dias_atraso


def devolver_prestamo(session: Session, prestamo_id: int, hoy: date) -> Prestamo:
    prestamo = obtener_prestamo(session, prestamo_id)  # regla 7
    if prestamo.fecha_devolucion is not None:  # regla 6
        raise Conflicto("El préstamo ya fue devuelto")

    prestamo.fecha_devolucion = hoy
    prestamo.multa = calcular_multa(prestamo.fecha_vencimiento, hoy)  # regla 5
    libro = obtener_libro(session, prestamo.libro_id)
    libro.stock += 1  # regla 5
    session.add(prestamo)
    session.add(libro)
    session.commit()
    session.refresh(prestamo)
    return prestamo
