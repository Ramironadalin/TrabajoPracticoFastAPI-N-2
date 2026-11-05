from datetime import date


def get_hoy() -> date:
    """Fecha actual. Es una dependencia para poder fijarla en los tests."""
    return date.today()
