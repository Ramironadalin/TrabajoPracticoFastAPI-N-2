from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from ..database import get_session
from ..models import PrestamoRead, SocioCreate, SocioRead, SocioUpdate
from ..services import prestamos, socios

router = APIRouter(prefix="/socios", tags=["socios"])


@router.post("", response_model=SocioRead, status_code=status.HTTP_201_CREATED)
def crear_socio(datos: SocioCreate, session: Session = Depends(get_session)):
    return socios.crear_socio(session, datos)


@router.get("", response_model=list[SocioRead])
def listar_socios(session: Session = Depends(get_session)):
    return socios.listar_socios(session)


@router.get("/{socio_id}", response_model=SocioRead)
def obtener_socio(socio_id: int, session: Session = Depends(get_session)):
    return socios.obtener_socio(session, socio_id)


@router.patch("/{socio_id}", response_model=SocioRead)
def actualizar_socio(socio_id: int, datos: SocioUpdate, session: Session = Depends(get_session)):
    return socios.actualizar_socio(session, socio_id, datos)


@router.delete("/{socio_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_socio(socio_id: int, session: Session = Depends(get_session)):
    socios.eliminar_socio(session, socio_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{socio_id}/prestamos", response_model=list[PrestamoRead])
def prestamos_del_socio(socio_id: int, activos: bool = False, session: Session = Depends(get_session)):
    return prestamos.listar_prestamos_socio(session, socio_id, activos)
