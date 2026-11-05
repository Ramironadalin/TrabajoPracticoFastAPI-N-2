from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from .links import LibroAutor

if TYPE_CHECKING:
    from .libro import Libro


class AutorBase(SQLModel):
    nombre: str = Field(min_length=1)
    nacionalidad: str | None = None


class Autor(AutorBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    libros: list["Libro"] = Relationship(back_populates="autores", link_model=LibroAutor)


class AutorCreate(AutorBase):
    pass


class AutorUpdate(SQLModel):
    nombre: str | None = Field(default=None, min_length=1)
    nacionalidad: str | None = None


class AutorRead(AutorBase):
    id: int
