from sqlmodel import Field, SQLModel


class LibroAutor(SQLModel, table=True):
    """Tabla intermedia de la relación N-N Libro/Autor."""

    libro_id: int = Field(foreign_key="libro.id", primary_key=True)
    autor_id: int = Field(foreign_key="autor.id", primary_key=True)
