from .autor import Autor, AutorCreate, AutorRead, AutorUpdate
from .libro import Libro, LibroCreate, LibroRead, LibroUpdate
from .links import LibroAutor
from .prestamo import Prestamo, PrestamoCreate, PrestamoRead
from .socio import Socio, SocioCreate, SocioRead, SocioUpdate

__all__ = [
    "Autor", "AutorCreate", "AutorRead", "AutorUpdate",
    "Libro", "LibroCreate", "LibroRead", "LibroUpdate",
    "LibroAutor",
    "Prestamo", "PrestamoCreate", "PrestamoRead",
    "Socio", "SocioCreate", "SocioRead", "SocioUpdate",
]
