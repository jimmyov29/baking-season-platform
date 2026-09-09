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
    return (cantidad_decimal * unidad.factor_conversion).quantize(Decimal("0.000001"))



def calcular_cantidad_por_unidad(cantidad_base, rendimiento) -> Decimal:
    cantidad_decimal = to_decimal(cantidad_base)
    if rendimiento <= 0:
        raise ValueError("El rendimiento debe ser mayor que cero.")
    return cantidad_decimal / Decimal(rendimiento)


def calcular_requerimientos_producto(producto, cantidad_producto) -> list[dict[str, Decimal]]:
    cantidad_producto_decimal = to_decimal(cantidad_producto)
    if cantidad_producto_decimal <= 0:
        raise ValueError("La cantidad a producir debe ser mayor que cero.")

    requerimientos = []
    for receta in producto.insumos_receta.select_related("insumo", "unidad", "insumo__unidad_base"):
        cantidad_por_unidad = calcular_cantidad_por_unidad(receta.cantidad_base, producto.rendimiento)
        requerimientos.append(
            {
                "insumo": receta.insumo,
                "unidad_base": receta.insumo.unidad_base,
                "cantidad_base": cantidad_por_unidad * cantidad_producto_decimal,
            }
        )
    return requerimientos
