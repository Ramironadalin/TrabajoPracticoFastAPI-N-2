from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .prestamo import Prestamo


class SocioBase(SQLModel):
    nombre: str = Field(min_length=1)
    email: str = Field(min_length=3, index=True, unique=True)
    activo: bool = True


class Socio(SocioBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    prestamos: list["Prestamo"] = Relationship(back_populates="socio")


class SocioCreate(SocioBase):
    pass


class SocioUpdate(SQLModel):
    nombre: str | None = Field(default=None, min_length=1)
    email: str | None = Field(default=None, min_length=3)
    activo: bool | None = None


class SocioRead(SocioBase):
    id: int
