from datetime import date

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from ..database import get_session
from ..dependencies import get_hoy
from ..models import PrestamoCreate, PrestamoRead
from ..services import prestamos

router = APIRouter(prefix="/prestamos", tags=["prestamos"])


@router.post("", response_model=PrestamoRead, status_code=status.HTTP_201_CREATED)
def registrar_prestamo(
    datos: PrestamoCreate,
    session: Session = Depends(get_session),
    hoy: date = Depends(get_hoy),
):
    return prestamos.crear_prestamo(session, datos.socio_id, datos.libro_id, hoy)


@router.get("", response_model=list[PrestamoRead])
def listar_prestamos(activos: bool = False, session: Session = Depends(get_session)):
    return prestamos.listar_prestamos(session, activos)


@router.get("/{prestamo_id}", response_model=PrestamoRead)
def obtener_prestamo(prestamo_id: int, session: Session = Depends(get_session)):
    return prestamos.obtener_prestamo(session, prestamo_id)


@router.post("/{prestamo_id}/devolucion", response_model=PrestamoRead)
def registrar_devolucion(
    prestamo_id: int,
    session: Session = Depends(get_session),
    hoy: date = Depends(get_hoy),
):
    return prestamos.devolver_prestamo(session, prestamo_id, hoy)
