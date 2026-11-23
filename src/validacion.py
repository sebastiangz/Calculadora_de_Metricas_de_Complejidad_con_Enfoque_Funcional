from radon.complexity import cc_visit


def obtener_complejidad_radon(codigo_fuente: str) -> dict[str, int]:
    """Devuelve la complejidad ciclomática de los bloques de Radon por nombre."""
    bloques = cc_visit(codigo_fuente)
    return {bloque.name: bloque.complexity for bloque in bloques}
