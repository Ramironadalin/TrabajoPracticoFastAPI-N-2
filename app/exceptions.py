"""Errores de dominio. main.py los traduce a códigos HTTP."""


class ErrorDominio(Exception):
    def __init__(self, detalle: str):
        super().__init__(detalle)
        self.detalle = detalle


class NoEncontrado(ErrorDominio):  # 404
    pass


class Conflicto(ErrorDominio):  # 409
    pass


class Prohibido(ErrorDominio):  # 403
    pass
