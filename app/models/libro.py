from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from .autor import Autor, AutorRead
from .links import LibroAutor

if TYPE_CHECKING:
    from .prestamo import Prestamo


class LibroBase(SQLModel):
    titulo: str = Field(min_length=1)
    isbn: str = Field(min_length=1, index=True, unique=True)
    stock: int = Field(default=0, ge=0)
    anio: int | None = None


class Libro(LibroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    autores: list[Autor] = Relationship(back_populates="libros", link_model=LibroAutor)
    prestamos: list["Prestamo"] = Relationship(back_populates="libro")


class LibroCreate(LibroBase):
    pass


class LibroUpdate(SQLModel):
    titulo: str | None = Field(default=None, min_length=1)
    isbn: str | None = Field(default=None, min_length=1)
    stock: int | None = Field(default=None, ge=0)
    anio: int | None = None


class LibroRead(LibroBase):
    id: int
    autores: list[AutorRead] = []
