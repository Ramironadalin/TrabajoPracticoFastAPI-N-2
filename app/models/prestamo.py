from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .libro import Libro
    from .socio import Socio


class Prestamo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    socio_id: int = Field(foreign_key="socio.id", index=True)
    libro_id: int = Field(foreign_key="libro.id", index=True)
    fecha_prestamo: date
    fecha_vencimiento: date
    fecha_devolucion: date | None = None
    multa: int = 0

    socio: Optional["Socio"] = Relationship(back_populates="prestamos")
    libro: Optional["Libro"] = Relationship(back_populates="prestamos")


class PrestamoCreate(SQLModel):
    socio_id: int
    libro_id: int


class PrestamoRead(SQLModel):
    id: int
    socio_id: int
    libro_id: int
    fecha_prestamo: date
    fecha_vencimiento: date
    fecha_devolucion: date | None
    multa: int
