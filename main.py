import sys
from collections import Counter
from pathlib import Path

from src.analizador import analizar_archivo_py
from src.validacion import obtener_complejidad_radon


def main(argumentos: list[str]) -> int:
    if len(argumentos) != 1:
        print("Uso: python main.py archivo.py", file=sys.stderr)
        return 2

    ruta = Path(argumentos[0])
    if not ruta.is_file():
        print(f"Error: no se encontró el archivo «{ruta}».", file=sys.stderr)
        return 1
    if ruta.suffix != ".py":
        print("Error: el archivo debe tener extensión .py.", file=sys.stderr)
        return 1

    try:
        codigo = ruta.read_text(encoding="utf-8")
        metricas = analizar_archivo_py(str(ruta))
        complejidades_radon = obtener_complejidad_radon(codigo)
    except SyntaxError as error:
        print(f"Error de sintaxis en la línea {error.lineno}: {error.msg}.", file=sys.stderr)
        return 1
    except (OSError, UnicodeError) as error:
        print(f"Error al leer «{ruta}»: {error}", file=sys.stderr)
        return 1

    if not metricas:
        print(f"No se encontraron funciones en «{ruta}».")
        return 0

    print(f"Archivo: {ruta}")
    nombres = Counter(metrica.name for metrica in metricas)
    for metrica in metricas:
        propia = metrica.cyclomatic_complexity
        radon = complejidades_radon.get(metrica.name)

        if nombres[metrica.name] > 1:
            valor_radon = "no disponible (nombre repetido)"
            coincidencia = "no comparable"
        elif radon is None:
            valor_radon = "no disponible"
            coincidencia = "no comparable"
        else:
            valor_radon = str(radon)
            coincidencia = "sí" if propia == radon else "no"

        print(f"\nFunción: {metrica.name}")
        print(f"  Complejidad ciclomática (analizador): {propia}")
        print(f"  Complejidad ciclomática (Radon): {valor_radon}")
        print(f"  ¿Coinciden?: {coincidencia}")
        print(f"  Líneas físicas: {metrica.lines}")
        print(f"  Profundidad máxima de anidamiento: {metrica.max_nesting_depth}")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
