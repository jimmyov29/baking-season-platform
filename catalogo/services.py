from decimal import Decimal, InvalidOperation

from .models import UnidadMedida


def to_decimal(value) -> Decimal:
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("La cantidad debe ser numerica.") from exc


def convertir_a_unidad_base(cantidad, unidad: UnidadMedida) -> Decimal:
    cantidad_decimal = to_decimal(cantidad)
    if cantidad_decimal < 0:
        raise ValueError("La cantidad no puede ser negativa.")
    return cantidad_decimal * unidad.factor_conversion
