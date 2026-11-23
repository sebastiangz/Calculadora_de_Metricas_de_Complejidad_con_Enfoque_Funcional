"""Dibuja el CFG como SVG independiente de la representación lógica."""
from html import escape

from src.cfg import CFG


def cfg_a_svg(grafo: CFG, numero: int = 0) -> str:
    entrada, salida = grafo.entrada, grafo.salida
    nodos = sorted(
        grafo.nodos,
        key=lambda nodo: (nodo.id == salida, nodo.linea or 0, -nodo.id),
    )
    filas = {nodo.id: fila for fila, nodo in enumerate(nodos)}
    y = {nodo.id: 32 + fila * 72 for fila, nodo in enumerate(nodos)}

    # Las aristas largas ocupan carriles laterales. Los intervalos
    # disjuntos pueden reutilizar un carril.
    carriles: dict[int, list[int]] = {-1: [], 1: []}
    rutas = {}
    orden = sorted(
        enumerate(grafo.aristas),
        key=lambda item: min(filas[item[1].origen], filas[item[1].destino]),
    )
    for indice, arista in orden:
        origen, destino = filas[arista.origen], filas[arista.destino]
        if destino == origen + 1 and arista.etiqueta == "siguiente":
            continue
        lado = 1 if destino >= origen else -1
        inicio, fin = sorted((origen, destino))
        ocupados = carriles[lado]
        carril = next((i for i, limite in enumerate(ocupados) if limite < inicio), len(ocupados))
        if carril == len(ocupados):
            ocupados.append(fin)
        else:
            ocupados[carril] = fin
        rutas[indice] = (lado, carril)

    paso = 112
    centro = 114 + paso * len(carriles[-1])
    ancho = centro + 114 + paso * len(carriles[1])
    alto = y[salida] + 32
    flecha = f"flecha-cfg-{numero}"
    partes = [
        f'<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Grafo de flujo de control"'
        f' width="{ancho}" height="{alto}" viewBox="0 0 {ancho} {alto}">',
        '<title>Grafo de flujo de control</title>',
        f'<defs><marker id="{flecha}" markerWidth="8" markerHeight="8" refX="8" refY="4" orient="auto">'
        '<path d="M0 0 L8 4 L0 8 Z" fill="#334155"/></marker></defs>',
    ]

    for indice, arista in enumerate(grafo.aristas):
        inicio, fin = y[arista.origen], y[arista.destino]
        ancla = "start"
        if indice not in rutas:
            camino = f"M {centro} {inicio + 17} V {fin - 17}"
            etiqueta_x, etiqueta_y = centro + 8, (inicio + fin) / 2
        else:
            lado, carril = rutas[indice]
            borde = centro + lado * 90
            lateral = borde + lado * (26 + paso * carril)
            # Separar las conexiones de entrada y salida del mismo lado.
            camino = f"M {borde} {inicio - 7} H {lateral} V {fin + 7} H {borde}"
            etiqueta_x = lateral + lado * 4
            ancla = "end" if lado < 0 else "start"
            etiqueta_y = (inicio + fin) / 2
        etiqueta = escape(arista.etiqueta)
        partes.append(
            f'<g data-origen="{arista.origen}" data-destino="{arista.destino}">'
            f'<title>{etiqueta}</title><path d="{camino}" fill="none" stroke="#334155"'
            f' stroke-width="1.5" marker-end="url(#{flecha})"/>'
            f'<text x="{etiqueta_x}" y="{etiqueta_y}" text-anchor="{ancla}" font-size="11" fill="#334155" stroke="white"'
            f' stroke-width="3" paint-order="stroke">{etiqueta}</text></g>'
        )

    for nodo in nodos:
        altura = y[nodo.id]
        decision = nodo.tipo in {"If", "For", "AsyncFor", "While"}
        terminal = nodo.id in {entrada, salida}
        etiqueta = escape(nodo.tipo)
        if nodo.linea is not None:
            etiqueta += f" · L{nodo.linea}"
        color = "#fef3c7" if decision else "#dbeafe" if terminal else "#f1f5f9"
        partes.append(
            f'<g data-nodo="{nodo.id}"><rect x="{centro - 90}" y="{altura - 17}" width="180"'
            f' height="34" rx="{17 if terminal else 4}" fill="{color}" stroke="#334155"/>'
            f'<text x="{centro}" y="{altura}" text-anchor="middle" dominant-baseline="middle"'
            f' font-size="13" fill="#0f172a">{etiqueta}</text></g>'
        )

    return "\n".join([*partes, "</svg>"])
